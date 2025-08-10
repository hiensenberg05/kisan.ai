import logging
import json
import base64
import hashlib
import re
from typing import Dict, Any, Optional, List, Union
from datetime import datetime, timedelta
import asyncio
import aiohttp
from io import BytesIO
import mimetypes

logger = logging.getLogger(__name__)

class Utils:
    """Utility functions for Project Kisan backend"""
    
    @staticmethod
    def validate_image_file(image_content: bytes, max_size: int = 10485760) -> Dict[str, Any]:
        """
        Validate image file content
        
        Args:
            image_content: Raw image bytes
            max_size: Maximum file size in bytes (default: 10MB)
            
        Returns:
            Validation result dictionary
        """
        try:
            # Check file size
            if len(image_content) > max_size:
                return {
                    "valid": False,
                    "error": f"File size exceeds maximum limit of {max_size / 1024 / 1024:.1f}MB"
                }
            
            # Check minimum size
            if len(image_content) < 100:
                return {
                    "valid": False,
                    "error": "File too small to be a valid image"
                }
            
            # Check file signature (magic bytes)
            image_signatures = {
                b'\xff\xd8\xff': 'JPEG',
                b'\x89PNG\r\n\x1a\n': 'PNG',
                b'GIF87a': 'GIF',
                b'GIF89a': 'GIF',
                b'RIFF': 'WEBP'
            }
            
            file_type = None
            for signature, img_type in image_signatures.items():
                if image_content.startswith(signature):
                    file_type = img_type
                    break
            
            if not file_type:
                return {
                    "valid": False,
                    "error": "Invalid image format. Supported formats: JPEG, PNG, GIF, WEBP"
                }
            
            return {
                "valid": True,
                "file_type": file_type,
                "size_bytes": len(image_content)
            }
            
        except Exception as e:
            logger.error(f"Error validating image file: {e}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    @staticmethod
    def validate_audio_file(audio_content: bytes, max_size: int = 10485760) -> Dict[str, Any]:
        """
        Validate audio file content
        
        Args:
            audio_content: Raw audio bytes
            max_size: Maximum file size in bytes (default: 10MB)
            
        Returns:
            Validation result dictionary
        """
        try:
            # Check file size
            if len(audio_content) > max_size:
                return {
                    "valid": False,
                    "error": f"File size exceeds maximum limit of {max_size / 1024 / 1024:.1f}MB"
                }
            
            # Check minimum size
            if len(audio_content) < 100:
                return {
                    "valid": False,
                    "error": "File too small to be a valid audio file"
                }
            
            # Check file signature
            audio_signatures = {
                b'RIFF': 'WAV',
                b'ID3': 'MP3',
                b'\xff\xfb': 'MP3',
                b'OggS': 'OGG',
                b'\x1A\x45\xDF\xA3': 'WEBM'  # EBML header for WebM/Matroska
            }
            
            file_type = None
            for signature, audio_type in audio_signatures.items():
                if audio_content.startswith(signature):
                    file_type = audio_type
                    break
            
            if not file_type:
                return {
                    "valid": False,
                    "error": "Invalid audio format. Supported formats: WAV, MP3, OGG, WEBM"
                }
            
            return {
                "valid": True,
                "file_type": file_type,
                "size_bytes": len(audio_content)
            }
            
        except Exception as e:
            logger.error(f"Error validating audio file: {e}")
            return {
                "valid": False,
                "error": f"Validation error: {str(e)}"
            }
    
    @staticmethod
    def sanitize_text(text: str, max_length: int = 1000) -> str:
        """
        Sanitize and clean text input
        
        Args:
            text: Input text
            max_length: Maximum allowed length
            
        Returns:
            Sanitized text
        """
        try:
            if not text:
                return ""
            
            # Remove excessive whitespace
            sanitized = re.sub(r'\s+', ' ', text.strip())
            
            # Remove special characters that might cause issues
            sanitized = re.sub(r'[^\w\s\.\,\!\?\-\:\;\(\)]', '', sanitized)
            
            # Truncate if too long
            if len(sanitized) > max_length:
                sanitized = sanitized[:max_length] + "..."
            
            return sanitized
            
        except Exception as e:
            logger.error(f"Error sanitizing text: {e}")
            return text[:max_length] if text else ""
    
    @staticmethod
    def extract_crop_keywords(text: str) -> List[str]:
        """
        Extract crop-related keywords from text
        
        Args:
            text: Input text
            
        Returns:
            List of crop keywords
        """
        try:
            # Common crop keywords
            crop_keywords = [
                "tomato", "rice", "wheat", "corn", "potato", "onion",
                "cotton", "sugarcane", "pulses", "lentils", "chickpeas",
                "maize", "millet", "sorghum", "barley", "oats",
                "vegetables", "fruits", "spices", "tea", "coffee"
            ]
            
            # Disease keywords
            disease_keywords = [
                "disease", "pest", "fungus", "bacteria", "virus",
                "blight", "rust", "mildew", "wilt", "rot",
                "spot", "lesion", "yellowing", "wilting", "stunting"
            ]
            
            # Market keywords
            market_keywords = [
                "price", "market", "mandi", "selling", "buying",
                "profit", "loss", "demand", "supply", "export"
            ]
            
            # Policy keywords
            policy_keywords = [
                "government", "scheme", "subsidy", "loan", "insurance",
                "support", "assistance", "program", "policy", "benefit"
            ]
            
            all_keywords = crop_keywords + disease_keywords + market_keywords + policy_keywords
            
            # Extract keywords from text
            found_keywords = []
            text_lower = text.lower()
            
            for keyword in all_keywords:
                if keyword in text_lower:
                    found_keywords.append(keyword)
            
            return found_keywords
            
        except Exception as e:
            logger.error(f"Error extracting crop keywords: {e}")
            return []
    
    @staticmethod
    def generate_response_id() -> str:
        """Generate unique response ID"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            random_hash = hashlib.md5(timestamp.encode()).hexdigest()[:8]
            return f"kisan_{timestamp}_{random_hash}"
        except Exception as e:
            logger.error(f"Error generating response ID: {e}")
            return f"kisan_{int(datetime.now().timestamp())}"
    
    @staticmethod
    def format_currency(amount: float, currency: str = "INR") -> str:
        """
        Format currency amount
        
        Args:
            amount: Amount to format
            currency: Currency code
            
        Returns:
            Formatted currency string
        """
        try:
            if currency == "INR":
                return f"₹{amount:,.2f}"
            else:
                return f"{currency} {amount:,.2f}"
        except Exception as e:
            logger.error(f"Error formatting currency: {e}")
            return str(amount)
    
    @staticmethod
    def calculate_price_range(min_price: float, max_price: float) -> Dict[str, Any]:
        """
        Calculate price range statistics
        
        Args:
            min_price: Minimum price
            max_price: Maximum price
            
        Returns:
            Price range statistics
        """
        try:
            if min_price <= 0 or max_price <= 0:
                return {
                    "range": 0,
                    "average": 0,
                    "variability": 0
                }
            
            price_range = max_price - min_price
            average_price = (min_price + max_price) / 2
            variability = (price_range / average_price) * 100 if average_price > 0 else 0
            
            return {
                "range": price_range,
                "average": average_price,
                "variability": variability,
                "min": min_price,
                "max": max_price
            }
            
        except Exception as e:
            logger.error(f"Error calculating price range: {e}")
            return {
                "range": 0,
                "average": 0,
                "variability": 0
            }
    
    @staticmethod
    async def make_http_request(
        url: str, 
        method: str = "GET", 
        headers: Dict[str, str] = None,
        data: Any = None,
        timeout: int = 10
    ) -> Dict[str, Any]:
        """
        Make HTTP request with error handling
        
        Args:
            url: Request URL
            method: HTTP method
            headers: Request headers
            data: Request data
            timeout: Request timeout
            
        Returns:
            Response data
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=data if method in ["POST", "PUT", "PATCH"] else None,
                    timeout=aiohttp.ClientTimeout(total=timeout)
                ) as response:
                    
                    if response.status == 200:
                        try:
                            result = await response.json()
                            return {
                                "success": True,
                                "data": result,
                                "status": response.status
                            }
                        except:
                            text_result = await response.text()
                            return {
                                "success": True,
                                "data": text_result,
                                "status": response.status
                            }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}",
                            "status": response.status
                        }
                        
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Request timeout",
                "status": 408
            }
        except Exception as e:
            logger.error(f"HTTP request error: {e}")
            return {
                "success": False,
                "error": str(e),
                "status": 500
            }
    
    @staticmethod
    def create_error_response(error: str, details: str = None) -> Dict[str, Any]:
        """
        Create standardized error response
        
        Args:
            error: Error message
            details: Additional error details
            
        Returns:
            Error response dictionary
        """
        response = {
            "success": False,
            "error": error,
            "timestamp": datetime.now().isoformat(),
            "request_id": Utils.generate_response_id()
        }
        
        if details:
            response["details"] = details
        
        return response
    
    @staticmethod
    def create_success_response(data: Any, message: str = None) -> Dict[str, Any]:
        """
        Create standardized success response
        
        Args:
            data: Response data
            message: Success message
            
        Returns:
            Success response dictionary
        """
        response = {
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat(),
            "request_id": Utils.generate_response_id()
        }
        
        if message:
            response["message"] = message
        
        return response
    
    @staticmethod
    def validate_language_code(language_code: str) -> bool:
        """
        Validate language code format
        
        Args:
            language_code: Language code to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check format: xx-XX or xx
            pattern = r'^[a-z]{2}(-[A-Z]{2})?$'
            return bool(re.match(pattern, language_code))
        except Exception as e:
            logger.error(f"Error validating language code: {e}")
            return False
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        """
        Get file extension from filename
        
        Args:
            filename: Filename
            
        Returns:
            File extension
        """
        try:
            return filename.split('.')[-1].lower() if '.' in filename else ""
        except Exception as e:
            logger.error(f"Error getting file extension: {e}")
            return ""
    
    @staticmethod
    def estimate_audio_duration(audio_content: bytes, sample_rate: int = 16000) -> float:
        """
        Estimate audio duration from content
        
        Args:
            audio_content: Audio file content
            sample_rate: Sample rate in Hz
            
        Returns:
            Estimated duration in seconds
        """
        try:
            # Rough estimation based on file size
            # Assuming 16-bit audio (2 bytes per sample)
            bytes_per_sample = 2
            total_samples = len(audio_content) / bytes_per_sample
            duration = total_samples / sample_rate
            
            return max(0.1, duration)  # Minimum 0.1 seconds
            
        except Exception as e:
            logger.error(f"Error estimating audio duration: {e}")
            return 0.0
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format duration in human-readable format
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        try:
            if seconds < 60:
                return f"{seconds:.1f}s"
            elif seconds < 3600:
                minutes = seconds / 60
                return f"{minutes:.1f}m"
            else:
                hours = seconds / 3600
                return f"{hours:.1f}h"
                
        except Exception as e:
            logger.error(f"Error formatting duration: {e}")
            return f"{seconds}s"
    
    @staticmethod
    def log_request_info(request_data: Dict[str, Any]) -> None:
        """
        Log request information for debugging
        
        Args:
            request_data: Request data dictionary
        """
        try:
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "request_id": request_data.get("request_id", "unknown"),
                "endpoint": request_data.get("endpoint", "unknown"),
                "method": request_data.get("method", "unknown"),
                "user_agent": request_data.get("user_agent", "unknown"),
                "ip_address": request_data.get("ip_address", "unknown")
            }
            
            logger.info(f"Request info: {json.dumps(log_data)}")
            
        except Exception as e:
            logger.error(f"Error logging request info: {e}")

# Export utility functions
__all__ = ["Utils"] 