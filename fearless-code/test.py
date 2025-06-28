import os
import random
import json
import torch
from typing import List, Dict, Any, Optional
from pathlib import Path
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    AutoModelForSeq2SeqLM,
    pipeline
)
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
 
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
from bs4 import BeautifulSoup
import requests
 
import nltk
from nltk.tokenize import sent_tokenize
 
KNOWLEDGE_BASE_PATH = "book.txt"
USER_HISTORY_PATH = "user_history.json"
WARMUP_QUESTIONS_COUNT = 2  
MAX_CONTEXT_LENGTH = 2048   
 
class KnowledgeAgent:
    def __init__(self, model_name="google/flan-t5-base"):
        """Initialize the Knowledge Agent with the specified model."""
        print("Initializing Knowledge Agent...")
      
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
              model_name,
              torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
              device_map="auto" if torch.cuda.is_available() else None,
              low_cpu_mem_usage=True
          )
        
       
        self.generator = pipeline("text-generation", model=self.model, tokenizer=self.tokenizer)
        
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
     
        self.search = DuckDuckGoSearchAPIWrapper()
      
        self.knowledge_base = self.load_knowledge_base()
        
        self.index = self.create_knowledge_index()
        
        self.user_history = self.load_user_history()
        
        # Current session data
        self.current_query = ""
        self.warmup_answers = {}
        self.warmup_questions = []
        
        print("Knowledge Agent initialized successfully!")
 
    def load_knowledge_base(self) -> List[str]:
        """Load and preprocess the knowledge base from a text file."""
        try:
            if not os.path.exists(KNOWLEDGE_BASE_PATH):
                print(f"Warning: Knowledge base file {KNOWLEDGE_BASE_PATH} not found.")
                return []
            
            with open(KNOWLEDGE_BASE_PATH, 'r', encoding='utf-8') as file:
                content = file.read()
            
            chunks = []
            paragraphs = content.split('\n\n')
            
            for paragraph in paragraphs:
                paragraph = paragraph.strip()
                if not paragraph:
                    continue
                
                if len(paragraph) > 500:
                    sentences = sent_tokenize(paragraph)
                    chunks.extend(sentences)
                else:
                    chunks.append(paragraph)
            
            return chunks
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            return []
 
    def create_knowledge_index(self):
        """Create a FAISS index for the knowledge base."""
        if not self.knowledge_base:
            return None
        
        embeddings = self.embedding_model.encode(self.knowledge_base)
        
        faiss.normalize_L2(embeddings)
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatIP(dimension)
        index.add(embeddings)
        
        return index
 
    def load_user_history(self) -> Dict:
        """Load user interaction history."""
        if os.path.exists(USER_HISTORY_PATH):
            try:
                with open(USER_HISTORY_PATH, 'r') as file:
                    return json.load(file)
            except:
                return {}
        return {}
 
    def save_user_history(self):
        """Save user interaction history."""
        with open(USER_HISTORY_PATH, 'w') as file:
            json.dump(self.user_history, file, indent=2)
 
    def generate_warmup_questions(self, query: str) -> List[str]:
        """Generate smart sub-questions to explore the query context."""
        prompt = (
            f"As a subject matter expert, break down the query '{query}' into {WARMUP_QUESTIONS_COUNT} insightful and diverse sub-questions "
            "that could help better explore the topic. Format them as a numbered list."
        )
 
        response = self.model.generate(
            **self.tokenizer(prompt, return_tensors="pt", truncation=True).to(self.model.device),
            max_length=200,
            num_return_sequences=1,
            do_sample=True,
            top_p=0.95,
            top_k=50,
            eos_token_id=self.tokenizer.eos_token_id
        )
 
        decoded = self.tokenizer.decode(response[0], skip_special_tokens=True)
        lines = decoded.strip().split('\n')
        print(f'lines ---------------------- {lines}')
 
        questions = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line[0].isdigit() and '.' in line:
                question = line.split('.', 1)[-1].strip()
            else:
                question = line
            if question.endswith('?') and len(question) > 10:
                questions.append(question)
            if len(questions) >= WARMUP_QUESTIONS_COUNT:
                break
        print(f'question --------------------- {questions}')
        return questions
 
    def search_knowledge_base(self, query: str, top_k: int = 3) -> List[str]:
        """Search the knowledge base for relevant information."""
        if not self.knowledge_base or self.index is None:
            return []
        
        # Create query embedding
        query_embedding = self.embedding_model.encode([query])
        faiss.normalize_L2(query_embedding)
        
        # Search the index
        scores, indices = self.index.search(query_embedding, top_k)
        
        # Get the relevant chunks
        relevant_chunks = [self.knowledge_base[idx] for idx in indices[0]]
        
        return relevant_chunks
 
    def search_web(self, query: str, num_results: int = 3) -> List[str]:
        """Search the web for relevant information."""
        try:
            search_results = self.search.results(query, num_results)
            
            results = []
            for result in search_results:
                title = result.get('title', '')
                snippet = result.get('snippet', '')
                link = result.get('link', '')
                
                # Try to get more content from the webpage
                try:
                    response = requests.get(link, timeout=5)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, 'html.parser')
                        # Extract main content (this is a simple approach, might need refinement)
                        paragraphs = soup.find_all('p')
                        content = ' '.join([p.get_text() for p in paragraphs[:5]])  # Get first 5 paragraphs
                    else:
                        content = snippet
                except:
                    content = snippet
                
                results.append({
                    'title': title,
                    'content': content,
                    'link': link
                })
            
            return results
        except Exception as e:
            print(f"Error searching web: {e}")
            return []
 
    def generate_response(self, query: str, kb_results: List[str], web_results: List[Dict], warmup_info: Dict) -> str:
        """Generate a response based on knowledge base, web results, and warmup information."""
        # Prepare context from knowledge base
        kb_context = "\n".join(kb_results) if kb_results else ""
        
        # Prepare context from web results
        web_context = ""
        for result in web_results:
            web_context += f"Title: {result['title']}\nContent: {result['content']}\nSource: {result['link']}\n\n"
        
        # Prepare warmup information
        warmup_context = ""
        for question, answer in warmup_info.items():
            warmup_context += f"Q: {question}\nA: {answer}\n"
        
        # Combine all context
        full_context = f"""
                            Knowledge Base Information:
                            {kb_context}
                            
                            Web Search Results:
                            {web_context}
                            
                            User Information from Warmup Questions:
                            {warmup_context}
                            
                            Based on the above information, provide a comprehensive answer to the query: "{query}"
                            """
        
        # Truncate context if it's too long
        if len(full_context) > MAX_CONTEXT_LENGTH:
            # Keep the query and some important parts
            kb_part = kb_context[:MAX_CONTEXT_LENGTH // 3]
            web_part = web_context[:MAX_CONTEXT_LENGTH // 3]
            warmup_part = warmup_context[:MAX_CONTEXT_LENGTH // 3]
            
            full_context = f"""
                            Knowledge Base Information (truncated):
                            {kb_part}...
                            
                            Web Search Results (truncated):
                            {web_part}...
                            
                            User Information from Warmup Questions:
                            {warmup_part}
                            
                            Based on the above information, provide a comprehensive answer to the query: "{query}"
                            """
        
        # Generate response
        response = self.generator(full_context, max_length=500, num_return_sequences=1)[0]['generated_text']
        
        # Extract the actual answer (after the prompt)
        answer_start = response.find(f'query: "{query}"')
        if answer_start != -1:
            answer = response[answer_start + len(f'query: "{query}"'):].strip()
        else:
            answer = response
        
        # Clean up the answer
        answer = answer.replace('"', '').strip()
        
        # Add sources if available
        sources = []
        if kb_results:
            sources.append("Knowledge Base")
        if web_results:
            web_sources = [f"{result['title']} ({result['link']})" for result in web_results]
            sources.extend(web_sources)
        
        if sources:
            answer += f"\n\nSources: {', '.join(sources)}"
        
        return answer
 
    def process_query(self, query: str) -> Dict:
        """Process a user query and return the agent's response and next action."""
        self.current_query = query
        
        # Check if we need to ask warmup questions
        if not self.warmup_questions:
            self.warmup_questions = self.generate_warmup_questions(query)
            return {
                "response_type": "warmup_question",
                "content": self.warmup_questions[0],
                "remaining_questions": len(self.warmup_questions) - 1
            }
        
        # If we have warmup questions left, process the answer and ask the next question
        if len(self.warmup_answers) < len(self.warmup_questions):
            # Store the answer to the previous question
            question_idx = len(self.warmup_answers)
            self.warmup_answers[self.warmup_questions[question_idx - 1]] = query
            
            # If we have more questions, ask the next one
            if question_idx < len(self.warmup_questions):
                return {
                    "response_type": "warmup_question",
                    "content": self.warmup_questions[question_idx],
                    "remaining_questions": len(self.warmup_questions) - question_idx - 1
                }
        
        # If we're here, we've collected all warmup answers or this is a follow-up query
        
        # Search knowledge base
        kb_results = self.search_knowledge_base(query)
        
        # Search web
        web_results = self.search_web(query)
        
        # Generate response
        response = self.generate_response(query, kb_results, web_results, self.warmup_answers)
        
        # Update user history
        if query not in self.user_history:
            self.user_history[query] = {
                "warmup_answers": self.warmup_answers.copy(),
                "response": response
            }
            self.save_user_history()
        
        # Reset for next query
        self.warmup_questions = []
        self.warmup_answers = {}
        
        return {
            "response_type": "answer",
            "content": response,
            "follow_up": "Do you want to know more about this topic?"
        }
 
def main():
    """Main function to run the Knowledge Agent."""
    print("Starting Knowledge Agent...")
    
    # Check if knowledge base exists
    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        print(f"Warning: Knowledge base file {KNOWLEDGE_BASE_PATH} not found.")
        print("Creating an empty knowledge base file. Please add content to it.")
        with open(KNOWLEDGE_BASE_PATH, 'w') as f:
            f.write("This is a placeholder for your knowledge base content.\n")
            f.write("Replace this with your actual content.\n")
    
    # Initialize the agent
    agent = KnowledgeAgent()
    
    print("\nKnowledge Agent is ready! Type 'exit' to quit.")
    print("Enter your query:")
    
    while True:
        user_input = input("> ").strip()
        
        if user_input.lower() in ['exit', 'quit']:
            print("Thank you for using Knowledge Agent. Goodbye!")
            break
        
        if not user_input:
            continue
        
        # Process the query
        result = agent.process_query(user_input)
        
        # Display the result
        if result["response_type"] == "warmup_question":
            print(f"\nTo better understand your needs, please answer this question:")
            print(f"{result['content']}")
            if result["remaining_questions"] > 0:
                print(f"({result['remaining_questions']} more question(s) after this)")
        else:
            print(f"\n{result['content']}")
            print(f"\n{result['follow_up']}")
 
if __name__ == "__main__":
    main()