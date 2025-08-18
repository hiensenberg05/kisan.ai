"""
Kisan.AI Backend Service

This module serves as the main entry point for the Kisan.AI FastAPI application.
It sets up the FastAPI app, middleware, routes, and handles the application lifecycle.
"""
import os
import time
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, RedirectResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.gzip import GZipMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import sentry_sdk
from pydantic import BaseModel

# Load environment variables
load_dotenv()

# Import API routers
from api.routes import router as api_router
from core.config import settings

# Configure Sentry for error tracking
if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        environment=settings.ENVIRONMENT,
        traces_sample_rate=1.0,
        profiles_sample_rate=1.0,
    )

# Configure logging
os.makedirs("logs", exist_ok=True)
logger.add(
    "logs/app.log",
    rotation="500 MB",
    retention="30 days",
    compression="zip",
    level=settings.LOG_LEVEL,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
           "<level>{message}</level>",
    enqueue=True,
    backtrace=True,
    diagnose=True
)

# Custom exception handlers
class KisanAIException(Exception):
    """Base exception for Kisan.AI application"""
    def __init__(self, message: str, status_code: int = 400, **kwargs):
        self.message = message
        self.status_code = status_code
        self.details = kwargs

# Request logging middleware
async def log_requests(request: Request, call_next):
    """Middleware to log all incoming requests"""
    start_time = time.time()
    
    # Skip logging for health checks
    if request.url.path == "/api/v1/health":
        return await call_next(request)
    
    logger.info(f"Request: {request.method} {request.url}")
    
    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        logger.info(
            f"Response: {request.method} {request.url} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.2f}ms"
        )
        return response
    except Exception as e:
        logger.error(f"Error processing {request.url}: {str(e)}")
        raise

# Application lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app"""
    # Startup
    startup_time = time.strftime("%Y-%m-%d %H:%M:%S")
    logger.info("=" * 50)
    logger.info(f"Starting Kisan.AI Backend Service - {startup_time}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info("=" * 50)
    
    # Create necessary directories
    os.makedirs("logs", exist_ok=True)
    os.makedirs("data/cache", exist_ok=True)
    
    # Initialize services
    try:
        # Initialize database connection
        # await database.connect()
        
        # Initialize AI models
        # await initialize_models()
        
        logger.info("✅ Services initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize services: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Kisan.AI Backend Service")
    # await database.disconnect()
    logger.info("✅ Cleanup completed")

# Create FastAPI app
app = FastAPI(
    title="Kisan.AI Backend API",
    description="Backend service for Kisan.AI - Empowering farmers with AI",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
origins = os.getenv("ALLOWED_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes (router already has prefix configured)
app.include_router(api_router)

@app.get("/")
async def root():
    """Root endpoint with basic API information"""
    return {
        "message": "Welcome to Kisan.AI Backend Service",
        "status": "operational",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Error handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    # To run the application, use the uvicorn command:
    # uvicorn backend.main:app --reload
    logger.warning("This script is not meant to be run directly. Use uvicorn.")
    pass
