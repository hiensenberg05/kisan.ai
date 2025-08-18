"""
Market Agent for providing agricultural market insights.
Integrates with MarketService to provide comprehensive market analysis.
"""
from google.adk import Agent
from agents.tools.market_tools import (
    get_market_insights,
    get_price_trends,
    get_current_time,
)

class MarketAgent:
    """Market Agent class for compatibility with orchestrator imports."""
    
    def __init__(self):
        self.agent = market_agent
    
    async def get_prices(self, commodity, location, timeframe="7d"):
        """Get current market prices for a commodity."""
        return await get_market_insights(
            commodity=commodity,
            location=location,
            timeframe=timeframe
        )
    
    async def analyze_trends(self, commodity, location):
        """Analyze price trends for a commodity."""
        return await get_price_trends(
            commodity=commodity,
            location=location
        )
    
    async def get_recommendations(self, commodity, quantity, location):
        """Get selling recommendations."""
        return {
            "commodity": commodity,
            "quantity": quantity,
            "location": location,
            "recommendations": [
                "Monitor prices for next 2-3 days before selling",
                "Consider selling in nearby mandis for better rates",
                "Check transportation costs to different markets"
            ],
            "best_selling_time": "morning hours (6-10 AM)",
            "market_outlook": "stable"
        }

market_agent = Agent(
    name="MarketAgent",
    description="Agent for providing agricultural market insights and recommendations.",
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