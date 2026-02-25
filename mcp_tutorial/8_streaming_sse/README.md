# MCP Streaming SSE Demo

This folder uses a FastAPI async server with Server-Sent Events (SSE). The server computes the random operation, updates the CSV, and streams progress back to the client.

## Run the server

```bash
python3 mcp_server.py
```

The server listens on http://127.0.0.1:3000/stream.

## Run the client

```bash
python3 mcp_client.py
```

The client sends the input number and prints each SSE message as JSON. The final message includes the updated record ID (or null if no update).

## Example

```
{"input": 9}
{"stage": "operation_selected", "operation": "-", "number": 4}
{"stage": "calculating"}
{"stage": "final", "value": 5}
{"stage": "updated", "updated_id": 5}
```
