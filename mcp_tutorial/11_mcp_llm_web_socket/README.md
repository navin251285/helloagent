# MCP Patient Summary System with WebSocket Communication

This is an advanced MCP (Model Context Protocol) implementation that uses **WebSocket** for client-server communication instead of stdio. It includes Chroma DB for semantic search and Ollama (Phi model) for AI-powered summary generation.

## 🌟 Key Features

- **WebSocket Communication**: Real-time bidirectional communication via WebSocket (ws://)
- **Chroma DB Vector Search**: Semantic search for patients by disease/symptoms
- **Ollama Integration**: AI-powered clinical summary generation using Phi model
- **MCP Protocol**: Full implementation of Model Context Protocol over WebSocket
- **Persistent Storage**: Patient data stored in CSV with automatic updates

## 🆚 Differences from stdio Version

| Feature | stdio Version (10_generate_patient_profiles) | WebSocket Version (This Folder) |
|---------|----------------------------------------------|----------------------------------|
| Communication | Standard input/output (stdio) | WebSocket (ws://127.0.0.1:8765) |
| Server Type | Stdio-based MCP server | FastAPI + WebSocket server |
| Client Type | stdio_client | websockets library client |
| Connection | Subprocess with pipes | Network socket connection |
| Scalability | Single client only | Multiple clients possible |
| Deployment | Local process only | Can run on different machines |

## 📋 Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running
   ```bash
   ollama pull phi
   ollama serve
   ```

## 🚀 Installation

```bash
# Navigate to the folder
cd 10_mcp_llm_web_socket

# Install dependencies
pip install -r requirements.txt
```

## 📊 Data Files

The system uses several CSV files:
- `patient_summaries.csv` - Current patient summaries
- `patients_data.csv` - Detailed patient health records
- `patient_embeddings.csv` - Vector embeddings for search
- `patients_detailed.csv` - Extended patient information
- `chroma_db/` - Vector database for semantic search

All data files are already included and ready to use.

## 🎯 Usage

### Step 1: Start the MCP Server

In one terminal, start the WebSocket server:

```bash
python mcp_server.py
```

You should see:
```
Starting MCP Server with WebSocket support on ws://127.0.0.1:8765/mcp
```

### Step 2: Run the Client

In another terminal, run the client:

```bash
python mcp_client.py
```

### Step 3: Interactive Workflow

1. **Search for Patients**: Enter a disease or symptom keyword (e.g., "diabetes", "chest pain")
2. **Review Results**: See top 5 matching patients from Chroma DB
3. **Select Patient**: Choose a patient by number
4. **Generate Summary**: Ollama Phi generates a clinical summary
5. **Save Summary**: Confirm to save the summary to CSV

## 🔧 How It Works

### Server Architecture (`mcp_server.py`)

```python
FastAPI Application
    ↓
WebSocket Endpoint (/mcp)
    ↓
JSON-RPC Protocol Handler
    ↓
MCP Server Tools:
    - search_patients_by_disease (Chroma DB)
    - get_patient_summary
    - generate_summary (Ollama Phi)
    - update_patient_summary (CSV)
```

### Client Architecture (`mcp_client.py`)

```python
MCPWebSocketClient
    ↓
WebSocket Connection (ws://127.0.0.1:8765/mcp)
    ↓
JSON-RPC Request/Response
    ↓
Interactive CLI Interface
```

### Communication Protocol

The system uses JSON-RPC 2.0 over WebSocket:

**Initialize Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2024-11-05",
    "capabilities": {},
    "clientInfo": {"name": "patient-client", "version": "1.0.0"}
  }
}
```

**Tool Call Request:**
```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "method": "tools/call",
  "params": {
    "name": "search_patients_by_disease",
    "arguments": {"disease_keyword": "diabetes"}
  }
}
```

## 🛠️ Available Tools

1. **search_patients_by_disease**
   - Search patients using Chroma DB vector similarity
   - Returns top 5 matching patients
   
2. **get_patient_summary**
   - Retrieve a patient's current summary by ID
   
3. **generate_summary**
   - Generate AI-powered clinical summary using Ollama Phi
   
4. **update_patient_summary**
   - Save generated summary to CSV database

## 📝 Example Session

```
Enter disease/symptom keyword: diabetes

