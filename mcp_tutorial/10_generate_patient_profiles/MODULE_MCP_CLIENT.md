# MCP Client Module - `mcp_client.py`

## 📌 Purpose
Interactive CLI application that allows users to:
1. Search for patients by disease/symptoms
2. Select a patient from results
3. Trigger LLM-based summary generation
4. Save summaries to persistent CSV storage

## 🎯 User Workflow

```
START
  │
  ├─→ Display welcome & instructions
  │
  ├─→ LOOP until user quits:
  │
  │   1️⃣ SEARCH
  │      "Enter disease keyword: > diabetes"
  │      └─→ MCP: search_patients_by_disease("diabetes")
  │          × Chroma DB returns top 5
  │          × Display: ID, Name, Age, Symptoms
  │
  │   2️⃣ SELECT
  │      "Select patient (1-5): > 3"
  │      └─→ Extract patient ID from selection
  │          (Validation: 1-5 range)
  │
  │   3️⃣ SHOW DETAILS
  │      MCP: get_patient_summary(ID=55)
  │      × Display full patient info
  │      × Show current summary status
  │
  │   4️⃣ GENERATE
  │      "Generating summary... (30-60 sec)"
  │      └─→ MCP: generate_summary(ID=55)
  │          × Server reads patient_data.csv
  │          × Creates LLM prompt
  │          × Sends to Ollama phi model
  │          × Returns generated text
  │
  │   5️⃣ EXTRACT & CONFIRM
  │      Parse response text
  │      "Save to CSV? (y/n): > y"
  │      └─→ If yes: extract summary
  │             clean whitespace
  │             validate not empty
  │
  │   6️⃣ UPDATE & SAVE
  │      MCP: update_patient_summary(ID=55, text)
  │      × Server updates patient_summaries.csv
  │      × Confirmation message
  │
  │   7️⃣ CONTINUE?
  │      "Continue? (y/n): > y"
  │      └─→ Loop back to step 1
  │          or exit if "n"
  │
  ├─→ User chooses to exit
  │
  └─→ END

Total time per workflow: ~60 seconds (mostly LLM generation)
```

---

## 🔧 Core Functions

### 1. `search_patients_by_disease(session, disease_keyword)`

**Purpose:** Query MCP server for similar patients

```python
async def search_patients_by_disease(session, disease_keyword):
    """Call MCP server to search patients by disease"""
    result = await session.call_tool("search_patients_by_disease", {
        "disease_keyword": disease_keyword
    })
    return result.content[0].text
```

**Flow:**
```
User input: "diabetes"
     │
     ▼
Call MCP server tool
     │
     ▼
Server queries Chroma DB
     │
     ├─→ Query embedding: "diabetes" → [0.12, -0.45, ...]
     │
     ├─→ Cosine similarity search top 5
     │
     └─→ Return metadata for patients: 11, 45, 55, 13, 50
     │
     ▼
Return formatted text to client:
"Found 5 patients matching 'diabetes':

1. ID: 11  | Name: Jerry Rivera      | Age: 59 | Symptoms: confusion, elevated BP, high sugar
2. ID: 45  | Name: Janet Torres      | Age: 70 | Symptoms: weakness, elevated BP, high sugar
3. ID: 55  | Name: John Johnson      | Age: 77 | Symptoms: shortness of breath, blurred vision...
4. ID: 13  | Name: Donald Evans      | Age: 65 | Symptoms: confusion, elevated BP...
5. ID: 50  | Name: Gregory Bailey    | Age: 68 | Symptoms: weakness, elevated BP..."
```

**Performance:** ~50ms (Chroma DB query + network)

---

### 2. `get_patient_summary(session, patient_id)`

**Purpose:** Display current patient information

```python
async def get_patient_summary(session, patient_id):
    """Call MCP server to get patient summary"""
    result = await session.call_tool("get_patient_summary", {
        "patient_id": str(patient_id)
    })
    return result.content[0].text
```

**Output example:**
```
Patient ID: 55
Name: John Johnson

Status: No summary yet. Use generate_summary to create one.
```

