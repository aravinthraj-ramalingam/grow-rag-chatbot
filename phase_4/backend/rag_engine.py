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

# Paths for Phase 4 Backend structure
current_dir = os.path.dirname(os.path.abspath(__file__))
env_path = os.path.join(current_dir, ".env")
vector_store_path = os.path.join(current_dir, "data", "vector_store.json")

load_dotenv(dotenv_path=env_path)
API_KEY = os.environ.get("GOOGLE_API_KEY")

class RAGChatbot:
    def __init__(self):
        if not API_KEY:
            raise ValueError("GOOGLE_API_KEY missing.")
        genai.configure(api_key=API_KEY)
        
        models = [m.name for m in genai.list_models()]
        self.gen_model = 'models/gemini-1.5-flash'
        if self.gen_model not in models:
            self.gen_model = next((m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods), 'models/gemini-pro')
            
        self.embed_model = 'models/gemini-embedding-001'
        if self.embed_model not in models:
            self.embed_model = 'models/embedding-001'
        
        self.llm = genai.GenerativeModel(self.gen_model)
        self.vector_store = self._load_vector_store()
        logger.info(f"Phase 4 Backend Initialized.")

    def _load_vector_store(self) -> List[Dict]:
        if not os.path.exists(vector_store_path):
            logger.error(f"Vector store missing at {vector_store_path}")
            return []
        with open(vector_store_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_embedding(self, text: str) -> List[float]:
        try:
            result = genai.embed_content(model=self.embed_model, content=text, task_type="retrieval_query")
            if hasattr(result, 'embedding'): return result.embedding
            return result['embedding']
        except Exception:
            # Fallback
            result = genai.embed_content(model=self.embed_model, content=text, task_type="retrieval_document")
            return result.embedding if hasattr(result, 'embedding') else result['embedding']

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
            "You are a factual Tata Mutual Fund Assistant. Answer precisely using the context.\n"
            "STRICT RULES:\n"
            "1. Answer based ONLY on context.\n"
            "2. Reject advice/opinions with disclaimer. Link: https://groww.in/blog/how-to-invest-in-mutual-funds\n"
            "3. Say you don't know if info is missing.\n\n"
            f"CONTEXT:\n{context}\n\n"
            f"USER QUERY: {query}\n"
            "ANSWER:"
        )
        try:
            r = self.llm.generate_content(prompt)
            return r.text.strip() if r.candidates else "Blocked."
        except Exception as e:
            return f"Error: {e}"
