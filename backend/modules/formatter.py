"""
Text formatting utilities for Kisan AI backend.
Handles formatting of various types of content for consistent display.
"""

from typing import Any, Dict, List, Union
import re
from datetime import datetime
import json
from typing import Optional

class TextFormatter:
    """Handles formatting of text content with consistent styling."""
    
    def __init__(self):
        self.bullet_point = "•"
        self.indent = "  "
    
    def format_as_list(
        self, 
        items: List[Any], 
        numbered: bool = False,
        indent_level: int = 0
    ) -> str:
        """
        Format a list of items as a bulleted or numbered list.
        
        Args:
            items: List of items to format
            numbered: Whether to use numbers instead of bullet points
            indent_level: Number of indentation levels
            
        Returns:
            Formatted string
        """
        indent = self.indent * indent_level
        result = []
        
        for i, item in enumerate(items, 1):
            prefix = f"{i}. " if numbered else f"{self.bullet_point} "
            result.append(f"{indent}{prefix}{str(item)}")
            
        return "\n".join(result)
    
    def format_key_value(
        self, 
        data: Dict[str, Any],
        separator: str = ": ",
        indent_level: int = 0
    ) -> str:
        """
        Format a dictionary as key-value pairs.
        
        Args:
            data: Dictionary to format
            separator: Separator between key and value
            indent_level: Number of indentation levels
            
        Returns:
            Formatted string
        """
        indent = self.indent * indent_level
        max_key_length = max(len(str(k)) for k in data.keys()) if data else 0
        
        result = []
        for key, value in data.items():
            if isinstance(value, (list, dict)):
                value_str = json.dumps(value, indent=2, ensure_ascii=False)
            else:
                value_str = str(value)
                
            key_part = str(key).ljust(max_key_length)
            result.append(f"{indent}{key_part}{separator}{value_str}")
            
        return "\n".join(result)
    
    def format_scheme_details(self, scheme_data: Dict[str, Any]) -> str:
        """
        Format government scheme details in a user-friendly way.
        
        Args:
            scheme_data: Dictionary containing scheme details
            
        Returns:
            Formatted scheme information
        """
        if not scheme_data:
            return "No scheme information available."
            
        sections = []
        
        # Title
        title = scheme_data.get('name', 'Unnamed Scheme')
        sections.append(f"📌 {title.upper()}")
        sections.append("=" * (len(title) + 2))
        
        # Basic info
        sections.append("\nℹ️ BASIC INFORMATION")
        sections.append("-" * 30)
        info = {
            "Category": scheme_data.get('category', 'N/A'),
            "State": scheme_data.get('state', 'All India'),
            "Last Updated": scheme_data.get('last_updated', 'N/A')
        }
        sections.append(self.format_key_value(info))
        
        # Description
        sections.append("\n📝 DESCRIPTION")
        sections.append("-" * 30)
        sections.append(scheme_data.get('description', 'No description available.'))
        
        # Benefits
        benefits = scheme_data.get('benefits', [])
        if benefits:
            sections.append("\n✨ BENEFITS")
            sections.append("-" * 30)
            sections.append(self.format_as_list(benefits))
        
        # Eligibility
        eligibility = scheme_data.get('eligibility', [])
        if eligibility:
            sections.append("\n✅ ELIGIBILITY")
            sections.append("-" * 30)
            if isinstance(eligibility, str):
                sections.append(eligibility)
            else:
                sections.append(self.format_as_list(eligibility))
        
        # Application Process
        app_process = scheme_data.get('application_process', '')
        if app_process:
            sections.append("\n📝 HOW TO APPLY")
            sections.append("-" * 30)
            sections.append(app_process)
        
        # Required Documents
        docs = scheme_data.get('documents_required', [])
        if docs:
            sections.append("\n📄 REQUIRED DOCUMENTS")
            sections.append("-" * 30)
            sections.append(self.format_as_list(docs))
        
        # Contact Information
        contact_info = {
            "Contact": scheme_data.get('contact', 'Not specified'),
            "Website": scheme_data.get('website', 'Not available')
        }
        sections.append("\n📞 CONTACT INFORMATION")
        sections.append("-" * 30)
        sections.append(self.format_key_value(contact_info))
        
        return "\n".join(sections)
    
    def format_error(self, error_message: str, details: Optional[Dict] = None) -> str:
        """
        Format an error message with optional details.
        
        Args:
            error_message: Main error message
            details: Optional dictionary with error details
            
        Returns:
            Formatted error message
        """
        error_lines = [
            "❌ ERROR",
            "=" * 30,
            error_message
        ]
        
        if details:
            error_lines.append("\nDetails:")
            error_lines.append(self.format_key_value(details, indent_level=1))
            
        return "\n".join(error_lines)

# Singleton instance
formatter = TextFormatter()