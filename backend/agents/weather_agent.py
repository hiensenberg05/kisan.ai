from google.adk import Agent
from agents.tools.weather_tools import (
    get_current_weather,
    get_weather_forecast,
    get_farming_advice,
    get_current_time,
)
from agents.base_agent import BaseAgent


class WeatherAgent(BaseAgent):
    """Weather Agent with LLM integration for weather and farming advice."""

    def __init__(self):
        system_prompt = """
        You are an Agricultural Weather Expert. Your role is to provide accurate weather
        information and farming-specific advice based on current and forecasted conditions.
        Be clear, concise, and focus on actionable insights for farmers.
        """
        super().__init__(
            name="WeatherAgent",
            description="Agent for providing weather information and farming advice.",
            system_prompt=system_prompt
        )

        # ✅ Define ADK agent inside
        self.agent = Agent(
            name="WeatherAgent",
            description="Agent for providing weather information and farming advice.",
            instruction=f"""
            You are an Agricultural Weather Expert. Your task is to analyze weather data
            and provide farming-specific recommendations.:
            1. Provide accurate weather information
            2. Offer farming-specific advice based on weather conditions
            3. Explain weather impacts on different crops
            4. Suggest preventive measures for adverse weather
            
            Always be:
            - Clear and concise
            - Culturally appropriate
            - Actionable in your advice
            - Sensitive to regional farming practices

            Today's date is {get_current_time()}.
            """,
            tools=[
                get_current_weather,
                get_weather_forecast,
                get_farming_advice,
            ],
        )

    async def get_forecast(self, lat: float, lon: float, days=7):
        """Get weather forecast for a location."""
        return await get_weather_forecast(lat=lat, lon=lon)

    async def get_farming_advice(self, lat: float, lon: float, crop: str):
        """Get farming advice based on weather conditions."""
        return await get_farming_advice(lat=lat, lon=lon, crop=crop)

    async def get_disease_risk(self, location, disease):
        """Get disease risk assessment based on weather."""
        return {
            "location": location,
            "disease": disease,
            "risk_level": "medium",
            "weather_factors": ["humidity", "temperature"],
            "recommendations": [
                "Monitor crops closely for disease symptoms",
                "Apply preventive treatments if conditions worsen"
            ]
        }
