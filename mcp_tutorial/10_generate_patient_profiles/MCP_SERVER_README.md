# Patient Summaries MCP Server

This directory contains an MCP (Model Context Protocol) server implementation for managing patient summaries. The server provides tools to read, update, and search patient summaries stored in a CSV file.

## Overview

The system consists of:

1. **generate_summaries.py** - Generates patient summaries from the main patient data CSV
2. **patient_summaries.csv** - CSV file containing patient ID, name, and summary
3. **mcp_server.py** - MCP server that provides tools to manage the summaries
4. **mcp_client.py** - Example client demonstrating how to use the MCP server

## Files

### patient_summaries.csv

Contains three columns:
- `patient_id`: Unique patient identifier (1-100)
- `name`: Patient name
- `summary`: Generated summary of patient's medical status and history

### MCP Server Tools

The server provides 4 tools:

1. **list_patients** - List all patients with their IDs and names
2. **get_patient_summary** - Get a specific patient's summary by ID
3. **update_patient_summary** - Update a patient's summary
4. **search_patients** - Search for patients by keyword in their summary

## Installation

```bash
# Install required package
pip install mcp
```

## Usage

### Step 1: Generate Patient Summaries

First, generate the patient summaries CSV from the main patient data:

```bash
python generate_summaries.py
```

This creates `patient_summaries.csv` with 100 patient summaries.

### Step 2: Run the MCP Server

The server runs in stdio mode and communicates via stdin/stdout:

```bash
python mcp_server.py
```

### Step 3: Use the MCP Client

Run the example client to interact with the server:

```bash
python mcp_client.py
```

The client demonstrates:
- Listing all patients
- Getting a specific patient's summary
- Updating a patient's summary
- Verifying the update
- Searching patients by keyword

## MCP Server API

### Tool: list_patients

**Description:** List all patients with their IDs and names

**Parameters:** None

**Returns:** List of all patients with ID and name

**Example:**
```python
result = await session.call_tool("list_patients", {})
```

### Tool: get_patient_summary

**Description:** Get a patient's summary by their ID

**Parameters:**
- `patient_id` (string, required): The patient ID (1-100)

**Returns:** Patient ID, name, and summary

**Example:**
```python
result = await session.call_tool("get_patient_summary", {"patient_id": "1"})
```

### Tool: update_patient_summary

**Description:** Update a patient's summary

**Parameters:**
- `patient_id` (string, required): The patient ID (1-100)
- `new_summary` (string, required): The new summary text for the patient

**Returns:** Success message with updated summary

**Example:**
```python
result = await session.call_tool(
    "update_patient_summary",
    {
        "patient_id": "1",
        "new_summary": "Updated summary text here..."
    }
)
```

### Tool: search_patients

**Description:** Search for patients by keyword in their summary

**Parameters:**
- `keyword` (string, required): Keyword to search for in patient summaries

**Returns:** List of matching patients (max 10 results)

**Example:**
```python
result = await session.call_tool("search_patients", {"keyword": "diabetes"})
```

## Integration with Your Application

To integrate the MCP server into your application:

```python
import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def use_patient_summaries():
    # Create server parameters
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )
    
    # Connect to server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()
            
            # Use the tools
            result = await session.call_tool("list_patients", {})
            print(result.content[0].text)
            
            # Get specific patient
            patient = await session.call_tool(
                "get_patient_summary", 
                {"patient_id": "25"}
            )
            print(patient.content[0].text)
            
            # Update summary
            update_result = await session.call_tool(
                "update_patient_summary",
                {
                    "patient_id": "25",
                    "new_summary": "Your new summary here..."
                }
            )
            print(update_result.content[0].text)

# Run it
asyncio.run(use_patient_summaries())
```

## Summary Generation

The `generate_summaries.py` script creates summaries that include:

- Patient demographics (age, gender)
- Medical history
- Risk assessment level
- Current symptoms
- Vital signs status (blood pressure, blood sugar)
- Current medications
- Visit history count
- Condition trends (improving, worsening, stable)
- Clinical recommendations

### Example Summary:

```
Justin Cox is an 83-year-old Female patient with obesity, 
currently at moderate risk (5.6). Presenting with leg swelling, 
weakness, and chills. Blood pressure is elevated at 179/103. 
Currently on lisinopril, metformin, and aspirin. Condition has 
improved since last visit. Requires close monitoring and 
medication adherence. Follow-up recommended in 2 weeks.
```

## Data Persistence

All updates made through the MCP server are persisted to the `patient_summaries.csv` file. The CSV is:
- Read on every tool call to ensure fresh data
- Written immediately after updates
- Safe for concurrent reads (but not concurrent writes)

## Use Cases

1. **Medical Record Management** - Update and maintain patient summaries
2. **Clinical Decision Support** - Search for patients with specific conditions
3. **Patient Monitoring** - Track and update patient status
4. **Research** - Query patient cohorts by keywords
5. **Integration** - Connect to EMR/EHR systems via MCP

## Error Handling

The server handles:
- Missing patient IDs (returns error message)
- Invalid tool names (raises ValueError)
- Missing CSV file (returns empty list for list_patients)
- Invalid parameters (raises ValueError with description)

## Testing

Run the client to test all functionality:

```bash
python mcp_client.py
```

Expected output shows:
- ✓ 4 tools available
- ✓ 100 patients listed
- ✓ Patient summary retrieved
- ✓ Summary updated successfully
- ✓ Updated summary verified
- ✓ Search results returned

## Extending the Server

To add new tools to the server:

1. Add tool definition in `handle_list_tools()`
2. Add tool implementation in `handle_call_tool()`
3. Update this README with the new tool documentation

Example:

```python
@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        # ... existing tools ...
        types.Tool(
            name="your_new_tool",
            description="What your tool does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param_name": {
                        "type": "string",
                        "description": "Parameter description"
                    }
                },
                "required": ["param_name"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict | None):
    if name == "your_new_tool":
        # Your implementation here
        return [types.TextContent(type="text", text="Result")]
    # ... existing tool implementations ...
```

## Related Files

- [patients_data.csv](patients_data.csv) - Source patient data with full history
- [patients_detailed.csv](patients_detailed.csv) - Detailed visit records
- [query_patients.py](query_patients.py) - Semantic search interface for patient profiles
- [README.md](README.md) - Main project documentation

## License

This is a demonstration project for educational purposes.
