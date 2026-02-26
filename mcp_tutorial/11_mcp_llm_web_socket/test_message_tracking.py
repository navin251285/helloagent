#!/usr/bin/env python3
"""
Quick test script for message tracking system.
Tests the message tracking API endpoints and runs basic operations.
"""

import asyncio
import json
import sys
import time
from typing import Optional
import httpx
import websockets

# Colors for output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
BLUE = '\033[94m'

BASE_URL = "http://localhost:8765"
WS_URL = "ws://localhost:8765/mcp"

async def test_api_endpoints():
    """Test all message tracking API endpoints."""
    print(f"\n{BLUE}=== Testing Message Tracking API ==={RESET}\n")
    
    async with httpx.AsyncClient() as client:
        # Test 1: Get all messages
        print(f"{YELLOW}1. Testing GET /api/messages/{RESET}")
        try:
            response = await client.get(f"{BASE_URL}/api/messages/")
            if response.status_code == 200:
                data = response.json()
                print(f"{GREEN}✓ Success{RESET} - Found {data['count']} messages")
            else:
                print(f"{RED}✗ Failed{RESET} - Status {response.status_code}")
        except Exception as e:
            print(f"{RED}✗ Error: {e}{RESET}")
        
        # Test 2: Get recent messages
        print(f"\n{YELLOW}2. Testing GET /api/messages/recent{RESET}")
        try:
            response = await client.get(f"{BASE_URL}/api/messages/recent?count=5")
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('messages', []))
                print(f"{GREEN}✓ Success{RESET} - Retrieved {count} recent messages")
                if count > 0:
                    msg = data['messages'][0]
                    print(f"  Latest message: {msg['message_type']} ({msg['source']})")
            else:
                print(f"{RED}✗ Failed{RESET} - Status {response.status_code}")
        except Exception as e:
            print(f"{RED}✗ Error: {e}{RESET}")
        
        # Test 3: Get statistics
        print(f"\n{YELLOW}3. Testing GET /api/stats{RESET}")
        try:
            response = await client.get(f"{BASE_URL}/api/stats")
            if response.status_code == 200:
                data = response.json()
                stats = data['statistics']
                print(f"{GREEN}✓ Success{RESET}")
                print(f"  Total messages: {stats['total_messages']}")
                print(f"  Time span: {stats['time_span_ms']}ms")
                if stats['total_messages'] > 0:
                    print(f"  Avg duration: {stats['average_duration_ms']:.2f}ms")
            else:
                print(f"{RED}✗ Failed{RESET} - Status {response.status_code}")
        except Exception as e:
            print(f"{RED}✗ Error: {e}{RESET}")
        
        # Test 4: Test message filtering by type
        print(f"\n{YELLOW}4. Testing GET /api/messages/type/tool_call_start{RESET}")
        try:
            response = await client.get(f"{BASE_URL}/api/messages/type/tool_call_start")
            if response.status_code == 200:
                data = response.json()
                count = len(data.get('messages', []))
                print(f"{GREEN}✓ Success{RESET} - Found {count} tool_call_start messages")
            else:
                print(f"{RED}✗ Failed{RESET} - Status {response.status_code}")
        except Exception as e:
            print(f"{RED}✗ Error: {e}{RESET}")
        
        # Test 5: Verify message schema
        print(f"\n{YELLOW}5. Verifying Message Schema{RESET}")
        try:
            response = await client.get(f"{BASE_URL}/api/messages/recent?count=1")
            if response.status_code == 200:
                data = response.json()
                messages = data.get('messages', [])
                if messages:
                    msg = messages[0]
                    required_fields = [
                        'id', 'correlation_id', 'source', 'message_type',
                        'timestamp', 'content', 'status'
                    ]
                    missing = [f for f in required_fields if f not in msg]
                    if missing:
                        print(f"{RED}✗ Missing fields: {missing}{RESET}")
                    else:
                        print(f"{GREEN}✓ Message schema valid{RESET}")
                        print(f"  Fields: {', '.join(required_fields)}")
                else:
                    print(f"{YELLOW}⚠ No messages found - run an operation first{RESET}")
            else:
                print(f"{RED}✗ Failed{RESET}")
        except Exception as e:
            print(f"{RED}✗ Error: {e}{RESET}")

