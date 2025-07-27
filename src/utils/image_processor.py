import base64
import logging
from typing import Optional
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import Settings

logger = logging.getLogger(__name__)

class ImageProcessor:
    """Simple image processor for HelpBuddy AI"""
    
    def __init__(self):
        """Initialize image processor"""
        self.settings = Settings()
        self.llm = ChatGoogleGenerativeAI(
            model=self.settings.GEMINI_MODEL,
            temperature=0.3,
            max_output_tokens=500
        )
    
    def describe_image(self, image_data: Optional[str], user_query: str = "") -> Optional[str]:
        """
        Get a description of the image based on user query
        
        Args:
            image_data: Base64 encoded image data
            user_query: User's question about the image
            
        Returns:
            Description of the image or None if error
        """
        try:
            logger.info(f"Processing image with query: '{user_query}'")
            logger.info(f"Image data length: {len(image_data) if image_data else 0} characters")
            
            # Validate image data
            if not image_data:
                logger.error("Image data is empty")
                return None
                
            if len(image_data) < 100:  # Too small to be a valid image
                logger.error(f"Image data too small: {len(image_data)} characters")
                return None
                
            # Check if it looks like base64
            try:
                import base64
                # Try to decode a small portion to validate base64
                test_decode = base64.b64decode(image_data[:100] + "==")
                logger.info("Base64 validation passed")
            except Exception as e:
                logger.error(f"Image data is not valid base64: {str(e)}")
                return None
            
            # Create a message with the image and user query
            if user_query:
                prompt = f"""Analyze this image and describe what you see that's relevant to the user's question: "{user_query}"

Focus on describing the scientific content, diagrams, experiments, or educational elements that would help answer the question.
Provide a detailed description of the image content that relates to NCERT Science Class 8 curriculum."""
            else:
                prompt = "Please describe this image in detail, focusing on any scientific or educational content that might be relevant to NCERT Science Class 8 curriculum."
            
            message = HumanMessage(
                content=[
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_data}"
                        }
                    }
                ]
            )
            
            # Get description from LLM
            logger.info("Invoking LLM for image description...")
            try:
                response = self.llm.invoke([message])
                description = response.content.strip()
                
                if description:
                    logger.info(f"Image description generated successfully ({len(description)} characters)")
                    logger.info(f"Description preview: '{description[:100]}...'")
                else:
                    logger.warning("Generated image description is empty")
                
                return description
            except Exception as e:
                logger.error(f"Error invoking LLM for image description: {str(e)}")
                return None
            
        except Exception as e:
            logger.error(f"Error processing image: {str(e)}")
            return None
        