# backend/services/location_service.py
import aiohttp
from typing import Optional, Dict, Any
from core.config import settings

class LocationService:
    async def geocode(self, address: str) -> Optional[Dict[str, Any]]:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {"address": address, "key": settings.GOOGLE_MAPS_API_KEY}
        async with aiohttp.ClientSession() as s:
            async with s.get(url, params=params, timeout=20) as r:
                data = await r.json()
                if data.get("results"):
                    loc = data["results"][0]["geometry"]["location"]
                    return {"lat": loc["lat"], "lon": loc["lng"], "formatted": data["results"][0]["formatted_address"]}
                return None
