import vertexai
from vertexai.generative_models import GenerativeModel, Tool
import logging
from typing import Dict, Any, Optional
import json
import re

from tools.rag import RAGTool
from tools.market import MarketDataHandler
from tools.policies import GovernmentPoliciesHandler
from tools.vision import VisionHandler
from config import settings
from tools.output_parser import concise_output

logger = logging.getLogger(__name__)

class KisanAgent:
    """
    Main orchestrator system for Project Kisan.
    Handles intent recognition and routes queries to appropriate tools.
    """
    
    def __init__(self):
        """Initialize the Kisan Agent with Vertex AI and tools"""
        # Initialize Vertex AI
        vertexai.init(
            project=settings.GOOGLE_CLOUD_PROJECT_ID,
            location=settings.GOOGLE_CLOUD_LOCATION
        )
        
        # Initialize tools
        self.rag_tool = RAGTool()
        self.market_handler = MarketDataHandler()
        self.policies_handler = GovernmentPoliciesHandler()
        self.vision_handler = VisionHandler()
        
        # Initialize Gemini model (lighter config for latency)
        self.model = GenerativeModel(
            model_name="gemini-2.0-flash",
            generation_config={
                "temperature": settings.GEMINI_TEMPERATURE,
                "top_p": 0.8,
                "top_k": 20,
                "max_output_tokens": settings.GEMINI_MAX_TOKENS,
            }
        )
        
        # Intent classification prompts
        self.intent_prompts = {
            "crop_disease": """
            You are an agricultural expert. Classify if the user query is about:
            - Crop diseases, pests, or plant health issues
            - Symptoms like yellow leaves, spots, wilting, etc.
            - Treatment or remedies for plant problems
            
            Query: {query}
            
            Respond with only: CROP_DISEASE or OTHER
            """,
            
            "market_prices": """
            You are an agricultural expert. Classify if the user query is about:
            - Market prices of crops
            - Selling crops or market information
            - Price trends or market analysis
            - When to sell crops
            
            Query: {query}
            
            Respond with only: MARKET_PRICES or OTHER
            """,
            
            "government_policies": """
            You are an agricultural expert. Classify if the user query is about:
            - Government schemes, subsidies, or policies
            - Financial assistance for farmers
            - Agricultural programs or support
            - Eligibility for government benefits
            
            Query: {query}
            
            Respond with only: GOVERNMENT_POLICIES or OTHER
            """,
            
            "general_agriculture": """
            You are an agricultural expert. Classify if the user query is about:
            - General farming practices
            - Crop cultivation techniques
            - Soil management
            - Weather and farming
            - General agricultural knowledge
            
            Query: {query}
            
            Respond with only: GENERAL_AGRICULTURE or OTHER
            """
        }
        
        # Response templates
        self.response_templates = {
            "crop_disease": """
            Based on the analysis, here's what I found about your crop issue:
            
            {analysis}
            
            **Recommended Actions:**
            {recommendations}
            
            **Prevention Tips:**
            {prevention}
            
            If you need more specific help, please share a photo of the affected plant.
            """,
            
            "market_prices": """
            Here's the current market information for {crop}:
            
            **Current Prices:**
            {prices}
            
            **Market Analysis:**
            {analysis}
            
            **Recommendation:**
            {recommendation}
            """,
            
            "government_policies": """
            Here are the relevant government schemes and policies:
            
            **Available Schemes:**
            {schemes}
            
            **Eligibility:**
            {eligibility}
            
            **How to Apply:**
            {application}
            """,
            
            "general_agriculture": """
            Here's information about {topic}:
            
            {information}
            
            **Best Practices:**
            {best_practices}
            
            **Additional Resources:**
            {resources}
            """
        }
    
    async def process_text_query(self, query: str) -> str:
        """
        Main method to process text queries from farmers.
        Handles intent recognition and routes to appropriate tools.
        """
        try:
            logger.info(f"Processing query: {query}")
            
            # Fast path: heuristic classification to avoid LLM roundtrip when obvious
            if settings.FAST_MODE:
                ql = query.lower()
                if any(k in ql for k in ["price", "mandi", "market"]):
                    response = await self._handle_market_query(query)
                elif any(k in ql for k in ["scheme", "subsidy", "government", "policy"]):
                    response = await self._handle_policy_query(query)
                elif any(k in ql for k in ["disease", "pest", "wilt", "blight", "rust", "spot"]):
                    response = await self._handle_crop_disease_query(query)
                else:
                    # Light general handler without extra classification
                    response = await self._handle_general_query(query)
            else:
                # Original multi-step route
                intent = await self._classify_intent(query)
                logger.info(f"Classified intent: {intent}")
                if intent == "CROP_DISEASE":
                    response = await self._handle_crop_disease_query(query)
                elif intent == "MARKET_PRICES":
                    response = await self._handle_market_query(query)
                elif intent == "GOVERNMENT_POLICIES":
                    response = await self._handle_policy_query(query)
                elif intent == "GENERAL_AGRICULTURE":
                    response = await self._handle_general_query(query)
                else:
                    response = await self._handle_general_query(query)
                
            return concise_output(response, max_lines=6)
                
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return "An error occurred. Please try again later."
    
    async def _classify_intent(self, query: str) -> str:
        """Classify the intent of the user query"""
        try:
            # Use Gemini to classify intent
            classification_prompt = f"""
            You are an agricultural expert assistant. Analyze the following farmer's query and classify it into one of these categories:

            1. CROP_DISEASE - Questions about plant diseases, pests, symptoms, treatments
            2. MARKET_PRICES - Questions about crop prices, market information, selling advice, mandi rates, price today, price in city, etc.
            3. GOVERNMENT_POLICIES - Questions about government schemes, subsidies, policies, loans, KCC, insurance, eligibility, how to apply, etc.
            4. GENERAL_AGRICULTURE - General farming questions, cultivation techniques, best practices, irrigation, weather, soil, etc.

            Query: "{query}"

            Respond with only the category name (e.g., MARKET_PRICES, CROP_DISEASE, etc.)
            """
            response = self.model.generate_content(classification_prompt)
            intent = response.text.strip().upper()
            return intent
        except Exception as e:
            logger.error(f"Error classifying intent: {e}", exc_info=True)
            return "GENERAL_AGRICULTURE"
    
    async def _handle_crop_disease_query(self, query: str) -> str:
        """Handle crop disease related queries"""
        try:
            extraction_prompt = f"""
            Extract the following information from this crop disease query:
            - Crop name (e.g., tomato, rice, wheat)
            - Symptoms described (e.g., yellow leaves, spots, wilting)
            - Any specific details mentioned

            Query: "{query}"

            Respond in JSON format:
            {{
                "crop": "crop_name",
                "symptoms": "symptoms_description",
                "details": "additional_details"
            }}
            """
            response = self.model.generate_content(extraction_prompt)
            extraction_result = json.loads(response.text)
            rag_query = f"disease symptoms {extraction_result['crop']} {extraction_result['symptoms']}"
            rag_response = await self.rag_tool.query_knowledge(rag_query, "disease_causes")
            response_prompt = f"""
            You are an agricultural expert. A farmer is asking about crop disease issues.

            Query: {query}
            Crop: {extraction_result['crop']}
            Symptoms: {extraction_result['symptoms']}

            RAG Information: {rag_response}

            Please provide a clear, well-formatted answer for the farmer:
            - Start with a short, bolded title (e.g., **Likely Disease and Solution**)
            - Use bullet points for diagnosis, treatment, and prevention
            - Use simple language and short sentences
            - Add a "Tips" section at the end if possible
            - Make the answer easy to read on a mobile phone
            """
            final_response = self.model.generate_content(response_prompt)
            return final_response.text
        except Exception as e:
            logger.error(f"Error handling crop disease query: {e}", exc_info=True)
            return await self._handle_general_query(query)
    
    async def _handle_market_query(self, query: str) -> str:
        """Handle market price related queries (always use market tool, never RAG)"""
        try:
            extraction_prompt = f"""
            Extract the following information from this market query:
            - Crop name (e.g., tomato, rice, wheat)
            - Location/region if mentioned
            - Type of market information needed

            Query: "{query}"

            Respond in JSON format:
            {{
                "crop": "crop_name",
                "location": "location_or_region",
                "info_type": "price/trend/analysis"
            }}
            """
            response = self.model.generate_content(extraction_prompt)
            extraction_result = json.loads(response.text)
            market_data = await self.market_handler.get_crop_prices(
                extraction_result['crop'], 
                extraction_result.get('location')
            )
            analysis_prompt = f"""
            You are an agricultural market expert. Analyze this market data and provide advice to a farmer.

            Query: {query}
            Crop: {extraction_result['crop']}
            Market Data: {market_data}

            Please provide a clear, well-formatted answer for the farmer:
            - Start with a short, bolded title (e.g., **Current Market Prices for Tomato in Bangalore**)
            - Use bullet points for prices, trends, and recommendations
            - Use simple language and short sentences
            - Add a "Tips" section at the end if possible
            - Make the answer easy to read on a mobile phone
            """
            final_response = self.model.generate_content(analysis_prompt)
            return final_response.text
        except Exception as e:
            logger.error(f"Error handling market query: {e}", exc_info=True)
            return await self._handle_general_query(query)
    
    async def _handle_policy_query(self, query: str) -> str:
        """Handle government policy related queries using RAG"""
        try:
            rag_response = await self.rag_tool.query_knowledge(query, "government_policies")
            response_prompt = f"""
            You are an agricultural policy expert. Help a farmer understand government schemes and policies.

            Query: {query}
            RAG Information: {rag_response}

            Please provide a clear, well-formatted answer for the farmer:
            - Start with a short, bolded title (e.g., **Kisan Credit Card - Benefits and How to Apply**)
            - Use bullet points for schemes, eligibility, and application steps
            - Use simple language and short sentences
            - Add a "Tips" section at the end if possible
            - Make the answer easy to read on a mobile phone
            """
            final_response = self.model.generate_content(response_prompt)
            return final_response.text
        except Exception as e:
            logger.error(f"Error handling policy query: {e}", exc_info=True)
            return await self._handle_general_query(query)
    
    async def _handle_general_query(self, query: str) -> str:
        """Handle general agricultural queries using RAG"""
        try:
            corpus_mapping = {
                "disease": "disease_causes",
                "remedy": "remedies", 
                "policy": "government_policies",
                "general": "general_queries"
            }
            query_lower = query.lower()
            selected_corpus = "general_queries"  # default
            for keyword, corpus in corpus_mapping.items():
                if keyword in query_lower:
                    selected_corpus = corpus
                    break
            rag_response = await self.rag_tool.query_knowledge(query, selected_corpus)
            response_prompt = f"""
            You are an agricultural expert assistant. Answer this farmer's question using the provided information.

            Question: {query}
            Agricultural Information: {rag_response}

            Please provide a clear, well-formatted answer for the farmer:
            - Start with a short, bolded title (e.g., **Best Practices for Irrigation**)
            - Use bullet points for key points and recommendations
            - Use simple language and short sentences
            - Add a "Tips" section at the end if possible
            - Make the answer easy to read on a mobile phone
            """
            final_response = self.model.generate_content(response_prompt)
            return final_response.text
        except Exception as e:
            logger.error(f"Error handling general query: {e}", exc_info=True)
            return "An error occurred. Please try again later."
    
    async def process_image_query(self, image_content: bytes, query: str = "") -> str:
        """Process image-based queries for crop disease diagnosis"""
        try:
            # Analyze image for crop diseases
            diagnosis_result = await self.vision_handler.analyze_crop_image(image_content)
            
            # Combine image analysis with text query
            if query:
                full_query = f"Image analysis shows: {diagnosis_result}. Additional question: {query}"
            else:
                full_query = f"Please provide detailed information about this crop condition: {diagnosis_result}"
            
            # Process through text query handler
            return await self.process_text_query(full_query)
            
        except Exception as e:
            logger.error(f"Error processing image query: {e}", exc_info=True)
            return "An error occurred. Please try again later." 