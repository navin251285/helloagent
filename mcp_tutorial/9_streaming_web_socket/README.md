# MCP Streaming WebSocket Demo

This folder mirrors 8_streaming_sse but uses WebSockets for streaming progress updates.

## Run the server

```bash
python3 mcp_server.py
```

The server listens on ws://127.0.0.1:3000/ws.

## Run the client

```bash
python3 mcp_client.py
```

The client sends the input number and prints each WebSocket message as JSON. The final message includes the updated record ID (or null if no update).

## Example

```
{"input": 9}
{"stage": "operation_selected", "operation": "-", "number": 4}
{"stage": "calculating"}
{"stage": "final", "value": 5}
{"stage": "updated", "updated_id": 5}
```
