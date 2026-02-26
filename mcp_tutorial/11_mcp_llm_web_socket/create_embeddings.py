import chromadb
from sentence_transformers import SentenceTransformer
import json
import csv
from datetime import datetime

# Initialize ChromaDB client with persistent storage
client = chromadb.PersistentClient(path="./chroma_db")

# Initialize embedding model
print("Loading embedding model: all-MiniLM-L6-v2...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✓ Model loaded successfully")

# Create or get collection
collection_name = "patient_profiles"
try:
    collection = client.create_collection(
        name=collection_name,
        metadata={"description": "Patient medical profiles with history"}
    )
    print(f"✓ Created new collection: {collection_name}")
except Exception as e:
    # Collection might already exist, get it
    collection = client.get_collection(name=collection_name)
    print(f"✓ Using existing collection: {collection_name}")


def load_patient_data():
    """Load patient data from JSON file"""
    with open("patients_data.json", 'r', encoding='utf-8') as f:
        patients = json.load(f)
    print(f"✓ Loaded {len(patients)} patient profiles")
    return patients


def create_patient_embedding_text(patient, visit):
    """Create comprehensive text for embedding from patient and visit data"""
    text_parts = [
        f"Patient: {patient['name']}",
        f"Age: {patient['age']} years",
        f"Gender: {patient['gender']}",
        f"Visit Date: {visit['visit_date']}",
        f"Symptoms: {visit['symptoms']}",
        f"Blood Pressure: {visit['bp']}",
        f"Blood Sugar: {visit['sugar']} mg/dL",
        f"Medical History: {visit['medical_history']}",
        f"Current Medications: {visit['current_medications']}",
        f"Doctor's Notes: {visit['notes']}"
    ]
    return " | ".join(text_parts)


def add_patients_to_chromadb(patients):
    """Add all patient visits to ChromaDB with embeddings"""
    documents = []
    metadatas = []
    ids = []
    
    print("\nGenerating embeddings for patient visits...")
    
    for patient in patients:
        patient_id = patient['patient_id']
        
        for visit_idx, visit in enumerate(patient['visit_history'], 1):
            # Create embedding text
            embedding_text = create_patient_embedding_text(patient, visit)
            documents.append(embedding_text)
            
            # Create metadata
            metadata = {
                "patient_id": str(patient_id),
                "patient_name": patient['name'],
                "age": patient['age'],
                "gender": patient['gender'],
                "visit_date": visit['visit_date'],
                "visit_number": visit_idx,
                "total_visits": len(patient['visit_history']),
                "symptoms": visit['symptoms'],
                "bp": visit['bp'],
                "sugar": str(visit['sugar']),
                "medical_history": visit['medical_history'],
                "current_medications": visit['current_medications'],
                "symptom_score": str(visit['symptom_score']),
                "bp_risk": str(visit['bp_risk']),
                "sugar_risk": str(visit['sugar_risk']),
                "age_factor": str(visit['age_factor']),
                "base_score": str(visit['base_score']),
                "risk_score": str(visit['risk_score']),
                "outcome": visit['outcome']
            }
            metadatas.append(metadata)
            
            # Create unique ID
            doc_id = f"patient_{patient_id}_visit_{visit_idx}"
            ids.append(doc_id)
    
    print(f"  Processing {len(documents)} patient visits...")
    
    # Generate embeddings
    print("  Generating embeddings with all-MiniLM-L6-v2...")
    embeddings = embedding_model.encode(documents, show_progress_bar=True)
    
    # Add to ChromaDB
    print("  Adding to ChromaDB...")
    collection.add(
        documents=documents,
        embeddings=embeddings.tolist(),
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"✓ Added {len(documents)} patient visit records to ChromaDB")


def query_high_risk_patients(threshold=7.0):
    """Query high-risk patients"""
    print(f"\n{'='*80}")
    print(f"HIGH-RISK PATIENTS (Risk Score >= {threshold})")
    print('='*80)
    
    # Get all records and filter manually since ChromaDB metadata is string-based
    all_records = collection.get()
    
    high_risk_patients = []
    for metadata in all_records['metadatas']:
        if float(metadata['risk_score']) >= threshold:
            high_risk_patients.append(metadata)
    
    if high_risk_patients:
        for i, metadata in enumerate(high_risk_patients[:10], 1):  # Limit to 10
            print(f"\n{i}. {metadata['patient_name']} (ID: {metadata['patient_id']})")
            print(f"   Visit Date: {metadata['visit_date']}")
            print(f"   Age: {metadata['age']}, Gender: {metadata['gender']}")
            print(f"   Symptoms: {metadata['symptoms']}")
            print(f"   Risk Score: {metadata['risk_score']}")
            print(f"   BP: {metadata['bp']}, Sugar: {metadata['sugar']}")
    else:
        print(f"No patients found with risk score >= {threshold}")
    
    return high_risk_patients


def semantic_search_similar_cases(query_text, n_results=5):
    """Search for similar patient cases using semantic search"""
    print(f"\n{'='*80}")
    print(f"SEMANTIC SEARCH RESULTS")
    print(f"Query: {query_text}")
    print('='*80)
    
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results
    )
    
    if results['metadatas']:
        for i, (metadata, distance) in enumerate(zip(results['metadatas'][0], results['distances'][0]), 1):
            print(f"\n{i}. {metadata['patient_name']} (ID: {metadata['patient_id']}) - Similarity: {1-distance:.4f}")
            print(f"   Visit Date: {metadata['visit_date']}")
            print(f"   Age: {metadata['age']}, Gender: {metadata['gender']}")
            print(f"   Symptoms: {metadata['symptoms']}")
            print(f"   Risk Score: {metadata['risk_score']}")
            print(f"   Medical History: {metadata['medical_history']}")
            print(f"   Outcome: {metadata['outcome']}")
    
    return results


