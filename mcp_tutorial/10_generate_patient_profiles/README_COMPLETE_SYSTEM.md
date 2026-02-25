# Patient Summary Generation System

## Overview

This system combines **Chroma DB** (vector database), **Ollama + Phi LLM**, and **MCP (Model Context Protocol)** to create an intelligent patient management workflow:

1. **Disease Search**: User enters a disease/symptom keyword
2. **Vector Search**: Chroma DB finds top 5 matching patient profiles using semantic similarity
3. **Patient Selection**: User selects one patient from results
4. **Summary Generation**: Ollama (Phi model) generates a clinical summary from patient health data
5. **Data Persistence**: Summary is saved to `patient_summaries.csv`

## Architecture

```
┌─────────────────┐
│  MCP Client     │  (Disease search, patient selection, UI)
└────────┬────────┘
         │ MCP Protocol (stdio)
         │
┌────────▼────────────────────────────────────────────────┐
│            MCP Server (mcp_server.py)                    │
├─────────────────────────────────────────────────────────┤
│ Tools Available:                                         │
│  • search_patients_by_disease → Chroma DB search        │
│  • generate_summary → Ollama Phi LLM                    │
│  • get_patient_summary → CSV read                       │
│  • update_patient_summary → CSV write                   │
└──┬──────────────────────┬──────────────────────┬────────┘
   │                      │                      │
   ▼                      ▼                      ▼
[Chroma DB]         [Ollama + Phi]         [patient_summaries.csv]
Vector DB with      Local LLM (2.7B)       Persistent storage
100 patients        Running on CPU
```

## Setup Instructions

### 1. Verify Installation

Check that everything is installed:

```bash
cd mcp_tutorial/10_generate_patient_profiles

# Verify Ollama
ollama list
# Output: phi:latest  1.6 GB

# Verify Chroma
ls -la chroma_db/
# Should exist and contain index data

# Verify CSV
ls -la patient_summaries.csv
```

### 2. Start Ollama Service

Ollama should be running as a system service on port 11434:

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start it manually:
ollama serve
```

### 3. Run the Client

```bash
cd mcp_tutorial/10_generate_patient_profiles
python3 mcp_client.py
```

## Workflow Example

```
$ python3 mcp_client.py

================================================================================
🏥 PATIENT SUMMARY GENERATION SYSTEM
================================================================================

Workflow: Disease Search → Select Patient → Generate Summary (via Ollama Phi)
================================================================================

------------------------------------
STEP 1: SEARCH PATIENTS BY DISEASE/SYMPTOMS
------------------------------------

Enter disease/symptom keyword (e.g., 'diabetes', 'chest pain', 'hypertension'): diabetes

Searching for patients with 'diabetes'...

================================================================================
SEARCH RESULTS FOR: DIABETES
================================================================================

Found 5 patients matching 'diabetes':

1. ID:   1 | Name: Justin Cox        | Age: 83 | Symptoms: swelling in legs, weakness, chills
2. ID:   3 | Name: Susan Hall        | Age: 20 | Symptoms: chest pain, joint pain, shortness of breath
3. ID:   4 | Name: Shirley Richardson | Age: 47 | Symptoms: fatigue, fever, confusion
4. ID:   5 | Name: Sharon Richardson | Age: 48 | Symptoms: dizziness, confusion, fatigue
5. ID:   6 | Name: Donald Parker     | Age: 56 | Symptoms: dizziness, weakness, confusion

------------------------------------
STEP 2: SELECT A PATIENT
------------------------------------

Select patient number (1-5) or 'b' to go back: 1

================================================================================
PATIENT DETAILS (ID: 1)
================================================================================

Patient ID: 1
Name: Justin Cox

Status: No summary yet. Use generate_summary to create one.

------------------------------------
STEP 3: GENERATE SUMMARY USING OLLAMA PHI LLM
------------------------------------

Generating clinical summary using Phi model (this may take 30-60 seconds)...

================================================================================
GENERATED SUMMARY
================================================================================

Generated Summary for Justin Cox (ID: 1):

