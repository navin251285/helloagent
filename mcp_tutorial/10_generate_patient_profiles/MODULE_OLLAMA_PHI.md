# Ollama + Phi LLM Module Documentation

## 📌 Purpose
Local LLM inference engine for generating clinical summaries. Privacy-preserving alternative to cloud-based API services.

## 🤖 What is Ollama?

**Ollama** is an open-source framework for running Large Language Models (LLMs) locally:
- 🖥️ Runs entirely on your machine (CPU or GPU)
- 🔒 No internet required, no data sent to cloud
- ⚡ Fast inference optimized with quantization
- 📦 Simple CLI for downloading and running models
- 🔌 HTTP API for application integration

**Website:** https://ollama.ai

---

## 🧠 What is Phi?

**Phi** is a lightweight LLM model developed by Microsoft:

| Feature | Details |
|---------|---------|
| **Size** | 2.7 Billion parameters |
| **Developer** | Microsoft Research |
| **Type** | Decoder-only transformer |
| **Training Data** | 1.4T tokens of filtered web + synthesized data |
| **License** | MIT (open source) |
| **Best for** | Instruction-following, common sense reasoning |

### Why Phi over larger models?

```
Model Comparison:

Phi (2.7B)          GPT-3.5 (175B)      Llama-2 (70B)
├─ Size: 2.7B       ├─ Size: 175B        ├─ Size: 70B
├─ Speed: FAST ✓    ├─ Speed: Slow       ├─ Speed: Medium
├─ Accuracy: 95%*   ├─ Accuracy: 99%     ├─ Accuracy: 98%
├─ CPU Capable: ✓   ├─ CPU: Impractical  ├─ CPU: Slow
├─ Local: Yes ✓     ├─ Local: No         ├─ Local: Yes ✓
└─ Cost: FREE ✓     └─ Cost: $$$/query   └─ Cost: FREE ✓

*Accuracy measured on common sense QA, MMLU, and similar benchmarks

For this clinical summary use case:
- Phi is 90%+ as accurate as larger models
- 10-100x faster
- Runs on CPU
- Free and open source
```

---

## 🚀 Installation & Setup

### Step 1: Download and Install Ollama

**Option A: Direct Download**
```bash
# Go to https://ollama.ai
# Download for your OS (Windows, Mac, Linux)
# Install like normal application
```

**Option B: Linux/Mac Script**
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

**Verify Installation:**
```bash
ollama --version
# Output: ollama version 0.1.0 (or similar)
```

---

### Step 2: Download the Phi Model

```bash
ollama pull phi

# Output:
# pulling manifest...
# pulling 29f5b86dbfce...
# pulling 2a73f5b1cea8...
# [████████████████████] 100%
# verifying sha256 digest
# writing manifest
# removing any unused layers
# success
```

**What happens:**
- Downloads Phi model (~1.6 GB) from Ollama registry
- Optimizes with quantization (4-bit to reduce size)
- Stores in `~/.ollama/models/`
- Ready to use locally

**Check Downloaded Models:**
```bash
ollama list
# NAME       ID              SIZE    MODIFIED
# phi        a0f8d0ca3f9e   1.6 GB  2 hours ago
```

---

### Step 3: Start Ollama Server

```bash
# Terminal 1 - Start server (keep running)
ollama serve

# Output:
# 2024/02/25 15:30:45 "GET /api/tags HTTP/1.1" 200 192
# listening on 127.0.0.1:11434
```

**What this does:**
- Starts HTTP server on localhost:11434
- Loads model into GPU/CPU memory
- Ready to accept inference requests
- Logs API calls

**Keep this terminal open - needed for client to work!**

---

## 📡 API Configuration

### MCP Server Configuration

In `mcp_server.py`:
```python
# Ollama Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "phi"
OLLAMA_TIMEOUT = 60  # seconds
OLLAMA_TEMPERATURE = 0.7  # creativity
```

**Settings Explanation:**

| Setting | Value | Meaning |
|---------|-------|---------|
| **API_URL** | localhost:11434 | Local HTTP endpoint |
| **MODEL** | phi | Which model to use |
| **TIMEOUT** | 60 sec | Max time to wait for response |
| **TEMPERATURE** | 0.7 | 0=deterministic, 1=creative |

---

## 🔄 How Generation Works

### Request Flow

