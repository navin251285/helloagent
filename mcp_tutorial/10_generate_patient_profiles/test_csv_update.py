#!/usr/bin/env python3
"""
Diagnostic script to test CSV update mechanism
Run this to verify summaries are being saved correctly
"""

import csv
import sys

def test_csv_update():
    """Test the complete CSV update flow"""
    
    print("=" * 80)
    print("CSV UPDATE DIAGNOSTIC TEST")
    print("=" * 80)
    
    CSV_FILE = "patient_summaries.csv"
    TEST_PATIENT_ID = "11"
    TEST_SUMMARY = "This is a TEST summary for Patient 11 - Jerry Rivera. Generated for diagnostic purposes."
    
    # Step 1: Read initial state
    print(f"\n1️⃣ Reading CSV file: {CSV_FILE}")
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            summaries = list(reader)
        print(f"   ✓ Read {len(summaries)} patient records")
    except Exception as e:
        print(f"   ❌ Error reading CSV: {e}")
        return False
    
    # Step 2: Get initial state
    print(f"\n2️⃣ Checking initial state of Patient {TEST_PATIENT_ID}:")
    initial_summary = None
    for row in summaries:
        if row['patient_id'] == TEST_PATIENT_ID:
            initial_summary = row['summary']
            print(f"   Name: {row['name']}")
            print(f"   Current Summary: '{initial_summary[:50] if initial_summary else 'EMPTY'}'")
            break
    
    # Step 3: Update summary
    print(f"\n3️⃣ Updating Patient {TEST_PATIENT_ID} summary:")
    updated = False
    for i, summary in enumerate(summaries):
        if summary['patient_id'] == TEST_PATIENT_ID:
            summaries[i]['summary'] = TEST_SUMMARY
            updated = True
            print(f"   ✓ Found patient, updating summary")
            break
    
    if not updated:
        print(f"   ❌ Patient {TEST_PATIENT_ID} not found in records!")
        return False
    
    # Step 4: Write back to CSV
    print(f"\n4️⃣ Writing updated CSV:")
    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['patient_id', 'name', 'summary']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(summaries)
        print(f"   ✓ CSV written successfully")
    except Exception as e:
        print(f"   ❌ Error writing CSV: {e}")
        return False
    
    # Step 5: Read back and verify
    print(f"\n5️⃣ Verification - Reading CSV again:")
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['patient_id'] == TEST_PATIENT_ID:
                    saved_summary = row['summary']
                    print(f"   Current Summary: '{saved_summary[:50]}...'")
                    
                    if saved_summary == TEST_SUMMARY:
                        print(f"   ✅ SUCCESS! Summary matches exactly")
                        success = True
                    else:
                        print(f"   ❌ MISMATCH! Saved summary doesn't match")
                        print(f"      Expected: '{TEST_SUMMARY[:50]}...'")
                        print(f"      Got:      '{saved_summary[:50]}...'")
                        success = False
                    break
    except Exception as e:
        print(f"   ❌ Error reading back CSV: {e}")
        return False
    
    # Step 6: Reset for next test
    print(f"\n6️⃣ Resetting Patient {TEST_PATIENT_ID} to initial state:")
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        summaries = list(reader)
    
    for i, summary in enumerate(summaries):
        if summary['patient_id'] == TEST_PATIENT_ID:
            summaries[i]['summary'] = initial_summary or ''
            break
    
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['patient_id', 'name', 'summary']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(summaries)
    
    print(f"   ✓ Reset complete")
    
    print("\n" + "=" * 80)
    if success:
        print("✅ ALL TESTS PASSED - CSV Update Mechanism Works!")
    else:
        print("❌ TESTS FAILED - CSV Update Mechanism Has Issues")
    print("=" * 80)
    
    return success

if __name__ == "__main__":
    success = test_csv_update()
    sys.exit(0 if success else 1)
