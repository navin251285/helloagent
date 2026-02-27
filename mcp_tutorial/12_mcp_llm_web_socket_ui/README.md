# MCP WebSocket UI (Patient Summaries)

This UI visualizes the full MCP + WebSocket + LLM workflow from the backend in `11_mcp_llm_web_socket`.

## Backend launch (verified)

From `mcp_tutorial/11_mcp_llm_web_socket`:

```bash
python mcp_server.py
```

- WebSocket: `ws://127.0.0.1:8765/mcp`
- REST API: `http://127.0.0.1:8765/api/messages/recent` and `http://127.0.0.1:8765/api/stats`

## UI setup

```bash
cd /home/navinkumar_25_gmail_com/12_mcp_llm_web_socket_ui
npm install
npm run dev
```

## Production build

```bash
cd /home/navinkumar_25_gmail_com/12_mcp_llm_web_socket_ui
npm run build
npm run start
```

The Vite dev server proxies `/mcp` and `/api` to the backend, so you can keep the defaults in the UI.

## What the UI shows

- Tool calls (search, generate, update)
- Streaming tokens from the LLM
- WebSocket requests/responses made by the UI
- Server event logs from the message tracker APIs
- Tool inventory and schemas

## Tip

If you need to bypass the proxy, set the API base field to `http://127.0.0.1:8765` and set the WebSocket path to `/mcp`.
