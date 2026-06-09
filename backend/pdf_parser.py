import fitz
import os
from llm import describe_image


def extract_text_and_images(pdf_bytes, image_folder="extracted_images"):
    os.makedirs(image_folder, exist_ok=True)

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")

    full_text = ""
    image_paths = []
    image_descriptions = []

    for page_number, page in enumerate(doc, start=1):
        text = page.get_text()
        full_text += f"\n\n--- Page {page_number} ---\n{text}"

        images = page.get_images(full=True)

        for image_index, img in enumerate(images, start=1):
            xref = img[0]
            image_data = doc.extract_image(xref)

            image_bytes = image_data["image"]
            image_ext = image_data["ext"]

            image_path = os.path.join(
                image_folder,
                f"page_{page_number}_image_{image_index}.{image_ext}"
            )

            with open(image_path, "wb") as f:
                f.write(image_bytes)

            image_paths.append(image_path)

            try:
                description = describe_image(image_path)
            except Exception:
                description = (
                    "Image was extracted from the document, "
                    "but image description could not be generated due to API limits."
                )

            image_descriptions.append(description)

    return full_text, image_paths, image_descriptions