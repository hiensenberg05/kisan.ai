"""
Tools package for Kisan.AI

This package contains various utility tools used by the Kisan.AI backend,
including web scraping, NLP utilities, and trend analysis.
"""

from .web_scraper import WebScraper
from .nlp_utils import *  # Import other utilities as needed
from .trend_analysis import *

__all__ = [
    'WebScraper',
    # Add other exported names here
]
