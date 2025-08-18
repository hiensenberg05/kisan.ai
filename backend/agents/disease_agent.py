"""
Disease Agent for handling plant disease diagnosis using PlantHealth API.
Provides a high-level interface for disease detection and recommendations.
"""
from google.adk import Agent
from agents.tools.disease_tools import (
    diagnose_disease,
    get_treatments,
    get_prevention_tips,
    get_current_time,
)
from agents.base_agent import BaseAgent


# First define the actual Google ADK agent
disease_agent = Agent(
    name="PlantDiseaseExpert",
    instruction=f"""
    You are an AI Plant Pathologist Assistant. Your role is to help farmers 
    identify plant diseases and provide actionable recommendations.
    
    Guidelines:
    - Be clear, concise, and professional
    - Use simple language that farmers can understand
    - Focus on practical, actionable advice
    - When in doubt, recommend consulting a local agricultural expert
    - Always include prevention tips for future reference

    Today's date is {get_current_time()}.
    """,
    tools=[
        diagnose_disease,
        get_treatments,
        get_prevention_tips,
    ],
)


class DiseaseAgent(BaseAgent):
    """Wrapper around disease_agent with extra business logic."""

    def __init__(self):
        system_prompt = """
        You are a Plant Disease Expert providing accurate diagnosis and treatment recommendations.
        Your goal is to help farmers identify plant diseases and suggest appropriate treatments.
        Be clear, concise, and focus on practical, actionable advice for farmers.
        """
        super().__init__(
            name="PlantDiseaseExpert",
            system_prompt=system_prompt,
        )
        self.agent = disease_agent

    async def identify(self, request_data):
        """Identify disease from image data."""
        try:
            return await diagnose_disease(
                image_b64=request_data.get("image_b64", ""),
                crop=request_data.get("crop")
            )
        except Exception as e:
            return {"error": str(e)}

    async def assess_risk(self, crop, weather_conditions):
        """Assess disease risk based on crop and weather conditions."""
        risk_level = "low"
        factors = []

        if weather_conditions.get("humidity", 0) > 80:
            risk_level = "high"
            factors.append("high humidity")

        if weather_conditions.get("temperature", 0) > 30:
            risk_level = "medium" if risk_level == "low" else "high"
            factors.append("high temperature")

        return {
            "crop": crop,
            "risk_level": risk_level,
            "risk_factors": factors,
            "recommendations": [
                "Monitor crops regularly for early signs of disease",
                "Ensure proper ventilation and spacing",
                "Apply preventive treatments if risk is high",
            ],
        }
