from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_engine import RAGChatbot
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Tata Mutual Fund RAG API - Phase 4")

# Configure CORS for React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

@app.get("/api")
def read_root():
    return {"status": "Backend Active"}

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return {}

@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if bot is None:
        raise HTTPException(status_code=500, detail="Chatbot offline.")
    
    try:
        answer = bot.ask(request.query)
        return ChatResponse(answer=answer)
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
