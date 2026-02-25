# JSON-RPC MCP Demo

Minimal stdio JSON-RPC demo for Celsius to Fahrenheit.

## Run

```bash
python3 mcp_client.py
```

## Server Only

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"convert","params":{"c":25}}' | python3 mcp_server.py
```
