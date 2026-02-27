# Multi-Tool Orchestration Demo

A simple demonstration of **MCP (Model Context Protocol)** multi-tool orchestration with:

- ✅ **5 Math Tools** (sum, multiply, subtract, divide, average)
- ✅ **Shared State** (inter-tool communication)
- ✅ **Tool Versioning** (track which version is used)
- ✅ **Inter-Tool Dependencies** (tools can use results from other tools)
- ✅ **Sequential Orchestration** (client calls tools in a workflow)
- ✅ **Two Communication Methods** (stdio and HTTP)
- ✅ **Interactive Mode** (menu-driven tool execution with quit option)
- ✅ **Demo Mode** (automated workflow demonstration)

---

## 🎯 What This Demo Shows

This demo demonstrates how multiple MCP tools can work together:

1. **Shared State**: Tools can read/write to a shared state dictionary
2. **Dependencies**: `tool_multiply` uses the result from `tool_sum` automatically
3. **Versioning**: Each tool has a version number (e.g., "1.0", "1.1")
4. **Orchestration**: Client calls 5 tools in sequence to solve a workflow

### 🧮 Calculator Mode (Accumulator Pattern)

The server implements a **calculator-like accumulator** that persists across all operations:

- **Running Accumulator**: `SHARED_STATE["accumulator"]` stores the current result
- **Operation History**: `SHARED_STATE["history"]` tracks all operations performed
- **Smart Input**: When you enter **0** as the first number (`a`), tools automatically use the current accumulator value
- **Final Result**: When you quit, it displays the final accumulator value and complete operation history

**Example Workflow:**
```
1. Sum 10 + 5        → Accumulator: 15  | History: SUM: 10 + 5 = 15
2. Multiply 0 * 2    → Accumulator: 30  | History: MULTIPLY: 15 * 2 = 30
3. Subtract 0 - 5    → Accumulator: 25  | History: SUBTRACT: 30 - 5 = 25
4. Quit              → Shows Final Accumulator: 25 (3 operations)
```

This allows you to chain operations naturally without manually passing results between calls.

---

## 🏗️ Architecture

### Stdio Version (Original)
```
┌─────────────────┐
│  MCP Client     │  Calls tools in sequence via stdio
│  (mcp_client.py)│  
└────────┬────────┘
         │ stdio (JSON-RPC)
         ▼
┌─────────────────┐
│  MCP Server     │  Provides 5 tools with shared state
│(mcp_server.py)  │  SHARED_STATE = {}
└─────────────────┘
```

### HTTP Version (Network-Based)
```
┌──────────────────────┐
│  MCP HTTP Client     │  Makes HTTP POST requests
│(mcp_client_http.py)  │  
└────────┬─────────────┘
         │ HTTP (JSON-RPC)
         ▼
┌──────────────────────┐
│  MCP HTTP Server     │  Listens on http://127.0.0.1:3000
│(mcp_server_http.py)  │  SHARED_STATE = {}
└──────────────────────┘
```

---

## 📋 The 5 Tools

| Tool | Description | Shared State Key | Version |
|------|-------------|------------------|---------|
| `tool_sum` | Sum two numbers (uses accumulator if a=0) | `last_sum`, `accumulator` | 1.0 |
| `tool_multiply` | Multiply two numbers (uses accumulator if a=0) | `last_multiply`, `accumulator` | 1.1 |
| `tool_subtract` | Subtract b from a (uses accumulator if a=0) | `last_subtract`, `accumulator` | 1.0 |
| `tool_divide` | Divide a by b (uses accumulator if a=0) | `last_divide`, `accumulator` | 1.0 |
| `tool_average` | Average a list of numbers | `last_average` | 1.0 |
| `get_state` | Get current accumulator and history (read-only) | - | - |

---

## 🔗 Inter-Tool Dependency Example

**Step 1**: `tool_sum(3, 5)` → Result: **8**  
→ Stores in `SHARED_STATE["last_sum"] = 8`

**Step 2**: `tool_multiply(2, 4)`  
→ Checks if `last_sum` exists in shared state  
→ Modifies calculation: `(2 + 8) * 4 = 40` instead of `2 * 4 = 8`  
→ **This demonstrates inter-tool dependency!**

---

## 🚀 Installation

```bash
cd mcp_tutorial/13_multi_tool_orchestration_demo
pip install -r requirements.txt
```

---

## ▶️ Run the Demo

Both versions now support **two modes**:
1. **Interactive Mode** - Call tools one by one with menu-driven interface
2. **Demo Mode** - Run the full orchestration workflow automatically

