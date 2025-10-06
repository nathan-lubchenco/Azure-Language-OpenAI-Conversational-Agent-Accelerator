# Memora Integration Plan

**Goal:** Integrate the conversational agent with locally-running Memora to add conversational memory and context retrieval.

## 📋 What is Memora?

Memora is Twilio's conversational memory management platform that:
- **Indexes** conversation memories with semantic search
- **Retrieves** contextually relevant memories using hybrid (lexical + semantic) search
- **Provides** the `/Recall` endpoint designed specifically for agentic workloads
- **Supports** OpenAI embeddings for vector-based retrieval

## 🎯 Integration Objectives

### Phase 1: Basic Memory Storage (Hackday Demo)
1. **Store conversation turns** in Memora after each interaction
2. **Retrieve relevant memories** before generating responses
3. **Show memory recall** in the UI/logs

### Phase 2: Advanced Features (Post-Hackday)
4. **User-specific memory isolation** using proper user IDs
5. **Metadata tagging** (topics, intents, entities extracted)
6. **Memory summarization** for long conversations
7. **Hybrid search tuning** (semantic vs lexical weight)

## 🏗️ Architecture

```
┌─────────────────┐
│   User Query    │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Conversational Agent (Our App)  │
│  ┌─────────────────────────────┐ │
│  │ 1. Recall from Memora       │ │ ─────┐
│  │    (retrieve context)        │ │      │
│  └─────────────────────────────┘ │      │
│  ┌─────────────────────────────┐ │      │
│  │ 2. Process with OpenAI      │ │      │
│  │    (utterance + memories)    │ │      │
│  └─────────────────────────────┘ │      │
│  ┌─────────────────────────────┐ │      │
│  │ 3. Index to Memora          │ │      │
│  │    (store interaction)       │ │ ─────┤
│  └─────────────────────────────┘ │      │
└──────────────────────────────────┘      │
                                           │
         ┌─────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│      Memora (Localhost)          │
│  ┌────────────────────────────┐  │
│  │   Memory API Server        │  │
│  │   REST: localhost:80       │  │
│  └────────────────────────────┘  │
│  ┌────────────────────────────┐  │
│  │   Memory Service (gRPC)    │  │
│  │   OpenSearch + Embeddings  │  │
│  └────────────────────────────┘  │
└──────────────────────────────────┘
```

## 🔌 API Integration Points

### 1. Recall Endpoint (Primary - For Retrieval)
```bash
POST http://localhost:8000/v1/Services/{service_id}/Profiles/{user_id}/Recall
Header: X-Pre-Auth-Context: {account_id}
Body: {
  "query": "user's current question",
  "longtermLimit": 5,
  "minScore": 0.1
}
```

**Returns:** Relevant memories with scores, optimized for agents

### 2. Index Endpoint (For Storage)
```bash
POST http://localhost:8000/v1/memories
Body: {
  "id": "unique-memory-id",
  "text": "conversation turn content",
  "account_id": "account_00000000000000000000000000",
  "service_id": "mem_service_00000000000000000000000000",
  "user_id": "mem_profile_user123",
  "conversation_id": "conv_session_abc",
  "metadata": {
    "intent": "order_status",
    "entities": "order_id:12345"
  }
}
```

## 📝 Implementation Steps

### Step 1: Create Memora Client Module
**File:** `src/backend/src/memora_client.py`

```python
import requests
import os
from datetime import datetime
import uuid

class MemoraClient:
    def __init__(
        self,
        base_url="http://localhost:8000",  # Direct to memory-api-server (bypasses Kong on :80)
        account_id="account_00000000000000000000000000",
        service_id="mem_service_00000000000000000000000000"
    ):
        self.base_url = base_url
        self.account_id = account_id
        self.service_id = service_id

    def recall(self, user_id, query, limit=5, min_score=0.1):
        """Retrieve relevant memories for a query"""
        url = f"{self.base_url}/v1/Services/{self.service_id}/Profiles/{user_id}/Recall"
        response = requests.post(
            url,
            headers={"X-Pre-Auth-Context": self.account_id},
            json={
                "query": query,
                "longtermLimit": limit,
                "minScore": min_score
            }
        )
        return response.json()

    def index_memory(self, user_id, text, conversation_id, metadata=None):
        """Store a new memory"""
        url = f"{self.base_url}/v1/memories"
        memory = {
            "id": str(uuid.uuid4()),
            "text": text,
            "account_id": self.account_id,
            "service_id": self.service_id,
            "user_id": user_id,
            "conversation_id": conversation_id,
            "metadata": metadata or {}
        }
        response = requests.post(url, json=memory)
        return response.json()
```

### Step 2: Integrate into Orchestrator
**Modify:** `src/backend/src/unified_app.py`

