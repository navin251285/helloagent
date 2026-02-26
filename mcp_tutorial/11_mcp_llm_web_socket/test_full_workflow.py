#!/usr/bin/env python3
"""
Complete End-to-End Test: Search → Select → Update Summary
Tests the full workflow and verifies file persistence
"""
import asyncio
import json
import websockets
import csv
from datetime import datetime


class E2ETest:
    def __init__(self):
        self.uri = "ws://127.0.0.1:8765/mcp"
        self.request_id = 0
        
    async def send_request(self, ws, method, params=None):
        """Send JSON-RPC request"""
        self.request_id += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params or {}
        }
        await ws.send(json.dumps(request))
        response = json.loads(await ws.recv())
        return response
    
    async def call_tool(self, ws, tool_name, arguments):
        """Call a tool"""
        response = await self.send_request(ws, "tools/call", {
            "name": tool_name,
            "arguments": arguments
        })
        if "error" in response:
            raise Exception(f"Tool error: {response['error']['message']}")
        return response["result"]["content"]
    
    async def run_test(self):
        """Run complete workflow test"""
        print("=" * 80)
        print("🧪 END-TO-END WORKFLOW TEST")
        print("=" * 80)
        
        try:
            async with websockets.connect(self.uri) as ws:
                # Step 1: Initialize
                print("\n1️⃣  Initializing connection...")
                init_response = await self.send_request(ws, "initialize", {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "e2e-test", "version": "1.0.0"}
                })
                print(f"   ✅ Connected to: {init_response['result']['serverInfo']['name']}")
                
                # Step 2: Search for patients
                print("\n2️⃣  Searching for patients with 'diabetes'...")
                search_result = await self.call_tool(ws, "search_patients_by_disease", {
                    "disease_keyword": "diabetes"
                })
                search_text = search_result[0]["text"]
                print(f"   {search_text[:200]}...")
                
                # Parse patient ID from results
                patient_id = None
                for line in search_text.split('\n'):
                    if line.strip().startswith('1.'):
                        # Extract ID from "1. ID: 11  | Name: ..."
                        parts = line.split('|')
                        if parts:
                            id_part = parts[0].split(':')[1].strip()
                            patient_id = id_part
                            break
                
                if not patient_id:
                    print("   ❌ No patients found in search results!")
                    return False
                
                print(f"   ✅ Selected patient ID: {patient_id}")
                
                # Step 3: Get patient details
                print(f"\n3️⃣  Getting patient details for ID {patient_id}...")
                patient_result = await self.call_tool(ws, "get_patient_summary", {
                    "patient_id": patient_id
                })
                patient_text = patient_result[0]["text"]
                patient_name = None
                for line in patient_text.split('\n'):
                    if line.startswith('Name:'):
                        patient_name = line.replace('Name:', '').strip()
                        break
                print(f"   ✅ Patient: {patient_name}")
                
                # Step 4: Read current summary from CSV
                print(f"\n4️⃣  Checking current summary in CSV...")
                current_summary = self.read_summary_from_csv(patient_id)
                if current_summary:
                    print(f"   📝 Current: {current_summary[:60]}...")
                else:
                    print(f"   📝 Current: (empty)")
                
                # Step 5: Create and save a new test summary
                print(f"\n5️⃣  Creating and saving new summary...")
                test_summary = f"[E2E TEST {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Patient shows symptoms consistent with metabolic syndrome. Recommend lifestyle modifications and monitoring."
                
                update_result = await self.call_tool(ws, "update_patient_summary", {
                    "patient_id": patient_id,
                    "summary": test_summary
                })
                update_text = update_result[0]["text"]
                
                if "✓" in update_text or "saved" in update_text.lower():
                    print(f"   ✅ Server confirmed update")
                else:
                    print(f"   ⚠️  Unexpected response: {update_text[:100]}")
                
                # Step 6: Verify file was actually updated
                print(f"\n6️⃣  Verifying file persistence...")
                await asyncio.sleep(1)  # Give file system a moment
                
                new_summary = self.read_summary_from_csv(patient_id)
                if new_summary == test_summary:
                    print(f"   ✅ File updated correctly!")
                    print(f"   📄 New summary: {new_summary[:80]}...")
                    print("\n" + "=" * 80)
                    print("✅ ALL TESTS PASSED!")
                    print("=" * 80)
                    return True
                else:
                    print(f"   ❌ File NOT updated!")
                    print(f"   Expected: {test_summary[:60]}...")
                    print(f"   Got:      {new_summary[:60] if new_summary else '(empty)'}...")
                    print("\n" + "=" * 80)
                    print("❌ TEST FAILED - File not persisted")
                    print("=" * 80)
                    return False
                    
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def read_summary_from_csv(self, patient_id):
        """Read summary from CSV file"""
        try:
            with open('patient_summaries.csv', 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row['patient_id'] == str(patient_id):
                        return row.get('summary', '').strip()
            return None
        except Exception as e:
            print(f"   ⚠️  Error reading CSV: {e}")
            return None


async def main():
    test = E2ETest()
    success = await test.run_test()
    
    if success:
        print("\n✅ Workflow verified: Search → Select → Update → Persist")
        print("📊 The system is working correctly!")
    else:
        print("\n❌ Workflow test failed. Check server logs.")
    
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
