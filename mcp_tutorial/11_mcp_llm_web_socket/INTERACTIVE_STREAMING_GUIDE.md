# Interactive LLM Streaming - User Guide

## Overview

Both interactive clients now support **real-time LLM token streaming**:
- **Tokens appear as they're generated** (30-60 seconds)
- **Complete summary saved to CSV** (not partial tokens)
- **Clear visual indicators** of streaming progress

## Two Ways to Run Streaming Demo

### Option 1: Simplified Interactive Demo (Recommended)

```bash
cd mcp_tutorial/11_mcp_llm_web_socket
python3 interactive_streaming_demo.py
```

**Features:**
- Clean, focused workflow
- Clear "STREAMING IN PROGRESS" messaging
- Perfect for demos
- Great first experience

**Example interaction:**
```
🎯 STREAMING LLM DEMO - Interactive Patient Summary Generation

[STEP 1] 🔍 SEARCH FOR PATIENTS
Enter disease/symptom to search for: diabetes

Found 5 patients matching 'diabetes':
1. ID: 11  | Name: Jerry Rivera
2. ID: 45  | Name: Janet Torres
...

[STEP 2] 📋 SELECT PATIENT
Enter patient ID: 45

[STEP 3] 🚀 GENERATE SUMMARY WITH STREAMING
⏳ Generating clinical summary...
📡 Tokens will appear below as the Phi model generates them

================================================================================
LIVE STREAMING TOKENS - Watch as the summary is generated:
================================================================================

[🔄 Streaming] Starting token stream:  Based on Janet Torres' medical history, 
age, and current symptoms, it is concerning that she has high blood pressure,
diabetes, and arthritis as well as confusion and difficulty breathing...

[STEP 4] 💾 SAVE TO CSV
Save this summary to patient_summaries.csv? (y/n): y
✅ Summary saved!
```

### Option 2: Full Interactive Workflow

```bash
python3 mcp_client.py
```

**Features:**
- Complete CLI workflow
- Multiple patient processing
- All MCP protocol details visible
- Production-ready

**Key difference:** Same streaming, but more detailed output

## What You'll See During Streaming

### Clear Progress Indicators

```
STEP 3: GENERATE SUMMARY USING OLLAMA PHI LLM (WITH STREAMING TOKENS)
--------
⏳ Generating clinical summary using Phi model...
   📡 Will show tokens in real-time as they are generated (30-60 seconds)
[Progress] Sending patient data to Ollama...
[Progress] LLM inference in progress... (WebSocket timeout: 120s)

LIVE STREAMING TOKENS - Watch as the summary is generated token-by-token:
========================================================================
```

### Token Stream Display

The client shows tokens appearing in real-time:

```
[Streaming] 🔄 Starting token stream:  Based on Janet Torres' medical history, 
age, and current symptoms, it is concerning that she has high blood pressure, 
diabetes, and arthritis as well as confusion and difficulty breathing...
[Streaming] Tokens complete
```

### Server-Side Progress

The server logs show real-time progress (visible in server terminal):

```
[OLLAMA] Starting streaming summary generation for Janet Torres...
[OLLAMA] 🔄 Receiving streaming tokens...
[OLLAMA] 📝 Received 10 tokens (~45 chars)...
[OLLAMA] 📝 Received 20 tokens (~97 chars)...
[OLLAMA] 📝 Received 30 tokens (~150 chars)...
[OLLAMA] 📝 Received 40 tokens (~214 chars)...
[OLLAMA] ✅ Streaming complete (86 tokens, 500 chars)
```

## How Streaming Works

### 1. **Initialization** (1-2s)
- Client connects to WebSocket
- Server initializes MCP protocol

### 2. **Search** (1-2s)
- User enters disease keyword
- Chroma DB semantic search
- Results displayed

### 3. **Selection** (0s)
- User selects patient from results
- Patient details retrieved

