from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from passlib.context import CryptContext

from database import get_db
from database_tables import User, Document, ChatHistory

from chunking import create_chunks
from vector_store import store_chunks, search_chunks
from pdf_parser import extract_text_and_images
from llm import generate_answer

from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "my_secret_key_change_later"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24 hours

security = HTTPBearer()


def create_access_token(data: dict):
    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user

@app.get("/")
def home():
    return {"message": "Backend is running"}


@app.post("/signup")
def signup(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.username == username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = password_context.hash(password)

    new_user = User(
        username=username,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User created successfully",
        "user_id": new_user.id,
        "username": new_user.username
    }


@app.post("/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == username).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not password_context.verify(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(
    data={"sub": user.username}
)

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username
    }


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = current_user

    pdf_bytes = await file.read()
    extracted_text, image_paths = extract_text_and_images(pdf_bytes)

    chunks = create_chunks(extracted_text)

    collection_name = f"user_{user.username}"

    store_chunks(user.username, file.filename, chunks)

    new_document = Document(
        user_id=user.id,
        file_name=file.filename,
        chunks_created=len(chunks),
        images_extracted=len(image_paths),
        collection_name=collection_name
    )

    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return {
        "message": "File uploaded and embeddings stored successfully",
        "document_id": new_document.id,
        "file_name": file.filename,
        "chunks_created": len(chunks),
        "images_extracted": len(image_paths),
        "collection_name": collection_name
    }


@app.post("/chat")
def chat(
    file_name: str = Form(...),
    query: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user = current_user

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    results = search_chunks(user.username, query, file_name, top_k=3)

    answer = generate_answer(query, results)

    new_chat = ChatHistory(
        user_id=user.id,
        file_name=file_name,
        question=query,
        answer=answer
    )

    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    suggestions = [
        "Can you explain this in simpler terms?",
        "What are the key points?",
        "How is this used in the project?"
    ]

    return {
        "answer": answer,
        "suggested_questions": suggestions,
        "retrieved_chunks": results
    }


@app.get("/history")
def get_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == current_user.id)
        .order_by(ChatHistory.created_at.desc())
        .all()
    )

    history = []

    for chat in chats:
        history.append({
            "file_name": chat.file_name,
            "question": chat.question,
            "answer": chat.answer,
            "created_at": chat.created_at
        })

    return {
        "username": current_user.username,
        "history": history
    }