```python
from memora_client import MemoraClient

# Initialize Memora client
MEMORA_ENABLED = os.environ.get("MEMORA_ENABLED", "false").lower() == "true"
if MEMORA_ENABLED:
    memora_client = MemoraClient()
    print("✅ Memora integration enabled")

def orchestrate_chat(message: str, user_id: str = "demo_user") -> list[str]:
    # ... existing code ...

    # STEP 1: Recall relevant memories
    if MEMORA_ENABLED:
        try:
            memories = memora_client.recall(user_id=user_id, query=message, limit=3)
            context_from_memories = format_memories_for_context(memories)
            print(f"📚 Retrieved {len(memories.get('memories', []))} relevant memories")
        except Exception as e:
            print(f"⚠️  Memora recall failed: {e}")
            context_from_memories = ""
    else:
        context_from_memories = ""

    # STEP 2: Process with context
    # Modify the message sent to OpenAI to include memory context
    if context_from_memories:
        enriched_message = f"Context from past conversations:\n{context_from_memories}\n\nCurrent query: {message}"
    else:
        enriched_message = message

    # ... existing orchestration code using enriched_message ...

    # STEP 3: Store interaction in Memora
    if MEMORA_ENABLED:
        try:
            conversation_id = f"conv_{user_id}_{datetime.now().strftime('%Y%m%d')}"
            memory_text = f"User: {message}\nAssistant: {' '.join(responses)}"
            memora_client.index_memory(
                user_id=user_id,
                text=memory_text,
                conversation_id=conversation_id,
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "router_type": router_type.name
                }
            )
            print(f"💾 Stored interaction in Memora")
        except Exception as e:
            print(f"⚠️  Memora indexing failed: {e}")

    return responses
```

### Step 3: Helper Functions
```python
def format_memories_for_context(memories_response):
    """Format Memora memories into context string"""
    memories = memories_response.get('memories', [])
    if not memories:
        return ""

    context_parts = ["Previous relevant conversations:"]
    for mem in memories[:3]:  # Top 3 most relevant
        content = mem.get('content', '')
        score = mem.get('score', 0)
        context_parts.append(f"- {content} (relevance: {score:.2f})")

    return "\n".join(context_parts)
```

### Step 4: Update Environment Configuration
**Modify:** `src/backend/src/hackday_run.sh`

```bash
# Add Memora configuration
export MEMORA_ENABLED="${MEMORA_ENABLED:-true}"
export MEMORA_BASE_URL="${MEMORA_BASE_URL:-http://localhost:8000}"  # Direct to memory-api-server
export MEMORA_ACCOUNT_ID="${MEMORA_ACCOUNT_ID:-account_00000000000000000000000000}"
export MEMORA_SERVICE_ID="${MEMORA_SERVICE_ID:-mem_service_00000000000000000000000000}"
```

### Step 5: Update UI to Show Memories
**Modify:** `src/frontend/src/App.jsx`

Add a section to display retrieved memories (optional for demo).

## 🧪 Testing Plan

### 1. Verify Memora is Running
```bash
# Check health (port 8000 = direct to memory-api-server)
curl http://localhost:8000/health

# Test Recall endpoint
curl -X POST http://localhost:8000/v1/Services/mem_service_00000000000000000000000000/Profiles/demo_user/Recall \
  -H "X-Pre-Auth-Context: account_00000000000000000000000000" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "longtermLimit": 3, "minScore": 0}' | jq .
```

### 2. Test Memory Storage
```bash
# Start the agent app with Memora enabled
export MEMORA_ENABLED=true
./hackday_run.sh

# Send a test message
curl -X POST http://127.0.0.1:7000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I love pizza"}' | jq .

# Check if memory was stored in Memora
curl -G http://localhost:8000/v1/memories \
  --data-urlencode "account_id=account_00000000000000000000000000" \
  --data-urlencode "service_id=mem_service_00000000000000000000000000" \
  --data-urlencode "user_id=demo_user" \
  --data-urlencode "limit=10" | jq .
```

### 3. Test Memory Recall
```bash
# Send a related message
curl -X POST http://127.0.0.1:7000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What food do I like?"}' | jq .

# Should use recalled memory to answer "pizza"
```

## 📊 Demo Script

### For Tuesday's Show-and-Tell

**1. Start Memora (in separate terminal):**
```bash
cd /Users/nlubchenco/dev/src/github.com/github.com/twilio-internal/memora-domain
AWS_PROFILE=memora-dev make dev-start
```

**2. Start Agent with Memora:**
```bash
export MEMORA_ENABLED=true
./hackday_run.sh
```

**3. Demo Flow:**
```
User: "My favorite color is blue"
Agent: [responds] + stores in Memora

User: "I love hiking on weekends"
Agent: [responds] + stores in Memora

User: "What do you know about me?"
Agent: [recalls memories about color and hiking]
       "I remember you mentioned your favorite color is blue
        and that you love hiking on weekends!"
```

**4. Show the Logs:**
```bash
python view_logs.py

# Should show:
# - Memories retrieved before processing
# - Interaction stored after response
```

## 🎯 Success Metrics

- ✅ Conversations stored in Memora
- ✅ Relevant memories recalled on subsequent queries
- ✅ Agent responses incorporate past context
- ✅ Logs show memory operations
- ✅ Demo shows "agent remembers previous conversations"

## 🔮 Advanced Features (Post-Hackday)

### Multi-User Support
- Track different user_ids from frontend
- Isolate memories per user

### Intent-Based Memory Tagging
- Tag memories with CLU intents
- Filter recall by intent type

### Memory Summarization
- Periodically summarize long conversations
- Store summaries as separate memory types

### Hybrid Search Tuning
- Experiment with `semantic_weight` parameter
- Compare pure semantic vs hybrid results

## 📚 Resources

- **Memora Docs:** `/Users/nlubchenco/dev/src/github.com/github.com/twilio-internal/memora-domain/README.md`
- **API Examples:** `/Users/nlubchenco/dev/src/github.com/github.com/twilio-internal/memora-domain/QUICKSTART.md`
- **Hackday Context:** `context.md` (has Memora API details for hackday)
