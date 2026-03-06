from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from phase_3.rag_engine import RAGChatbot
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tata Mutual Fund RAG API")

# Initialize the RAG bot
try:
    bot = RAGChatbot()
except Exception as e:
    logger.error(f"Failed to initialize RAG Chatbot: {e}")
    bot = None

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str

@app.get("/")
def read_root():
    return {"status": "Tata Mutual Fund RAG API is running"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if bot is None:
        raise HTTPException(status_code=500, detail="Chatbot not initialized. Check API Key.")
    
    try:
        answer = bot.ask(request.query)
        return ChatResponse(answer=answer)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
