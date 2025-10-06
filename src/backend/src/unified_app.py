# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# HACKDAY: Added data logging and Memora integration
import os
import json
import importlib
import pii_redacter
from json import JSONDecodeError
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from azure.search.documents import SearchClient
from aoai_client import AOAIClient, get_prompt
from router.router_type import RouterType
from unified_conversation_orchestrator import UnifiedConversationOrchestrator
from utils import get_azure_credential
from data_logger import log_utterance_extraction, log_orchestration, log_chat_completion, log_error, get_log_stats
from memora_client import MemoraClient


DIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "dist"))
# log dist_dir
print(f"DIST_DIR: {DIST_DIR}")


# FastAPI app:
app = FastAPI()
app.mount("/assets", StaticFiles(directory=os.path.join(DIST_DIR, "assets")), name="assets")


# HACKDAY: Use mock search client
from hackday_mocks import MockSearchClient
search_client = MockSearchClient(
    endpoint=os.environ.get("SEARCH_ENDPOINT", "dummy"),
    index_name=os.environ.get("SEARCH_INDEX_NAME", "dummy"),
    credential=None
)

# RAG AOAI client (now using OpenAI):
rag_client = AOAIClient(
    endpoint=os.environ.get("AOAI_ENDPOINT", "dummy"),  # Ignored for OpenAI
    deployment=os.environ.get("AOAI_DEPLOYMENT", "gpt-4o-mini"),
    use_rag=False,  # HACKDAY: Disable RAG since we don't have Azure Search
    search_client=search_client
)


# Extract-utterances AOAI client (now using OpenAI):
extract_prompt = get_prompt("extract_utterances.txt")
extract_client = AOAIClient(
    endpoint=os.environ.get("AOAI_ENDPOINT", "dummy"),  # Ignored for OpenAI
    deployment=os.environ.get("AOAI_DEPLOYMENT", "gpt-4o-mini"),
    system_message=extract_prompt
)


# PII:
PII_ENABLED = os.environ.get("PII_ENABLED", "false").lower() == "true"


# Fallback function (RAG):
def fallback_function(
    query: str,
    language: str,
    id: int
) -> str:
    """
    Call RAG client for grounded chat completion.
    """
    if PII_ENABLED:
        # Redact PII:
        query = pii_redacter.redact(
            text=query,
            id=id,
            language=language,
            cache=True
        )

    return rag_client.chat_completion(query)


# Unified-Conversation-Orchestrator:
router_type = RouterType(os.environ.get("ROUTER_TYPE", "BYPASS"))
orchestrator = UnifiedConversationOrchestrator(
    router_type=router_type,
    fallback_function=fallback_function
)

# HACKDAY: Memora integration
MEMORA_ENABLED = os.environ.get("MEMORA_ENABLED", "false").lower() == "true"
MEMORA_USER_ID = os.environ.get("MEMORA_USER_ID", "caroline")  # Default to caroline

if MEMORA_ENABLED:
    memora_client = MemoraClient(
        base_url=os.environ.get("MEMORA_BASE_URL", "http://localhost:8000"),
        account_id=os.environ.get("MEMORA_ACCOUNT_ID", "test-account"),
        service_id=os.environ.get("MEMORA_SERVICE_ID", "test-service")
    )
    print(f"✅ Memora integration enabled for user: {MEMORA_USER_ID}")
else:
    memora_client = None
    print("⚠️  Memora integration disabled")

chat_id = 0


