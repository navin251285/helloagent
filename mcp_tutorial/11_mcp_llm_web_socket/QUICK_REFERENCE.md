# Quick Reference & Cheat Sheet

## 🚀 Start Here - 30 Second Setup

```bash
# Terminal 1: Start the server
cd /home/navinkumar_25_gmail_com/mcp_tutorial/11_mcp_llm_web_socket
python mcp_server.py

# Terminal 2: Start the client (in another terminal)
python mcp_client.py

# Terminal 3: Monitor in real-time (in another terminal)
watch -n 2 'curl -s http://localhost:8765/api/messages/recent?count=5 | jq'
```

---

## 📋 Client Commands - Copy & Paste

### Search Operations
```bash
# Find patients with specific disease/symptom
search_patients_by_disease diabetes

search_patients_by_disease hypertension

search_patients_by_disease "high blood pressure"

search_patients_by_disease arthritis

search_patients_by_disease fever
```

### AI Summary Generation
```bash
# Generate AI summary for a patient (takes 30-60 seconds)
generate_summary 25

generate_summary 11

generate_summary 45
```

### Save Results
```bash
# Save generated summary to database
update_summary 25

update_summary 11

update_summary 45
```

### View Data
```bash
# List all patients
list_patients

# View all tracked messages
view_messages

# View application info
info
```

### Admin Commands
```bash
# Clear all message logs (start fresh)
clear_data

# Exit the client
exit

quit

quit_client
```

---

## 🔍 Monitor Everything - API Queries

### View Messages

**All messages:**
```bash
curl http://localhost:8765/api/messages/ | jq
```

**Last 10 messages:**
```bash
curl http://localhost:8765/api/messages/recent?count=10 | jq
```

**Last 5 messages (compact):**
```bash
curl http://localhost:8765/api/messages/recent?count=5 | \
  jq '.messages[] | {type: .message_type, source, duration}'
```

### Filter by Operation Type

**Search operations:**
```bash
curl http://localhost:8765/api/messages/type/chroma_search | jq '.messages | length'
```

**AI generation operations:**
```bash
curl http://localhost:8765/api/messages/type/ollama_stream_complete | jq '.count'
```

**Database writes:**
```bash
curl http://localhost:8765/api/messages/type/csv_write | jq '.messages[] | {duration, status}'
```

**Errors:**
```bash
curl http://localhost:8765/api/messages/type/error_occurred | jq '.messages'
```

### Filter by Patient

**All messages for patient 25:**
```bash
curl http://localhost:8765/api/messages/patient/25 | jq '.count'
```

**What happened with patient 25:**
```bash
curl http://localhost:8765/api/messages/patient/25 | \
  jq '.messages[] | {type: .message_type, duration}'
```

### Trace Complete Operation

**Get correlation ID from recent messages:**
```bash
CORR_ID=$(curl -s http://localhost:8765/api/messages/recent?count=1 | \
  jq -r '.messages[0].correlation_id')
echo $CORR_ID
```

**See complete operation journey:**
```bash
curl http://localhost:8765/api/messages/correlation/$CORR_ID | \
  jq '.messages[] | {type: .message_type, duration, status}'
```

** Or do it in one command:**
```bash
curl http://localhost:8765/api/messages/recent?count=1 | \
  jq -r '.messages[0].correlation_id' | \
  xargs -I {} curl -s http://localhost:8765/api/messages/correlation/{} | \
  jq '.messages[] | {type: .message_type, duration}'
```

### System Statistics

**Overall stats:**
```bash
curl http://localhost:8765/api/stats | jq
```

**Just the stats (no full data):**
```bash
curl http://localhost:8765/api/stats | jq '.statistics'
```

**Message count:**
```bash
curl http://localhost:8765/api/messages/ | jq '.count'
```

**Average operation time:**
```bash
curl http://localhost:8765/api/stats | jq '.statistics.average_duration_ms'
```

**Data throughput:**
```bash
curl http://localhost:8765/api/stats | jq '.statistics.total_data_bytes'
```

### Clear Data

**Reset all message logs:**
```bash
curl -X POST http://localhost:8765/api/messages/clear
```

---

## 🎯 Common Workflows

### Workflow 1: Search → Generate Summary → Save

