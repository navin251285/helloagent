# Chroma DB Setup Module - `chroma_setup.py`

## 📌 Purpose
Create a vector database index of all 100 patient profiles for fast semantic similarity search. Enables finding patients by disease/symptom description, not just keyword matching.

## 🎯 What It Does

Converts patient health data into vector embeddings and stores them in a persistent Chroma database:
1. Reads `patients_data.csv` (100 patient records)
2. Combines symptoms + medical history + visit history into search documents
3. Generates embeddings using sentence-transformers
4. Stores in Chroma persistent collection
5. Enables semantic search: "find patients with diabetes" → returns top 5 conceptually similar patients

## 🧮 Vector Embedding Process

### Traditional Search (Keyword-based)
```
Query: "diabetes"
Search: patients where [medical_history] LIKE '%diabetes%'
Result: Exact matches only

Problem: ❌ Misses patients with "Type 2 Diabetes", "high blood sugar", "glucose issues"
```

### Semantic Search (Vector-based)
```
Query: "diabetes"
         ↓
Convert to embedding: [0.123, -0.456, 0.789, ..., 0.234]  (384 dimensions)
                      ↑
                      sentence-transformers model
         ↓
Find embeddings in Chroma with highest cosine similarity
         ↓
Return top 5 patients: Jerry Rivera, Janet Torres, John Johnson, ...

Advantage: ✅ Finds conceptually related patients even with different wording
```

## 🏗️ Architecture

```
patients_data.csv (100 rows)
         │
         │ Read all patients
         ▼
For each patient:
┌─────────────────────────────────────┐
│ Combine health data:                │
│                                     │
│ ID: 11                              │
│ Name: Jerry Rivera                  │
│ Symptoms: confusion, elevated BP    │
│ Medications: Metformin, Lisinopril │
│ Medical History: Type 2 Diabetes    │
│ Visit History: "2024-12: monitor"   │
│                                     │
│ → Create search document:           │
│ "confusion elevated blood pressure  │
│  metformin lisinopril type 2        │
│  diabetes..."                       │
└──────────────┬──────────────────────┘
               │
               ▼
         Convert to embedding
     (sentence-transformers)
               │
              384-dim vector
         [0.12, -0.45, 0.78, ...]
               │
               ▼
        Store in Chroma DB
      with patient metadata
               │
               │ (repeat for 100 patients)
               │
               ▼
      chroma_db/ directory
    (persistent vector database)
```

## 📦 Installation & Dependencies

```bash
pip install chromadb
pip install sentence-transformers
pip install pandas
```

## 🔄 Setup Process

### Step 1: Read Patient Data
```python
import pandas as pd

df = pd.read_csv('patients_data.csv')
# 100 rows, 11 columns
```

### Step 2: Create Search Documents
```python
for idx, row in df.iterrows():
    # Combine all health-related text
    document = f"""
    Patient: {row['name']}
    Age: {row['age']}
    Symptoms: {row['current_symptoms']}
    Blood Pressure: {row['current_bp']}
    Blood Sugar: {row['current_sugar']}
    Medications: {row['current_medications']}
    Medical History: {row['medical_history']}
    Visit History: {row['visit_history']}
    """
    
    documents.append(document)
    metadata.append({
        'patient_id': str(row['patient_id']),
        'name': row['name'],
        'age': row['age'],
        'symptoms': row['current_symptoms']
    })
```

### Step 3: Generate Embeddings
```python
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')
# - Small & fast (~30MB)
# - Produces 384-dimensional vectors
# - Good accuracy for medical text

# Convert documents to embeddings
embeddings = model.encode(documents, convert_to_tensor=True)
# Result: (100, 384) matrix
```

### Step 4: Store in Chroma
```python
import chromadb

# Create persistent client
client = chromadb.PersistentClient(path="./chroma_db")

# Create collection
collection = client.get_or_create_collection(
    name="patients",
    metadata={"hnsw:space": "cosine"}  # Cosine similarity
)

# Add embeddings to collection
for i, doc in enumerate(documents):
    collection.add(
        documents=[doc],
        embeddings=[embeddings[i].tolist()],  # Convert to list
        metadatas=[metadata[i]],
        ids=[str(i)]
    )
```

## 🚀 Running the Setup

```bash
cd /path/to/10_generate_patient_profiles

# Run setup
python3 chroma_setup.py

# Output:
# ✓ Reading patients_data.csv
# ✓ Creating 100 search documents
# ✓ Generating embeddings (all-MiniLM-L6-v2)
# ✓ Storing in Chroma DB
# ✓ Setup complete: ./chroma_db
# ✓ Collection size: 100 documents
```

## 📍 Output Structure

```
chroma_db/
├── chroma.db
├── 000001.bin
├── 000002.bin
└── index/
    └── index_data.json
```

All files are auto-generated by Chroma. Don't edit manually.

## 🔍 Semantic Search Example

After setup, you can search:

