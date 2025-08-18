from google.adk import Agent
from pydantic import BaseModel
from agents.tools.schemes_tools import (
    search_schemes,
    get_scheme_details,
    get_current_time,
)
from agents.base_agent import BaseAgent


class SchemeSearchQuery(BaseModel):
    query: str
    state: str | None = None


class SchemesAgent(BaseAgent):
    """Schemes Agent with LLM integration for government scheme information."""

    def __init__(self):
        system_prompt = f"""
        You are a Government Schemes Expert specializing in agricultural programs.
        Your role is to help farmers find and understand government schemes and subsidies.

        Your responsibilities:
        1. Identify relevant schemes using semantic search
        2. Explain the schemes in simple, local language
        3. Provide clear application instructions and requirements
        4. Highlight eligibility criteria and key benefits

        Always be:
        - Clear and concise
        - Culturally sensitive
        - Action-oriented
        - Up-to-date with the latest scheme information

        Today's date is {get_current_time()}.
        """

        super().__init__(
            name="SchemesAgent",
            description="Agent for finding and explaining government schemes using RAG.",
            system_prompt=system_prompt,
        )

        # Create the Google ADK agent internally
        self.agent = Agent(
            name="SchemesAgent",
            description="Agent for finding and explaining government schemes using RAG.",
            instruction=system_prompt,
            tools=[search_schemes, get_scheme_details],
        )

    async def search(self, query_data: dict):
        """Search for government schemes using semantic search."""
        query_obj = SchemeSearchQuery(**query_data)
        return await search_schemes(query=query_obj.query, state=query_obj.state)

    async def check_subsidy(self, item: str, state: str):
        """Check subsidy information for an item."""
        # Placeholder logic (replace with DB/API lookup later)
        return {
            "item": item,
            "state": state,
            "subsidy_available": True,
            "subsidy_percentage": "50%",
            "max_amount": "₹10,000",
            "application_process": "Apply through local agricultural office",
        }