def get_patient_history(patient_id):
    """Retrieve complete history for a specific patient"""
    print(f"\n{'='*80}")
    print(f"PATIENT HISTORY - ID: {patient_id}")
    print('='*80)
    
    results = collection.get(
        where={"patient_id": str(patient_id)}
    )
    
    if results['metadatas']:
        patient_name = results['metadatas'][0]['patient_name']
        print(f"Patient: {patient_name}")
        print(f"Total Visits: {len(results['metadatas'])}")
        print()
        
        # Sort by visit number
        visits = sorted(zip(results['metadatas'], results['documents']), 
                       key=lambda x: int(x[0]['visit_number']))
        
        for metadata, document in visits:
            print(f"Visit {metadata['visit_number']} - {metadata['visit_date']}")
            print(f"  Symptoms: {metadata['symptoms']}")
            print(f"  BP: {metadata['bp']}, Sugar: {metadata['sugar']}")
            print(f"  Risk Score: {metadata['risk_score']}")
            print(f"  Outcome: {metadata['outcome']}")
            print()
    else:
        print(f"No records found for patient ID: {patient_id}")
    
    return results


def get_collection_stats():
    """Get statistics about the collection"""
    count = collection.count()
    print(f"\n{'='*80}")
    print(f"CHROMADB COLLECTION STATISTICS")
    print('='*80)
    print(f"Collection Name: {collection_name}")
    print(f"Total Records: {count}")
    
    # Get sample of all records to calculate stats
    all_records = collection.get()
    
    if all_records['metadatas']:
        # Calculate risk score distribution
        risk_scores = [float(m['risk_score']) for m in all_records['metadatas']]
        avg_risk = sum(risk_scores) / len(risk_scores)
        max_risk = max(risk_scores)
        min_risk = min(risk_scores)
        
        print(f"Average Risk Score: {avg_risk:.2f}")
        print(f"Max Risk Score: {max_risk:.2f}")
        print(f"Min Risk Score: {min_risk:.2f}")
        
        # Count high-risk patients
        high_risk = sum(1 for score in risk_scores if score >= 7.0)
        medium_risk = sum(1 for score in risk_scores if 4.0 <= score < 7.0)
        low_risk = sum(1 for score in risk_scores if score < 4.0)
        
        print(f"\nRisk Distribution:")
        print(f"  High Risk (≥7.0): {high_risk} visits ({high_risk/len(risk_scores)*100:.1f}%)")
        print(f"  Medium Risk (4.0-6.9): {medium_risk} visits ({medium_risk/len(risk_scores)*100:.1f}%)")
        print(f"  Low Risk (<4.0): {low_risk} visits ({low_risk/len(risk_scores)*100:.1f}%)")
    
    print('='*80)


def export_embeddings_to_csv():
    """Export all data with embeddings to CSV"""
    all_data = collection.get(include=['documents', 'metadatas', 'embeddings'])
    
    filename = "patient_embeddings.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'patient_id', 'patient_name', 'age', 'gender', 'visit_date', 
            'visit_number', 'symptoms', 'bp', 'sugar', 'medical_history',
            'current_medications', 'risk_score', 'base_score', 'outcome',
            'embedding_vector'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for metadata, embedding in zip(all_data['metadatas'], all_data['embeddings']):
            row = {
                'patient_id': metadata['patient_id'],
                'patient_name': metadata['patient_name'],
                'age': metadata['age'],
                'gender': metadata['gender'],
                'visit_date': metadata['visit_date'],
                'visit_number': metadata['visit_number'],
                'symptoms': metadata['symptoms'],
                'bp': metadata['bp'],
                'sugar': metadata['sugar'],
                'medical_history': metadata['medical_history'],
                'current_medications': metadata['current_medications'],
                'risk_score': metadata['risk_score'],
                'base_score': metadata['base_score'],
                'outcome': metadata['outcome'],
                'embedding_vector': str(embedding[:10]) + "..." # First 10 dimensions only
            }
            writer.writerow(row)
    
    print(f"✓ Exported embeddings to {filename}")


def main():
    print("="*80)
    print("PATIENT PROFILE EMBEDDING GENERATION")
    print("="*80)
    
    # Load patient data
    patients = load_patient_data()
    
    # Add to ChromaDB
    add_patients_to_chromadb(patients)
    
    # Get collection statistics
    get_collection_stats()
    
    # Export embeddings
    export_embeddings_to_csv()
    
    # Example queries
    print("\n" + "="*80)
    print("EXAMPLE QUERIES")
    print("="*80)
    
    # Query high-risk patients
    query_high_risk_patients(threshold=7.0)
    
    # Semantic search for similar cases
    semantic_search_similar_cases(
        "Patient with chest pain and high blood pressure",
        n_results=5
    )
    
    # Get specific patient history
    get_patient_history(patient_id=1)
    
    print("\n" + "="*80)
    print("✓ EMBEDDING GENERATION COMPLETE")
    print("="*80)
    print(f"\nChromaDB Directory: ./chroma_db")
    print(f"Collection Name: {collection_name}")
    print(f"Embedding Model: all-MiniLM-L6-v2")
    print(f"Total Records: {collection.count()}")
    print("\nYou can now use ChromaDB for semantic searches and patient similarity matching!")


if __name__ == "__main__":
    main()
