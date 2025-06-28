# from sentence_transformers import SentenceTransformer
# from sklearn.metrics.pairwise import cosine_similarity
# import numpy as np
# import os
# from transformers import AutoModelForCausalLM, AutoTokenizer
# import torch
# from typing import List

# class AgentHelper:
#     def __init__(self, knowledge_path, model_name="all-MiniLM-L6-v2"):
#         self.knowledge_path = knowledge_path
#         # Initialize embedding model with memory-efficient settings
#         self.embedding_model = SentenceTransformer(model_name, device='cpu')
#         self.chunks = None
#         self.embeddings = None
        
#         # Initialize lightweight LLM (BERT-tiny)
#         self.tokenizer = AutoTokenizer.from_pretrained('prajjwal1/bert-tiny')
#         self.llm = AutoModelForCausalLM.from_pretrained('prajjwal1/bert-tiny')
#         self.llm.to('cpu')  # Force CPU usage
        
#         # Set to evaluation mode to disable dropout and save memory
#         self.llm.eval()
        
#         # Lazy load embeddings
#         self._lazy_load_knowledge_base()

#     def _lazy_load_knowledge_base(self):
#         if self.chunks is None or self.embeddings is None:
#             # Load and split text
#             with open(self.knowledge_path, "r", encoding="utf-8") as f:
#                 text = f.read()
#             self.chunks = self._split_text(text)
            
#             # Process embeddings in small batches to save memory
#             batch_size = 8  # Smaller batch size
#             all_embeddings = []
            
#             for i in range(0, len(self.chunks), batch_size):
#                 batch = self.chunks[i:i + batch_size]
#                 embeddings = self.embedding_model.encode(
#                     batch,
#                     convert_to_tensor=True,
#                     show_progress_bar=False,
#                     normalize_embeddings=True  # Normalize to save memory
#                 )
#                 all_embeddings.append(embeddings)
                
#             self.embeddings = np.vstack(all_embeddings)

#     def _split_text(self, text, chunk_size=500, overlap=100):
#         words = text.split()
#         chunks = []
#         for i in range(0, len(words), chunk_size - overlap):
#             chunk = " ".join(words[i:i + chunk_size])
#             chunks.append(chunk)
#         return chunks

#     def retrieve_context(self, query, top_k=3):
#         # Ensure knowledge base is loaded
#         self._lazy_load_knowledge_base()
        
#         # Get query embedding using the embedding model
#         query_embedding = self.embedding_model.encode(
#             [query],
#             convert_to_tensor=True,
#             show_progress_bar=False,
#             normalize_embeddings=True
#         )
        
#         # Calculate similarities
#         similarities = cosine_similarity(query_embedding, self.embeddings)[0]
#         top_indices = np.argsort(similarities)[-top_k:][::-1]
        
#         return "\n\n".join([self.chunks[i] for i in top_indices])

#     def process_query(self, query: str) -> str:
#         if not query or not isinstance(query, str):
#             return "Invalid query provided"
            
#         try:
#             # Get relevant context
#             context = self.retrieve_context(query)
#             if not context:
#                 return "No relevant context found to answer the question"
            
#             # Prepare input with a more explicit prompt
#             prompt = (
#                 "Based on the following context, provide a clear and concise answer to the question.\n\n"
#                 f"Context: {context}\n\n"
#                 f"Question: {query}\n\n"
#                 "Answer: "
#             )
            
#             # Tokenize with safety checks
#             try:
#                 inputs = self.tokenizer(
#                     prompt,
#                     return_tensors="pt",
#                     max_length=512,
#                     truncation=True,
#                     padding=True
#                 )
#             except Exception as e:
#                 return f"Error processing input: {str(e)}"
            
#             # Generate response with minimal memory usage
#             try:
#                 with torch.no_grad():  # Disable gradient tracking
#                     outputs = self.llm.generate(
#                         inputs["input_ids"],
#                         max_length=200,
#                         num_return_sequences=1,
#                         temperature=0.7,
#                         pad_token_id=self.tokenizer.eos_token_id,
#                         do_sample=True,
#                         top_k=50,
#                         top_p=0.95,
#                         no_repeat_ngram_size=3,  # Prevent repetition
#                         early_stopping=True
#                     )
                
#                 # Decode response
#                 response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
                
#                 # Extract and validate answer
#                 answer = response.split("Answer:")[-1].strip()
#                 if not answer:
#                     return "I apologize, but I couldn't generate a meaningful response. Please try rephrasing your question."
                    
#                 return answer
                
#             except Exception as e:
#                 return f"Error generating response: {str(e)}"
                
#         except Exception as e:
#             return f"Unexpected error: {str(e)}"


