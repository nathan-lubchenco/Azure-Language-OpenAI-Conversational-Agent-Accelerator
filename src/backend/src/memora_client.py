# HACKDAY: Memora integration client
import requests
import uuid
from datetime import datetime
from typing import Optional, Dict, List


class MemoraClient:
    """Client for interacting with Memora memory-api-server"""

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        account_id: str = "test-account",
        service_id: str = "test-service"
    ):
        self.base_url = base_url
        self.account_id = account_id
        self.service_id = service_id

    def recall(
        self,
        user_id: str,
        query: str,
        limit: int = 5,
        min_score: float = 0.0
    ) -> Dict:
        """
        Retrieve relevant memories for a query using the Recall endpoint.

        Args:
            user_id: User profile ID (e.g., "caroline", "melanie", "gina")
            query: Search query
            limit: Maximum number of memories to return
            min_score: Minimum relevance score threshold

        Returns:
            Dict with 'memories' and 'meta' keys
        """
        url = f"{self.base_url}/v1/Services/{self.service_id}/Profiles/{user_id}/Recall"

        try:
            response = requests.post(
                url,
                headers={
                    "X-Pre-Auth-Context": self.account_id,
                    "Content-Type": "application/json"
                },
                json={
                    "query": query,
                    "longtermLimit": limit,
                    "minScore": min_score
                },
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Memora recall failed: {e}")
            return {"memories": [], "meta": {}}

    def index_memory(
        self,
        user_id: str,
        text: str,
        conversation_id: str,
        metadata: Optional[Dict] = None
    ) -> Optional[Dict]:
        """
        Store a new memory in Memora.

        Args:
            user_id: User profile ID
            text: Memory content
            conversation_id: Conversation identifier
            metadata: Optional metadata dictionary

        Returns:
            Response dict or None if failed
        """
        url = f"{self.base_url}/v1/memories"

        memory = {
            "id": str(uuid.uuid4()),
            "text": text,
            "account_id": self.account_id,
            "service_id": self.service_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "source": "conversational-agent",
            "metadata": metadata or {}
        }

        try:
            response = requests.post(
                url,
                json=memory,
                timeout=5
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Memora indexing failed: {e}")
            return None

    def format_memories_for_context(
        self,
        memories_response: Dict,
        max_memories: int = 3
    ) -> str:
        """
        Format retrieved memories into a context string for the LLM.

        Args:
            memories_response: Response from recall()
            max_memories: Maximum number of memories to include

        Returns:
            Formatted string with memory context
        """
        memories = memories_response.get("memories", [])

        if not memories:
            return ""

        context_parts = ["=== Relevant memories from past conversations ==="]

        for mem in memories[:max_memories]:
            content = mem.get("content", "")
            score = mem.get("score", 0)
            occurred_at = mem.get("occurredAt", "")

            # Format the memory with score for transparency
            context_parts.append(
                f"- {content} (relevance: {score:.2f}, from: {occurred_at[:10]})"
            )

        context_parts.append("=" * 50)
        return "\n".join(context_parts)

    def get_memory_stats(self, user_id: str) -> Dict:
        """
        Get statistics about memories for a user.

        Args:
            user_id: User profile ID

        Returns:
            Dict with memory count and other stats
        """
        url = f"{self.base_url}/v1/memories"

        try:
            response = requests.get(
                url,
                params={
                    "account_id": self.account_id,
                    "service_id": self.service_id,
                    "user_id": user_id,
                    "limit": 1  # Just check if any exist
                },
                timeout=5
            )
            response.raise_for_status()
            data = response.json()

            return {
                "has_memories": len(data.get("memories", [])) > 0,
                "query_time_ms": data.get("meta", {}).get("queryTime", 0)
            }
        except requests.exceptions.RequestException as e:
            print(f"⚠️  Memora stats failed: {e}")
            return {"has_memories": False, "query_time_ms": 0}


# Test the client if run directly
if __name__ == "__main__":
    client = MemoraClient()

    print("Testing Memora client...")
    print("\n1. Testing recall for Caroline (LGBTQ advocacy):")
    result = client.recall("caroline", "Tell me about pride events", limit=2)
    print(f"   Found {len(result.get('memories', []))} memories")
    print(f"   Context: {client.format_memories_for_context(result, max_memories=2)}")

    print("\n2. Testing recall for Melanie (family):")
    result = client.recall("melanie", "Tell me about camping", limit=2)
    print(f"   Found {len(result.get('memories', []))} memories")

    print("\n3. Testing stats:")
    stats = client.get_memory_stats("caroline")
    print(f"   Stats: {stats}")

    print("\n✅ Memora client test complete!")
