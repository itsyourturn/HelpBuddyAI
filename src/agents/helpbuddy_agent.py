"""
HelpBuddy AI Agent - LangGraph-based chatbot for NCERT Science Class 8
"""

import logging
from typing import Dict, Any, Optional
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import Settings
from src.guardrails.content_filter import ContentFilter
from src.vectorstore.chroma_store import ChromaStore
from src.utils.image_processor import ImageProcessor
from src.utils.memory_manager import MemoryManager

logger = logging.getLogger(__name__)

class HelpBuddyAgent:
    """Simplified HelpBuddy AI agent for NCERT Science Class 8"""
    
    def __init__(self):
        """Initialize the agent"""
        self.settings = Settings()
        self.llm = ChatGoogleGenerativeAI(
            model=self.settings.GEMINI_MODEL,
            temperature=0.7,
            max_output_tokens=2048
        )
        
        self.content_filter = ContentFilter()
        self.vector_store = ChromaStore()
        self.image_processor = ImageProcessor()
        self.memory_manager = MemoryManager(max_history=10, max_age_hours=24)
        
        logger.info("HelpBuddy Agent initialized with memory management")
    
    def initialize_knowledge_base(self) -> bool:
        """Initialize the knowledge base from PDF"""
        try:
            return self.vector_store.index_pdf()
        except Exception as e:
            logger.error(f"Error initializing knowledge base: {str(e)}")
            return False
    
    def process_query(self, query: str, has_image: bool = False, image_data: Optional[str] = None) -> Dict[str, Any]:
        """Process a user query through the agent workflow"""
        try:
            logger.info(f"Processing query: '{query}' (has_image: {has_image})")
            
            # Initialize state
            state = {
                "query": query,
                "processed_query": query,
                "context": "",
                "response": "",
                "messages": [],
                "metadata": {
                    "has_image": has_image,
                    "context_retrieved": False,
                    "scope_checked": False
                }
            }
            
            # Step 1: Check if this is a conversation history question or follow-up question
            query_lower = query.lower()
            history_keywords = ["first", "last", "previous", "before", "how many", "what did", "what was", "all questions"]
            follow_up_keywords = ["it", "that", "this", "the", "those", "these", "above", "mentioned", "said", "explained", "discussed", "talked about", "also", "too", "as well", "in addition", "furthermore", "moreover"]
            
            is_history_question = any(keyword in query_lower for keyword in history_keywords)
            is_follow_up_question = any(keyword in query_lower for keyword in follow_up_keywords)
            
            # Priority 1: Handle history questions first
            if is_history_question:
                logger.info("Detected conversation history question")
                history_info = self.memory_manager.get_conversation_history_info(query)
                state["response"] = history_info
                return state
            
            # Priority 2: If there's an image, process it first (don't treat as follow-up)
            if has_image and image_data:
                logger.info("Image detected - processing image first, not treating as follow-up")
                # Skip follow-up detection for image queries
                pass
            else:
                # Priority 3: Check if it's a follow-up question (only for text queries)
                if is_follow_up_question or self._is_follow_up_question(query):
                    logger.info("Detected follow-up question")
                    # Get conversation context and generate contextual response
                    conversation_context = self.memory_manager.get_conversation_context(last_n=5)
                    related_context = self.memory_manager.get_related_context(query)
                    
                    if conversation_context and conversation_context != "No previous conversation histroy":
                        # Generate response using conversation context
                        state["response"] = self._generate_follow_up_response(query, conversation_context, related_context)
                        return state
            
            # Step 2: Process image if present (Step 1: Image to description generation)
            if has_image and image_data:
                logger.info("Step 1: Processing image to generate description...")
                logger.info(f"Original query: '{query}'")
                logger.info(f"Image data length: {len(image_data)} characters")
                
                image_description = self.image_processor.describe_image(image_data, query)
                if image_description:
                    # Combine original query with image description for better context
                    combined_query = f"{query} - Image shows: {image_description}"
                    state["processed_query"] = combined_query
                    logger.info(f"Image processed successfully. Combined query: '{combined_query[:100]}...'")
                    logger.info(f"Full image description: '{image_description}'")
                else:
                    # If image processing fails, use original query
                    state["processed_query"] = query
                    logger.warning("Image processing failed, using original query")
            else:
                # For text-only queries, use the original query
                state["processed_query"] = query
                logger.info(f"Text-only query: '{query}'")
            
            # Step 3: Check scope relevance using LLM (Step 2: Check scope through LLM)
            logger.info("Step 2: Checking scope relevance through LLM...")
            scope_check = self.content_filter.check_scope_relevance(state["processed_query"])
            state["metadata"]["scope_checked"] = True
            
            if not scope_check["is_relevant"]:
                logger.info(f"Query marked as out of scope: {scope_check.get('reason', 'Unknown')}")
                state["response"] = self.content_filter.generate_scope_response(query)
                return state
            
            logger.info("Query passed scope check, proceeding to context retrieval")
            
            # Step 4: Retrieve context from vector store (Step 3: Retrieve details from vector DB)
            logger.info("Step 3: Retrieving details from vector database...")
            state = self._retrieve_context(state)
            
            # Step 5: Generate response with conversation context (Step 4: Add previous questions & context to generate answer)
            logger.info("Step 4: Generating answer with previous conversation context...")
            state = self._generate_response(state, query, image_data)
            
            # Step 6: Add interaction to memory
            self.memory_manager.add_interaction(
                user_query=query,
                bot_response=state["response"],
                metadata=state["metadata"]
            )
            
            logger.info("Query processed successfully and added to memory")
            return state
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {
                "query": query,
                "processed_query": query,
                "context": "",
                "response": "I apologize, but I encountered an error while processing your question. Please try again.",
                "messages": [],
                "metadata": {
                    "has_image": has_image,
                    "error": str(e)
                }
            }
    
    def _retrieve_context(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Retrieve relevant context from vector store"""
        try:
            query = state["processed_query"]
            logger.info(f"Retrieving context for query: '{query}'")
            
            # Get context from vector store - no relevance filtering
            context = self.vector_store.get_relevant_context(query, max_chunks=5)
            
            state["context"] = context
            state["metadata"]["context_retrieved"] = True
            
            # Count the number of context chunks retrieved
            context_chunks = context.count("[Context")
            logger.info(f"Retrieved {context_chunks} document chunks from vector store")
            
            return state
            
        except Exception as e:
            logger.error(f"Error retrieving context: {str(e)}")
            state["context"] = "No information found in NCERT Science Class 8."
            state["metadata"]["context_retrieved"] = False
            return state
    
    def _generate_response(self, state: Dict[str, Any], query: str, image_data: Optional[str] = None) -> Dict[str, Any]:
        """Generate response using LLM with conversation context"""
        try:
            processed_query = state["processed_query"]
            context = state["context"]
            
            # Get conversation context from memory (previous questions & context)
            conversation_context = self.memory_manager.get_conversation_context(last_n=5)
            related_context = self.memory_manager.get_related_context(query)
            
            # Create prompt with context and conversation history
            if image_data:
                # For image queries, use original query and image description
                prompt = f"""You are HelpBuddy AI, a helpful assistant for NCERT Science Class 8 students.

Context from NCERT Science Class 8 textbook:
{context}

Previous conversation context (this will help provide better answers):
{conversation_context}

Related previous discussions:
{related_context}

Student's question about the image: {query}
Image description and analysis: {processed_query}

RESPONSE FORMAT REQUIREMENTS:
- Start your answer directly with the information about the image
- DO NOT include phrases like "Okay, I understand!", "Based on the textbook", or "Student's question:"
- DO NOT mention any context references like "[Context 1 - Page 5]" in your answer
- DO NOT cite sources or page numbers
- Provide a clear, direct, and educational answer suitable for Class 8 students
- Keep it simple and engaging
- If the previous conversation is related, build upon it naturally but don't reference it explicitly

Answer the question about the image directly:"""
            else:
                # For text queries
                prompt = f"""You are HelpBuddy AI, a helpful assistant for NCERT Science Class 8 students.

Context from NCERT Science Class 8 textbook:
{context}

Previous conversation context (this will help provide better answers):
{conversation_context}

Related previous discussions:
{related_context}

Student's question: {query}

RESPONSE FORMAT REQUIREMENTS:
- Start your answer directly with the information requested
- DO NOT include phrases like "Okay, I understand!", "Based on the textbook", or "Student's question:"
- DO NOT mention any context references like "[Context 1 - Page 5]" in your answer
- DO NOT cite sources or page numbers
- Provide a clear, direct, and educational answer suitable for Class 8 students
- Keep it simple and engaging
- If the previous conversation is related, build upon it naturally but don't reference it explicitly

Answer the question directly:"""

            # Generate response
            response = self.llm.invoke(prompt)
            state["response"] = response.content
            
            # Add to conversation history
            state["messages"].append(AIMessage(content=state["response"]))
            
            return state
            
        except Exception as e:
            state["response"] = "I apologize, but I encountered an error while processing your question. Please try again."
            state["messages"].append(AIMessage(content=state["response"]))
            return state
    
    def clear_conversation_memory(self):
        """Clear the conversation memory"""
        try:
            self.memory_manager.clear_memory()
            logger.info("Conversation memory cleared")
        except Exception as e:
            logger.error(f"Error clearing conversation memory: {str(e)}")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of the conversation"""
        try:
            return self.memory_manager.get_conversation_summary()
        except Exception as e:
            logger.error(f"Error getting conversation summary: {str(e)}")
            return {"error": str(e)}
    
    def get_conversation_history_info(self, query: str) -> str:
        """Get specific information about conversation history"""
        try:
            return self.memory_manager.get_conversation_history_info(query)
        except Exception as e:
            logger.error(f"Error getting conversation history info: {str(e)}")
            return "Error retrieving conversation history information."
    
    def sync_conversation_history(self, conversation_history: list) -> bool:
        """Sync conversation history from external source to memory manager"""
        try:
            if not conversation_history:
                return True
            
            # Clear existing conversations if any
            if self.memory_manager.conversations:
                self.memory_manager.clear_memory()
            
            # Convert conversation history to memory manager format
            for i in range(0, len(conversation_history), 2):
                if i + 1 < len(conversation_history):
                    user_msg = conversation_history[i]
                    assistant_msg = conversation_history[i + 1]
                    
                    if user_msg.get("role") == "user" and assistant_msg.get("role") == "assistant":
                        self.memory_manager.add_interaction(
                            user_query=user_msg.get("content", ""),
                            bot_response=assistant_msg.get("content", ""),
                            metadata={"timestamp": user_msg.get("timestamp", "")}
                        )
            
            logger.info(f"Synced {len(conversation_history) // 2} conversation pairs to memory manager")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing conversation history: {str(e)}")
            return False
    
    def _is_follow_up_question(self, query: str) -> bool:
        """Check if a query is a follow-up question based on context and structure"""
        try:
            query_lower = query.lower()
            
            # Check for pronouns that indicate reference to previous context
            pronouns = ["it", "that", "this", "the", "those", "these", "they", "them", "their"]
            has_pronouns = any(pronoun in query_lower for pronoun in pronouns)
            
            # Check for context words
            context_words = ["above", "mentioned", "said", "explained", "discussed", "talked about", "earlier", "before"]
            has_context_words = any(word in query_lower for word in context_words)
            
            # Check for short questions that likely refer to previous context
            is_short_question = len(query.split()) <= 5
            
            # Check for questions that start with context indicators
            starts_with_context = any(query_lower.startswith(word) for word in ["what about", "how about", "and", "but", "so", "then"])
            
            # Check if there's conversation history to refer to
            has_history = len(self.memory_manager.conversations) > 0
            
            # Determine if it's a follow-up question
            is_follow_up = (has_pronouns or has_context_words or is_short_question or starts_with_context) and has_history
            
            logger.info(f"Follow-up detection: pronouns={has_pronouns}, context={has_context_words}, short={is_short_question}, starts_with_context={starts_with_context}, has_history={has_history}, is_follow_up={is_follow_up}")
            
            return is_follow_up
            
        except Exception as e:
            logger.error(f"Error detecting follow-up question: {str(e)}")
            return False
    
    def _generate_follow_up_response(self, query: str, conversation_context: str, related_context: str) -> str:
        """Generate a response for follow-up questions using conversation context"""
        try:
            # Create a prompt for follow-up questions
            prompt = f"""You are HelpBuddy AI, a helpful assistant for NCERT Science Class 8 students.

Previous conversation context:
{conversation_context}

{related_context}

Student's follow-up question: {query}

RESPONSE FORMAT REQUIREMENTS:
- Start your answer directly with the information requested
- DO NOT include phrases like "Okay, I understand!", "Based on the textbook", or "Student's question:"
- DO NOT mention any context references like "[Context 1 - Page 5]" in your answer
- DO NOT cite sources or page numbers
- Provide a clear, direct, and educational answer suitable for Class 8 students
- Keep it simple and engaging
- This is a follow-up question, so build upon our previous conversation naturally

Answer the follow-up question directly:"""

            # Generate response
            response = self.llm.invoke(prompt)
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating follow-up response: {str(e)}")
            return "I'm having trouble understanding your follow-up question. Could you please rephrase it or provide more context?"
