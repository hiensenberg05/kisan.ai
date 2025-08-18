# backend/services/scheme_service.py
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from utils.logger import get_logger
from core.config import settings

logger = get_logger(__name__)

@dataclass
class Scheme:
    id: str
    name: str
    description: str
    eligibility: str
    benefits: str
    application_process: str
    documents_required: List[str]
    contact: str
    website: str
    category: str
    state: str
    last_updated: str
    embedding: Optional[np.ndarray] = None

class SchemeService:
    """Service for managing and retrieving government schemes using RAG."""
    
    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2"):
        self.schemes: List[Scheme] = []
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.embedding_size = 384  # Default for all-MiniLM-L6-v2
        self._load_schemes()
    
    def _load_schemes(self):
        """Load schemes from JSON file and generate embeddings."""
        try:
            # Load from JSON file
            data_dir = Path(__file__).parent.parent / "data"
            schemes_file = data_dir / "government_schemes.json"
            
            with open(schemes_file, 'r', encoding='utf-8') as f:
                schemes_data = json.load(f)
            
            # Create Scheme objects and generate embeddings
            for scheme_data in schemes_data:
                scheme = Scheme(
                    id=scheme_data["id"],
                    name=scheme_data["name"],
                    description=scheme_data["description"],
                    eligibility=scheme_data.get("eligibility", ""),
                    benefits=scheme_data.get("benefits", ""),
                    application_process=scheme_data.get("application_process", ""),
                    documents_required=scheme_data.get("documents_required", []),
                    contact=scheme_data.get("contact", ""),
                    website=scheme_data.get("website", ""),
                    category=scheme_data.get("category", "General"),
                    state=scheme_data.get("state", "National"),
                    last_updated=scheme_data.get("last_updated", "")
                )
                
                # Generate embedding for semantic search
                text_to_embed = f"{scheme.name} {scheme.description} {scheme.benefits} {scheme.category}"
                scheme.embedding = self.embedding_model.encode(text_to_embed, convert_to_numpy=True)
                self.schemes.append(scheme)
                
            logger.info(f"Loaded {len(self.schemes)} schemes with embeddings")
            
        except Exception as e:
            logger.error(f"Error loading schemes: {str(e)}")
            raise
    
    def search_schemes(
        self,
        query: str,
        state: Optional[str] = None,
        category: Optional[str] = None,
        top_k: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Search for schemes using semantic search.
        
        Args:
            query: Natural language query
            state: Filter by state (optional)
            category: Filter by category (optional)
            top_k: Number of results to return
            similarity_threshold: Minimum similarity score (0-1)
            
        Returns:
            List of matching schemes with similarity scores
        """
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query, convert_to_numpy=True)
            query_embedding = query_embedding.reshape(1, -1)
            
            # Calculate similarities
            results = []
            for scheme in self.schemes:
                # Apply filters
                if state and scheme.state.lower() != state.lower():
                    continue
                if category and scheme.category.lower() != category.lower():
                    continue
                
                # Calculate cosine similarity
                sim = cosine_similarity(
                    query_embedding,
                    scheme.embedding.reshape(1, -1)
                )[0][0]
                
                if sim >= similarity_threshold:
                    scheme_dict = scheme.__dict__.copy()
                    scheme_dict.pop('embedding', None)  # Remove embedding from result
                    scheme_dict['similarity_score'] = float(sim)
                    results.append(scheme_dict)
            
            # Sort by similarity score (descending)
            results.sort(key=lambda x: x['similarity_score'], reverse=True)
            
            return results[:top_k]
            
        except Exception as e:
            logger.error(f"Error searching schemes: {str(e)}")
            raise
    
    def get_scheme_by_id(self, scheme_id: str) -> Optional[Dict[str, Any]]:
        """Get a scheme by its ID."""
        for scheme in self.schemes:
            if scheme.id == scheme_id:
                result = scheme.__dict__.copy()
                result.pop('embedding', None)
                return result
        return None

# Singleton instance
scheme_service = SchemeService()