### 4. **Generation with Streaming** (30-60s)
```
Timeline:
├─ 0-5s:   Connect to Ollama Phi model
├─ 5-30s:  LLM generates tokens (you see them appearing!)
│         [🔄 Streaming] Token 1: "Based"
│         [🔄 Streaming] Token 2: "on"
│         [🔄 Streaming] Token 3: "Janet's..."
└─ 30-60s: Rest of summary generated
```

### 5. **Save** (1-2s)
- Complete summary saved to CSV
- Not the streaming tokens, but full final summary

## Key Features

### ✅ Real-Time Token Display
```
[🔄 Streaming] Starting token stream:  Based on Janet Torres' medical history, 
age, and current symptoms, it is concerning that she has high blood pressure...
```

Tokens appear character by character as Phi model generates them.

### ✅ Complete Summary Persistence
```
CSV before: Patient 45 | Janet Torres | (empty summary)
CSV after:  Patient 45 | Janet Torres | "Based on Janet Torres' medical history..."
```

Only the **complete, polished summary** is saved (not partial streaming text).

### ✅ Non-Blocking Display
- Tokens stream while server continues processing
- No artificial delays
- Live feedback of model's thinking

### ✅ Transparent Logging
- `[WebSocket]` - Connection messages
- `[MCP Protocol]` - Protocol messages
- `[Ollama]` - Model generation progress
- `[🔄 Streaming]` - Token streaming
- `[Tool Call]` - Function invocations

## Test Scenarios

### Scenario 1: Quick Demo (2-3 minutes)

```bash
python3 interactive_streaming_demo.py
# Input: diabetes → 11 → y → Done
# Shows: One full streaming cycle
```

### Scenario 2: Multiple Patients

```bash
python3 mcp_client.py
# Search diabetes → Patient 11 → Save → Search hypertension → Patient 45 → Save
# Shows: Multiple streaming cycles with different patients
```

### Scenario 3: Production Workflow

```bash
python3 mcp_client.py
# Search with different keywords
# Process different patients
# Save all summaries to CSV
```

## CSV Verification

After running, check that summaries were saved:

```bash
# View specific patient summary
grep "^45," patient_summaries.csv

# Expected output:
# 45,Janet Torres,"Based on Janet Torres' medical history, age..."
```

## Troubleshooting

### Tokens Not Visible
- **Check:** Server is running (`ps aux | grep mcp_server.py`)
- **Check:** Ollama is running (`ollama serve`)
- **Check:** WebSocket connection successful (look for `[WebSocket] ✅ Connected`)

### Streaming Seems Slow
- **Normal:** Token rate is 5-10 tokens/second (depends on system)
- **Normal:** Full summary takes 30-60 seconds
- **Check:** Network latency with `ping 127.0.0.1`

### CSV Not Updating
- **Check:** Summary is at least 100 characters
- **Check:** CSV file is writable (`ls -la patient_summaries.csv`)
- **Check:** Patient ID is 1-100

### WebSocket Timeout
- **Check:** Ollama model is responsive (`curl http://localhost:11434/api/tags`)
- **Check:** System resources (RAM, CPU) are available
- **Check:** Timeouts are set to 120s (already configured)

## Performance Metrics

Typical performance from test runs:

| Metric | Time |
|--------|------|
| Connection | 1-2 seconds |
| Search | 1-2 seconds |
| First token visible | 5-10 seconds |
| Complete summary | 35-55 seconds |
| CSV write | <500ms |
| **Total** | **40-70 seconds** |

## Architecture

```
Client (interactive_streaming_demo.py or mcp_client.py)
  ↓ (WebSocket JSON-RPC)
Server (mcp_server.py)
  ├─ Generate summary with Ollama (streaming=True)
  └─ Send tokens to client via WebSocket
       ↓ (stream_token messages)
  Client receives and displays tokens in real-time
```

## Next Steps

1. **First time?** → Run `interactive_streaming_demo.py`
2. **Want full details?** → Run `mcp_client.py`
3. **Multiple patients?** → Use either with different search terms
4. **Verify results?** → Check `patient_summaries.csv`

---

**Streaming is production-ready! Enjoy seeing the Phi model generate summaries in real-time.** 🚀
