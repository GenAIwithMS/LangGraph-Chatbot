from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router.chat import chat_router
from app.router.health import health_router
from database.init_db import init_database


def create_app():
    app = FastAPI(
        title="LangGraph Chatbot API",
        description="FastAPI backend for LangGraph-powered chatbot also multi-thread support",
        version="1.0.0"
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    

    init_database()
            
    # Include routers
    app.include_router(chat_router, prefix="/api", tags=["chat"])
    app.include_router(health_router, prefix="/api", tags=["health"])
    return app