### Option 1: Stdio Version (Original)

```bash
python mcp_client.py
```

**Interactive Mode Example:**
```
Choose mode:
1. Interactive mode (call tools one by one)
2. Demo mode (run full orchestration workflow)

Select mode (1 or 2): 1

MENU:
1. tool_sum - Sum two numbers
2. tool_multiply - Multiply two numbers (uses last_sum if available)
3. tool_subtract - Subtract two numbers
4. tool_divide - Divide two numbers
5. tool_average - Average a list of numbers
6. list_tools - Show all available tools
7. demo - Run the full orchestration demo
8. quit - Exit

Select an option (1-8): 1
Enter first number (a): 10
Enter second number (b): 5

✓ Result: 15.0
  Shared State: {'last_sum': 15.0}
```

### Option 2: HTTP Version (Network-Based)

**Terminal 1 - Start the server:**
```bash
python mcp_server_http.py
```

**Terminal 2 - Run the client:**
```bash
python mcp_client_http.py
```

**Interactive Mode Features:**
- Choose which tool to call
- Provide custom inputs
- See shared state after each operation
- Run full demo anytime (option 8)
- Quit anytime by typing 'quit', 'exit', 'q', or selecting option 9 (HTTP) / 8 (stdio)

---

## 🎮 Interactive Mode Commands

Both clients support these interactive commands:

| Option | Command | Description |
|--------|---------|-------------|
| 1 | tool_sum | Sum two numbers |
| 2 | tool_multiply | Multiply (uses last_sum if available) |
| 3 | tool_subtract | Subtract two numbers |
| 4 | tool_divide | Divide two numbers |
| 5 | tool_average | Average a list of numbers |
| 6 | list_tools | Show all available tools |
| 7 (HTTP) | show_state | Show current shared state |
| 7/8 | demo | Run full orchestration workflow |
| 8/9 or 'quit' | Exit | Quit interactive mode |

---

## 📊 Comparison: Stdio vs HTTP

| Feature | Stdio Version | HTTP Version |
|---------|---------------|--------------|
| **Communication** | stdin/stdout pipes | HTTP POST requests |
| **Process Model** | Single process | Two processes |
| **Network** | Local only | Can run on different machines |
| **Debugging** | Server logs in client output | Separate server logs |
| **Scalability** | Single client | Multiple clients possible |
| **Complexity** | Simpler (one command) | Slightly more complex (two commands) |

---

## 📝 Expected Output

Both versions produce the same output:

```
==============================================================
MULTI-TOOL ORCHESTRATION WORKFLOW
==============================================================
Demonstrating: Inter-tool dependencies and shared state
==============================================================

────────────────────────────────────────────────────────────
STEP 1: Calculate Sum
────────────────────────────────────────────────────────────
Tool: tool_sum
Arguments: {'a': 3, 'b': 5}

✓ Result: 8.0
  Version: 1.0
  Shared State: {'last_sum': 8.0}

────────────────────────────────────────────────────────────
STEP 2: Multiply (with dependency on last_sum)
────────────────────────────────────────────────────────────
Tool: tool_multiply
Arguments: {'a': 2, 'b': 4}

✓ Result: 40.0
  Version: 1.1
  Shared State: {'last_sum': 8.0, 'last_multiply': 40.0}

────────────────────────────────────────────────────────────
STEP 3: Subtract
────────────────────────────────────────────────────────────
Tool: tool_subtract
Arguments: {'a': 20, 'b': 5}

✓ Result: 15.0
  Version: 1.0
  Shared State: {'last_sum': 8.0, 'last_multiply': 40.0, 'last_subtract': 15.0}

────────────────────────────────────────────────────────────
STEP 4: Divide
────────────────────────────────────────────────────────────
Tool: tool_divide
Arguments: {'a': 16, 'b': 4}

✓ Result: 4.0
  Version: 1.0
  Shared State: {'last_sum': 8.0, 'last_multiply': 40.0, 'last_subtract': 15.0, 'last_divide': 4.0}

────────────────────────────────────────────────────────────
STEP 5: Calculate Average of all results
────────────────────────────────────────────────────────────
Tool: tool_average
Arguments: {'numbers': [8.0, 40.0, 15.0, 4.0]}

✓ Result: 16.75
  Version: 1.0
  Shared State: {'last_sum': 8.0, 'last_multiply': 40.0, 'last_subtract': 15.0, 'last_divide': 4.0, 'last_average': 16.75}

==============================================================
ORCHESTRATION COMPLETE - FINAL SUMMARY
==============================================================
Step 1: Sum           = 8.0
Step 2: Multiply      = 40.0
Step 3: Subtract      = 15.0
Step 4: Divide        = 4.0
Step 5: Average       = 16.75
==============================================================

📌 KEY OBSERVATION:
   tool_multiply used last_sum (8.0) from shared state
   Expected: 2 * 4 = 8
   Actual: (2 + 8.0) * 4 = 40.0
   This demonstrates inter-tool dependency!
==============================================================
```

