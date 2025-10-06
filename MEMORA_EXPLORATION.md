# Memora Exploration & Testing

## 🎯 Goal
Verify Memora is working locally and explore the pre-loaded test data before integrating with our conversational agent.

## 📊 What's Already Loaded

**1,000 memories across 8 users:**

| User | Memories | Key Themes |
|------|----------|------------|
| john | 197 (19.7%) | Various life experiences |
| maria | 180 (18.0%) | Personal narratives |
| caroline | 114 (11.4%) | LGBTQ+ advocacy, art, inclusivity |
| melanie | 76 (7.6%) | Family, parenting, pottery |
| gina | 119 (11.9%) | Entrepreneurship, dance, clothing store |
| joanna | 118 (11.8%) | Community support |
| jon | 110 (11.0%) | Various experiences |
| nate | 86 (8.6%) | Life stories |

**Key Topics:**
- LGBTQ+ community & pride events
- Arts (painting, pottery, dance)
- Family activities & camping trips
- Business & entrepreneurship
- Community volunteering
- Personal growth journeys

## 🔍 Exploration Steps

### Step 1: Verify Memora is Running

```bash
# Terminal 1: Start Memora
cd /Users/nlubchenco/dev/src/github.com/github.com/twilio-internal/memora-domain
AWS_PROFILE=memora-dev make dev-start

# Wait for services to start (1-2 minutes)
# Look for: "Started memory-api-server"
```

```bash
# Terminal 2: Check health (direct to memory-api-server, bypassing Kong)
curl http://localhost:8000/health

# Expected: {"status":"ok"} or similar
```

**Note:** Port 8000 is the direct memory-api-server port. Port 80 goes through Kong which may need additional setup.

### Step 2: Check if Test Data is Loaded

```bash
# Get all memories for user "caroline" (LGBTQ+ advocate)
curl -G 'http://localhost:8000/v1/memories' \
  --data-urlencode 'account_id=test-account' \
  --data-urlencode 'service_id=test-service' \
  --data-urlencode 'user_id=caroline' \
  --data-urlencode 'limit=5' \
  --data-urlencode 'include_metadata=true' | jq .

# Expected: Should return 5 memories about Caroline
```

### Step 3: Test Semantic Search

**Query 1: LGBTQ+ Community**
```bash
curl -G 'http://localhost:8000/v1/memories' \
  --data-urlencode 'account_id=test-account' \
  --data-urlencode 'service_id=test-service' \
  --data-urlencode 'user_id=caroline' \
  --data-urlencode 'q=LGBTQ community support' \
  --data-urlencode 'search_type=semantic' \
  --data-urlencode 'limit=3' \
  --data-urlencode 'threshold=0.1' | jq '.memories[] | {text: .text, score: .score}'

# Expected: Memories about LGBTQ advocacy, pride events, community support
```

**Query 2: Art & Creativity**
```bash
curl -G 'http://localhost:8000/v1/memories' \
  --data-urlencode 'account_id=test-account' \
  --data-urlencode 'service_id=test-service' \
  --data-urlencode 'user_id=caroline' \
  --data-urlencode 'q=art painting creativity' \
  --data-urlencode 'search_type=semantic' \
  --data-urlencode 'limit=3' | jq '.memories[] | {text: .text, score: .score}'

# Expected: Memories about Caroline's art, paintings, exhibitions
```

**Query 3: Family Activities**
```bash
curl -G 'http://localhost:8000/v1/memories' \
  --data-urlencode 'account_id=test-account' \
  --data-urlencode 'service_id=test-service' \
  --data-urlencode 'user_id=melanie' \
  --data-urlencode 'q=family camping kids' \
  --data-urlencode 'search_type=hybrid' \
  --data-urlencode 'semantic_weight=0.7' \
  --data-urlencode 'limit=5' | jq '.memories[] | {text: .text, score: .score}'

# Expected: Memories about Melanie's family trips, camping, children
```

### Step 4: Test the Recall Endpoint (Agent-Optimized)

```bash
# Recall endpoint - designed for agentic workloads
curl -X POST 'http://localhost:8000/v1/Services/test-service/Profiles/caroline/Recall' \
  -H 'X-Pre-Auth-Context: test-account' \
  -H 'Content-Type: application/json' \
  -d '{
    "query": "What do you know about LGBTQ advocacy?",
    "longtermLimit": 5,
    "minScore": 0.1
  }' | jq .

# Expected: Top relevant memories about Caroline's LGBTQ work
```

### Step 5: Test Hybrid Search Weights

**Semantic-heavy (0.8):**
```bash
curl -G 'http://localhost:8000/v1/memories' \
  --data-urlencode 'account_id=test-account' \
  --data-urlencode 'service_id=test-service' \
  --data-urlencode 'user_id=gina' \
  --data-urlencode 'q=business entrepreneurship' \
  --data-urlencode 'search_type=hybrid' \
  --data-urlencode 'semantic_weight=0.8' \
  --data-urlencode 'limit=3' | jq '.memories[] | .text'

# Favors semantic meaning over exact keyword matches
```

**Keyword-heavy (0.2):**
```bash
curl -G 'http://localhost:8000/v1/memories' \
  --data-urlencode 'account_id=test-account' \
  --data-urlencode 'service_id=test-service' \
  --data-urlencode 'user_id=gina' \
  --data-urlencode 'q=business entrepreneurship' \
  --data-urlencode 'search_type=hybrid' \
  --data-urlencode 'semantic_weight=0.2' \
  --data-urlencode 'limit=3' | jq '.memories[] | .text'

# Favors exact keyword matches
```

## 📝 Test Queries by Theme

