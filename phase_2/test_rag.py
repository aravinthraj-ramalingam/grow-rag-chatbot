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

VECTOR_STORE_PATH = os.path.join(current_dir, "vector_store.json")
API_KEY = os.environ.get("GOOGLE_API_KEY")

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    v1 = np.array(v1)
    v2 = np.array(v2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def get_query_embedding(query: str) -> List[float]:
    genai.configure(api_key=API_KEY)
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=query,
        task_type="retrieval_query"
    )
    # Robust extraction
    if hasattr(result, 'embedding'):
        return result.embedding
    elif isinstance(result, dict) and 'embedding' in result:
        return result['embedding']
    elif hasattr(result, 'values'):
        return result.values
    else:
        # Check for list of embeddings just in case
        if hasattr(result, 'embeddings'):
            emb = result.embeddings[0]
            return emb.values if hasattr(emb, 'values') else emb
        raise KeyError(f"Could not find embedding in response. Keys/Attrs: {dir(result)}")

def search(query: str, top_k: int = 3):
    if not os.path.exists(VECTOR_STORE_PATH):
        logger.error(f"Vector store not found at {VECTOR_STORE_PATH}. Run indexer.py first.")
        return

    with open(VECTOR_STORE_PATH, 'r', encoding='utf-8') as f:
        vector_store = json.load(f)

    logger.info(f"Searching for: {query}")
    try:
        query_embedding = get_query_embedding(query)
    except Exception as e:
        logger.error(f"Embedding error: {e}")
        return
    
    scores = []
    for item in vector_store:
        score = cosine_similarity(query_embedding, item["embedding"])
        scores.append((score, item))
    
    # Sort by score descending
    scores.sort(key=lambda x: x[0], reverse=True)
    
    results = scores[:top_k]
    
    print(f"\n--- Results for: {query} ---")
    for i, (score, item) in enumerate(results):
        print(f"\nResult {i+1} (Similarity: {score:.4f})")
        print(f"Content: {item['text']}")
        print(f"Metadata: {item['metadata']}")

if __name__ == "__main__":
    queries = [
        "What is the exit load for Tata Large Cap Fund?",
        "Who is the fund manager for Tata ELSS?",
        "Minimum SIP amount for Tata Multicap?",
        "What is the expense ratio of Tata Flexi Cap?"
    ]
    for q in queries:
        search(q)
