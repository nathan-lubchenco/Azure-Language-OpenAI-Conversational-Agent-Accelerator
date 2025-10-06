# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Azure Language OpenAI Conversational Agent Accelerator - A code-first template for building deterministic conversational agents using Azure AI Language (CLU/CQA), Azure AI Agent Service, and Azure OpenAI. Minimizes prompt engineering by routing top questions to exact answers, intents to deterministic handlers, and using LLM for long-tail queries.

## Hackday Context

**Note:** `context.md` in the repository root contains our hackday overview and broader project context. Not all content in `context.md` may be specific to this repository, but it provides valuable guidance on when to reference external resources or related projects.

## Architecture

### Core Components

**Backend (`src/backend/src/`):**
- **Two Orchestration Modes** (controlled by `APP_MODE` environment variable):
  - `UNIFIED`: Uses `UnifiedConversationOrchestrator` with multiple routing strategies
  - `SEMANTIC_KERNEL`: Uses `SemanticKernelOrchestrator` with Azure AI Agent group chat

- **Routing Strategies** (`router/router_type.py`):
  - `TRIAGE_AGENT`: Intent routing agent using CLU and CQA as tools
  - `FUNCTION_CALLING`: AOAI function-calling to decide CLU or CQA
  - `CLU`: Conversational Language Understanding only
  - `CQA`: Custom Question Answering only
  - `ORCHESTRATION`: Azure AI Language orchestration project
  - `BYPASS`: Direct fallback (RAG only)

- **Agent Plugins** (`agents/`): Semantic Kernel plugins for order operations (status, refund, cancel)
- **PII Handling** (`pii_redacter.py`): Optional PII detection and redaction before LLM processing
- **Fallback**: RAG with Azure AI Search when routing "fails"

**Frontend (`src/frontend/`):**
- React + Vite web UI for testing chat interactions
- Build outputs to `dist/` directory which is served by FastAPI

**Infrastructure (`infra/`):**
- Bicep templates for Azure deployment
- Setup scripts for CLU, CQA, and Azure AI Search indexes
- Sample data in `data/` (CLU intents, CQA Q&A pairs, product info)

### Key Workflow

1. User message → PII redaction (optional) → Utterance extraction
2. Each utterance → Router (based on `ROUTER_TYPE`)
3. Router decides: CLU (intent) → custom handler, CQA (FAQ) → exact answer, or fallback to RAG
4. Response → PII reconstruction (optional) → User

## Development Commands

### Frontend

```bash
cd src/frontend
npm install
npm run dev          # Development server
npm run build        # Production build (outputs to dist/)
```

### Backend

**Local development:**
```bash
cd src/backend
pip install -r requirements.txt
cd src

# Run Unified orchestration mode:
python3 -m uvicorn unified_app:app --reload --host 127.0.0.1 --port 7000

# Run Semantic Kernel orchestration mode:
python3 -m uvicorn semantic_kernel_app:app --reload --host 127.0.0.1 --port 7000
```

**Note:** Before running locally, build frontend and move `dist/` directory:
```bash
cd src/frontend && npm run build
mv dist ../backend/src/
```

### Testing

```bash
cd src/backend/src

# Test unified orchestration:
pytest test/test_unified_chat.py -s -v

# Test semantic kernel orchestration:
pytest test/test_sk_chat.py -s -v
```

Tests use pytest fixtures to launch uvicorn server automatically. Each test module validates single-turn and multi-turn conversations with expected responses.

### Deployment

**Deploy to Azure using azd:**
```bash
# First time setup:
az login
source infra/setup_azd_parameters.sh  # Configure deployment parameters

# Deploy:
azd auth login
azd up                                 # Provision + deploy (10-15 minutes)

# Clean up:
azd down
```

**Infrastructure scripts:**
- `infra/setup_azd_parameters.sh`: Helper to select region and model configurations
- `infra/scripts/language/`: CLU/CQA project setup scripts
- `infra/scripts/search/`: Azure AI Search index setup
- `infra/resources/`: Bicep modules for Azure resources

## Environment Variables

**Required for both modes:**
- `AOAI_ENDPOINT`, `AOAI_DEPLOYMENT`: Azure OpenAI configuration
- `SEARCH_ENDPOINT`, `SEARCH_INDEX_NAME`: Azure AI Search for RAG
- `LANGUAGE_ENDPOINT`: Azure AI Language service
- `USE_MI_AUTH`, `MI_CLIENT_ID`: Managed identity configuration
- `ROUTER_TYPE`: Routing strategy (see RouterType enum)
- `APP_MODE`: `SEMANTIC_KERNEL` or `UNIFIED`

