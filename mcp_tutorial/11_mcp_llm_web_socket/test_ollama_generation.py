#!/usr/bin/env python3
"""
Quick test: Generate summary with Ollama to verify it works
"""
import asyncio
import json
import websockets


async def test_ollama_summary():
    """Test the generate_summary function with actual Ollama"""
    uri = "ws://127.0.0.1:8765/mcp"
    request_id = 0
    
    def next_id():
        nonlocal request_id
        request_id += 1
        return request_id
    
    print("=" * 80)
    print("🧪 TESTING OLLAMA SUMMARY GENERATION")
    print("=" * 80)
    
    async with websockets.connect(uri, ping_timeout=120, close_timeout=10) as ws:
        # Initialize
        print("\n1️⃣  Connecting...")
        init_req = {"jsonrpc": "2.0", "id": next_id(), "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05", "capabilities": {}, 
                              "clientInfo": {"name": "test", "version": "1.0"}}}
        await ws.send(json.dumps(init_req))
        await ws.recv()
        print("   ✅ Connected")
        
        # Search for a patient
        print("\n2️⃣  Searching for patient...")
        search_req = {"jsonrpc": "2.0", "id": next_id(), "method": "tools/call",
                     "params": {"name": "search_patients_by_disease", 
                               "arguments": {"disease_keyword": "diabetes"}}}
        await ws.send(json.dumps(search_req))
        response = json.loads(await ws.recv())
        
        # Get first patient ID
        search_text = response["result"]["content"][0]["text"]
        patient_id = search_text.split('\n')[2].split('|')[0].split(':')[1].strip()
        print(f"   ✅ Found patient ID: {patient_id}")
        
        # Generate summary with Ollama
        print(f"\n3️⃣  Generating summary with Ollama Phi model...")
        print("   ⏳ This may take 30-60 seconds...")
        
        import time
        start_time = time.time()
        
        gen_req = {"jsonrpc": "2.0", "id": next_id(), "method": "tools/call",
                   "params": {"name": "generate_summary",
                             "arguments": {"patient_id": patient_id}}}
        await ws.send(json.dumps(gen_req))
        
        response = json.loads(await ws.recv())
        elapsed = time.time() - start_time
        
        if "result" in response:
            summary = response["result"]["content"][0]["text"]
            print(f"   ✅ Summary generated in {elapsed:.1f} seconds")
            print(f"\n📄 Generated Summary:")
            print("   " + "-" * 76)
            for line in summary.split('\n')[:10]:  # Show first 10 lines
                print(f"   {line}")
            print("   " + "-" * 76)
            
            print("\n" + "=" * 80)
            print("✅ OLLAMA INTEGRATION WORKING!")
            print("=" * 80)
            return True
        else:
            print(f"   ❌ Error: {response.get('error', 'Unknown error')}")
            return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_ollama_summary())
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
