#!/usr/bin/env python3
"""
MCP HTTP Server - Multi-Tool Orchestration Demo
Demonstrates 5 math tools with shared state and inter-tool dependencies
Uses HTTP JSON-RPC instead of stdio
"""

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

# ========================================
# SHARED STATE (Inter-Tool Communication)
# ========================================
SHARED_STATE: Dict[str, Any] = {
    "accumulator": 0,  # Running result like a calculator
    "history": [],     # Track all operations
}

# ========================================
# TOOL VERSIONING
# ========================================
TOOL_VERSIONS = {
    "tool_sum": "1.0",
    "tool_multiply": "1.1",
    "tool_subtract": "1.0",
    "tool_divide": "1.0",
    "tool_average": "1.0",
}

# ========================================
# TOOL IMPLEMENTATIONS
# ========================================

def tool_sum(a: float, b: float) -> float:
    """Sum two numbers and store result in accumulator"""
    result = a + b
    SHARED_STATE["accumulator"] = result
    SHARED_STATE["last_sum"] = result
    SHARED_STATE["history"].append(f"SUM: {a} + {b} = {result}")
    print(f"[TOOL_SUM v{TOOL_VERSIONS['tool_sum']}] {a} + {b} = {result}")
    print(f"[ACCUMULATOR] {result}")
    return result


def tool_multiply(a: float, b: float) -> float:
    """
    Multiply: Uses accumulator if a is not provided (a=0 means use accumulator)
    """
    # If a is 0, use accumulator value (calculator behavior)
    if a == 0 and SHARED_STATE["accumulator"] != 0:
        a = SHARED_STATE["accumulator"]
        print(f"[TOOL_MULTIPLY v{TOOL_VERSIONS['tool_multiply']}] Using accumulator: {a}")
    
    result = a * b
    SHARED_STATE["accumulator"] = result
    SHARED_STATE["last_multiply"] = result
    SHARED_STATE["history"].append(f"MULTIPLY: {a} * {b} = {result}")
    print(f"[TOOL_MULTIPLY v{TOOL_VERSIONS['tool_multiply']}] {a} * {b} = {result}")
    print(f"[ACCUMULATOR] {result}")
    return result


def tool_subtract(a: float, b: float) -> float:
    """Subtract: Uses accumulator if a is not provided (a=0 means use accumulator)"""
    # If a is 0, use accumulator value (calculator behavior)
    if a == 0 and SHARED_STATE["accumulator"] != 0:
        a = SHARED_STATE["accumulator"]
        print(f"[TOOL_SUBTRACT v{TOOL_VERSIONS['tool_subtract']}] Using accumulator: {a}")
    
    result = a - b
    SHARED_STATE["accumulator"] = result
    SHARED_STATE["last_subtract"] = result
    SHARED_STATE["history"].append(f"SUBTRACT: {a} - {b} = {result}")
    print(f"[TOOL_SUBTRACT v{TOOL_VERSIONS['tool_subtract']}] {a} - {b} = {result}")
    print(f"[ACCUMULATOR] {result}")
    return result


def tool_divide(a: float, b: float) -> float:
    """Divide: Uses accumulator if a is not provided (a=0 means use accumulator)"""
    # If a is 0, use accumulator value (calculator behavior)
    if a == 0 and SHARED_STATE["accumulator"] != 0:
        a = SHARED_STATE["accumulator"]
        print(f"[TOOL_DIVIDE v{TOOL_VERSIONS['tool_divide']}] Using accumulator: {a}")
    
    if b == 0:
        print(f"[TOOL_DIVIDE v{TOOL_VERSIONS['tool_divide']}] Error: Division by zero")
        result = None
    else:
        result = a / b
        SHARED_STATE["accumulator"] = result
        SHARED_STATE["history"].append(f"DIVIDE: {a} / {b} = {result}")
        print(f"[TOOL_DIVIDE v{TOOL_VERSIONS['tool_divide']}] {a} / {b} = {result}")
        print(f"[ACCUMULATOR] {result}")
    
    SHARED_STATE["last_divide"] = result
    return result


def tool_average(numbers: list) -> float:
    """
    Average a list of numbers
    DEPENDENCY: Can use results from other tools stored in shared state
    """
    if not numbers:
        print(f"[TOOL_AVERAGE v{TOOL_VERSIONS['tool_average']}] Error: Empty list")
        return None
    
    result = sum(numbers) / len(numbers)
    SHARED_STATE["accumulator"] = result
    SHARED_STATE["last_average"] = result
    SHARED_STATE["history"].append(f"AVERAGE: {numbers} = {result}")
    print(f"[TOOL_AVERAGE v{TOOL_VERSIONS['tool_average']}] Average of {numbers} = {result}")
    print(f"[ACCUMULATOR] {result}")
    return result


