# Patient Summary Generation System - Complete Architecture

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Components](#components)
4. [Data Flow](#data-flow)
5. [How to Run](#how-to-run)

---

## 🏗️ System Overview

This is an AI-powered clinical decision support system that:
- **Searches** for patients with similar health profiles using semantic similarity (Chroma DB)
- **Generates** clinical summaries using a local LLM (Ollama + Phi)
- **Saves** summaries persistently to CSV
- **Uses** MCP (Model Context Protocol) for client-server communication

**Key Features:**
- 🔍 Disease/symptom-based patient search (not keyword matching, but semantic similarity)
- 🤖 Local LLM-based summary generation (privacy-preserving, no cloud API)
- 📊 Vector database for intelligent patient matching
- 🔌 MCP protocol for robust async communication
- 💾 CSV-based persistence

---

## 🎯 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         USER TERMINAL (Interactive)                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                   │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │              MCP CLIENT (mcp_client.py)                                  │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │ 1. User Input: Disease/Symptom Keyword (e.g., "diabetes")     │    │   │
│  │  │ 2. Display Search Results (5 matching patients)                │    │   │
│  │  │ 3. User Selects Patient                                        │    │   │
│  │  │ 4. Show Patient Details                                        │    │   │
│  │  │ 5. Request Summary Generation                                  │    │   │
│  │  │ 6. Extract Summary Text                                        │    │   │
│  │  │ 7. Confirm & Save                                              │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│           │                                                                      │
│           │  MCP Stdio Communication (Async)                                     │
│           │  • search_patients_by_disease                                        │
│           │  • get_patient_summary                                               │
│           │  • generate_summary (calls Ollama)                                   │
│           │  • update_patient_summary                                            │
│           ▼                                                                      │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │              MCP SERVER (mcp_server.py)                                  │   │
│  │  ┌─────────────────────────────────────────────────────────────────┐    │   │
│  │  │ • Tool Handlers for 4 operations                                │    │   │
│  │  │ • CSV Read/Write Operations                                     │    │   │
│  │  │ • Chroma DB Query Interface                                     │    │   │
│  │  │ • Ollama HTTP Client                                            │    │   │
│  │  │ • Patient Data Manager                                          │    │   │
│  │  └─────────────────────────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
│           │                                                                      │
└───────────┼──────────────────────────────────────────────────────────────────────┘
            │
    ┌───────┴──────────┬─────────────────────┬──────────────────┐
    │                  │                     │                  │
    ▼                  ▼                     ▼                  ▼
┌─────────────┐  ┌──────────────┐  ┌────────────────┐  ┌──────────────┐
│  Chroma DB  │  │  CSV Files   │  │ Ollama (Local) │  │  Data Files  │
│ (Vector DB) │  │              │  │   + Phi LLM    │  │              │
├─────────────┤  ├──────────────┤  ├────────────────┤  ├──────────────┤
│ • 100 pts   │  │• patients_   │  │ • Port: 11434  │  │• patients_   │
│   indexed   │  │  data.csv    │  │ • Model:Phi    │  │  data.csv    │
│ • Symptoms  │  │• patient_    │  │ • 2.7B params  │  │• 100 patient │
│   as docs   │  │  summaries.  │  │ • CPU mode     │  │  profiles    │
│ • ST embed  │  │  csv         │  │ • Generation   │  │              │
│   enabled   │  │              │  │   30-60 sec    │  │              │
└─────────────┘  └──────────────┘  └────────────────┘  └──────────────┘
```

---

## 🔧 Components

### 1. **Data Generation** (`generate_patients.py`)
**Purpose:** Create initial patient dataset with realistic health profiles

**Outputs:**
- `patients_data.csv` - 100 patient records with health data
- Columns: `patient_id`, `name`, `age`, `gender`, `current_symptoms`, `current_bp`, `current_sugar`, `current_medications`, `risk_score`, `medical_history`, `visit_history`

**How it works:**
```
Import faker → Generate random patient demographics
        ↓
Select from symptom pool → Create symptom combinations
        ↓
Generate health metrics (BP, sugar, risk) → Create realistic profiles
        ↓
Output to CSV
```

---

### 2. **Chroma DB Setup** (`chroma_setup.py`)
**Purpose:** Create vector embeddings and index patient profiles for semantic search

**Process:**
```
Read patients_data.csv (100 records)
        ↓
For each patient:
  - Combine symptoms + medical_history + visit_history
  - Create search document
        ↓
Generate embeddings using sentence-transformers
  - Model: all-MiniLM-L6-v2 (lightweight, accurate)
  - Converts text → 384-dim vector
        ↓
Store in Chroma persistent collection
  - Vector DB path: ./chroma_db
  - Collection name: "patients"
```

**Result:** Semantic search enabled - can find similar patients by symptom description, not exact keyword matching

---

### 3. **MCP Server** (`mcp_server.py`)
**Purpose:** Backend service that handles all patient operations

**4 Tools Exposed:**

#### Tool 1: `search_patients_by_disease`
```
Input: disease_keyword (e.g., "diabetes", "chest pain")
         ↓
Query Chroma DB with semantic similarity
         ↓
Return top 5 most similar patients with metadata
```

#### Tool 2: `get_patient_summary`
```
Input: patient_id
         ↓
Read patient_summaries.csv
         ↓
Return patient details + current summary (if exists)
```

#### Tool 3: `generate_summary`
```
Input: patient_id
         ↓
Read patient health data from patients_data.csv
         ↓
Create LLM prompt with:
  - Name, age, gender
  - Current symptoms
  - Blood pressure, blood sugar
  - Medical history
  - Current medications
  - Risk score
         ↓
Send HTTP POST to Ollama (localhost:11434)
  - Model: phi
  - Stream: false
  - Temperature: 0.7
         ↓
Return generated clinical summary (2-3 sentences)
```

#### Tool 4: `update_patient_summary`
```
Input: patient_id, summary_text
         ↓
Read patient_summaries.csv (100 records)
         ↓
Find patient by ID
         ↓
Update summary field
         ↓
Write back to CSV (all 100 records)
         ↓
Success response
```

---

### 4. **MCP Client** (`mcp_client.py`)
**Purpose:** Interactive user interface for searching and generating summaries

**Workflow:**
```
1. Display welcome message
   ↓
2. Get disease keyword from user
   ↓
3. Call server: search_patients_by_disease(keyword)
   ↓
4. Display 5 matching patients with:
   - ID, Name, Age, Symptoms
   ↓
5. Ask user to select (1-5)
   ↓
6. Call server: get_patient_summary(selected_id)
   ↓
7. Display patient details
   ↓
8. Call server: generate_summary(selected_id)
   - Wait 30-60 seconds for Ollama
   ↓
9. Display generated summary
   ↓
10. Ask "Save to CSV? (y/n)"
    ↓
11. If yes:
    - Extract summary text from response
    - Parse and clean
    - Call server: update_patient_summary(id, text)
    - Confirm save
    ↓
12. Ask "Continue? (y/n)"
    ↓
13. Loop or exit
```

---

### 5. **Ollama + Phi LLM**
**Purpose:** Generate realistic clinical summaries from patient data

**Setup:**
```
- Ollama: Open-source LLM runtime
- Phi: 2.7B parameter model (lightweight, CPU-friendly)
- Port: 11434
- API: HTTP POST /api/generate

Before running client:
$ ollama serve          # Terminal 1 (keep running)

$ python3 mcp_client.py # Terminal 2
```

**Why Phi?**
- ✅ Lightweight (2.7B params vs 7B+)
- ✅ Fast on CPU (still 30-60 sec per summary)
- ✅ Accurate for clinical text
- ✅ Privacy (local, no cloud calls)

---

## 📊 Data Flow Diagram

### Complete User Journey:

```
┌──────────────────────┐
│  User Starts Client  │
└──────────────┬───────┘
               │
               ▼
        ┌─────────────┐
        │ "Enter      │
        │  disease"   │
        └──────┬──────┘
               │
   ┌───────────┴────────────┐
   │ MCP: search_patients   │
   │ → Chroma DB query      │
   │ ← top 5 patients       │
   │                        │
   │  [ID→Name→Symptoms]    │
   └───────────┬────────────┘
               │
               ▼
        User selects 1-5
               │
               ├→ 1: ID=41, Karen Jones
               ├→ 2: ID=84, Patrick Robinson
               ├→ 3: ID=55, John Johnson  ← User picks this
               ├→ 4: ID=69, Sarah Gutierrez
               └→ 5: ID=9,  Larry Bailey
               │
               ▼
   ┌───────────────────────┐
   │ MCP: get_patient_     │
   │ summary(ID=55)        │
   │ ← Patient details     │
   └───────────┬───────────┘
               │
               ▼
        ┌─────────────────────┐
        │ "Generating         │
        │  summary..."        │
        │ (waiting 30-60 sec) │
        └────────────┬────────┘
                     │
       ┌─────────────┴──────────────┐
       │ MCP: generate_summary      │
       │ → Patient ID to server     │
       │ → Server reads patient     │
       │   data from CSV            │
       │ → Creates prompt           │
       │ → HTTP to Ollama Phi       │
       │ ← Returns summary text     │
       │                            │
       │ Summary generated:         │
       │ "Patient John Johnson,     │
       │  a 77-year-old with...    │
       │  requires monitoring..."   │
       └────────────┬───────────────┘
                    │
                    ▼
            ┌──────────────────┐
            │ "Save to CSV?    │
            │  (y/n)"          │
            └────┬─────────┬───┘
                 │         │
                 ▼         ▼
              YES          NO
               │            └→ Loop back
               │               to Step 2
               ▼
┌──────────────────────────────────────┐
│ Extract summary text from response   │
│ Clean up blank lines                 │
│ Validate (not empty)                 │
└─────────────────┬────────────────────┘
                  │
       ┌──────────┴──────────┐
       │ MCP: update_patient │
       │ _summary(55, text)  │
       │ → Server reads CSV  │
       │ → Finds patient 55  │
       │ → Updates summary   │
       │ → Writes CSV        │
       │ ← Confirmation      │
       └──────────┬──────────┘
                  │
                  ▼
        ┌──────────────────────┐
        │ Summary saved to     │
        │ patient_summaries.csv│
        │                      │
        │ Patient 55:          │
        │ "John Johnson, a     │
        │  77-year-old..."     │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ "Continue? (y/n)"    │
        └────┬──────────┬──────┘
             │          │
             ▼          ▼
            YES         NO
             │           └→ EXIT
             └─→ Loop back to Step 2
```

---

## 📁 File Structure

```
10_generate_patient_profiles/
├── generate_patients.py          # Create patient dataset
├── chroma_setup.py              # Index patients in Chroma
├── mcp_server.py                # Backend server (4 tools)
├── mcp_client.py                # Interactive CLI client
├── patients_data.csv            # 100 patient profiles (read-only)
├── patient_summaries.csv        # Generated summaries (persistent)
├── chroma_db/                   # Vector database (created by setup)
├── test_*.py                    # Test scripts
└── SYSTEM_ARCHITECTURE.md       # This file
```

---

## 🚀 How to Run

### Prerequisites
1. Python 3.8+
2. Ollama installed (https://ollama.ai)
3. Phi model downloaded

### Setup (One-time)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate patient data (if not exists)
python3 generate_patients.py

# 3. Create Chroma DB index
python3 chroma_setup.py

# Verify chroma_db/ directory is created
ls -la chroma_db/
```

### Runtime (Every time you use the system)

**Terminal 1 - Start Ollama:**
```bash
ollama serve
# Output: Listening on 127.0.0.1:11434
# Keep this running!
```

**Terminal 2 - Start the interactive client:**
```bash
cd /path/to/10_generate_patient_profiles
python3 mcp_client.py

# Then:
# 1. Enter disease keyword: diabetes
# 2. Select patient: 3
# 3. Wait for summary generation
# 4. Confirm save: y
# 5. Continue: y/n
```

---

## 🔌 Technologies Used

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Vector DB | Chroma | Semantic similarity search |
| Embeddings | sentence-transformers | Text → vectors (384-dim) |
| LLM | Ollama + Phi | Local summary generation |
| Protocol | MCP (stdio) | Async client-server |
| Data | CSV | Summary persistence |
| async/await | Python asyncio | Non-blocking operations |

---

## 📊 Performance Characteristics

- **Search:** 10-50ms (Chroma DB)
- **Summary Generation:** 30-60 seconds (Ollama Phi on CPU)
- **CSV Read/Write:** <100ms (100 records)
- **Total workflow time:** ~60 seconds per patient

---

## 🔐 Privacy & Security

- ✅ **No cloud calls** - Everything runs locally
- ✅ **MCP uses stdio** - Process-based isolation
- ✅ **CSV-based** - Portable, no database setup
- ✅ **Open source** - Transparent, auditable code

---

## 🎓 Architecture Highlights

1. **Separation of Concerns**
   - Client (UI) ←→ Server (Logic) ←→ Storage (CSV) ←→ ML (Ollama)

2. **Async Communication**
   - MCP handles async tool calls without blocking

3. **Semantic Search**
   - Chroma DB finds conceptually similar patients, not just keywords

4. **Privacy-First**
   - Local LLM generation, no API keys, no cloud logging

5. **Minimal I/O**
   - Single CSV read/write per operation (optimized)

---

## 📝 Example Output

```
====================================================================================================
🏥 PATIENT SUMMARY GENERATION SYSTEM
====================================================================================================

----------------------------------------------------------------------------------------------------
STEP 1: SEARCH PATIENTS BY DISEASE/SYMPTOMS
----------------------------------------------------------------------------------------------------

Enter disease/symptom keyword: diabetes

Found 5 patients matching 'diabetes':

1. ID: 11  | Name: Jerry Rivera        | Age: 59 | Symptoms: confusion, elevated BP, high sugar
2. ID: 45  | Name: Janet Torres        | Age: 70 | Symptoms: weakness, elevated BP, high sugar
3. ID: 70  | Name: Jerry Young         | Age: 52 | Symptoms: elevated BP, high sugar, fatigue
4. ID: 13  | Name: Donald Evans        | Age: 65 | Symptoms: confusion, elevated BP, high sugar
5. ID: 50  | Name: Gregory Bailey      | Age: 68 | Symptoms: weakness, elevated BP, high sugar

----------------------------------------------------------------------------------------------------
STEP 2: SELECT A PATIENT
----------------------------------------------------------------------------------------------------

Select patient number (1-5): 1

====================================================================================================
PATIENT DETAILS (ID: 11)
====================================================================================================
Patient ID: 11
Name: Jerry Rivera
Age: 59
Gender: Male
Current Symptoms: confusion, elevated blood pressure, elevated blood sugar
Current BP: 150/90 mmHg
Current Sugar: 180 mg/dL
Current Medications: Metformin, Lisinopril
Medical History: Type 2 Diabetes, Hypertension
Risk Score: 8.2/10

====================================================================================================
GENERATED SUMMARY (via Ollama Phi)
====================================================================================================
Patient Jerry Rivera presents with Type 2 Diabetes and Hypertension with elevated blood pressure 
and glucose levels. Current medications include Metformin and Lisinopril. Recommend continued 
medication adherence, dietary modifications, and close monitoring of vital signs to prevent 
complications.

Save to patient_summaries.csv? (y/n): y

✓ Summary saved successfully!
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| Ollama connection refused | Run `ollama serve` in another terminal |
| Permission denied on CSV | `chmod 666 patient_summaries.csv` |
| Chroma DB not found | Run `python3 chroma_setup.py` |
| Slow summary generation | Normal - Phi on CPU takes 30-60 sec |
| Empty search results | Try different symptom keywords |

---

**Last Updated:** February 25, 2026
