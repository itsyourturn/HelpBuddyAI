import re
import logging
from typing import Dict, Any, List
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import Settings

logger = logging.getLogger(__name__)

class ContentFilter:
    """Content filtering and guardrails for user queries"""
    
    def __init__(self):
        self.settings = Settings()
        self.llm = ChatGoogleGenerativeAI(
            model=self.settings.GEMINI_MODEL,
            temperature=0.1,
            max_output_tokens=100
        )
        
        # Toxic patterns for age-appropriateness and vulgarity
        self.toxic_patterns = [
            r'\b(kill\s+yourself|suicide|self\s*harm)\b',
            r'\b(fuck|shit|bitch|asshole|dick|pussy)\b',
            r'\b(nazi|hitler|white\s+supremacy)\b',
            r'\b(drugs?|cocaine|heroin|meth)\b',
            r'\b(porn|pornography|sex\s+video)\b',
            r'\b(hate\s+speech|racist|sexist)\b'
        ]
        
    def check_content_safety(self, content: str) -> Dict[str, Any]:
        """
        Check if content is safe and appropriate
        
        Args:
            content: Content to check
            
        Returns:
            Dict with safety information
        """
        try:
            content_lower = content.lower()
            
            # Check for toxic patterns
            for pattern in self.toxic_patterns:
                if re.search(pattern, content_lower):
                    return {
                        "is_safe": False,
                        "reason": f"Content contains inappropriate language or topics",
                        "confidence": 0.9
                    }
            
            # Default to safe
            return {
                "is_safe": True,
                "reason": "Content is appropriate",
                "confidence": 0.8
            }
            
        except Exception as e:
            logger.error(f"Error checking content safety: {str(e)}")
            # Default to safe on error
            return {
                "is_safe": True,
                "reason": "Error checking safety, defaulting to safe",
                "confidence": 0.5
            }
    
    def check_scope_relevance(self, query: str) -> Dict[str, Any]:
        """Check if query is relevant to NCERT Science Class 8 scope using LLM"""
        try:
            # First check for NCERT keywords
            query_lower = query.lower()
            for keyword in self.settings.SCOPE_KEYWORDS:
                if keyword.lower() in query_lower:
                    logger.info(f"Query matched NCERT keyword: '{keyword}'")
                    return {"is_relevant": True, "reason": f"Contains NCERT keyword: {keyword}"}
            
            logger.info("No keyword match found, using LLM for scope check")
            
            # If no keywords found, use LLM to check
            prompt = f"""You are a helpful assistant checking if a student's question is relevant to NCERT Science Class 8 curriculum.

IMPORTANT: Be very permissive. If the question could be related to any science topic, mark it as relevant.

Student's question: "{query}"

Is this question relevant to NCERT Science Class 8 Science curriculum? 
Consider topics like: physics, chemistry, biology, force, pressure, friction, sound, light, electricity, magnets, cells, reproduction, adolescence, crops, microorganisms, fibers, plastics, metals, coal, petroleum, combustion, conservation, pollution, solar system, stars, natural phenomena, agriculture, plants, soil, etc.

Respond with ONLY "YES" or "NO"."""

            response = self.llm.invoke(prompt)
            llm_response = response.content.strip().upper()
            
            # Default to relevant if LLM response is unclear
            if not llm_response or llm_response not in ["YES", "NO"]:
                logger.warning(f"LLM returned unclear response: '{llm_response}', defaulting to relevant")
                return {"is_relevant": True, "reason": "LLM response unclear, defaulting to relevant"}
            
            is_relevant = llm_response == "YES"
            logger.info(f"LLM scope check result: {llm_response} (relevant: {is_relevant})")
            return {"is_relevant": is_relevant, "reason": f"LLM determined: {llm_response}"}
            
        except Exception as e:
            logger.error(f"Error checking scope relevance: {str(e)}")
            return {"is_relevant": True, "reason": "Error occurred, defaulting to relevant"}
    
    def generate_scope_response(self, query: str) -> str:
        """
        Generate a helpful response when query is out of scope
        
        Args:
            query: User query
            
        Returns:
            Helpful response with NCERT topics
        """
        return f"I'm sorry, but '{query}' is outside the scope of NCERT Science Class 8. I can help you with topics like crop production, microorganisms, materials, force, pressure, sound, light, and environmental science. Please ask me about any NCERT Science Class 8 topics!"
