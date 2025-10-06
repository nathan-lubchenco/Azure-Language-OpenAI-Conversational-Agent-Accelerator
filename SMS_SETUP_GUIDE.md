# SMS Integration Setup Guide

## 🎉 You've Got SMS Working!

LifePath AI now responds to SMS messages using your Twilio number: **+1 (513) 935-3686**

## 🚀 Quick Setup (5 minutes)

### Step 1: Install Dependencies

```bash
cd src/backend
pip install twilio python-multipart
```

### Step 2: Install ngrok (for local testing)

```bash
# Mac
brew install ngrok

# Or download from: https://ngrok.com/download
```

### Step 3: Start ngrok

```bash
# In a separate terminal
ngrok http 7000
```

You'll see output like:
```
Forwarding    https://abc123.ngrok.io -> http://localhost:7000
```

**Copy that `https://abc123.ngrok.io` URL!**

### Step 4: Configure Twilio

1. Go to [Twilio Console](https://console.twilio.com/us1/develop/phone-numbers/manage/incoming)
2. Click on your number: **+1 (513) 935-3686**
3. Scroll to "Messaging Configuration"
4. Under "A MESSAGE COMES IN":
   - **Webhook**: `https://abc123.ngrok.io/sms` (your ngrok URL + `/sms`)
   - **HTTP POST**
5. Click **Save**

### Step 5: Test It!

Send a text to **+1 (513) 935-3686**:
```
What should I do next in life?
```

You should see:
- 📱 SMS activity in your terminal
- 🔍 Tool calls being made
- 💬 Personalized response via SMS!

## 📱 How It Works

```
┌─────────────────────────────────────────────┐
│  User sends SMS to +1 (513) 935-3686        │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  Twilio receives SMS                         │
│  Sends webhook to your ngrok URL            │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  ngrok forwards to localhost:7000/sms       │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  LifePath AI Backend                         │
│  1. Maps phone → user (you = john)          │
│  2. Uses orchestrate_chat (same as web!)    │
│  3. Searches memories with tools            │
│  4. Returns TwiML response                   │
└─────────────────┬───────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  Twilio sends SMS back to user              │
└─────────────────────────────────────────────┘
```

## 🎯 Phone Number Mapping

Your phone number is mapped to user `john` (who has 197 memories):

```python
# In unified_app.py
PHONE_USER_MAP = {
    "+15139353686": "john",  # Your number!
    "+11234567890": "caroline",  # Example: other users
    "+19876543210": "melanie",
}
```

To test different personas, update the mapping and restart the server.

## 🧪 Test Scenarios

### Scenario 1: Life Direction
```
Text: "What should I do next in life?"
Expected: Tool call to search_memories, personalized response
```

### Scenario 2: Emotional Statement
```
Text: "This is making me sad about Max"
Expected: Tool call to search Max memories, empathetic response
```

### Scenario 3: Simple Question (No Tools)
```
Text: "What's 2 + 2?"
Expected: Direct answer "4", no tool calls
```

### Scenario 4: Share New Info
```
Text: "I just completed a mental health workshop"
Expected: Tool call to store_memory, confirmation
```

## 🔍 Debugging

### Terminal Output
Watch your terminal for these lines:
```
📱 SMS RECEIVED
From: +15139353686
Message: What should I do next in life?
📱 Mapped +15139353686 → user: john
📱 Using memory for: john
🔧 Tool calls made: ['search_memories']
📱 SMS RESPONSE SENT
```

### ngrok Web Interface
Open http://127.0.0.1:4040 to see:
- All HTTP requests
- Request/response details
- Useful for debugging!

### Common Issues

**"Webhook not receiving requests"**
- Check ngrok is running
- Verify Twilio webhook URL is correct (include `/sms`)
- Make sure it's HTTPS (ngrok provides this)

**"No tool calls happening"**
- Check backend terminal for errors
- Verify MEMORA_ENABLED=true
- Check Memora is running on port 8000

**"Wrong user's memories"**
- Check PHONE_USER_MAP in unified_app.py
- Phone number must include country code: +1...

## 🎬 Demo Tips

### Before Demo:
1. Start Memora
2. Start backend with `./hackday_run.sh`
3. Start ngrok: `ngrok http 7000`
4. Configure Twilio webhook
5. Send test SMS to verify

### During Demo:
1. Show web interface still works
2. Send SMS from your phone
3. Show terminal with tool calls
4. Show SMS response on phone
5. Explain: "Same AI, multiple channels"

### Cool Demo Flow:
```
You: [Show web interface]
     "This is LifePath AI on the web"

You: [Send SMS from phone]
     "What should I do next in life?"

You: [Show terminal]
     "Watch it search my memories..."
     [Point out tool calls]

You: [Show phone]
     "Personalized response via SMS!"

You: "Same backend, same memory tools, different interface"
```

## 📊 What's Working

- ✅ SMS receives messages
- ✅ Maps your number to john's memories
- ✅ Uses existing orchestrate_chat logic
- ✅ Tool calls work (search_memories, store_memory)
- ✅ Returns SMS responses
- ✅ Web interface still works independently
- ✅ Different users can have different memories

## 🔧 Advanced: Multiple Users

To support multiple people texting:

```python
# Update PHONE_USER_MAP in unified_app.py
PHONE_USER_MAP = {
    "+15139353686": "john",          # You
    "+14155551234": "caroline",      # Friend 1
    "+14085559876": "melanie",       # Friend 2
}
```

Each person gets their own memory profile!

## 🚀 Next Steps

**Working SMS** = ✅ Done!

**Want to add:**
- WhatsApp (use Twilio sandbox, same code works!)
- MMS (images in/out)
- Maestro integration (conversation management)
- Voice (8+ hours more work)

## 🎉 You're Live!

Text **+1 (513) 935-3686** right now and try:
- "What should I do next in life?"
- "Tell me about my goals"
- "This makes me think of Max"

Your LifePath AI is now multi-channel! 🌟
