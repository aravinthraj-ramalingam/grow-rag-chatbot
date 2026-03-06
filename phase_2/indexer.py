import os
import json
import logging
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List, Dict
import time

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Absolute path resolution
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
env_path = os.path.join(root_dir, ".env")
load_dotenv(dotenv_path=env_path)

DATA_PATH = os.path.join(root_dir, "phase_1", "fund_data.json")
VECTOR_STORE_PATH = os.path.join(current_dir, "vector_store.json")
API_KEY = os.environ.get("GOOGLE_API_KEY")

def get_single_embedding(text: str) -> List[float]:
    genai.configure(api_key=API_KEY)
    # Using the most stable single-content method
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    # Single embedding response has 'embedding' (singular) attribute/key
    if hasattr(result, 'embedding'):
        return result.embedding
    elif isinstance(result, dict) and 'embedding' in result:
        return result['embedding']
    else:
        # Final attempt: check for 'values' if it's returning the embedding object directly
        if hasattr(result, 'values'):
            return result.values
        raise KeyError(f"Could not find 'embedding' in response types: {type(result)}")

def prepare_chunks(fund_data: List[Dict]) -> List[Dict]:
    chunks = []
    for fund in fund_data:
        name = fund.get("fund_name", "Unknown")
        url = fund.get("url", "")
        # Summary
        chunks.append({"text": f"Fund Name: {name}. NAV: {fund.get('nav')}. Risk: {fund.get('riskometer')}.", "metadata": {"name": name, "url": url, "cat": "summary"}})
        # FAQs
        for faq in fund.get("faqs", []):
            q, a = faq.get("question", ""), faq.get("answer", "")
            if len(q) > 5:
                chunks.append({"text": f"Question about {name}: {q} Answer: {a}", "metadata": {"name": name, "url": url, "cat": "faq"}})
        # Min
        min_i = fund.get("min_investments", {})
        if min_i:
            chunks.append({"text": f"{name} Minimum Investments: {min_i}", "metadata": {"name": name, "url": url, "cat": "min"}})
        # Returns
        for r in fund.get("returns_and_rankings", []):
            chunks.append({"text": f"{name} returns/ranking: {r}", "metadata": {"name": name, "url": url, "cat": "returns"}})
        # Mgmt
        for m in fund.get("fund_management", []):
            chunks.append({"text": f"Fund Manager for {name}: {m.get('name')}. Details: {m.get('details')}", "metadata": {"name": name, "url": url, "cat": "mgmt"}})
    return chunks

def run():
    if not API_KEY:
        logger.error("GOOGLE_API_KEY missing.")
        return
    if not os.path.exists(DATA_PATH):
        logger.error(f"Data not found at {DATA_PATH}")
        return
        
    with open(DATA_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    chunks = prepare_chunks(data)
    logger.info(f"Derived {len(chunks)} chunks. Generating embeddings one-by-one for stability...")
    
    vector_store = []
    for i, c in enumerate(chunks):
        try:
            emb = get_single_embedding(c["text"])
            vector_store.append({"id": f"id_{i}", "text": c["text"], "metadata": c["metadata"], "embedding": emb})
            if (i+1) % 10 == 0:
                logger.info(f"Progress: {i+1}/{len(chunks)}...")
        except Exception as e:
            logger.error(f"Error at chunk {i}: {e}")
            # Keep going if possible or stop? Let's stop to be safe.
            return
    
    with open(VECTOR_STORE_PATH, 'w', encoding='utf-8') as f:
        json.dump(vector_store, f, indent=2)
    logger.info(f"SUCCESS! Saved {len(vector_store)} vectors to {VECTOR_STORE_PATH}")

if __name__ == "__main__":
    run()
