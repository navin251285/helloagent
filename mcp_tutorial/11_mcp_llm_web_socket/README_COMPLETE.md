# Patient Summary Assistant - Complete Documentation

## 🏥 What Does This Application Do? (Simple Explanation)

Imagine you're a doctor with 100 patients. You want to:

1. **Find patients** with specific conditions (like "diabetes" or "high blood pressure")
2. **Generate smart summaries** of each patient's medical profile automatically using AI
3. **Save those summaries** to a database for future reference
4. **Track everything** that happens - what you search for, how long it takes, what the AI generates

This application does exactly that! It's like having an intelligent medical assistant that:
- 🔍 **Searches** through patient databases instantly
- 🤖 **Writes** professional medical summaries using AI
- 💾 **Saves** everything automatically
- 📊 **Records** every step so you see exactly what happened and how long it took

---

## ⚡ Quick Start

### Prerequisites
```bash
# Python 3.8+
# Ollama running locally (for LLM)
# ChromaDB already initialized with patient data
```

### Start the Server
```bash
cd /home/navinkumar_25_gmail_com/mcp_tutorial/11_mcp_llm_web_socket
python mcp_server.py
```

Server starts on: `ws://127.0.0.1:8765/mcp` (WebSocket)

### Use the Interactive Client (in another terminal)
```bash
python mcp_client.py
```

Then try these commands:
```
search_patients_by_disease diabetes
generate_summary 25
update_summary 25
list_patients
clear_data
```

---

## 📋 How to Use the Application

### Command 1: Search for Patients by Disease
```bash
> search_patients_by_disease diabetes

Output:
[RESULTS]
Found 5 patients with diabetes:
  - Patient 11: Jerry Rivera (Risk Score: 6.6)
  - Patient 45: Janet Torres (Risk Score: 7.2)
  ... (and more)
```

This searches through all patient health records and finds ones matching your keyword.

### Command 2: Generate AI Summary for a Patient
```bash
> generate_summary 25

Output:
[PROCESSING]
Connecting to Ollama AI model...
Generating summary for Janet Lee (ID: 25)...
✓ Summary generated (1,234 characters, 247 tokens)

Generated Summary:
"Based on Janet Lee's medical history and current symptoms of numbness in limbs..."
```

The AI reads patient health data and writes a professional medical summary.

### Command 3: Save Summary to Database
```bash
> update_summary 25

Output:
[SAVING]
Reading patient record for ID: 25...
Writing summary to patient_summaries.csv...
✓ Summary saved successfully
```

Stores the generated summary in the patient database.

### Command 4: View All Patients
```bash
> list_patients

Output:
ID  | Name                | Summary Length
----|------------------|----------------
1   | Justin Cox       | (empty)
2   | Heather Baker    | (empty)
25  | Janet Lee        | 487 characters
...
```

### Command 5: Monitor All Activity
```bash
> view_messages

Output:
[Messages Logged]
Total: 47 messages

Recent Activity:
- tool_call_start (server_process)
- chroma_search (chroma_db) - Duration: 358ms
- ollama_stream_complete (ollama) - Duration: 12,456ms
- csv_write (csv_operation) - Duration: 45ms
- tool_call_complete (server_process)
```

