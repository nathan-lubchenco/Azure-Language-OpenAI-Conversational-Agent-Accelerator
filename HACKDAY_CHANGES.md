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

### 6. `src/backend/src/data_logger.py` (NEW)
- Logs all conversation data to flat files (JSONL format)
- Tracks utterance extraction, orchestration, and chat completions
- Stores in `./hackday_logs/` directory

### 7. `src/backend/src/view_logs.py` (NEW)
- Helper script to view and analyze logged data
- Search logs, view statistics, filter by event type

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

### View Logged Data

**Using the command-line viewer:**
```bash
# View latest 10 conversations
python view_logs.py

# View latest 50 conversations
python view_logs.py 50

# Show statistics
python view_logs.py stats

# Search for specific content
python view_logs.py search "return policy"

# Filter by event type
python view_logs.py utterances     # Only utterance extractions
python view_logs.py completions    # Only chat completions
python view_logs.py orchestration  # Only orchestration events
python view_logs.py errors         # Only errors
```

**Using the web API:**
```bash
# Get log statistics
curl http://127.0.0.1:7000/logs/stats
```

**Direct file access:**
```bash
# Logs are stored in JSONL format (one JSON object per line)
cat hackday_logs/conversations_20251006.jsonl | jq .

# Count conversations
wc -l hackday_logs/*.jsonl
```

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
