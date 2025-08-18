import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import vision
import logging
from typing import Dict, Any, Optional, List
import base64
import io
import json

from config import settings

logger = logging.getLogger(__name__)

class VisionHandler:
    """
    Vision handler for crop disease diagnosis using Google Cloud Vision API and Gemini Vision.
    Handles image analysis for agricultural purposes.
    """
    
    def __init__(self):
        """Initialize Vision handler with Google Cloud Vision and Gemini Vision"""
        # Initialize Vertex AI
        vertexai.init(
            project=settings.GOOGLE_CLOUD_PROJECT_ID,
            location=settings.GOOGLE_CLOUD_LOCATION
        )
        
        # Initialize Vision client
        self.vision_client = vision.ImageAnnotatorClient()
        
        # Initialize Gemini Vision model
        self.gemini_vision = GenerativeModel("gemini-2.0-flash-exp")
        
        # Common crop diseases and their visual indicators
        self.crop_diseases = {
            "tomato": [
                "early_blight", "late_blight", "bacterial_speck", "bacterial_spot",
                "leaf_mold", "septoria_leaf_spot", "verticillium_wilt", "fusarium_wilt"
            ],
            "rice": [
                "bacterial_blight", "brown_spot", "blast", "sheath_blight",
                "tungro", "bacterial_leaf_streak", "false_smut"
            ],
            "wheat": [
                "rust", "powdery_mildew", "septoria", "fusarium_head_blight",
                "tan_spot", "stripe_rust", "leaf_rust"
            ],
            "potato": [
                "late_blight", "early_blight", "bacterial_wilt", "blackleg",
                "common_scab", "powdery_scab", "pink_rot"
            ],
            "corn": [
                "northern_leaf_blight", "southern_leaf_blight", "gray_leaf_spot",
                "common_rust", "southern_rust", "anthracnose"
            ]
        }
        
        # Disease symptoms for better analysis
        self.disease_symptoms = {
            "early_blight": "dark brown spots with concentric rings, yellow halos",
            "late_blight": "water-soaked lesions, white fungal growth",
            "bacterial_speck": "small black spots with yellow halos",
            "bacterial_spot": "dark brown spots with yellow margins",
            "rust": "orange to brown powdery spots on leaves",
            "powdery_mildew": "white powdery growth on leaves",
            "blast": "diamond-shaped lesions with gray centers"
        }
        
        logger.info("Vision Handler initialized for crop disease diagnosis")
    
    async def analyze_crop_image(self, image_content: bytes) -> str:
        """
        Analyze crop image for disease diagnosis using multiple AI models.
        
        Args:
            image_content: Raw image bytes
            
        Returns:
            Detailed analysis and diagnosis
        """
        try:
            logger.info("Starting crop image analysis")
            
            # Step 1: Basic image analysis with Vision API
            vision_analysis = await self._analyze_with_vision_api(image_content)
            
            # Step 2: Detailed analysis with Gemini Vision
            gemini_analysis = await self._analyze_with_gemini_vision(image_content)
            
            # Step 3: Combine and synthesize results
            final_analysis = await self._synthesize_analysis(vision_analysis, gemini_analysis)
            
            return final_analysis
            
        except Exception as e:
            logger.error(f"Error in crop image analysis: {e}", exc_info=True)
            return "An error occurred. Please try again later."
    
    async def _analyze_with_vision_api(self, image_content: bytes) -> Dict[str, Any]:
        """Analyze image using Google Cloud Vision API"""
        try:
            # Create image object
            image = vision.Image(content=image_content)
            
            # Perform multiple analyses
            analyses = {}
            
            # Label detection
            label_response = self.vision_client.label_detection(image=image)
            labels = label_response.label_annotations
            analyses["labels"] = [label.description for label in labels]
            
            # Text detection (for any text in image)
            text_response = self.vision_client.text_detection(image=image)
            texts = text_response.text_annotations
            if texts:
                analyses["text"] = texts[0].description
            
            # Object detection
            object_response = self.vision_client.object_localization(image=image)
            objects = object_response.localized_object_annotations
            analyses["objects"] = [obj.name for obj in objects]
            
            # Color analysis
            properties_response = self.vision_client.image_properties(image=image)
            colors = properties_response.image_properties_annotation.dominant_colors.colors
            analyses["dominant_colors"] = [
                {
                    "red": color.color.red,
                    "green": color.color.green,
                    "blue": color.color.blue,
                    "score": color.score
                }
                for color in colors[:5]  # Top 5 colors
            ]
            
            logger.info(f"Vision API analysis completed: {len(analyses)} analyses")
            return analyses
            
        except Exception as e:
            logger.error(f"Error in Vision API analysis: {e}", exc_info=True)
            return {"error": "An error occurred. Please try again later."}
    
    async def _analyze_with_gemini_vision(self, image_content: bytes) -> str:
        """Analyze image using Gemini Vision for detailed crop analysis"""
        try:
            # Convert image to base64 for Gemini
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            
            # Create concise prompt for agricultural analysis
            prompt = """
            You are an expert agricultural pathologist. Analyze this crop image and provide a structured diagnosis.
            
            Focus on:
            1. Identifying the crop/plant species
            2. Noting any visible symptoms (spots, discoloration, damage)
            3. Identifying potential diseases/pests/nutrient issues
            
            Format your response concisely:
            
            Plant: [crop/plant species or "Unidentified"]
            
            Symptoms: [1-3 key symptoms, comma-separated]
            
            Possible Issues: [1-3 most likely problems]
            
            Confidence: [High/Medium/Low] - [brief reason]
            
            Keep the response brief and to the point. Use simple agricultural terms.
            If uncertain, say so rather than guessing.
            """
            
            # Generate response with Gemini Vision
            response = self.gemini_vision.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_base64}])
            
            logger.info("Gemini Vision analysis completed")
            return response.text
            
        except Exception as e:
            logger.error(f"Error in Gemini Vision analysis: {e}", exc_info=True)
            return "An error occurred. Please try again later."
    
    async def _synthesize_analysis(self, vision_analysis: Dict[str, Any], gemini_analysis: str) -> str:
        """Synthesize results from both Vision API and Gemini Vision"""
        try:
            # Create concise analysis prompt
            synthesis_prompt = f"""
            You are an agricultural expert. Analyze the following crop image data and provide a concise diagnosis:
            
            Vision API Analysis: {json.dumps(vision_analysis, indent=2)}
            
            Gemini Vision Analysis: {gemini_analysis}
            
            Format your response in this exact structure:
            
            Crop Identification: [crop/plant species or "Unable to identify"]
            
            Visible Symptoms: [1-3 most prominent symptoms]
            
            Likely Issue: [most probable disease/pest/nutrient problem]
            
            Confidence: [High/Medium/Low] - [brief reason for confidence level]
            
            Recommended Actions:
            1. [Primary action]
            2. [Secondary action]
            3. [Additional action if needed]
            
            Note: [If professional consultation is recommended]
            
            Keep the entire response concise (max 150 words). Use simple language suitable for farmers.
            """
            
            # Generate synthesized response
            response = self.gemini_vision.generate_content(synthesis_prompt)
            
            # Clean up the response
            clean_response = response.text.strip()
            return clean_response
            
        except Exception as e:
            logger.error(f"Error synthesizing analysis: {e}", exc_info=True)
            # Fallback to combining results manually
            return f"""
            **Image Analysis Results:**
            
            **Vision API Findings:**
            {json.dumps(vision_analysis, indent=2)}
            
            **Detailed Analysis:**
            {gemini_analysis}
            
            **Note:** Please consult with a local agricultural expert for confirmation of any diagnosis.
            """
    
    async def detect_crop_species(self, image_content: bytes) -> str:
        """Detect crop species from image"""
        try:
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            
            prompt = """
            Identify the crop or plant species shown in this image. 
            Focus on common agricultural crops in India such as:
            - Rice, Wheat, Corn, Millet
            - Tomato, Potato, Onion, Peppers
            - Cotton, Sugarcane, Tea, Coffee
            - Pulses (lentils, chickpeas, etc.)
            
            Provide the most likely crop name and any relevant details about the plant.
            """
            
            response = self.gemini_vision.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_base64}])
            return response.text
            
        except Exception as e:
            logger.error(f"Error detecting crop species: {e}", exc_info=True)
            return "Unable to identify crop species from image"
    
    async def analyze_disease_symptoms(self, image_content: bytes, crop_type: str = None) -> str:
        """Analyze disease symptoms for specific crop type"""
        try:
            image_base64 = base64.b64encode(image_content).decode('utf-8')
            
            # Get common diseases for the crop type
            common_diseases = []
            if crop_type and crop_type.lower() in self.crop_diseases:
                common_diseases = self.crop_diseases[crop_type.lower()]
            
            prompt = f"""
            Analyze this image for disease symptoms in {crop_type if crop_type else 'the crop'}.
            
            Look for these common symptoms:
            - Leaf spots, lesions, or discoloration
            - Wilting or drooping leaves
            - Powdery or fuzzy growth
            - Yellowing or browning
            - Stunted growth
            - Unusual patterns or markings
            
            {f'Common diseases for {crop_type}: {", ".join(common_diseases)}' if common_diseases else ''}
            
            Provide a detailed analysis of any symptoms you observe and suggest possible causes.
            """
            
            response = self.gemini_vision.generate_content([prompt, {"mime_type": "image/jpeg", "data": image_base64}])
            return response.text
            
        except Exception as e:
            logger.error(f"Error analyzing disease symptoms: {e}", exc_info=True)
            return "An error occurred. Please try again later."
    
    async def validate_image_quality(self, image_content: bytes) -> Dict[str, Any]:
        """Validate image quality for analysis"""
        try:
            # Basic image validation
            image_size = len(image_content)
            
            # Check minimum size (at least 10KB)
            if image_size < 10240:
                return {
                    "valid": False,
                    "reason": "Image too small for analysis",
                    "size_bytes": image_size
                }
            
            # Check maximum size (max 10MB)
            if image_size > 10485760:
                return {
                    "valid": False,
                    "reason": "Image too large for analysis",
                    "size_bytes": image_size
                }
            
            # Try to analyze with Vision API for basic validation
            image = vision.Image(content=image_content)
            response = self.vision_client.label_detection(image=image)
            
            if response.label_annotations:
                return {
                    "valid": True,
                    "size_bytes": image_size,
                    "labels_detected": len(response.label_annotations)
                }
            else:
                return {
                    "valid": False,
                    "reason": "No recognizable content in image",
                    "size_bytes": image_size
                }
                
        except Exception as e:
            logger.error(f"Error validating image quality: {e}", exc_info=True)
            return {
                "valid": False,
                "reason": "An error occurred. Please try again later.",
                "size_bytes": len(image_content) if image_content else 0
            }
    
    async def test_connection(self) -> bool:
        """Test Vision API connection"""
        try:
            # Create a simple test image (1x1 pixel)
            test_image = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7),01444\x1f\'9=82<.342\xff\xc0\x00\x11\x08\x00\x01\x00\x01\x01\x01\x11\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\xff\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00\x3f\x00\xaa\xff\xd9'
            
            image = vision.Image(content=test_image)
            response = self.vision_client.label_detection(image=image)
            
            logger.info("Vision API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Vision API connection test failed: {e}", exc_info=True)
            return False 