def orchestrate_chat(message: str) -> list[str]:
    print(f"\n{'='*80}")
    print(f"🔵 NEW REQUEST: {message}")
    print(f"{'='*80}")

    # HACKDAY: Step 1 - Recall relevant memories from Memora
    memory_context = ""
    if MEMORA_ENABLED and memora_client:
        try:
            print(f"📚 Recalling memories for user: {MEMORA_USER_ID}")
            memories_response = memora_client.recall(
                user_id=MEMORA_USER_ID,
                query=message,
                limit=3,
                min_score=0.5
            )
            memory_count = len(memories_response.get("memories", []))
            print(f"   Found {memory_count} relevant memories")

            if memory_count > 0:
                memory_context = memora_client.format_memories_for_context(
                    memories_response,
                    max_memories=3
                )
                print(f"   Memory context added to query")
        except Exception as e:
            print(f"⚠️  Memory recall failed: {e}")

    try:
        if PII_ENABLED:
            # Redact PII:
            message = pii_redacter.redact(
                text=message,
                id=chat_id,
                cache=True
            )

        # Break user message into separate utterances:
        print(f"⚙️  Extracting utterances...")
        utterances = extract_client.chat_completion(message)
        print(f"✅ Utterances: {utterances}")
    except Exception as e:
        print(f"❌ ERROR in utterance extraction: {e}")
        import traceback
        traceback.print_exc()
        return [f"Error extracting utterances: {str(e)}"]
    if not isinstance(utterances, list):
        try:
            utterances = json.loads(utterances)
        except JSONDecodeError:
            # Harmful content case:
            if PII_ENABLED:
                # Clean up PII memory:
                pii_redacter.remove(id=chat_id)
            log_error("harmful_content", "Unable to parse utterances", {"message": message})
            return ['I am unable to respond or participate in this conversation.']

    # HACKDAY: Safety check - if no utterances extracted, use original message
    if not utterances or len(utterances) == 0:
        print(f"⚠️  WARNING: No utterances extracted! Using original message as fallback.")
        utterances = [message]

    # HACKDAY: Log utterance extraction
    try:
        log_utterance_extraction(
            original_message=message,
            extracted_utterances=utterances,
            model=os.environ.get("AOAI_DEPLOYMENT", "gpt-4o-mini")
        )
    except Exception as e:
        print(f"Warning: Failed to log utterance extraction: {e}")

    # Process each utterance:
    responses = []
    for i, query in enumerate(utterances, 1):
        print(f"\n⚙️  Processing utterance {i}/{len(utterances)}: {query}")

        # HACKDAY: Add memory context to first utterance
        if i == 1 and memory_context:
            enriched_query = f"{memory_context}\n\nCurrent query: {query}"
            print(f"   ✨ Enriched with memory context")
        else:
            enriched_query = query

        try:
            if PII_ENABLED:
                # Reconstruct PII:
                query = pii_redacter.reconstruct(
                    text=query,
                    id=chat_id,
                    cache=True
                )

            # Orchestrate:
            print(f"   Calling orchestrator...")
            orchestration_response = orchestrator.orchestrate(
                message=enriched_query,  # HACKDAY: Use enriched query with memory context
                id=chat_id
            )
            print(f"   ✅ Orchestration route: {orchestration_response['route']}")

            # Parse response:
            response = None
            if orchestration_response["route"] == "fallback":
                response = orchestration_response["result"]

            elif orchestration_response["route"] == "clu":
                intent = orchestration_response["result"]["intent"]
                entities = orchestration_response["result"]["entities"]

                # Here, you may call external functions based on recognized intent:
                hooks_module = importlib.import_module("clu_hooks")
                hook_func = getattr(hooks_module, intent)
                response = hook_func(entities)

            elif orchestration_response["route"] == "cqa":
                answer = orchestration_response["result"]["answer"]
                response = answer

            print(f"   ✅ Response preview: {str(response)[:100]}...")
        except Exception as e:
            print(f"   ❌ ERROR processing utterance: {e}")
            import traceback
            traceback.print_exc()
            response = f"Error: {str(e)}"

        # HACKDAY: Log orchestration event
        try:
            log_orchestration(
                message=query,
                route=orchestration_response["route"],
                result=response,
                router_type=router_type.name
            )
        except Exception as e:
            print(f"Warning: Failed to log orchestration: {e}")

        responses.append(response)

    if PII_ENABLED:
        # Clean up PII memory:
        pii_redacter.remove(id=chat_id)

    # HACKDAY: Log complete chat interaction
    try:
        log_chat_completion(
            original_message=message,
            utterances=utterances,
            responses=responses,
            model=os.environ.get("AOAI_DEPLOYMENT", "gpt-4o-mini"),
            router_type=router_type.name
        )
    except Exception as e:
        print(f"Warning: Failed to log chat completion: {e}")

    # HACKDAY: Step 2 - Store interaction in Memora
    if MEMORA_ENABLED and memora_client and responses:
        try:
            conversation_id = f"conv_{MEMORA_USER_ID}_{datetime.now().strftime('%Y%m%d')}"
            memory_text = f"User: {message}\nAssistant: {' '.join(responses)}"

            print(f"💾 Storing interaction in Memora (conversation: {conversation_id})")
            result = memora_client.index_memory(
                user_id=MEMORA_USER_ID,
                text=memory_text,
                conversation_id=conversation_id,
                metadata={
                    "timestamp": datetime.now().isoformat(),
                    "router_type": router_type.name,
                    "utterance_count": len(utterances)
                }
            )
            if result:
                print(f"   ✅ Memory stored successfully")
            else:
                print(f"   ⚠️  Memory storage failed")
        except Exception as e:
            print(f"⚠️  Memory storage error: {e}")

    print(f"\n✅ RETURNING {len(responses)} responses: {responses}")
    print(f"{'='*80}\n")
    return responses


@app.get("/", response_class=HTMLResponse)
async def home_page():
    """Serve the index.html page."""
    with open("dist/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/chat")
async def chat(request: Request):
    content = await request.json()
    message = content["message"]

    responses = orchestrate_chat(message)

    print(f"responses: {responses}")
    return JSONResponse({
        "messages": responses
    })


@app.get("/logs/stats")
async def logs_stats():
    """HACKDAY: Get statistics about logged data"""
    stats = get_log_stats()
    return JSONResponse(stats)
