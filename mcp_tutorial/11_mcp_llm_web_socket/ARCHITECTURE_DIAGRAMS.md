# Architecture Diagrams & Visual References

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PATIENT MANAGEMENT SYSTEM                         │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                    Interactive Client (mcp_client.py)               │  │
│  │                                                                      │  │
│  │  Commands:                                                           │  │
│  │   • search_patients_by_disease <keyword>                           │  │
│  │   • generate_summary <patient_id>                                  │  │
│  │   • update_summary <patient_id>                                    │  │
│  │   • list_patients                                                   │  │
│  │   • view_messages                                                   │  │
│  │                                                                      │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│               │                                                     │       │
│               │ WebSocket                                          │ REST  │
│               │ JSON-RPC                                           │ API   │
│               ▼                                                     ▼       │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │                         MCP Server (mcp_server.py)                  │  │
│  │                   ws://127.0.0.1:8765/mcp                          │  │
│  │                                                                      │  │
│  │  ┌────────────────────────────────────────────────────────────┐   │  │
│  │  │          Message Tracking System (message_tracker.py)      │   │  │
│  │  │    Logs every event with unique ID, timestamp, duration    │   │  │
│  │  └────────────────────────────────────────────────────────────┘   │  │
│  │                                                                      │  │
│  │  ┌────────────────────────────────────────────────────────────┐   │  │
│  │  │                    Request Handler                         │   │  │
│  │  │                                                            │   │  │
│  │  │  • Receives WebSocket messages (async)                   │   │  │
│  │  │  • Parses JSON-RPC requests                              │   │  │
│  │  │  • Routes to appropriate tool                            │   │  │
│  │  │  • Calls tools asynchronously                            │   │  │
│  │  │  • Formats responses                                     │   │  │
│  │  │  • Sends back to client                                  │   │  │
│  │  │  • Logs each step                                        │   │  │
│  │  └────────────────────────────────────────────────────────────┘   │  │
│  │                          │                                          │  │
│  │         ┌────────────────┼────────────────┐                        │  │
│  │         ▼                ▼                ▼                        │  │
│  │   ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                │  │
│  │   │   Search    │ │  Generate   │ │   Update    │                │  │
│  │   │  Patients   │ │  Summary    │ │  Summary    │                │  │
│  │   │   (Chroma)  │ │  (Ollama)   │ │   (CSV)     │                │  │
│  │   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘                │  │
│  │          │               │               │                        │  │
│  └──────────┼───────────────┼───────────────┼────────────────────────┘  │
│             │               │               │                          │
│             ▼               ▼               ▼                          │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                   External Services & Data                      │   │
│  │                                                                 │   │
│  │  ┌──────────────────┐ ┌──────────────┐ ┌────────────────────┐ │   │
│  │  │   Chroma DB      │ │  Ollama AI   │ │  CSV Files         │ │   │
│  │  │ (Vector Search)  │ │  (LLM)       │ │  (Database)        │ │   │
│  │  │                  │ │              │ │                    │ │   │
│  │  │ • 356 profiles   │ │ • Phi model  │ │ • patients_data    │ │   │
│  │  │ • 100 patients   │ │ • ~30-60s    │ │ • patient_summaries│ │   │
│  │  │ • ~358ms search  │ │ • Per summary│ │ • Fast read/write  │ │   │
│  │  └──────────────────┘ └──────────────┘ └────────────────────┘ │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                          ▲                                              │
│                          │ Query via REST                              │
│                          │                                              │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │        Message Tracking API (message_api.py)                    │  │
│  │              /api/messages/* endpoints                          │  │
│  │      View logs, filter by type/source/patient, get stats       │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Request Processing Pipeline (Detailed Flow)

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER ISSUES COMMAND                           │
│              search_patients_by_disease "diabetes"                      │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────────┐
         │         1. COMMAND ENCODING (Client)          │
         │                                               │
         │  Convert to JSON-RPC request:                │
         │  {                                            │
         │    "jsonrpc": "2.0",                         │
         │    "id": 1,                                   │
         │    "method": "tools/call",                   │
         │    "params": {                               │
         │      "name": "search_patients...",           │
         │      "arguments": {                          │
         │        "disease_keyword": "diabetes"        │
         │      }                                        │
         │    }                                          │
         │  }                                            │
         └───────────────────────┬───────────────────────┘
                                 │
                    ═════════════════════════════════════
                      WebSocket Transport Layer
                    ═════════════════════════════════════
                                 │
                                 ▼
         ┌───────────────────────────────────────────────┐
         │    2. MESSAGE RECEPTION (Server WebSocket)   │
         │                                               │
         │  • WebSocket receives text message           │
         │  • Parses JSON                               │
         │  • Extracts method, params, id              │
         │                                               │
         │  ✓ Event Logged: WEBSOCKET_RECEIVE          │
         │    - ID: a1b2c3d4-...                       │
         │    - Correlation: x9y8z7w6-...             │
         │    - Timestamp: 1772109306941                │
         │    - Message size: 245 bytes                │
         │                                               │
         └───────────────────────┬───────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────────┐
         │      3. REQUEST DISPATCH (Route Handler)      │
         │                                               │
         │  Method: "tools/call"                        │
         │  Tool: "search_patients_by_disease"          │
         │  Arguments: {"disease_keyword": "diabetes"} │
         │                                               │
         │  ✓ Event Logged: TOOL_CALL_START            │
         │    - Correlation: x9y8z7w6-... (same!)     │
         │    - Tool: search_patients_by_disease        │
         │    - Status: in-progress                    │
         │                                               │
         └───────────────────────┬───────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────────┐
         │  4. RETRIEVAL (RAG - Get from Database)      │
         │                                               │
         │  Async call to Chroma DB:                    │
         │  1. Convert "diabetes" to vector             │
         │     [0.234, 0.891, 0.456, ...]             │
         │  2. Load all 356 patient embeddings         │
         │  3. Calculate similarity scores             │
         │  4. Sort by similarity                       │
         │  5. Return top 5 matches                     │
         │                                               │
         │  Results:                                    │
         │   ✓ Patient 11: Jerry Rivera (score: 0.92)  │
         │   ✓ Patient 45: Janet Torres (score: 0.90)  │
         │   ✓ Patient 25: Janet Lee (score: 0.87)     │
         │   ✓ Patient 69: Sarah Gutierrez (score: 0.85)
         │   ✓ Patient 41: Karen Jones (score: 0.83)   │
         │                                               │
         │  ✓ Event Logged: CHROMA_SEARCH             │
         │    - Correlation: x9y8z7w6-... (same!)     │
         │    - Duration: 358ms ⏱️                      │
         │    - Results count: 5                       │
         │    - Query: "diabetes"                       │
         │                                               │
         └───────────────────────┬───────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────────┐
         │   5. AUGMENTATION (Add retrieved data)       │
         │                                               │
         │  Format results as readable response:        │
         │  "Found 5 patients with diabetes:            │
         │   - Jerry Rivera (Risk: 6.6)                │
         │   - Janet Torres (Risk: 7.2)                │
         │   - Janet Lee (Risk: 5.8)                   │
         │   - Sarah Gutierrez (Risk: 4.2)             │
         │   - Karen Jones (Risk: 4.6)"                │
         │                                               │
         │  ✓ Event Logged: TOOL_CALL_COMPLETE        │
         │    - Correlation: x9y8z7w6-... (same!)     │
         │    - Status: success                        │
         │    - Duration: 370ms (total)                │
         │    - Results: 5 patients                    │
         │                                               │
         └───────────────────────┬───────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────────┐
         │     6. RESPONSE ENCODING (JSON-RPC)          │
         │                                               │
         │  {                                            │
         │    "jsonrpc": "2.0",                         │
         │    "id": 1,                                   │
         │    "result": {                               │
         │      "content": [{                           │
         │        "type": "text",                       │
         │        "text": "Found 5 patients..."        │
         │      }]                                      │
         │    }                                          │
         │  }                                            │
         │                                               │
         │  Response size: 2,456 bytes                  │
         │                                               │
         │  ✓ Event Logged: WEBSOCKET_SEND             │
         │    - Correlation: x9y8z7w6-... (same!)     │
         │    - Message size: 2,456 bytes              │
         │    - Status: sent                           │
         │                                               │
         └───────────────────────┬───────────────────────┘
                                 │
                    ═════════════════════════════════════
                      WebSocket Transport Layer
                    ═════════════════════════════════════
                                 │
                                 ▼
         ┌───────────────────────────────────────────────┐
         │      7. MESSAGE TRANSMISSION (Server)         │
         │                                               │
         │  Send JSON response over open WebSocket      │
         │  Client receives immediately                 │
         │  Connection stays open for next command      │
         │                                               │
         └───────────────────────┬───────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────────┐
         │     8. RESPONSE DISPLAY (Client)             │
         │                                               │
         │  Parse JSON response                         │
         │  Extract results from content                │
         │  Display to user:                            │
         │                                               │
         │  [RESULTS]                                   │
         │  Found 5 patients with diabetes:             │
         │   - Patient 11: Jerry Rivera (Risk: 6.6)    │
         │   - Patient 45: Janet Torres (Risk: 7.2)    │
         │   - Patient 25: Janet Lee (Risk: 5.8)       │
         │   - Patient 69: Sarah Gutierrez (Risk: 4.2) │
         │   - Patient 41: Karen Jones (Risk: 4.6)     │
         │                                               │
         └───────────────────────┬───────────────────────┘
                                 │
                                 ▼
         ┌───────────────────────────────────────────────┐
         │  9. MESSAGE LOG INSPECTION (Monitoring)      │
         │                                               │
         │  Query: GET /api/messages/correlation/       │
         │         x9y8z7w6-...                         │
         │                                               │
         │  Returns all 6 events linked:                │
         │  ✓ WEBSOCKET_RECEIVE (message_size: 245)   │
         │  ✓ TOOL_CALL_START (status: in-progress)   │
         │  ✓ CHROMA_SEARCH (duration: 358ms)          │
         │  ✓ TOOL_CALL_COMPLETE (duration: 370ms)    │
         │  ✓ WEBSOCKET_SEND (message_size: 2456)     │
         │                                               │
         │  Time Span: 370ms from start to finish       │
         │  Total Data: 245 + 2456 = 2,701 bytes       │
         │                                               │
         └───────────────────────────────────────────────┘
```

---

## 3. Asynchronous Processing Pattern

```
SYNCHRONOUS (Blocking - Old Way):
═════════════════════════════════

Search (358ms) → Wait ⏳
  Then AI Gen (35s) → Wait ⏳
    Then CSV Write (45ms) → Wait ⏳
Total: 35,403ms (35 seconds) 🐌


Timeline:
0ms ├─ [Search 358ms] ────────┐
     │                         │
358ms├─ [AI Gen 35s] ───────────────────────────────────┐
     │                                                   │
35,358ms├─ [CSV Write 45ms] ───┐
         │                     │
35,403ms └──────────────────────────── Complete


ASYNCHRONOUS (Non-blocking - This App):
═════════════════════════════════════════

Start Search (358ms)
  ▲
  │ Meanwhile, server can:
  │ • Accept other WebSocket connections
  │ • Start other operations
  │ • Respond to monitoring requests
  │
  Continue with other things
  
Complete Search → Get Results (358ms)
Complete AI Gen → Get Summary (35s)
Complete CSV Write → Confirm Save (45ms)

Timeline (Multiple concurrent operations):
0ms ├─ [Search 358ms] ────────┐
     │ [AI Gen 35s] ──────────────────────────┐
     │ [CSV Write 45ms] ─┐
     │                  │    │                │
358ms├──────────────────┘    │                │
     │                       │                │
45ms ├─ [Search 2 358ms] ────────────────────┐
     │                       │                │
     ...                     │                │
35,000ms├────────────────────┘                │
        │                                     │
35,358ms└──────────────────────────────────────┘
        
Total time: Still ~35s but MULTIPLE operations running!
```

---

## 4. Data Flow Through System

```
SEARCH OPERATION:
═════════════════

User Input
   │
   ├─→ "search_patients_by_disease diabetes"
   │
   ├─→ WebSocket Message
   │   (245 bytes of JSON)
   │
   ├─→ Server Receives & Parses
   │   (MCP Router)
   │
   ├─→ Chroma DB Query
   │   Input: Query string "diabetes"
   │   Process: 
   │   ├─ Convert to vector: [0.234, 0.891, ...]
   │   ├─ Load 356 patient embeddings
   │   ├─ Calculate similarities
   │   └─ Return top 5
   │   Output: 5 patient IDs + scores
   │   Time: 358ms
   │
   ├─→ Format Results
   │   Text: "Found 5 patients with diabetes..."
   │   Convert to JSON-RPC response
   │
   ├─→ WebSocket Response
   │   (2,456 bytes of JSON)
   │
   └─→ Client Receives & Displays
       User sees: 5 patients listed


GENERATION OPERATION:
═════════════════════

User Input
   │
   ├─→ "generate_summary 25"
   │
   ├─→ WebSocket Message
   │   (180 bytes of JSON)
   │
   ├─→ Server Receives & Parses
   │   (MCP Router)
   │   Extracts: patient_id=25
   │
   ├─→ Read Patient Data
   │   From: patients_data.csv
   │   Get: Name, age, symptoms, BP, blood sugar, etc.
   │   Data size: ~500-1000 bytes
   │
   ├── OpenAI Ollama Request
   │   Input: All patient data (500 bytes)
   │   Prompt: "Summarize this patient's health..."
   │   Model: Phi 2.7B
   │   Process: Token-by-token generation
   │   │
   │   ├─ Token 1: "Based" ─→ Logged
   │   ├─ Token 2: "on" ─→ Logged
   │   ├─ Token 3: "the" ─→ Logged
   │   ├─ ... (250+ tokens)
   │   ├─ Token 247: "plan" ─→ Logged
   │   │
   │   Output: 1,400 bytes (medical summary)
   │   Time: 30-60 seconds
   │
   ├─→ Format Results
   │   Include: Patient name, summary text
   │   Convert to JSON-RPC response
   │
   ├─→ WebSocket Response
   │   (1,500 bytes of JSON)
   │
   ├─→ Return to User (shown in client)
   │
   ├─→ Wait for next command: "update_summary 25"
   │
   ├─→ WebSocket Message
   │   (150 bytes)
   │
   ├─→ Update Patient Record
   │   Read: patient_summaries.csv (19KB, 100 rows)
   │   Find: Row for patient 25
   │   Update: Summary field with generated text
   │   Write: patient_summaries.csv (now 19.5KB)
   │   Time: <100ms
   │
   ├─→ Confirm Success
   │   Response: "Summary saved for patient 25"
   │
   └─→ Client Receives & Shows Confirmation


MONITORING / EVENT INSPECTION:
══════════════════════════════

At any time, you can query: GET /api/messages/

Message Store (in memory):
┌──────────────────────────────────────────┐
│ [Message 1] WEBSOCKET_RECEIVE            │
│ [Message 2] TOOL_CALL_START              │
│ [Message 3] CHROMA_SEARCH (358ms)        │
│ [Message 4] CHROMA_SEARCH (358ms)        │
│ [Message 5] TOOL_CALL_COMPLETE (370ms)   │
│ [Message 6] WEBSOCKET_SEND               │
│ [Message 7] CONNECTION (client_1)        │
│ [Message 8] WEBSOCKET_RECEIVE            │
│ [Message 9] TOOL_CALL_START              │
│ [Message 10] OLLAMA_STREAM_START         │
│ [Message 11] STREAM_TOKEN (every 10)     │
│ [Message 12] STREAM_TOKEN (every 10)     │
│ ... (continued)                          │
│ [Message N] WEBSOCKET_SEND               │
└──────────────────────────────────────────┘
    ↓
Get /api/messages/correlation/abc-123
    ↓
Returns all events for request abc-123:
- TOOL_CALL_START
- CHROMA_SEARCH (358ms)
- TOOL_CALL_COMPLETE (370ms)
- WEBSOCKET_SEND
```

---

## 5. Message Lifecycle (Tracking)

```
SINGLE MESSAGE LIFECYCLE:
═════════════════════════

1. MESSAGE CREATION
   ├─ Unique ID generated: a1b2c3d4-e5f6-g7h8
   ├─ Correlation ID set: x9y8z7w6-v5u4-t3s2
   ├─ Timestamp recorded: 1772109306941 (ms)
   ├─ Source determined: WEBSOCKET_RECEIVE
   ├─ Type classified: WEBSOCKET_RECEIVE
   ├─ Content captured: {method, request_id, size}
   └─ Status marked: "received"

2. MESSAGE STORAGE
   ├─ Added to messages array (in memory)
   ├─ Indexed by ID
   ├─ Indexed by correlation_id
   ├─ Indexed by source
   ├─ Indexed by type
   └─ Total stored: 47 messages

3. MESSAGE RETRIEVAL
   Via REST API:
   ├─ GET /api/messages/ → All 47
   ├─ GET /api/messages/recent?count=5 → Last 5
   ├─ GET /api/messages/correlation/x9y8z7w6 → Linked 6
   ├─ GET /api/messages/type/chroma_search → 3
   ├─ GET /api/messages/patient/25 → 8
   └─ GET /api/stats → Aggregates

4. MESSAGE ANALYSIS
   ├─ Duration: 358ms (CHROMA_SEARCH)
   ├─ Latency: <10ms (Network)
   ├─ Message size: 245 bytes (WEBSOCKET_RECEIVE)
   ├─ Status: "success" or "error"
   ├─ Correlation chain: 6 related messages
   └─ System health: Total 47, avg duration 250ms


CORRELATION ID FLOW:
════════════════════

User: search_patients_by_disease diabetes
   │
   ├─ Generate New Correlation ID: x9y8z7w6
   │  └─ Session ID for tracking this operation
   │
   ├─ Message 1: WEBSOCKET_RECEIVE
   │  └─ Correlation: x9y8z7w6 ✓
   │
   ├─ Message 2: TOOL_CALL_START  
   │  └─ Correlation: x9y8z7w6 ✓
   │
   ├─ Message 3: CHROMA_SEARCH
   │  └─ Correlation: x9y8z7w6 ✓ (358ms)
   │
   ├─ Message 4: TOOL_CALL_COMPLETE
   │  └─ Correlation: x9y8z7w6 ✓ (370ms total)
   │
   └─ Message 5: WEBSOCKET_SEND
      └─ Correlation: x9y8z7w6 ✓

Query: GET /api/messages/correlation/x9y8z7w6
   │
   └─ Returns all 5 messages:
      ✓ Linked by same correlation ID
      ✓ Shows complete operation flow
      ✓ Total duration: 370ms
      ✓ 5 steps visible
      ✓ Easy debugging!
```

---

## 6. WebSocket vs REST Comparison

```
WEBSOCKET (This App - JSON-RPC):
═════════════════════════════════

                    Client                Server
                      │                     │
                      │─ CONNECT ─→         │
                      │  (handshake)        │
                      │                     │
                      │← CONNECTED ─        │
                      │(connection open)    │
                      │                     │
Command 1:   │─ {"method": "..."} ─→│
                      │                │ Process (358ms)
                      │                │
                      │← {"result": ...}──│
                      │                     │
Command 2:   │─ {"method": "..."} ─→│
                      │                │ Process (30s)
                      │← {"result": ...}──│
                      │                     │
Query Logs:  │─ GET /api/messages ─→│
                      │                │ Query in-memory
                      │← {messages: ...}──│
                      │                     │
                      │─ DISCONNECT ─→ │
                      │(close connection)  │

Benefits:
✓ Connection stays open
✓ No connection overhead per request
✓ Can get multiple results
✓ Real-time streaming possible
✓ Server is responsive to monitoring


TRADITIONAL HTTP REST:
═════════════════════════════════

                    Client                Server
                      │                     │
Command 1:   │─ HTTP POST ─→│
                      │      │ Process
                      │      │
                      │←─ 200 OK ─────│
                      │                     │
              (connection closes)
                      │                     │
Command 2:   │─ HTTP POST ─→│ (new connection!)
                      │      │ Process
                      │      │
                      │←─ 200 OK ─────│
                      │                     │
              (connection closes)
                      │                     │
Query Logs:  │─ GET /api/messages ─→│
                      │      │ Query
                      │      │
                      │←─ 200 OK ─────│
                      │                     │
              (connection closes)

Drawbacks:
✗ Connection overhead for each request
✗ No streaming responses
✗ More latency
✗ Doesn't scale well
```

---

## 7. Message Types & Sources Matrix

```
                   SOURCES
              ┌─────────────────────────────────────────┐
              │           WHERE MESSAGE COMES FROM      │
              └─────────────────────────────────────────┘

Types/Sources │ WS Recv │ WS Send │ Server │ Chroma │ Ollama │ CSV │ Error │
──────────────┼─────────┼─────────┼────────┼────────┼────────┼─────┼───────┤
CONNECTION    │    ✓    │    ✓    │        │        │        │     │       │
WEBSOCKET_RCV │    ✓    │         │        │        │        │     │       │
WEBSOCKET_SND │         │    ✓    │        │        │        │     │       │
TOOL_START    │         │         │   ✓    │        │        │     │       │
TOOL_COMPLETE │         │         │   ✓    │        │        │     │       │
CHROMA_SEARCH │         │         │        │   ✓    │        │     │       │
OLLAMA_START  │         │         │        │        │   ✓    │     │       │
OLLAMA_TOKEN  │         │         │        │        │   ✓    │     │       │
OLLAMA_COMPL  │         │         │        │        │   ✓    │     │       │
CSV_READ      │         │         │        │        │        │ ✓   │       │
CSV_WRITE     │         │         │        │        │        │ ✓   │       │
ERROR         │         │         │        │        │        │     │   ✓   │
──────────────┴─────────┴─────────┴────────┴────────┴────────┴─────┴───────┘

Common Patterns:
• Search: TOOL_START → CHROMA_SEARCH → TOOL_COMPLETE
• Generate: TOOL_START → OLLAMA_START → OLLAMA_TOKEN*N → OLLAMA_COMPLETE → TOOL_COMPLETE
• Update: TOOL_START → CSV_READ → CSV_WRITE → TOOL_COMPLETE
• Everything: WEBSOCKET_RCV → (above) → WEBSOCKET_SND
```

---

## 8. Performance Timeline Example

```
COMPLETE OPERATION: Search + Generate + Update
═════════════════════════════════════════════════

Time    Event                              Message Logged        Duration
────────────────────────────────────────────────────────────────────────
0ms     Client connects                    CONNECTION            -
        ↓

10ms    User: search_patients...          WEBSOCKET_RECEIVE     -
        ↓

15ms    Server routing                    TOOL_CALL_START       -
        ↓

18ms    Chroma query starts→              (processing)
        ↓

376ms   Chroma returns results            CHROMA_SEARCH         358ms ✓
        ↓

380ms   Search completes                  TOOL_CALL_COMPLETE    365ms
        ↓

385ms   Response sent to client           WEBSOCKET_SEND        -
        ↓
        User selects patient 25
        ↓

400ms   User: generate_summary 25         WEBSOCKET_RECEIVE     -
        ↓

405ms   Server routing                    TOOL_CALL_START       -
        ↓

410ms   Read patient data from CSV        CSV_READ              8ms ✓
        ↓

450ms   Ollama connection                 OLLAMA_START          -
        ↓

470ms   Ollama generates tokens...        OLLAMA_TOKEN (x247)   (ongoing)
        
        Token 1: "Based"                  STREAM_TOKEN          2300ms
        Token 10: "Lee's"                 STREAM_TOKEN          4500ms
        Token 50: "carefully"             STREAM_TOKEN          8900ms
        Token 100: "treatment"            STREAM_TOKEN         13200ms
        Token 150: "healthcare"           STREAM_TOKEN         18900ms
        Token 200: "management"           STREAM_TOKEN         24200ms
        Token 247: "plan"                 OLLAMA_COMPLETE      30150ms ✓
        ↓

30155ms  Summary ready                    TOOL_CALL_COMPLETE    30150ms
        ↓

30160ms  Response sent to client          WEBSOCKET_SEND        -
        ↓
        User: update_summary 25
        ↓

30180ms  User sends update command        WEBSOCKET_RECEIVE     -
        ↓

30185ms  Server routing                   TOOL_CALL_START       -
        ↓

30192ms  Read summaries CSV               CSV_READ              12ms ✓
        ↓

30210ms  Write updated summary            CSV_WRITE             35ms ✓
        ↓

30215ms  Update completes                 TOOL_CALL_COMPLETE    45ms
        ↓

30220ms  Response sent to client          WEBSOCKET_SEND        -

────────────────────────────────────────────────────────────────────────

TOTAL TIME: 30.22 seconds
TOTAL MESSAGES LOGGED: 15+
BOTTLENECK: Ollama generation (30.15 seconds)
OTHER OPERATIONS: <1 second total
```

---

## 9. Concept Integration Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│           HOW ALL CONCEPTS WORK TOGETHER                             │
└──────────────────────────────────────────────────────────────────────┘

                        COMMUNICATION PROTOCOL
                               (MCP)
                                 │
                    ┌────────────┴────────────┐
                    │                         │
              JSON-RPC Request           JSON-RPC Response
             {"method": "..."}           {"result": "..."}
                    │                         │
                    ▼                         ▼
           ╔═════════════════╗       ╔═════════════════╗
           ║   WEBSOCKET     ║       ║   WEBSOCKET     ║
           ║  (Transport)    ║◄─────►║  (Transport)    ║
           ║  Port 8765      ║       ║  (Async)        ║
           ╚═════════════════╝       ╚═════════════════╝
                    ▲                         ▲
                    │                         │
      ┌─────────────┴─────────────┐          │
      │                           │          │
      ▼                           ▼          │
   CLIENT              REQUEST HANDLER       │
(mcp_client.py)        (mcp_server.py)       │
                                             │
                    ┌────────────────────────┘
                    │
          ┌─────────┼─────────┐
          │         │         │
          ▼         ▼         ▼
      ┌────────┐┌────────┐┌────────┐
      │SEARCH  ││GENERATE││UPDATE  │
      │(Chroma)││(Ollama)││(CSV)   │
      └────┬───┘└───┬────┘└───┬────┘
           │        │         │
    RAG:   │        │         │
    ┌──────┘        │         │
    │    ┌──────────┘         │
    │    │    ┌───────────────┘
    │    │    │
    ▼    ▼    ▼
Retrieve (DB) + Augment (Real data) + Generate (AI output)
│                   │                    │
├─ Patient records  ├─ Health data      ├─ Medical summary
├─ Symptoms        ├─ Medications       ├─ Risk assessment
├─ Medical history ├─ BP/glucose levels ├─ Recommendations
└─ Previous notes  └─ Test results      └─ Follow-up Plan

                    MESSAGE TRACKING SYSTEM
                  (message_tracker.py + message_api.py)
                            │
                  ┌─────────┬┴┬─────────┐
                  │         │ │         │
          Generate ID   Correlation  Log with
          + Timestamp   (link ops)   Duration
                  │         │         │
                  └─────────┼─────────┘
                            │
                  ┌─────────┴─────────┐
                  │                   │
            Store in memory      REST API
                  │               /api/msgs
            Message array        /api/stats
                  │               /api/msgs/
                  │              correlation/
                  │
                  └──→ Answer questions:
                       • What happened?
                       • When?
                       • How long?
                       • What was linked?
                       • Any errors?
```

---

## 10. System Health Check (Monitoring)

```
REAL-TIME MONITORING:
═════════════════════

Every N seconds, you can query:

GET /api/stats → {
  "total_messages": 47,
  "unique_sources": 4,
    ├─ websocket_send: 8
    ├─ websocket_receive: 6
    ├─ server_process: 15
    ├─ chroma_db: 3
    └─ ollama: 15

  "unique_types": 6,
    ├─ tool_call_start: 3
    ├─ tool_call_complete: 3
    ├─ chroma_search: 3
    ├─ ollama_stream_complete: 3
    ├─ websocket_send: 8
    └─ websocket_receive: 6

  "time_span_ms": 30220,
  "total_data_bytes": 18456,
  "average_duration_ms": 125
}

INTERPRETATION:
├─ 47 messages = active system
├─ 4 sources = all components working
├─ 30.2 seconds = typical operation
├─ 18.5KB data = normal throughput
└─ 125ms avg = performance OK


ERROR MONITORING:
═════════════════

GET /api/messages/type/error_occurred → {
  "count": 0,
  "messages": []
} ✓ No errors!

If errors exist:
  "count": 2,
  "messages": [
    {
      "error": "patient_not_found",
      "patient_id": "999",
      "timestamp": 1772109401234,
      "correlation_id": "abc-123"
    },
    {
      "error": "chroma_connection_timeout",
      "timestamp": 1772109425456,
      "correlation_id": "def-456"
    }
  ]

→ Can trace errors to specific operations! → Can investigate with correlation ID!
```

---

**All diagrams show the complete system architecture and information flow!**
