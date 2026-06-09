import os
from dotenv import load_dotenv
from google import genai
from PIL import Image

#Dotenv is a lightweight library used to load environment variables from a .env file into your application's environment at runtime

load_dotenv()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
#Create a Gemini API connection using the API key stored in the .env file.

def describe_image(image_path):
    try:
        image = Image.open(image_path)

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                "Describe this image clearly for document question answering. Mention any text, diagram, chart, architecture, flow, or important visual details.",
                image
            ]
        )

        return response.text

    except Exception as e:
        print("Image description failed:", e)

        return (
            "Image description could not be generated because the Gemini API quota was exhausted. "
            "The image was uploaded successfully, but visual understanding is temporarily unavailable."
        )
    
def generate_answer(query, retrieved_chunks):
    context = ""

    for chunk, score in retrieved_chunks:
        context += chunk + "\n\n"

    if not context.strip():
        return "I could not find relevant content from the uploaded document."

    prompt = f"""
You are a helpful document intelligence assistant.

Answer the question using the context below.

Rules:
- Use the document context as much as possible.
- If the answer is partially available, explain from the available context.
- If the question is about an image, diagram, chart, flow, or architecture, use any IMAGE DESCRIPTION in the context.
- Only say "I don't know from the given document" if the context is completely unrelated.

Context:
{context}

Question:
{query}

Answer:
"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.text

    except Exception as e:
        print("Answer generation failed:", e)

        fallback_answer = "Gemini answer generation failed. But these are the most relevant document parts I found:\n\n"

        for chunk, score in retrieved_chunks:
            fallback_answer += f"{chunk}\n\n"

        return fallback_answer