See exactly what happened behind the scenes with timing.

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     YOUR COMMAND (Interactive Client)           │
│                    python mcp_client.py                         │
│              "search_patients_by_disease diabetes"              │
└────────┬────────────────────────────────────────────────────────┘
         │
         │ JSON-RPC over WebSocket
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP SERVER (mcp_server.py)                   │
│         ┌─────────────────────────────────────────────┐         │
│         │   Message Tracking System (Event Logger)    │         │
│         │  Logs every action with timestamps & IDs    │         │
│         └─────────────────────────────────────────────┘         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              REQUEST PROCESSING PIPELINE                │  │
│  │                                                          │  │
│  │  1️⃣ RECEIVE                                             │  │
│  │  ├─ Client WebSocket message received                   │  │
│  │  ├─ Message logged with unique ID & correlation ID      │  │
│  │  └─ Action identified (search/generate/update)          │  │
│  │                                                          │  │
│  │  2️⃣ SEARCH (if needed)                                  │  │
│  │  ├─ Query sent to ChromaDB                              │  │
│  │  ├─ Vector similarity search finds matching patients    │  │
│  │  ├─ Results returned with timestamps                    │  │
│  │  └─ Search log entry added with duration (e.g., 358ms)  │  │
│  │                                                          │  │
│  │  3️⃣ AI GENERATION (if needed)                           │  │
│  │  ├─ Patient health data prepared                        │  │
│  │  ├─ Request sent to local Ollama model                  │  │
│  │  ├─ AI generates medical summary token-by-token         │  │
│  │  ├─ Stream received with progress updates               │  │
│  │  └─ Generation log entry added with duration, token count│ │
│  │                                                          │  │
│  │  4️⃣ DATABASE SAVE (if needed)                           │  │
│  │  ├─ CSV file read to get patient record                 │  │
│  │  ├─ Summary field updated                               │  │
│  │  ├─ CSV file written back to disk                       │  │
│  │  └─ Save log entry added                                │  │
│  │                                                          │  │
│  │  5️⃣ SEND RESPONSE                                       │  │
│  │  ├─ Results packaged as JSON-RPC response               │  │
│  │  ├─ Sent back to client via WebSocket                   │  │
│  │  ├─ Response log entry added                            │  │
│  │  └─ Total request duration recorded                     │  │
│  │                                                          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         │
         │ WebSocket Response
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   DATA STORAGE & EXTERNAL SERVICES              │
│                                                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌─────────────┐  │
│  │   ChromaDB       │  │   Ollama (AI)    │  │ CSV Files   │  │
│  │ (Vector Database)│  │ (LLM Language)   │  │ (Database)  │  │
│  │                  │  │ (Model)          │  │             │  │
│  │ • 356 patient    │  │ • Phi 2.7B Model │  │ • patients_ │  │
│  │   health profiles│  │ • Runs locally   │  │   data.csv  │  │
│  │ • 100 patients   │  │ • ~30-60s per    │  │ • patient_  │  │
│  │ • Vector search  │  │   summary        │  │   summaries │  │
│  │ • ~358ms lookup  │  │                  │  │   .csv      │  │
│  └──────────────────┘  └──────────────────┘  └─────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
         │
         │ Real-time Query
         ▼
┌─────────────────────────────────────────────────────────────────┐
│              MESSAGE TRACKING API (REST Endpoints)              │
│                  View logs & analytics                          │
│                                                                 │
│  GET /api/messages/              - All logged messages          │
│  GET /api/messages/recent?count=10 - Last N messages          │
│  GET /api/messages/patient/{id}  - Messages for patient        │
│  GET /api/messages/type/{type}   - Messages by type            │
│  GET /api/stats                  - System statistics           │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔑 Key Concepts Explained

### 1. Message Passing Protocol (MCP) 🔄

**What it is:**
MCP is a standard way for applications to talk to each other using structured messages. Think of it like a formal letter format that both sides understand.

**In this app:**
- Client sends: `{"method": "search_patients_by_disease", "params": {"disease_keyword": "diabetes"}}`
- Server responds: `{"result": {"patients": [...], "count": 5}}`
- Every message has an ID so you know which response goes with which request

**Why we use it:**
- Standard communication protocol
- Works over any transport (WebSocket, stdio, HTTP)
- Easy to extend with new methods
- Built-in error handling

**Example Flow:**
```
CLIENT                           SERVER
  │                               │
  │─ {"id": 1, "method":         │
  │   "search_patients.."}─────→  │
  │                         Process request
  │                         Search database
  │                         ✓ Found 5 patients
  │  ← {"id": 1, "result":      │
  │     {"patients": [...]}}     │
  │                               │
```

---

### 2. WebSocket Communication 📡

**What it is:**
WebSocket is a technology that keeps a continuous connection open between your computer and the server, like a phone line. You don't have to hang up and call back for each question.

**Traditional HTTP (old way):**
```
Ask → Wait for answer → Hang up → Ask again → Wait → Hang up
```

**WebSocket (this app):**
```
Connect once → Ask → Get answer → Ask again → Get answer
(Connection stays open)
```

**In this app:**
- Client connects: `ws://127.0.0.1:8765/mcp`
- Stays connected while you use the app
- Much faster for multiple operations
- Perfect for streaming AI responses

**Benefits:**
- 🚀 Faster - no connection overhead for each request
- 🔄 Real-time - server can send updates anytime
- 💬 Streaming - AI can send summary word-by-word
- 📊 Monitoring - message tracking works seamlessly

