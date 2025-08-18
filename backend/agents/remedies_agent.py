from google.adk import Agent
from agents.tools.remedies_tools import (
    get_economical_remedies,
    compare_remedies,
    get_current_time,
)
from agents.base_agent import BaseAgent


class RemediesAgent(BaseAgent):
    """Wrapper for the Remedies Agent with LLM + tool integration."""

    def __init__(self):
        system_prompt = f"""
        You are an Agricultural Remedies Specialist. Your task is to:
        1. Analyze disease diagnosis
        2. Find the most cost-effective remedies
        3. Consider organic alternatives
        4. Provide clear application instructions
        5. Include safety precautions

        Always prioritize:
        - Cost-effectiveness
        - Availability
        - Safety
        - Environmental impact

        Today's date is {get_current_time()}.
        """

        super().__init__(
            name="RemediesAgent",
            description="Agent for suggesting economical remedies for plant diseases.",
            system_prompt=system_prompt,
        )

        # Create the Google ADK agent internally
        self.agent = Agent(
            name="RemediesAgent",
            description="Agent for suggesting economical remedies for plant diseases.",
            instruction=system_prompt,
            tools=[get_economical_remedies, compare_remedies],
        )

    async def suggest_treatment(self, disease, crop, severity="medium"):
        """Suggest treatment options for a disease using the ADK agent."""
        query = f"Suggest remedies for {disease} in {crop} (severity: {severity})."
        return await self.agent.run(query)
