#!/usr/bin/env python
# coding: utf-8

# # Lesson 6: Tool Registry and Dynamic Routing
# 
# ## Objective
# Create a dynamic tool registry that allows runtime tool discovery and intelligent selection based on problem context.
# 
# ## Problem Statement
# In **Lesson 5**, tool selection was manual. The agent didn't intelligently choose which tool to use. In production, systems may have 10s or 100s of tools. How can agents discover and select the right tools dynamically?
# 
# ## What's New
# - **Dynamic Discovery**: Agent can ask "what tools are available?"
# - **Intelligent Selection**: Agent picks tools based on tool descriptions
# - **Scalability**: New tools can be added to registry without code changes
# - **Context-Aware**: Tool selection adapts to problem characteristics

# ## Setup

# In[ ]:


# Packages already installed: pip install -q python-dotenv google-cloud-aiplatform langchain-google-vertexai langgraph pydantic

from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

import os
import vertexai
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
import json
import re

load_dotenv()
vertexai.init(
    project=os.getenv("PROJECT_ID"),
    location=os.getenv("LOCATION")
)

llm = ChatVertexAI(model="gemini-2.5-flash", temperature=0)

print("✓ Setup complete")


# ## Define Extended Tool Registry

# In[ ]:


@tool
def add(a: float, b: float) -> float:
    """Add two numbers. Use when you need to combine values."""
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers. Use for scaling or computing products."""
    return a * b

@tool
def divide(a: float, b: float) -> float:
    """Divide two numbers. Use for ratios or equal split."""
    return a / b if b != 0 else 0

@tool
def subtract(a: float, b: float) -> float:
    """Subtract two numbers. Use for difference calculation."""
    return a - b

@tool
def power(base: float, exponent: float) -> float:
    """Raise base to the power of exponent."""
    return base ** exponent

# Create registry
class DynamicToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, tool_func, metadata: dict = None):
        """Register a tool with optional metadata."""
        name = tool_func.name
        self.tools[name] = {
            "func": tool_func,
            "description": tool_func.description,
            "metadata": metadata or {}
        }
        print(f"  → Registered: {name}")

    def get_tool_descriptions(self):
        """Return formatted tool descriptions for LLM."""
        descriptions = []
        for name, info in self.tools.items():
            descriptions.append(f"- {name}: {info['description']}")
        return "\n".join(descriptions)

    def invoke(self, tool_name: str, **kwargs):
        """Invoke a tool by name."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not found")
        tool_func = self.tools[tool_name]["func"]
        return tool_func.invoke(kwargs)

# Register all tools
registry = DynamicToolRegistry()
print("\nRegistering tools...")
registry.register(add)
registry.register(multiply)
registry.register(divide)
registry.register(subtract)
registry.register(power)

print(f"\n✓ {len(registry.tools)} tools registered")


# In[ ]:


## Define State and Nodes


# In[ ]:


class DynamicRoutingState(TypedDict):
    problem: str
    steps: list
    result: float

def router_node(state: DynamicRoutingState):
    """Intelligently route to appropriate tools."""
    problem = state["problem"]
    steps = state["steps"]

    # Pass list of available tools to LLM
    tool_list = registry.get_tool_descriptions()

    prompt = f"""Available tools:
{tool_list}

Problem: {problem}
Current steps: {', '.join(steps) if steps else 'None yet'}

Choose the next tool and arguments needed. Respond as: TOOL_NAME(arg1, arg2)
Example: add(5, 3)

If done, respond: DONE
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    action = response.content.strip()

    # Parse and execute
    if "DONE" in action.upper():
        steps.append("Problem solved")
        state["result"] = state.get("result", 0)
    else:
        match = re.match(r'(\w+)\((.*?)\)', action)
        if match:
            tool_name = match.group(1)
            args_str = match.group(2)
            try:
                args = [float(x.strip()) for x in args_str.split(',')]
                result = registry.invoke(tool_name, a=args[0], b=args[1])

                steps.append(f"{tool_name}({args[0]}, {args[1]}) = {result}")
                state["result"] = result
            except Exception as e:
                steps.append(f"Error: {str(e)}")

    return state

print("✓ Router node defined")


# In[ ]:


## Build Graph


# In[ ]:


graph_builder = StateGraph(DynamicRoutingState)
graph_builder.add_node("route", router_node)

graph_builder.add_edge(START, "route")
graph_builder.add_edge("route", END)

graph = graph_builder.compile()
print("✓ Dynamic routing graph compiled")


# In[ ]:


## Test Dynamic Tool Selection


# In[ ]:


# Test 1: Addition problem
problem1 = "Calculate 10 + 5"
state1 = {"problem": problem1, "steps": [], "result": 0}
result1 = graph.invoke(state1)

print(f"Problem: {problem1}")
print(f"Steps: {result1['steps']}")
print(f"Result: {result1['result']}")
print()

# Test 2: Multiplication problem
problem2 = "Calculate 7 * 3"
state2 = {"problem": problem2, "steps": [], "result": 0}
result2 = graph.invoke(state2)

print(f"Problem: {problem2}")
print(f"Steps: {result2['steps']}")
print(f"Result: {result2['result']}")
print()

# Verify results
assert result1["result"] == 15, f"Expected 15, got {result1['result']}"
assert result2["result"] == 21, f"Expected 21, got {result2['result']}"
print("✓ All arithmetic assertions passed")


# In[ ]:


## Key Concepts


# In[ ]:


print("""
Dynamic Routing Benefits
========================

1. TOOL DISCOVERY
   - Agent doesn't need hardcoded tool list
   - New tools automatically available
   - Tool descriptions guide selection

2. INTELLIGENT SELECTION
   - LLM chooses based on semantics
   - Adaptive to problem context
   - Extensible to many tools

3. PRODUCTION PATTERNS
   - Microservice discovery (Kubernetes)
   - Plugin systems
   - API gateway routing

4. SCALABILITY
   - Works with 5 tools or 500 tools
   - Tool registry is central control point
   - A/B testing different tool implementations
""")


# In[ ]:


## Verification


# In[ ]:


print("="*50)
print("VERIFICATION - LESSON 6")
print("="*50)
print(f"✓ DynamicToolRegistry implemented")
print(f"✓ 5 tools registered (add, multiply, divide, subtract, power)")
print(f"✓ Tool descriptions auto-generated")
print(f"✓ Router intelligently selects tools")
print(f"✓ Tests passed with correct arithmetic results")
print(f"\n✓ LESSON 6 COMPLETE: Dynamic Routing working!")
print("="*50)