---

## 🔍 How It Works

### 1. Shared State (Server Side)

```python
SHARED_STATE = {}

async def tool_sum(a, b):
    result = a + b
    SHARED_STATE["last_sum"] = result  # Store for other tools
    return result
```

### 2. Inter-Tool Dependency

```python
async def tool_multiply(a, b):
    # Check if last_sum exists
    if "last_sum" in SHARED_STATE:
        a = a + SHARED_STATE["last_sum"]  # Use result from tool_sum
    
    result = a * b
    SHARED_STATE["last_multiply"] = result
    return result
```

### 3. Tool Versioning

```python
TOOL_VERSIONS = {
    "tool_sum": "1.0",
    "tool_multiply": "1.1",  # Version 1.1 has the dependency feature
    "tool_subtract": "1.0",
    "tool_divide": "1.0",
    "tool_average": "1.0",
}
```

### 4. Client Orchestration

```python
# Step 1: Calculate sum
sum_result = await session.call_tool("tool_sum", {"a": 3, "b": 5})

# Step 2: Multiply (automatically uses sum_result via shared state)
multiply_result = await session.call_tool("tool_multiply", {"a": 2, "b": 4})

# ... continue with other tools

# Step 5: Average all results
average_result = await session.call_tool(
    "tool_average", 
    {"numbers": [sum_result, multiply_result, subtract_result, divide_result]}
)
```

---

## 📚 Key Concepts Demonstrated

| Concept | How It's Shown |
|---------|----------------|
| **Multi-Tool System** | 5 different tools working together |
| **Shared State** | `SHARED_STATE` dictionary accessible by all tools |
| **Tool Dependencies** | `tool_multiply` depends on `tool_sum`'s result |
| **Versioning** | Each tool has a version (e.g., v1.0, v1.1) |
| **Sequential Orchestration** | Client calls tools in a specific order |
| **MCP Protocol** | Uses standard MCP JSON-RPC over stdio |

---

## 🎓 Learning Points

1. **Tools can communicate** via shared state (not isolated)
2. **Dependencies can be implicit** (multiply checks for last_sum automatically)
3. **Versioning helps track** which implementation is used
4. **Orchestration is client-driven** (client decides the workflow)
5. **Results can be composed** (average uses all previous results)

---

## 🔧 Files

| File | Purpose |
|------|---------|
| **Stdio Version** | |
| `mcp_server.py` | MCP server with 5 tools and shared state (stdio) |
| `mcp_client.py` | Client that orchestrates the workflow (stdio) |
| **HTTP Version** | |
| `mcp_server_http.py` | MCP HTTP server on port 3000 |
| `mcp_client_http.py` | HTTP client that makes POST requests |
| **Documentation** | |
| `requirements.txt` | Python dependencies |
| `README.md` | This documentation |

---

## 🧪 Testing Different Workflows

You can modify `mcp_client.py` to test different orchestrations:

```python
# Test division by zero
await session.call_tool("tool_divide", {"a": 10, "b": 0})

# Test average with different numbers
await session.call_tool("tool_average", {"numbers": [1, 2, 3, 4, 5]})

# Call multiply without calling sum first (no dependency)
await session.call_tool("tool_multiply", {"a": 5, "b": 6})  # Result: 30
```

---

## 📖 Next Steps

After understanding this demo, you can:

1. Add more complex tools (e.g., statistics, transformations)
2. Implement streaming responses for long-running calculations
3. Add more inter-tool dependencies
4. Integrate with LLMs for intelligent orchestration
5. Build a UI to visualize the workflow

---

## ✅ Summary

This demo shows the **simplest possible** multi-tool orchestration:

- 5 math tools with clear purposes
- Shared state for inter-tool communication
- One explicit dependency (multiply → sum)
- Sequential workflow with visible results
- Complete with versioning and error handling

**Everything you need to understand MCP multi-tool orchestration in one simple example!**
