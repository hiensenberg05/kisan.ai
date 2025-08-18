"""
LLM Service for handling Gemini 2.0 Flash model integration.
"""
import google.generativeai as genai
from typing import Dict, Any, Optional, List
from core.config import settings

class LLMService:
    """Service for handling interactions with Gemini 2.0 Flash model."""
    
    def __init__(self):
        """Initialize the Gemini model with the API key from settings."""
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """
        Generate text using Gemini 2.0 Flash model.
        
        Args:
            prompt: The input prompt for the model
            **kwargs: Additional parameters for generation
            
        Returns:
            Generated text response
        """
        try:
            response = await self.model.generate_content_async(
                prompt,
                **{
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                    **kwargs
                }
            )
            return response.text
        except Exception as e:
            raise Exception(f"Error generating text with Gemini: {str(e)}")
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Chat with the Gemini 2.0 Flash model.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional parameters for generation
            
        Returns:
            Generated chat response
        """
        try:
            chat = self.model.start_chat(history=[])
            response = await chat.send_message_async(
                messages,
                **{
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                    **kwargs
                }
            )
            return response.text
        except Exception as e:
            raise Exception(f"Error in chat with Gemini: {str(e)}")

# Create a singleton instance
llm_service = LLMService()
