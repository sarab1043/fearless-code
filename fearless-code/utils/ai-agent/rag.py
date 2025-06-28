import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from config import BOOK_PATH, EMBED_MODEL

def build_or_load_vectorstore():
    embedder = HuggingFaceEmbeddings(model_name=EMBED_MODEL)

    if os.path.exists("faiss_index"):
        return FAISS.load_local(
            "faiss_index",
            embeddings=embedder,
            allow_dangerous_deserialization=True  # ✅ Allow safe loading
        )
    
    with open(BOOK_PATH, "r") as f:
        raw_text = f.read()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    texts = text_splitter.split_text(raw_text)

    vectorstore = FAISS.from_texts(texts, embedder)
    vectorstore.save_local("faiss_index")
    return vectorstore
