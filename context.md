Goal:

Invite R&D cohorts to gain and share experiences of building agents. 

The motivation is for Sierra PM + ENG to learn/understand the customer experience of building agents to use them with the capabilities being developed under Project Sierra.

Who: 
The core group will be Architects, Product Managers and Engineering Leaders including EMs and Engineers. Preference will be given to those working on Project Sierra but the hack day is open to broader R&D groups as well

The core group will be limited to 15 Twilions.

When:
Hack Day - Monday Oct 06 [9.00am until 5.00pm] PST
Show and tell experiences - Tuesday Oct 07 [9.00am until noon PST]

Agenda: All times in PST

Monday Oct 06
09:00-09:45am: Introductions, walk through basic scenarios on all 3 platforms
10:00-12:00: Breakout for each group to work on their own [Support team will be available]
12:00-12:30: Group check-in [Zoom meeting ] Big room for in person
12.30-13:30: Lunch
13:30-16:30: Breakout for each group to work on their own [Support team will be available]
16:30-17:00: Group check-in [Zoom meeting ] Big room for in person


Tuesday Oct 07 [Zoom meeting ] Big room for in person
09:00-09:45am: Group 1 share and tell learning
10:00-10:45am: Group 2 share and tell learning
11:00-11:45am: Group 3 share and tell learning
12:00-12:30: Group wrap-up


Where: 
SF Office - If you are local, join in the office
Virtual attendance will be supported

How:
There will be 3 core squads (+1 specialized Maestro squad) - one for each Agentic AI platform (OpenAI, Bedrock, Foundry)
Each squad will have a leader who will play a role of an expert to provide as much support as possible (bear in mind that everyone is learning)
The core squad would be 3-5 Twilions. 
Folks can work solo or in groups but the share and tell will be per squad, not individuals. 
Each squad will have core [P0] use cases to be completed within the hack day
Each squad will have 1 hour to share their experiences on Tuesday
Bonus points for additional use cases

Besides the core squads, if there is additional interest, we will form squads to work in parallel with each of the core squads.

What are we building:
[P0] Use case A: Build an agent using one of the 3 frameworks
Create an agent with an operator (e.g. summarize a blob of text)
Provide this agent with knowledge
Setup tools for the agent
Setup memory for the agent
Deploy the agent and run it through a few examples
[P0] Use case B: Setup Agent <-> Twilio integrations (CPaaS layer)
Procure a Twilio toll-free PN (anyone needing toll-free number registration approval, please add your details to this sheet)
Connect up the agent to listen to incoming voice calls, configure and connect the ConversationRelay, listen for prompt, answer question about Sierra PRFAQ and send that answer through the ConversationRelay
Bonus points for SMS, MMS and RCS integrations
In dev env choose to work on SMS since there are challenges with voice (you cannot receive voice calls) 
[P0] Use case C: Setup Agent <-> Twilio integrations using TAF (+CPaaS layer)
Procure a Twilio PN (anyone needing toll-free number registration, please add your details to this sheet after completing the verification forms in console)
Alternative: use whatsapp in sandbox mode to avoid 10dlc
Log in 
Connect up the agent to listen to incoming voice call and respond back - but this time using the TAF SDK
Bonus points for Messaging integrations
[P1] Use case D:
Use case C + call Maestro API to start a conversation
[P1] Use case E:
Use case C + call Memora API 

Attendee preparations/next steps:
Each attendee will sign up here by Oct 01 EOD
Each participant would have completed the prerequisites (Step 1 and Step 2 below)  before the hack day
Preqs will be shared by Tuesday Sept 30 EOD
Active participation is required (hands on code/claude code)
Feature flags:
Account flag “sierra-enabled” is required (DEV only) 
This enables passive Conversation creation from delivered Messages
The account flag needs to be set in DEV OneAdmin
Watch the exec connect demo video to see how AI Agents will use Sierra
Start at 7:30 and watch until 17:00


