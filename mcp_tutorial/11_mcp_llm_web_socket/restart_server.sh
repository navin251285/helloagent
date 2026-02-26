#!/bin/bash
# Restart the MCP WebSocket Server

echo "🔄 Restarting MCP WebSocket Server..."
echo

# Stop the old server
echo "1. Stopping old server..."
pkill -f "python.*mcp_server.py" 2>/dev/null || pkill -9 -f "python.*mcp_server.py" 2>/dev/null
sleep 2

# Check if stopped
if ps aux | grep -v grep | grep "mcp_server.py" > /dev/null; then
    echo "   ⚠️  Server still running. Please manually stop it with Ctrl+C in the server terminal."
    echo "   Or run: pkill -9 -f 'python.*mcp_server.py'"
    exit 1
else
    echo "   ✅ Old server stopped"
fi

echo
echo "2. Starting new server with updated code..."
echo "   Server will run on ws://127.0.0.1:8765/mcp"
echo "   Press Ctrl+C to stop"
echo
echo "----------------------------------------"

# Start the new server
python3 mcp_server.py
