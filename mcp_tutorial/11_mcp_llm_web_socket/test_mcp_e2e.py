#!/usr/bin/env python3
"""
End-to-end MCP test
Tests the complete flow: client → server via MCP → CSV update
"""

import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def test_mcp_update():
    """Test MCP communication for CSV update"""
    
    print("=" * 80)
    print("END-TO-END MCP TEST")
    print("=" * 80)
    
    # Create server parameters
    server_params = StdioServerParameters(
        command="python3",
        args=["mcp_server.py"]
    )
    
    patient_id = "45"
    test_summary = "E2E MCP TEST: This summary was sent via MCP stdio communication"
    
    try:
        print(f"\n1. Starting MCP server and connecting...")
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize
                await session.initialize()
                print(f"   ✓ Connected to MCP server")
                
                # Check initial state via get_patient_summary tool
                print(f"\n2. Getting initial patient state...")
                result = await session.call_tool("get_patient_summary", {
                    "patient_id": patient_id
                })
                initial = result.content[0].text
                print(f"   {initial[:60]}...")
                
                # Call update tool
                print(f"\n3. Calling update_patient_summary tool via MCP...")
                print(f"   Patient: {patient_id}")
                print(f"   Summary: {test_summary}")
                
                update_result = await session.call_tool("update_patient_summary", {
                    "patient_id": patient_id,
                    "summary": test_summary
                })
                print(f"   ✓ Tool call returned:")
                print(f"   {update_result.content[0].text[:60]}...")
                
                # Verify by calling get_patient_summary again
                print(f"\n4. Verifying update via get_patient_summary tool...")
                verify_result = await session.call_tool("get_patient_summary", {
                    "patient_id": patient_id
                })
                verify_text = verify_result.content[0].text
                print(f"   {verify_text[:80]}...")
                
                if test_summary in verify_text:
                    print(f"   ✅ Summary present in verification")
                else:
                    print(f"   ❌ Summary NOT found in verification")
                
        # Verify directly from CSV (check after MCP connection closes)
        print(f"\n5. Final verification - reading CSV directly...")
        import csv
        with open('patient_summaries.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['patient_id'] == patient_id:
                    csv_summary = row['summary']
                    print(f"   CSV contains: '{csv_summary[:60]}'")
                    
                    if csv_summary == test_summary:
                        print(f"   ✅ CSV MATCHES - E2E test PASSED!")
                        return True
                    else:
                        print(f"   ❌ CSV MISMATCH")
                        print(f"      Expected: {test_summary}")
                        print(f"      Got: {csv_summary}")
                        return False
        
        print(f"   ❌ Patient {patient_id} not found in CSV")
        return False
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 Testing MCP client-server communication for CSV updates\n")
    success = asyncio.run(test_mcp_update())
    print("\n" + "=" * 80)
    if success:
        print("✅ MCP END-TO-END TEST PASSED")
    else:
        print("❌ MCP END-TO-END TEST FAILED")
    print("=" * 80)
    sys.exit(0 if success else 1)
