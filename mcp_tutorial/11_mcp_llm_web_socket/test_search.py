#!/usr/bin/env python3
"""
Quick test to verify Chroma DB search is working in the server
"""
import sys

# Import the server's search function
import chromadb

def search_patients_by_disease(disease_keyword, top_k=5):
    """Search for patients by disease/symptoms using Chroma DB"""
    client = chromadb.PersistentClient(path="./chroma_db")
    
    try:
        collection = client.get_collection(name="patients")
        # Query with top_k * 2 to ensure we get diverse results
        results = collection.query(
            query_texts=[disease_keyword],
            n_results=top_k * 2
        )
        
        patients = []
        # results['metadatas'] returns [[{...}, {...}, ...]]  - list of lists
        # We want the first list's items (top_k results)
        if results and results['metadatas'] and len(results['metadatas']) > 0:
            for metadata in results['metadatas'][0][:top_k]:  # Take top_k from first list
                if metadata:
                    patients.append(metadata)
        
        return patients
    except Exception as e:
        print(f"Chroma search error: {e}", file=sys.stderr)
        return []


if __name__ == "__main__":
    print("Testing Chroma DB search function...")
    print("=" * 80)
    
    # Test 1: Search for diabetes
    print("\nTest 1: Searching for 'diabetes'")
    print("-" * 80)
    patients = search_patients_by_disease("diabetes")
    
    if patients:
        print(f"✅ Found {len(patients)} patients:")
        for i, p in enumerate(patients, 1):
            print(f"{i}. ID: {p['patient_id']:3s} | Name: {p['name']:20s} | Age: {p['age']:2s} | Symptoms: {p['current_symptoms'][:40]}")
    else:
        print("❌ No patients found!")
    
    # Test 2: Search for chest pain
    print("\n\nTest 2: Searching for 'chest pain'")
    print("-" * 80)
    patients = search_patients_by_disease("chest pain")
    
    if patients:
        print(f"✅ Found {len(patients)} patients:")
        for i, p in enumerate(patients, 1):
            print(f"{i}. ID: {p['patient_id']:3s} | Name: {p['name']:20s} | Age: {p['age']:2s} | Symptoms: {p['current_symptoms'][:40]}")
    else:
        print("❌ No patients found!")
    
    # Test 3: Search for hypertension
    print("\n\nTest 3: Searching for 'hypertension'")
    print("-" * 80)
    patients = search_patients_by_disease("hypertension")
    
    if patients:
        print(f"✅ Found {len(patients)} patients:")
        for i, p in enumerate(patients, 1):
            print(f"{i}. ID: {p['patient_id']:3s} | Name: {p['name']:20s} | Age: {p['age']:2s} | Symptoms: {p['current_symptoms'][:40]}")
    else:
        print("❌ No patients found!")
    
    print("\n" + "=" * 80)
    print("✅ All tests completed!")
