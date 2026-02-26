#!/usr/bin/env python3
"""
MCP Server for Patient Summaries with Chroma DB and Ollama - WebSocket Version
- Search patients by disease/symptoms using Chroma DB
- Generate summaries using Ollama (Phi model)
- Update and persist summaries to CSV
- Communication via WebSocket instead of stdio
- Event tracking with message transparency for UI
"""

import asyncio
import csv
import json
import sys
import requests
import uuid
from typing import Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp import types

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

# Import message tracking system
from message_tracker import get_tracker, MessageSource, MessageType
from message_api import message_router, stats_router

# Configuration
CSV_FILE = "patient_summaries.csv"
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi"

# Global websocket for streaming
websocket_connection = None

# Initialize FastAPI and MCP server
fastapi_app = FastAPI()
mcp_server = Server("patient-summaries-server")

# Add message tracking endpoints to FastAPI
fastapi_app.include_router(message_router)
fastapi_app.include_router(stats_router)

# Message tracker instance
tracker = get_tracker()

# Chroma client for search
chroma_client = None
if CHROMA_AVAILABLE:
    try:
        chroma_client = chromadb.PersistentClient(path="./chroma_db")
        print(f"[INIT] ✅ Chroma DB initialized successfully", file=sys.stderr)
        collections = chroma_client.list_collections()
        print(f"[INIT] Found {len(collections)} collections:", file=sys.stderr)
        for col in collections:
            print(f"[INIT]   - {col.name}: {col.count()} items", file=sys.stderr)
    except Exception as e:
        print(f"[INIT] ❌ Chroma DB initialization failed: {e}", file=sys.stderr)
        chroma_client = None
else:
    print(f"[INIT] ❌ chromadb not available!", file=sys.stderr)


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
    print(f"[SEARCH] Called with keyword: '{disease_keyword}'", file=sys.stderr)
    
    # Track operation start
    operation_id = f"chroma_search_{uuid.uuid4()}"
    tracker.start_operation(operation_id)
    
    if not chroma_client:
        print(f"[SEARCH] ❌ chroma_client is None! Cannot search.", file=sys.stderr)
        # Log error
        tracker.log_message(
            source=MessageSource.CHROMA_DB,
            message_type=MessageType.CHROMA_SEARCH,
            content={"keyword": disease_keyword, "error": "chroma_client not initialized"},
            status="error",
        )
        return []
    
    try:
        collection = chroma_client.get_collection(name="patients")
        print(f"[SEARCH] Got collection 'patients' with {collection.count()} items", file=sys.stderr)
        
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
        
        print(f"[SEARCH] ✅ Found {len(patients)} patients", file=sys.stderr)
        
        # Get operation duration
        duration = tracker.end_operation(operation_id)
        
        # Log successful search
        tracker.log_message(
            source=MessageSource.CHROMA_DB,
            message_type=MessageType.CHROMA_SEARCH,
            content={
                "keyword": disease_keyword,
                "results_count": len(patients),
                "patients": patients,
            },
            status="success",
            duration=duration,
        )
        
        return patients
    except Exception as e:
        print(f"[SEARCH] ❌ Chroma search error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        
        # Get operation duration
        duration = tracker.end_operation(operation_id)
        
        # Log error
        tracker.log_message(
            source=MessageSource.CHROMA_DB,
            message_type=MessageType.CHROMA_SEARCH,
            content={"keyword": disease_keyword, "error": str(e)},
            status="error",
            duration=duration,
        )
        
        return []


def generate_summary_with_ollama(patient_data):
    """Generate a clinical summary using Ollama (Phi model) - Non-streaming version"""
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

    print(f"[OLLAMA] Starting summary generation for {patient_data.get('name', 'Unknown')}...", file=sys.stderr)
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "temperature": 0.7
            },
            timeout=120  # Increased to 2 minutes for slower systems
        )
        
        if response.status_code == 200:
            result = response.json()
            generated_text = result.get('response', 'Summary generation failed').strip()
            print(f"[OLLAMA] ✅ Summary generated ({len(generated_text)} chars)", file=sys.stderr)
            return generated_text
        else:
            error_msg = f"Ollama API error: {response.status_code}"
            print(f"[OLLAMA] ❌ {error_msg}", file=sys.stderr)
            return error_msg
    except requests.exceptions.Timeout:
        error_msg = "Error: Ollama request timed out after 120 seconds. The model may be too slow."
        print(f"[OLLAMA] ❌ {error_msg}", file=sys.stderr)
        return error_msg
    except requests.exceptions.ConnectionError:
        error_msg = "Error: Cannot connect to Ollama. Make sure Ollama is running on port 11434"
        print(f"[OLLAMA] ❌ {error_msg}", file=sys.stderr)
        return error_msg
    except Exception as e:
        error_msg = f"Error generating summary: {str(e)}"
        print(f"[OLLAMA] ❌ {error_msg}", file=sys.stderr)
        return error_msg


