#!/usr/bin/env python3
"""
Test the server's search function directly (without WebSocket)
"""
import sys
sys.path.insert(0, '.')

# Import from the server
from mcp_server import search_patients_by_disease, chroma_client

print("=" * 80)
print("SERVER DIAGNOSTIC TEST")
print("=" * 80)

# Check if chroma_client is initialized
print(f"\n1. Chroma client status: {'✅ Initialized' if chroma_client else '❌ None'}")

if not chroma_client:
    print("\n❌ ERROR: Chroma client is not initialized!")
    print("This means Chroma DB failed to load when the server module was imported.")
    sys.exit(1)

# Test search directly
print("\n2. Testing search function...")
print("-" * 80)

test_keywords = ["diabetes", "chest pain", "hypertension"]

for keyword in test_keywords:
    print(f"\nSearching for: '{keyword}'")
    patients = search_patients_by_disease(keyword)
    
    if patients:
        print(f"✅ Found {len(patients)} patients:")
        for i, p in enumerate(patients[:3], 1):  # Show first 3
            print(f"   {i}. ID: {p['patient_id']:3s} | {p['name']:20s} | {p['current_symptoms'][:40]}")
    else:
        print(f"❌ No results returned!")

print("\n" + "=" * 80)
print("✅ Diagnostic complete!")
