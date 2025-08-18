"""
Base Agent class with LLM integration for all agents.
"""
from typing import Dict, Any, Optional, List
from services.llm_service import llm_service

class BaseAgent:
    """Base class for all agents with LLM integration."""
    
    def __init__(self, name: str, description: str, system_prompt: str = ""):
        """
        Initialize the base agent with LLM capabilities.
        
        Args:
            name: Name of the agent
            description: Description of the agent's purpose
            system_prompt: Initial system prompt for the agent
        """
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
    
    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Generate text using the LLM service."""
        full_prompt = f"""{self.system_prompt}
        
        {prompt}
        """
        return await llm_service.generate_text(full_prompt, **kwargs)
    
    async def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """
        Chat with the LLM service.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            **kwargs: Additional parameters for the LLM
        """
        # Add system prompt if not already present
        if messages and messages[0]["role"] != "system":
            messages = [{"role": "system", "content": self.system_prompt}] + messages
        return await llm_service.chat(messages, **kwargs)
