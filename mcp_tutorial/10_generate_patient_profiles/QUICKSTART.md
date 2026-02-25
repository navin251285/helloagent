# 🚀 Quick Start Guide - Patient Summary System

## One Command to Start

```bash
cd mcp_tutorial/10_generate_patient_profiles
python3 mcp_client.py
```

## What You Get

The system is **fully set up and ready to use**:

✅ **Ollama + Phi LLM** - Downloaded and ready on port 11434  
✅ **Chroma DB** - Indexed with 100 patient profiles  
✅ **MCP Server** - Ready to handle patient search and summary generation  
✅ **CSV Storage** - Patient summaries persist between runs  

## Step-by-Step Workflow

### 1. Enter Disease/Symptom
```
Enter disease/symptom keyword: diabetes
```

### 2. Select from Top 5 Results
```
Found 5 patients matching 'diabetes':
1. ID:   1 | Name: Justin Cox
2. ID:   3 | Name: Susan Hall
[...]

Select patient number (1-5): 1
```

### 3. View Patient Details
```
Patient ID: 1
Name: Justin Cox

Status: No summary yet. Use generate_summary to create one.
```

### 4. Generate Summary (30-60 seconds)
```
Generating clinical summary using Phi model...

Generated Summary:
Patient Justin Cox, an 83-year-old female, presents with multiple concerning 
symptoms including swelling in the legs, weakness, and chills...
```

### 5. Save Summary
```
Save this summary to patient_summaries.csv? (y/n): y

✓ Summary saved successfully!
```

## Try These Searches

```
diabetes, hypertension, chest pain, fever, weakness, obesity, arthritis, dizziness
```

## What's Happening Behind the Scenes?

```
User Input (Disease)
       ↓
Chroma DB (Vector Search) → Top 5 Patients
       ↓
Patient Selection
       ↓
Ollama Phi LLM → Clinical Summary
       ↓
Save to CSV → Persistent Storage
```

## System Architecture

| Component | Technology | Status |
|-----------|-----------|--------|
| **Vector Database** | Chroma DB | ✅ Ready (100 patients) |
| **LLM** | Ollama + Phi 2.7B | ✅ Ready (1.6GB) |
| **Server** | MCP (Model Context Protocol) | ✅ Ready |
| **Storage** | CSV + Chroma DB | ✅ Ready |
| **Client** | Python CLI | ✅ Ready |

## Feature Highlights

🔍 **Semantic Search** - Find patients by disease/symptoms, not just names  
🤖 **AI Summaries** - Phi LLM generates smart clinical summaries  
💾 **Persistent** - Summaries saved to CSV, available next session  
⚡ **Fast** - Searches <100ms, summaries 30-60 sec  
🏥 **Healthcare Ready** - Clinical terminology and patient data  

## No Dependencies Left to Install

Everything is already installed:
- ✅ Ollama (with Phi model)
- ✅ Chroma DB
- ✅ MCP libraries
- ✅ Python packages

## Start Now!

```bash
python3 mcp_client.py
```

That's it! The system is ready to use.