**Example:**
```
[1] Connect → WebSocket open
[2] User: "search_patients_by_disease diabetes"
    → Sent over WebSocket
    → Server processes (358ms)
    → Results streamed back immediately
[3] User: "generate_summary 25"
    → Sent over WebSocket (connection still open!)
    → Server sends AI response token-by-token
    → You see it appearing in real-time
[4] User: "update_summary 25"
    → Sent over WebSocket
    → Saved and confirmed
[5] Disconnect → WebSocket closes
```

---

### 3. RAG: Retrieval Augmented Generation 🧠

**What it is:**
RAG means: Get relevant information from a database → Feed it to AI → Let AI write something smart

**Traditional AI (no RAG):**
```
"Summarize patient 25"
→ AI doesn't know who patient 25 is
→ Makes up generic summary ❌
```

**With RAG (this app):**
```
User asks: "Summarize patient 25"
   ↓
Retrieve: Look up patient 25 data from database
   ├─ Name: Janet Lee
   ├─ Age: 45
   ├─ Symptoms: numbness in limbs, swelling
   ├─ BP: 150/94
   ├─ Blood sugar: 85 mg/dL
   ├─ Medications: (list)
   ↓
Augment: Add this real data to AI request
   ↓
Generate: AI reads all this info and writes smart summary
   ├─ Identifies risk factors
   ├─ Suggests follow-ups
   ├─ Makes professional recommendation ✅
```

**In our system:**
1. User searches disease → Found patients from Chroma DB
2. User picks one patient → System retrieves their health data from CSV files
3. System sends ALL patient data to Ollama → AI generates accurate summary
4. Summary saved to database

**Why it's powerful:**
- AI uses real data, not imagination
- Summaries are accurate and personalized
- Catches patterns human might miss
- Professional quality output

---

### 4. Chroma DB Vector Search 🔍

**What it is:**
Instead of searching for exact matches ("diabetes" = "diabetes"), Chroma converts medical text to numbers (vectors) and finds similar meanings.

**Traditional Search (text matching):**
```
Search: "diabetes"
Matches: Only records with word "diabetes"
Misses: "high blood sugar" (same thing, different words) ❌
```

**Vector Search (this app):**
```
Search: "diabetes"
Converts to: [0.2, 0.8, 0.1, 0.9, ...] (mathematical representation)
Finds: All similar records including:
  ✓ "diabetes"
  ✓ "high blood sugar"
  ✓ "glucose management"
  ✓ "insulin therapy"
```

**How it works in our app:**
```
1. Patient health data loaded → "diabetes, high BP, glucose 208 mg/dL"
2. Chroma AI converts to vector → [0.234, 0.891, 0.456, ...]
3. User searches "diabetes" → Also converts to vector
4. Chroma finds similar vectors → Returns matching patients
5. Results: 5 patients with diabetes-related conditions
```

**Speed:**
- 356 patient profiles
- Searches complete in ~358ms
- Much faster than reading all records

**Use case:**
```
search_patients_by_disease "high blood pressure"
↓
Chroma finds:
  ✓ Hypertension patients
  ✓ Elevated BP patients
  ✓ Cardiovascular disease patients
```

---

### 5. Asynchronous (Async) Communication ⏳

**What it is:**
Instead of waiting for one thing to finish before starting the next, you can start multiple things and wait for all to finish. Like ordering multiple items at a restaurant instead of waiting for each one individually.

**Synchronous (old way - blocking):**
```
1. Search Chroma DB → Wait 358ms ⏳
2. NOW generate with Ollama → Wait 30,000ms ⏳
3. NOW save to CSV → Wait 45ms ⏳
Total: ~30,400ms (30 seconds) 🐌
```

**Asynchronous (this app - non-blocking):**
```
1. Start Chroma search
2. Start Ollama generation (while searching!)
3. Start CSV save (could happen anytime!)
4. Total: ~30,000ms but more efficient 🚀
```

**In our code:**
```python
# Async allows things to happen concurrently
async def websocket_endpoint(websocket):
    while True:
        # Don't block waiting for client message
        # Can handle other clients meanwhile
        message = await websocket.receive_text()
        
        # Don't block waiting for database response
        # Server stays responsive
        results = await search_chroma(query)
        
        # Don't block waiting for AI response
        # Can stream back intermediate results
        summary = await generate_with_ollama(data)

# Key word: "await" = "wait here without blocking others"
```