def list_tools() -> list:
    """Return list of available tools"""
    return [
        {
            "name": "tool_sum",
            "description": f"Sum two numbers (v{TOOL_VERSIONS['tool_sum']}). Stores result in accumulator.",
            "parameters": ["a", "b"]
        },
        {
            "name": "tool_multiply",
            "description": f"Multiply two numbers (v{TOOL_VERSIONS['tool_multiply']}). Enter 0 for 'a' to use accumulator. Stores result in accumulator.",
            "parameters": ["a", "b"]
        },
        {
            "name": "tool_subtract",
            "description": f"Subtract second number from first (v{TOOL_VERSIONS['tool_subtract']}). Enter 0 for 'a' to use accumulator. Stores result in accumulator.",
            "parameters": ["a", "b"]
        },
        {
            "name": "tool_divide",
            "description": f"Divide first number by second (v{TOOL_VERSIONS['tool_divide']}). Enter 0 for 'a' to use accumulator. Handles division by zero. Stores result in accumulator.",
            "parameters": ["a", "b"]
        },
        {
            "name": "tool_average",
            "description": f"Calculate average of a list of numbers (v{TOOL_VERSIONS['tool_average']}). Stores result in accumulator.",
            "parameters": ["numbers"]
        },
        {
            "name": "get_state",
            "description": "Get current accumulator value and operation history without modifying state.",
            "parameters": []
        },
    ]


# ========================================
# HTTP REQUEST HANDLER
# ========================================

class MCPHandler(BaseHTTPRequestHandler):
    """Handle HTTP JSON-RPC requests for MCP tools"""
    
    def do_POST(self) -> None:
        """Handle POST requests"""
        if self.path != "/":
            self.send_response(404)
            self.end_headers()
            return
        
        # Read request body
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        request = json.loads(raw) if raw else {}
        
        print(f"\n{'='*50}")
        print(f"INCOMING REQUEST")
        print(f"{'='*50}")
        print(f"Method: {request.get('method')}")
        print(f"Params: {request.get('params')}")
        print(f"Shared State Before: {SHARED_STATE}")
        print(f"{'='*50}")
        
        # Handle different methods
        method = request.get("method", "")
        
        try:
            if method == "list_tools":
                result = list_tools()
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id", 1),
                    "result": result
                }
            
            elif method == "call_tool":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                # Handle get_state specially
                if tool_name == "get_state":
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id", 1),
                        "result": {
                            "tool": "get_state",
                            "version": "1.0",
                            "result": None,
                            "shared_state": dict(SHARED_STATE)
                        }
                    }
                else:
                    # Call the appropriate tool
                    if tool_name == "tool_sum":
                        tool_result = tool_sum(arguments["a"], arguments["b"])
                    elif tool_name == "tool_multiply":
                        tool_result = tool_multiply(arguments["a"], arguments["b"])
                    elif tool_name == "tool_subtract":
                        tool_result = tool_subtract(arguments["a"], arguments["b"])
                    elif tool_name == "tool_divide":
                        tool_result = tool_divide(arguments["a"], arguments["b"])
                    elif tool_name == "tool_average":
                        tool_result = tool_average(arguments["numbers"])
                    else:
                        raise ValueError(f"Unknown tool: {tool_name}")
                    
                    response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id", 1),
                        "result": {
                            "tool": tool_name,
                            "version": TOOL_VERSIONS.get(tool_name),
                            "result": tool_result,
                            "shared_state": dict(SHARED_STATE)
                        }
                    }
            
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id", 1),
                    "error": {"code": -32601, "message": f"Method not found: {method}"}
                }
        
        except Exception as e:
            print(f"ERROR: {e}")
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "error": {"code": -32603, "message": str(e)}
            }
        
        print(f"Shared State After: {SHARED_STATE}")
        print(f"{'='*50}\n")
        
        # Send response
        body = json.dumps(response).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    
    def log_message(self, format, *args):
        """Suppress default HTTP logging"""
        pass


def main() -> None:
    """Run the HTTP MCP server"""
    print("=" * 60)
    print("MCP HTTP SERVER: Multi-Tool Orchestration Demo")
    print("=" * 60)
    print("Available Tools:")
    for tool_name, version in TOOL_VERSIONS.items():
        print(f"  - {tool_name} (v{version})")
    print("=" * 60)
    print("Server listening on http://127.0.0.1:3000")
    print("=" * 60)
    print()
    
    server = HTTPServer(("127.0.0.1", 3000), MCPHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