async def test_websocket_connection():
    """Test WebSocket connection and MCP protocol."""
    print(f"\n{BLUE}=== Testing WebSocket Connection ==={RESET}\n")
    
    try:
        async with websockets.connect(WS_URL) as websocket:
            print(f"{GREEN}✓ WebSocket connected{RESET}")
            
            # Send tools/list request
            print(f"\n{YELLOW}Requesting tools list...{RESET}")
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            await websocket.send(json.dumps(request))
            
            # Receive response
            response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
            data = json.loads(response)
            
            if "result" in data:
                tools = data["result"].get("tools", [])
                print(f"{GREEN}✓ Received tools list{RESET}")
                print(f"  Available tools: {len(tools)}")
                for tool in tools:
                    print(f"    - {tool['name']}: {tool.get('description', 'No description')}")
            else:
                print(f"{RED}✗ Error in response{RESET}")
                print(json.dumps(data, indent=2))
                
    except asyncio.TimeoutError:
        print(f"{RED}✗ Timeout waiting for response{RESET}")
    except ConnectionRefusedError:
        print(f"{RED}✗ WebSocket connection refused - Is server running?{RESET}")
    except Exception as e:
        print(f"{RED}✗ Error: {e}{RESET}")

async def test_search_operation():
    """Test a search operation and verify message logging."""
    print(f"\n{BLUE}=== Testing Search Operation ==={RESET}\n")
    
    async with httpx.AsyncClient() as client:
        # Clear previous messages
        print(f"{YELLOW}Clearing previous messages...{RESET}")
        await client.post(f"{BASE_URL}/api/messages/clear")
        
        # Get initial count
        response = await client.get(f"{BASE_URL}/api/messages/")
        initial_count = response.json()['count']
        print(f"Initial message count: {initial_count}")
        
        # Perform search via WebSocket
        print(f"\n{YELLOW}Performing search operation...{RESET}")
        try:
            async with websockets.connect(WS_URL) as websocket:
                # Initialize
                init_request = {
                    "jsonrpc": "2.0",
                    "id": 1,
                    "method": "initialize",
                    "params": {}
                }
                await websocket.send(json.dumps(init_request))
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                print(f"{GREEN}✓ Connection initialized{RESET}")
                
                # Call search tool
                search_request = {
                    "jsonrpc": "2.0",
                    "id": 2,
                    "method": "tools/call",
                    "params": {
                        "name": "search_patients_by_disease",
                        "arguments": {
                            "disease": "diabetes"
                        }
                    }
                }
                await websocket.send(json.dumps(search_request))
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                result = json.loads(response)
                
                if "result" in result:
                    print(f"{GREEN}✓ Search completed successfully{RESET}")
                else:
                    print(f"{YELLOW}⚠ Search returned error{RESET}")
                
        except Exception as e:
            print(f"{RED}✗ Search operation failed: {e}{RESET}")
            return
        
        # Check messages logged
        print(f"\n{YELLOW}Checking logged messages...{RESET}")
        await asyncio.sleep(0.5)  # Wait for messages to be logged
        
        response = await client.get(f"{BASE_URL}/api/messages/")
        final_count = response.json()['count']
        new_messages = final_count - initial_count
        
        print(f"Messages logged: {new_messages}")
        
        if new_messages > 0:
            print(f"{GREEN}✓ Messages were logged{RESET}")
            
            # Show message types
            response = await client.get(f"{BASE_URL}/api/messages/recent?count={new_messages}")
            messages = response.json()['messages']
            
            print(f"\nMessage sequence:")
            for msg in reversed(messages):
                duration = f" ({msg.get('duration', '?')}ms)" if msg.get('duration') else ""
                print(f"  - {msg['message_type']}{duration}")
                
            # Check correlation
            if len(messages) > 1:
                corr_id = messages[0]['correlation_id']
                all_same = all(m['correlation_id'] == corr_id for m in messages)
                if all_same:
                    print(f"{GREEN}✓ All messages share same correlation ID{RESET}")
                else:
                    print(f"{YELLOW}⚠ Correlation IDs don't match{RESET}")
        else:
            print(f"{YELLOW}⚠ No messages logged{RESET}")

async def main():
    """Run all tests."""
    print(f"\n{BLUE}{'=' * 50}")
    print("Message Tracking System Test Suite")
    print(f"{'=' * 50}{RESET}")
    
    # Check server is running
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/api/messages/", timeout=2.0)
    except Exception as e:
        print(f"\n{RED}✗ Server not responding at {BASE_URL}{RESET}")
        print(f"  Error: {e}")
        print(f"\nStart the server first:")
        print(f"  python mcp_server.py")
        sys.exit(1)
    
    # Run tests
    await test_api_endpoints()
    await test_websocket_connection()
    await test_search_operation()
    
    print(f"\n{BLUE}{'=' * 50}")
    print("Tests completed!")
    print(f"{'=' * 50}{RESET}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{YELLOW}Tests interrupted{RESET}")
        sys.exit(0)
