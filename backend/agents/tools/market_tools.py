# backend/agents/tools/market_tools.py
from datetime import datetime
from typing import Dict, Any, Optional

from services.market_service import MarketService
from utils.logger import get_logger

logger = get_logger(__name__)
market_service = MarketService()

def get_current_time() -> str:
    """Returns the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def get_market_insights(commodity: str, lat: float, lng: float) -> Dict[str, Any]:
    """Get comprehensive market insights including prices, trends, and weather impact."""
    logger.info(f"Getting market insights for {commodity} at ({lat}, {lng})")
    try:
        return await market_service.get_market_insights(commodity, lat, lng)
    except Exception as e:
        logger.error(f"Error in get_market_insights tool: {e}")
        raise

async def get_price_trends(commodity: str, state: str, days: int = 30) -> Dict[str, Any]:
    """Get price trends for a commodity over a number of days."""
    logger.info(f"Getting price trends for {commodity} in {state} for {days} days.")
    try:
        return await market_service.get_price_trends(commodity, state, days)
    except Exception as e:
        logger.error(f"Error in get_price_trends tool: {e}")
        raise