Patient Justin Cox, an 83-year-old female, presents with multiple concerning symptoms including swelling in the legs, weakness, and chills. With a current blood pressure of 179/103 and blood sugar level of 117 mg/dL, the patient shows signs of hypertension and potential metabolic issues. Given her extensive medical history of obesity and current medications including lisinopril, metformin, and aspirin, comprehensive evaluation and specialist consultation are recommended to address the complex health concerns and optimize treatment outcomes.

------------------------------------
STEP 4: SAVE SUMMARY
------------------------------------

Save this summary to patient_summaries.csv? (y/n): y

================================================================================
✓ Summary for Patient ID 1 (Justin Cox) has been saved.

Summary:
Patient Justin Cox, an 83-year-old female...
================================================================================

✓ Summary saved successfully!

------------------------------------
Would you like to search for another patient? (y/n): n

✓ Thank you for using the Patient Summary System. Goodbye!
```

## Files Explanation

### 1. **mcp_client.py**
- Interactive CLI for the user
- Handles disease keyword input
- Parses search results
- Manages patient selection
- Displays generated summaries
- Confirmation before saving

### 2. **mcp_server.py**
- Implements 4 MCP tools:
  - `search_patients_by_disease`: Vector search via Chroma DB
  - `generate_summary`: LLM call to Ollama Phi
  - `get_patient_summary`: Read from CSV
  - `update_patient_summary`: Write to CSV

### 3. **chroma_setup.py**
- One-time setup script
- Indexes 100 patient profiles in Chroma DB
- Creates semantic embeddings from symptoms + medical history
- Enables vector similarity search

### 4. **chroma_db/** (Directory)
- Persistent Chroma database
- Contains embeddings and metadata for all patients
- Enables fast semantic search

### 5. **patient_summaries.csv**
- Three columns: `patient_id`, `name`, `summary`
- Initially all summaries are empty
- Gets populated as user generates summaries
- Persists between sessions

### 6. **patients_data.csv**
- Read-only source data
- Contains 100 patient health profiles
- Includes: age, gender, symptoms, BP, blood sugar, medications, risk scores
- Used for generating summaries and Chroma indexing

## Performance Notes

- **Phi Model**: 2.7B parameters, ~1.5GB on disk
- **Memory Usage**: ~2-3GB during summary generation
- **CPU Time**: 30-60 seconds per summary (CPU-only)
- **Chroma Search**: <100ms for semantic search
- **Network**: All local (localhost:11434)

## Troubleshooting

### Issue: "Cannot connect to Ollama"

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running:
ollama serve &

# Or restart the service:
sudo systemctl restart ollama
```

### Issue: "No patients found"

- Try different keywords: "hypertension", "chest pain", "diabetes", "fever"
- Search is based on symptom/disease similarity
- More specific terms work better

### Issue: Chroma DB not found

```bash
# Rebuild Chroma DB
python3 chroma_setup.py
```

## Search Examples

Try these keywords for good results:

- `diabetes` - Returns patients with high blood sugar or diabetes
- `hypertension` - Returns patients with high blood pressure
- `chest pain` - Returns patients with cardiac symptoms
- `fever` - Returns patients with infection symptoms
- `weakness` - Returns patients with general weakness
- `obesity` - Returns patients with weight-related issues
- `arthritis` - Returns patients with joint problems

## System Requirements

- Python 3.8+
- 16GB RAM (as you confirmed using Phi CPU-only)
- ~2GB disk space for Phi model
- Internet (for first-time setup only)
- ulimit should be set for Chroma: `ulimit -n 4096`

## What Happens Behind the Scenes?

1. **Search**:
   - User enters "diabetes"
   - mcp_server.py calls Chroma DB's semantic search
   - Chroma returns top 5 patients with similar symptoms/history
   - Results displayed to user

2. **Generation**:
   - User selects patient ID 1
   - mcp_server.py reads patient health data from patients_data.csv
   - Sends formatted prompt to Ollama on localhost:11434
   - Phi model processes the prompt (30-60 sec)
   - Clinical summary returned

3. **Saving**:
   - User confirms save
   - Summary written to patient_summaries.csv
   - Next time you search for same patient, summary is displayed

## Next Steps

- Run `python3 mcp_client.py` to start
- Search for a disease
- Select a patient
- Watch Phi generate a smart clinical summary
- Save the summary to make it persistent

Enjoy the patient summary system! 🏥