**Benefits:**
- ⚡ Handle multiple users at once
- 🔄 Server stays responsive
- 📊 Can start next operation while current one running
- 🎯 Stream results as they arrive

---

### 6. REST API for Monitoring 📊

**What it is:**
REST is a way to get information using simple web URLs. Like visiting a website - you get data back.

**In this app - Message Tracking API:**

```
GET /api/messages/
├─ Returns: All logged messages
├─ Count: How many messages total
└─ Use: Overview of all activity

GET /api/messages/recent?count=10
├─ Returns: Last 10 messages
├─ Shows: Most recent activity
└─ Use: What just happened?

GET /api/messages/patient/25
├─ Returns: All messages for patient 25
├─ Shows: Everything done for that patient
└─ Use: Patient-specific audit trail

GET /api/messages/type/tool_call_complete
├─ Returns: Only completed tool calls
├─ Shows: What operations finished
└─ Use: Success/failure analysis

GET /api/stats
├─ Returns: System statistics
├─ Shows: Total messages, time spent, data throughput
└─ Use: System health check
```

**Example queries you can run:**

```bash
# See all activity
curl http://localhost:8765/api/messages/ | jq

# See last 5 actions
curl http://localhost:8765/api/messages/recent?count=5 | jq

# See what happened for patient 25
curl http://localhost:8765/api/messages/patient/25 | jq '.messages[] | {type, duration}'

# See how many searches were done
curl http://localhost:8765/api/messages/type/chroma_search | jq '.count'

# See system stats
curl http://localhost:8765/api/stats | jq
```

**Typical Output:**
```json
{
  "count": 47,
  "messages": [
    {
      "id": "a1b2c3d4-e5f6-...",
      "correlation_id": "x9y8z7w6-v5u4-...",
      "source": "websocket_receive",
      "message_type": "WEBSOCKET_RECEIVE",
      "timestamp": 1772109306941,
      "duration": null,
      "content": {
        "method": "tools/call",
        "tool": "search_patients_by_disease"
      },
      "status": "received"
    },
    ...
  ]
}
```

---

### 7. Message Tracking & Event Sourcing 📝

**What it is:**
Every single thing that happens is logged as an event with a timestamp. Like a security camera recording everything that happens in a building.

**Why it matters:**
- 🔍 **Debugging** - See exactly what went wrong
- 📊 **Analytics** - Understand how system performs
- 🔒 **Audit** - Track who did what when
- ⏱️ **Performance** - See which operations are slow

**What gets logged:**
```
1. User connects                   → CONNECTION event
2. Client sends command           → WEBSOCKET_RECEIVE event
3. Server starts processing       → TOOL_CALL_START event
4. Database searches              → CHROMA_SEARCH event (358ms)
5. AI generates summary          → OLLAMA_STREAM_START event
6. AI sends each token           → STREAM_TOKEN event (every 10)
7. AI finishes                   → OLLAMA_STREAM_COMPLETE event
8. Server saves to database      → CSV_WRITE event
9. Server sends response         → WEBSOCKET_SEND event
10. User gets result             → Everything visible in /api/messages
```

**Each message contains:**
- `id`: Unique identifier (UUID)
- `correlation_id`: Links all related messages together
- `source`: Where it came from (websocket, server, database, etc.)
- `message_type`: What happened (search started, data received, etc.)
- `timestamp`: When it happened (millisecond precision)
- `duration`: How long it took (in milliseconds)
- `content`: What the data was
- `status`: success/error

**Example: Complete Request Journey**

```
User searches "diabetes"
     ↓
[1] CONNECTION (client connected)
    - Event logged: connection_opened
    - Correlation ID: abc-123-xyz
    
[2] WEBSOCKET_RECEIVE (command received)
    - Event logged: client_sent_search_command
    - Correlation ID: abc-123-xyz
    - Duration: 0ms (just receiving)
    
[3] TOOL_CALL_START (processing begins)
    - Event logged: search_tool_starting
    - Correlation ID: abc-123-xyz
    - Duration: ---
    
[4] CHROMA_SEARCH (database search)
    - Event logged: chroma_query_executed
    - Correlation ID: abc-123-xyz
    - Duration: 358ms ⏱️
    - Results: 5 patients found
    
[5] TOOL_CALL_COMPLETE (processing done)
    - Event logged: search_tool_completed
    - Correlation ID: abc-123-xyz
    - Duration: 370ms total
    
[6] WEBSOCKET_SEND (response sent)
    - Event logged: response_sent_to_client
    - Correlation ID: abc-123-xyz
    - Message size: 2,456 bytes

Total time: 370ms
Total messages logged: 6 (all linked by same correlation ID)
```