```
Client: "Generate summary for patient 55"
         │
         ▼
MCP Server: read_patient_health_data(55)
         │
         Patient: John Johnson, 77M, BP: 175/105, Sugar: 245
         │
         ▼
MCP Server: generate_summary_with_ollama(patient_data)
         │
         Create prompt:
         "Generate a concise clinical summary for:
          Patient Name: John Johnson
          Age: 77
          Current Symptoms: shortness of breath, blurred vision, weakness
          Blood Pressure: 175/105 mmHg
          Blood Sugar: 245 mg/dL
          ...
          Provide a brief clinical assessment (2-3 sentences)."
         │
         ▼
HTTP POST to http://localhost:11434/api/generate
{
  "model": "phi",
  "prompt": "...",
  "stream": false,
  "temperature": 0.7,
  "num_predict": 128
}
         │
         ▼
Ollama Server: Load Phi model
         │
         Tokenize prompt
         │
         Forward pass through 2.7B parameters
         │ (Takes ~30-60 seconds on CPU)
         │
         Generate tokens one by one
         │
         Stop at natural ending
         │
         ▼
HTTP Response:
{
  "response": "Based on the patient's medical history...",
  "done": true,
  "total_duration": 45000000000,  # 45 seconds in nanoseconds
  "load_duration": 2000000000,
  "prompt_eval_duration": 1200000000,
  "eval_duration": 41800000000
}
         │
         ▼
Client: Display generated summary
```

---

### Prompt Engineering

**Current prompt structure:**

```python
prompt = f"""Generate a concise clinical summary for the following patient:

Patient Name: {patient_data['name']}
Age: {patient_data['age']}
Gender: {patient_data['gender']}
Current Symptoms: {patient_data['current_symptoms']}
Blood Pressure: {patient_data['current_bp']}
Blood Sugar: {patient_data['current_sugar']}
Medical History: {patient_data['medical_history']}
Current Medications: {patient_data['current_medications']}
Risk Score: {patient_data['risk_score']}

Provide a brief clinical assessment (2-3 sentences) highlighting key health concerns and recommendations."""
```

**Why this structure:**
- ✅ Clear labeling (Phi understands structured input)
- ✅ All relevant context (patient data)
- ✅ Explicit output length (2-3 sentences)
- ✅ Task specification ("clinical assessment")

**To improve output, you can:**
```python
# Option 1: Add examples (few-shot learning)
prompt += """

Example:
Patient: Sarah, 65F, high BP, diabetes
Summary: Patient presents with uncontrolled hypertension and Type 2 diabetes. 
Recommend close monitoring and medication adjustment. Lifestyle changes essential.

Now generate summary for:
..."""

# Option 2: Change temperature
OLLAMA_TEMPERATURE = 0.3  # More deterministic
OLLAMA_TEMPERATURE = 0.9  # More creative

# Option 3: Control length
prompt += "num_predict: 100"  # Max number of tokens
```

---

## 🧪 Testing Ollama Directly

### Test 1: Server Health Check

```bash
curl http://localhost:11434/api/tags
# Response:
# {"models":[{"name":"phi:latest","modified_at":"2024-02-25T20:10:30.123456789Z","size":1673903514,"digest":"a0f8d0ca3f9e"}]}
```

### Test 2: Simple Generate Query

```bash
curl -X POST http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "phi",
    "prompt": "What is 2+2?",
    "stream": false
  }'

# Response:
# {
#   "response": "2+2 equals 4.",
#   "done": true,
#   "total_duration": 2451234568,
#   "load_duration": 234567890,
#   "prompt_eval_count": 8,
#   "eval_count": 4
# }
```

### Test 3: With python requests

```bash
python3 << 'EOF'
import requests
import time

url = "http://localhost:11434/api/generate"

payload = {
    "model": "phi",
    "prompt": "Explain Type 2 Diabetes in one sentence.",
    "stream": False,
    "temperature": 0.7
}

print("Sending request...")
start = time.time()

response = requests.post(url, json=payload, timeout=60)
result = response.json()

elapsed = time.time() - start

print(f"\n✓ Response received in {elapsed:.1f} seconds")
print(f"Generated text:\n{result['response']}")
print(f"\nStats:")
print(f"  Total time: {result['total_duration']/1e9:.1f} sec")
print(f"  Tokens generated: {result.get('eval_count', 'N/A')}")
EOF
```

---

## 📊 Performance Characteristics

### Generation Speed (Per Summary)

```
Hardware: CPU-based (no GPU)

First inference:
├─ Model loading: 2-3 seconds (one-time)
├─ Tokenization: <100ms
├─ Generation: 25-55 seconds
└─ Total: ~30-60 seconds

Subsequent inferences:
├─ Model already loaded
├─ Tokenization: <100ms
├─ Generation: 25-55 seconds
└─ Total: ~25-55 seconds

Throughput: ~0.017 summaries/second (1 per minute)
```

