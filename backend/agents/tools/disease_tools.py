# backend/agents/tools/disease_tools.py
from datetime import datetime
from typing import Dict, Optional, Any
from services.disease_service import PlantHealthService
from utils.logger import get_logger

logger = get_logger(__name__)
health_service = PlantHealthService()

async def diagnose_disease(image_b64: str, crop: Optional[str] = None) -> Dict[str, Any]:
    """Diagnose plant disease from an image."""
    try:
        logger.info(f"Starting disease diagnosis for crop: {crop or 'unknown'}")
        diagnosis = await health_service.diagnose(image_b64, crop)
        return diagnosis
    except Exception as e:
        logger.error(f"Disease diagnosis failed: {str(e)}")
        raise

async def get_treatments(disease_name: str, crop: Optional[str] = None) -> Dict[str, Any]:
    """Get treatment recommendations for a specific disease."""
    return await health_service.get_treatments(disease_name, crop)

async def get_prevention_tips(disease_name: str, crop: Optional[str] = None) -> Dict[str, Any]:
    """Get prevention tips for a specific disease."""
    return await health_service.get_prevention_tips(disease_name, crop)

def get_current_time() -> str:
    """Returns the current date and time."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
