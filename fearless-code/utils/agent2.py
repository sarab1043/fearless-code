import os
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_core.documents import Document

class PhiResponder:
    db_faiss = None
    faiss_index_path="faiss_index"

    def __init__(self, doc_path="fearless_code.txt"):
        self.doc_path = doc_path
        self.last_query = ""
        self.last_context = ""
        self.model = ChatOllama(model="mistral")

    @classmethod
    def _initialize_once(cls, doc_path="fearless_code.txt"):
        """Build or load FAISS index just once on startup."""
        if not os.path.exists(cls.faiss_index_path) or not os.listdir(cls.faiss_index_path):
            print("📦 FAISS index not found — creating new one")
            with open(doc_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            documents = [Document(page_content=content)]
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
            chunks = splitter.split_documents(documents)
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

            cls.db_faiss = FAISS.from_documents(chunks, embeddings,allow_dangerous_deserialization=True ) #Trust my own data
            cls.db_faiss.save_local(cls.faiss_index_path)
        else:
            print("✅ FAISS index found — loading")
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            cls.db_faiss = FAISS.load_local(cls.faiss_index_path, embeddings,allow_dangerous_deserialization=True )

    def ask(self, messages: list, user_prompt: str, role="assistant") -> str:
        if user_prompt != self.last_query:
            docs = PhiResponder.db_faiss.similarity_search_with_score(user_prompt, k=5)
            self.last_context = "\n\n".join([doc.page_content for doc, _ in docs])
            self.last_query = user_prompt
        
        print(self.last_context)

        # Minimal prompt, replace with full instruction if needed
        PROMPT_TEMPLATE = """
        You are the Fearless Code Agent. Do NOT break format. Do NOT roleplay.

        Your task: Help users explore their current inner state using Fearless Code principles from the CONTEXT.
        {context}

        Process:
        1. If this is the user's first message, only then ask 2 open-ended warm-up questions specific to the selected topic otherwise give it a answer and ask quetions.
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

        prompt = PromptTemplate.from_template(PROMPT_TEMPLATE).format(context=self.last_context)

        prompt_messages = [{"role": "system", "content": prompt}]
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            # Only append if it's a unique message compared to the last one
            if role and content:
                # Compare the last message in prompt_messages with the current message
                if not prompt_messages or (prompt_messages[-1]["role"].lower().strip() != role.lower() or prompt_messages[-1]["content"].lower().strip() != content.lower()):
                    prompt_messages.append({"role": role, "content": content})

       

        response = self.model.invoke(prompt_messages)
        return response.content.strip()