---

### 8. Correlation IDs 🔗

**What it is:**
A unique ID that groups all related messages together. Like a case number that tracks one request through the entire system.

**Why it matters:**
```
User: "search for diabetes"

Without Correlation ID:
  [SEARCH REQUEST]
  [CHROMA QUERY]
  [RESULTS FOUND]
  [RESPONSE SENT]
  → Can't tell which messages go together ❌

With Correlation ID (abc-123):
  [SEARCH REQUEST] - Correlation: abc-123
  [CHROMA QUERY] - Correlation: abc-123
  [RESULTS FOUND] - Correlation: abc-123
  [RESPONSE SENT] - Correlation: abc-123
  → All linked! Can see complete journey ✅
```

**In our system:**
```bash
# You can query all messages for one request
curl http://localhost:8765/api/messages/correlation/abc-123-xyz | jq

Output:
{
  "messages": [
    {"type": "tool_call_start", "duration": null},
    {"type": "chroma_search", "duration": 358},
    {"type": "tool_call_complete", "duration": 370}
  ],
  "total_time_ms": 370,
  "steps_completed": 3
}
```

**Benefits:**
- 🔍 Easy debugging - follow request through system
- 📊 Performance analysis - see where time is spent
- 🧪 Testing - verify all steps completed
- 📈 Analytics - group related operations

---

## 🔄 How Everything Works Together

### Complete Workflow Example

You run this command:
```bash
> search_patients_by_disease diabetes
```

**Step 1: Send Command (WebSocket)**
```
Client sends:
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "search_patients_by_disease",
    "arguments": {"disease_keyword": "diabetes"}
  }
}

Event Logged:
- MESSAGE_ID: a1b2c3d4
- CORRELATION_ID: x9y8z7w6
- SOURCE: WEBSOCKET_RECEIVE
- TYPE: WEBSOCKET_RECEIVE
- TIMESTAMP: 1772109306941
```

**Step 2: Server Receives & Validates (MCP)**
```
Server receives JSON-RPC message
Validates JSON structure
Identifies method: "search_patients_by_disease"
Extracts parameters: {"disease_keyword": "diabetes"}

Event Logged:
- CORRELATION_ID: x9y8z7w6 (same as above)
- TYPE: TOOL_CALL_START
- DURATION: ---
```

**Step 3: Chroma DB Search (RAG Retrieval)**
```
Query: "diabetes"
↓
Chroma converts to vector: [0.234, 0.891, ...]
↓
Searches 356 patient profiles for similarity
↓
Finds matches:
  - Patient 11: Jerry Rivera (risk: 6.6)
  - Patient 45: Janet Torres (risk: 7.2)
  - Patient 25: Janet Lee (risk: 5.8)
  - Patient 69: Sarah Gutierrez (risk: 4.2)
  - Patient 41: Karen Jones (risk: 4.6)

Event Logged:
- CORRELATION_ID: x9y8z7w6 (same!)
- TYPE: CHROMA_SEARCH
- DURATION: 358ms ⏱️
- RESULTS: 5 patients
```

**Step 4: Format Response (MCP)**
```
Server formats results for client:
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [{
      "type": "text",
      "text": "Found 5 patients with diabetes..."
    }]
  }
}

Event Logged:
- CORRELATION_ID: x9y8z7w6
- TYPE: TOOL_CALL_COMPLETE  
- DURATION: 370ms total
- STATUS: success
```

**Step 5: Send to Client (WebSocket)**
```
Server sends response over open WebSocket
Client receives immediately

Event Logged:
- CORRELATION_ID: x9y8z7w6
- TYPE: WEBSOCKET_SEND
- MESSAGE_SIZE: 2,456 bytes
- STATUS: sent
```

**Step 6: Client Displays Results**
```
Output:
[RESULTS]
Found 5 patients with diabetes:
  - Patient 11: Jerry Rivera (Risk: 6.6)
  - Patient 45: Janet Torres (Risk: 7.2)
  ... (and more)
```