Step 1: How to get access to your Agent Platform:
OpenAI
Make an application access request in service now
Once approved, available through Okta Tile
Bedrock
Submit PR to https://github.com/twilio-internal/cnd-account-factory to create a sandbox AWS account. See this thread for an example and additional documentation
Request Administrator permissions to your AWS sandbox account within the SNOW JIT request. Follow the steps in AWS JIT Access
Example of building an agent
https://github.com/twilio-internal/sierra-example-agents/pull/1
Foundry
Install VS Code - a lot of MSFT tools leverage VSCode
Pull down this repo: https://github.com/Azure-Samples/get-started-with-ai-agents
Make an application access request in service now:
Organization: Twilio
Application: Azure-AI-DEV (we are going to use Dev not prod)
Type: I need new access
Business use case: Sierra Oct 6th hack day
Once approved, enter your twilio email at https://portal.azure.com/
You may be prompted to setup 2FA for your account before getting access to the portal
Go to Azure AI Foundry in the UI to get started

Step 2: Have a Twilio PN for Voice and SMS
With your Twilio account (Prod and/or Dev), have a PN ready that you can use. 
In case you need a Toll-free number it will need registration and verification. Make sure to complete the needed details on the registration form in the console and please add the number here for the expedited approvals
Step 3: Get familiar with TAF (Twilio internal GIT access)
 SDK

Step 4: Get familiar with Maestro APIs (dev env only - will need ZScaler access)
API spec: https://friendly-adventure-16rng7z.pages.github.io/ 
Dev URL: http://dev-maestro-domain-us-eas-gw-nlb-ce6d2610dba401ec.elb.us-east-1.amazonaws.com:8000  
Alternative VPC endpoint: http://vpce-04bdbf2e138c919dd-uz9fqb3d.vpce-svc-05b176ae3352b17b6.us-east-1.vpce.amazonaws.com:8000/ 
Important Notes:
All Conversations and Communications will resolve to a mock profile of mem_profile_00000000000000000000000000. This is due to Memora running locally and Maestro being unable to resolve a real Profile. Memora will seed their database with memories using this mock profile ID. So you can use this freely when accessing Memora APIs. 
Steps to start using Maesto
Configure a Callback Url for Conversation events - as of the Hack Day, only a system generated ‘default’ service configuration will enable Callback invocations.  As a result, you will need to make the following sequence of Maestro API calls to property register your Callback Url:
Check to see if the ‘default’ Service Configuration already exists - this step is optional but you can use it at any time to verify your Service Configuration:

curl -X GET "http://${MAESTRO_URL}/v1/Services//Configurations/default" \
    -H "I-Twilio-Auth-Account: {{AccountSid}}"


Create a dummy Conversation - If above call returns a 404 (Not Found) then you will need to create a (dummy) Conversation to trigger the creation of the default Service Configuration:

curl -X POST "http://${MAESTRO_URL}/v1/Services//Conversations" \
    -H "I-Twilio-Auth-Account: {{AccountSid}}" \
    -H "Content-Type: application/json" \
    -d '{
          "name": "Sample Conversation to trigger default service configuration creation"
        }'


Add your Callback Url - Once the default Service Configuration exists you can then update it to include your Callback Url:
curl -X PUT "http://${MAESTRO_URL}/v1/Services/comms_service_00000000000000000000000000/Configurations/default" \
  -H "I-Twilio-Auth-Account: ${ACCOUNT_ID}" \
  -H "Content-Type: application/json" \
  -d '{
    "friendly_name": ${SERVICE_NAME},
    "conversation_grouping_type": "group_by_participant_addresses",
    "status_callbacks": [
      {
        "url": `${MY_WEBHOOK_URL}`,
        "method": "POST",
        "headers": {
          "Authorization": `Bearer ${TOKEN_ID}`
        },
        "cookies": {
          "updated_session": `${SESSION_ID}`
        }
      }
    ]
  }'

Test the Callback - POST some update to the Conversation created above to (or create a new one).  This will trigger a call to your Callback Url