**Or if summary exists:**
```
Patient ID: 55
Name: John Johnson

Summary:
Patient John Johnson, a 77-year-old male, presents with significant risk factors 
including shortness of breath and blurred vision. Current blood pressure is elevated 
at a concerning level, with blood sugar at critical levels. Immediate intervention 
and specialist consultation are strongly recommended.
```

**Performance:** ~20ms (CSV read)

---

### 3. `generate_summary(session, patient_id)`

**Purpose:** Trigger Ollama-based summary generation

```python
async def generate_summary(session, patient_id):
    """Call MCP server to generate summary using Ollama"""
    result = await session.call_tool("generate_summary", {
        "patient_id": str(patient_id)
    })
    return result.content[0].text
```

**Flow:**
```
Input: patient_id=55
     │
     ▼
Server reads patient_data.csv
Patient 55 (John Johnson, 77M):
- Symptoms: shortness of breath, blurred vision, weakness
- BP: 175/105
- Sugar: 245 mg/dL
- Medications: Metoprolol, Atorvastatin
- History: Hypertension, High Cholesterol
     │
     ▼
Create LLM prompt:
"Generate a concise clinical summary for:
Patient Name: John Johnson
Age: 77
Gender: Male
Current Symptoms: shortness of breath, blurred vision, weakness
Blood Pressure: 175/105 mmHg
Blood Sugar: 245 mg/dL
Medical History: Hypertension, High Cholesterol
Current Medications: Metoprolol, Atorvastatin
Risk Score: 9.1

Provide a brief clinical assessment (2-3 sentences)."
     │
     ▼
HTTP POST to Ollama (localhost:11434)
{
  "model": "phi",
  "prompt": "...",
  "stream": false,
  "temperature": 0.7
}
     │
     ▼
Wait 30-60 seconds for Phi model inference
     │
     ▼
Return response:
"Based on the patient's medical history, current symptoms, and test results, 
it is likely that John Johnson has hypertension and cardiovascular disease, 
which may be contributing to his shortness of breath, blurred vision, and weakness. 
Aspirin and medications like Metoprolol and Atorvastatin are appropriate for managing 
these symptoms, but further testing and consultation with a cardiologist will be 
necessary to determine the appropriate course of treatment."
     │
     ▼
Client displays to user
```

**Format of returned text:**
```
Generated Summary for John Johnson (ID: 55):

Based on the patient's medical history, current symptoms, and test results, it is 
likely that John Johnson has hypertension and cardiovascular disease...
```

**Performance:** 30-60 seconds (LLM computation)
**Note:** User sees progress message "<waiting for Phi model> (this may take 30-60 seconds)"

---

### 4. `update_summary(session, patient_id, summary)`

**Purpose:** Save generated summary to persistent storage

```python
async def update_summary(session, patient_id, summary):
    """Call MCP server to update and save summary"""
    print(f"\n[CLIENT] Calling update_summary with:")
    print(f"[CLIENT]   Patient ID: {patient_id}")
    print(f"[CLIENT]   Summary length: {len(summary)} chars")
    
    result = await session.call_tool("update_patient_summary", {
        "patient_id": str(patient_id),
        "summary": summary
    })
    
    output = result.content[0].text
    print(f"\n[CLIENT] Server response:")
    print(f"{output}")
    return output
```

**Flow:**
```
Input: patient_id=55, summary="Based on the patient's medical..."
     │
     ▼
Server:
1. Read patient_summaries.csv (100 rows)
2. Find patient 55 (Janet Torres)
3. Update summaries[54]['summary'] = new_summary
4. Write back to CSV (all 100 rows)
5. Return success/failure
     │
     ▼
CSV file updated:
Before: 55,John Johnson,
After:  55,John Johnson,"Based on the patient's medical history..."
     │
     ▼
Display confirmation to user:
"✓ Summary for Patient ID 55 (John Johnson) has been saved.

Summary (234 characters):
Based on the patient's medical history, current symptoms..."
```

**Performance:** ~50ms (CSV I/O)

---

## 📖 Input Parsing & Extraction

### Parsing Search Results