**Step 7: View Complete Journey**
```bash
# Query all messages with this correlation ID
curl http://localhost:8765/api/messages/correlation/x9y8z7w6 | jq

Output shows all 6 events:
1. WEBSOCKET_RECEIVE - received command
2. TOOL_CALL_START - started processing
3. CHROMA_SEARCH - database search (358ms)
4. TOOL_CALL_COMPLETE - finished processing (370ms)
5. WEBSOCKET_SEND - sent response
3. CONNECTION - client connected

Total time: 370ms from start to finish
All events linked by same correlation ID
```

---

## 📁 File Structure

```
11_mcp_llm_web_socket/
│
├── mcp_server.py
│   └─ Main server that:
│      • Accepts WebSocket connections
│      • Processes MCP requests
│      • Coordinates all operations
│      • Logs messages to tracking system
│      • Provides REST API for monitoring
│
├── mcp_client.py
│   └─ Interactive client that:
│      • Connects via WebSocket
│      • Sends user commands
│      • Receives and displays results
│      • Shows real-time progress
│
├── message_tracker.py
│   └─ Event logging system that:
│      • Records every operation
│      • Generates unique IDs
│      • Tracks correlation IDs
│      • Measures durations
│      • Stores in memory
│
├── message_api.py
│   └─ REST endpoints that:
│      • Expose /api/messages/* endpoints
│      • Filter by type, source, patient, etc.
│      • Provide statistics
│      • Enable UI monitoring
│
├── patient_embeddings.csv
│   └─ Vector embeddings for all patient health profiles
│      (Used by Chroma for vector search)
│
├── patients_data.csv
│   └─ Raw patient health data:
│      • Patient ID, Name, Age, Gender
│      • Symptoms, Medications
│      • Blood Pressure, Blood Sugar
│      • Medical History
│
├── patient_summaries.csv
│   └─ Generated medical summaries:
│      • Patient ID, Name
│      • AI-generated summary (empty initially)
│      • Updated by server when summarized
│
├── chroma_db/
│   └─ Vector database directory:
│      • Stores 356 embedded patient profiles
│      • Enables fast vector similarity search
│      • Manages two collections:
│        ├─ patient_profiles (356 items)
│        └─ patients (100 items)
│
└── TESTING_MESSAGE_TRACKING.md
    └─ Complete testing guide with:
       • API endpoint examples
       • Message schema documentation
       • Troubleshooting tips
```

---

## 🔌 API Reference

### Message Tracking Endpoints

#### Get All Messages
```
GET /api/messages/

Response:
{
  "count": 47,
  "messages": [
    {
      "id": "uuid",
      "correlation_id": "uuid",
      "source": "websocket_send",
      "message_type": "websocket_send",
      "timestamp": 1772109306941,
      "duration": null,
      "latency": null,
      "content": {...},
      "tool_name": null,
      "patient_id": null,
      "message_size": 87,
      "status": "success",
      "metadata": {}
    },
    ...
  ]
}
```

#### Get Recent Messages
```
GET /api/messages/recent?count=10

Returns last N messages with most recent first
```

#### Get Messages by Correlation ID
```
GET /api/messages/correlation/{correlation_id}

Returns all messages that are part of same operation/request
```

#### Get Messages by Patient
```
GET /api/messages/patient/{patient_id}

Returns all messages related to specific patient
```

#### Get Messages by Type
```
GET /api/messages/type/{message_type}

Returns all messages of specific type:
- tool_call_start
- tool_call_complete
- chroma_search
- ollama_stream_complete
- csv_write
- websocket_send
- websocket_receive
- connection
- etc.
```

#### Get Messages by Source
```
GET /api/messages/source/{source}

Returns messages from specific source:
- websocket_send
- websocket_receive
- server_process
- chroma_db
- ollama
- csv_operation
- error
```

#### Get Statistics
```
GET /api/stats

Response:
{
  "statistics": {
    "total_messages": 47,
    "unique_sources": 4,
    "sources": ["websocket_send", "server_process", ...],
    "unique_types": 6,
    "types": ["tool_call_complete", "connection", ...],
    "time_span_ms": 18346,
    "total_data_bytes": 4651,
    "average_latency_ms": null,
    "first_message_ts": 1772109306941,
    "last_message_ts": 1772109325287
  }
}
```

#### Clear All Messages
```
POST /api/messages/clear

Resets message tracking for fresh start
```

