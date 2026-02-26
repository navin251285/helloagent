import chromadb
from sentence_transformers import SentenceTransformer
import sys

# Initialize ChromaDB client
client = chromadb.PersistentClient(path="./chroma_db")

# Load the collection
try:
    collection = client.get_collection(name="patient_profiles")
    print(f"✓ Loaded collection with {collection.count()} patient visit records\n")
except Exception as e:
    print(f"Error: Could not load patient profiles collection.")
    print(f"Make sure to run 'create_embeddings.py' first to generate the database.")
    sys.exit(1)

# Initialize embedding model
print("Loading embedding model: all-MiniLM-L6-v2...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✓ Model loaded successfully\n")


def semantic_search(query_text, n_results=5, min_risk_score=None, max_risk_score=None):
    """
    Search for similar patient cases using semantic search
    
    Args:
        query_text: Natural language query describing symptoms, conditions, or patient characteristics
        n_results: Number of similar cases to return (default: 5)
        min_risk_score: Optional minimum risk score filter
        max_risk_score: Optional maximum risk score filter
    """
    print("="*80)
    print("SEMANTIC SEARCH RESULTS")
    print("="*80)
    print(f"Query: {query_text}")
    print(f"Showing top {n_results} similar cases")
    
    if min_risk_score is not None or max_risk_score is not None:
        risk_filter = []
        if min_risk_score is not None:
            risk_filter.append(f"Risk Score >= {min_risk_score}")
        if max_risk_score is not None:
            risk_filter.append(f"Risk Score <= {max_risk_score}")
        print(f"Filters: {' and '.join(risk_filter)}")
    
    print("="*80)
    
    # Perform semantic search
    results = collection.query(
        query_texts=[query_text],
        n_results=n_results * 3  # Get more results for filtering
    )
    
    if not results['metadatas'] or not results['metadatas'][0]:
        print("\nNo results found.")
        return
    
    # Filter by risk score if specified
    filtered_results = []
    for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
        risk_score = float(metadata['risk_score'])
        
        if min_risk_score is not None and risk_score < min_risk_score:
            continue
        if max_risk_score is not None and risk_score > max_risk_score:
            continue
        
        filtered_results.append((metadata, distance))
        
        if len(filtered_results) >= n_results:
            break
    
    if not filtered_results:
        print("\nNo results found matching the criteria.")
        return
    
    # Display results
    for i, (metadata, distance) in enumerate(filtered_results, 1):
        similarity_score = (1 - distance) * 100  # Convert to percentage
        
        print(f"\n{i}. {metadata['patient_name']} (Patient ID: {metadata['patient_id']})")
        print(f"   Similarity: {similarity_score:.2f}%")
        print(f"   Visit Date: {metadata['visit_date']} (Visit #{metadata['visit_number']} of {metadata['total_visits']})")
        print(f"   Demographics: {metadata['age']} years old, {metadata['gender']}")
        print(f"   Risk Score: {metadata['risk_score']} (Base: {metadata['base_score']})")
        print(f"   Symptoms: {metadata['symptoms']}")
        print(f"   Vitals: BP {metadata['bp']}, Blood Sugar {metadata['sugar']} mg/dL")
        print(f"   Medical History: {metadata['medical_history']}")
        print(f"   Medications: {metadata['current_medications']}")
        print(f"   Outcome: {metadata['outcome']}")
    
    print("\n" + "="*80)


