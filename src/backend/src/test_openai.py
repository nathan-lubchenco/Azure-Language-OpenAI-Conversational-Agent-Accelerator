#!/usr/bin/env python3
"""Quick test to see if OpenAI client is working"""

import os
from aoai_client import AOAIClient

print("Testing OpenAI client...")
print(f"OPENAI_API_KEY set: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No'}")

try:
    # Create client
    print("\n1. Creating client...")
    client = AOAIClient(
        deployment="gpt-4o-mini",
        system_message="You are a helpful assistant."
    )
    print("✅ Client created successfully")

    # Test chat completion
    print("\n2. Testing chat completion...")
    response = client.chat_completion("Say 'Hello world' and nothing else.")
    print(f"✅ Got response: {response}")

    print("\n✅ All tests passed!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
