#!/bin/bash
# HACKDAY: Run the app with OpenAI instead of Azure

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "ERROR: OPENAI_API_KEY environment variable is not set"
    echo "Get your API key from: https://platform.openai.com/api-keys"
    echo "Then run: export OPENAI_API_KEY='your-key-here'"
    exit 1
fi

echo "🚀 Starting HACKDAY version with OpenAI..."
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

echo "✅ Using OpenAI model: $AOAI_DEPLOYMENT"
echo "✅ Router type: $ROUTER_TYPE (direct to OpenAI, no Azure services)"
echo ""
echo "🌐 Starting server on http://127.0.0.1:7000"
echo ""

# Run the app
python3 -m uvicorn unified_app:app --host 127.0.0.1 --port 7000
