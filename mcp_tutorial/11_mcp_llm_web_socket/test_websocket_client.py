#!/usr/bin/env python3
"""
Test WebSocket connection and search
"""
import asyncio
import json
import websockets


async def test_search():
    uri = "ws://127.0.0.1:8765/mcp"
    
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected to server")
            
            # Initialize
            request_id = 1
            init_request = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test-client", "version": "1.0.0"}
                }
            }
            
            await websocket.send(json.dumps(init_request))
            response = await websocket.recv()
            print(f"✅ Initialized: {json.loads(response)['result']['serverInfo']['name']}")
            
            # Test search
            request_id += 1
            search_request = {
                "jsonrpc": "2.0",
                "id": request_id,
                "method": "tools/call",
                "params": {
                    "name": "search_patients_by_disease",
                    "arguments": {"disease_keyword": "diabetes"}
                }
            }
            
            print("\n📤 Sending search request for 'diabetes'...")
            await websocket.send(json.dumps(search_request))
            
            print("⏳ Waiting for response...")
            response_text = await websocket.recv()
            response = json.loads(response_text)
            
            print("\n📥 Response received:")
            print(json.dumps(response, indent=2))
            
            if "result" in response:
                content = response["result"].get("content", [])
                if content:
                    print("\n📝 Search result text:")
                    print(content[0]["text"])
            elif "error" in response:
                print(f"\n❌ Error: {response['error']}")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_search())
