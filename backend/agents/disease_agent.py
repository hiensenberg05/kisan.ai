# backend/agents/disease_agent.py
from schemas.schemas import DiagnoseResult
from services.disease_service import PlantHealthService
from google_adk import Agent, Tool, Prompt

class DiseaseAgent:
    def __init__(self):
        self.client = PlantHealthService()
        self.prompt = Prompt(
            system="""
            You are a Crop Disease Expert.
            - Input: plant photo + crop name.
            - Output: most likely disease, short name only.
            - Avoid long explanations; return clear disease labels.
            """
        )
        self.agent = Agent(
            name="DiseaseAgent",
            prompt=self.prompt,
            tools=[
                Tool("diagnose", self.client.diagnose, description="Diagnose plant diseases using Plant.Health API")
            ]
        )

    async def diagnose(self, image_b64: str, crop: str = None) -> DiagnoseResult:
        result = await self.agent.run({"image_b64": image_b64, "crop": crop})
        parsed = self.client.parse_result(result)
        return DiagnoseResult(**parsed) if parsed else None
