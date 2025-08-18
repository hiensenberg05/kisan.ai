from google.adk import Agent
from agents.tools.weather_tools import (
    get_current_weather,
    get_weather_forecast,
    get_farming_advice,
    get_current_time,
)

class WeatherAgent:
    """Weather Agent class for compatibility with orchestrator imports."""
    
    def __init__(self):
        self.agent = weather_agent
    
    async def get_forecast(self, location, days=7):
        """Get weather forecast for a location."""
        return await get_weather_forecast(
            location=location,
            days=days
        )
    
    async def get_farming_advice(self, location, crop):
        """Get farming advice based on weather conditions."""
        return await get_farming_advice(
            location=location,
            crop=crop
        )
    
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

weather_agent = Agent(
    name="WeatherAgent",
    description="Agent for providing weather information and farming advice.",
    instruction=f"""
    You are a Weather & Farming Advisor for Indian farmers.
    
    Your responsibilities:
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