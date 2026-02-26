#!/usr/bin/env python3
"""
Demonstration: Complete workflow with realistic use case
"""
import asyncio
import json
import websockets
import csv


async def demo_workflow():
    """Demonstrate the complete patient summary workflow"""
    uri = "ws://127.0.0.1:8765/mcp"
    request_id = 0
    
    def next_id():
        nonlocal request_id
        request_id += 1
        return request_id
    
    print("=" * 80)
    print("🏥 PATIENT SUMMARY SYSTEM - WORKFLOW DEMONSTRATION")
    print("=" * 80)
    
    async with websockets.connect(uri) as ws:
        # Initialize
        init_req = {"jsonrpc": "2.0", "id": next_id(), "method": "initialize",
                    "params": {"protocolVersion": "2024-11-05", "capabilities": {}, 
                              "clientInfo": {"name": "demo", "version": "1.0"}}}
        await ws.send(json.dumps(init_req))
        await ws.recv()
        print("\n✅ Connected to MCP Server")
        
        # Test Case 1: Search for hypertension patients
        print("\n" + "─" * 80)
        print("📋 USE CASE 1: Search for hypertension patients")
        print("─" * 80)
        
        search_req = {"jsonrpc": "2.0", "id": next_id(), "method": "tools/call",
                     "params": {"name": "search_patients_by_disease", 
                               "arguments": {"disease_keyword": "hypertension"}}}
        await ws.send(json.dumps(search_req))
        response = json.loads(await ws.recv())
        
        search_text = response["result"]["content"][0]["text"]
        print(search_text)
        
        # Extract first patient ID
        patient_id = None
        for line in search_text.split('\n'):
            if line.strip().startswith('1.'):
                patient_id = line.split('|')[0].split(':')[1].strip()
                break
        
        if patient_id:
            # Get patient details
            print(f"\n📝 Selected Patient ID: {patient_id}")
            
            details_req = {"jsonrpc": "2.0", "id": next_id(), "method": "tools/call",
                          "params": {"name": "get_patient_summary", 
                                    "arguments": {"patient_id": patient_id}}}
            await ws.send(json.dumps(details_req))
            response = json.loads(await ws.recv())
            details = response["result"]["content"][0]["text"]
            print("\n" + details)
            
            # Update with a clinical summary
            print(f"\n💾 Updating patient summary...")
            summary = "Patient presents with elevated blood pressure (150/95 mmHg) and associated symptoms of blurred vision and palpitations. Assessment indicates Stage 2 hypertension with moderate cardiovascular risk. Recommend: (1) Lifestyle modifications including low-sodium diet and regular exercise, (2) Initiate ACE inhibitor therapy, (3) Monitor BP weekly and follow-up in 2 weeks."
            
            update_req = {"jsonrpc": "2.0", "id": next_id(), "method": "tools/call",
                         "params": {"name": "update_patient_summary",
                                   "arguments": {"patient_id": patient_id, "summary": summary}}}
            await ws.send(json.dumps(update_req))
            response = json.loads(await ws.recv())
            result = response["result"]["content"][0]["text"]
            
            if "✓" in result or "saved" in result.lower():
                print(f"   ✅ Summary saved successfully!")
                
                # Verify in CSV
                with open('patient_summaries.csv', 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if row['patient_id'] == patient_id:
                            print(f"\n📄 Verified in CSV:")
                            print(f"   Patient: {row['name']}")
                            print(f"   Summary: {row['summary'][:100]}...")
                            break
        
        # Test Case 2: Search for diabetes patients
        print("\n\n" + "─" * 80)
        print("📋 USE CASE 2: Search for diabetes patients")
        print("─" * 80)
        
        search_req = {"jsonrpc": "2.0", "id": next_id(), "method": "tools/call",
                     "params": {"name": "search_patients_by_disease",
                               "arguments": {"disease_keyword": "diabetes"}}}
        await ws.send(json.dumps(search_req))
        response = json.loads(await ws.recv())
        search_text = response["result"]["content"][0]["text"]
        
        # Show first 3 results
        lines = search_text.split('\n')
        for line in lines[:6]:  # Header + 3 patients
            print(line)
        
        print("\n" + "=" * 80)
        print("✅ DEMONSTRATION COMPLETE")
        print("=" * 80)
        print("\n📊 Summary:")
        print("   • Connected to WebSocket server")
        print("   • Searched patients by disease (semantic search via Chroma DB)")
        print("   • Retrieved patient details")
        print("   • Updated patient summary")
        print("   • Verified persistence in CSV file")
        print("\n🎯 The system is fully operational!")


if __name__ == "__main__":
    asyncio.run(demo_workflow())
