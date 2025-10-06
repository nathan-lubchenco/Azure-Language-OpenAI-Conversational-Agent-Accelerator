# Memora Integration - Quick Start

## ✅ Integration Complete!

Your conversational agent now integrates with Memora for memory recall and storage.

## 🚀 How to Use

### Step 1: Start Memora (Terminal 1)
```bash
cd /Users/nlubchenco/dev/src/github.com/github.com/twilio-internal/memora-domain
AWS_PROFILE=memora-dev make dev-start

# Wait until you see: "Started memory-api-server"
```

### Step 2: Start Agent with Memora Enabled (Terminal 2)
```bash
cd /Users/nlubchenco/dev/src/github.com/Azure-Language-OpenAI-Conversational-Agent-Accelerator/src/backend/src

# Enable Memora
export MEMORA_ENABLED=true
export MEMORA_USER_ID=caroline  # or: melanie, gina, john, etc.

./hackday_run.sh
```

### Step 3: Test the Integration

**Option A: Run Demo Script**
```bash
# Terminal 3
cd src/backend/src
./demo_with_memora.sh
```

**Option B: Manual Testing**
```bash
# Test query about pride events (Caroline has memories about this)
curl -X POST http://127.0.0.1:7000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about pride events"}' | jq .

# Test query about mentoring
curl -X POST http://127.0.0.1:7000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Who are you mentoring?"}' | jq .
```

## 🎯 What Happens

### For each request:

1. **📚 Memory Recall**
   - Agent queries Memora with user's message
   - Retrieves top 3 most relevant memories (score > 0.5)
   - Formats them into context

2. **🤖 Processing**
   - Adds memory context to the query
   - Sends enriched query to OpenAI
   - Generates response with full context

3. **💾 Memory Storage**
   - Stores user message + agent response
   - Tagged with timestamp and metadata
   - Available for future recall

## 👁️ Watching It Work

**In the server terminal, you'll see:**
```
================================================================================
🔵 NEW REQUEST: Tell me about pride events
================================================================================
📚 Recalling memories for user: caroline
   Found 3 relevant memories
   ✨ Enriched with memory context
⚙️  Extracting utterances...
✅ Utterances: ['Tell me about pride events.']

⚙️  Processing utterance 1/1: Tell me about pride events.
   ✨ Enriched with memory context
   Calling orchestrator...
   📤 Sending 2 messages to OpenAI...
   📥 OpenAI response: Based on your past experiences, you attended...
   ✅ Orchestration route: fallback
   ✅ Response preview: Based on your past experiences...

💾 Storing interaction in Memora (conversation: conv_caroline_20251006)
   ✅ Memory stored successfully

✅ RETURNING 1 responses: [...]
================================================================================
```

## 🎭 Demo Personas

### Caroline (LGBTQ+ Advocate & Artist)
**Good queries:**
- "Tell me about pride events"
- "Who are you mentoring?"
- "What kind of art do you create?"
- "How do you support the LGBTQ community?"

**Expected:** Agent recalls memories about pride parades, mentoring transgender teen, advocacy art

### Melanie (Parent & Artist)
**Good queries:**
- "Tell me about your family"
- "What do you do with your children?"
- "Tell me about camping trips"
- "What pottery projects are you working on?"

**Expected:** Agent recalls memories about family camping, children's milestones, pottery

### Gina (Entrepreneur & Dancer)
**Good queries:**
- "Tell me about your business"
- "What kind of dance do you do?"
- "How did you start your clothing store?"

**Expected:** Agent recalls memories about clothing store launch, dance rehearsals

## 🔄 Switching Personas

```bash
# Stop the server (Ctrl+C)

# Switch to Melanie
export MEMORA_USER_ID=melanie
./hackday_run.sh

# Now queries will recall Melanie's memories instead!
```

## 🐛 Troubleshooting

### "No memories found"
- Check Memora is running: `curl http://localhost:8000/health`
- Verify data is loaded: See `MEMORA_EXPLORATION.md`
- Try lowering min_score: Edit `unified_app.py` line 122 to `min_score=0.0`

### "Memora disabled"
- Make sure you set: `export MEMORA_ENABLED=true`
- Check server startup logs for "Memora integration enabled"

### Agent not using memory context
- Watch server terminal for "📚 Recalling memories"
- Check if memories were found: Should show "Found N relevant memories"
- If found 0, the query might not match available memories

## 📊 View Integration Logs

```bash
# View recent interactions
python view_logs.py

# Check for Memora-specific events
python view_logs.py | grep -i memora

# View statistics
python view_logs.py stats
```

## 🎬 For Your Tuesday Demo

**Demo Flow:**
1. Show agent WITHOUT Memora (generic responses)
2. Enable Memora with Caroline's persona
3. Ask about pride events → Show rich, contextual response
4. Ask follow-up questions → Show agent maintains context
5. Switch to Melanie → Show different memories/personality

**What to Highlight:**
- ✅ Agent recalls relevant past conversations
- ✅ Responses are personalized with actual memories
- ✅ New interactions are stored for future recall
- ✅ Semantic search finds relevant memories even without exact keywords
- ✅ Each user has isolated memory profiles

## 🔧 Configuration Options

```bash
# In hackday_run.sh or export before running:

# Enable/disable Memora
export MEMORA_ENABLED=true

# Switch user personas
export MEMORA_USER_ID=caroline   # LGBTQ+ advocate
export MEMORA_USER_ID=melanie    # Parent & artist
export MEMORA_USER_ID=gina       # Entrepreneur & dancer

# Adjust recall parameters (edit unified_app.py line 118-122):
# - limit: Number of memories to retrieve (default: 3)
# - min_score: Minimum relevance score (default: 0.5, lower = more results)
```

## 🚀 Quick Test

```bash
# Terminal 1: Start Memora
cd /Users/nlubchenco/dev/src/github.com/github.com/twilio-internal/memora-domain
AWS_PROFILE=memora-dev make dev-start

# Terminal 2: Start Agent with Memora
cd /Users/nlubchenco/dev/src/github.com/Azure-Language-OpenAI-Conversational-Agent-Accelerator/src/backend/src
export MEMORA_ENABLED=true
export MEMORA_USER_ID=caroline
./hackday_run.sh

# Terminal 3: Test
curl -X POST http://127.0.0.1:7000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about pride events"}' | jq .
```

You should see a response that incorporates Caroline's actual memories about pride parades!