Step 5: Get familiar with Memora APIs (running against Kiran Vaddey’s local service that is publicly available through ngrok)
Long Term: Memora maintains long term memory for user profiles across conversations. There are 3 types of long term memory: observations, summaries, and traits. Eventually, Conversational Intelligence operators will extract observations from conversations, and these will be stored in a vector db. Consumers will have access to these memories during subsequent conversations via Memora’s Recall endpoint which performs hybrid search over the vector db.
Current State: Memora is not present in dev yet, so the ngrok endpoint will need to be used to access Memora: https://kiran.ngrok.io. A couple observations around mock Aritzia support cases have been pre-seeded into the service. You have access to the Recall endpoint to extract these memories, and can use the  Index endpoint below to create new mock observations.


https://memora-domain-api.internal-pages.twilio.com/
A few mock observations from Aritizia customer support have  already been pre-seeded into the service
Profile/User ID: see profile ids here or use mem_profile_00000000000000000000000000
Account ID: account_00000000000000000000000000
Service ID: mem_service_00000000000000000000000000



Try the recall endpoint

curl -X POST https://kiran.ngrok.io/v1/Services/mem_service_00000000000000000000000000/Profiles/mem_profile_00000000000000000000000000/Recall \
  -H "Content-Type: application/json" \
  -H "X-Pre-Auth-Context: account_00000000000000000000000000" \
  -d '{
"query": "I would like to return my previous order",
"longtermLimit": 3,
"minScore": 0}' | jq

Create your own observations


curl -X POST https://kiran.ngrok.io/v1/memories \
  -H "Content-Type: application/json" \
  -d '{
    "id": "<generate a random id>",
    "text": "<observation text here>",
    "account_id": "account_00000000000000000000000000",
    "service_id": "mem_service_00000000000000000000000000",
    "user_id": "mem_profile_<your name>",
    "conversation_id": "conv456"
  }'



Step 6: Think of the use cases that you like to build and start hacking



Know your squad leaders:
Squad Leader 1: OpenAI Andrew Hitti
Squad Leader 2: Azure Foundry Vinnie Giarrusso
Squad Leader 3: Bedrock Peter Janovsky
Squad Leader 4: TAF <> Maestro (Special Group) Andrew Severson
Oct 6 Hack Day Squad 4

Logistics for Day1:

Office: Please come to SF-5F-Jenga-HackableSpace-ZM (44) for common meetings - 9am, 12noon, 4.30pm
Remote: Please join the main zoom meeting for common meetings -  9am, 12noon, 4.30pm


Rooms:
Main room:SF-5F-Jenga-HackableSpace-ZM (44)
Squad 1: SF-5F-Minion-ZM (12)
Squad 2: SF-5F-Soren-ZM (10)
Squad 3: SF-5F-Tawny Owl-ZM (9)
Squad 4: SF-5F-Chess-HackableSpace-ZM (8)

Zoom breakout rooms:
Squad 1: Breakout room 1
Squad 2: Breakout room 2
Squad 3: Breakout room 3
Squad 4: Breakout room 4





FAQs:
Will I need to be hands-on coding?

While many parts of agent building could be done through clicks and configurations, to deploy and run, you will need some hands on coding. But don’t let this stop you from participating. Partner with someone from engineering

What if I want to try other scenarios?

As long as you have exercised the core P0 scenarios, you can bring your own scripts to leverage Sierra platform capabilities (Maestro/Memora/CIntel/TAF) APIs and build

Points/bonus points are mentioned. What do these mean?

Groups/individuals who bring the best learnings forward will get bragging rights for customer obsession.



Appendix:

OpenAI Agents

Pre-reqs:
Create an API Key
Install brew:
 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"


Install >=Python3.9, use PyEnv recommended
Install uv:
pip install uv or brew install uv
UV Installation Instructions
Virtualenv is okay


SDK documentation: OpenAI Agents SDK
Get Started docs



