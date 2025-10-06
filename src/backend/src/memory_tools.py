"""
Memory tools for LifePath AI - Personal Growth Companion

These tools allow the AI agent to search and store memories about the user's
life experiences, relationships, goals, and personal growth journey.
"""

from typing import Dict, Any
from memora_client import MemoraClient


def create_memory_tools(memora_client: MemoraClient, user_id: str):
    """
    Create memory tools for the agent.

    Args:
        memora_client: Configured Memora client
        user_id: Current user's ID

    Returns:
        List of tool definitions in OpenAI format and their implementations
    """

    def search_memories(query: str, limit: int = 5) -> Dict[str, Any]:
        """
        Search through the user's life memories to find relevant past experiences,
        conversations, and stored information.

        CRITICAL: Use this tool whenever you need context about the user to answer their question.

        ALWAYS use this when the user asks:
        - Questions about THEMSELVES ("What should I do next?", "What are my goals?")
        - About their past experiences or conversations
        - Questions using their name ("What should John do next?")
        - For advice that requires knowing their background
        - About their relationships, work, interests, achievements
        - Any "What have I...", "Who am I...", "How do I..." questions
        - Questions where you need personal context to give a good answer

        Args:
            query: What to search for in the user's memories. Be broad to capture relevant context.
                   Examples: "goals aspirations", "career interests", "relationships family",
                   "achievements projects", "challenges struggles", "values beliefs"
            limit: Maximum number of memories to retrieve (default: 5, use more for life questions)

        Returns:
            Dictionary with memories array and metadata
        """
        try:
            result = memora_client.recall(
                user_id=user_id,
                query=query,
                limit=limit,
                min_score=0.3  # Lower threshold to get more results
            )
            return {
                "success": True,
                "memories": result.get("memories", []),
                "count": len(result.get("memories", [])),
                "query": query
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

    def store_memory(content: str, tags: str = "") -> Dict[str, Any]:
        """
        Store important information from the current conversation into the user's
        long-term memory.

        Use this tool when the user:
        - Shares significant life events or experiences
        - Mentions important people in their life
        - Discusses goals or aspirations
        - Reveals preferences or values
        - Describes completed projects or achievements
        - Updates you on ongoing situations

        Args:
            content: The information to remember (be specific and include context)
            tags: Optional comma-separated tags for categorization (e.g., "family,milestone"
                  or "advocacy,pride" or "business,creative")

        Returns:
            Confirmation of storage with memory ID
        """
        try:
            from datetime import datetime

            conversation_id = f"conv_{user_id}_{datetime.now().strftime('%Y%m%d')}"
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "source": "lifepath_ai",
            }

            if tags:
                metadata["tags"] = tags

            result = memora_client.index_memory(
                user_id=user_id,
                text=content,
                conversation_id=conversation_id,
                metadata=metadata
            )

            return {
                "success": True,
                "message": "Memory stored successfully",
                "memory_id": result.get("id") if result else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    # Tool definitions in OpenAI format
    tools = [
        {
            "type": "function",
            "function": {
                "name": "search_memories",
                "description": "Search the user's life memories for relevant context. CRITICAL: Use this whenever you need to know about the user's background, goals, experiences, relationships, or life situation to answer their question. Examples: 'What should I do next?' → search for 'goals aspirations career interests'. 'Tell me about my achievements' → search for 'achievements projects successes'.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Broad search query to find relevant memories. Use terms like: 'goals aspirations', 'career work interests', 'relationships family friends', 'achievements projects', 'challenges struggles', 'values beliefs', 'hobbies interests'"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of memories to retrieve. Use 5-10 for life direction questions.",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "store_memory",
                "description": store_memory.__doc__.strip(),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "The information to remember"
                        },
                        "tags": {
                            "type": "string",
                            "description": "Optional comma-separated tags",
                            "default": ""
                        }
                    },
                    "required": ["content"]
                }
            }
        }
    ]

    # Tool implementations lookup
    implementations = {
        "search_memories": search_memories,
        "store_memory": store_memory
    }

    return tools, implementations
