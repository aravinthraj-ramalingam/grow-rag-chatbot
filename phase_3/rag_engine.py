import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Absolute path resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
env_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path=env_path)

VECTOR_STORE_PATH = os.path.join(root_dir, "phase_2", "vector_store.json")
API_KEY = os.environ.get("GOOGLE_API_KEY")

class RAGChatbot:
    def __init__(self):
        if not API_KEY:
            raise ValueError("GOOGLE_API_KEY missing.")
        genai.configure(api_key=API_KEY)
        
        # Auto-detect models
        models = [m.name for m in genai.list_models()]
        
        # Generation Model
        self.gen_model = 'models/gemini-1.5-flash'
        if self.gen_model not in models:
            # Fallback to anything with generateContent
            self.gen_model = next((m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods), 'models/gemini-pro')
            
        # Embedding Model
        self.embed_model = 'models/gemini-embedding-001'
        if self.embed_model not in models:
            self.embed_model = 'models/embedding-001'
            if self.embed_model not in models:
                self.embed_model = next((m.name for m in genai.list_models() if 'embedContent' in m.supported_generation_methods), 'models/embedding-001')
        
        self.llm = genai.GenerativeModel(self.gen_model)
        self.vector_store = self._load_vector_store()
        logger.info(f"RAG initialized with gen:{self.gen_model} and embed:{self.embed_model}")

    def _load_vector_store(self) -> List[Dict]:
        if not os.path.exists(VECTOR_STORE_PATH):
            logger.error(f"Store not found at {VECTOR_STORE_PATH}")
            return []
        with open(VECTOR_STORE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_embedding(self, text: str) -> List[float]:
        try:
            result = genai.embed_content(
                model=self.embed_model,
                content=text,
                task_type="retrieval_query"
            )
            # Standard extraction
            if hasattr(result, 'embedding'):
                return result.embedding
            elif isinstance(result, dict) and 'embedding' in result:
                return result['embedding']
            elif hasattr(result, 'values'):
                return result.values
            else:
                if hasattr(result, 'embeddings'):
                    e = result.embeddings[0]
                    return e.values if hasattr(e, 'values') else e
                raise KeyError("No embedding list found")
        except Exception as e:
            # Fallback to retrieval_document if query fails
            if "task_type" in str(e):
                 result = genai.embed_content(model=self.embed_model, content=text, task_type="retrieval_document")
                 return result.embedding if hasattr(result, 'embedding') else result['embedding']
            raise e

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        v1, v2 = np.array(v1), np.array(v2)
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

    def retrieve(self, query: str, k: int = 5) -> str:
        emb = self._get_embedding(query)
        scores = []
        for item in self.vector_store:
            scores.append((self._cosine_similarity(emb, item["embedding"]), item))
        scores.sort(key=lambda x: x[0], reverse=True)
        return "\n\n".join([f"Context: {i['text']}" for s, i in scores[:k]])

    def ask(self, query: str) -> str:
        context = self.retrieve(query)
        prompt = (
            "You are a factual Tata Mutual Fund assistant. Answer precisely using the context.\n"
            "If user asks for investment advice or opinion, refuse: 'I am a factual assistant. Please consult a financial advisor for investment advice. Link: https://groww.in/blog/how-to-invest-in-mutual-funds'\n"
            "If info is missing, say you don't have that specific data.\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"USER QUERY: {query}\n"
            "FACTUAL ANSWER:"
        )
        try:
            r = self.llm.generate_content(prompt)
            return r.text.strip() if r.candidates else "Blocked."
        except Exception as e:
            return f"Error: {e}"

if __name__ == "__main__":
    bot = RAGChatbot()
    test_queries = [
        "What is the exit load for Tata Large Cap Fund?",
        "Who is the manager for Tata ELSS?",
        "Is Tata Multicap a good investment?"
    ]
    for q in test_queries:
        print(f"\nQ: {q}\nA: {bot.ask(q)}")