SEARCH RESULTS FOR: DIABETES
====================================
Found 5 patients matching 'diabetes':

1. ID: 11  | Name: Jerry Rivera      | Age: 59 | Symptoms: fatigue, increased thirst, frequent uri...
2. ID: 23  | Name: Sarah Johnson     | Age: 45 | Symptoms: blurred vision, excessive hunger, weig...
...

Select patient number (1-5): 1

PATIENT DETAILS (ID: 11)
====================================
Patient ID: 11
Name: Jerry Rivera

Generating clinical summary using Phi model (this may take 30-60 seconds)...

GENERATED SUMMARY
====================================
Generated Summary for Jerry Rivera (ID: 11):

This patient presents with classic symptoms of Type 2 Diabetes...

Save this summary to patient_summaries.csv? (y/n): y

✓ Summary saved successfully!
```

## 🔍 Troubleshooting

### Server won't start
- Check if port 8765 is already in use
- Make sure FastAPI and uvicorn are installed

### Client can't connect
- Ensure the server is running first
- Verify WebSocket URL is correct (ws://127.0.0.1:8765/mcp)

### Chroma DB errors
- Check if `chroma_db/` directory exists
- Verify embeddings are loaded correctly

### Ollama errors
- Make sure Ollama is running: `ollama serve`
- Verify the Phi model is installed: `ollama pull phi`

## 🧪 Testing

Run the test files to verify functionality:

```bash
# Test client workflow
python test_client_workflow.py

# Test end-to-end
python test_mcp_e2e.py
```

## 📁 Project Structure

```
10_mcp_llm_web_socket/
├── mcp_server.py              # WebSocket MCP server
├── mcp_client.py              # WebSocket MCP client
├── requirements.txt           # Python dependencies
├── patient_summaries.csv      # Summary database
├── patients_data.csv          # Patient health records
├── patients_data.json         # JSON patient data
├── patient_embeddings.csv     # Vector embeddings
├── patients_detailed.csv      # Detailed records
├── chroma_db/                 # Vector database
├── generate_patients.py       # Data generation tool
├── create_embeddings.py       # Embedding creation
├── chroma_setup.py            # Chroma DB setup
├── query_patients.py          # Query utility
└── test_*.py                  # Test files
```

## 🚀 Advanced Usage

### Running on Different Machines

Since this uses WebSocket, you can run the server and client on different machines:

**On Server Machine:**
```python
# In mcp_server.py, change:
uvicorn.run(fastapi_app, host="0.0.0.0", port=8765)
```

**On Client Machine:**
```python
# In mcp_client.py, change:
MCPWebSocketClient(uri="ws://<server-ip>:8765/mcp")
```

### Multiple Clients

Since WebSocket supports multiple connections, multiple clients can connect simultaneously:

```bash
# Terminal 1
python mcp_client.py

# Terminal 2 (different user)
python mcp_client.py

# Both can interact with the same server
```

## 🔐 Security Considerations

This is a demo implementation. For production:
- Add authentication (JWT tokens, API keys)
- Use WSS (WebSocket Secure) instead of WS
- Implement rate limiting
- Add input validation and sanitization
- Use proper error handling

## 📚 Related Documentation

- MCP Protocol: https://modelcontextprotocol.io/
- Chroma DB: https://www.trychroma.com/
- Ollama: https://ollama.ai/
- FastAPI WebSocket: https://fastapi.tiangolo.com/advanced/websockets/

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section
2. Review error messages in server/client logs
3. Verify all dependencies are installed
4. Ensure Ollama is running and accessible

## 📄 License

This is a tutorial/demo project. Use at your own discretion.
