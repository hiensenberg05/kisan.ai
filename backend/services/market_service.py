# backend/services/market_service.py
from typing import Dict, Any, List, Optional
import aiohttp
from config import settings

class MarketService:
    async def agmarknet_prices(self, commodity: str, state: Optional[str] = None, district: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        If you have a direct Agmarknet API route, call it here.
        Otherwise, use data.gov.in Agmarknet dataset endpoints with your key.
        """
        if not settings.DATA_GOV_API_KEY:
            return []
        # Example placeholder resource id (replace with the official Agmarknet resource id you use)
        resource_id = "AGMARKNET_RESOURCE_ID"
        url = f"{settings.MANDI_API_URL}/{resource_id}"
        params = {
            "api-key": settings.DATA_GOV_API_KEY,
            "format": "json",
            "filters[commodity]": commodity,
        }
        if state: params["filters[state]"] = state
        if district: params["filters[district]"] = district
        async with aiohttp.ClientSession() as s:
            async with s.get(url, params=params, timeout=30) as r:
                return (await r.json()).get("records", [])
