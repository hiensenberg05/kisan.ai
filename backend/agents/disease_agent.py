"""
Disease Agent for handling plant disease diagnosis using Plant.Health API.
Provides a high-level interface for disease detection and recommendations.
"""
from google.adk import Agent
from agents.tools.disease_tools import (
    diagnose_disease,
    get_treatments,
    get_prevention_tips,
    get_current_time,
)

class DiseaseAgent:
    """Disease Agent class for compatibility with orchestrator imports."""
    
    def __init__(self):
        self.agent = disease_agent
    
    async def identify(self, request_data):
        """Identify disease from image data."""
        return await diagnose_disease(
            image_b64=request_data.get("image_b64", ""),
            crop=request_data.get("crop")
        )
    
    async def assess_risk(self, crop, weather_conditions):
        """Assess disease risk based on crop and weather conditions."""
        # Simple risk assessment based on weather
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
                "Apply preventive treatments if risk is high"
            ]
        }

disease_agent = Agent(
    name="PlantDiseaseExpert",
    description="Agent for handling plant disease diagnosis and recommendations.",
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
