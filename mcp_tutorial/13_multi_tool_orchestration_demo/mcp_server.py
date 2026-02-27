#!/usr/bin/env python3
"""
MCP Server - Multi-Tool Orchestration Demo
Demonstrates 5 math tools with shared state and inter-tool dependencies
"""

import asyncio
import json
from typing import Any, Dict
from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

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

async def tool_sum(a: float, b: float) -> float:
    """Sum two numbers and store result in accumulator"""
    await asyncio.sleep(0.5)  # Simulate processing
    result = a + b
    SHARED_STATE["accumulator"] = result
    SHARED_STATE["last_sum"] = result
    SHARED_STATE["history"].append(f"SUM: {a} + {b} = {result}")
    print(f"[TOOL_SUM v{TOOL_VERSIONS['tool_sum']}] {a} + {b} = {result}")
    print(f"[ACCUMULATOR] {result}")
    return result


async def tool_multiply(a: float, b: float) -> float:
    """
    Multiply: Uses accumulator if a is not provided (a=0 means use accumulator)
    """
    await asyncio.sleep(0.5)
    
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


async def tool_subtract(a: float, b: float) -> float:
    """Subtract: Uses accumulator if a is not provided (a=0 means use accumulator)"""
    await asyncio.sleep(0.3)
    
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


async def tool_divide(a: float, b: float) -> float:
    """Divide: Uses accumulator if a is not provided (a=0 means use accumulator)"""
    await asyncio.sleep(0.3)
    
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


async def tool_average(numbers: list) -> float:
    """
    Average a list of numbers
    DEPENDENCY: Can use results from other tools stored in shared state
    """
    await asyncio.sleep(0.5)
    
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


# ========================================
# MCP SERVER SETUP
# ========================================

app = Server("multi-tool-orchestration-demo")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available math tools"""
    return [
        Tool(
            name="tool_sum",
            description=f"Sum two numbers (v{TOOL_VERSIONS['tool_sum']}). Stores result in shared state as 'last_sum'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="tool_multiply",
            description=f"Multiply two numbers (v{TOOL_VERSIONS['tool_multiply']}). If last_sum exists, adds it to first number. Stores result as 'last_multiply'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="tool_subtract",
            description=f"Subtract second number from first (v{TOOL_VERSIONS['tool_subtract']}). Stores result as 'last_subtract'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number"},
                    "b": {"type": "number", "description": "Second number"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="tool_divide",
            description=f"Divide first number by second (v{TOOL_VERSIONS['tool_divide']}). Handles division by zero. Stores result as 'last_divide'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "Numerator"},
                    "b": {"type": "number", "description": "Denominator"},
                },
                "required": ["a", "b"],
            },
        ),
        Tool(
            name="tool_average",
            description=f"Calculate average of a list of numbers (v{TOOL_VERSIONS['tool_average']}). Can use results from other tools. Stores result as 'last_average'.",
            inputSchema={
                "type": "object",
                "properties": {
                    "numbers": {
                        "type": "array",
                        "items": {"type": "number"},
                        "description": "List of numbers to average",
                    },
                },
                "required": ["numbers"],
            },
        ),
        Tool(
            name="get_state",
            description="Get current accumulator value and operation history without modifying state.",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute tool and return result"""
    
    print(f"\n{'='*50}")
    print(f"TOOL CALL: {name}")
    print(f"VERSION: {TOOL_VERSIONS.get(name, 'unknown')}")
    print(f"ARGUMENTS: {arguments}")
    print(f"SHARED STATE BEFORE: {SHARED_STATE}")
    print(f"{'='*50}")
    
    try:
        if name == "get_state":
            # Just return state without modifying it
            result = None
        elif name == "tool_sum":
            result = await tool_sum(arguments["a"], arguments["b"])
        elif name == "tool_multiply":
            result = await tool_multiply(arguments["a"], arguments["b"])
        elif name == "tool_subtract":
            result = await tool_subtract(arguments["a"], arguments["b"])
        elif name == "tool_divide":
            result = await tool_divide(arguments["a"], arguments["b"])
        elif name == "tool_average":
            result = await tool_average(arguments["numbers"])
        else:
            raise ValueError(f"Unknown tool: {name}")
        
        print(f"SHARED STATE AFTER: {SHARED_STATE}")
        print(f"{'='*50}\n")
        
        return [
            TextContent(
                type="text",
                text=json.dumps({
                    "tool": name,
                    "version": TOOL_VERSIONS.get(name),
                    "result": result,
                    "shared_state": dict(SHARED_STATE),
                }, indent=2)
            )
        ]
    
    except Exception as e:
        print(f"ERROR: {e}")
        print(f"{'='*50}\n")
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    """Run the MCP server"""
    print("=" * 60)
    print("MCP SERVER: Multi-Tool Orchestration Demo")
    print("=" * 60)
    print("Available Tools:")
    for tool_name, version in TOOL_VERSIONS.items():
        print(f"  - {tool_name} (v{version})")
    print("=" * 60)
    print("Server running via stdio...")
    print()
    
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
