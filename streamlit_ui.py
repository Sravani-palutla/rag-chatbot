import streamlit as st
from chunking import create_chunks
from vector_store import store_chunks, search_chunks
from llm import generate_answer
from pdf_parser import extract_text_and_images

st.title("RAG Chatbot")

user_id = st.text_input("Enter user id", value="sravani")

uploaded_file = st.file_uploader("Upload the pdf here:", type=["pdf"])

if uploaded_file is not None:
    st.write("File uploaded successfully")

    file_name = uploaded_file.name

    st.write("File name:", file_name)
    st.write("File type:", uploaded_file.type)
    st.write("File_size:", uploaded_file.size, "bytes")

    if st.button("Store document embeddings"):
        extracted_text, image_paths = extract_text_and_images(uploaded_file)

        chunks = create_chunks(extracted_text)

        store_chunks(user_id, file_name, chunks)

        st.success("Chunks stored in Chroma successfully!")

        st.write("Extracted images:", len(image_paths))

query = st.text_input("Enter your query here:")

if query and uploaded_file is not None:
    results = search_chunks(user_id, query, uploaded_file.name, top_k=3)

    st.subheader("Retrieved Chunks")
    for chunk, score in results:
        st.write("Score:", score)
        st.write(chunk)

    answer = generate_answer(query, results)

    st.subheader("Final Answer")
    st.write(answer)