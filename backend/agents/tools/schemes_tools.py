# backend/agents/tools/schemes_tools.py
from datetime import datetime
from typing import Any, Dict, List, Optional

from services.scheme_service import scheme_service
from utils.logger import get_logger

logger = get_logger(__name__)

def get_current_time() -> str:
    """Returns the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def search_schemes(
    query: str,
    state: Optional[str] = None,
    category: Optional[str] = None,
    top_k: int = 5,
) -> List[Dict[str, Any]]:
    """Search for government schemes using natural language."""
    logger.info(f"Searching for schemes with query: '{query}'")
    try:
        return scheme_service.search_schemes(query, state, category, top_k)
    except Exception as e:
        logger.error(f"Error in search_schemes tool: {e}")
        raise


def get_scheme_details(scheme_id: str) -> Optional[Dict[str, Any]]:
    """Get detailed information about a specific scheme by its ID."""
    logger.info(f"Getting details for scheme ID: {scheme_id}")
    try:
        return scheme_service.get_scheme_by_id(scheme_id)
    except Exception as e:
        logger.error(f"Error in get_scheme_details tool: {e}")
        raise
