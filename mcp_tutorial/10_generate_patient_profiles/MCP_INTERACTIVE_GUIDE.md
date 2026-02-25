# MCP Client-Server - Patient Summary Update System

## Overview
This is an **interactive MCP (Model Context Protocol) client-server system** that allows users to:
1. **View the top 5 highest-risk patients**
2. **Select one patient** to update their summary
3. **MCP server updates the selected patient's summary** in `patient_summaries.csv`

The workflow uses MCP's bidirectional communication protocol for secure and structured data updates.

## How It Works

### 1. MCP Client (mcp_client.py)
The client runs locally and:
- Reads `patients_data.csv` to find the top 5 patients by risk score
- Displays them in a numbered list with key information (risk score, age, symptoms, vitals)
- Prompts user to select one patient (1-5)
- Connects to the MCP server to fetch/update the selected patient's summary
- Provides two update options:
  - **Option 1**: Enter a custom summary
  - **Option 2**: Accept the current summary (no change)
- Verifies the update was successful

### 2. MCP Server (mcp_server.py)
The server provides 4 tools accessed via MCP protocol:
- **list_patients**: List all 100 patients with IDs and names
- **get_patient_summary**: Fetch a patient's current summary
- **update_patient_summary**: Update a patient's summary in CSV
- **search_patients**: Search patients by keyword

### 3. Data Flow
```
User Input
    ↓
mcp_client.py (displays top 5)
    ↓
User selects patient
    ↓
mcp_client calls MCP server tools
    ↓
mcp_server.py executes tools
    ↓
Updates patient_summaries.csv
    ↓
Returns success response
    ↓
mcp_client displays verification
```

## Getting Started

### Prerequisites
```bash
pip install mcp sentence-transformers chromadb
```

### Run the Interactive System
```bash
python mcp_client.py
```

## Interactive Workflow

### Step 1: View Top 5 Patients
When you run the client, you'll see:
```
================================================================================
TOP 5 HIGH-RISK PATIENTS - SELECT ONE TO UPDATE SUMMARY
================================================================================

  [1] Patient ID: 87  | Jason Nelson         | Risk: 7.8  (HIGH    ) | Age: 50 | Sugar: 287
  [2] Patient ID: 56  | Stephanie Morgan     | Risk: 7.33 (HIGH    ) | Age: 74 | Sugar: 271
  [3] Patient ID: 70  | Jerry Young          | Risk: 7.2  (HIGH    ) | Age: 67 | Sugar: 206
  [4] Patient ID: 31  | Robert Adams         | Risk: 6.8  (MODERATE) | Age: 74 | Sugar: 294
  [5] Patient ID: 37  | Raymond Flores       | Risk: 6.8  (MODERATE) | Age: 72 | Sugar: 258
```

### Step 2: Select a Patient
```
Enter patient number to update (1-5) or 'q' to quit: 1
```
This selects Jason Nelson (ID: 87)

### Step 3: View Current Summary
The client fetches and displays the patient's current summary:
```
Current Summary:
────────────────────────────────────────────────────────────────────
Jason Nelson is a 50-year-old Female patient. with a history of 
hypertension, diabetes. currently at high risk (score: 7.8). 
presenting with shortness of breath, confusion...
```

### Step 4: Choose Update Method
```
What would you like to do?
1. Enter custom summary
2. Accept current summary
Enter choice (1 or 2): 1
```

**If you choose Option 1 (Custom Summary):**
```
Enter new summary for this patient:
(Press Enter twice on an empty line when done, or type 'CANCEL' to cancel)

[Type your custom summary here]

[Press Enter twice when done]
```

**If you choose Option 2 (Accept Current):**
- The current summary is kept unchanged

### Step 5: MCP Server Updates CSV
The MCP server:
1. Validates the patient exists
2. Updates the `patient_summaries.csv` file
3. Returns a success message with the new summary

### Step 6: Verification
The client verifies the update by fetching the updated summary:
```
✓ PATIENT SUMMARY UPDATE COMPLETED SUCCESSFULLY
```

## File Structure

```
mcp_client.py              # Interactive client for user (displays top 5 & handles input)
mcp_server.py             # MCP server with 4 patient management tools
patient_summaries.csv     # CSV file with patient summaries (updated by server)
patients_data.csv         # Read-only: source data with risk scores
```

## CSV File Format

**patient_summaries.csv:**
```csv
patient_id,name,summary
1,Justin Cox,"Justin Cox is an 83-year-old Female patient with obesity..."
2,Heather Baker,"Heather Baker is a 67-year-old Male patient..."
...
```

## Risk Score Levels

- **HIGH**: Score ≥ 7.0 (Red alert - immediate attention needed)
- **MODERATE**: Score ≥ 4.0 and < 7.0 (Yellow alert - regular monitoring)
- **LOW**: Score < 4.0 (Green - routine monitoring)

## Features

✓ **Interactive Selection**: Choose from top 5 high-risk patients
✓ **Real-time Verification**: Confirms updates immediately
✓ **Flexible Updates**: Custom or current summary retention
✓ **MCP Protocol**: Secure, structured communication
✓ **CSV Persistence**: Updates saved to patient_summaries.csv
✓ **Formatted Display**: Clear, readable patient information
✓ **Cancel Support**: Type 'q' or 'CANCEL' at any point

## Example: Complete Update Workflow

```bash
$ python mcp_client.py

# Display shows top 5 patients
# User enters: 2
✓ Selected: Stephanie Morgan (ID: 56)

# Current summary displayed
# User enters: 1 (choose custom summary)

# User types new summary:
Stephanie Morgan is a 74-year-old patient with severe diabetes.
Critical intervention needed immediately. Blood sugar dangerously high at 271 mg/dL.
Requires hospitalization and intensive insulin management.

# [User presses Enter twice]

# Server updates CSV
# Client shows success:
✓ PATIENT SUMMARY UPDATE COMPLETED SUCCESSFULLY
```

## Troubleshooting

**"Patient not found"**
- Ensure patient ID is valid (1-100)
- Check that patients_data.csv exists

**"Failed to update"**
- Verify patient_summaries.csv has write permissions
- Check disk space availability
- Ensure CSV format is correct

**MCP Connection Error**
- Verify mcp_server.py is executable
- Check Python MCP library is installed: `pip install mcp`
- Ensure both files are in same directory

## Integration with Other Systems

The MCP server can be integrated with:
- AI agents for automated patient analysis
- Web applications for remote patient management
- Healthcare platforms for data synchronization
- Batch processing systems for bulk updates

Use the MCP tools directly in your application:
```python
result = await session.call_tool("update_patient_summary", 
    {"patient_id": "87", "new_summary": "Updated summary text"})
```

## Next Steps

After updating summaries, you can:
1. Run searches: `search_patients` tool to find patients by keyword
2. Review all patients: `list_patients` tool for full inventory
3. Export updates: Copy patient_summaries.csv to other systems
4. Analyze trends: Track which patients have been updated
