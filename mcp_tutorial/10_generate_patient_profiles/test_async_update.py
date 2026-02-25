#!/usr/bin/env python3
"""
Test the update_patient_summary function directly in async context
This test imports the actual server functions and tests them
"""

import asyncio
import sys
import os
import csv

# Add path to import mcp_server
sys.path.insert(0, '/home/navinkumar_25_gmail_com/mcp_tutorial/10_generate_patient_profiles')

# Import the actual server functions (without starting the server)
from mcp_server import (
    read_summaries, 
    write_summaries, 
    get_patient_by_id, 
    update_patient_summary
)

async def test_async_update():
    """Test update_patient_summary in async context"""
    
    print("=" * 80)
    print("ASYNC CONTEXT UPDATE TEST")
    print("=" * 80)
    
    test_patient_id = "11"
    test_summary = "ASYNC TEST: This patient requires close monitoring due to multiple comorbidities."
    
    # Test 1: Get initial state
    print(f"\n1️⃣ Reading initial state for Patient {test_patient_id}:")
    initial = get_patient_by_id(test_patient_id)
    if initial:
        print(f"   ✓ Found: {initial['name']}")
        print(f"   Summary: '{initial['summary'][:50] if initial['summary'] else 'EMPTY'}'")
    else:
        print(f"   ❌ Patient not found!")
        return False
    
    # Test 2: Call update in async context (this is what MCP does)
    print(f"\n2️⃣ Updating in async context:")
    success = update_patient_summary(test_patient_id, test_summary)
    print(f"   Update result: {success}")
    
    # Small delay to ensure file operations complete
    await asyncio.sleep(0.1)
    
    # Test 3: Verify the update
    print(f"\n3️⃣ Verifying update:")
    updated = get_patient_by_id(test_patient_id)
    if updated:
        saved_summary = updated['summary']
        print(f"   Saved summary: '{saved_summary[:50]}'")
        
        if saved_summary == test_summary:
            print(f"   ✅ MATCH - Update successful!")
            success = True
        else:
            print(f"   ❌ MISMATCH - Summaries don't match")
            print(f"      Expected: {test_summary}")
            print(f"      Got: {saved_summary}")
            success = False
    
    # Test 4: Reset
    print(f"\n4️⃣ Resetting to initial state:")
    reset_success = update_patient_summary(test_patient_id, initial['summary'])
    print(f"   Reset result: {reset_success}")
    
    return success

async def test_multiple_async_calls():
    """Test multiple sequential async updates"""
    
    print("\n\n" + "=" * 80)
    print("MULTIPLE ASYNC CALLS TEST")
    print("=" * 80)
    
    patients = ["11", "45", "70"]
    summaries_to_save = [
        "First test patient with updating",
        "Second test patient for validation",
        "Third test for async workflow"
    ]
    
    # Save multiple summaries
    print(f"\n1️⃣ Updating {len(patients)} patients:")
    for pid, summary in zip(patients, summaries_to_save):
        print(f"   Updating patient {pid}...")
        update_patient_summary(pid, summary)
        await asyncio.sleep(0.05)  # Small delay between updates
    
    # Verify all were saved
    print(f"\n2️⃣ Verifying all updates:")
    all_match = True
    for pid, expected_summary in zip(patients, summaries_to_save):
        patient = get_patient_by_id(pid)
        if patient and patient['summary'] == expected_summary:
            print(f"   ✅ Patient {pid}: Match")
        else:
            print(f"   ❌ Patient {pid}: Mismatch or not found")
            all_match = False
    
    # Reset all
    print(f"\n3️⃣ Resetting all patients:")
    for pid in patients:
        patient = get_patient_by_id(pid)
        update_patient_summary(pid, '')
        print(f"   ✓ Reset patient {pid}")
    
    return all_match

async def main():
    """Run all async tests"""
    
    print("\n" + "🧪 ASYNC CONTEXT TESTING FOR MCP UPDATE MECHANISM" + "\n")
    
    # Test 1: Single async update
    test1_result = await test_async_update()
    
    # Test 2: Multiple async calls
    test2_result = await test_multiple_async_calls()
    
    # Summary
    print("\n\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    if test1_result and test2_result:
        print("✅ ALL ASYNC TESTS PASSED")
        print("   The async context is not causing the issue")
    else:
        print("❌ SOME TESTS FAILED")
        print("   May be an async/concurrency issue")
    print("=" * 80)
    
    return test1_result and test2_result

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
