from fastapi import FastAPI
from pydantic import BaseModel
from rag import build_or_load_vectorstore
from agent import build_prompt
import requests

app = FastAPI()

# Load vectorstore from book.txt (build if not exists)
vectorstore = build_or_load_vectorstore()

# Input schema
class Query(BaseModel):
    message: str
    agent: str  # "life_coach" or "wellness_guide"

# Chat endpoint
@app.post("/chat/")
def chat(query: Query):
    # 1. Search for relevant content from the book
    docs = vectorstore.similarity_search(query.message, k=2)

    context = "\n".join([doc.page_content for doc in docs]) if docs else ""

    print("📚 Book context found:\n", context or "⚠️ No context matched from book.")

    # 2. Build the final prompt for the selected agent
    prompt = build_prompt(query.message, context, query.agent)
    print("🧠 Final prompt sent to LLM:\n", prompt)

    # 3. Call Ollama (local LLM API)
    try:
        response = call_local_llm(prompt)
        return {"response": response.strip()}
    except Exception as e:
        return {"error": str(e)}

# Call to Ollama
def call_local_llm(prompt: str) -> str:
    try:
        r = requests.post(
            "http://localhost:11434/api/generate",
            json={"model": "phi", "prompt": prompt, "stream": False},
            timeout=60  # Increased timeout further
        )
        r.raise_for_status()
        return r.json()["response"]
    except requests.exceptions.Timeout:
        raise Exception("Connection to Ollama timed out. Please ensure Ollama is running and not overloaded.")
    except requests.exceptions.ConnectionError:
        raise Exception("Could not connect to Ollama. Please ensure the Ollama server is running on localhost:11434.")
    except Exception as e:
        raise Exception(f"Error calling Ollama: {str(e)}")