async def generate_summary_with_ollama_streaming(patient_data, websocket=None):
    """Generate a clinical summary using Ollama with streaming tokens"""
    if not patient_data:
        return "Error: No patient data provided"
    
    patient_name = patient_data.get('name', 'Unknown')
    patient_id = patient_data.get('patient_id', 'unknown')
    operation_id = f"ollama_gen_{uuid.uuid4()}"
    
    # Build prompt for the LLM
    prompt = f"""Generate a concise clinical summary for the following patient:

Patient Name: {patient_name}
Age: {patient_data.get('age', 'N/A')}
Gender: {patient_data.get('gender', 'N/A')}
Current Symptoms: {patient_data.get('current_symptoms', 'None')}
Blood Pressure: {patient_data.get('current_bp', 'N/A')}
Blood Sugar: {patient_data.get('current_sugar', 'N/A')} mg/dL
Medical History: {patient_data.get('medical_history', 'None')}
Current Medications: {patient_data.get('current_medications', 'None')}
Risk Score: {patient_data.get('risk_score', 'N/A')}

Provide a brief clinical assessment (2-3 sentences) highlighting key health concerns and recommendations."""

    print(f"[OLLAMA] Starting streaming summary generation for {patient_name}...", file=sys.stderr)
    
    # Log operation start
    tracker.start_operation(operation_id)
    tracker.log_message(
        source=MessageSource.OLLAMA,
        message_type=MessageType.OLLAMA_START,
        content={"patient_name": patient_name, "model": OLLAMA_MODEL},
        patient_id=patient_id,
        status="in-progress",
    )
    
    try:
        response = requests.post(
            OLLAMA_API_URL,
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": True,  # Enable streaming
                "temperature": 0.7
            },
            timeout=120,
            stream=True  # Stream the response
        )
        
        if response.status_code != 200:
            error_msg = f"Ollama API error: {response.status_code}"
            print(f"[OLLAMA] ❌ {error_msg}", file=sys.stderr)
            
            duration = tracker.end_operation(operation_id)
            tracker.log_message(
                source=MessageSource.OLLAMA,
                message_type=MessageType.OLLAMA_COMPLETE,
                content={"error": error_msg},
                patient_id=patient_id,
                status="error",
                duration=duration,
            )
            return error_msg
        
        print(f"[OLLAMA] 🔄 Receiving streaming tokens...", file=sys.stderr)
        full_summary = ""
        token_count = 0
        
        # Process streaming response
        for line in response.iter_lines():
            if line:
                try:
                    chunk = json.loads(line)
                    token = chunk.get('response', '')
                    
                    if token:
                        full_summary += token
                        token_count += 1
                        
                        # Log every 10th token to avoid spam
                        if token_count % 10 == 0:
                            tracker.log_message(
                                source=MessageSource.OLLAMA,
                                message_type=MessageType.OLLAMA_TOKEN,
                                content={
                                    "token_count": token_count,
                                    "chars_generated": len(full_summary),
                                },
                                patient_id=patient_id,
                                status="in-progress",
                            )
                        
                        # Send streaming token to client via websocket
                        if websocket:
                            try:
                                stream_msg = {
                                    "type": "stream_token",
                                    "token": token,
                                    "position": len(full_summary)
                                }
                                await websocket.send_text(json.dumps(stream_msg))
                            except Exception as e:
                                print(f"[OLLAMA] ⚠️  Failed to send token to client: {e}", file=sys.stderr)
                        
                        # Print progress every 10 tokens to console
                        if token_count % 10 == 0:
                            print(f"[OLLAMA] 📝 Received {token_count} tokens (~{len(full_summary)} chars)...", file=sys.stderr)
                    
                    # Check if generation is done
                    if chunk.get('done', False):
                        print(f"[OLLAMA] ✅ Streaming complete ({token_count} tokens, {len(full_summary)} chars)", file=sys.stderr)
                        break
                except json.JSONDecodeError:
                    continue
        
        # Log operation complete
        duration = tracker.end_operation(operation_id)
        tracker.log_message(
            source=MessageSource.OLLAMA,
            message_type=MessageType.OLLAMA_COMPLETE,
            content={
                "token_count": token_count,
                "chars_generated": len(full_summary),
                "summary_preview": full_summary[:100],
            },
            patient_id=patient_id,
            status="success",
            duration=duration,
        )
        
        return full_summary.strip()
    
    except requests.exceptions.Timeout:
        error_msg = "Error: Ollama request timed out after 120 seconds. The model may be too slow."
        print(f"[OLLAMA] ❌ {error_msg}", file=sys.stderr)
        
        duration = tracker.end_operation(operation_id)
        tracker.log_message(
            source=MessageSource.OLLAMA,
            message_type=MessageType.OLLAMA_COMPLETE,
            content={"error": "timeout"},
            patient_id=patient_id,
            status="error",
            duration=duration,
        )
        return error_msg
    except requests.exceptions.ConnectionError:
        error_msg = "Error: Cannot connect to Ollama. Make sure Ollama is running on port 11434"
        print(f"[OLLAMA] ❌ {error_msg}", file=sys.stderr)
        
        duration = tracker.end_operation(operation_id)
        tracker.log_message(
            source=MessageSource.OLLAMA,
            message_type=MessageType.OLLAMA_COMPLETE,
            content={"error": "connection_failed"},
            patient_id=patient_id,
            status="error",
            duration=duration,
        )
        return error_msg
    except Exception as e:
        error_msg = f"Error generating summary: {str(e)}"
        print(f"[OLLAMA] ❌ {error_msg}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        
        duration = tracker.end_operation(operation_id)
        tracker.log_message(
            source=MessageSource.OLLAMA,
            message_type=MessageType.OLLAMA_COMPLETE,
            content={"error": str(e)},
            patient_id=patient_id,
            status="error",
            duration=duration,
        )
        return error_msg


def update_patient_summary(patient_id, new_summary):
    """Update a patient's summary - optimized for single read/write"""
    print(f"[UPDATE_PATIENT_SUMMARY] Called with patient_id={patient_id}, summary_length={len(new_summary)}", file=sys.stderr)
    
    operation_id = f"csv_update_{uuid.uuid4()}"
    tracker.start_operation(operation_id)
    
    # Log CSV read start
    tracker.log_message(
        source=MessageSource.CSV_OPERATION,
        message_type=MessageType.CSV_READ,
        content={"action": "read_summaries"},
        patient_id=str(patient_id),
        status="in-progress",
    )
    
    try:
        # Read once
        summaries = read_summaries()
        
        # Log CSV read complete
        duration_read = tracker.end_operation(operation_id)
        tracker.log_message(
            source=MessageSource.CSV_OPERATION,
            message_type=MessageType.CSV_READ,
            content={"records_read": len(summaries)},
            patient_id=str(patient_id),
            status="success",
            duration=duration_read,
        )
        
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
            tracker.log_message(
                source=MessageSource.CSV_OPERATION,
                message_type=MessageType.CSV_WRITE,
                content={"error": "patient_not_found"},
                patient_id=str(patient_id),
                status="error",
            )
            return False
        
        # Write once
        print(f"[UPDATE_PATIENT_SUMMARY] Writing to CSV...", file=sys.stderr)
        
        operation_id_write = f"csv_write_{uuid.uuid4()}"
        tracker.start_operation(operation_id_write)
        
        write_result = write_summaries(summaries)
        duration_write = tracker.end_operation(operation_id_write)
        
        if write_result:
            print(f"[UPDATE_PATIENT_SUMMARY] ✅ Write successful", file=sys.stderr)
            
            tracker.log_message(
                source=MessageSource.CSV_OPERATION,
                message_type=MessageType.CSV_WRITE,
                content={
                    "patient_id": patient_id,
                    "summary_length": len(new_summary),
                    "summary_preview": new_summary[:100],
                },
                patient_id=str(patient_id),
                status="success",
                duration=duration_write,
            )
            return True
        else:
            print(f"[UPDATE_PATIENT_SUMMARY] ❌ Write failed", file=sys.stderr)
            
            tracker.log_message(
                source=MessageSource.CSV_OPERATION,
                message_type=MessageType.CSV_WRITE,
                content={"error": "write_failed"},
                patient_id=str(patient_id),
                status="error",
                duration=duration_write,
            )
            return False
            
    except Exception as e:
        print(f"[UPDATE_PATIENT_SUMMARY] Exception: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        
        duration = tracker.end_operation(operation_id)
        tracker.log_message(
            source=MessageSource.CSV_OPERATION,
            message_type=MessageType.CSV_WRITE,
            content={"error": str(e)},
            patient_id=str(patient_id),
            status="error",
            duration=duration,
        )
        return False


@mcp_server.list_tools()
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


@mcp_server.call_tool()
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
        
        # Generate summary using Ollama with streaming (non-async fallback)
        # If we have a global websocket_connection, use streaming version
        if websocket_connection:
            # For async streaming, we need to run it in an event loop
            # Since handle_call_tool may not be async, we'll use the regular version for now
            summary = generate_summary_with_ollama(patient_data)
        else:
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


@fastapi_app.websocket("/mcp")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for MCP protocol communication"""
    await websocket.accept()
    print("[WebSocket] Client connected", file=sys.stderr)
    
    # Create new correlation ID for this WebSocket session
    session_correlation_id = str(uuid.uuid4())
    tracker.set_correlation_id(session_correlation_id)
    
    # Log connection
    tracker.log_message(
        source=MessageSource.WEBSOCKET_SEND,
        message_type=MessageType.CONNECTION,
        content={"event": "client_connected", "correlation_id": session_correlation_id},
        status="success",
    )
    
    try:
        while True:
            # Receive JSON-RPC request from client
            message_text = await websocket.receive_text()
            request_data = json.loads(message_text)
            
            print(f"[WebSocket] Received: {request_data.get('method', 'unknown')}", file=sys.stderr)
            
            # Log incoming WebSocket message
            tracker.log_message(
                source=MessageSource.WEBSOCKET_RECEIVE,
                message_type=MessageType.WEBSOCKET_RECEIVE,
                content={
                    "method": request_data.get('method'),
                    "request_id": request_data.get('id'),
                    "message_size": len(message_text.encode('utf-8'))
                },
                tool_name=request_data.get('params', {}).get('name'),
                status="received",
            )
            
            # Handle different MCP protocol messages
            method = request_data.get("method")
            request_id = request_data.get("id")
            params = request_data.get("params", {})
            
            if method == "initialize":
                # Initialize MCP server
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {
                            "tools": {}
                        },
                        "serverInfo": {
                            "name": "patient-summaries-server",
                            "version": "2.0.0"
                        }
                    }
                }
                response_text = json.dumps(response)
                await websocket.send_text(response_text)
                
                # Log outgoing message
                tracker.log_message(
                    source=MessageSource.WEBSOCKET_SEND,
                    message_type=MessageType.WEBSOCKET_SEND,
                    content={"method": "initialize", "status": "success", "message_size": len(response_text.encode('utf-8'))},
                    status="sent",
                )
                
            elif method == "tools/list":
                # List available tools
                tools = await handle_list_tools()
                tools_data = [
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "inputSchema": tool.inputSchema
                    }
                    for tool in tools
                ]
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": tools_data
                    }
                }
                response_text = json.dumps(response)
                await websocket.send_text(response_text)
                
                # Log outgoing message
                tracker.log_message(
                    source=MessageSource.WEBSOCKET_SEND,
                    message_type=MessageType.WEBSOCKET_SEND,
                    content={"method": "tools/list", "tools_count": len(tools_data), "message_size": len(response_text.encode('utf-8'))},
                    status="sent",
                )
                
            elif method == "tools/call":
                # Call a tool
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                try:
                    # Log tool call start
                    tracker.log_message(
                        source=MessageSource.SERVER_PROCESS,
                        message_type=MessageType.TOOL_CALL_START,
                        content={"tool": tool_name, "args": arguments},
                        tool_name=tool_name,
                        patient_id=arguments.get('patient_id', ''),
                        status="in-progress",
                    )
                    
                    # Handle streaming for generate_summary tool
                    if tool_name == "generate_summary":
                        print(f"[WebSocket] generate_summary tool called with streaming support", file=sys.stderr)
                        patient_id = arguments.get("patient_id")
                        
                        # Get patient health data
                        patient_data = read_patient_health_data(patient_id)
                        if not patient_data:
                            result = [types.TextContent(
                                type="text",
                                text=f"Patient ID {patient_id} not found in health records."
                            )]
                        else:
                            # Use streaming generation
                            summary = await generate_summary_with_ollama_streaming(patient_data, websocket)
                            result_text = f"Generated Summary for {patient_data['name']} (ID: {patient_id}):\n\n"
                            result_text += summary
                            result = [types.TextContent(type="text", text=result_text)]
                    else:
                        # Use regular tool handler for other tools
                        result = await handle_call_tool(tool_name, arguments)
                    
                    result_data = [
                        {
                            "type": content.type,
                            "text": content.text
                        }
                        for content in result
                    ]
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": result_data
                        }
                    }
                    
                    # Log tool call complete
                    tracker.log_message(
                        source=MessageSource.SERVER_PROCESS,
                        message_type=MessageType.TOOL_CALL_COMPLETE,
                        content={"tool": tool_name, "result_size": sum(len(r.get('text', '')) for r in result_data)},
                        tool_name=tool_name,
                        patient_id=arguments.get('patient_id', ''),
                        status="success",
                    )
                    
                except Exception as e:
                    print(f"[WebSocket] Error calling tool: {e}", file=sys.stderr)
                    import traceback
                    traceback.print_exc(file=sys.stderr)
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32603,
                            "message": str(e)
                        }
                    }
                    
                    # Log tool call error
                    tracker.log_message(
                        source=MessageSource.SERVER_PROCESS,
                        message_type=MessageType.TOOL_CALL_COMPLETE,
                        content={"tool": tool_name, "error": str(e)},
                        tool_name=tool_name,
                        patient_id=arguments.get('patient_id', ''),
                        status="error",
                    )
                
                response_text = json.dumps(response)
                await websocket.send_text(response_text)
                
                # Log outgoing message
                tracker.log_message(
                    source=MessageSource.WEBSOCKET_SEND,
                    message_type=MessageType.WEBSOCKET_SEND,
                    content={"method": "tools/call", "tool": tool_name, "message_size": len(response_text.encode('utf-8'))},
                    tool_name=tool_name,
                    patient_id=arguments.get('patient_id', ''),
                    status="sent",
                )
                
            else:
                # Unknown method
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                response_text = json.dumps(response)
                await websocket.send_text(response_text)
                
                # Log unknown method
                tracker.log_message(
                    source=MessageSource.ERROR,
                    message_type=MessageType.ERROR_OCCURRED,
                    content={"error": "unknown_method", "method": method},
                    status="error",
                )
                
    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected", file=sys.stderr)
        tracker.log_message(
            source=MessageSource.WEBSOCKET_SEND,
            message_type=MessageType.CONNECTION,
            content={"event": "client_disconnected"},
            status="success",
        )
    except Exception as e:
        print(f"[WebSocket] Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        tracker.log_message(
            source=MessageSource.ERROR,
            message_type=MessageType.ERROR_OCCURRED,
            content={"error": str(e)},
            status="error",
        )


if __name__ == "__main__":
    import uvicorn
    print("Starting MCP Server with WebSocket support on ws://127.0.0.1:8765/mcp", file=sys.stderr)
    # Configure longer timeouts for LLM operations (Ollama can take 30-60 seconds)
    uvicorn.run(
        fastapi_app, 
        host="127.0.0.1", 
        port=8765,
        ws_ping_interval=30,  # Send ping every 30 seconds
        ws_ping_timeout=120,  # Wait up to 2 minutes for pong
        timeout_keep_alive=120  # Keep connection alive for 2 minutes
    )
