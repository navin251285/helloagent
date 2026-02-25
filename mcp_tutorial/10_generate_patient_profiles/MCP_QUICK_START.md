# MCP Interactive Update System - Quick Start

## What Changed?
You now have a **complete MCP client-server system** where:
- User runs `mcp_client.py` 
- Selects from **top 5 highest-risk patients**
- Updates their summary
- **MCP server** handles the CSV update automatically

## Files

| File | Purpose |
|------|---------|
| `mcp_client.py` | Interactive CLI - shows top 5 patients, gets user input, verifies updates |
| `mcp_server.py` | MCP server - provides 4 tools for patient management |
| `patient_summaries.csv` | CSV database updated by server with clean, non-nested summaries |
| `patients_data.csv` | Read-only source data with risk scores |

## Quick Usage

```bash
python mcp_client.py
```

**Interactive steps:**
1. See top 5 highest-risk patients displayed
2. Enter 1-5 to select a patient
3. View their current summary
4. Choose:
   - Option 1: Enter new custom summary
   - Option 2: Keep current summary  
5. Server updates CSV automatically
6. Client verifies the update

## Example Session

```
================================================================================
TOP 5 HIGH-RISK PATIENTS - SELECT ONE TO UPDATE SUMMARY
================================================================================

  [1] Patient ID: 87  | Jason Nelson         | Risk: 7.8  (HIGH)
  [2] Patient ID: 56  | Stephanie Morgan     | Risk: 7.33 (HIGH)
  [3] Patient ID: 70  | Jerry Young          | Risk: 7.2  (HIGH)
  [4] Patient ID: 31  | Robert Adams         | Risk: 6.8  (MODERATE)
  [5] Patient ID: 37  | Raymond Flores       | Risk: 6.8  (MODERATE)

Enter patient number to update (1-5) or 'q' to quit: 1

✓ Selected: Jason Nelson (ID: 87)

[Current summary displayed...]

What would you like to do?
1. Enter custom summary
2. Accept current summary
Enter choice (1 or 2): 2

✓ PATIENT SUMMARY UPDATE COMPLETED SUCCESSFULLY
```

## Key Features

✓ **Top 5 Patients by Risk Score** - Displays highest-risk patients first
✓ **Interactive Selection** - User chooses which patient to update
✓ **Two Update Options**:
  - Custom summary (write your own)
  - Accept current (no change)
✓ **MCP Protocol** - Secure, structured communication between client-server
✓ **Instant Verification** - Confirms update was successful
✓ **Clean CSV Storage** - Summaries stored without formatting artifacts

## MCP Server Tools

The MCP server provides these tools accessible via `mcp_client.py`:

1. **list_patients** - Lists all 100 patients
2. **get_patient_summary** - Fetches a patient's current summary
3. **update_patient_summary** - Updates patient summary in CSV
4. **search_patients** - Searches by keyword

## Data Flow

```
User Input
    ↓
mcp_client.py displays top 5
    ↓
User selects patient
    ↓
mcp_client calls MCP server tools via stdio
    ↓
mcp_server.py executes tools
    ↓
Updates patient_summaries.csv
    ↓
Server returns success response
    ↓
mcp_client verifies and displays result
```

## CSV Format

Before update:
```csv
31,Robert Adams,"Robert Adams is a 74-year-old Male patient..."
```

After update (clean, no artifacts):
```csv
31,Robert Adams,"Robert Adams is a 74-year-old Male patient..."
```

## What Happens Under the Hood

1. **Client** reads patients_data.csv and finds top 5 by risk_score
2. **Client** displays them in a formatted table
3. **User** selects one
4. **Client** connects to MCP server over stdio
5. **Server** fetches current summary from patient_summaries.csv
6. **Client** shows it to user
7. **User** chooses update option
8. **Client** sends update command to server
9. **Server** updates patient_summaries.csv
10. **Server** sends success response
11. **Client** verifies by re-fetching summary
12. **Client** displays final result

## Error Handling

- **"Patient not found"** - ID doesn't exist (1-100)
- **"Failed to update"** - CSV permission or write error  
- **"Update cancelled"** - User typed 'CANCEL'
- **Invalid choice** - Use 1-5 for patient selection or 'q' to quit

## Requirements

```bash
pip install mcp sentence-transformers chromadb
```

## Configuration

All data files are in `10_generate_patient_profiles/`:
- `patients_data.csv` - 100 patient profiles with risk scores
- `patient_summaries.csv` - Patient summaries (updated by server)
- `mcp_client.py` - Client application
- `mcp_server.py` - Server application

## Next Steps

1. Run `python mcp_client.py` to start
2. Select a patient from top 5
3. Update their summary
4. Repeat as needed
5. All updates are persistent in patient_summaries.csv

## Integration Notes

The MCP server can be integrated with:
- AI agents for automated analysis
- Web dashboards for remote management  
- Healthcare systems for data sync
- Batch processing for bulk operations

See `MCP_INTERACTIVE_GUIDE.md` for detailed documentation.