### Why So Slow?

**LLM inference is sequential:**
```
Phi model: 2.7 billion parameters
Each token generation requires:
  1. Embedding lookup
  2. Full forward pass through 2.7B weights
  3. Softmax over 50K vocab
  4. Sample next token

For a 100-token summary:
  100 tokens × (computation time per token) = 25-55 sec

On GPU: 5-10x faster (would be 5-10 sec)
```

### Memory Usage

```
Ollama on CPU:
├─ Model loading: ~3.5 GB RAM (full 16-bit precision)
├─ During inference: ~4 GB
├─ Quantization variants:
│  ├─ Q8 (8-bit):  ~2.8 GB
│  ├─ Q5 (5-bit):  ~1.8 GB
│  ├─ Q4 (4-bit):  ~1.3 GB  ← Used by default
│  └─ Q2 (2-bit):  ~700 MB
└─ Impact: Lower bits = faster, less accurate
```

---

## 🔧 Troubleshooting

### Connection Issues

**Error: "Cannot connect to Ollama on localhost:11434"**

```bash
# Check if server is running
curl http://localhost:11434/api/tags

# If no response:
# 1. Start ollama server
ollama serve

# 2. Check port
netstat -an | grep 11434

# 3. Check firewall
sudo ufw allow 11434

# 4. Try different port (if needed)
# Edit mcp_server.py: OLLAMA_API_URL = "http://localhost:11435/api/generate"
# Start ollama on port 11435: ollama serve --port 11435
```

---

### Model Issues

**Error: "No such file or directory: ~/.ollama/models"**

```bash
# Model not downloaded yet
ollama pull phi

# Takes ~5 minutes depending on internet speed
```

**Error: "OOM: out of memory"**

```bash
# System doesn't have enough RAM
# Solutions:
# 1. Close other applications
# 2. Use smaller model: ollama pull mistral (7B instead of Phi 2.7B)
# 3. Use quantized version: already default (Q4)
```

---

### Speed Issues

**Generation taking >60 seconds**

```
Expected on CPU: 30-60 seconds per summary
This is normal and expected

If >120 seconds:
- System might be swapping to disk
- Close other applications
- Increase system RAM if possible
```

---

## 📈 Advanced Configuration

### Custom Temperature Range

```python
# Current: 0.7 (good balance)

# For deterministic output (reproducible)
OLLAMA_TEMPERATURE = 0.2   # Mostly follows training data

# For creative output (varied)
OLLAMA_TEMPERATURE = 0.9   # Will explore alternatives

# Test different values:
for temp in [0.2, 0.5, 0.7, 0.9]:
    prompt = "List 3 symptoms of diabetes:"
    # Same prompt, different temperatures → different outputs
```

### Alternative Models

If Phi is too slow or too small, try:

```bash
# Mistral: 7B, faster on CPU
ollama pull mistral
# Inference: 60-120 sec (slower than Phi)

# Neural Chat: 7B, optimized for conversation
ollama pull neural-chat
# Inference: 60-120 sec

# LLama-2: 7B, general purpose
ollama pull llama2
# Inference: 60-120 sec

# Then update mcp_server.py:
OLLAMA_MODEL = "mistral"  # instead of "phi"
```

---

## 🎯 Use Cases Where Phi Excels

| Use Case | Phi? | Why |
|----------|------|-----|
| Clinical summaries | ✅ | Understands medical context |
| Simple Q&A | ✅ | Instruction-following |
| Math/Logic | ✅ | Trained on code |
| Translation | ❌ | Limited multilingual |
| Creative writing | ⚠️ | Sometimes repetitive |
| Long documents | ⚠️ | Context limited to ~2K tokens |

---

## 📚 Resources

- **Ollama Docs:** https://github.com/ollama/ollama
- **Phi Paper:** https://arxiv.org/abs/2309.05463
- **Model Explorer:** https://ollama.ai/library
- **LLM Benchmarks:** https://huggingface.co/spaces/HuggingFaceH4/open_llm_leaderboard

---

## 🔐 Privacy & Security

✅ **All computation is local**
- No data leaves your machine
- No API keys needed
- No cloud access logging
- GDPR/HIPAA compliant (if needed)

✅ **Open source**
- Ollama: MIT license
- Phi: MIT license
- Transparent, auditable code

✅ **No subscription**
- Download once, use forever
- No usage limits

---

**Last Updated:** February 25, 2026
