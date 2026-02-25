# Complete System Documentation Index

## 📚 Documentation Files

### 1. **SYSTEM_ARCHITECTURE.md** ⭐ START HERE
**Complete system overview with visual diagrams**
- Full system architecture with flowcharts
- How all components work together
- Data flow from user input to CSV persistence
- Performance characteristics
- Technologies used (Chroma, MCP, Ollama, Phi)
- Troubleshooting guide

**Read this first to understand the big picture**

---

### 2. **MODULE_DATA_GENERATION.md**
**How the patient dataset is created**
- Purpose: Generate realistic 100-patient dataset
- Data schema (11 fields per patient)
- Demographics, health metrics, medications
- Randomization approach
- Running instructions
- Output format

**When:** First-time setup, or when you need to regenerate the dataset

---

### 3. **MODULE_CHROMA_DB.md**
**Vector database setup for semantic search**
- What is semantic search vs keyword search
- How sentence-transformers work
- Embedding process (text → 384-dim vectors)
- HNSW search algorithm
- Installing and running chroma_setup.py
- Testing the vector database
- Alternative models and configurations

**When:** First-time setup, or tuning search quality

---

### 4. **MODULE_MCP_SERVER.md**
**Backend service with 4 tools**
- Complete server architecture
- 4 tool handlers explained:
  1. search_patients_by_disease (Chroma DB)
  2. get_patient_summary (CSV read)
  3. generate_summary (Ollama)
  4. update_patient_summary (CSV write)
- Core functions (read/write/update)
- Performance metrics
- Testing and troubleshooting

**When:** Understanding backend operations, debugging issues

---

### 5. **MODULE_MCP_CLIENT.md**
**Interactive CLI application for users**
- User workflow (7 steps per patient)
- 4 main functions explained
- Input parsing and extraction logic
- Async/await pattern
- UI/UX layout
- Integration with MCP
- Testing procedures

**When:** Understanding user interface, debugging client issues

---

### 6. **MODULE_OLLAMA_PHI.md**
**Local LLM inference engine**
- What is Ollama (local LLM runtime)
- What is Phi (2.7B model by Microsoft)
- Installation steps
- API configuration
- How generation works (request flow)
- Performance metrics (30-60 sec per summary)
- Temperature and prompt engineering
- Troubleshooting connection issues

**When:** Setting up Ollama, tuning generation, debugging LLM issues

---

## 🚀 Quick Start

### First Time Setup (5 minutes)

```bash
cd /path/to/10_generate_patient_profiles

# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate patient data (one-time)
python3 generate_patients.py

# 3. Create vector database index (one-time)
python3 chroma_setup.py

echo "✓ Setup complete!"
```

### Every Session (2+ terminals)

**Terminal 1: Start Ollama**
```bash
ollama serve
# Keep running!
```

**Terminal 2: Run Client**
```bash
cd /path/to/10_generate_patient_profiles
python3 mcp_client.py

# Interactive workflow:
# 1. Enter disease keyword
# 2. Select patient (1-5)
# 3. Wait for summary generation
# 4. Confirm save
```

---

## 📊 System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    PATIENT SUMMARY SYSTEM                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ MCP Client (mcp_client.py)      [MODULE_MCP_CLIENT.md]  │   │
│  │ - User interface                                         │   │
│  │ - Search & select patients                              │   │
│  │ - Extract summaries                                      │   │
│  │ - Confirm saves                                          │   │
│  └────────────────┬─────────────────────────────────────────┘   │
│                   │ MCP (stdio)                                  │
│  ┌────────────────▼─────────────────────────────────────────┐   │
│  │ MCP Server (mcp_server.py)      [MODULE_MCP_SERVER.md]  │   │
│  │ - 4 tool handlers                                        │   │
│  │ - CSV I/O                                                │   │
│  │ - Chroma queries                                         │   │
│  │ - Ollama integration                                     │   │
│  └────────┬──────────────┬──────────────┬────────────────────┘   │
│           │              │              │                        │
│    ┌──────▼──┐    ┌──────▼──┐   ┌──────▼──┐    ┌──────────┐    │
│    │Chroma DB│    │CSV Stor │   │Ollama   │    │Patients  │    │
│    │[MODULE_ │    │[patient │   │+ Phi    │    │Data CSV  │    │
│    │CHROMA  │    │_summaries    │[MODULE_ │    │[MODULE_  │    │
│    │_DB.md]  │    │.csv]    │   │OLLAMA_  │    │DATA_GEN] │    │
│    │         │    │         │   │PHI.md]  │    │          │    │
│    └─────────┘    └─────────┘   └─────────┘    └──────────┘    │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📖 Reading Guide by Role

