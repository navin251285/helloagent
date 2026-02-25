#!/usr/bin/env python3
"""
Simulated client test - tests the extraction and MCP update flow
Without needing Ollama to be running
"""

import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_client_workflow():
    """Simulate the client workflow"""
    
    print("=" * 100)
    print("SIMULATED CLIENT WORKFLOW TEST")
    print("=" * 100)
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="python3",
        args=["mcp_server.py"]
    )
    
    # Simulate Ollama response (what generate_summary would return)
    simulated_ollama_response = """Generated Summary for Janet Torres (ID: 45):

Patient Janet Torres, a 70-year-old female, presents with elevated risk factors including confusion and breathing difficulty. Current blood pressure is 160/100 mmHg with blood sugar at 210 mg/dL. Requires close monitoring and medication review."""
    
    patient_id = "45"
    
    try:
        print(f"\n1. Simulating Ollama response:")
        print(f"   {simulated_ollama_response[:100]}...")
        
        # Simulate client extraction (this is the exact code from mcp_client.py)
        print(f"\n2. Extracting summary (same logic as mcp_client.py):")
        
        summary_lines = simulated_ollama_response.split('\n')
        summary_start = None
        
        for i, line in enumerate(summary_lines):
            if 'Generated Summary for' in line:
                summary_start = i + 2
                print(f"   Found 'Generated Summary for' at line {i}")
                print(f"   Summary extraction starts at line {summary_start}")
                break
        
        if summary_start and summary_start < len(summary_lines):
            summary_text = '\n'.join(summary_lines[summary_start:]).strip()
        else:
            summary_text = simulated_ollama_response.strip()
            print(f"   NOT FOUND - using entire response")
        
        # Clean up multiple blank lines
        summary_text = '\n'.join([ln.strip() for ln in summary_text.split('\n') if ln.strip()])
        
        print(f"   Extracted summary ({len(summary_text)} characters):")
        if summary_text:
            print(f"   {summary_text[:80]}...")
            print(f"   [DEBUG] Full extracted text length: {len(summary_text)}")
            print(f"   [DEBUG] First 100 chars: {summary_text[:100]}")
        else:
            print(f"   ⚠️  WARNING: Extracted summary is EMPTY!")
        
        if not summary_text or len(summary_text) == 0:
            print(f"\n❌ ERROR: Extraction produced empty summary!")
            return False
        
        # Connect to MCP and send update
        print(f"\n3. Connecting to MCP server and sending update...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                print(f"   ✓ Connected")
                
                # Call update
                print(f"\n4. Calling update_patient_summary tool:")
                print(f"   Patient ID: {patient_id}")
                print(f"   Summary length: {len(summary_text)}")
                
                result = await session.call_tool("update_patient_summary", {
                    "patient_id": str(patient_id),
                    "summary": summary_text
                })
                
                output = result.content[0].text
                print(f"   ✓ Server response: {output[:80]}...")
        
        # Verify CSV
        print(f"\n5. Verifying CSV was updated...")
        import csv
        with open('patient_summaries.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['patient_id'] == patient_id:
                    csv_summary = row['summary']
                    print(f"   CSV contains: '{csv_summary[:80]}'")
                    
                    if csv_summary == summary_text:
                        print(f"   ✅ MATCH - Simulated client workflow PASSED!")
                        return True
                    else:
                        print(f"   ❌ MISMATCH")
                        print(f"      Expected: {summary_text}")
                        print(f"      Got: {csv_summary}")
                        return False
        
        print(f"   ❌ Patient not found")
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 Testing client workflow (extraction + MCP update)\n")
    success = asyncio.run(test_client_workflow())
    print("\n" + "=" * 100)
    if success:
        print("✅ SIMULATED CLIENT WORKFLOW TEST PASSED")
    else:
        print("❌ SIMULATED CLIENT WORKFLOW TEST FAILED")
    print("=" * 100)
    sys.exit(0 if success else 1)
