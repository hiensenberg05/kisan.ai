# backend/services/weather_service.py
import os
import httpx
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from pydantic import BaseModel, Field
from core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

class WeatherData(BaseModel):
    """Weather data model"""
    temperature: float = Field(..., description="Temperature in Celsius")
    feels_like: float = Field(..., description="Feels like temperature in Celsius")
    humidity: int = Field(..., description="Humidity percentage")
    wind_speed: float = Field(..., description="Wind speed in m/s")
    wind_direction: int = Field(..., description="Wind direction in degrees")
    description: str = Field(..., description="Weather condition description")
    icon: str = Field(..., description="Weather icon code")
    timestamp: datetime = Field(..., description="Time of data calculation")

class WeatherForecast(BaseModel):
    """Weather forecast data model"""
    location: str = Field(..., description="Location name")
    current: WeatherData = Field(..., description="Current weather data")
    hourly: list[WeatherData] = Field(..., description="Hourly forecast")
    daily: list[Dict[str, Any]] = Field(..., description="Daily forecast summary")

class WeatherService:
    """Service for fetching weather data from OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = settings.WEATHER_API
        if not self.api_key:
            logger.warning("WEATHER_API not found in settings")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the OpenWeatherMap API"""
        try:
            params = {**params, "appid": self.api_key, "units": "metric"}
            response = await self.client.get(f"{self.base_url}/{endpoint}", params=params)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(f"Weather API request failed: {e}")
            raise
        except Exception as e:
            logger.error(f"Error making weather API request: {e}")
            raise
    
    async def current(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get current weather data for a location
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
            
        Returns:
            Dictionary containing current weather data
        """
        data = await self._make_request(
            "weather",
            {"lat": lat, "lon": lon}
        )
        
        return self._format_current_weather(data)
    
    async def forecast(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get weather forecast for a location
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
            
        Returns:
            Dictionary containing weather forecast
        """
        data = await self._make_request(
            "onecall",
            {
                "lat": lat,
                "lon": lon,
                "exclude": "minutely,alerts",
                "units": "metric"
            }
        )
        
        return self._format_forecast(data)
    
    def _format_current_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format current weather data"""
        return {
            "location": data.get("name", "Unknown"),
            "temperature": data["main"]["temp"],
            "feels_like": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"],
            "wind_direction": data["wind"].get("deg", 0),
            "description": data["weather"][0]["description"],
            "icon": data["weather"][0]["icon"],
            "timestamp": datetime.utcfromtimestamp(data["dt"])
        }
    
    def _format_forecast(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Format forecast data"""
        current = self._format_current_weather({
            "main": data["current"],
            "weather": data["current"]["weather"],
            "wind": data["current"],
            "name": "Current Location",
            "dt": data["current"]["dt"]
        })
        
        hourly = [
            {
                "temperature": hour["temp"],
                "feels_like": hour["feels_like"],
                "humidity": hour["humidity"],
                "wind_speed": hour.get("wind_speed", 0),
                "wind_direction": hour.get("wind_deg", 0),
                "description": hour["weather"][0]["description"],
                "icon": hour["weather"][0]["icon"],
                "timestamp": datetime.utcfromtimestamp(hour["dt"])
            }
            for hour in data.get("hourly", [])[:24]  # Next 24 hours
        ]
        
        daily = [
            {
                "date": datetime.utcfromtimestamp(day["dt"]).strftime("%Y-%m-%d"),
                "temp": {
                    "min": day["temp"]["min"],
                    "max": day["temp"]["max"],
                    "morn": day["temp"].get("morn"),
                    "day": day["temp"].get("day"),
                    "eve": day["temp"].get("eve"),
                    "night": day["temp"].get("night")
                },
                "weather": {
                    "main": day["weather"][0]["main"],
                    "description": day["weather"][0]["description"],
                    "icon": day["weather"][0]["icon"]
                },
                "humidity": day["humidity"],
                "wind_speed": day.get("wind_speed", 0),
                "wind_direction": day.get("wind_deg", 0),
                "pop": day.get("pop", 0)  # Probability of precipitation
            }
            for day in data.get("daily", [])[:7]  # Next 7 days
        ]
        
        return {
            "current": current,
            "hourly": hourly,
            "daily": daily
        }
    
    async def get_farming_advice(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Get farming-specific weather advice
        
        Args:
            lat: Latitude of the location
            lon: Longitude of the location
            
        Returns:
            Dictionary containing farming advice based on weather
        """
        data = await self.forecast(lat, lon)
        current = data["current"]
        daily = data["daily"][0]  # Today's forecast
        
        advice = {
            "irrigation": self._get_irrigation_advice(current, daily),
            "spraying": self._get_spraying_advice(current, daily),
            "harvesting": self._get_harvesting_advice(daily),
            "general_advice": self._get_general_advice(current, daily)
        }
        
        return {
            "current_weather": current,
            "forecast": data["daily"][:3],  # Next 3 days
            "advice": advice
        }
    
    def _get_irrigation_advice(self, current: Dict, daily: Dict) -> str:
        """Get irrigation advice based on weather"""
        if current["humidity"] > 80:
            return "No irrigation needed - high humidity and recent rainfall detected."
        elif current["humidity"] < 40 and daily["temp"]["max"] > 30:
            return "Irrigation recommended - low humidity and high temperatures expected."
        return "Standard irrigation schedule recommended."
    
    def _get_spraying_advice(self, current: Dict, daily: Dict) -> str:
        """Get spraying advice based on weather"""
        if daily["wind_speed"] > 5:  # m/s
            return "Avoid spraying - wind speeds are too high."
        if "rain" in daily["weather"]["description"].lower() or daily["pop"] > 0.3:
            return "Postpone spraying - rain is expected within 24 hours."
        if daily["temp"]["max"] > 30:
            return "Early morning or late evening spraying recommended - high temperatures expected."
        return "Good conditions for spraying."
    
    def _get_harvesting_advice(self, daily: Dict) -> str:
        """Get harvesting advice based on weather"""
        if daily["pop"] > 0.5:  # High chance of precipitation
            return "Consider delaying harvest - wet conditions expected."
        if daily["temp"]["max"] > 35:
            return "Harvest in early morning to avoid heat stress on crops."
        return "Good conditions for harvesting."
    
    def _get_general_advice(self, current: Dict, daily: Dict) -> str:
        """Get general farming advice based on weather"""
        advice = []
        
        if current["temperature"] < 5:
            advice.append("⚠️ Frost warning: Protect sensitive crops from frost.")
        if daily["pop"] > 0.7:
            advice.append("🌧️ Heavy rain expected: Ensure proper drainage in fields.")
        if daily["wind_speed"] > 8:  # m/s
            advice.append("💨 High winds: Secure loose items and protect young plants.")
        if daily["temp"]["max"] > 35:
            advice.append("☀️ Heat advisory: Provide shade for livestock and sensitive crops.")
        
        return " ".join(advice) if advice else "No significant weather advisories."

# Singleton instance
weather_service = WeatherService()