**Raw MCP Response:**
```
Found 5 patients matching 'diabetes':

1. ID: 11  | Name: Jerry Rivera      | Age: 59 | Symptoms: confusion, elevated BP
2. ID: 45  | Name: Janet Torres      | Age: 70 | Symptoms: weakness, elevated BP
3. ID: 55  | Name: John Johnson      | Age: 77 | Symptoms: shortness of breath
4. ID: 13  | Name: Donald Evans      | Age: 65 | Symptoms: confusion, elevated BP
5. ID: 50  | Name: Gregory Bailey    | Age: 68 | Symptoms: weakness, elevated BP
```

**Parsing Code:**
```python
search_results = await search_patients_by_disease(session, disease_keyword)

print(search_results)  # Display to user

# Parse results to extract patient IDs
lines = search_results.split('\n')
patients = []
for line in lines:
    if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
        # Extract patient ID from line
        # Format: "1. ID: 11  | Name: Jerry Rivera | ..."
        parts = line.split('|')
        if len(parts) >= 1:
            # Extract ID from "1. ID: 11  "
            id_part = parts[0].split(':')[1].strip()
            patients.append(id_part)

# Result: patients = ['11', '45', '55', '13', '50']
```

**User Selection:**
```
Select patient number (1-5): > 3
              ↓
selected_patient_id = patients[3 - 1] = patients[2] = '55'
```

---

### Extracting Generated Summary

**Raw LLM Response:**
```
Generated Summary for John Johnson (ID: 55):

Based on the patient's medical history, current symptoms, and test results, it is very likely 
that John Johnson has hypertension and cardiovascular disease, which may be contributing to his 
shortness of breath, blurred vision, and weakness. Further testing and consultation with a cardiologist 
will be necessary for proper diagnosis and treatment optimization.
```

**Extraction Code:**
```python
generated_summary = "Generated Summary for John Johnson (ID: 55):\n\nBased on..."

# Step 1: Split into lines
summary_lines = generated_summary.split('\n')

# Step 2: Find where actual summary starts
summary_start = None
for i, line in enumerate(summary_lines):
    if 'Generated Summary for' in line:
        summary_start = i + 2  # Skip title and blank line
        break

# Step 3: Extract summary text
if summary_start and summary_start < len(summary_lines):
    summary_text = '\n'.join(summary_lines[summary_start:]).strip()
else:
    summary_text = generated_summary.strip()

# Step 4: Clean up multiple blank lines
summary_text = '\n'.join([ln.strip() for ln in summary_text.split('\n') if ln.strip()])

# Result:
# "Based on the patient's medical history, current symptoms, and test results, 
#  it is very likely that John Johnson has hypertension and cardiovascular disease, 
#  which may be contributing to his shortness of breath, blurred vision, and weakness. 
#  Further testing and consultation with a cardiologist will be necessary..."
```

**Validation:**
```python
if not summary_text or len(summary_text) == 0:
    print("❌ ERROR: Cannot save empty summary. Extraction failed.")
    continue  # Skip to next search
else:
    print(f"✅ Extracted {len(summary_text)} characters")
    # Proceed to save
```

---

## 🔄 Async/Await Pattern

**Why async?**
- Non-blocking I/O (network, file operations)
- Can handle long-running operations (30-60 sec summary generation)
- Responsive UI (no freezing)

**Example Pattern:**
```python
async def main():
    # Create MCP server subprocess
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )
    
    # Connect to server via stdio
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize connection
            await session.initialize()
            
            # Now we can call tools
            result = await session.call_tool("search_patients_by_disease", {
                "disease_keyword": "diabetes"
            })
            
            # Process result (non-blocking)
            print(result.content[0].text)

# Run async main
asyncio.run(main())
```

---

## 🎨 User Interface

### Welcome Screen
```
====================================================================================================
🏥 PATIENT SUMMARY GENERATION SYSTEM
====================================================================================================

Workflow: Disease Search → Select Patient → Generate Summary (via Ollama Phi)
====================================================================================================
```

