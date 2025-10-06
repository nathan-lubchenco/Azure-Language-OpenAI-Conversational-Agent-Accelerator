# Hackday Modifications

**Date:** October 2025
**Purpose:** Run the conversational agent locally using OpenAI (not Azure) for hackday testing

## What Was Changed

### 1. `src/backend/src/aoai_client.py`
- **Changed:** `AzureOpenAI` → `OpenAI`
- **Auth:** Azure AD token → OpenAI API key from `OPENAI_API_KEY` env var
- **Endpoint:** Azure endpoint → api.openai.com (default)
- **Models:** Azure deployment names → OpenAI model names (e.g., `gpt-4o-mini`)

### 2. `src/backend/src/hackday_mocks.py` (NEW)
- **MockTextAnalyticsClient:** Always returns "en" for language detection
- **MockSearchClient:** Returns empty search results (disables RAG)

### 3. `src/backend/src/unified_app.py`
- Uses `MockSearchClient` instead of Azure AI Search
- Uses `MockTextAnalyticsClient` instead of Azure Language
- Disables RAG (no Azure Search available)
- All clients now use OpenAI

### 4. `src/backend/src/unified_conversation_orchestrator.py`
- Uses `MockTextAnalyticsClient` for language detection

### 5. `src/backend/src/hackday_run.sh` (NEW)
- Startup script that sets all required env vars
- Checks for `OPENAI_API_KEY`
- Runs the server on port 7000

## How to Use

### Prerequisites
1. **Get OpenAI API Key:**
   - Go to https://platform.openai.com/api-keys (or use Twilio's OpenAI Okta tile)
   - Create a new API key
   - Copy it

2. **Set Environment Variable:**
   ```bash
   export OPENAI_API_KEY='sk-proj-...'
   ```

### Run the App
```bash
cd src/backend/src
./hackday_run.sh
```

### Access the UI
Open browser to: http://127.0.0.1:7000

## What Works

✅ Basic chat with OpenAI (gpt-4o-mini)
✅ Utterance extraction
✅ BYPASS router (direct to OpenAI)
✅ Language detection (mocked to always return "en")

## What Doesn't Work

❌ Azure AI Search / RAG (mocked, returns empty results)
❌ CLU (Conversational Language Understanding) - requires Azure
❌ CQA (Custom Question Answering) - requires Azure
❌ TRIAGE_AGENT router - requires Azure AI Foundry
❌ FUNCTION_CALLING router - requires CLU/CQA
❌ SEMANTIC_KERNEL mode - requires Azure AI Foundry agents
❌ PII detection/redaction - requires Azure Language

## Limitations

- **Only BYPASS mode works:** Routes everything directly to OpenAI
- **No grounding:** RAG is disabled (no Azure Search)
- **English only:** Language detection always returns "en"
- **No deterministic routing:** Can't use CLU intents or CQA exact answers

## For Production

**DO NOT use these changes in production.** This is a hackday workaround. The real app requires:
- Azure OpenAI (not OpenAI)
- Azure AI Search (for RAG)
- Azure AI Language (for CLU/CQA/PII)
- Azure AI Foundry (for Semantic Kernel agents)

To deploy properly:
```bash
azd up  # Requires Azure subscription
```

## Reverting Changes

To restore original Azure functionality:
```bash
git checkout src/backend/src/aoai_client.py
git checkout src/backend/src/unified_app.py
git checkout src/backend/src/unified_conversation_orchestrator.py
rm src/backend/src/hackday_mocks.py
rm src/backend/src/hackday_run.sh
```

## Environment Variables Used

| Variable | Value | Purpose |
|----------|-------|---------|
| `OPENAI_API_KEY` | Your API key | **REQUIRED** - OpenAI authentication |
| `AOAI_DEPLOYMENT` | `gpt-4o-mini` | Model to use (can also use `gpt-4o`, `gpt-3.5-turbo`) |
| `ROUTER_TYPE` | `BYPASS` | Direct routing to OpenAI (only mode that works) |
| `APP_MODE` | `UNIFIED` | Use UnifiedConversationOrchestrator |
| `PII_ENABLED` | `false` | Disable PII (requires Azure) |
| Others | `dummy` | Ignored, set for compatibility |
