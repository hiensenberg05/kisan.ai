import logging
from typing import Dict, Any, Optional, List
import json
import re
from datetime import datetime

from config import settings

logger = logging.getLogger(__name__)

class GovernmentPoliciesHandler:
    """
    Government policies handler for searching agricultural schemes and subsidies.
    Provides information about government programs for farmers.
    """
    
    def __init__(self):
        """Initialize government policies handler"""
        # Government schemes database (in a real implementation, this would be in a database)
        self.schemes_database = {
            "pm_kisan": {
                "name": "PM-KISAN (Pradhan Mantri Kisan Samman Nidhi)",
                "description": "Direct income support of ₹6,000 per year to eligible farmer families",
                "eligibility": [
                    "Small and marginal farmers",
                    "Family should own cultivable land",
                    "Should be registered in land records",
                    "Excludes institutional landholders, government employees, professionals"
                ],
                "benefits": [
                    "₹6,000 per year in three equal installments",
                    "Direct transfer to bank account",
                    "No middlemen involved"
                ],
                "how_to_apply": [
                    "Visit PM-KISAN portal (pmkisan.gov.in)",
                    "Fill online application form",
                    "Upload required documents",
                    "Submit to local agriculture office"
                ],
                "documents_required": [
                    "Aadhaar card",
                    "Land records",
                    "Bank account details",
                    "Passport size photograph"
                ],
                "contact": "PM-KISAN Helpline: 155261",
                "website": "https://pmkisan.gov.in"
            },
            
            "pm_fasal_bima": {
                "name": "PM Fasal Bima Yojana (PMFBY)",
                "description": "Crop insurance scheme to protect farmers against natural calamities",
                "eligibility": [
                    "All farmers growing notified crops",
                    "Compulsory for loanee farmers",
                    "Voluntary for non-loanee farmers"
                ],
                "benefits": [
                    "Comprehensive crop insurance coverage",
                    "Low premium rates (1.5% to 5%)",
                    "Quick claim settlement",
                    "Coverage for natural calamities and pests"
                ],
                "how_to_apply": [
                    "Contact nearest bank or insurance company",
                    "Fill insurance application form",
                    "Pay premium amount",
                    "Submit to insurance company"
                ],
                "documents_required": [
                    "Land records",
                    "Crop details",
                    "Bank account details",
                    "Aadhaar card"
                ],
                "contact": "PMFBY Helpline: 1800-180-1551",
                "website": "https://pmfby.gov.in"
            },
            
            "kisan_credit_card": {
                "name": "Kisan Credit Card (KCC)",
                "description": "Credit facility for farmers to meet agricultural needs",
                "eligibility": [
                    "Individual farmers",
                    "Joint borrowers",
                    "Tenant farmers",
                    "Sharecroppers"
                ],
                "benefits": [
                    "Easy credit access",
                    "Flexible repayment options",
                    "Low interest rates",
                    "Coverage for crop production, post-harvest expenses"
                ],
                "how_to_apply": [
                    "Visit nearest bank branch",
                    "Fill KCC application form",
                    "Submit required documents",
                    "Bank will process and issue card"
                ],
                "documents_required": [
                    "Aadhaar card",
                    "Land records",
                    "Bank account",
                    "Passport size photographs"
                ],
                "contact": "Contact nearest bank branch",
                "website": "https://www.nabard.org"
            },
            
            "soil_health_card": {
                "name": "Soil Health Card Scheme",
                "description": "Provides soil health information and recommendations to farmers",
                "eligibility": [
                    "All farmers",
                    "No income or land size restrictions"
                ],
                "benefits": [
                    "Free soil testing",
                    "Personalized fertilizer recommendations",
                    "Improved crop productivity",
                    "Cost savings on fertilizers"
                ],
                "how_to_apply": [
                    "Visit nearest agriculture office",
                    "Fill application form",
                    "Provide soil sample",
                    "Receive card within 30 days"
                ],
                "documents_required": [
                    "Aadhaar card",
                    "Land records",
                    "Soil sample"
                ],
                "contact": "Contact local agriculture office",
                "website": "https://soilhealth.dac.gov.in"
            },
            
            "drip_irrigation": {
                "name": "Per Drop More Crop (Micro Irrigation)",
                "description": "Subsidy for drip and sprinkler irrigation systems",
                "eligibility": [
                    "Small and marginal farmers",
                    "SC/ST farmers",
                    "Women farmers",
                    "Land holding up to 5 hectares"
                ],
                "benefits": [
                    "Up to 55% subsidy on drip irrigation",
                    "Water conservation",
                    "Increased crop yield",
                    "Reduced labor costs"
                ],
                "how_to_apply": [
                    "Contact agriculture department",
                    "Submit application with land details",
                    "Get technical approval",
                    "Install system and claim subsidy"
                ],
                "documents_required": [
                    "Land records",
                    "Aadhaar card",
                    "Bank account details",
                    "Technical approval"
                ],
                "contact": "Contact agriculture department",
                "website": "https://pmksy.gov.in"
            },
            
            "organic_farming": {
                "name": "Paramparagat Krishi Vikas Yojana (PKVY)",
                "description": "Promotes organic farming practices",
                "eligibility": [
                    "Farmers willing to adopt organic farming",
                    "Minimum 50 farmers per cluster",
                    "Land should be free from chemical use for 3 years"
                ],
                "benefits": [
                    "₹50,000 per hectare for 3 years",
                    "Training and capacity building",
                    "Certification support",
                    "Market linkage assistance"
                ],
                "how_to_apply": [
                    "Form farmer group of 50 members",
                    "Submit cluster proposal",
                    "Get approval from agriculture department",
                    "Implement organic practices"
                ],
                "documents_required": [
                    "Farmer group registration",
                    "Land records",
                    "Organic farming plan",
                    "Bank account details"
                ],
                "contact": "Contact agriculture department",
                "website": "https://pgsindia-ncof.gov.in"
            }
        }
        
        # Keywords for scheme matching
        self.scheme_keywords = {
            "pm_kisan": ["pm kisan", "kisan samman nidhi", "6000", "income support", "direct benefit"],
            "pm_fasal_bima": ["crop insurance", "fasal bima", "insurance", "natural calamity", "disaster"],
            "kisan_credit_card": ["credit card", "loan", "credit", "kcc", "bank loan"],
            "soil_health_card": ["soil", "fertilizer", "soil testing", "soil health"],
            "drip_irrigation": ["drip", "irrigation", "water", "sprinkler", "micro irrigation"],
            "organic_farming": ["organic", "natural farming", "chemical free", "pkvy"]
        }
        
        logger.info("Government Policies Handler initialized")
    
    async def search_policies(self, query: str) -> Dict[str, Any]:
        """
        Search for government policies and schemes based on query.
        
        Args:
            query: Search query from farmer
            
        Returns:
            Matching policies and schemes
        """
        try:
            logger.info(f"Searching policies for query: {query}")
            
            # Normalize query
            normalized_query = query.lower().strip()
            
            # Find matching schemes
            matching_schemes = await self._find_matching_schemes(normalized_query)
            
            # Generate response
            response = await self._generate_policy_response(matching_schemes, query)
            
            return response
            
        except Exception as e:
            logger.error(f"Error searching policies: {e}", exc_info=True)
            return await self._get_fallback_response(query)
    
    async def _find_matching_schemes(self, query: str) -> List[Dict[str, Any]]:
        """Find schemes matching the query"""
        try:
            matching_schemes = []
            
            # Check each scheme for matches
            for scheme_id, scheme_data in self.schemes_database.items():
                score = await self._calculate_match_score(query, scheme_id, scheme_data)
                
                if score > 0.3:  # Threshold for relevance
                    scheme_info = {
                        "id": scheme_id,
                        "score": score,
                        **scheme_data
                    }
                    matching_schemes.append(scheme_info)
            
            # Sort by relevance score
            matching_schemes.sort(key=lambda x: x["score"], reverse=True)
            
            return matching_schemes[:5]  # Return top 5 matches
            
        except Exception as e:
            logger.error(f"Error finding matching schemes: {e}", exc_info=True)
            return []
    
    async def _calculate_match_score(self, query: str, scheme_id: str, scheme_data: Dict[str, Any]) -> float:
        """Calculate relevance score for a scheme"""
        try:
            score = 0.0
            
            # Check keyword matches
            if scheme_id in self.scheme_keywords:
                keywords = self.scheme_keywords[scheme_id]
                for keyword in keywords:
                    if keyword in query:
                        score += 0.4
                        break
            
            # Check name matches
            scheme_name = scheme_data.get("name", "").lower()
            if any(word in scheme_name for word in query.split()):
                score += 0.3
            
            # Check description matches
            description = scheme_data.get("description", "").lower()
            if any(word in description for word in query.split()):
                score += 0.2
            
            # Check eligibility matches
            eligibility = " ".join(scheme_data.get("eligibility", [])).lower()
            if any(word in eligibility for word in query.split()):
                score += 0.1
            
            return min(score, 1.0)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"Error calculating match score: {e}", exc_info=True)
            return 0.0
    
    async def _generate_policy_response(self, matching_schemes: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
        """Generate comprehensive policy response"""
        try:
            if not matching_schemes:
                return {
                    "query": query,
                    "schemes_found": 0,
                    "message": "No specific schemes found for your query. Please try different keywords or contact your local agriculture office.",
                    "general_info": await self._get_general_policy_info(query),
                    "contact_info": {
                        "agriculture_office": "Contact your nearest agriculture office",
                        "helpline": "Kisan Call Center: 1800-180-1551",
                        "website": "https://farmer.gov.in"
                    }
                }
            
            # Format schemes for response
            formatted_schemes = []
            for scheme in matching_schemes:
                formatted_scheme = {
                    "name": scheme["name"],
                    "description": scheme["description"],
                    "eligibility": scheme["eligibility"],
                    "benefits": scheme["benefits"],
                    "how_to_apply": scheme["how_to_apply"],
                    "documents_required": scheme["documents_required"],
                    "contact": scheme["contact"],
                    "website": scheme["website"],
                    "relevance_score": scheme["score"]
                }
                formatted_schemes.append(formatted_scheme)
            
            return {
                "query": query,
                "schemes_found": len(formatted_schemes),
                "schemes": formatted_schemes,
                "summary": await self._generate_scheme_summary(formatted_schemes),
                "next_steps": await self._generate_next_steps(formatted_schemes),
                "contact_info": {
                    "agriculture_office": "Contact your nearest agriculture office",
                    "helpline": "Kisan Call Center: 1800-180-1551",
                    "website": "https://farmer.gov.in"
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating policy response: {e}", exc_info=True)
            return await self._get_fallback_response(query)
    
    async def _generate_scheme_summary(self, schemes: List[Dict[str, Any]]) -> str:
        """Generate summary of found schemes"""
        try:
            if not schemes:
                return "No specific schemes found."
            
            summary_parts = []
            
            for scheme in schemes:
                name = scheme["name"]
                benefits = scheme["benefits"]
                if benefits:
                    main_benefit = benefits[0]
                    summary_parts.append(f"• {name}: {main_benefit}")
            
            return "Found schemes:\n" + "\n".join(summary_parts)
            
        except Exception as e:
            logger.error(f"Error generating scheme summary: {e}", exc_info=True)
            return "Multiple schemes found. Please check details above."
    
    async def _generate_next_steps(self, schemes: List[Dict[str, Any]]) -> List[str]:
        """Generate next steps for farmers"""
        try:
            next_steps = [
                "Review the eligibility criteria for each scheme",
                "Gather required documents (Aadhaar, land records, bank details)",
                "Visit your nearest agriculture office for detailed guidance",
                "Apply online if the scheme has online application facility",
                "Keep copies of all submitted documents",
                "Follow up on your application status"
            ]
            
            return next_steps
            
        except Exception as e:
            logger.error(f"Error generating next steps: {e}", exc_info=True)
            return ["Contact your local agriculture office for guidance."]
    
    async def _get_general_policy_info(self, query: str) -> str:
        """Get general policy information when no specific schemes match"""
        try:
            general_info = {
                "subsidy": "Various subsidies are available for irrigation, seeds, fertilizers, and equipment. Contact your agriculture office.",
                "loan": "Kisan Credit Card and other loan schemes are available. Visit your nearest bank branch.",
                "insurance": "Crop insurance schemes protect against natural calamities. Check with insurance companies.",
                "training": "Free training programs are available for modern farming techniques.",
                "market": "Government supports market access through various programs and infrastructure."
            }
            
            # Find relevant general info
            for keyword, info in general_info.items():
                if keyword in query.lower():
                    return info
            
            return "Government provides various support programs for farmers. Visit your nearest agriculture office for detailed information."
            
        except Exception as e:
            logger.error(f"Error getting general policy info: {e}", exc_info=True)
            return "Contact your local agriculture office for information about available schemes."
    
    async def _get_fallback_response(self, query: str) -> Dict[str, Any]:
        """Get fallback response when search fails"""
        try:
            return {
                "query": query,
                "schemes_found": 0,
                "message": "Unable to search schemes at the moment. Please try again later or contact your local agriculture office.",
                "general_info": "Government provides various agricultural schemes and subsidies. Visit your nearest agriculture office for information.",
                "contact_info": {
                    "agriculture_office": "Contact your nearest agriculture office",
                    "helpline": "Kisan Call Center: 1800-180-1551",
                    "website": "https://farmer.gov.in"
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating fallback response: {e}", exc_info=True)
            return {
                "query": query,
                "error": "Service temporarily unavailable",
                "contact_info": {
                    "helpline": "Kisan Call Center: 1800-180-1551"
                }
            }
    
    async def get_all_schemes(self) -> Dict[str, Any]:
        """Get all available schemes"""
        try:
            schemes_list = []
            
            for scheme_id, scheme_data in self.schemes_database.items():
                scheme_info = {
                    "id": scheme_id,
                    "name": scheme_data["name"],
                    "description": scheme_data["description"],
                    "benefits": scheme_data["benefits"][:2],  # First 2 benefits
                    "website": scheme_data["website"]
                }
                schemes_list.append(scheme_info)
            
            return {
                "total_schemes": len(schemes_list),
                "schemes": schemes_list
            }
            
        except Exception as e:
            logger.error(f"Error getting all schemes: {e}", exc_info=True)
            return {"error": "Unable to retrieve schemes"}
    
    async def get_scheme_details(self, scheme_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific scheme"""
        try:
            if scheme_id in self.schemes_database:
                return {
                    "found": True,
                    "scheme": self.schemes_database[scheme_id]
                }
            else:
                return {
                    "found": False,
                    "message": f"Scheme '{scheme_id}' not found"
                }
                
        except Exception as e:
            logger.error(f"Error getting scheme details: {e}", exc_info=True)
            return {"error": "Unable to retrieve scheme details"}
    
    async def test_connection(self) -> bool:
        """Test policy handler functionality"""
        try:
            # Test basic search functionality
            test_query = "crop insurance"
            result = await self.search_policies(test_query)
            
            if result and "schemes_found" in result:
                logger.info("Government Policies Handler test successful")
                return True
            else:
                logger.warning("Government Policies Handler test returned unexpected result")
                return False
                
        except Exception as e:
            logger.error(f"Government Policies Handler test failed: {e}", exc_info=True)
            return False 