```python
from mcp_server import search_patients_by_disease

# Query 1
results = search_patients_by_disease("diabetes")
# Returns: Patients with high sugar, Type 2 Diabetes, etc.

# Query 2
results = search_patients_by_disease("chest pain")
# Returns: Patients with cardiac symptoms, high BP, etc.

# Query 3
results = search_patients_by_disease("breathing difficulty")
# Returns: Patients with shortness of breath, asthma, etc.

# Even loose queries work:
results = search_patients_by_disease("old patient with high numbers")
# Returns: Elderly patients with elevated metrics
```

## 📊 Embedding Model Details

**Model:** `all-MiniLM-L6-v2`
- **Publisher:** Sentence-Transformers (Hugging Face)
- **Size:** ~30 MB
- **Vector dimension:** 384
- **Use case:** General semantic search
- **Speed:** Very fast (<1ms per document)
- **Accuracy:** High for medical text

**Why this model?**
- ✅ Lightweight (fast loading)
- ✅ Accurate for medical terminology
- ✅ Pre-trained on diverse text
- ✅ No fine-tuning needed

## 🎯 Search Algorithm

Chroma uses **HNSW (Hierarchical Navigable Small World)** for fast similarity search:

```
Query embedding: [0.12, -0.45, 0.78, ...]
                        │
                        ▼
        Compare cosine similarity with all 100 embeddings
                        │
                        ├─ Jerry Rivera:     similarity = 0.94 ✓ (diabetes match)
                        ├─ Janet Torres:     similarity = 0.91 ✓ (diabetes match)
                        ├─ John Johnson:     similarity = 0.88 ✓ (high BP match)
                        ├─ Sarah Gutierrez:  similarity = 0.85 ✓ (breathing match)
                        ├─ Larry Bailey:     similarity = 0.82 ✓ (symptoms match)
                        ├─ Justin Cox:       similarity = 0.65   (weak match)
                        └─ ...
                        │
                        ▼
            Return top 5: [11, 45, 55, 69, 9]
```

**Complexity:**
- Insert: O(log n) amortized
- Search: O(log n) average case
- Total for 100 patients: ~milliseconds

## 🔌 Integration with MCP Server

The server uses Chroma in `search_patients_by_disease()`:

```python
def search_patients_by_disease(disease_keyword, top_k=5):
    collection = chroma_client.get_collection(name="patients")
    
    # Query with semantic similarity
    results = collection.query(
        query_texts=[disease_keyword],  # User input
        n_results=top_k * 2             # Get top 10, return top 5
    )
    
    # Extract patient metadata
    patients = []
    for metadata in results['metadatas'][0][:top_k]:
        patients.append(metadata)
    
    return patients
```

## ⚙️ Configuration Options

**If you want to change similarity metric:**
```python
# Current: Cosine similarity
metadata={"hnsw:space": "cosine"}

# Options:
# "cosine"    - Cosine similarity (0-1, higher = more similar)
# "l2"        - Euclidean distance (lower = more similar)
# "ip"        - Inner product
```

**If you want different embedding model:**
```python
# Current: all-MiniLM-L6-v2 (384-dim, fast)

# Alternative: all-mpnet-base-v2 (768-dim, more accurate, slower)
model = SentenceTransformer('all-mpnet-base-v2')

# Alternative: distiluse-base-multilingual (multilingual support)
model = SentenceTransformer('distiluse-base-multilingual-cased-v2')
```

## 🧪 Testing Chroma

After setup, verify it works:

```bash
python3 << 'EOF'
import chromadb

client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="patients")

print(f"✓ Collection loaded")
print(f"✓ Documents indexed: {collection.count()}")

# Test search
results = collection.query(
    query_texts=["diabetes"],
    n_results=5
)

print(f"✓ Query successful")
print(f"✓ Found {len(results['metadatas'][0])} results")
for meta in results['metadatas'][0][:3]:
    print(f"  - {meta['name']} (ID: {meta['patient_id']})")
EOF
```

Expected output:
```
✓ Collection loaded
✓ Documents indexed: 100
✓ Query successful
✓ Found 5 results
  - Jerry Rivera (ID: 11)
  - Janet Torres (ID: 45)
  - John Johnson (ID: 55)
```

## 🔐 Performance Metrics

- **Indexing time:** ~5-10 seconds (100 patients)
- **Search time:** 10-50 milliseconds per query
- **Storage:** ~5-10 MB (chroma_db/ directory)
- **Memory:** ~100-200 MB during initialization

## 📋 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: chromadb` | `pip install chromadb` |
| `No module named 'sentence_transformers'` | `pip install sentence-transformers` |
| Slow first run | downloading embedding model (~30MB), normal |
| Chroma connection refused | Run from correct directory with `./chroma_db/` |
| Empty search results | Try different keywords, chroma_db may not be indexed |

## 🎓 Learn More

- **Chroma docs:** https://docs.trychroma.com
- **sentence-transformers:** https://www.sbert.net
- **Vector databases:** https://en.wikipedia.org/wiki/Vector_database
- **HNSW algorithm:** https://arxiv.org/abs/1802.02413

---

**When to rebuild:**
- After adding new patients to `patients_data.csv`
- After changing embedding model
- If you want to tune similarity metric

**Rebuild command:**
```bash
rm -rf chroma_db/              # Delete old index
python3 chroma_setup.py        # Create new index
```