---

## 🚀 Performance Characteristics

| Operation | Typical Time | Notes |
|-----------|--------------|-------|
| **Search (Chroma)** | 358ms | Searches 356 profiles via vector similarity |
| **AI Summary (Ollama)** | 30-60s | Depends on patient data length & model |
| **CSV Read** | <50ms | Loads patient_summaries.csv |
| **CSV Write** | <100ms | Writes updated summary |
| **Total Search+Return** | ~370ms | From command to results displayed |
| **Total Generate+Save** | 30-65s | From command to summary saved |
| **WebSocket Latency** | <10ms | Local connection |
| **Message Logging** | <1ms | Minimal overhead |

---

## 🛠️ System Requirements

### Minimum Hardware
- CPU: 2 cores (4+ recommended for LLM)
- RAM: 4GB (8GB+ recommended for Ollama)
- Disk: 10GB (for Chroma DB + Ollama model)

### Software Requirements
- Python 3.8+
- Ollama running locally (for LLM generation)
- Chroma DB initialized with patient data
- FastAPI, websockets libraries

### Network
- Localhost only (127.0.0.1)
- WebSocket on port 8765
- REST API on same port

---

## 🔮 What Happens Behind the Scenes

### When You Search:
```
Your Command: "search_patients_by_disease diabetes"
     ↓
1. WebSocket message received & logged
2. Command parsed as MCP request
3. Search function called asynchronously
4. Chroma DB loads vector for "diabetes"
5. Runs similarity search on 356 vectors
6. Returns 5 most similar patients
7. Formats response as JSON-RPC
8. Sends over WebSocket
9. Client receives results
10. All steps logged with timings & IDs
```

### When You Generate Summary:
```
Your Command: "generate_summary 25"
     ↓
1. WebSocket message received & logged
2. Patient 25 data loaded from CSV
3. Data sent to local Ollama model
4. Ollama generates summary token-by-token
5. Each token logged as it arrives
6. Summary accumulated in memory
7. Final summary returned to client
8. Operation took 30-60 seconds visible in logs
9. You see everything in real-time progress
```

### When You Update Summary:
```
Your Command: "update_summary 25"
     ↓
1. WebSocket message received & logged
2. CSV file read (all patient records loaded)
3. Patient 25 record found
4. Summary field updated
5. CSV file written back
6. File operation logged with timing
7. Success confirmed to client
8. Total time: <200ms
```

---

## 💡 Key Takeaways

1. **MCP** = Structured way for systems to talk
2. **WebSocket** = Persistent connection for real-time communication
3. **RAG** = AI uses real data from database to generate accurate content
4. **Chroma DB** = Smart search using vector similarity (finds "similar meaning")
5. **Async** = Multiple operations without blocking others
6. **REST API** = Simple URLs to query logged messages
7. **Message Tracking** = Complete audit trail of everything that happens
8. **Correlation IDs** = Groups related messages together

---

## 📚 Further Reading

- **MCP Specification**: Model Context Protocol official docs
- **WebSocket Protocol**: RFC 6455
- **Chroma Documentation**: https://docs.trychroma.com/
- **Ollama Models**: https://ollama.ai/
- **FastAPI**: https://fastapi.tiangolo.com/
- **Python Async**: https://docs.python.org/3/library/asyncio.html

---

## ❓ Common Questions

**Q: Why does generating a summary take so long?**
A: Ollama runs an LLM locally, which is compute-intensive. On a CPU, it can take 30-60 seconds to generate a 400-word medical summary.

**Q: Can I see the message logs?**
A: Yes! Query `/api/messages/` or `/api/messages/recent` endpoints, or run `view_messages` in the client.

**Q: What if something goes wrong?**
A: Check the logs: `curl http://localhost:8765/api/messages/type/error_occurred` to see error details with timestamps.

**Q: Can multiple users use this at the same time?**
A: Yes! Async design allows multiple concurrent WebSocket connections. Each gets logged with their own correlation ID.

**Q: How long are message logs kept?**
A: In memory only. When server restarts, logs clear. For persistent logging, save them to a database.

**Q: Can I use this for real healthcare?**
A: For demo/educational purposes. Real healthcare needs HIPAA compliance, data encryption, database persistence, etc.

---

**Last Updated**: February 26, 2026
**Version**: 1.0 - Complete System
