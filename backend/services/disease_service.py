# backend/services/disease_service.py
import base64
import aiohttp
from typing import Optional, Dict, Any
from config import settings

class PlantHealthService:
    """
    Minimal Plant.health API client.
    Adjust endpoint/fields to the actual spec of your account.
    """
    def __init__(self):
        self.base_url = str(settings.PLANT_HEALTH_API_URL)
        self.api_key = settings.PLANT_HEALTH_API_KEY

    async def diagnose(self, image_b64: str, crop: Optional[str] = None) -> Optional[Dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "image": image_b64,
            "crop": crop
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, json=payload, headers=headers, timeout=60) as resp:
                if resp.status == 200:
                    return await resp.json()
                # in practice, parse error body for debugging
                return None

    @staticmethod
    def parse_result(api_json: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Normalize response → {disease, confidence, crop}
        Change these keys to match Plant.health’s actual response.
        """
        try:
            top = api_json.get("predictions", [])[0]
            return {
                "disease": top.get("label") or top.get("name"),
                "confidence": float(top.get("score") or top.get("confidence") or 0),
                "crop": api_json.get("crop")
            }
        except Exception:
            return None
