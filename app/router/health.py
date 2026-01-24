from fastapi import APIRouter

health_router = APIRouter()

@health_router.get("/")
async def root():
    return {
        "message": "LangGraph Chatbot API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@health_router.get("/health")
async def health():
    return {"status": "ok"}