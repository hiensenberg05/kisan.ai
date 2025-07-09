import vertexai
from vertexai.generative_models import GenerativeModel, Tool
from vertexai import rag

# --- CORRECTED RAG IMPORTS ---
# Import RAG components using the correct pattern
# All RAG components are accessed through the rag module
# --- END CORRECTED RAG IMPORTS ---

import logging
from typing import Dict, Any, Optional, List
import json
import base64

from config import settings # Assuming 'config.py' exists and holds your settings

logger = logging.getLogger(__name__)

class RAGTool:
    """
    RAG (Retrieval-Augmented Generation) tool for agricultural knowledge retrieval.
    Uses Google Vertex AI RAG system with custom corpus.
    """
    
    def __init__(self):
        """Initialize RAG tool with Vertex AI configuration"""
        # Initialize Vertex AI
        vertexai.init(
            project=settings.GOOGLE_CLOUD_PROJECT_ID,
            location=settings.GOOGLE_CLOUD_LOCATION
        )
        
        # RAG Corpus configuration
        self.project_id = settings.GOOGLE_CLOUD_PROJECT_ID
        self.location = settings.GOOGLE_CLOUD_LOCATION
        self.rag_corpus_id = settings.RAG_CORPUS_ID
        
        # Construct corpus resource name
        self.rag_corpus_name = f"projects/{self.project_id}/locations/{self.location}/ragCorpora/{self.rag_corpus_id}"
        
        # Corpus mapping for different types of queries (This mapping logic isn't used
        # in the current code but might be for future enhancements with multiple corpora)
        self.corpus_mapping = {
            "disease_causes": "disease_causes",
            "remedies": "remedies", 
            "government_policies": "government_policies",
            "general_queries": "general_queries"
        }
        
        # Initialize Gemini model for RAG-enhanced generation
        self.rag_model = GenerativeModel(
            model_name="gemini-2.0-flash", # Updated to Gemini 2.0 Flash model
            generation_config={
                "temperature": 0.3,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            }
        )
        
        # RAG retrieval configuration - Using the imported RagRetrievalConfig
        self.rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=5,  # Retrieve top 5 relevant chunks
            filter=rag.Filter(vector_distance_threshold=0.7), # Using rag.Filter
        )

        logger.info(f"RAG Tool initialized with corpus: {self.rag_corpus_name}")
    
    async def test_connection(self) -> bool:
        """Test RAG corpus connection and accessibility"""
        try:
            # Use the rag.list_files function
            files = rag.list_files(rag_corpus=self.rag_corpus_name)
            logger.info(f"RAG connection test successful. Found {len(list(files))} files.")
            return True
        except Exception as e:
            logger.error(f"RAG connection test failed: {e}", exc_info=True)
            return False
    
    async def query_knowledge(self, query: str, corpus_type: str = "general_queries") -> str:
        """
        Query agricultural knowledge using RAG system.
        
        Args:
            query: The user's question
            corpus_type: Type of corpus to search (disease_causes, remedies, etc.)
            
        Returns:
            Generated response based on retrieved knowledge
        """
        try:
            logger.info(f"Querying RAG knowledge: {query} (corpus: {corpus_type})")
            
            # Step 1: Direct retrieval for context
            retrieval_response = self._retrieve_context(query, corpus_type) # No await, as _retrieve_context is not async
            
            if not retrieval_response:
                logger.warning("No relevant context retrieved from RAG")
                return self._fallback_response(query) # No await, as _fallback_response is not async
            
            # Step 2: Generate response using retrieved context
            response = self._generate_response(query, retrieval_response, corpus_type) # No await, as _generate_response is not async
            
            return response
            
        except Exception as e:
            logger.error(f"Error in RAG query: {e}", exc_info=True)
            return self._fallback_response(query) # No await
    
    # Changed to synchronous as retrieval_query is not async
    def _retrieve_context(self, query: str, corpus_type: str) -> Optional[str]:
        """Retrieve relevant context from RAG corpus"""
        try:
            # Perform direct retrieval query - Using the imported retrieval_query function
            response = rag.retrieval_query(
                rag_resources=[
                    # Use the imported RagResource class
                    rag.RagResource(
                        rag_corpus=self.rag_corpus_name,
                        # You can specify specific file IDs if needed
                        # rag_file_ids=["file1", "file2"]
                    )
                ],
                text=query,
                rag_retrieval_config=self.rag_retrieval_config,
            )
            
            # Extract and format retrieved context
            if hasattr(response, 'contexts') and response.contexts:
                contexts = []
                for context in response.contexts:
                    if hasattr(context, 'text'):
                        contexts.append(context.text)
                
                return "\n\n".join(contexts)
            else:
                logger.warning("No contexts found in RAG response")
                return None
                
        except Exception as e:
            logger.error(f"Error in context retrieval: {e}", exc_info=True)
            return None
    
    # Changed to synchronous as generate_content is not async
    def _generate_response(self, query: str, context: str, corpus_type: str) -> str:
        """Generate response using retrieved context and Gemini model"""
        try:
            # Create RAG retrieval tool - Using the imported Retrieval and VertexRagStore
            # Note: If _retrieve_context already retrieves the best context,
            # this tool might be redundant in this specific setup, but it's
            # syntactically correct for tool-augmented generation.
            rag_retrieval_tool = Tool.from_retrieval(
                retrieval=rag.Retrieval(
                    source=rag.VertexRagStore(
                        rag_resources=[
                            rag.RagResource( # Use the imported RagResource class
                                rag_corpus=self.rag_corpus_name,
                            )
                        ],
                        rag_retrieval_config=self.rag_retrieval_config,
                    ),
                )
            )
            
            # Create model with RAG tool
            rag_enhanced_model = GenerativeModel(
                model_name="gemini-2.0-flash", # Updated to Gemini 2.0 Flash model
                tools=[rag_retrieval_tool],
                generation_config={
                    "temperature": 0.3,
                    "top_p": 0.8,
                    "top_k": 40,
                    "max_output_tokens": 2048,
                }
            )
            
            # Generate response with context
            response_prompt = f"""
            You are an agricultural expert assistant for Indian farmers. 
            Answer the following question using the provided agricultural knowledge.
            
            Question: {query}
            
            Available Context: {context}
            
            Please provide a comprehensive, practical answer that:
            1. Directly addresses the farmer's question
            2. Uses simple, understandable language suitable for Indian farmers
            3. Provides actionable advice and recommendations
            4. Considers local agricultural practices and conditions
            5. Includes relevant examples or tips when appropriate
            
            Focus on being helpful, practical, and culturally appropriate for Indian farmers.
            """
            
            response = rag_enhanced_model.generate_content(response_prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error in response generation: {e}", exc_info=True)
            # Fallback to simple model without RAG
            return self._simple_response(query, context) # No await
    
    # Changed to synchronous as generate_content is not async
    def _simple_response(self, query: str, context: str) -> str:
        """Fallback response generation without RAG tool"""
        try:
            response_prompt = f"""
            You are an agricultural expert assistant for Indian farmers.
            
            Question: {query}
            Context: {context}
            
            Provide a helpful, practical answer in simple language.
            """
            
            response = self.rag_model.generate_content(response_prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error in simple response generation: {e}", exc_info=True)
            return "An error occurred. Please try again later."
    
    # Changed to synchronous as generate_content is not async
    def _fallback_response(self, query: str) -> str:
        """Fallback response when RAG system is unavailable"""
        try:
            fallback_prompt = f"""
            You are an agricultural expert assistant for Indian farmers.
            The farmer is asking: {query}
            
            Provide a general, helpful response about agricultural topics.
            Keep it practical and suitable for Indian farming conditions.
            """
            
            response = self.rag_model.generate_content(fallback_prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error in fallback response: {e}", exc_info=True)
            return "An error occurred. Please try again later."
    
    async def search_diseases(self, crop: str, symptoms: str) -> str:
        """Search for crop diseases based on symptoms"""
        try:
            query = f"disease symptoms {crop} {symptoms}"
            return await self.query_knowledge(query, "disease_causes")
        except Exception as e:
            logger.error(f"Error searching diseases: {e}", exc_info=True)
            return self._fallback_response(f"disease in {crop} with {symptoms}") # No await
    
    async def search_remedies(self, disease: str, crop: str) -> str:
        """Search for remedies for specific diseases"""
        try:
            query = f"treatment remedy {disease} {crop}"
            return await self.query_knowledge(query, "remedies")
        except Exception as e:
            logger.error(f"Error searching remedies: {e}", exc_info=True)
            return self._fallback_response(f"remedy for {disease} in {crop}") # No await
    
    async def search_policies(self, policy_query: str) -> str:
        """Search for government policies and schemes"""
        try:
            return await self.query_knowledge(policy_query, "government_policies")
        except Exception as e:
            logger.error(f"Error searching policies: {e}", exc_info=True)
            return self._fallback_response(policy_query) # No await
    
    async def get_general_info(self, topic: str) -> str:
        """Get general agricultural information"""
        try:
            return await self.query_knowledge(topic, "general_queries")
        except Exception as e:
            logger.error(f"Error getting general info: {e}", exc_info=True)
            return self._fallback_response(topic) # No await
    
    async def list_corpus_files(self) -> List[str]:
        """List all files in the RAG corpus"""
        try:
            # Use the rag.list_files function
            files = rag.list_files(rag_corpus=self.rag_corpus_name)
            file_list = []
            for file in files:
                if hasattr(file, 'name'):
                    file_list.append(file.name)
            return file_list
        except Exception as e:
            logger.error(f"Error listing corpus files: {e}", exc_info=True)
            return []
    
    async def get_corpus_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG corpus"""
        try:
            files = await self.list_corpus_files()
            return {
                "total_files": len(files),
                "corpus_id": self.rag_corpus_id,
                "corpus_name": self.rag_corpus_name,
                "available_corpus_types": list(self.corpus_mapping.keys())
            }
        except Exception as e:
            logger.error(f"Error getting corpus stats: {e}", exc_info=True)
            return {
                "error": str(e),
                "corpus_id": self.rag_corpus_id
            }