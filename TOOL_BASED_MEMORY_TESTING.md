# Tool-Based Memory Integration - Testing Guide

## ✅ Implementation Complete!

We've successfully converted Memora integration from automatic to tool-based approach.

## 🎯 What Changed?

### Before (Automatic)
- ❌ Memora recall happened on EVERY request
- ❌ Memora storage happened on EVERY response
- ❌ No visibility into when memory was used
- ❌ Wasted API calls on simple queries

### After (Tool-Based)
- ✅ Agent decides WHEN to recall memories
- ✅ Agent decides WHEN to store memories
- ✅ UI shows tool calls with full transparency
- ✅ More efficient - only searches when relevant

## 🧪 Testing Instructions

### 1. Rebuild Frontend
```bash
cd src/frontend
npm run build
```

### 2. Start Memora (Terminal 1)
```bash
cd /Users/nlubchenco/dev/src/github.com/github.com/twilio-internal/memora-domain
AWS_PROFILE=memora-dev make dev-start

# Wait for: "Started memory-api-server"
```

### 3. Start Agent with Memora Enabled (Terminal 2)
```bash
cd src/backend/src
export MEMORA_ENABLED=true
export MEMORA_USER_ID=caroline
./hackday_run.sh
```

### 4. Open Browser
```bash
open http://127.0.0.1:7000
```

## 🎬 Test Scenarios

### Scenario 1: Query That Should Trigger Memory Search
**User Query:** "Tell me about my pride event experiences"

**Expected Behavior:**
1. UI shows expandable "Tool Calls" section (orange/yellow background)
2. Click to expand and see: `🔍 search_memories`
3. Arguments show: `query: "pride events"` (or similar)
4. Agent response includes specific details from Caroline's memories

**What to Look For:**
- Tool call appears BEFORE the agent response
- Response mentions specific events (pride parades, organizing)
- Response feels personalized, not generic

### Scenario 2: Query That Should NOT Trigger Tools
**User Query:** "What's 2 + 2?"

**Expected Behavior:**
1. NO tool calls section appears
2. Agent responds directly: "4"
3. Fast response (no unnecessary memory search)

**What to Look For:**
- No orange "Tool Calls" section
- Immediate response
- Simple, direct answer

### Scenario 3: Sharing Information That Should Be Stored
**User Query:** "I just organized a youth pride workshop focused on mental health resources"

**Expected Behavior:**
1. UI shows tool call: `💾 store_memory`
2. Arguments show the content being stored
3. Agent confirms the memory was stored

**Follow-up Test:**
- Ask: "What advocacy work have I done recently?"
- Should now include the youth pride workshop

### Scenario 4: Multiple Tool Calls
**User Query:** "What mentoring work have I done, and please remember that I'm planning a new mentorship program for next month"

**Expected Behavior:**
1. Tool call: `🔍 search_memories` (query: "mentoring")
2. Tool call: `💾 store_memory` (content about new program)
3. Response incorporates both recalled memories AND acknowledges the new plan

### Scenario 5: Switch Personas
```bash
# Stop server (Ctrl+C in Terminal 2)
export MEMORA_USER_ID=melanie
./hackday_run.sh
```

**User Query:** "Tell me about family activities"

**Expected Behavior:**
- Tool call shows search for family/activities
- Response includes Melanie's memories (camping, pottery)
- Different memories than Caroline's

## 🐛 Troubleshooting

### Tool Calls Not Showing
**Check:**
1. Is `MEMORA_ENABLED=true`? Look for startup message: "✅ Memora integration enabled"
2. Did frontend rebuild complete? Check `src/backend/src/dist/` has new files
3. Hard refresh browser (Cmd+Shift+R or Ctrl+Shift+R)

### No Memories Found
**Check:**
1. Memora is running: `curl http://localhost:8000/health`
2. User has memories: Check MEMORA_QUICK_START.md for persona details
3. Try lowering relevance threshold in `memory_tools.py` line 49: `min_score=0.1`

### Agent Not Calling Tools
**This is expected for:**
- Math questions
- General knowledge queries
- Greeting messages
- Simple yes/no questions

**Agent SHOULD call tools for:**
- "Tell me about my..."
- "What have I done..."
- "Remember that I..."
- "I just..."

## 📊 Verification Checklist

- [ ] Tool calls appear in UI with expandable section
- [ ] `search_memories` called for relevant queries
- [ ] `store_memory` called when sharing information
- [ ] Tool call arguments are visible
- [ ] Agent responses use recalled memories
- [ ] Simple queries DON'T trigger tools
- [ ] Different personas retrieve different memories

## 🎨 UI Features

### Tool Calls Display
- **Orange/yellow background**: Distinguishes from regular messages
- **Expandable**: Click arrow to show/hide details
- **Icons**: 🔍 for search, 💾 for storage
- **Arguments**: Shows exactly what was passed to tools

### Backend Console Output
Watch Terminal 2 for detailed logging:
```
🔵 NEW REQUEST: Tell me about pride events
⚙️  Extracting utterances...
⚙️  Processing utterance 1/1: Tell me about pride events
   Calling orchestrator...
   📤 Sending N messages to OpenAI...
   🔧 Tool calls made: ['search_memories']
   📥 OpenAI response: Based on your experiences...
✅ RETURNING 1 responses
🔧 Tool calls made: 1
```

## 🚀 Next Steps for Demo

1. **Prepare Queries**: Create a list of demo queries that showcase different scenarios
2. **Compare Before/After**: Show response with and without memory context
3. **Live Tool Visibility**: Highlight the expandable tool calls section
4. **Switch Personas**: Demo how memories are personalized per user

## 📝 Key Files Modified

- `src/backend/src/memory_tools.py` - Memory tool definitions
- `src/backend/src/aoai_client.py` - Tool calling support
- `src/backend/src/unified_app.py` - Tool-based orchestration
- `src/backend/src/unified_conversation_orchestrator.py` - Pass-through support
- `src/frontend/src/Chat.jsx` - Tool calls UI
- `src/frontend/src/App.css` - Tool calls styling

## 🎯 Demo Talking Points

1. **Efficiency**: "Agent only searches memories when relevant"
2. **Transparency**: "You can see exactly when and how your memories are used"
3. **Intelligence**: "The AI decides when memory is helpful vs. when it's not needed"
4. **Personalization**: "Same question, different memories based on who you are"

Happy testing! 🎉