def search_by_patient_id(patient_id):
    """Search for all visits by a specific patient ID"""
    print("="*80)
    print(f"PATIENT HISTORY - ID: {patient_id}")
    print("="*80)
    
    results = collection.get(
        where={"patient_id": str(patient_id)}
    )
    
    if not results['metadatas']:
        print(f"\nNo records found for patient ID: {patient_id}")
        return
    
    patient_name = results['metadatas'][0]['patient_name']
    age = results['metadatas'][0]['age']
    gender = results['metadatas'][0]['gender']
    
    print(f"Patient: {patient_name}")
    print(f"Demographics: {age} years old, {gender}")
    print(f"Total Visits: {len(results['metadatas'])}")
    print("="*80)
    
    # Sort by visit number
    visits = sorted(zip(results['metadatas'], results['documents']), 
                   key=lambda x: int(x[0]['visit_number']))
    
    for metadata, document in visits:
        print(f"\nVisit {metadata['visit_number']} - {metadata['visit_date']}")
        print(f"  Risk Score: {metadata['risk_score']} (Base: {metadata['base_score']})")
        print(f"  Symptoms: {metadata['symptoms']}")
        print(f"  Vitals: BP {metadata['bp']}, Blood Sugar {metadata['sugar']} mg/dL")
        print(f"  Medical History: {metadata['medical_history']}")
        print(f"  Medications: {metadata['current_medications']}")
        print(f"  Outcome: {metadata['outcome']}")
    
    print("\n" + "="*80)


def search_high_risk_patients(threshold=7.0, n_results=10):
    """Find patients with high risk scores"""
    print("="*80)
    print(f"HIGH-RISK PATIENTS (Risk Score >= {threshold})")
    print("="*80)
    
    all_records = collection.get()
    
    high_risk_patients = []
    for metadata in all_records['metadatas']:
        if float(metadata['risk_score']) >= threshold:
            high_risk_patients.append(metadata)
    
    # Sort by risk score (highest first)
    high_risk_patients.sort(key=lambda x: float(x['risk_score']), reverse=True)
    
    if not high_risk_patients:
        print(f"\nNo patients found with risk score >= {threshold}")
        return
    
    print(f"Found {len(high_risk_patients)} high-risk visits")
    print(f"Showing top {min(n_results, len(high_risk_patients))} results")
    print("="*80)
    
    for i, metadata in enumerate(high_risk_patients[:n_results], 1):
        print(f"\n{i}. {metadata['patient_name']} (Patient ID: {metadata['patient_id']})")
        print(f"   Risk Score: {metadata['risk_score']} ⚠️")
        print(f"   Visit Date: {metadata['visit_date']}")
        print(f"   Demographics: {metadata['age']} years old, {metadata['gender']}")
        print(f"   Symptoms: {metadata['symptoms']}")
        print(f"   Vitals: BP {metadata['bp']}, Blood Sugar {metadata['sugar']} mg/dL")
        print(f"   Medical History: {metadata['medical_history']}")
        print(f"   Outcome: {metadata['outcome']}")
    
    print("\n" + "="*80)


def search_by_condition(condition):
    """Search for patients with a specific medical condition"""
    print("="*80)
    print(f"PATIENTS WITH CONDITION: {condition}")
    print("="*80)
    
    all_records = collection.get()
    
    matching_patients = []
    for metadata in all_records['metadatas']:
        if condition.lower() in metadata['medical_history'].lower():
            matching_patients.append(metadata)
    
    if not matching_patients:
        print(f"\nNo patients found with condition: {condition}")
        return
    
    print(f"Found {len(matching_patients)} visits with {condition}")
    print("="*80)
    
    # Sort by risk score
    matching_patients.sort(key=lambda x: float(x['risk_score']), reverse=True)
    
    for i, metadata in enumerate(matching_patients[:10], 1):
        print(f"\n{i}. {metadata['patient_name']} (Patient ID: {metadata['patient_id']})")
        print(f"   Risk Score: {metadata['risk_score']}")
        print(f"   Visit Date: {metadata['visit_date']}")
        print(f"   Demographics: {metadata['age']} years old, {metadata['gender']}")
        print(f"   Symptoms: {metadata['symptoms']}")
        print(f"   Medical History: {metadata['medical_history']}")
        print(f"   Medications: {metadata['current_medications']}")
    
    print("\n" + "="*80)