**For CLU routing:**
- `CLU_PROJECT_NAME`, `CLU_DEPLOYMENT_NAME`, `CLU_CONFIDENCE_THRESHOLD`

**For CQA routing:**
- `CQA_PROJECT_NAME`, `CQA_DEPLOYMENT_NAME`, `CQA_CONFIDENCE_THRESHOLD`

**For Semantic Kernel mode (additional):**
- `AGENTS_PROJECT_ENDPOINT`: Azure AI Foundry project endpoint
- Agent IDs loaded from `config.json`: `TRIAGE_AGENT_ID`, `HEAD_SUPPORT_AGENT_ID`, `ORDER_STATUS_AGENT_ID`, `ORDER_CANCEL_AGENT_ID`, `ORDER_REFUND_AGENT_ID`, `TRANSLATION_AGENT_ID`
- `DELETE_OLD_AGENTS`, `MAX_AGENT_RETRY`

**Optional:**
- `PII_ENABLED`, `PII_CATEGORIES`, `PII_CONFIDENCE_THRESHOLD`: PII redaction
- `TRANSLATOR_RESOURCE_ID`, `TRANSLATOR_REGION`: Translation support

See `src/README.md` for complete list.

## Key Implementation Details

### Adding Custom Intents (CLU)

1. Update `infra/data/clu_import.json` with new intents, entities, utterances
2. Create handler function in `src/backend/src/clu_hooks.py` matching intent name
3. Redeploy: `azd up`

### Adding FAQ Pairs (CQA)

1. Update `infra/data/cqa_import.json` with question-answer pairs
2. Redeploy: `azd up`

### Extending Semantic Kernel Agents

- Add new plugins in `src/backend/src/agents/` (inherit from Semantic Kernel plugin base)
- Register in `SemanticKernelOrchestrator.initialize_agents()`
- Update routing logic in `CustomGroupChatManager.select_next_agent()`
- Create corresponding agent definition in Azure AI Foundry

### Custom Router Implementation

- Create router function in `src/backend/src/router/` (signature: `Callable[[str, str, str], dict]`)
- Add enum value to `RouterType` in `router/router_type.py`
- Register in `router/router_utils.py:create_router()`

## Docker Build

Multi-stage Dockerfile (`src/Dockerfile`):
1. Stage 1: Build frontend (Node.js 18)
2. Stage 2: Copy frontend build + install Python dependencies
3. Exposes port 7000, runs uvicorn with `app:app` (note: adjust CMD based on deployment target app file)

## Testing Strategy

- **Integration tests** (`test/test_*.py`): Validate end-to-end chat flows with real server
- **Parameterized test cases**: Single-turn and multi-turn conversations
- **Expected responses**: Exact string matching for deterministic validation
- **Multilingual support**: Tests include Spanish language validation

## Important Considerations

- **Confidence Thresholds**: CLU and CQA routes "fail" if confidence below threshold → triggers fallback
- **PII Lifecycle**: Redact before LLM → reconstruct after → clean up cache
- **Utterance Extraction**: User messages split into separate queries before routing
- **Semantic Kernel Retry Logic**: Max 3 retries with runtime cleanup between attempts
- **Agent Selection**: Custom routing logic in `CustomGroupChatManager` determines agent flow based on message content and role

## Sample Data Context

Default sample data based on "Contoso Outdoors" fictional outdoor retail company:
- CLU intents: OrderStatus, OrderRefund, OrderCancel
- CQA: Return policy, product information
- RAG grounding data: Product manuals for outdoor gear

## Project Dependencies

**Backend:**
- `semantic-kernel`: Agent orchestration framework
- `azure-ai-agents`: Azure AI Agent Service SDK
- `azure-ai-language-conversations`: CLU client
- `azure-ai-language-questionanswering`: CQA client
- `azure-search-documents`: RAG with Azure AI Search
- `fastapi`, `uvicorn`: Web framework

**Frontend:**
- `react` 19.0.0, `react-dom`, `react-markdown`
- `vite`: Build tool

## Security Notes

- Uses Managed Identity (no secrets in code)
- PII redaction before LLM processing
- Not production-ready without additional security hardening
- Follow guidance in README.md for limiting access and enabling VNet
