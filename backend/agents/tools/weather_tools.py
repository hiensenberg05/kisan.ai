# backend/agents/tools/weather_tools.py
from datetime import datetime
from typing import Any, Dict, Optional

from services.weather_service import weather_service
from utils.logger import get_logger

logger = get_logger(__name__)

def get_current_time() -> str:
    """Returns the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def get_current_weather(lat: float, lon: float) -> Dict[str, Any]:
    """Get current weather conditions for a specific location."""
    logger.info(f"Getting current weather for lat={lat}, lon={lon}")
    try:
        return await weather_service.current(lat, lon)
    except Exception as e:
        logger.error(f"Error in get_current_weather tool: {e}")
        raise

async def get_weather_forecast(lat: float, lon: float) -> Dict[str, Any]:
    """Get the weather forecast for a specific location."""
    logger.info(f"Getting weather forecast for lat={lat}, lon={lon}")
    try:
        return await weather_service.forecast(lat, lon)
    except Exception as e:
        logger.error(f"Error in get_weather_forecast tool: {e}")
        raise

async def get_farming_advice(lat: float, lon: float, crop: Optional[str] = None) -> Dict[str, Any]:
    """Get farming-specific advice based on weather conditions."""
    logger.info(f"Getting farming advice for lat={lat}, lon={lon}, crop={crop}")
    try:
        advice_data = await weather_service.get_farming_advice(lat, lon)
        if crop:
            current = advice_data["current_weather"]
            forecast = advice_data["forecast"][0]
            crop_advice = _get_crop_specific_advice(crop, current, forecast)
            advice_data["advice"]["crop_specific"] = crop_advice
        return advice_data
    except Exception as e:
        logger.error(f"Error in get_farming_advice tool: {e}")
        raise

def _get_crop_specific_advice(crop: str, current: Dict, forecast: Dict) -> str:
    """Helper to generate crop-specific weather advice."""
    crop = crop.lower()
    temp = current.get("temperature", 0)
    humidity = current.get("humidity", 0)
    wind_speed = current.get("wind_speed", 0)
    advice = []

    if "rice" in crop:
        if temp < 20: advice.append("Rice is sensitive to cold.")
        if humidity > 80: advice.append("High humidity increases disease risk.")
    elif "wheat" in crop:
        if temp > 25: advice.append("High temperatures can reduce yield.")
        if "rain" in forecast.get("weather", {}).get("description", "").lower():
            advice.append("Harvest before rain to avoid quality loss.")
    elif "cotton" in crop:
        if humidity > 85: advice.append("High humidity increases boll rot risk.")
        if wind_speed > 10: advice.append("Strong winds can damage bolls.")
    else:
        if temp < 10: advice.append("Protect sensitive crops from cold stress.")
        if temp > 35: advice.append("Provide shade or mulch to reduce heat stress.")

    return " ".join(advice) if advice else "No specific weather concerns for this crop."