def interactive_mode():
    """Interactive query interface"""
    print("\n" + "="*80)
    print("PATIENT PROFILE SIMILARITY SEARCH - INTERACTIVE MODE")
    print("="*80)
    print("\nAvailable Commands:")
    print("  1. Type a natural language query (e.g., 'chest pain and high blood pressure')")
    print("  2. 'patient:<ID>' - Get history for specific patient (e.g., 'patient:5')")
    print("  3. 'highrisk:<threshold>' - Find high-risk patients (e.g., 'highrisk:7.0')")
    print("  4. 'condition:<name>' - Find patients with condition (e.g., 'condition:diabetes')")
    print("  5. 'quit' or 'exit' - Exit the program")
    print("\nOptional parameters for semantic search:")
    print("  Add '--results N' to change number of results (default: 5)")
    print("  Add '--minrisk X' to filter by minimum risk score")
    print("  Add '--maxrisk Y' to filter by maximum risk score")
    print("\nExamples:")
    print("  chest pain and dizziness --results 10")
    print("  shortness of breath --minrisk 5.0 --results 3")
    print("="*80 + "\n")
    
    while True:
        try:
            user_input = input("Enter query: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\nGoodbye!")
                break
            
            # Parse command
            if user_input.lower().startswith('patient:'):
                patient_id = user_input.split(':', 1)[1].strip()
                search_by_patient_id(patient_id)
            
            elif user_input.lower().startswith('highrisk:'):
                threshold_str = user_input.split(':', 1)[1].strip()
                try:
                    threshold = float(threshold_str)
                    search_high_risk_patients(threshold)
                except ValueError:
                    print(f"Error: Invalid threshold value '{threshold_str}'. Please use a number.")
            
            elif user_input.lower().startswith('condition:'):
                condition = user_input.split(':', 1)[1].strip()
                search_by_condition(condition)
            
            else:
                # Parse semantic search parameters
                parts = user_input.split('--')
                query_text = parts[0].strip()
                
                n_results = 5
                min_risk_score = None
                max_risk_score = None
                
                for part in parts[1:]:
                    part = part.strip()
                    if part.startswith('results '):
                        try:
                            n_results = int(part.split()[1])
                        except (IndexError, ValueError):
                            print("Warning: Invalid --results parameter, using default (5)")
                    elif part.startswith('minrisk '):
                        try:
                            min_risk_score = float(part.split()[1])
                        except (IndexError, ValueError):
                            print("Warning: Invalid --minrisk parameter, ignoring")
                    elif part.startswith('maxrisk '):
                        try:
                            max_risk_score = float(part.split()[1])
                        except (IndexError, ValueError):
                            print("Warning: Invalid --maxrisk parameter, ignoring")
                
                semantic_search(query_text, n_results, min_risk_score, max_risk_score)
            
            print()  # Empty line for readability
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"\nError: {e}")
            print("Please try again.\n")


def main():
    """Main function - run single query and exit"""
    if len(sys.argv) > 1:
        # Command-line mode
        query = ' '.join(sys.argv[1:])
        
        # Check for interactive mode request
        if query.lower() == 'interactive':
            interactive_mode()
            return
        
        if query.lower().startswith('patient:'):
            patient_id = query.split(':', 1)[1].strip()
            search_by_patient_id(patient_id)
        elif query.lower().startswith('highrisk:'):
            threshold = float(query.split(':', 1)[1].strip())
            search_high_risk_patients(threshold)
        elif query.lower().startswith('condition:'):
            condition = query.split(':', 1)[1].strip()
            search_by_condition(condition)
        else:
            semantic_search(query, n_results=5)
    else:
        # Run example queries only
        print("EXAMPLE QUERIES:\n")
        print("Run with arguments for specific queries. Examples:")
        print("  python query_patients.py \"chest pain and high blood pressure\"")
        print("  python query_patients.py patient:5")
        print("  python query_patients.py highrisk:7.0")
        print("  python query_patients.py condition:diabetes")
        print("\n" + "="*80 + "\n")
        
        # Example 1: Semantic search
        semantic_search("patient with chest pain and high blood pressure", n_results=3)
        print()
        
        # Example 2: High-risk patients
        search_high_risk_patients(threshold=7.0, n_results=5)
        print()
        
        # Example 3: Search by condition
        search_by_condition("diabetes")
        print()
        
        print("\n" + "="*80)
        print("For interactive mode, run: python query_patients.py interactive")
        print("="*80)


if __name__ == "__main__":
    main()
