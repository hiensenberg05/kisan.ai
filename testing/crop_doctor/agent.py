import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool, google_search
from dotenv import load_dotenv

# Import the custom tools and the detailed prompt
from . import prompts
from . import tools

# Load environment variables from .env file
load_dotenv()

# Define Plant Health Assessment Tool
plant_health_tool = FunctionTool(tools.get_plant_health_assessment)

# Define IndiaMART Scraper Tool
indiamart_scraper_tool = FunctionTool(tools.scrape_indiamart_for_remedies)
google_search_tool = FunctionTool(tools.search_remedy_prices_google)
# Create the Agent instance
crop_doctor_agent = Agent(
    model="gemini-2.0-flash",
    name="crop_doctor_agent",
    instruction=prompts.CROP_DOCTOR_PROMPT,
    tools=[
        plant_health_tool,
        indiamart_scraper_tool,
        google_search_tool
        
    ],
)

root_agent = crop_doctor_agent