### 👤 **New User (I just want to use it)**
1. Read: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) - Overview
2. Follow: Quick Start section above
3. Run: `python3 mcp_client.py`
4. Troubleshoot: See [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md#-troubleshooting)

### 💻 **Developer (I want to understand the code)**
1. Read: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) - Architecture
2. Read: [MODULE_MCP_SERVER.md](MODULE_MCP_SERVER.md) - Backend
3. Read: [MODULE_MCP_CLIENT.md](MODULE_MCP_CLIENT.md) - Frontend
4. Study: Source code with docs
5. Extend: Modify tools/functions as needed

### 🔬 **Data Scientist (I want to improve the system)**
1. Read: [MODULE_DATA_GENERATION.md](MODULE_DATA_GENERATION.md) - Dataset
2. Read: [MODULE_CHROMA_DB.md](MODULE_CHROMA_DB.md) - Search
3. Read: [MODULE_OLLAMA_PHI.md](MODULE_OLLAMA_PHI.md) - LLM tuning
4. Experiment: Adjust embeddings, temperatures, prompts

### 🛠️ **DevOps (I want to deploy it)**
1. Read: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md) - Requirements
2. Read: [MODULE_OLLAMA_PHI.md](MODULE_OLLAMA_PHI.md) - Ollama setup
3. Containerize: Use Dockerfile for reproducibility
4. Monitor: Watch for Ollama connection issues

---

## 🎯 Key Concepts

### Semantic Search (Chroma DB)
**What:** Find conceptually similar patients vs. keyword matching
**Where:** [MODULE_CHROMA_DB.md](MODULE_CHROMA_DB.md)
**Why:** "diabetes" finds patients with "Type 2 Diabetes", "high blood sugar", etc.
**How:** Sentence-transformers + HNSW algorithm

### MCP Protocol (Client-Server)
**What:** Async tool-based communication between programs
**Where:** [MODULE_MCP_CLIENT.md](MODULE_MCP_CLIENT.md) + [MODULE_MCP_SERVER.md](MODULE_MCP_SERVER.md)
**Why:** Clean separation of concerns, robust async design
**How:** JSON-RPC over stdio with async/await

### Local LLM (Ollama + Phi)
**What:** Privacy-preserving summary generation without cloud APIs
**Where:** [MODULE_OLLAMA_PHI.md](MODULE_OLLAMA_PHI.md)
**Why:** No data leaves your machine, cost-free, reproducible
**How:** HTTP POST requests to local Ollama server

---

## 📋 File Structure

```
10_generate_patient_profiles/
├── README.md                          ← Overview
├── SYSTEM_ARCHITECTURE.md             ← Complete system design (START HERE)
├── MODULE_DATA_GENERATION.md          ← Patient dataset creation
├── MODULE_CHROMA_DB.md                ← Vector database
├── MODULE_MCP_SERVER.md               ← Backend service
├── MODULE_MCP_CLIENT.md               ← User interface
├── MODULE_OLLAMA_PHI.md               ← LLM engine
│
├── generate_patients.py               ← Create dataset (run once)
├── chroma_setup.py                    ← Index database (run once)
├── mcp_server.py                      ← Backend (auto-launched)
├── mcp_client.py                      ← Frontend (main executable)
│
├── patients_data.csv                  ← Source data (100 patients)
├── patient_summaries.csv              ← Generated summaries (100 rows)
├── chroma_db/                         ← Vector index (auto-created)
│
├── requirements.txt                   ← Python dependencies
├── test_*.py                          ← Test scripts
└── README_MCP_SYSTEM.md               ← (Other docs)
```

---

## 🔄 Development Workflow

### To Add a New Search Feature
1. Modify `search_patients_by_disease()` in `mcp_server.py`
2. Update tool schema in `handle_list_tools()`
3. Update client parsing in `mcp_client.py`
4. Test with `test_mcp_e2e.py`
5. Document in [MODULE_MCP_SERVER.md](MODULE_MCP_SERVER.md)

