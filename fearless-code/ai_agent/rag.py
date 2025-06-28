# rag.py

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def build_or_load_vectorstore():
    if os.path.exists("faiss_index"):
        return FAISS.load_local("faiss_index", HuggingFaceEmbeddings(model_name=EMBED_MODEL), allow_dangerous_deserialization=True)

    print("📘 Building new FAISS index from book.txt...")
    loader = TextLoader("book.txt")
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)

    texts = splitter.split_documents(documents)

    embeddings = HuggingFaceEmbeddings(model_name=EMBED_MODEL)
    vectorstore = FAISS.from_documents(texts, embeddings)
    vectorstore.save_local("faiss_index")
    return vectorstore
