import os
from dotenv import load_dotenv
from google import genai

#Dotenv is a lightweight library used to load environment variables from a .env file into your application's environment at runtime

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#Create a Gemini API connection using the API key stored in the .env file.

def generate_answer(query, retrieved_chunks):
    context = ""

    for chunk, score in retrieved_chunks:
        context += chunk + "\n\n"

    prompt = f"""
You are a helpful RAG assistant.

Answer the user question using ONLY the context below.
If the answer is not present in the context, say: "I don't know from the given document."

Context:
{context}

Question:
{query}

Answer:
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text