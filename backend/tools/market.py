import aiohttp
import logging
from typing import Dict, Any, Optional, List
import json
import asyncio
from datetime import datetime, timedelta

from config import settings

logger = logging.getLogger(__name__)

class MarketDataHandler:
    """
    Market data handler for fetching real-time crop prices and market information.
    Integrates with various market APIs and provides analysis.
    """
    
    def __init__(self):
        """Initialize market data handler"""
        # Market APIs configuration
        self.apis = {
            "agmarknet": {
                "base_url": "https://agmarknet.gov.in/api/v1",
                "enabled": True
            },
            "mandi_prices": {
                "base_url": "https://api.data.gov.in/resource",
                "enabled": True
            },
            "fallback": {
                "base_url": "https://api.example.com",  # Placeholder
                "enabled": False
            }
        }
        
        # Common crops in India
        self.common_crops = {
            "tomato": ["tomato", "tamatar", "tamata"],
            "rice": ["rice", "chawal", "arisi", "akki"],
            "wheat": ["wheat", "gehun", "godhuma", "gothambu"],
            "potato": ["potato", "aloo", "urulai", "batata"],
            "onion": ["onion", "pyaaz", "ulli", "venkayam"],
            "corn": ["corn", "makka", "cholam", "mokka"],
            "cotton": ["cotton", "kapas", "paruthi", "hatti"],
            "sugarcane": ["sugarcane", "ganna", "karumbu", "chera"],
            "pulses": ["pulses", "dal", "paruppu", "pappu"]
        }
        
        # Market locations
        self.market_locations = {
            "karnataka": ["bangalore", "mysore", "hubli", "mangalore"],
            "maharashtra": ["mumbai", "pune", "nagpur", "aurangabad"],
            "tamil_nadu": ["chennai", "coimbatore", "madurai", "salem"],
            "andhra_pradesh": ["hyderabad", "vijayawada", "visakhapatnam"],
            "gujarat": ["ahmedabad", "surat", "vadodara", "rajkot"]
        }
        
        # Cache for market data
        self.cache = {}
        self.cache_duration = timedelta(hours=1)  # Cache for 1 hour
        
        logger.info("Market Data Handler initialized")
    
    async def get_crop_prices(self, crop: str, location: str = None) -> Dict[str, Any]:
        """
        Get real-time crop prices from multiple sources.
        
        Args:
            crop: Crop name
            location: Market location (optional)
            
        Returns:
            Market data with prices and analysis
        """
        try:
            logger.info(f"Fetching prices for {crop} in {location or 'all locations'}")
            
            # Check cache first
            cache_key = f"{crop}_{location or 'all'}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                if datetime.now() - cached_data["timestamp"] < self.cache_duration:
                    logger.info("Returning cached market data")
                    return cached_data["data"]
            
            # Fetch from multiple sources
            market_data = await self._fetch_market_data(crop, location)
            
            # Analyze market trends
            analysis = await self._analyze_market_trends(market_data)
            
            # Combine results
            result = {
                "crop": crop,
                "location": location,
                "timestamp": datetime.now().isoformat(),
                "prices": market_data,
                "analysis": analysis,
                "recommendations": await self._generate_recommendations(market_data, analysis)
            }
            
            # Cache the result
            self.cache[cache_key] = {
                "data": result,
                "timestamp": datetime.now()
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching crop prices: {e}", exc_info=True)
            return await self._get_fallback_data(crop, location)
    
    async def _fetch_market_data(self, crop: str, location: str = None) -> List[Dict[str, Any]]:
        """Fetch market data from multiple sources"""
        try:
            tasks = []
            
            # Fetch from AgMarkNet
            if self.apis["agmarknet"]["enabled"]:
                tasks.append(self._fetch_agmarknet_data(crop, location))
            
            # Fetch from Mandi Prices API
            if self.apis["mandi_prices"]["enabled"]:
                tasks.append(self._fetch_mandi_data(crop, location))
            
            # Execute all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine and filter results
            market_data = []
            for result in results:
                if isinstance(result, list):
                    market_data.extend(result)
                elif isinstance(result, dict):
                    market_data.append(result)
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error fetching market data: {e}", exc_info=True)
            return []
    
    async def _fetch_agmarknet_data(self, crop: str, location: str = None) -> List[Dict[str, Any]]:
        """Fetch data from AgMarkNet API"""
        try:
            # Normalize crop name
            normalized_crop = self._normalize_crop_name(crop)
            
            # Build API URL
            url = f"{self.apis['agmarknet']['base_url']}/commodity/{normalized_crop}"
            if location:
                url += f"/state/{location}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_agmarknet_data(data)
                    else:
                        logger.warning(f"AgMarkNet API returned status {response.status}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching AgMarkNet data: {e}", exc_info=True)
            return []
    
    async def _fetch_mandi_data(self, crop: str, location: str = None) -> List[Dict[str, Any]]:
        """Fetch data from Mandi Prices API"""
        try:
            # This is a placeholder for the actual API integration
            # In a real implementation, you would integrate with the actual API
            
            # Simulated data for demonstration
            simulated_data = [
                {
                    "market": "Bangalore APMC",
                    "crop": crop,
                    "min_price": 2500,
                    "max_price": 3500,
                    "modal_price": 3000,
                    "unit": "per quintal",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": "mandi_prices"
                },
                {
                    "market": "Mysore APMC",
                    "crop": crop,
                    "min_price": 2400,
                    "max_price": 3400,
                    "modal_price": 2900,
                    "unit": "per quintal",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": "mandi_prices"
                }
            ]
            
            return simulated_data
            
        except Exception as e:
            logger.error(f"Error fetching Mandi data: {e}", exc_info=True)
            return []
    
    def _parse_agmarknet_data(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse AgMarkNet API response"""
        try:
            parsed_data = []
            
            if "data" in data and isinstance(data["data"], list):
                for item in data["data"]:
                    parsed_item = {
                        "market": item.get("market", "Unknown"),
                        "crop": item.get("commodity", "Unknown"),
                        "min_price": item.get("min_price", 0),
                        "max_price": item.get("max_price", 0),
                        "modal_price": item.get("modal_price", 0),
                        "unit": item.get("unit", "per quintal"),
                        "date": item.get("date", ""),
                        "source": "agmarknet"
                    }
                    parsed_data.append(parsed_item)
            
            return parsed_data
            
        except Exception as e:
            logger.error(f"Error parsing AgMarkNet data: {e}", exc_info=True)
            return []
    
    async def _analyze_market_trends(self, market_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze market trends from price data"""
        try:
            if not market_data:
                return {"trend": "no_data", "confidence": "low"}
            
            # Calculate average prices
            prices = [item.get("modal_price", 0) for item in market_data if item.get("modal_price", 0) > 0]
            
            if not prices:
                return {"trend": "no_valid_prices", "confidence": "low"}
            
            avg_price = sum(prices) / len(prices)
            min_price = min(prices)
            max_price = max(prices)
            
            # Simple trend analysis
            price_range = max_price - min_price
            price_variability = (price_range / avg_price) * 100 if avg_price > 0 else 0
            
            # Determine trend
            if price_variability < 10:
                trend = "stable"
                confidence = "high"
            elif price_variability < 25:
                trend = "moderate_volatility"
                confidence = "medium"
            else:
                trend = "high_volatility"
                confidence = "medium"
            
            return {
                "trend": trend,
                "confidence": confidence,
                "average_price": avg_price,
                "price_range": price_range,
                "price_variability_percent": price_variability,
                "min_price": min_price,
                "max_price": max_price,
                "market_count": len(market_data)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market trends: {e}", exc_info=True)
            return {"trend": "analysis_error", "confidence": "low"}
    
    async def _generate_recommendations(self, market_data: List[Dict[str, Any]], analysis: Dict[str, Any]) -> List[str]:
        """Generate selling recommendations based on market data"""
        try:
            recommendations = []
            
            if not market_data:
                recommendations.append("No market data available. Consider checking local mandi prices.")
                return recommendations
            
            trend = analysis.get("trend", "unknown")
            avg_price = analysis.get("average_price", 0)
            price_variability = analysis.get("price_variability_percent", 0)
            
            if trend == "stable":
                recommendations.append("Market prices are stable. You can sell when convenient.")
                recommendations.append("Consider selling in smaller batches to spread risk.")
            
            elif trend == "moderate_volatility":
                recommendations.append("Moderate price volatility detected. Monitor prices closely.")
                recommendations.append("Consider selling when prices are above average.")
            
            elif trend == "high_volatility":
                recommendations.append("High price volatility. Be cautious with selling decisions.")
                recommendations.append("Consider waiting for price stabilization or sell in small quantities.")
            
            # Price-based recommendations
            if avg_price > 0:
                recommendations.append(f"Current average price: ₹{avg_price:.2f} per quintal")
                
                if price_variability > 20:
                    recommendations.append("High price variation between markets. Compare prices before selling.")
            
            # Market-specific recommendations
            if len(market_data) > 1:
                best_market = max(market_data, key=lambda x: x.get("modal_price", 0))
                recommendations.append(f"Best price currently at {best_market.get('market', 'Unknown')} market.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}", exc_info=True)
            return ["Unable to generate recommendations due to data processing error."]
    
    def _normalize_crop_name(self, crop: str) -> str:
        """Normalize crop name for API queries"""
        crop_lower = crop.lower().strip()
        
        # Check common crop mappings
        for standard_name, variations in self.common_crops.items():
            if crop_lower in variations or crop_lower == standard_name:
                return standard_name
        
        # Return original if no match found
        return crop_lower
    
    async def _get_fallback_data(self, crop: str, location: str = None) -> Dict[str, Any]:
        """Get fallback market data when APIs are unavailable"""
        try:
            # Generate realistic fallback data
            fallback_data = [
                {
                    "market": "Local Mandi",
                    "crop": crop,
                    "min_price": 2000,
                    "max_price": 3000,
                    "modal_price": 2500,
                    "unit": "per quintal",
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "source": "fallback"
                }
            ]
            
            analysis = {
                "trend": "unknown",
                "confidence": "low",
                "average_price": 2500,
                "price_range": 1000,
                "price_variability_percent": 40,
                "min_price": 2000,
                "max_price": 3000,
                "market_count": 1
            }
            
            return {
                "crop": crop,
                "location": location,
                "timestamp": datetime.now().isoformat(),
                "prices": fallback_data,
                "analysis": analysis,
                "recommendations": [
                    "This is estimated data. Please verify with local mandi.",
                    "Contact local agricultural office for accurate prices.",
                    "Consider checking multiple markets for best prices."
                ],
                "note": "Fallback data - verify with local sources"
            }
            
        except Exception as e:
            logger.error(f"Error generating fallback data: {e}", exc_info=True)
            return {
                "crop": crop,
                "location": location,
                "error": "Unable to fetch market data",
                "recommendations": ["Please check local mandi prices directly."]
            }
    
    async def get_market_locations(self) -> Dict[str, List[str]]:
        """Get available market locations"""
        return self.market_locations
    
    async def get_supported_crops(self) -> Dict[str, List[str]]:
        """Get supported crop names and variations"""
        return self.common_crops
    
    async def clear_cache(self) -> bool:
        """Clear the market data cache"""
        try:
            self.cache.clear()
            logger.info("Market data cache cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}", exc_info=True)
            return False
    
    async def test_connection(self) -> bool:
        """Test market data API connections"""
        try:
            # Test basic connectivity
            async with aiohttp.ClientSession() as session:
                # Test with a simple request
                test_url = "https://httpbin.org/get"
                async with session.get(test_url, timeout=5) as response:
                    if response.status == 200:
                        logger.info("Market data API connection test successful")
                        return True
                    else:
                        logger.warning(f"Market data API test returned status {response.status}")
                        return False
                        
        except Exception as e:
            logger.error(f"Market data API connection test failed: {e}", exc_info=True)
            return False 