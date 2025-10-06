# Tool Calling Test Scenarios

## 🎯 Critical Test: Life Direction Question

### ❌ Before (Wrong Behavior)
```
User: "What should John do next in life?"

Agent Response (NO TOOL CALLED):
"To provide tailored advice, I would need to know more about John's current
situation, goals, or any challenges he may be facing..."
```

**Problem**: Agent asks for more info instead of searching memories!

### ✅ After (Correct Behavior)
```
User: "What should John do next in life?"

Tool Called: search_memories
Arguments: {
  "query": "goals aspirations career interests life direction",
  "limit": 5
}

Agent Response (using John's actual memories):
"Based on your experiences and interests, here are some directions to consider:
1. [Specific advice based on John's actual goals from memories]
2. [References to John's past achievements]
3. [Suggestions aligned with John's values and interests]"
```

## 📋 Test Scenarios

### Scenario 1: Life Direction (MUST trigger search_memories)
**Queries that MUST call search_memories:**
- "What should I do next in life?"
- "What should John do next?"
- "What are my goals?"
- "What direction should I take?"
- "Help me figure out my next steps"

**Expected Tool Call:**
```json
{
  "name": "search_memories",
  "arguments": {
    "query": "goals aspirations career interests life direction",
    "limit": 5
  }
}
```

### Scenario 2: Past Experiences (MUST trigger search_memories)
**Queries:**
- "Tell me about my pride event experiences"
- "What have I accomplished?"
- "Who am I mentoring?"

**Expected Tool Call:**
```json
{
  "name": "search_memories",
  "arguments": {
    "query": "pride events advocacy lgbtq",
    "limit": 3
  }
}
```

### Scenario 3: Sharing New Info (MUST trigger store_memory)
**Queries:**
- "I just completed a mental health workshop"
- "I'm planning a new mentorship program"
- "My goal is to launch a business next year"

**Expected Tool Call:**
```json
{
  "name": "store_memory",
  "arguments": {
    "content": "Completed mental health workshop...",
    "tags": "advocacy,lgbtq,workshop"
  }
}
```

### Scenario 4: Simple Questions (NO tools)
**Queries that should NOT call tools:**
- "What's 2 + 2?"
- "What's the capital of France?"
- "Hello"
- "How's the weather?"

**Expected**: Direct answer, no tool calls

## 🔍 How to Verify

### Backend Console Check
Look for these lines:
```
🔧 Tool calls made: ['search_memories']
```

### UI Check
1. Look for orange "Tool Calls" section
2. Click to expand
3. Verify tool name and arguments

### Response Quality Check
Response should:
- Reference specific memories
- Be personalized (not generic)
- Show understanding of user's background

## 🚨 Red Flags

**If you see these, something is wrong:**
- ❌ "I would need to know more about..."
- ❌ "Can you tell me more about your goals?"
- ❌ Generic advice without personal context
- ❌ No tool calls for life direction questions

## ✅ Success Indicators

**What good responses look like:**
- ✅ Tool call appears in logs and UI
- ✅ Response references actual memories
- ✅ Specific, personalized advice
- ✅ No generic "tell me more" responses

## 🧪 Testing Checklist

Before demo:
- [ ] Test: "What should I do next in life?" → Calls search_memories
- [ ] Test: "What are my goals?" → Calls search_memories
- [ ] Test: "Tell me about my achievements" → Calls search_memories
- [ ] Test: "I just completed X" → Calls store_memory
- [ ] Test: "What's 2+2?" → NO tools called
- [ ] Verify tool calls show in UI
- [ ] Verify responses use actual memories
- [ ] Test with different personas (Caroline, Melanie, Gina, John)

## 🎯 Key Prompt Updates

We made these critical changes to ensure tools are called:

### System Prompt (`lifepath_system.txt`)
- Added "CRITICAL INSTRUCTIONS" section
- Explicit list of triggers: "ALWAYS search memories when..."
- Examples: "What should I do next in life?"
- Directive: "DON'T say you need more information. SEARCH THEIR MEMORIES FIRST"

### Tool Description (`memory_tools.py`)
- "CRITICAL: Use this whenever you need context about the user"
- Concrete examples in description
- Increased default limit from 3 to 5
- Better parameter descriptions with examples

These changes should make the agent ~10x more likely to proactively use memory tools!
