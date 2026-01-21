"""
Sakti-Link Edge Server
Main application entry point for Community Edge Server (Block 2)
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from loguru import logger
import sys

from edge_server.api.v1 import voice, learning, gigs, legal, skills, system
from edge_server.core.config import settings
from edge_server.db.database import init_db, close_db
from edge_server.ai.model_manager import ModelManager

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="INFO" if not settings.DEBUG else "DEBUG"
)
logger.add(
    "logs/edge_server.log",
    rotation="100 MB",
    retention="30 days",
    level="INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting Sakti-Link Edge Server...")
    
    # Initialize database
    await init_db()
    logger.info("Database initialized")
    
    # Initialize AI model manager
    model_manager = ModelManager()
    await model_manager.initialize()
    app.state.model_manager = model_manager
    logger.info("AI models loaded")
    
    logger.info(f"Edge Server running in {'OFFLINE' if settings.OFFLINE_MODE else 'ONLINE'} mode")
    logger.info(f"Supported languages: {', '.join(settings.SUPPORTED_LANGUAGES)}")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Sakti-Link Edge Server...")
    await model_manager.cleanup()
    await close_db()
    logger.info("Cleanup completed")


# Create FastAPI app
app = FastAPI(
    title="Sakti-Link Edge Server",
    description="Voice-first, offline-first AI platform for women's empowerment",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "message": str(exc) if settings.DEBUG else "An error occurred"
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "sakti-link-edge",
        "version": "1.0.0",
        "mode": "offline" if settings.OFFLINE_MODE else "online"
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Sakti-Link Edge Server",
        "version": "1.0.0",
        "description": "Voice-first, offline-first empowerment platform",
        "status": "operational"
    }


# Include API routers
app.include_router(voice.router, prefix="/api/v1/voice", tags=["Voice"])
app.include_router(learning.router, prefix="/api/v1/learning", tags=["Learning"])
app.include_router(gigs.router, prefix="/api/v1/gigs", tags=["Gigs"])
app.include_router(legal.router, prefix="/api/v1/legal", tags=["Legal"])
app.include_router(skills.router, prefix="/api/v1/skills", tags=["Skills"])
app.include_router(system.router, prefix="/api/v1/system", tags=["System"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )
