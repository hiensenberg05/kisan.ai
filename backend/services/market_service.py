"""
Market Service for fetching and analyzing agricultural market data.
Integrates with multiple data sources including Agmarknet, weather APIs, and geolocation services.
"""
import logging
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import aiohttp
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pytz

from utils.logger import get_logger
from utils.errors import APIServiceError, InvalidInputError
from core.config import settings

# Initialize logger
logger = get_logger(__name__)

class MarketService:
    """Service for fetching and analyzing agricultural market data."""
    
    def __init__(self):
        """Initialize the MarketService with API configurations."""
        self.geolocator = Nominatim(user_agent="kisan_ai_market")
        self.timeout = aiohttp.ClientTimeout(total=30)
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache TTL
    
    async def _make_api_request(self, url: str, params: Optional[Dict] = None, headers: Optional[Dict] = None) -> Dict:
        """Make an HTTP request with error handling and retries."""
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {str(e)}")
            raise APIServiceError(f"Failed to fetch data: {str(e)}")
    
    async def get_location_info(self, lat: float, lng: float) -> Dict[str, str]:
        """Get location information from coordinates."""
        cache_key = f"location_{lat}_{lng}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            location = await asyncio.to_thread(
                self.geolocator.reverse, 
                f"{lat}, {lng}",
                exactly_one=True
            )
            
            if not location:
                raise APIServiceError("Location not found")
                
            address = location.raw.get('address', {})
            result = {
                'state': address.get('state', ''),
                'district': address.get('county', '').replace(' District', ''),
                'village': address.get('village', ''),
                'full_address': location.address
            }
            
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Geocoding failed: {str(e)}")
            raise APIServiceError(f"Failed to get location info: {str(e)}")
    
    async def get_weather_forecast(self, lat: float, lng: float) -> Dict:
        """Get weather forecast for a location."""
        cache_key = f"weather_{lat}_{lng}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            # Using OpenWeatherMap API (you'll need to set OPENWEATHER_API_KEY in settings)
            url = "https://api.openweathermap.org/data/2.5/onecall"
            params = {
                'lat': lat,
                'lon': lng,
                'appid': settings.OPENWEATHER_API_KEY,
                'units': 'metric',
                'exclude': 'minutely,hourly',
                'lang': 'en'
            }
            
            data = await self._make_api_request(url, params=params)
            
            # Process the forecast data
            current = data.get('current', {})
            daily = data.get('daily', [{}])[0]  # Get today's forecast
            
            result = {
                'current': {
                    'temp': current.get('temp'),
                    'feels_like': current.get('feels_like'),
                    'humidity': current.get('humidity'),
                    'weather': current.get('weather', [{}])[0].get('main', 'N/A'),
                    'description': current.get('weather', [{}])[0].get('description', 'N/A')
                },
                'forecast': {
                    'temp': {
                        'day': daily.get('temp', {}).get('day'),
                        'min': daily.get('temp', {}).get('min'),
                        'max': daily.get('temp', {}).get('max')
                    },
                    'rain': daily.get('rain', 0),
                    'wind_speed': daily.get('wind_speed', 0),
                    'humidity': daily.get('humidity', 0)
                }
            }
            
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            logger.error(f"Weather API error: {str(e)}")
            return {}
    
    async def get_market_prices(self, commodity: str, state: str, district: Optional[str] = None) -> List[Dict]:
        """Get market prices for a commodity in a specific location."""
        cache_key = f"prices_{commodity}_{state}_{district or ''}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            # First try Agmarknet API
            try:
                agmarknet_data = await self._get_agmarknet_prices(commodity, state, district)
                if agmarknet_data:
                    self.cache[cache_key] = agmarknet_data
                    return agmarknet_data
            except Exception as e:
                logger.warning(f"Agmarknet API failed, falling back to alternative: {str(e)}")
                # Fallback to alternative data source if available
                # This is a placeholder - implement your fallback logic here
                return []
                
        except Exception as e:
            logger.error(f"Failed to fetch market prices: {str(e)}")
            raise APIServiceError(f"Failed to fetch market prices: {str(e)}")
    
    async def _get_agmarknet_prices(self, commodity: str, state: str, district: Optional[str] = None) -> List[Dict]:
        """Get prices from Agmarknet API."""
        if not settings.DATA_GOV_API_KEY:
            raise APIServiceError("API key not configured")
            
        url = f"{settings.MANDI_API_URL}/agmarknet"
        params = {
            'api-key': settings.DATA_GOV_API_KEY,
            'format': 'json',
            'commodity': commodity,
            'state': state,
            'limit': 10
        }
        
        if district:
            params['district'] = district
            
        data = await self._make_api_request(url, params=params)
        return self._process_agmarknet_response(data)
    
    def _process_agmarknet_response(self, data: Dict) -> List[Dict]:
        """Process and normalize Agmarknet API response."""
        records = data.get('records', [])
        processed = []
        
        for record in records:
            try:
                processed.append({
                    'market': record.get('market'),
                    'commodity': record.get('commodity'),
                    'variety': record.get('variety'),
                    'min_price': float(record.get('min_price', 0)),
                    'max_price': float(record.get('max_price', 0)),
                    'modal_price': float(record.get('modal_price', 0)),
                    'arrival_date': record.get('arrival_date'),
                    'state': record.get('state'),
                    'district': record.get('district')
                })
            except (ValueError, TypeError) as e:
                logger.warning(f"Error processing market record: {str(e)}")
                continue
                
        return processed
    
    async def get_price_trends(self, commodity: str, state: str, days: int = 30) -> Dict:
        """Get price trends for a commodity over time."""
        cache_key = f"trends_{commodity}_{state}_{days}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            # This is a simplified example - implement actual trend analysis
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # In a real implementation, you would fetch historical data here
            # For now, we'll return mock data
            return {
                'commodity': commodity,
                'state': state,
                'time_period': {
                    'start': start_date.strftime('%Y-%m-%d'),
                    'end': end_date.strftime('%Y-%m-%d')
                },
                'prices': [
                    {'date': (end_date - timedelta(days=i)).strftime('%Y-%m-%d'),
                     'price': 1000 + (i * 10) - (i * i)  # Mock trend
                    } for i in range(days, 0, -1)
                ]
            }
            
        except Exception as e:
            logger.error(f"Failed to get price trends: {str(e)}")
            raise APIServiceError(f"Failed to get price trends: {str(e)}")
    
    async def get_market_insights(self, commodity: str, lat: float, lng: float) -> Dict:
        """Get comprehensive market insights for a location."""
        try:
            # Get location info
            location = await self.get_location_info(lat, lng)
            
            # Get market data
            prices = await self.get_market_prices(
                commodity=commodity,
                state=location['state'],
                district=location['district']
            )
            
            # Get price trends
            trends = await self.get_price_trends(commodity, location['state'])
            
            # Get weather forecast
            weather = await self.get_weather_forecast(lat, lng)
            
            # Generate insights
            insight = self._generate_insights(
                commodity=commodity,
                prices=prices,
                trends=trends,
                weather=weather,
                location=location
            )
            
            return {
                'commodity': commodity,
                'location': location,
                'current_prices': prices[:5],  # Top 5 markets
                'price_trends': trends,
                'weather_forecast': weather,
                'insights': insight,
                'timestamp': datetime.now(pytz.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate market insights: {str(e)}")
            raise
    
    def _generate_insights(
        self,
        commodity: str,
        prices: List[Dict],
        trends: Dict,
        weather: Dict,
        location: Dict
    ) -> Dict:
        """Generate market insights based on available data."""
        if not prices:
            return {
                'summary': f"No recent price data available for {commodity} in {location.get('district', 'your area')}.",
                'recommendation': 'Check back later or try a different location.'
            }
        
        # Calculate average price
        valid_prices = [p['modal_price'] for p in prices if p.get('modal_price')]
        avg_price = sum(valid_prices) / len(valid_prices) if valid_prices else 0
        
        # Price trend analysis (simplified)
        price_points = trends.get('prices', [])
        if len(price_points) > 1:
            price_change = ((price_points[-1]['price'] - price_points[0]['price']) / 
                          price_points[0]['price'] * 100)
            trend = 'increasing' if price_change > 0 else 'decreasing' if price_change < 0 else 'stable'
        else:
            trend = 'stable'
        
        # Weather impact
        weather_impact = ""
        if weather.get('forecast', {}).get('rain', 0) > 5:  # More than 5mm rain
            weather_impact = "Expected rain may affect market arrivals."
        
        # Generate recommendations
        recommendations = []
        if trend == 'increasing':
            recommendations.append("Prices are trending upward. Consider waiting for better rates.")
        elif trend == 'decreasing':
            recommendations.append("Prices are trending downward. Consider selling soon.")
        
        if weather_impact:
            recommendations.append(weather_impact)
        
        return {
            'summary': (
                f"Current average price for {commodity} in {location.get('district', 'your area')} "
                f"is ₹{avg_price:.2f}/quintal. "
                f"Prices have been {trend} in the last 30 days."
            ),
            'price_analysis': {
                'average_price': round(avg_price, 2),
                'price_range': {
                    'min': min(valid_prices) if valid_prices else 0,
                    'max': max(valid_prices) if valid_prices else 0
                },
                'trend': trend,
                'price_change_pct': abs(round(price_change, 2)) if 'price_change' in locals() else 0
            },
            'recommendations': recommendations or ["Market conditions appear stable."],
            'best_markets': sorted(
                prices,
                key=lambda x: x.get('modal_price', 0),
                reverse=True
            )[:3]  # Top 3 markets by price
        }
