# backend/agents/tools/remedies_tools.py
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional

from services.price_service import PriceService
from utils.logger import get_logger

logger = get_logger(__name__)
price_service = PriceService()

def get_current_time() -> str:
    """Returns the current date and time.""" 
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

async def get_economical_remedies(diagnosis: Dict[str, Any]) -> Dict[str, Any]:
    """Get cost-effective remedies for a disease based on a diagnosis."""
    logger.info(f"Getting economical remedies for {diagnosis.get('disease_name')}")
    try:
        remedies_tasks = [
            _get_remedy_details(chem, diagnosis.get('affected_plant', ''))
            for chem in diagnosis.get('recommended_chemicals', [])[:3]
        ]
        remedies = await asyncio.gather(*remedies_tasks, return_exceptions=True)
        
        valid_remedies = [r for r in remedies if isinstance(r, dict) and not isinstance(r, Exception)]
        valid_remedies.sort(key=lambda x: x.get('final_price', float('inf')))

        organic_alternatives = await _get_organic_alternatives(diagnosis.get('disease_name'), diagnosis.get('affected_plant'))
        
        return {
            "disease": diagnosis.get('disease_name'),
            "suggested_remedies": valid_remedies[:3],
            "organic_alternatives": organic_alternatives,
            "prevention_tips": _get_prevention_tips(diagnosis.get('disease_name'))
        }
    except Exception as e:
        logger.error(f"Error in get_economical_remedies tool: {e}")
        raise

async def compare_remedies(chemicals: List[str], plant: str, state: str = "Maharashtra") -> Dict[str, Any]:
    """Compare different remedy options based on price and availability."""
    logger.info(f"Comparing remedies for {chemicals} in {state}")
    try:
        prices_tasks = [price_service.get_pesticide_prices(chem, state) for chem in chemicals]
        all_prices = await asyncio.gather(*prices_tasks, return_exceptions=True)
        
        comparison = []
        for chem, prices in zip(chemicals, all_prices):
            if isinstance(prices, Exception) or not prices:
                comparison.append({"chemical": chem, "available": False, "error": str(prices)})
                continue
            
            best = min(prices, key=lambda x: x.price - (x.subsidy_amount if x.subsidy_available else 0))
            comparison.append({
                "chemical": chem,
                "available": True,
                "brand": best.brand,
                "price": best.price,
                "final_price": best.price - (best.subsidy_amount if best.subsidy_available else 0),
                "source": best.source
            })
        
        comparison.sort(key=lambda x: x.get('final_price', float('inf')))
        return {"comparison": comparison, "best_option": comparison[0] if comparison else None}
    except Exception as e:
        logger.error(f"Error in compare_remedies tool: {e}")
        raise

async def _get_remedy_details(chemical: str, plant: str) -> Optional[Dict[str, Any]]:
    """Helper to get detailed information for a single chemical remedy."""
    try:
        prices = await price_service.get_pesticide_prices(chemical, "Maharashtra")
        if not prices:
            return None
        
        best_option = price_service.get_most_economical(prices)
        return {
            "pesticide": chemical,
            "brand": best_option.brand,
            "price": best_option.price,
            "final_price": best_option.price - (best_option.subsidy_amount if best_option.subsidy_available else 0),
            "subsidy_available": best_option.subsidy_available,
            "subsidy_amount": best_option.subsidy_amount,
            "source": best_option.source,
            "application_method": _get_application_method(chemical, plant),
            "safety_instructions": _get_safety_instructions(chemical)
        }
    except Exception as e:
        logger.error(f"Error getting remedy details for {chemical}: {e}")
        return None

def _get_application_method(chemical: str, plant: str) -> str:
    return f"Mix 2g of {chemical} per liter of water and spray on {plant}."

def _get_safety_instructions(chemical: str) -> str:
    return f"Wear protective gear when handling {chemical}."

def _get_prevention_tips(disease: str) -> List[str]:
    return ["Ensure good air circulation.", "Water at the base of the plant."]

async def _get_organic_alternatives(disease: str, plant: str) -> List[Dict[str, Any]]:
    return [{"name": "Neem Oil", "application": "Spray on leaves."}]
