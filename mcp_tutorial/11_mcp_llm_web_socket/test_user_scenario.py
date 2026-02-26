#!/usr/bin/env python3
"""
Test the exact scenario from the user's error:
Search for "blood pressure" → Select Patient 69 (Sarah Gutierrez) → Generate Summary
"""
import asyncio
import json
import websockets
import time


async def test_user_scenario():
    """Replicate the exact user scenario that caused the timeout"""
    uri = "ws://127.0.0.1:8765/mcp"
    request_id = 0
    
    def next_id():
        nonlocal request_id
        request_id += 1
        return request_id
    
    print("=" * 80)
    print("🧪 TESTING USER'S EXACT SCENARIO")
    print("=" * 80)
    print("\nScenario: Search 'blood pressure' → Select Patient 69 → Generate Summary")
    print("=" * 80)
    
    async with websockets.connect(uri, ping_timeout=120, close_timeout=10) as ws:
        # Initialize
        print("\n✅ Step 1: Connecting to server...")
        init_req = {"jsonrpc": "2.0", "id": next_id(), "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05", "capabilities": {}, 
                              "clientInfo": {"name": "test", "version": "1.0"}}}
        await ws.send(json.dumps(init_req))
        await ws.recv()
        print("   Connected!")
        
        # Search
        print("\n✅ Step 2: Searching for 'blood preassure' (as user typed)...")
        search_req = {"jsonrpc": "2.0", "id": next_id(), "method": "tools/call",
                     "params": {"name": "search_patients_by_disease", 
                               "arguments": {"disease_keyword": "blood preassure"}}}
        await ws.send(json.dumps(search_req))
        response = json.loads(await ws.recv())
        
        search_text = response["result"]["content"][0]["text"]
        print(search_text[:300] + "...")
        
        # Get patient 69
        print("\n✅ Step 3: Getting details for Patient 69 (Sarah Gutierrez)...")
        patient_req = {"jsonrpc": "2.0", "id": next_id(), "method": "tools/call",
                      "params": {"name": "get_patient_summary",
                                "arguments": {"patient_id": "69"}}}
        await ws.send(json.dumps(patient_req))
        response = json.loads(await ws.recv())
        patient_info = response["result"]["content"][0]["text"]
        print(patient_info)
        
        # Generate summary - THIS IS WHERE IT TIMED OUT BEFORE
        print("\n✅ Step 4: Generating summary with Ollama...")
        print("   ⏳ Please wait 30-60 seconds (this is where it failed before)...")
        
        start_time = time.time()
        
        gen_req = {"jsonrpc": "2.0", "id": next_id(), "method": "tools/call",
                   "params": {"name": "generate_summary",
                             "arguments": {"patient_id": "69"}}}
        await ws.send(json.dumps(gen_req))
        
        # This should NOT timeout anymore
        response = json.loads(await ws.recv())
        elapsed = time.time() - start_time
        
        if "result" in response:
            summary = response["result"]["content"][0]["text"]
            print(f"\n✅ SUCCESS! Summary generated in {elapsed:.1f} seconds")
            print("\n📄 Generated Summary:")
            print("=" * 80)
            print(summary)
            print("=" * 80)
            
            # Now save it
            print("\n✅ Step 5: Saving summary to CSV...")
            
            # Extract the summary text (remove the header)
            summary_lines = summary.split('\n')
            summary_text = ""
            for i, line in enumerate(summary_lines):
                if 'Generated Summary for' in line:
                    summary_text = '\n'.join(summary_lines[i+2:]).strip()
                    break
            
            if not summary_text:
                summary_text = summary.strip()
            
            save_req = {"jsonrpc": "2.0", "id": next_id(), "method": "tools/call",
                       "params": {"name": "update_patient_summary",
                                 "arguments": {"patient_id": "69", "summary": summary_text}}}
            await ws.send(json.dumps(save_req))
            response = json.loads(await ws.recv())
            
            save_result = response["result"]["content"][0]["text"]
            if "✓" in save_result or "saved" in save_result.lower():
                print("   ✅ Summary saved successfully!")
                
                # Verify in CSV
                import csv
                with open('patient_summaries.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['patient_id'] == '69':
                            print(f"\n📄 Verified in patient_summaries.csv:")
                            print(f"   Patient: {row['name']}")
                            print(f"   Summary: {row['summary'][:100]}...")
                            break
            
            print("\n" + "=" * 80)
            print("🎉 SUCCESS! THE EXACT SCENARIO THAT FAILED NOW WORKS!")
            print("=" * 80)
            print("\nWhat changed:")
            print("  ✅ WebSocket ping_timeout: 20s → 120s")
            print("  ✅ Server ws_ping_timeout: default → 120s")
            print("  ✅ Ollama request timeout: 60s → 120s")
            print(f"\n  📊 Total time: {elapsed:.1f} seconds (under the 120s limit)")
            return True
        else:
            print(f"\n❌ Error: {response.get('error', 'Unknown error')}")
            return False


if __name__ == "__main__":
    try:
        success = asyncio.run(test_user_scenario())
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
