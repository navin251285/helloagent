#!/usr/bin/env python3
"""
Setup Chroma DB with patient profiles
Creates embeddings of patient symptoms/diseases for semantic search
"""

import csv
import chromadb

# Initialize Chroma client with persistent storage
client = chromadb.PersistentClient(path="./chroma_db")

# Delete existing collection if it exists
try:
    client.delete_collection(name="patients")
except:
    pass

# Create new collection
collection = client.create_collection(
    name="patients",
    metadata={"hnsw:space": "cosine"}
)

# Read patient data and add to Chroma
documents = []
metadatas = []
ids = []

with open('patients_data.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        patient_id = row['patient_id']
        
        # Create searchable text from symptoms and medical history
        search_text = f"{row['current_symptoms']} {row['medical_history']} {row['current_medications']}"
        
        documents.append(search_text)
        metadatas.append({
            "patient_id": patient_id,
            "name": row['name'],
            "age": row['age'],
            "gender": row['gender'],
            "current_symptoms": row['current_symptoms'],
            "current_bp": row['current_bp'],
            "current_sugar": row['current_sugar'],
            "risk_score": row['risk_score'],
            "medical_history": row['medical_history'],
            "current_medications": row['current_medications']
        })
        ids.append(f"patient_{patient_id}")

# Add all documents to collection
collection.add(
    ids=ids,
    documents=documents,
    metadatas=metadatas
)

print(f"✓ Chroma DB initialized with {len(ids)} patient profiles")
print(f"✓ Collection 'patients' created at ./chroma_db")
