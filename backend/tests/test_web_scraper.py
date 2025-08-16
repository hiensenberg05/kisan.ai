"""
Tests for the WebScraper tool.
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from tools.web_scraper import WebScraper

@pytest.fixture
def mock_response():
    """Mock aiohttp response"""
    response = MagicMock()
    response.text.return_value = "<html><body>Test content</body></html>"
    response.status = 200
    return response

@pytest.fixture
def mock_session(mock_response):
    """Mock aiohttp client session"""
    session = AsyncMock()
    session.get.return_value.__aenter__.return_value = mock_response
    return session

@pytest.mark.asyncio
async def test_web_scraper_fetch(mock_session):
    """Test the fetch method of WebScraper"""
    test_url = "https://example.com"
    
    with patch('aiohttp.ClientSession', return_value=mock_session):
        async with WebScraper() as scraper:
            # Mock the session's get method
            mock_session.get.return_value.__aenter__.return_value.text.return_value = "<html>Test</html>"
            
            # Test successful fetch
            result = await scraper.fetch(test_url)
            assert result == "<html>Test</html>"
            
            # Test error handling
            mock_session.get.return_value.__aenter__.return_value.raise_for_status.side_effect = Exception("Test error")
            with pytest.raises(Exception, match="Test error"):
                await scraper.fetch(test_url)

@pytest.mark.asyncio
async def test_scrape_agri_prices():
    """Test the scrape_agri_prices method"""
    async with WebScraper() as scraper:
        # Test with mock data
        results = await scraper.scrape_agri_prices("Tomato", "Maharashtra")
        
        # Verify the structure of the results
        assert isinstance(results, list)
        if results:  # If mock data is returned
            assert 'commodity' in results[0]
            assert 'min_price' in results[0]
            assert 'market' in results[0]

@pytest.mark.asyncio
async def test_scrape_weather_forecast():
    """Test the scrape_weather_forecast method"""
    async with WebScraper() as scraper:
        # Test with mock data
        weather = await scraper.scrape_weather_forecast("Nashik, Maharashtra", days=5)
        
        # Verify the structure of the weather data
        assert 'location' in weather
        assert 'current' in weather
        assert 'forecast' in weather
        assert 'source' in weather
        assert weather['forecast_days'] == 5

@pytest.mark.asyncio
async def test_scrape_agri_news():
    """Test the scrape_agri_news method"""
    async with WebScraper() as scraper:
        # Test with mock data
        news = await scraper.scrape_agri_news("organic farming", max_results=3)
        
        # Verify the structure of the news data
        assert isinstance(news, list)
        if news:  # If mock data is returned
            assert 'title' in news[0]
            assert 'summary' in news[0]
            assert 'source' in news[0]
            assert 'url' in news[0]

# Run tests if executed directly
if __name__ == "__main__":
    import pytest
    import sys
    sys.exit(pytest.main(["-v", __file__]))
