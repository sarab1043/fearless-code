import os
import pickle
import ollama
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from langchain.text_splitter import RecursiveCharacterTextSplitter
import requests
from langchain.embeddings.sentence_transformer import SentenceTransformerEmbeddings
from langchain.vectorstores import FAISS

class PhiResponder:
    _vectorstore = None
    _text_cache = None
    _session = None

    def __init__(self, doc_path="fearless_code.txt"):
        self.doc_path = doc_path
        if PhiResponder._session is None:
            PhiResponder._session = requests.Session()

    @classmethod
    def _initialize(cls, doc_path="fearless_code.txt"):
        if cls._vectorstore is not None:
            return  # Already initialized
        

        if not os.path.exists(doc_path):
            raise FileNotFoundError(f"Document not found: {doc_path}")

        with open(doc_path, "r", encoding="utf-8") as f:
            text = f.read().strip()
            if not text:
                raise ValueError("Document is empty.")
            cls._text_cache = text

        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        documents = splitter.create_documents([cls._text_cache])
        if not documents:
            raise ValueError("No documents created from input text.")

        embedding_model = SentenceTransformerEmbeddings(
            model_name="all-MiniLM-L6-v2",
            cache_folder="/tmp/embeddings_cache"
        )
        cls._vectorstore = FAISS.from_documents(documents, embedding_model)

    def get_vectorstore(self):
        if PhiResponder._vectorstore is None:
            raise RuntimeError("Vectorstore not initialized.")
        return PhiResponder._vectorstore

    def retrieve_context(self, query, k=2):
        retriever = self.get_vectorstore().as_retriever(
            search_type="similarity", search_kwargs={"k": k}
        )
        docs = retriever.get_relevant_documents(query)
        return "\n\n".join(doc.page_content for doc in docs)

    def ask(self, messages=None, query=None, role="assistant"):
        context = self.retrieve_context(query)

        # if role=="assistant":
        #     system_prompt = f"""
        #     You are a sharp, powerful assistant who responds clearly and short answers with one follow up question.
        #     ONLY use the following CONTEXT to answer the question.
        #     {context}
        #     Ask one follow up question to keep conversation ongoing.
        #     Only answer what user asked nothing unnecessary examples including imaginations.
        #     ALways follow these Rules:
        #     - Only answer what the user asks.
        #     - If unclear, ask the user to clarify.
        #     - Answers must be short and point to point and not be in long paragraph.
        #     - One follow up question to keep conversation ongoing.
            
        #     """
        if role=="assistant":
            system_prompt = f"""You are the Fearless Code Agent. Do NOT break format. Do NOT roleplay.

            Your task: Help users explore their current inner state using Fearless code princliples in the CONTEXT.

            ONLY use the following CONTEXT to answer the question.

            {context}

            Process:
            1. If this is the user's first message, then ask 2 open-ended warm-up questions specific to the selected topic.
            2. After that, only respond if user replies or says “Answer now”.

            Constraints:
            - Only respond about: career, self-confidence, or finances.
            - Use perception → action logic from Fearless Code.
            - Include “I frequency” if helpful.
            - NEVER mention goals, affirmations, or psychology terms.
            - NEVER explain what Fearless Code is.
            - NEVER answer instead of asking warm-up questions.
            - NEVER create imaginary scenarios or examples.

            Format:
            Start response with:  
            “Answering per Fearless Code principles...”
            Then ask:
            1) [question]
            2) [question]

            Tone: Direct, kind, never overreaching.
            """

        if role=="wellness":
            system_prompt = f"""
            You are a warm, emotionally intelligent mental wellness guide with high EQ (EQ 150). 
            Act like a mental and life optimizer who helps user to guide about life and mental promplems
            Always ask one follow up questions to understand user and keep conversation ongoing.
            Alwasy short as short as possible
            ONLY use the following CONTEXT to answer the question.
            {context}
            """
        
        prompt_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            # Only append if it's a unique message compared to the last one
            if role and content:
                # Compare the last message in prompt_messages with the current message
                if not prompt_messages or (prompt_messages[-1]["role"].lower().strip() != role.lower() or prompt_messages[-1]["content"].lower().strip() != content.lower()):
                    prompt_messages.append({"role": role, "content": content})

        if prompt_messages:
            response = ollama.chat(model="mistral:7b-instruct-v0.2-q2_K", messages=prompt_messages)
        else:
            response = ollama.chat(model="mistral:7b-instruct-v0.2-q2_K", messages=query)

        return f"{response['message']['content']}"

        
