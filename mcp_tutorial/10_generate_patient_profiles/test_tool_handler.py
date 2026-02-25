#!/usr/bin/env python3
"""
Direct test of MCP server tool handler
This simulates what happens when the client calls the update_patient_summary tool
"""

import sys
import os
import asyncio

# Add path to import mcp_server
sys.path.insert(0, '/home/navinkumar_25_gmail_com/mcp_tutorial/10_generate_patient_profiles')

# Import necessary components
from mcp_server import handle_call_tool, get_patient_by_id, update_patient_summary

async def test_tool_handler():
    """Test calling the tool handler directly"""
    
    print("=" * 80)
    print("DIRECT ASYNC TOOL HANDLER TEST")
    print("=" * 80)
    
    patient_id = "11"
    test_summary = "DIRECT TEST: This is a test summary generated via direct async tool handler call."
    
    print(f"\n1️⃣ Calling async tool handler for update_patient_summary")
    print(f"   Patient ID: {patient_id}")
    print(f"   Summary length: {len(test_summary)}")
    
    try:
        # Call the async tool handler directly
        result = await handle_call_tool(
            name="update_patient_summary",
            arguments={
                "patient_id": patient_id,
                "summary": test_summary
            }
        )
        
        print(f"\n2️⃣ Tool handler result:")
        if result:
            print(result[0].text)
        
        # Check if CSV was updated
        print(f"\n3️⃣ Verifying CSV update:")
        patient = get_patient_by_id(patient_id)
        if patient:
            saved = patient['summary']
            print(f"   Saved summary: '{saved[:50]}...'")
            if saved == test_summary:
                print(f"   ✅ MATCH - CSV updated successfully!")
            else:
                print(f"   ❌ MISMATCH - CSV not updated properly")
                print(f"      Expected: {test_summary}")
                print(f"      Got: {saved}")
        else:
            print(f"   ❌ Patient not found")
        
        # Reset
        print(f"\n4️⃣ Resetting:")
        update_patient_summary(patient_id, '')
        print(f"   Reset complete")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tool_handler())

