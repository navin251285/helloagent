#!/usr/bin/env python3
"""
MCP Server for Patient Summaries with Chroma DB and Ollama
- Search patients by disease/symptoms using Chroma DB
- Generate summaries using Ollama (Phi model)
- Update and persist summaries to CSV
"""

import asyncio
import csv
import json
import sys
import requests
from typing import Any
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp import types

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

# Configuration
CSV_FILE = "patient_summaries.csv"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi"

# Initialize the MCP server
app = Server("patient-summaries-server")

# Chroma client for search
chroma_client = None
if CHROMA_AVAILABLE:
    try:
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
    except:
        chroma_client = None


def read_summaries():
    """Read all patient summaries from CSV"""
    summaries = []
    try:
        with open(CSV_FILE, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                summaries.append(row)
        print(f"[READ_SUMMARIES] Successfully read {len(summaries)} records from {CSV_FILE}", file=sys.stderr)
    except FileNotFoundError:
        print(f"[READ_SUMMARIES] File not found: {CSV_FILE}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"[READ_SUMMARIES] ERROR reading {CSV_FILE}: {e}", file=sys.stderr)
    return summaries


def write_summaries(summaries):
    """Write all patient data to CSV"""
    try:
        with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['patient_id', 'name', 'summary']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for summary in summaries:
                writer.writerow({
                    'patient_id': summary['patient_id'], 
                    'name': summary['name'],
                    'summary': summary.get('summary', '')
                })
        print(f"[WRITE_SUMMARIES] Successfully wrote {len(summaries)} records to {CSV_FILE}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"[WRITE_SUMMARIES] ERROR writing to {CSV_FILE}: {e}", file=sys.stderr)
        return False


def get_patient_by_id(patient_id):
    """Get a specific patient's summary by ID"""
    summaries = read_summaries()
    for summary in summaries:
        if summary['patient_id'] == str(patient_id):
            return summary
    return None


def read_patient_health_data(patient_id):
    """Read patient health data from patients_data.csv"""
    try:
        with open('patients_data.csv', 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['patient_id'] == str(patient_id):
                    return row
    except FileNotFoundError:
        return None
    return None


def search_patients_by_disease(disease_keyword, top_k=5):
    """Search for patients by disease/symptoms using Chroma DB"""
    if not chroma_client:
        return []
    
    try:
        collection = chroma_client.get_collection(name="patients")
        # Query with top_k * 2 to ensure we get diverse results
        results = collection.query(
            query_texts=[disease_keyword],
            n_results=top_k * 2
        )
        
        patients = []
        # results['metadatas'] returns [[{...}, {...}, ...]]  - list of lists
        # We want the first list's items (top_k results)
        if results and results['metadatas'] and len(results['metadatas']) > 0:
            for metadata in results['metadatas'][0][:top_k]:  # Take top_k from first list
                if metadata:
                    patients.append(metadata)
        
        return patients
    except Exception as e:
        print(f"Chroma search error: {e}", file=__import__('sys').stderr)
        return []


def generate_summary_with_ollama(patient_data):
    """Generate a clinical summary using Ollama (Phi model)"""
    if not patient_data:
        return "Error: No patient data provided"
    
    # Build prompt for the LLM
    prompt = f"""Generate a concise clinical summary for the following patient:

Patient Name: {patient_data.get('name', 'Unknown')}
Age: {patient_data.get('age', 'N/A')}
Gender: {patient_data.get('gender', 'N/A')}
Current Symptoms: {patient_data.get('current_symptoms', 'None')}
Blood Pressure: {patient_data.get('current_bp', 'N/A')}
Blood Sugar: {patient_data.get('current_sugar', 'N/A')} mg/dL
Medical History: {patient_data.get('medical_history', 'None')}
Current Medications: {patient_data.get('current_medications', 'None')}
Risk Score: {patient_data.get('risk_score', 'N/A')}

Provide a brief clinical assessment (2-3 sentences) highlighting key health concerns and recommendations."""

    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'Summary generation failed').strip()
        else:
            return f"Ollama API error: {response.status_code}"
    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Make sure Ollama is running on port 11434"
    except Exception as e:
        return f"Error generating summary: {str(e)}"


def update_patient_summary(patient_id, new_summary):
    """Update a patient's summary - optimized for single read/write"""
    print(f"[UPDATE_PATIENT_SUMMARY] Called with patient_id={patient_id}, summary_length={len(new_summary)}", file=sys.stderr)
    try:
        # Read once
        summaries = read_summaries()
        
        # Find and update
        updated = False
        for i, summary in enumerate(summaries):
            if summary['patient_id'] == str(patient_id):
                summaries[i]['summary'] = new_summary
                updated = True
                print(f"[UPDATE_PATIENT_SUMMARY] Found patient {patient_id} at index {i}, updating", file=sys.stderr)
                break
        
        if not updated:
            print(f"[UPDATE_PATIENT_SUMMARY] Patient {patient_id} NOT found in records!", file=sys.stderr)
            return False
        
        # Write once
        print(f"[UPDATE_PATIENT_SUMMARY] Writing to CSV...", file=sys.stderr)
        write_result = write_summaries(summaries)
        
        if write_result:
            print(f"[UPDATE_PATIENT_SUMMARY] ✅ Write successful", file=sys.stderr)
            return True
        else:
            print(f"[UPDATE_PATIENT_SUMMARY] ❌ Write failed", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"[UPDATE_PATIENT_SUMMARY] Exception: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return False


@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools"""
    return [
        types.Tool(
            name="search_patients_by_disease",
            description="Search for patients by disease/symptoms using vector similarity (returns top 5 matching patients)",
            inputSchema={
                "type": "object",
                "properties": {
                    "disease_keyword": {
                        "type": "string",
                        "description": "Disease name or symptoms to search for (e.g., 'diabetes', 'chest pain', 'hypertension')"
                    }
                },
                "required": ["disease_keyword"]
            }
        ),
        types.Tool(
            name="get_patient_summary",
            description="Get a patient's current summary by their ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "The patient ID (1-100)"
                    }
                },
                "required": ["patient_id"]
            }
        ),
        types.Tool(
            name="generate_summary",
            description="Generate a clinical summary for a patient using Ollama (Phi model) based on their health data",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "The patient ID (1-100)"
                    }
                },
                "required": ["patient_id"]
            }
        ),
        types.Tool(
            name="update_patient_summary",
            description="Update and save a patient's summary to the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "patient_id": {
                        "type": "string",
                        "description": "The patient ID (1-100)"
                    },
                    "summary": {
                        "type": "string",
                        "description": "The summary text to save"
                    }
                },
                "required": ["patient_id", "summary"]
            }
        )
    ]


@app.call_tool()
async def handle_call_tool(
    name: str, arguments: dict[str, Any] | None
) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution"""
    
    if name == "search_patients_by_disease":
        if not arguments or "disease_keyword" not in arguments:
            raise ValueError("Missing disease_keyword argument")
        
        keyword = arguments["disease_keyword"]
        patients = search_patients_by_disease(keyword)
        
        if not patients:
            return [types.TextContent(
                type="text",
                text=f"No patients found matching '{keyword}'. Try searching for common symptoms or diseases."
            )]
        
        result = f"Found {len(patients)} patients matching '{keyword}':\n\n"
        for i, patient in enumerate(patients, 1):
            result += f"{i}. ID: {patient['patient_id']:3s} | Name: {patient['name']:20s} | "
            result += f"Age: {patient['age']:2s} | Symptoms: {patient['current_symptoms'][:40]}\n"
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "get_patient_summary":
        if not arguments or "patient_id" not in arguments:
            raise ValueError("Missing patient_id argument")
        
        patient_id = arguments["patient_id"]
        patient = get_patient_by_id(patient_id)
        
        if not patient:
            return [types.TextContent(
                type="text",
                text=f"Patient ID {patient_id} not found."
            )]
        
        result = f"Patient ID: {patient['patient_id']}\n"
        result += f"Name: {patient['name']}\n"
        
        if patient.get('summary', '').strip():
            result += f"\nSummary:\n{patient['summary']}"
        else:
            result += f"\nStatus: No summary yet. Use generate_summary to create one."
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "generate_summary":
        if not arguments or "patient_id" not in arguments:
            raise ValueError("Missing patient_id argument")
        
        patient_id = arguments["patient_id"]
        
        # Get patient health data
        patient_data = read_patient_health_data(patient_id)
        if not patient_data:
            return [types.TextContent(
                type="text",
                text=f"Patient ID {patient_id} not found in health records."
            )]
        
        # Generate summary using Ollama
        summary = generate_summary_with_ollama(patient_data)
        
        result = f"Generated Summary for {patient_data['name']} (ID: {patient_id}):\n\n"
        result += summary
        
        return [types.TextContent(type="text", text=result)]
    
    elif name == "update_patient_summary":
        print(f"[TOOL_HANDLER] update_patient_summary tool called", file=sys.stderr)
        print(f"[TOOL_HANDLER]   Arguments received (patient_id and summary)", file=sys.stderr)
        
        if not arguments or "patient_id" not in arguments or "summary" not in arguments:
            raise ValueError("Missing required arguments: patient_id and summary")
        
        patient_id = arguments["patient_id"]
        summary = arguments["summary"]
        
        print(f"[TOOL_HANDLER] Processing patient_id={patient_id}, summary_length={len(summary)}", file=sys.stderr)
        
        # Check if patient exists (single read)
        patient = get_patient_by_id(patient_id)
        if not patient:
            print(f"[TOOL_HANDLER] Patient {patient_id} NOT found", file=sys.stderr)
            return [types.TextContent(
                type="text",
                text=f"Error: Patient ID {patient_id} not found."
            )]
        
        print(f"[TOOL_HANDLER] Found patient: {patient['name']}", file=sys.stderr)
        
        # Update the summary (handles all read/write logic)
        print(f"[TOOL_HANDLER] Calling update_patient_summary function...", file=sys.stderr)
        update_result = update_patient_summary(patient_id, summary)
        print(f"[TOOL_HANDLER] Update returned: {update_result}", file=sys.stderr)
        
        if update_result:
            result = f"✓ Summary for Patient ID {patient_id} ({patient['name']}) has been saved.\n\n"
            result += f"Summary ({len(summary)} characters):\n{summary}"
            print(f"[TOOL_HANDLER] ✅ Returning success message", file=sys.stderr)
            return [types.TextContent(type="text", text=result)]
        else:
            print(f"[TOOL_HANDLER] ❌ Update failed - returning error", file=sys.stderr)
            return [types.TextContent(
                type="text",
                text=f"Error: Failed to update summary for patient ID {patient_id}."
            )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Main entry point for the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="patient-summaries-server",
                server_version="2.0.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
