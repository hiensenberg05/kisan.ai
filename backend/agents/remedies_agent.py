from google.adk import Agent
from agents.tools.remedies_tools import (
    get_economical_remedies,
    compare_remedies,
    get_current_time,
)

class RemediesAgent:
    """Remedies Agent class for compatibility with orchestrator imports."""
    
    def __init__(self):
        self.agent = remedies_agent
    
    async def suggest_treatment(self, disease, crop, severity="medium"):
        """Suggest treatment options for a disease."""
        return await get_economical_remedies(
            disease=disease,
            crop=crop,
            severity=severity
        )

remedies_agent = Agent(
    name="RemediesAgent",
    description="Agent for suggesting economical remedies for plant diseases.",
    instruction=f"""
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
    """,
    tools=[
        get_economical_remedies,
        compare_remedies,
    ],
)