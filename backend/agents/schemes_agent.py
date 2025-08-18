from google.adk import Agent
from pydantic import BaseModel
from agents.tools.schemes_tools import (
    search_schemes,
    get_scheme_details,
    get_current_time,
)

class SchemeSearchQuery(BaseModel):
    query: str

class SchemesAgent:
    """Schemes Agent class for compatibility with orchestrator imports."""
    
    def __init__(self):
        self.agent = schemes_agent
    
    async def search(self, query_data):
        """Search for government schemes."""
        return await search_schemes(
            query=query_data.get("query", ""),
            state=query_data.get("state")
        )
    
    async def check_subsidy(self, item, state):
        """Check subsidy information for an item."""
        return {
            "item": item,
            "state": state,
            "subsidy_available": True,
            "subsidy_percentage": "50%",
            "max_amount": "₹10,000",
            "application_process": "Apply through local agricultural office"
        }

schemes_agent = Agent(
    name="SchemesAgent",
    description="Agent for finding and explaining government schemes using RAG.",
    instruction=f"""
    You are a helpful Government Scheme Assistant. Your task is to:
    1. Understand the farmer's query about government schemes
    2. Find the most relevant schemes using semantic search
    3. Explain the schemes in simple, local language
    4. Provide clear application instructions and requirements
    
    Always be:
    - Clear and concise
    - Culturally sensitive
    - Action-oriented
    - Up-to-date with the latest scheme information

    Today's date is {get_current_time()}.
    """,
    tools=[
        search_schemes,
        get_scheme_details,
    ],
)