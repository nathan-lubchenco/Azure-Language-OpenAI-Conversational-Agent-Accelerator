#!/bin/bash
# HACKDAY: Run the app with OpenAI instead of Azure

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: OPENAI_API_KEY environment variable is not set"
    echo "Get your API key from: https://platform.openai.com/api-keys"
    echo "Then run: export OPENAI_API_KEY='your-key-here'"
    exit 1
fi

echo "🌟 Starting LifePath AI - Your Personal Growth Companion"
echo "OPENAI_API_KEY: ${OPENAI_API_KEY:0:7}..."

# Set minimal env vars
export LANGUAGE_ENDPOINT="dummy"
export AOAI_ENDPOINT="dummy"
export AOAI_DEPLOYMENT="${AOAI_DEPLOYMENT:-gpt-4o-mini}"
export SEARCH_ENDPOINT="dummy"
export SEARCH_INDEX_NAME="dummy"
export USE_MI_AUTH="false"
export ROUTER_TYPE="BYPASS"
export APP_MODE="UNIFIED"
export PII_ENABLED="false"

# Memora integration (HACKDAY)
export MEMORA_ENABLED="${MEMORA_ENABLED:-true}"
export MEMORA_BASE_URL="${MEMORA_BASE_URL:-http://localhost:8000}"
export MEMORA_ACCOUNT_ID="${MEMORA_ACCOUNT_ID:-test-account}"
export MEMORA_SERVICE_ID="${MEMORA_SERVICE_ID:-test-service}"
export MEMORA_USER_ID="${MEMORA_USER_ID:-john}"  # john (197 memories), caroline, melanie, gina

echo "✅ Using OpenAI model: $AOAI_DEPLOYMENT"
echo "✅ Router type: $ROUTER_TYPE (direct to OpenAI, no Azure services)"

if [ "$MEMORA_ENABLED" = "true" ]; then
    echo "✅ Memory tools enabled for: $MEMORA_USER_ID (${MEMORA_BASE_URL})"
    echo "   🔍 search_memories - Find relevant past experiences"
    echo "   💾 store_memory - Remember new information"
else
    echo "⚠️  Memory tools disabled (set MEMORA_ENABLED=true to enable)"
fi

echo ""
echo "🌐 Open LifePath AI at: http://127.0.0.1:7000"
echo ""

# Run the app
python3 -m uvicorn unified_app:app --host 127.0.0.1 --port 7000