### To Improve Summary Generation
1. Modify prompt in `generate_summary_with_ollama()`
2. Adjust temperature in `OLLAMA_TEMPERATURE`
3. Test with different patients
4. Document changes in [MODULE_OLLAMA_PHI.md](MODULE_OLLAMA_PHI.md)

### To Change the Dataset
1. Modify `generate_patients.py`
2. Run: `python3 generate_patients.py`
3. Rebuild Chroma: `rm -rf chroma_db/ && python3 chroma_setup.py`
4. Test search results
5. Update [MODULE_DATA_GENERATION.md](MODULE_DATA_GENERATION.md)

---

## ⚡ Performance Summary

| Operation | Time | Bottleneck |
|-----------|------|-----------|
| Search (Chroma) | 10-50ms | Network |
| Load patient | 10-20ms | CSV read |
| Generate summary | 30-60 sec | **LLM inference** |
| Save summary | 20-30ms | CSV write |
| **Total workflow** | **~60 sec** | LLM |

---

## 🆘 Troubleshooting Flowchart

```
Issue?
├─→ "Cannot find patients"
│   └─→ Check: chroma_db/ exists?
│       └─→ No: Run chroma_setup.py
│       └─→ Yes: Try different keyword
│
├─→ "Cannot connect to Ollama"
│   └─→ Check: ollama serve running?
│       └─→ No: Start in another terminal
│       └─→ Yes: Check port 11434
│
├─→ "Permission denied" on CSV
│   └─→ Fix: chmod 666 patient_summaries.csv
│
├─→ "Summary generation slow" (>60 sec)
│   └─→ Normal on CPU (expected)
│       └─→ Close background apps
│       └─→ Add more RAM
│
└─→ "Can't start client"
    └─→ Check: Python 3.8+?
        └─→ pip install -r requirements.txt
```

---

## 📚 Additional Resources

**Chroma Vector DB:**
- Docs: https://docs.trychroma.com
- GitHub: https://github.com/chroma-core/chroma

**Ollama:**
- Website: https://ollama.ai
- GitHub: https://github.com/ollama/ollama
- Model Library: https://ollama.ai/library

**MCP (Model Context Protocol):**
- Docs: https://modelcontextprotocol.io
- Python SDK: https://github.com/modelcontextprotocol/python-sdk

**Phi LLM:**
- Paper: https://arxiv.org/abs/2309.05463
- Model Card: https://huggingface.co/microsoft/phi-2

**Sentence Transformers:**
- Website: https://www.sbert.net
- GitHub: https://github.com/UKPLab/sentence-transformers

---

## 🎓 Learning Paths

### Path 1: Complete Beginner
1. Read: [SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)
2. Watch: Video on vector databases (YouTube search "FAISS tutorial")
3. Watch: Video on LLMs (YouTube search "LLM inference basics")
4. Run: This system
5. Experiment: Modify prompts in MODULE_OLLAMA_PHI.md

### Path 2: Software Developer
1. Read: [MODULE_MCP_SERVER.md](MODULE_MCP_SERVER.md)
2. Read: [MODULE_MCP_CLIENT.md](MODULE_MCP_CLIENT.md)
3. Study: Source code
4. Extend: Add new tool
5. Deploy: Containerize with Docker

### Path 3: ML Engineer
1. Read: [MODULE_CHROMA_DB.md](MODULE_CHROMA_DB.md)
2. Read: [MODULE_OLLAMA_PHI.md](MODULE_OLLAMA_PHI.md)
3. Experiment: Different embedding models
4. Experiment: Different LLM models
5. Optimize: Quantization, pruning

---

## ✅ Verification Checklist

**After setup, verify:**
- [ ] `patients_data.csv` has 100 rows
- [ ] `chroma_db/` directory exists
- [ ] `ollama list` shows `phi` model
- [ ] `ollama serve` starts without errors
- [ ] `python3 mcp_client.py` launches
- [ ] Search returns 5 results
- [ ] Summary generation takes 30-60 sec
- [ ] Summary saves to `patient_summaries.csv`

---

**Last Updated:** February 25, 2026

**Total Documentation:** ~15,000 words across 7 files
