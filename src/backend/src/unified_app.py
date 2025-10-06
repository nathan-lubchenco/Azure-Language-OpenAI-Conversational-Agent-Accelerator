# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# HACKDAY: Added data logging and Memora tool-based integration
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
from memory_tools import create_memory_tools


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

    # Create memory tools
    memory_tools, memory_tool_implementations = create_memory_tools(memora_client, MEMORA_USER_ID)
    print(f"✅ Created {len(memory_tools)} memory tools: {[t['function']['name'] for t in memory_tools]}")
else:
    memora_client = None
    memory_tools = []
    memory_tool_implementations = {}
    print("⚠️  Memora integration disabled")

# LifePath AI system prompt
lifepath_prompt = get_prompt("lifepath_system.txt")

# RAG AOAI client (now using OpenAI with memory tools):
rag_client = AOAIClient(
    endpoint=os.environ.get("AOAI_ENDPOINT", "dummy"),  # Ignored for OpenAI
    deployment=os.environ.get("AOAI_DEPLOYMENT", "gpt-4o-mini"),
    system_message=lifepath_prompt,  # LifePath AI personality
    use_rag=False,  # HACKDAY: Disable RAG since we don't have Azure Search
    search_client=search_client,
    function_calling=MEMORA_ENABLED,  # Enable if Memora is enabled
    tools=memory_tools if MEMORA_ENABLED else None,
    functions=memory_tool_implementations if MEMORA_ENABLED else None
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


# Fallback function (RAG with tool calling):
def fallback_function(
    query: str,
    language: str,
    id: int,
    return_tool_calls: bool = False
) -> str | dict:
    """
    Call RAG client for grounded chat completion with optional tool calling.
    """
    if PII_ENABLED:
        # Redact PII:
        query = pii_redacter.redact(
            text=query,
            id=id,
            language=language,
            cache=True
        )

    return rag_client.chat_completion(query, return_tool_calls=return_tool_calls)


# Unified-Conversation-Orchestrator:
router_type = RouterType(os.environ.get("ROUTER_TYPE", "BYPASS"))
orchestrator = UnifiedConversationOrchestrator(
    router_type=router_type,
    fallback_function=fallback_function
)

chat_id = 0


def orchestrate_chat(message: str) -> dict:
    """
    Orchestrate chat with tool-based memory integration.

    Returns:
        dict with {
            "messages": list of response strings,
            "tool_calls": list of tool call info (if any tools were called)
        }
    """
    print(f"\n{'='*80}")
    print(f"🔵 NEW REQUEST: {message}")
    print(f"{'='*80}")

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
    all_tool_calls = []

    for i, query in enumerate(utterances, 1):
        print(f"\n⚙️  Processing utterance {i}/{len(utterances)}: {query}")

        try:
            if PII_ENABLED:
                # Reconstruct PII:
                query = pii_redacter.reconstruct(
                    text=query,
                    id=chat_id,
                    cache=True
                )

            # Orchestrate (with tool calling if enabled):
            print(f"   Calling orchestrator...")
            orchestration_response = orchestrator.orchestrate(
                message=query,
                id=chat_id,
                return_tool_calls=MEMORA_ENABLED  # Request tool call info if Memora enabled
            )
            print(f"   ✅ Orchestration route: {orchestration_response['route']}")

            # Parse response:
            response = None
            tool_calls = []

            if orchestration_response["route"] == "fallback":
                result = orchestration_response["result"]

                # Handle dict response with tool_calls (from AOAIClient)
                if isinstance(result, dict) and "content" in result:
                    response = result["content"]
                    tool_calls = result.get("tool_calls", [])
                    if tool_calls:
                        print(f"   🔧 Tool calls made: {[tc['name'] for tc in tool_calls]}")
                        all_tool_calls.extend(tool_calls)
                else:
                    response = result

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

    result = {
        "messages": responses,
        "tool_calls": all_tool_calls if all_tool_calls else None
    }

    print(f"\n✅ RETURNING {len(responses)} responses")
    if all_tool_calls:
        print(f"🔧 Tool calls made: {len(all_tool_calls)}")
    print(f"{'='*80}\n")
    return result


@app.get("/", response_class=HTMLResponse)
async def home_page():
    """Serve the index.html page."""
    with open("dist/index.html", "r", encoding="utf-8") as f:
        return f.read()


@app.post("/chat")
async def chat(request: Request):
    content = await request.json()
    message = content["message"]

    result = orchestrate_chat(message)

    print(f"result: {result}")
    return JSONResponse(result)


@app.get("/logs/stats")
async def logs_stats():
    """HACKDAY: Get statistics about logged data"""
    stats = get_log_stats()
    return JSONResponse(stats)


@app.get("/user-info")
async def user_info():
    """HACKDAY: Return current user ID for UI display"""
    return JSONResponse({
        "user_id": MEMORA_USER_ID,
        "memora_enabled": MEMORA_ENABLED
    })
