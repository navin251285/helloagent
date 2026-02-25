# MCP Tutorial (Local Demo)

This folder contains a minimal demo MCP server and a client using HTTP JSON-RPC.

## Run the server

```bash
python3 mcp_server.py
```

## List tools

```bash
python3 mcp_client.py
```

## Call the echo tool

```bash
python3 mcp_client.py --method tools/call --params '{"name":"echo","arguments":{"text":"hello"}}'
```
