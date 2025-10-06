# Twilio Integration Plan for LifePath AI

Based on the hackday context.md requirements and our current architecture.

## 🎯 Integration Opportunities

### 1. SMS/WhatsApp via TAF (RECOMMENDED FIRST)

**Why this fits LifePath AI:**
- Async conversations perfect for reflection
- Users can check in throughout the day
- "Text your growth companion anytime"
- More personal than web interface

**Technical Approach:**
```python
# We already have the TAF pattern from our research!
from taf import TAFConfig
from taf.core.context import ConversationSession
from taf.tools.memory import create_memory_tools

# Create webhook endpoint for incoming messages
@app.post("/sms-webhook")
async def handle_sms(request: Request):
    # Parse Twilio request
    form_data = await request.form()
    user_message = form_data.get("Body")
    from_number = form_data.get("From")

    # Map phone number to Memora user_id
    user_id = get_user_from_phone(from_number)

    # Use existing orchestrate_chat logic!
    result = orchestrate_chat(user_message)

    # Send response via Twilio
    return TwiML_response(result["messages"])
```

**What we need:**
- Twilio phone number (context: use WhatsApp sandbox to avoid 10DLC)
- Webhook endpoint (FastAPI already has this!)
- Phone number → user_id mapping

**Demo value:**
- "Text LifePath AI from your phone"
- More immersive than web demo
- Shows real-world use case

### 2. Maestro Integration (ENHANCES MULTI-CHANNEL)

**What Maestro adds:**
- Unified conversation management across channels
- Automatic Profile resolution
- Conversation grouping by participant
- Real-time webhooks for events

**Architecture with Maestro:**
```
┌─────────────────────────────────────────────┐
│  Twilio Channels (SMS, Voice, WhatsApp)     │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  Maestro (Conversation Management)           │
│  - Groups messages by participant            │
│  - Resolves Profile ID                       │
│  - Triggers webhooks                         │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  LifePath AI Backend (Your code!)            │
│  - Memory tools (search/store)               │
│  - OpenAI orchestration                      │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  Memora (Memory Storage)                     │
└─────────────────────────────────────────────┘
```

**Setup steps from context.md:**
```bash
# 1. Create default service config
curl -X POST "http://${MAESTRO_URL}/v1/Services//Conversations" \
  -H "I-Twilio-Auth-Account: ${ACCOUNT_SID}"

# 2. Configure callback URL
curl -X PUT "http://${MAESTRO_URL}/v1/Services/comms_service_00000000000000000000000000/Configurations/default" \
  -H "I-Twilio-Auth-Account: ${ACCOUNT_ID}" \
  -d '{
    "conversation_grouping_type": "group_by_participant_addresses",
    "status_callbacks": [{
      "url": "https://your-lifepath-ai.com/maestro-webhook"
    }]
  }'
```

**Benefit for demo:**
- Professional production architecture
- Shows Sierra platform integration
- Multi-channel ready (SMS, voice, WhatsApp all work)

### 3. Voice Integration via ConversationRelay

**Use case:**
- Call LifePath AI on the phone
- Voice-based life coaching
- More emotional/intimate medium

**Technical approach:**
```python
# Voice webhook endpoint
@app.post("/voice-webhook")
async def handle_voice_call(request: Request):
    # ConversationRelay configuration
    response = VoiceResponse()
    response.say("Hello! I'm LifePath AI, your personal growth companion.")

    # Start ConversationRelay with our agent
    connect = Connect()
    connect.conversation_relay(
        url="wss://your-lifepath-ai.com/relay",
        voice="Polly.Joanna"  # Natural-sounding voice
    )
    response.append(connect)

    return str(response)
```

**Demo value:**
- "Call your AI growth companion"
- Voice adds emotional depth
- Natural conversation flow

## 🚀 Recommended Implementation Order

### Phase 1: SMS Integration (2-3 hours)
**Minimal changes to existing code:**
1. Add `/sms-webhook` endpoint to `unified_app.py`
2. Parse Twilio SMS request format
3. Map phone number → user_id
4. Return TwiML response
5. Test with WhatsApp sandbox (no 10DLC needed!)

**Files to modify:**
- `unified_app.py` - Add SMS webhook
- `hackday_run.sh` - Add Twilio credentials
- New: `twilio_sms.py` - SMS handling logic

