import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class MemoryManager:
    """Memory management for conversation history and context"""

    def __init__(self, max_history: int = 10, max_age_hours: int = 24):
        """
        Initialize memory manager

        Args:
            max_history: Maximum number of interactions to keep
            max_age_hours: Maximum age of interactions in hours
        """
        self.max_history = max_history
        self.max_age_hours = max_age_hours
        self.conversations: List[Dict[str, Any]] = []
        self.user_context: Dict[str, Any] = {}

    def add_interaction(
            self,
            user_query: str,
            bot_response: str,
            metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Add a new interaction to memory

        Args:
            user_query: User's question
            bot_response: Bot's response
            metadata: Additional metadata
        """
        try:
            interaction = {
                "timestamp": datetime.now(),
                "user_query": user_query,
                "bot_response": bot_response,
                "metadata": metadata or {}
            }

            self.conversations.append(interaction)

            # Clean up old interactions
            self._cleanup_old_interactions()

            # Limit history size
            if len(self.conversations) > self.max_history:
                self.conversations = self.conversations[-self.max_history:]
            
            logger.info(f"Added interaction to memory. Total: {len(self.conversations)}")

        except Exception as e:
            logger.error(f"Error adding interaction to memory: {str(e)}")
    
    def get_conversation_context(self, last_n: int = 5) -> str:
        """
        Get recent conversation context

        Args:
            last_n: Number of recent interactions to include

        Returns:
            Formatted conversation context
        """
        try:
            if not self.conversations:
                return "No previous conversation histroy"
            
            # Get recent interactions
            recent_conversations = self.conversations[-last_n:]

            context_parts = ["Previous conversation context:"]

            for i, conv in enumerate(recent_conversations, 1):
                context_parts.append(
                    f"\n{i}. User: {conv['user_query']}"
                )
                context_parts.append(
                    f"  Assistant: {conv['bot_response'][:200]}..."
                    if len(conv['bot_response']) > 200
                    else f" Assistant: {conv['bot_response']}"
                )

            return "\n".join(context_parts)
        
        except Exception as e:
            logger.error(f"Error getting conversation context: {str(e)}")
            return "Error retreiving conversation context."
        
    def get_related_context(self, current_query: str) -> str:
        """
        Get context related to current query

        Args:
            current_query: current user query

        Returns:
            Related conversation context
        """
        try:
            if not self.conversations:
                return ""
            
            query_lower = current_query.lower()
            related_interactions = []

            # FInd related interactions based on keyword overlap
            for conv in self.conversations:
                prev_query = conv['user_query'].lower()
                prev_response = conv['bot_response'].lower()

                # Simple keyword matching
                query_words = set(query_lower.split())
                prev_words = set(prev_query.split())
                response_words = set(prev_response.split())

                # Calculate overlap
                query_overlap = len(query_words & prev_words) / max(len(query_words), 1)
                response_overlap = len(query_words & response_words) / max(len(query_words), 1)

                if query_overlap > 0.3 or response_overlap > 0.2:
                    related_interactions.append({
                        "interaction": conv,
                        "relevance": max(query_overlap, response_overlap)
                    })
            
            if not related_interactions:
                return ""
            
            # Sort by relevance
            related_interactions.sort(
                key=lambda x: x["relevance"],
                reverse=True
            )

            # Format related context
            context_parts = ["Related previous discussions:"]

            for item in related_interactions[:3]:
                conv = item["interaction"]
                context_parts.append(
                    f"\n- Previously asked: {conv['user_query']}"
                )
                context_parts.append(
                    f"  Response: {conv['bot_response'][:150]}..."
                    if len(conv['bot_response']) > 150
                    else f" Response: {conv['bot_response']}"
                )

            return "\n".join(context_parts)
        
        except Exception as e:
            logger.error(f"Error getting related context: {str(e)}")
            return ""
    
    def get_conversation_history_info(self, query: str) -> str:
        """
        Get specific information about conversation history based on query
        
        Args:
            query: User query asking about conversation history
            
        Returns:
            Formatted conversation history information
        """
        try:
            if not self.conversations:
                return "No conversation history available."
            
            query_lower = query.lower()
            
            # Handle specific questions about conversation history
            if any(word in query_lower for word in ["first", "1st", "initial", "start"]):
                if "question" in query_lower or "ask" in query_lower:
                    first_conv = self.conversations[0]
                    return f"Your first question was: '{first_conv['user_query']}'"
                elif "response" in query_lower or "answer" in query_lower:
                    first_conv = self.conversations[0]
                    return f"My first response was: '{first_conv['bot_response'][:200]}...'"
            
            elif any(word in query_lower for word in ["last", "recent", "previous", "before"]):
                if "question" in query_lower or "ask" in query_lower:
                    last_conv = self.conversations[-1]
                    return f"Your last question was: '{last_conv['user_query']}'"
                elif "response" in query_lower or "answer" in query_lower:
                    last_conv = self.conversations[-1]
                    return f"My last response was: '{last_conv['bot_response'][:200]}...'"
            
            elif "how many" in query_lower and ("question" in query_lower or "ask" in query_lower):
                return f"You have asked {len(self.conversations)} questions so far."
            
            elif "what" in query_lower and "discuss" in query_lower:
                # Get all unique topics discussed
                all_queries = " ".join([conv['user_query'] for conv in self.conversations])
                topics = []
                science_topics = [
                    "photosynthesis", "cell", "force", "motion", "light", "sound", 
                    "electricity", "magnet", "chemical", "reaction", "acid", "base", 
                    "animal", "plant", "reproduction", "food", "nutrition", 
                    "respiration", "excretion", "weeds", "crop", "fertilizer"
                ]
                for topic in science_topics:
                    if topic in all_queries.lower():
                        topics.append(topic)
                
                if topics:
                    return f"We have discussed: {', '.join(topics)}"
                else:
                    return "We haven't discussed any specific science topics yet."
            
            elif "all" in query_lower and ("question" in query_lower or "ask" in query_lower):
                # List all questions
                questions = []
                for i, conv in enumerate(self.conversations, 1):
                    questions.append(f"{i}. {conv['user_query']}")
                return "All your questions:\n" + "\n".join(questions)
            
            # Default: return recent conversation context
            return self.get_conversation_context(last_n=3)
        
        except Exception as e:
            logger.error(f"Error getting conversation history info: {str(e)}")
            return "Error retrieving conversation history information."
        
    def update_user_context(self, key: str, value: Any):
        """
        Update user context information

        Args:
            key: Context key
            value: Context value
        """
        try:
            self.user_context[key] = {
                "value": value,
                "timestamp": datetime.now()
            }

            logger.info(f"Updated user context: {key}")
        
        except Exception as e:
            logger.error(f"Error updating user context: {str(e)}")

    def get_user_context(self, key: str) -> Any:
        """
        Get user context value

        Args:
            key: Context key

        Returns:
            Context value or None
        """
        try:
            context_item = self.user_context.get(key)
            if context_item:
                return context_item["value"]
            return None
        
        except Exception as e:
            logger.error(f"Error getting user context: {str(e)}")
            return None
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """
        Get summary of conversation

        Returns:
            Dictionary with conversation statistics
        """
        try:
            if not self.conversations:
                return {
                    "total_interactions": 0,
                    "topics_discussed": [],
                    "common_themes": []
                }
            
            # Extract topics (simple keyword extraction)
            all_queries = " ".join([
                conv["user_query"] for conv in self.conversations
            ])

            # Common science topics
            science__topics = [
                "photosynthesis", "cell", "force", "motion", "light",
                "sound", "electricity", "magnet", "chemical", "reaction",
                "acid", "base", "animal", "plant", "reproduction",
                "food", "nutrition", "respiration", "excretion"
            ]

            topics_discussed = [
                topic for topic in science__topics
                if topic in all_queries.lower()
            ]

            return {
                "total_interactions": len(self.conversations),
                "topics_discussed": topics_discussed,
                "first_query": self.conversations[0]["user_query"][:50] + "...",
                "last_query": self.conversations[-1]["user_query"][:50] + "..."
            }
        
        except Exception as e:
            logger.error(f"Error getting conversation summary: {str(e)}")
            return {"error": str(e)}
        
    def _cleanup_old_interactions(self):
        """Remove interactions older than max_age_hours"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)

            # Filter out old interactions
            self.conversations = [
                conv for conv in self.conversations
                if conv["timestamp"] > cutoff_time
            ]

        except Exception as e:
            logger.error(f"Error cleaning up old interactions: {str(e)}")

    def clear_memory(self):
        """Clear all memory"""
        try:
            self.conversations.clear()
            self.user_context.clear()
            logger.info("Memory Cleared")

        except Exception as e:
            logger.error(f"Error clearing memory: {str(e)}")

    def get_memory_info(self) -> Dict[str, Any]:
        """
        Get information about current memory state

        Returns:
            Dictionary with memory information
        """
        try:
            total_size = len(self.conversations) + len(self.user_context)

            # Calculate memory usage (approximate)
            memory_usage = 0
            for conv in self.conversations:
                memory_usage += len(str(conv))
            
            for key, value in self.user_context.items():
                memory_usage += len(str(key)) + len(str(value))

            return {
                "size": total_size,
                "conversations": len(self.conversations),
                "user_context_items": len(self.user_context),
                "memory_usage_bytes":memory_usage,
                "memory_usage_kb": round(memory_usage / 1024, 2),
                "max_history": self.max_history,
                "max_age_hours": self.max_age_hours
            }
        
        except Exception as e:
            logger.error(f"Error getting memory info: {str(e)}")
            return {"error": str(e)}
        
    def export_conversation(self) -> List[Dict[str, Any]]:
        """
        Export conversation history

        Returns:
            List of conversation interactions
        """
        try:
            exported_conversations = []

            for conv in self.conversations:
                exported_conversations.append({
                    "timestamp": conv["timestamp"].isoformat(),
                    "user_query": conv["user_query"],
                    "bot_response": conv["bot_response"],
                    "metadata": conv.get("metadata", {})
                })

            return exported_conversations
        
        except Exception as e:
            logger.error(f"Error exporting conversations: {str(e)}")
            return []
