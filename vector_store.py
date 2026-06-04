import chromadb
from chromadb.utils import embedding_functions

"""
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-base-en-v1.5"
)
"""
embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path="./chroma_db")


def get_user_collection(user_id):
    collection_name = f"user_{user_id}"

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_function,
        metadata={"hnsw:space": "cosine"}
    )

    return collection


def store_chunks(user_id, file_name, chunks):
    collection = get_user_collection(user_id)

    ids = []
    documents = []
    metadatas = []

    for i, chunk in enumerate(chunks):
        ids.append(f"{file_name}_{i}")
        documents.append(chunk)
        metadatas.append({
            "user_id": user_id,
            "file_name": file_name,
            "chunk_number": i
        })

    collection.upsert(
        ids=ids,
        documents=documents,
        metadatas=metadatas
    )


def search_chunks(user_id, query, file_name=None, top_k=3):
    collection = get_user_collection(user_id)

    where_filter = None

    if file_name is not None:
        where_filter = {"file_name": file_name}

    results = collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where_filter
    )

    final_results = []

    documents = results["documents"][0]
    distances = results["distances"][0]

    for doc, distance in zip(documents, distances):
        score = 1 - distance
        final_results.append((doc, score))

    return final_results