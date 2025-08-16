import os
import uvicorn
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import API router
from api.routes import router as api_router

# Configure logging
logger.add(
    "logs/app.log",
    rotation="500 MB",
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    enqueue=True,
    backtrace=True,
    diagnose=True
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI app"""
    # Startup
    logger.info("Starting Kisan.AI Backend Service")
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    yield
    
    # Shutdown
    logger.info("Shutting down Kisan.AI Backend Service")

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

# Include API routes
app.include_router(api_router, prefix="/api/v1")

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
    # Run the FastAPI application
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=os.getenv("API_DEBUG", "True").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower(),
        workers=int(os.getenv("WORKERS", "1")),
    )