```bash
# Step 1: Search for patients with condition
> search_patients_by_disease diabetes

[Shows patient list]

# Step 2: Generate summary for one patient (takes 30-60s)
> generate_summary 25

[AI generates medical summary...]

# Step 3: Save the summary
> update_summary 25

[Summary saved to database]

# Step 4: Verify in another terminal
curl http://localhost:8765/api/messages/recent?count=10 | jq
```

### Workflow 2: Monitor Performance

**Terminal 1:**
```bash
# Running a search
python mcp_client.py
> search_patients_by_disease hypertension
```

**Terminal 2:**
```bash
# Monitor in real-time
while true; do
  echo "=== $(date) ==="
  curl -s http://localhost:8765/api/stats | jq '.statistics | {total_messages, time_span_ms, average_duration_ms}'
  sleep 3
done
```

### Workflow 3: Troubleshoot Issues

```bash
# Check for errors
curl http://localhost:8765/api/messages/type/error_occurred | jq

# If errors exist, get details
curl http://localhost:8765/api/messages/type/error_occurred | \
  jq '.messages[] | {timestamp, content, correlation_id}'

# Find the operation that failed using correlation ID
CORR_ID="<paste-correlation-id>"
curl http://localhost:8765/api/messages/correlation/$CORR_ID | \
  jq '.messages'
```

### Workflow 4: Test System Health

```bash
# Run all tests
python test_message_tracking.py

# Check if all endpoints respond
curl http://localhost:8765/api/messages/ -w "\nStatus: %{http_code}\n"
curl http://localhost:8765/api/stats -w "\nStatus: %{http_code}\n"
curl http://localhost:8765/api/messages/recent -w "\nStatus: %{http_code}\n"
```

---

## 📊 Useful Queries (One-Liners)

```bash
# Count total messages
curl -s http://localhost:8765/api/messages/ | jq '.count'

# Show message types (raw)
curl -s http://localhost:8765/api/messages/ | jq '.messages[] | .message_type' | sort | uniq -c

# Show message sources (raw)
curl -s http://localhost:8765/api/messages/ | jq '.messages[] | .source' | sort | uniq -c

# Find slowest operation
curl -s http://localhost:8765/api/messages/ | jq '.messages[] | select(.duration != null) | {type: .message_type, duration}' | sort -k3 -rn | head -5

# Find all patient 25 operations with times
curl -s http://localhost:8765/api/messages/patient/25 | jq '.messages[] | {type: .message_type, duration, timestamp}' | jq -s 'sort_by(.timestamp)'

# Calculate total time spent on operations
curl -s http://localhost:8765/api/messages/ | jq '[.messages[] | .duration? | select(. != null)] | add'

# Show latest 3 complete operations
curl -s http://localhost:8765/api/messages/type/tool_call_complete | jq '.messages[-3:] | .[] | {timestamp, duration}'

# Check if system is healthy (zero errors)
curl -s http://localhost:8765/api/messages/type/error_occurred | jq '.count'
```

---

## ⚙️ Configuration

### Port Configuration
Server runs on port **8765** by default. To change:

Edit `mcp_server.py` line ~975:
```python
uvicorn.run(
    fastapi_app,
    host="127.0.0.1",
    port=8765,  # ← Change this
)
```

### Client Configuration
Edit `mcp_client.py` line ~24:
```python
def __init__(self, uri="ws://127.0.0.1:8765/mcp"):  # ← Change this
```

### WebSocket Timeouts
Edit `mcp_server.py` line ~975:
```python
uvicorn.run(
    fastapi_app,
    host="127.0.0.1",
    port=8765,
    ws_ping_interval=30,      # ← Ping every 30s
    ws_ping_timeout=120,      # ← 2 minute timeout
    timeout_keep_alive=120,   # ← Keep alive 2 min
)
```

---

## 🔥 Pro Tips

### Tip 1: Real-Time Monitoring Dashboard
```bash
# Create a simple dashboard
while true; do
  clear
  echo "╔════════ PATIENT SYSTEM STATUS ════════╗"
  echo "║ Time: $(date '+%H:%M:%S')"
  echo "║ Total Messages: $(curl -s http://localhost:8765/api/messages/ | jq '.count')"
  echo "║ Avg Duration: $(curl -s http://localhost:8765/api/stats | jq '.statistics.average_duration_ms')ms"
  echo "║ Total Data: $(curl -s http://localhost:8765/api/stats | jq '.statistics.total_data_bytes')B"
  echo "║ Errors: $(curl -s http://localhost:8765/api/messages/type/error_occurred | jq '.count')"
  echo "║ Sources: $(curl -s http://localhost:8765/api/stats | jq '.statistics.unique_sources')"
  echo "╚════════════════════════════════════╝"
  sleep 3
done
```

