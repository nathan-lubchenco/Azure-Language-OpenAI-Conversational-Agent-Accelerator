# Hackday Data Logging

All conversation data is automatically logged to flat files for analysis.

## Log Location

```
src/backend/src/hackday_logs/
└── conversations_YYYYMMDD.jsonl  (one file per day)
```

## Log Format

Logs use **JSONL format** (JSON Lines) - one JSON object per line. This makes it easy to:
- Stream process large files
- Use with `jq` for filtering
- Import into analysis tools

## Event Types

### 1. `utterance_extraction`
Logged when user message is split into separate utterances.

```json
{
  "timestamp": "2025-10-06T14:30:22.123456",
  "event_type": "utterance_extraction",
  "original_message": "What is your return policy? And how long does shipping take?",
  "extracted_utterances": [
    "What is your return policy?",
    "How long does shipping take?"
  ],
  "utterance_count": 2,
  "model": "gpt-4o-mini"
}
```

### 2. `orchestration`
Logged for each utterance routed through the orchestrator.

```json
{
  "timestamp": "2025-10-06T14:30:22.456789",
  "event_type": "orchestration",
  "message": "What is your return policy?",
  "route": "fallback",
  "router_type": "BYPASS",
  "result_preview": "Our return policy allows..."
}
```

### 3. `chat_completion`
Logged when the complete conversation is processed.

```json
{
  "timestamp": "2025-10-06T14:30:22.789012",
  "event_type": "chat_completion",
  "original_message": "What is your return policy? And how long does shipping take?",
  "utterances": ["What is your return policy?", "How long does shipping take?"],
  "responses": ["Our return policy allows...", "Shipping typically takes 3-5 days..."],
  "utterance_count": 2,
  "response_count": 2,
  "model": "gpt-4o-mini",
  "router_type": "BYPASS"
}
```

### 4. `error`
Logged when errors occur.

```json
{
  "timestamp": "2025-10-06T14:30:22.999999",
  "event_type": "error",
  "error_type": "harmful_content",
  "error_message": "Unable to parse utterances",
  "context": {"message": "..."}
}
```

## Viewing Logs

### Command-Line Viewer

```bash
# View latest conversations
python view_logs.py

# Show statistics
python view_logs.py stats

# Search for specific content
python view_logs.py search "return"

# View only specific event types
python view_logs.py utterances
python view_logs.py completions
python view_logs.py orchestration
python view_logs.py errors
```

### Using jq (JSON processor)

```bash
# View all chat completions
cat hackday_logs/*.jsonl | jq 'select(.event_type == "chat_completion")'

# Extract just the messages
cat hackday_logs/*.jsonl | jq -r '.original_message'

# Count events by type
cat hackday_logs/*.jsonl | jq -r '.event_type' | sort | uniq -c

# Find conversations with specific keywords
cat hackday_logs/*.jsonl | jq 'select(.original_message | contains("return"))'

# Get all responses
cat hackday_logs/*.jsonl | jq -r 'select(.event_type == "chat_completion") | .responses[]'
```

### Web API

```bash
# Get statistics
curl http://127.0.0.1:7000/logs/stats | jq .
```

## Analysis Examples

### Count total conversations
```bash
grep -c '"event_type": "chat_completion"' hackday_logs/*.jsonl
```

### Find most common queries
```bash
cat hackday_logs/*.jsonl | jq -r 'select(.event_type == "chat_completion") | .original_message' | sort | uniq -c | sort -rn | head -10
```

### Calculate average utterances per message
```bash
cat hackday_logs/*.jsonl | jq -r 'select(.event_type == "chat_completion") | .utterance_count' | awk '{sum+=$1; count++} END {print sum/count}'
```

### Export to CSV
```bash
cat hackday_logs/*.jsonl | jq -r 'select(.event_type == "chat_completion") | [.timestamp, .original_message, .response_count] | @csv' > conversations.csv
```

## Data Retention

- Logs are stored indefinitely (not automatically deleted)
- One file per day keeps files manageable
- Safe to delete old logs manually if needed

## Privacy

**Important:** These logs contain all user messages and AI responses.
- Don't commit logs to git (`.gitignore` should exclude `hackday_logs/`)
- Review before sharing
- Delete after hackday if containing sensitive test data

## For Demo

Use these logs to:
- Show what utterances were extracted
- Demonstrate routing decisions
- Analyze conversation patterns
- Compare different models or configurations
- Create visualizations of agent behavior
