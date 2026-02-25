# MCP tools/list Demo

Minimal stdio demo for tools/list and tools/call for Celsius to Fahrenheit.

## List tools

```bash
python3 mcp_client.py
```

## Call tool

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"c_to_f","arguments":{"c":25}}}' | python3 mcp_server.py
```