### Tip 2: Export Messages to CSV
```bash
# Export all messages
curl -s http://localhost:8765/api/messages/ | \
  jq -r '.messages[] | [.timestamp, .message_type, .source, .duration] | @csv' > messages.csv
```

### Tip 3: Filter and Count by Correlation ID
```bash
# How many unique operations?
curl -s http://localhost:8765/api/messages/ | jq '.messages[] | .correlation_id' | sort -u | wc -l
```

### Tip 4: Performance Profile
```bash
# Which operations take longest?
curl -s http://localhost:8765/api/messages/ | \
  jq '[.messages[] | select(.duration != null)] | group_by(.message_type) | .[] | {type: .[0].message_type, total: (map(.duration) | add), count: length, avg: ((map(.duration) | add) / length)}' | jq -s 'sort_by(-.total)'
```

### Tip 5: Track Single Patient Journey
```bash
# See everything that happened to patient 25
curl -s http://localhost:8765/api/messages/patient/25 | \
  jq '.messages | map({time: .timestamp, type: .message_type, duration}) | sort_by(.time)'
```

---

## 🐛 Troubleshooting Quick Ref

| Problem | Check | Solution |
|---------|-------|----------|
| **Server won't start** | Port 8765 in use | `lsof -i :8765` and kill the process |
| **Client can't connect** | Server running? | Check `python mcp_server.py` is active |
| **Search is slow** | Chroma loading slow? | Normal for first search (loads 356 profiles) |
| **AI generation hangs** | Ollama running? | Verify Ollama is installed and running |
| **Messages not appearing** | Tracking enabled? | Check server logs for errors |
| **API returns 404** | Endpoint typo? | Check endpoint spelling, must be exact |
| **Old messages visible** | Not cleared? | Run `clear_data` in client or `POST /api/messages/clear` |

---

## 📁 Important Files Location

```
11_mcp_llm_web_socket/
├── mcp_server.py          ← Run this first (python mcp_server.py)
├── mcp_client.py          ← Run this second (python mcp_client.py)
├── message_tracker.py     ← Message logging system
├── message_api.py         ← REST API endpoints
├── test_message_tracking.py ← Run tests (python test_message_tracking.py)
├── patients_data.csv      ← Patient health data
├── patient_summaries.csv  ← Generated summaries (updates here)
├── patient_embeddings.csv ← Vector embeddings
├── chroma_db/             ← Vector database
├── README_COMPLETE.md     ← This documentation
├── ARCHITECTURE_DIAGRAMS.md ← Visual architecture
└── TESTING_MESSAGE_TRACKING.md ← Testing guide
```

---

## 🎓 Learning Path

1. **Start Here:** Read `README_COMPLETE.md` (explanations for lay people)
2. **See It Work:** Run `mcp_client.py` and try commands
3. **Understand Flow:** Read `ARCHITECTURE_DIAGRAMS.md` (visual explanations)
4. **Know The Concepts:** Read concepts section in `README_COMPLETE.md`
5. **Test It:** Run `test_message_tracking.py` to validate everything
6. **Monitor:** Use API queries to see what's happening
7. **Debug:** Use message tracking to investigate issues

---

## 📞 Quick Support

**Q: How do I know if it's working?**
```bash
curl http://localhost:8765/api/messages/ | jq '.count'
# If you get a number > 0, it's working!
```

**Q: Where do I find the errors?**
```bash
curl http://localhost:8765/api/messages/type/error_occurred | jq
```

**Q: How long did that last operation take?**
```bash
curl http://localhost:8765/api/messages/recent?count=1 | jq '.messages[0] | {type: .message_type, duration}'
```

**Q: Show me everything for patient 25:**
```bash
curl http://localhost:8765/api/messages/patient/25 | jq '.messages | length'
```

**Q: Is the system healthy?**
```bash
curl http://localhost:8765/api/stats | jq '.statistics | {total_messages, average_duration_ms, error_count: 0}'
```

---

**Save this file for quick reference while using the application!**
