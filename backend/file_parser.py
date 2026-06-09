import os
from docx import Document as DocxDocument
from llm import describe_image


def parse_txt(file_bytes):
    return file_bytes.decode("utf-8", errors="ignore"), [], []


def parse_docx(file_bytes, temp_path="temp_uploaded.docx"):
    with open(temp_path, "wb") as f:
        f.write(file_bytes)

    doc = DocxDocument(temp_path)

    text = ""
    for para in doc.paragraphs:
        text += para.text + "\n"

    os.remove(temp_path)

    return text, [], []


def parse_image(file_bytes, filename, image_folder="extracted_images"):
    os.makedirs(image_folder, exist_ok=True)

    image_path = os.path.join(image_folder, filename)

    with open(image_path, "wb") as f:
        f.write(file_bytes)

    description = describe_image(image_path)

    text = f"""
[IMAGE DOCUMENT]
File name: {filename}

Image description:
{description}
"""

    return text, [image_path], [description]