### LGBTQ+ Advocacy (User: caroline)
```bash
# Query 1
curl -X POST 'http://localhost:8000/v1/Services/test-service/Profiles/caroline/Recall' \
  -H 'X-Pre-Auth-Context: test-account' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Tell me about pride events", "longtermLimit": 3, "minScore": 0}' | jq '.memories[].content'

# Query 2
curl -X POST 'http://localhost:8000/v1/Services/test-service/Profiles/caroline/Recall' \
  -H 'X-Pre-Auth-Context: test-account' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Who are you mentoring?", "longtermLimit": 3, "minScore": 0}' | jq '.memories[].content'
```

### Family & Parenting (User: melanie)
```bash
# Query 1
curl -X POST 'http://localhost:8000/v1/Services/test-service/Profiles/melanie/Recall' \
  -H 'X-Pre-Auth-Context: test-account' \
  -H 'Content-Type: application/json' \
  -d '{"query": "What activities do you do with your children?", "longtermLimit": 5, "minScore": 0}' | jq '.memories[].content'

# Query 2
curl -X POST 'http://localhost:8000/v1/Services/test-service/Profiles/melanie/Recall' \
  -H 'X-Pre-Auth-Context: test-account' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Tell me about camping trips", "longtermLimit": 3, "minScore": 0}' | jq '.memories[].content'
```

### Business & Entrepreneurship (User: gina)
```bash
# Query 1
curl -X POST 'http://localhost:8000/v1/Services/test-service/Profiles/gina/Recall' \
  -H 'X-Pre-Auth-Context: test-account' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Tell me about your clothing store", "longtermLimit": 3, "minScore": 0}' | jq '.memories[].content'

# Query 2
curl -X POST 'http://localhost:8000/v1/Services/test-service/Profiles/gina/Recall' \
  -H 'X-Pre-Auth-Context: test-account' \
  -H 'Content-Type: application/json' \
  -d '{"query": "What kind of dance do you do?", "longtermLimit": 3, "minScore": 0}' | jq '.memories[].content'
```

### Arts & Creativity (Multi-user)
```bash
# Caroline's art
curl -X POST 'http://localhost:8000/v1/Services/test-service/Profiles/caroline/Recall' \
  -H 'X-Pre-Auth-Context: test-account' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Describe your artwork", "longtermLimit": 3, "minScore": 0}' | jq '.memories[].content'

# Melanie's pottery
curl -X POST 'http://localhost:8000/v1/Services/test-service/Profiles/melanie/Recall' \
  -H 'X-Pre-Auth-Context: test-account' \
  -H 'Content-Type: application/json' \
  -d '{"query": "Tell me about your pottery projects", "longtermLimit": 3, "minScore": 0}' | jq '.memories[].content'
```

## ✅ Success Checklist

After running these tests, you should be able to confirm:

- [ ] Memora services are running (health endpoint responds)
- [ ] Test data is loaded (can retrieve memories for users)
- [ ] Semantic search works (finds relevant memories by meaning)
- [ ] Hybrid search works (combines keywords + semantics)
- [ ] Recall endpoint works (agent-optimized retrieval)
- [ ] Different users have different memory profiles
- [ ] Search scores reflect relevance

## 🎬 Demo Script Ideas

Based on test data, here are compelling demo scenarios:

### Scenario 1: "Ask Caroline About Her Work"
```
Agent Query: "What do you do for the LGBTQ community?"
Memora Recalls: Pride events, mentoring transgender teen, advocacy art
Agent Response: [Enriched with Caroline's actual memories]
```

### Scenario 2: "Ask Melanie About Family"
```
Agent Query: "What are your favorite family memories?"
Memora Recalls: Camping trips, children's milestones, beach visits
Agent Response: [Personalized with Melanie's experiences]
```

### Scenario 3: "Ask Gina for Business Advice"
```
Agent Query: "How did you start your business?"
Memora Recalls: Clothing store launch, ad campaign, challenges
Agent Response: [Context from Gina's entrepreneur journey]
```

## 🔧 Troubleshooting

### If no memories are returned:
```bash
# Check if data is loaded
curl -G 'http://localhost:8000/v1/memories' \
  --data-urlencode 'account_id=test-account' \
  --data-urlencode 'service_id=test-service' \
  --data-urlencode 'limit=1' | jq .

# If empty, load the test data:
cd /Users/nlubchenco/dev/src/github.com/github.com/twilio-internal/memora-domain/services/memory-service
make local-index-create
# Then run the data loading script from memory-service docs
```

### If Memora isn't starting:
```bash
# Check logs
cd /Users/nlubchenco/dev/src/github.com/github.com/twilio-internal/memora-domain
make dev-logs-api

# Restart services
make dev-stop
AWS_PROFILE=memora-dev make dev-start
```

## 📊 Next Steps After Exploration

Once you've confirmed Memora is working and explored the data:

1. **Choose a demo persona** (Caroline, Melanie, or Gina)
2. **Design conversation flows** that leverage their memories
3. **Integrate Recall endpoint** into the agent's orchestration
4. **Show before/after** - agent without memory vs with Memora
5. **Demonstrate search quality** - semantic understanding of user intent

## 🎯 Key Insights for Integration

From exploration, note:
- **Best user profiles**: Caroline (114 memories, rich LGBTQ+ advocacy), John (197 memories)
- **Recall endpoint**: Best for agent integration (optimized for agentic workloads)
- **Search types**: Hybrid with semantic_weight=0.7 gives good balance
- **Score thresholds**: minScore=0.1 filters low-relevance results
- **Context window**: 3-5 memories is good for agent context (not too much, not too little)

---

**Ready to explore?** Start with Step 1 and work through the queries. Save interesting results to show in your demo!