### Search Results Display
```
====================================================================================================
SEARCH RESULTS FOR: DIABETES
====================================================================================================
Found 5 patients matching 'diabetes':

1. ID: 11  | Name: Jerry Rivera      | Age: 59 | Symptoms: confusion, elevated BP, high sugar
2. ID: 45  | Name: Janet Torres      | Age: 70 | Symptoms: weakness, elevated BP, high sugar
3. ID: 55  | Name: John Johnson      | Age: 77 | Symptoms: shortness of breath, blurred vision
4. ID: 13  | Name: Donald Evans      | Age: 65 | Symptoms: confusion, elevated BP, high sugar
5. ID: 50  | Name: Gregory Bailey    | Age: 68 | Symptoms: weakness, elevated BP, high sugar
```

### Patient Details
```
====================================================================================================
PATIENT DETAILS (ID: 55)
====================================================================================================
Patient ID: 55
Name: John Johnson
Age: 77
Gender: Male
Current Symptoms: shortness of breath, blurred vision, weakness
Blood Pressure: 175/105 mmHg
Blood Sugar: 245 mg/dL
Current Medications: Metoprolol, Atorvastatin
Medical History: Hypertension, High Cholesterol
Risk Score: 9.1/10

Status: No summary yet. Use generate_summary to create one.
```

### Summary Generation Progress
```
----------------------------------------------------------------------------------------------------
STEP 3: GENERATE SUMMARY USING OLLAMA PHI LLM
----------------------------------------------------------------------------------------------------

Generating clinical summary using Phi model (this may take 30-60 seconds)...
```

### Confirmation & Save
```
----------------------------------------------------------------------------------------------------
STEP 4: SAVE SUMMARY
----------------------------------------------------------------------------------------------------

Save this summary to patient_summaries.csv? (y/n): y

📝 Extracted summary (347 characters):
   Based on the patient's medical history of hypertension...
   [DEBUG] Full extracted text length: 347
   [DEBUG] First 100 chars: Based on the patient's medical history, current symptoms, and test results...

[CLIENT] Server response:
✓ Summary for Patient ID 55 (John Johnson) has been saved.

Summary (347 characters):
Based on the patient's medical history...

====================================================================================================
✓ Summary saved successfully!
====================================================================================================

Would you like to search for another patient? (y/n): y
```

---

## 🚀 Running the Client

```bash
cd /path/to/10_generate_patient_profiles

# Prerequisite: Ollama server running in another terminal
# $ ollama serve

# Start client
python3 mcp_client.py

# Interactive session begins
# User can search, select, generate, and save summaries
# Ctrl+C to exit
```

---

## 🔌 MCP Integration

**MCP Client Features:**
- Automatic subprocess launching of server
- Async stdio communication
- Tool-based API
- Error handling and connection management

**Under the hood:**
```python
async with stdio_client(server_params) as (read, write):
    # read: AsyncBytesIO for reading server responses
    # write: AsyncBytesIO for sending requests
    
    async with ClientSession(read, write) as session:
        # session: Handles all MCP JSON-RPC communication
        # Converts tool calls to JSON, parses responses
        
        result = await session.call_tool("search_patients_by_disease", {
            "disease_keyword": disease_keyword
        })
        # result: ToolResult with content array
```

---

## 🧪 Testing the Client

**Test 1: Search Only**
```bash
python3 mcp_client.py
> diabetes
# View search results
> b  (back)
> quit
```

**Test 2: Full Workflow**
```bash
python3 mcp_client.py
> diabetes
> 1
# View patient details
# Wait 30-60 sec for summary
> y  (save)
> n  (don't continue)
```

**Test 3: Multiple Searches**
```bash
python3 mcp_client.py
> diabetes
> 1
> y
> y  (continue)
> hypertension
> 2
> y
> n
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "Cannot connect to Ollama" | Start `ollama serve` in another terminal |
| "Summary extraction failed" | Generated text format changed, check parsing |
| "Permission denied" on CSV | Run `chmod 666 patient_summaries.csv` |
| Slow generation (>60 sec) | CPU bottleneck, normal for Phi on CPU |
| Empty search results | Try different keywords |

---

## 📝 Code Quality

- **Error handling:** Try/except on network calls
- **User input validation:** Range checking (1-5 for patient selection)
- **Async pattern:** Properly awaits all async operations
- **Logging:** Debug output for extraction and MCP calls
- **Type hints:** Async functions properly typed

---

**Last Updated:** February 25, 2026
