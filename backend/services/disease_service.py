"""
Plant Health Service for interacting with the Plant.Health API.
Handles disease diagnosis, treatment recommendations, and prevention tips.
"""
import asyncio
import base64
import logging
from typing import Optional, Dict, Any, List, Tuple
import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from utils.logger import get_logger
from utils.errors import APIServiceError, InvalidInputError
from core.config import settings

# Initialize logger
logger = get_logger(__name__)

class PlantHealthService:
    """Service for interacting with the Plant.Health API for plant disease diagnosis."""
    
    def __init__(self):
        """Initialize the PlantHealthService with API configuration."""
        self.base_url = str(settings.PLANT_HEALTH_API_URL).rstrip('/')
        self.api_key = settings.PLANT_HEALTH_API_KEY
        self.timeout = aiohttp.ClientTimeout(total=120)  # 2 minutes timeout
        self.max_retries = 3
        
        if not self.base_url or not self.api_key:
            logger.warning("Plant.Health API URL or API key not configured")
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((aiohttp.ClientError, asyncio.TimeoutError)),
        reraise=True
    )
    async def _make_api_request(self, endpoint: str, payload: Dict) -> Dict[str, Any]:
        """Make an authenticated request to the Plant.Health API.
        
        Args:
            endpoint: API endpoint path (e.g., '/diagnose')
            payload: Request payload
            
        Returns:
            Dict containing the API response
            
        Raises:
            APIServiceError: If the API request fails
            InvalidInputError: If the input is invalid
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                logger.debug(f"Sending request to {endpoint}")
                async with session.post(url, json=payload, headers=headers) as response:
                    response.raise_for_status()
                    return await response.json()
                    
        except aiohttp.ClientError as e:
            logger.error(f"API request failed: {str(e)}")
            raise APIServiceError(f"Failed to call Plant.Health API: {str(e)}")
    
    async def diagnose(self, image_b64: str, crop: Optional[str] = None) -> Dict[str, Any]:
        """Diagnose plant diseases from an image.
        
        Args:
            image_b64: Base64 encoded image data (with or without data URL prefix)
            crop: Optional crop type (e.g., 'tomato', 'wheat')
            
        Returns:
            Dict containing diagnosis results
            
        Raises:
            APIServiceError: If the API request fails
            InvalidInputError: If the input is invalid
        """
        logger.info("Starting disease diagnosis...")
        
        if not image_b64:
            logger.error("No image data provided")
            raise InvalidInputError("No image data provided")
            
        if not isinstance(image_b64, str):
            logger.error(f"Image data must be a string, got {type(image_b64)}")
            raise InvalidInputError("Invalid image data format")
            
        try:
            # Handle different input formats
            if image_b64.startswith('data:image/'):
                # Handle data URL format: data:image/png;base64,<data>
                if ',' in image_b64:
                    header, data = image_b64.split(',', 1)
                    # Validate the header
                    if not any(header.endswith(ext) for ext in ['/jpeg', '/png', '/jpg']):
                        logger.error(f"Unsupported image format in data URL: {header}")
                        raise InvalidInputError("Unsupported image format. Please use JPEG or PNG.")
                    clean_image_data = data
                else:
                    logger.error("Malformed data URL")
                    raise InvalidInputError("Invalid image data URL format")
            else:
                # Assume it's raw base64 data
                clean_image_data = image_b64
            
            # Validate base64 format
            try:
                # Add padding if needed
                padding = len(clean_image_data) % 4
                if padding:
                    clean_image_data += '=' * (4 - padding)
                base64.b64decode(clean_image_data, validate=True)
            except Exception as e:
                logger.error(f"Invalid base64 data: {str(e)}")
                raise InvalidInputError("Invalid image data. Please check the image format.")
            
            # Prepare the payload with the original format
            payload = {
                "image": f"data:image/jpeg;base64,{clean_image_data}" if not image_b64.startswith('data:image/') else image_b64,
                "crop": crop,
                "include_treatments": True,
                "include_prevention": True,
                "language": "en"
            }
            
            logger.info(f"Initiating disease diagnosis for crop: {crop or 'unknown'}")
            
            # If API is not configured, return mock response
            if not self.api_key or not self.base_url:
                logger.warning("Plant.Health API not configured, returning mock diagnosis")
                return self._get_mock_diagnosis(crop)
                
            response = await self._make_api_request("/v1/diagnose", payload)
            return self._parse_diagnosis_response(response, crop)
            
        except Exception as e:
            logger.error(f"Error in diagnose: {str(e)}", exc_info=True)
            if not isinstance(e, InvalidInputError):
                raise APIServiceError(f"Failed to process image: {str(e)}")
            raise
    
    def _parse_diagnosis_response(self, api_response: Dict, crop: Optional[str] = None) -> Dict[str, Any]:
        """Parse and validate the API response.
        
        Args:
            api_response: Raw API response
            crop: Original crop name used in the request
            
        Returns:
            Normalized diagnosis result
            
        Raises:
            APIServiceError: If the response is invalid
        """
        try:
            if not api_response or 'predictions' not in api_response:
                raise APIServiceError("Invalid API response format")
                
            predictions = api_response.get('predictions', [])
            if not predictions:
                return {
                    'disease': 'healthy',
                    'confidence': 1.0,
                    'crop': crop,
                    'treatments': [],
                    'prevention_tips': []
                }
                
            # Get top prediction
            top_prediction = predictions[0]
            disease_name = (
                top_prediction.get('disease_name') or 
                top_prediction.get('label') or 
                top_prediction.get('name') or 
                'unknown_disease'
            )
            
            confidence = min(1.0, max(0.0, float(
                top_prediction.get('confidence') or 
                top_prediction.get('score') or 
                top_prediction.get('probability') or 
                0.0
            )))
            
            # Extract treatments and prevention tips if available
            treatments = api_response.get('treatments', [])
            prevention_tips = api_response.get('prevention', [])
            
            return {
                'disease': disease_name.lower().replace(' ', '_'),
                'confidence': round(confidence, 4),
                'crop': crop,
                'treatments': treatments,
                'prevention_tips': prevention_tips,
                'raw_response': api_response  # Include raw response for debugging
            }
            
        except (KeyError, ValueError, TypeError, AttributeError) as e:
            logger.error(f"Failed to parse API response: {str(e)}")
            raise APIServiceError(f"Failed to parse API response: {str(e)}")
    
    async def get_treatments(self, disease_name: str, crop: str = None) -> List[Dict]:
        """Get treatment recommendations for a specific disease.
        
        Args:
            disease_name: Name of the disease
            crop: Optional crop type for more specific recommendations
            
        Returns:
            List of treatment recommendations
        """
        try:
            payload = {
                'disease': disease_name,
                'crop': crop
            }
            response = await self._make_api_request("/v1/treatments", payload)
            return response.get('treatments', [])
            
        except Exception as e:
            logger.error(f"Failed to fetch treatments: {str(e)}")
            return []
    
    async def get_prevention_tips(self, disease_name: str, crop: str = None) -> List[str]:
        """Get prevention tips for a specific disease.
        
        Args:
            disease_name: Name of the disease
            crop: Optional crop type for more specific tips
            
        Returns:
            List of prevention tips
        """
        try:
            payload = {
                'disease': disease_name,
                'crop': crop
            }
            response = await self._make_api_request("/v1/prevention", payload)
            return response.get('tips', [])
            
        except Exception as e:
            logger.error(f"Failed to fetch prevention tips: {str(e)}")
            return []
    
    @staticmethod
    def format_diagnosis_result(result: Dict) -> str:
        """Format diagnosis result into a human-readable string.
        
        Args:
            result: Diagnosis result from diagnose()
            
        Returns:
            Formatted string with diagnosis information
        """
        if not result:
            return "No diagnosis available."
            
        disease = result.get('disease', 'unknown').replace('_', ' ').title()
        confidence = result.get('confidence', 0) * 100
        
        output = [
            f"Diagnosis: {disease}",
            f"Confidence: {confidence:.1f}%"
        ]
        
        if result.get('treatments'):
            output.append("\nRecommended Treatments:")
            for i, treatment in enumerate(result['treatments'][:3], 1):
                output.append(f"{i}. {treatment.get('name', 'Treatment')}: {treatment.get('description', '')}")
        
        if result.get('prevention_tips'):
            output.append("\nPrevention Tips:")
            for i, tip in enumerate(result['prevention_tips'][:3], 1):
                output.append(f"{i}. {tip}")
                
        return "\n".join(output)
    
    def _get_mock_diagnosis(self, crop: Optional[str] = None) -> Dict[str, Any]:
        """Return a mock diagnosis when API is not available.
        
        Args:
            crop: Optional crop type
            
        Returns:
            Mock diagnosis result
        """
        return {
            'disease': 'healthy',
            'confidence': 0.85,
            'crop': crop or 'unknown',
            'treatments': [
                {
                    'name': 'Regular Monitoring',
                    'description': 'Continue regular plant monitoring and maintain good agricultural practices.'
                }
            ],
            'prevention_tips': [
                'Ensure proper watering and drainage',
                'Maintain optimal spacing between plants',
                'Regular inspection for early disease detection'
            ],
            'raw_response': {
                'mock': True,
                'status': 'success',
                'message': 'This is a mock response. Please configure the Plant.Health API for real diagnosis.'
            }
        }
