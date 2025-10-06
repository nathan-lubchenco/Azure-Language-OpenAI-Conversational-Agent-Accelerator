#!/bin/bash
# HACKDAY: Demo script showing Memora integration

echo "🎬 Memora Integration Demo"
echo "=========================="
echo ""
echo "This demo shows the agent recalling Caroline's memories about LGBTQ advocacy."
echo ""

# Test queries that should trigger memory recall
QUERIES=(
    "Tell me about pride events"
    "Who are you mentoring?"
    "What kind of art do you create?"
    "Tell me about your community work"
)

echo "📝 Running ${#QUERIES[@]} test queries..."
echo ""

for query in "${QUERIES[@]}"; do
    echo "───────────────────────────────────────────────────────────"
    echo "Query: $query"
    echo "───────────────────────────────────────────────────────────"

    response=$(curl -s -X POST http://127.0.0.1:7000/chat \
        -H "Content-Type: application/json" \
        -d "{\"message\": \"$query\"}")

    echo "$response" | jq -r '.messages[]'
    echo ""
    sleep 1
done

echo "✅ Demo complete!"
echo ""
echo "💡 Check the server terminal to see:"
echo "   - Memories recalled from Memora"
echo "   - Enriched context added to queries"
echo "   - New interactions stored back to Memora"
echo ""
echo "📊 View logs with: python view_logs.py"
