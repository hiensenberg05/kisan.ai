"""
Kisan.AI Backend API Package

This package contains all API routes and endpoints for the Kisan.AI backend service.
"""

# Import the router to make it available when the package is imported
from .routes import router as api_router

__all__ = ["api_router"]
