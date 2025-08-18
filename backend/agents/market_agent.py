"""
Market Agent for providing agricultural market insights.
Integrates with MarketService and LLM to provide comprehensive market analysis.
"""
from google.adk import Agent
from agents.tools.market_tools import (
    get_market_insights,
    get_price_trends,
    get_current_time,
)
from agents.base_agent import BaseAgent


# First define the raw Google ADK agent
market_agent = Agent(
    name="MarketAgent",
    instruction=f"""
    You are an Agricultural Market Analyst providing insights to farmers.
    Your goal is to help farmers make informed decisions about when and where to sell their produce.
    Consider market prices, trends, and weather conditions in your analysis.
    Provide clear, actionable recommendations in simple language.
    
    Today's date is {get_current_time()}.
    """,
    tools=[
        get_market_insights,
        get_price_trends,
    ],
)


class MarketAgent(BaseAgent):
    """Wrapper around market_agent with extra business logic."""

    def __init__(self):
        system_prompt = """
        You are an Agricultural Market Analyst providing insights to farmers.
        Your goal is to help farmers make informed decisions about when and where to sell their produce.
        Consider market prices, trends, and weather conditions in your analysis.
        Provide clear, actionable recommendations in simple language.
        """
        super().__init__(
            name="MarketAgent",
            description="Provides real-time market prices, trends, and selling recommendations for agricultural produce",
            system_prompt=system_prompt
        )
        self.agent = market_agent

    async def get_prices(self, commodity: str, lat: float, lng: float, timeframe: int = 7):
        """Get current market prices for a commodity."""
        try:
            return await get_market_insights(
                commodity=commodity,
                lat=lat,
                lng=lng
            )
        except Exception as e:
            return {"error": str(e)}

    async def analyze_trends(self, commodity: str, state: str, days: int = 30):
        """Analyze price trends for a commodity."""
        try:
            return await get_price_trends(
                commodity=commodity,
                state=state,
                days=days
            )
        except Exception as e:
            return {"error": str(e)}

    async def get_recommendations(self, commodity: str, quantity: float, location: str):
        """Get selling recommendations (heuristic, not from service)."""
        return {
            "commodity": commodity,
            "quantity": quantity,
            "location": location,
            "recommendations": [
                "Monitor prices for next 2-3 days before selling",
                "Consider selling in nearby mandis for better rates",
                "Check transportation costs to different markets",
            ],
            "best_selling_time": "morning hours (6-10 AM)",
            "market_outlook": "stable",
        }
