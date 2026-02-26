# Patient Summaries App - Plain-English Guide

## What This App Does (Layman Overview)
This app helps you search for patients by a health issue and generate a clear summary of their health data. You type a keyword like "diabetes" or "high blood pressure", the system finds the most relevant patients, and it can create a short, easy-to-read summary for each patient. Think of it like a smart assistant for patient notes.

It also keeps a full "paper trail" of what the user sent, what the server did, and what was sent back over WebSocket, so you can see the full flow and any delays.

## How To Run and Use the App

### 1) Start the server
```bash
cd /home/navinkumar_25_gmail_com/mcp_tutorial/11_mcp_llm_web_socket
python mcp_server.py
```

### 2) Run the interactive client
```bash
python mcp_client.py
```

### 3) Example commands (inside the client)
- Search patients by keyword:
  - `search_patients_by_disease diabetes`
- Generate summary for a patient:
  - `generate_summary 25`
- Update summary in CSV:
  - `update_summary 25`

### 4) View tracking messages (for UI / debugging)
```bash
# Recent messages
curl http://localhost:8765/api/messages/recent?count=10 | jq

# System stats
curl http://localhost:8765/api/stats | jq
```

## Architecture Diagram

```mermaid
flowchart LR
  U[User] -->|WebSocket| C[MCP Client]
  C -->|JSON-RPC| WS[MCP Server (FastAPI + WebSocket)]

  WS -->|Search Query| CH[Chroma DB]
  CH -->|Top Matches| WS

  WS -->|Patient Data| LLM[Ollama LLM]
  LLM -->|Streaming Tokens| WS

  WS -->|Update Summary| CSV[(patient_summaries.csv)]

  WS -->|Message Events| MT[Message Tracker]
  MT -->|API| API[/api/messages, /api/stats/]

  UI[Future UI] -->|Fetch Events| API
  UI -->|WebSocket View| WS
```

## Concepts Explained (Separate Section)

### RAG (Retrieval-Augmented Generation)
- The app searches a vector database (Chroma) for the most relevant patients.
- The results become "context" for the summary generator.
- This keeps the LLM grounded in actual patient records instead of guessing.

### WebSocket Communication
- WebSocket keeps a live, two-way connection between client and server.
- This is how streaming responses (token-by-token) are sent in real time.

### MCP (Model Context Protocol)
- MCP provides a standard way to call "tools" such as search or summary generation.
- The client sends JSON-RPC requests like `tools/list` and `tools/call`.
- The server responds with structured results.

### Asynchronous Communication
- WebSockets and LLM streaming are async so the app stays responsive.
- While the model is generating, the server can still send progress updates.

### API Endpoints
- FastAPI exposes REST endpoints for message tracking:
  - `/api/messages` - all events
  - `/api/messages/recent` - latest events
  - `/api/messages/type/...` - filtered by type
  - `/api/stats` - summary stats

### Event Tracking System
- Every action is logged with timestamps and correlation IDs.
- You can separate three views:
  - User input (left pane)
  - Server processing (center pane)
  - WebSocket traffic (right pane)
- This is used for transparency, debugging, and UI timelines.

## What Files Matter Most
- `mcp_server.py` - main server with WebSocket + APIs
- `mcp_client.py` - interactive client
- `message_tracker.py` - event tracking system
- `message_api.py` - API endpoints for events
- `patient_summaries.csv` - generated summaries
- `TESTING_MESSAGE_TRACKING.md` - test instructions