### Phase 2: Maestro Integration (3-4 hours)
**Adds conversation management:**
1. Register callback URL with Maestro
2. Create `/maestro-webhook` endpoint
3. Parse Maestro conversation events
4. Use Profile ID from Maestro → Memora user_id
5. Test multi-channel (SMS + web)

**Files to modify:**
- `unified_app.py` - Add Maestro webhook
- New: `maestro_client.py` - Maestro API wrapper

### Phase 3: Voice Integration (4-5 hours)
**Most complex, most impressive:**
1. Configure ConversationRelay
2. WebSocket server for real-time audio
3. Speech-to-text integration
4. Text-to-speech for responses
5. Handle conversational flow

## 📝 Code Starter for SMS Integration

Here's a quick implementation you could add:

```python
# Add to unified_app.py

from twilio.twiml.messaging_response import MessagingResponse

# Phone number to user_id mapping (simple version)
PHONE_USER_MAP = {
    "+1234567890": "john",
    "+0987654321": "caroline",
    # Add more mappings
}

@app.post("/sms")
async def handle_sms(request: Request):
    """Handle incoming SMS from Twilio"""
    form_data = await request.form()

    user_message = form_data.get("Body")
    from_number = form_data.get("From")

    # Map phone to user
    user_id = PHONE_USER_MAP.get(from_number, "john")

    # Update MEMORA_USER_ID for this request
    global MEMORA_USER_ID
    original_user = MEMORA_USER_ID
    MEMORA_USER_ID = user_id

    # Use existing orchestration!
    result = orchestrate_chat(user_message)

    # Restore original user
    MEMORA_USER_ID = original_user

    # Create TwiML response
    resp = MessagingResponse()
    for message in result["messages"]:
        resp.message(message)

    return Response(content=str(resp), media_type="application/xml")
```

## 🎬 Demo Scenarios

### SMS Demo:
1. **Setup**: Configure WhatsApp sandbox number
2. **Demo**: Text "What should I do next in life?"
3. **Show**: Tool call logs, memory search
4. **Result**: Personalized SMS response

### Maestro Demo:
1. **Setup**: Register webhook with Maestro
2. **Demo**: Send SMS, show conversation in Maestro UI
3. **Show**: Profile resolution, conversation grouping
4. **Result**: Multi-channel conversation management

### Voice Demo (Advanced):
1. **Setup**: Configure Twilio phone number with voice
2. **Demo**: Call LifePath AI, ask about life direction
3. **Show**: Real-time memory search during call
4. **Result**: Voice-based personal growth conversation

## 📚 Resources from Context

**TAF SDK:**
- Location: `twilio-agentic-framework-python` (you already explored this!)
- Examples: `examples/openai_chat_with_tools.py`

**Maestro API:**
- Dev URL: `http://dev-maestro-domain-us-eas-gw-nlb-ce6d2610dba401ec.elb.us-east-1.amazonaws.com:8000`
- API Spec: https://friendly-adventure-16rng7z.pages.github.io/

**Memora API:**
- You're already using this!
- Mock profile for testing: `mem_profile_00000000000000000000000000`

## ✅ Quick Wins for Tuesday Demo

**If you only have 2-3 hours:**
1. Add SMS webhook endpoint
2. Test with WhatsApp sandbox
3. Show: "Text your LifePath AI from your phone"

**If you have 4-6 hours:**
1. SMS integration (above)
2. Add Maestro callback
3. Show: Multi-channel conversation management

**If you have full day:**
1. SMS + Maestro (above)
2. Add voice with ConversationRelay
3. Show: "Call or text your personal growth companion"

## 🎯 Value Proposition

**For Demo:**
- "LifePath AI works where you are - text, voice, or web"
- "Built on Twilio Sierra platform"
- "Production-ready multi-channel architecture"

**For Product:**
- SMS: Check in with your growth companion throughout the day
- Voice: More intimate, emotional conversations
- Multi-channel: Seamless experience across platforms

## 💡 Next Steps

1. **Decide scope**: SMS only? SMS + Maestro? Voice?
2. **Get Twilio number**: Use WhatsApp sandbox for fastest setup
3. **Implement webhook**: Start with `/sms` endpoint
4. **Test locally**: ngrok for webhook testing
5. **Deploy**: Show live SMS integration in demo

Ready to start? I can help implement any of these phases!
