# Testing Message Tracking System

## Quick Start

### 1. Start the Server
```bash
cd /home/navinkumar_25_gmail_com/mcp_tutorial/11_mcp_llm_web_socket
python mcp_server.py
```

The server starts on `http://localhost:8000` with WebSocket on `ws://localhost:8000/mcp`

### 2. Test Message API Endpoints

Open a new terminal and test these endpoints:

#### Get All Messages
```bash
curl http://localhost:8000/api/messages/ | jq
```

#### Get Recent Messages (last 10)
```bash
curl http://localhost:8000/api/messages/recent?count=10 | jq
```

#### Get Statistics
```bash
curl http://localhost:8000/api/stats | jq
```

#### Get Messages by Type
```bash
curl "http://localhost:8000/api/messages/type/tool_call_start" | jq
```

#### Get Messages by Source
```bash
curl "http://localhost:8000/api/messages/source/WEBSOCKET_SEND" | jq
```

#### Get Messages by Patient ID
```bash
curl "http://localhost:8000/api/messages/patient/25" | jq
```

### 3. Test with WebSocket Client

Use the provided test client:

```bash
python test_message_tracking.py
```

Or use the interactive client to manually test operations:

```bash
python mcp_client.py
```

Then in the client, try:
1. **Search patients**: `search_patients_by_disease diabetes`
2. **Generate summary**: `generate_summary 25`
3. **Update summary**: `update_summary 25`
4. **View raw summary in CSV**: Check `patient_summaries.csv`

## Expected Message Flow

### For a Search Operation
Messages logged:
1. `user_search` - Initial search request
2. `chroma_search` - Chroma DB search start
3. `chroma_search_results` - Results returned with count
4. `operation_complete` - Search finished with duration

Example query:
```bash
curl http://localhost:8000/api/messages/type/chroma_search | jq
```

### For a Summary Generation (Ollama Streaming)
Messages logged:
1. `tool_call_start` - Generation started
2. `ollama_stream_start` - Ollama connection
3. `stream_token` - Every 10 tokens (progress updates)
4. `ollama_stream_complete` - Generation finished with token count
5. `tool_call_complete` - Tool call finished

Example query:
```bash
curl http://localhost:8000/api/messages/type/ollama_stream_start | jq
```

### For a CSV Update Operation
Messages logged:
1. `tool_call_start` - Update started
2. `csv_read` - Patient record read with count
3. `csv_write` - Summary written
4. `tool_call_complete` - Update finished

Example query:
```bash
curl http://localhost:8000/api/messages/type/csv_write | jq
```

## Detailed Testing Checklist

### ✓ Message Schema Validation
Check that messages contain all expected fields:
```bash
curl http://localhost:8000/api/messages/recent?count=1 | jq '.messages[0]'
```

Expected fields in each message:
- `id` (UUID)
- `correlation_id` (UUID) 
- `source` (MessageSource enum)
- `message_type` (MessageType enum)
- `timestamp` (milliseconds)
- `duration` (milliseconds, if applicable)
- `latency` (milliseconds, if applicable)
- `content` (varies by type)
- `message_size` (bytes)
- `status` (success/error)

### ✓ Correlation ID Tracking
All related messages should share the same `correlation_id`:

```bash
# Get a correlation ID from a recent message
CORR_ID=$(curl -s http://localhost:8000/api/messages/recent?count=1 | jq -r '.messages[0].correlation_id')

# Find all messages with that correlation ID
curl "http://localhost:8000/api/messages/correlation/$CORR_ID" | jq
```

You should see 3-5 messages all with the same `correlation_id` showing the operation flow.

### ✓ Timing Measurements
Verify duration and latency are captured:

```bash
curl http://localhost:8000/api/messages/type/tool_call_complete | jq '.messages[] | {message_type, duration, status}'
```

Look for non-zero `duration` values in milliseconds.

### ✓ Patient ID Tracking
Verify patient operations are logged with patient_id:

```bash
curl "http://localhost:8000/api/messages/patient/25" | jq '.messages | length'
```

Should show messages from your patient operations.

### ✓ Statistics
Check aggregated stats:

```bash
curl http://localhost:8000/api/stats | jq
```

Expected output includes:
- `total_messages`: Total number of messages logged
- `message_sources`: Count by source
- `message_types`: Count by type
- `time_span_ms`: Duration from first to last message
- `average_duration_ms`: Average operation duration

## Clear Messages for Fresh Test
To clear all messages and start fresh:

```bash
curl -X POST http://localhost:8000/api/messages/clear | jq
```

Then run a single operation and check messages:
```bash
# Clear
curl -X POST http://localhost:8000/api/messages/clear

# Run operation (example: search)
# In mcp_client.py: search_patients_by_disease diabetes

# Check what was logged
curl http://localhost:8000/api/messages/ | jq
```

## Debugging Tips

### Check Server Logs
The server prints diagnostic info to stderr:

```bash
python mcp_server.py 2>&1 | grep -i message
```

### Verify WebSocket Connection
The initial connection should log a CONNECTION message:

```bash
curl http://localhost:8000/api/messages/type/CONNECTION | jq '.messages[0]'
```

### Check for Errors
Find any error messages:

```bash
curl http://localhost:8000/api/messages/type/ERROR_OCCURRED | jq '.messages | length'
```

If errors exist, examine them:

```bash
curl http://localhost:8000/api/messages/type/ERROR_OCCURRED | jq '.messages[] | {timestamp, content}'
```

### Verify Message Sizes
Confirm WebSocket message sizes are captured:

```bash
curl http://localhost:8000/api/messages/source/WEBSOCKET_SEND | jq '.messages[] | {message_type, message_size}'
```

## Testing Workflow

**Complete End-to-End Test:**

```bash
# 1. Clear previous messages
curl -X POST http://localhost:8000/api/messages/clear

# 2. Run operation via mcp_client.py
# Option A: Search
#   > search_patients_by_disease diabetes

# Option B: Generate summary  
#   > generate_summary 25

# Option C: Update summary
#   > update_summary 25

# 3. Query results
curl http://localhost:8000/api/messages/ | jq '{total: .count, messages: .messages | length}'

# 4. Check correlation
CORR_ID=$(curl -s http://localhost:8000/api/messages/recent?count=1 | jq -r '.messages[0].correlation_id')
curl "http://localhost:8000/api/messages/correlation/$CORR_ID" | jq '.messages | map({type: .message_type, duration})'

# 5. View stats
curl http://localhost:8000/api/stats | jq
```

## Next Steps

Once message tracking is working:

1. **Build UI Consumer**: Use `/api/messages/recent?count=50` polling to populate three-pane UI
2. **Implement WebSocket Subscription**: Optional - for real-time message stream
3. **Create Message Timeline**: Display operation sequence with durations
4. **Add Latency Visualization**: Show WebSocket round-trip times

## Troubleshooting

### No messages appearing?
- Check server is running: `curl http://localhost:8000/api/messages/ -w "\n"`
- Check WebSocket connection logged: `curl http://localhost:8000/api/messages/type/CONNECTION`
- Verify operation completed: Check server stderr for errors

### Correlation IDs not matching?
- Each operation should have unique `correlation_id`
- All sub-messages in that operation should share the same `correlation_id`
- Check latest messages: `curl http://localhost:8000/api/messages/recent?count=5`

### Message sizes showing 0?
- Verify `message_size` parameters are passed in log_message() calls
- Check server isn't truncating messages in JSON encoding

### Missing timestamps?
- All messages auto-generate timestamps in milliseconds
- Check `timestamp` field exists: `curl http://localhost:8000/api/messages/recent?count=1 | jq '.messages[0].timestamp'`
