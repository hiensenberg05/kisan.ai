# backend/services/price_service.py
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from core.config import settings
from utils.logger import get_logger

logger = get_logger(__name__)

@dataclass
class PesticideInfo:
    name: str
    price: float
    currency: str = "INR"
    quantity: str = "1L"
    brand: Optional[str] = None
    source: str = "Unknown"
    subsidy_available: bool = False
    subsidy_amount: float = 0.0
    subsidy_details: Optional[Dict] = None
    last_updated: datetime = datetime.utcnow()

class PriceService:
    """
    Enhanced PriceService with multiple data sources:
    1. IndiaMART (Apify)
    2. Google Shopping API
    3. Government subsidy APIs
    4. Web scraping for local vendors
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600
        self.session = None
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession(headers=self.headers)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if self.session:
            await self.session.close()

    async def get_pesticide_prices(self, pesticide_name: str, state: str) -> List[PesticideInfo]:
        cache_key = f"pesticide_{pesticide_name.lower()}_{state.lower()}"
        if cache_key in self.cache:
            cached = self.cache[cache_key]
            if datetime.utcnow() - cached['timestamp'] < timedelta(seconds=self.cache_ttl):
                return cached['data']

        # Run all data sources concurrently
        tasks = [
            self._fetch_apify_indiamart(pesticide_name, state),
            self._fetch_google_shopping(pesticide_name, state),
            self._fetch_govt_subsidy(pesticide_name, state),
            self._scrape_local_vendors(pesticide_name, state)
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_prices = [item for sublist in results if isinstance(sublist, list) for item in sublist]
        
        # Sort by final price (price - subsidy)
        all_prices.sort(key=lambda x: x.price - (x.subsidy_amount if x.subsidy_available else 0))
        
        self.cache[cache_key] = {
            'data': all_prices,
            'timestamp': datetime.utcnow()
        }
        
        return all_prices

    async def _fetch_apify_indiamart(self, pesticide_name: str, state: str) -> List[PesticideInfo]:
        """Fetch prices from IndiaMART using Apify."""
        if not settings.APIFY_TOKEN:
            logger.warning("Apify token not configured")
            return []

        try:
            async with self.session.post(
                f"https://api.apify.com/v2/acts/apify~web-scraper/run-sync-get-dataset-items?token={settings.APIFY_TOKEN}",
                json={
                    "startUrls": [{
                        "url": f"https://dir.indiamart.com/search.mp?ss={pesticide_name.replace(' ', '+')}"
                    }],
                    "proxy": {"useApifyProxy": True}
                }
            ) as response:
                data = await response.json()
                return self._parse_indiamart_results(data)
        except Exception as e:
            logger.error(f"Apify IndiaMART error: {str(e)}")
            return []

    async def _fetch_google_shopping(self, query: str, state: str) -> List[PesticideInfo]:
        """Fetch prices from Google Shopping API."""
        if not settings.GOOGLE_API_KEY:
            logger.warning("Google API key not configured")
            return []

        try:
            params = {
                'q': f'{query} pesticide buy {state}',
                'engine': 'google_shopping',
                'api_key': settings.GOOGLE_API_KEY
            }
            
            async with self.session.get(
                'https://serpapi.com/search.json',
                params=params
            ) as response:
                data = await response.json()
                return self._parse_google_shopping_results(data)
        except Exception as e:
            logger.error(f"Google Shopping API error: {str(e)}")
            return []

    async def _fetch_govt_subsidy(self, pesticide_name: str, state: str) -> List[PesticideInfo]:
        """Fetch government subsidy information."""
        try:
            # This would be implemented to call government APIs
            # For now, returning mock data
            return [
                PesticideInfo(
                    name=pesticide_name,
                    price=1000.00,
                    brand="Govt. Approved",
                    source="Govt. Emporium",
                    subsidy_available=True,
                    subsidy_amount=400.00,
                    subsidy_details={
                        "scheme": "PM-KISAN",
                        "valid_until": "2023-12-31",
                        "documents_required": ["Aadhaar", "Land Records"]
                    }
                )
            ]
        except Exception as e:
            logger.error(f"Govt subsidy API error: {str(e)}")
            return []

    async def _scrape_local_vendors(self, pesticide_name: str, state: str) -> List[PesticideInfo]:
        """Scrape local vendor websites for prices."""
        try:
            # Example: Scraping from a hypothetical agricultural marketplace
            url = f"https://example-agri-marketplace.com/search?q={pesticide_name}&state={state}"
            async with self.session.get(url) as response:
                html = await response.text()
                return self._parse_vendor_website(html, pesticide_name)
        except Exception as e:
            logger.error(f"Local vendor scraping error: {str(e)}")
            return []

    def _parse_indiamart_results(self, data: List[Dict]) -> List[PesticideInfo]:
        """Parse IndiaMART API results."""
        results = []
        for item in data:
            try:
                price_text = item.get('price', '0')
                price = float(''.join(filter(str.isdigit, price_text)) or '0')
                
                results.append(PesticideInfo(
                    name=item.get('title', ''),
                    price=price,
                    brand=item.get('brand'),
                    source="IndiaMART",
                    subsidy_available=False
                ))
            except Exception as e:
                logger.error(f"Error parsing IndiaMART item: {str(e)}")
        return results

    def _parse_google_shopping_results(self, data: Dict) -> List[PesticideInfo]:
        """Parse Google Shopping API results."""
        results = []
        for item in data.get('shopping_results', []):
            try:
                price = float(item.get('price', '0').replace('₹', '').replace(',', ''))
                results.append(PesticideInfo(
                    name=item.get('title', ''),
                    price=price,
                    brand=item.get('source', 'Google Shopping'),
                    source="Google Shopping"
                ))
            except Exception as e:
                logger.error(f"Error parsing Google Shopping item: {str(e)}")
        return results

    def _parse_vendor_website(self, html: str, pesticide_name: str) -> List[PesticideInfo]:
        """Parse vendor website HTML for prices."""
        results = []
        try:
            soup = BeautifulSoup(html, 'html.parser')
            # This would be customized based on the actual website structure
            products = soup.find_all('div', class_='product')
            
            for product in products:
                try:
                    name = product.find('h3').text.strip()
                    price_text = product.find('span', class_='price').text
                    price = float(''.join(filter(str.isdigit, price_text)) or '0')
                    
                    results.append(PesticideInfo(
                        name=name,
                        price=price,
                        source="Local Vendor Network"
                    ))
                except Exception as e:
                    logger.error(f"Error parsing vendor product: {str(e)}")
        except Exception as e:
            logger.error(f"Error parsing vendor website: {str(e)}")
        
        return results

    def get_most_economical(self, pesticides: List[PesticideInfo]) -> PesticideInfo:
        """Get the most economical option considering subsidies."""
        if not pesticides:
            raise ValueError("No pesticide data available")
        return min(
            pesticides,
            key=lambda x: x.price - (x.subsidy_amount if x.subsidy_available else 0)
        )

    def filter_by_budget(self, pesticides: List[PesticideInfo], max_budget: float) -> List[PesticideInfo]:
        """Filter pesticides by maximum budget."""
        return [
            p for p in pesticides
            if (p.price - (p.subsidy_amount if p.subsidy_available else 0)) <= max_budget
        ]