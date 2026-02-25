#!/usr/bin/env python3
"""
Test script to simulate the complete MCP workflow WITHOUT running a server
This tests the update_patient_summary logic directly
"""

import csv
import json
import sys
import os

def read_summaries():
    """Read patient summaries from CSV"""
    csv_file = "patient_summaries.csv"
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return []

def write_summaries(summaries):
    """Write patient summaries to CSV"""
    csv_file = "patient_summaries.csv"
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['patient_id', 'name', 'summary']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summaries)
        return True
    except Exception as e:
        print(f"Error writing CSV: {e}")
        return False

def get_patient_by_id(patient_id):
    """Get patient record by ID"""
    summaries = read_summaries()
    for summary in summaries:
        if summary['patient_id'] == str(patient_id):
            return summary
    return None

def update_patient_summary(patient_id, new_summary):
    """
    Update a patient's summary in the CSV
    This mirrors the server function logic
    """
    print(f"\n  [SERVER] update_patient_summary called")
    print(f"    Patient ID: {patient_id}")
    print(f"    Summary length: {len(new_summary)} chars")
    
    # Read current data
    summaries = read_summaries()
    
    # Find and update patient
    found = False
    for i, summary in enumerate(summaries):
        if summary['patient_id'] == str(patient_id):
            summaries[i]['summary'] = new_summary
            found = True
            print(f"    ✓ Found patient in CSV, updating...")
            break
    
    if not found:
        print(f"    ❌ Patient not found!")
        return False
    
    # Write back to CSV
    if not write_summaries(summaries):
        print(f"    ❌ Failed to write CSV")
        return False
    
    print(f"    ✓ CSV written")
    
    # VERIFICATION STEP: Read back and confirm
    verification = get_patient_by_id(patient_id)
    if verification and verification.get('summary') == new_summary:
        print(f"    ✓ Verification PASSED - summary persisted")
        return True
    else:
        if verification:
            print(f"    ⚠️  Verification FAILED - summary mismatch")
            print(f"        Expected length: {len(new_summary)}")
            print(f"        Got length: {len(verification.get('summary', ''))}")
        else:
            print(f"    ⚠️  Verification FAILED - patient not found after write")
        return False

def test_full_workflow():
    """
    Simulate the complete workflow:
    1. Search for disease (simulated - we'll use patient 11)
    2. Generate summary (simulated - we'll use test summary)
    3. Save summary via MCP tool call
    """
    
    print("=" * 80)
    print("FULL WORKFLOW TEST - Simulating MCP Save Flow")
    print("=" * 80)
    
    # Simulate search results
    test_patient_id = "11"
    test_patient_name = "Jerry Rivera"
    
    test_summary = """Patient Jerry Rivera (ID: 11) presents with multiple chronic conditions 
including Type 2 Diabetes and Hypertension. Current medications include Metformin 500mg 
and Enalapril 10mg. Recent BP readings show good control (135/85). Blood sugar levels 
remain elevated at 145 mg/dL. Recommend continued medication adherence and lifestyle modifications."""
    
    print(f"\n1️⃣ SEARCH RESULTS (Simulated)")
    print(f"   Found patient: {test_patient_name} (ID: {test_patient_id})")
    
    print(f"\n2️⃣ GENERATED SUMMARY (Simulated)")
    print(f"   Summary length: {len(test_summary)} characters")
    print(f"   Summary preview: {test_summary[:80]}...")
    
    print(f"\n3️⃣ SAVING SUMMARY - Calling MCP Tool: update_patient_summary")
    success = update_patient_summary(test_patient_id, test_summary)
    
    print(f"\n4️⃣ VERIFICATION - Reading CSV directly")
    patient = get_patient_by_id(test_patient_id)
    if patient:
        saved = patient.get('summary', '')
        print(f"   Patient found: {patient['name']}")
        print(f"   Saved summary length: {len(saved)} characters")
        print(f"   Match with original: {saved == test_summary}")
        
        if saved == test_summary:
            print(f"   ✅ PERFECT MATCH")
        else:
            print(f"   ❌ MISMATCH")
            if saved:
                print(f"      First 100 chars of saved: {saved[:100]}")
                print(f"      First 100 chars of test: {test_summary[:100]}")
    
    # Reset to empty
    print(f"\n5️⃣ CLEANUP - Resetting summary")
    reset_success = update_patient_summary(test_patient_id, "")
    
    print("\n" + "=" * 80)
    if success:
        print("✅ WORKFLOW TEST PASSED")
    else:
        print("❌ WORKFLOW TEST FAILED")
    print("=" * 80)
    
    return success

if __name__ == "__main__":
    success = test_full_workflow()
    sys.exit(0 if success else 1)
