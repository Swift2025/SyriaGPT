from fastapi import FastAPI
from api.authentication.routes import router as auth_router
from api.questions import questions_router
from api.answers import answers_router
from api.ai.intelligent_qa import router as intelligent_qa_router
import asyncio
import logging

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Syria GPT API", 
    version="1.0.0",
    description="Intelligent Q&A system for Syria-related questions powered by Google Gemini AI"
)

app.include_router(auth_router)
app.include_router(questions_router)
app.include_router(answers_router)
app.include_router(intelligent_qa_router)

@app.on_event("startup")
async def startup_event():
    """
    Initialize the Syria GPT Q&A system on startup.
    This loads all knowledge data from the data folder into Redis and Qdrant.
    """
    try:
        logger.info("🚀 Starting Syria GPT application...")
        
        # Import here to avoid circular imports
        from services.ai.intelligent_qa_service import intelligent_qa_service
        
        # Initialize the system
        init_result = await intelligent_qa_service.initialize_system()
        
        if init_result.get("status") == "success":
            logger.info("✅ Syria GPT system initialized successfully")
        else:
            logger.error(f"❌ System initialization failed: {init_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"❌ Startup initialization failed: {e}")
        # Don't fail the startup, just log the error

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Syria GPT!", 
        "version": "1.0.0",
        "ai_provider": "Google Gemini",
        "features": ["Intelligent Q&A", "Vector Search", "Redis Caching", "Multilingual Support"]
    }

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}! Welcome to Syria GPT."}
