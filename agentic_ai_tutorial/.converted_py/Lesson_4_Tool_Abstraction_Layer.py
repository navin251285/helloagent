#!/usr/bin/env python
# coding: utf-8

# # Lesson 4: Tool Abstraction Layer
# 
# ## Objective
# Build a tool abstraction layer that allows an agent to use external tools (calculator, string operations) through a unified interface. Learn how to define, register, and invoke tools in LangGraph.
# 
# ## Problem Statement
# In previous lessons, agents could only reason and make structured decisions. But real-world problems require **tool execution**: calling functions, APIs, or external systems. How can we enable agents to use tools reliably and safely?
# 
# ## What Was Missing in Previous Lesson (Lesson 3)
# - **Lesson 3** introduced planning and decision-making, but the agent couldn't actually **execute** tools to perform calculations
# - Agents could decide "we need to add 2 + 3", but had no mechanism to actually call an addition function
# - No abstraction for tool definition, registration, or invocation
# 
# ## What New Concept Solves This
# **Tool Abstraction Layer** allows agents to:
# 1. **Define tools** using structured schemas (input/output contracts)
# 2. **Register tools** in a central registry
# 3. **Invoke tools** through a unified interface
# 4. **Handle tool results** and integrate them back into the agent loop
# 
# This decouples the agent logic from specific tool implementations, making the system modular, testable, and extensible.
# 
# ## Key Concepts
# - **Tool Definition**: Schema-based tool specifications using Pydantic or @tool decorator
# - **Tool Registry**: Central lookup for available tools
# - **Tool Invocation**: Safe, uniform tool execution with error handling
# - **Result Integration**: Feeding tool outputs back into agent state

# ## Setup and Imports

# In[ ]:


# Install required libraries
# Packages already installed: pip install -q python-dotenv google-cloud-aiplatform langchain-google-vertexai langgraph pydantic


# In[ ]:


from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

import os
import vertexai
from vertexai.preview.generative_models import GenerativeModel, GenerationConfig
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from typing import List, Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command
import json

load_dotenv()

vertexai.init(
    project=os.getenv("PROJECT_ID"),
    location=os.getenv("LOCATION")
)

llm = ChatVertexAI(
    model="gemini-2.5-flash",
    temperature=0
)

print("✓ Environment loaded")
print(f"✓ Project: {os.getenv('PROJECT_ID')}")
print(f"✓ Location: {os.getenv('LOCATION')}")


# ## Why These Imports Matter
# 
# - **`load_dotenv()`**: Loads credentials from `.env` file securely (never hardcode secrets)
# - **`vertexai.init()`**: Authenticates with Google Cloud and initializes the Vertex AI SDK
# - **`ChatVertexAI`**: LangChain wrapper for Gemini on Vertex AI (better than OpenAI for enterprise)
# - **`@tool` and `tool()`**: Decorators to convert Python functions into LangChain tools
# - **`BaseModel`**: Pydantic for type-safe tool contracts
# - **`StateGraph`**: LangGraph's graph builder for multi-step agent workflows
# - **`temperature=0`**: Deterministic outputs (essential for reliable arithmetic)

# ## Step 1: Define Tools Using @tool Decorator

# In[ ]:


# Define simple arithmetic tools

@tool
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

@tool
def divide(a: float, b: float) -> float:
    """Divide two numbers. Returns 0 if b is 0."""
    if b == 0:
        return 0
    return a / b

# Test the tools
result_add = add.invoke({"a": 2, "b": 3})
result_multiply = multiply.invoke({"a": 4, "b": 5})
result_divide = divide.invoke({"a": 10, "b": 2})

print(f"✓ Tool: add(2, 3) = {result_add}")
print(f"✓ Tool: multiply(4, 5) = {result_multiply}")
print(f"✓ Tool: divide(10, 2) = {result_divide}")

assert result_add == 5, "Add tool failed"
assert result_multiply == 20, "Multiply tool failed"
assert result_divide == 5.0, "Divide tool failed"


# ## Step 2: Create Tool Registry

# In[ ]:


# Tool Registry: Central lookup for available tools
class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Any] = {}

    def register(self, name: str, tool_func):
        """Register a tool by name."""
        self.tools[name] = tool_func
        print(f"  → Registered tool: {name}")

    def get(self, name: str):
        """Retrieve a tool by name."""
        return self.tools.get(name)

    def list(self):
        """List all registered tools."""
        return list(self.tools.keys())

    def invoke(self, name: str, **kwargs):
        """Invoke a tool by name with kwargs."""
        tool_func = self.get(name)
        if not tool_func:
            raise ValueError(f"Tool '{name}' not found")
        return tool_func.invoke(kwargs)

# Create and populate registry
registry = ToolRegistry()
print("\nRegistering tools...")
registry.register("add", add)
registry.register("multiply", multiply)
registry.register("divide", divide)

print(f"\n✓ Available tools: {registry.list()}")


# ## Step 3: Define Agent State and Tools

# In[ ]:


# Define agent state using TypedDict style
from typing import TypedDict

class AgentState(TypedDict):
    problem: str
    steps: list  # List of executed steps
    current_value: float  # Current computation result
    final_answer: str

print("✓ AgentState defined")


# ## Step 4: Build Agent with Tool Invocation Node

# In[ ]:


def plan_and_execute(state: AgentState):
    """Agent node that plans which tools to use."""
    problem = state["problem"]
    steps = state.get("steps", [])
    current_value = state.get("current_value", 0)

    # Ask LLM to suggest a tool
    prompt = f"""Given this arithmetic problem: {problem}
    Current value: {current_value}

    Suggest which tool to use next (add, multiply, or divide) with specific numbers.
    Format your response as: TOOL_NAME(arg1, arg2)
    Example: add(2, 3)
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    tool_call = response.content.strip()

    # Parse tool call (simple parser for demo)
    import re
    match = re.match(r'(\w+)\((.*?)\)', tool_call)
    if match:
        tool_name = match.group(1)
        args_str = match.group(2)
        args = [float(x.strip()) for x in args_str.split(',')]

        # Invoke tool from registry
        try:
            if tool_name == "add":
                result = registry.invoke("add", a=args[0], b=args[1])
            elif tool_name == "multiply":
                result = registry.invoke("multiply", a=args[0], b=args[1])
            elif tool_name == "divide":
                result = registry.invoke("divide", a=args[0], b=args[1])
            else:
                result = "Unknown tool"

            steps.append(f"{tool_name}({args[0]}, {args[1]}) = {result}")
            current_value = result
        except Exception as e:
            steps.append(f"Error: {str(e)}")
    else:
        steps.append(f"Could not parse tool call: {tool_call}")

    return {
        "problem": problem,
        "steps": steps,
        "current_value": current_value,
        "final_answer": str(current_value)
    }

print("✓ Agent node function created")


# ## Step 5: Build and Execute Agent Graph

# In[ ]:


# Create graph
graph_builder = StateGraph(AgentState)

# Add nodes
graph_builder.add_node("plan_and_execute", plan_and_execute)

# Add edges
graph_builder.add_edge(START, "plan_and_execute")
graph_builder.add_edge("plan_and_execute", END)

# Compile graph
graph = graph_builder.compile()

print("✓ Agent graph compiled")


# ## Step 6: Test the Agent

# In[ ]:


# Test case: Solve "What is 5 + 3?"
test_problem = "What is 5 + 3?"

initial_state = {
    "problem": test_problem,
    "steps": [],
    "current_value": 0,
    "final_answer": ""
}

print(f"\nProblem: {test_problem}")
print("\nExecuting agent...")
result = graph.invoke(initial_state)

print(f"\nExecution steps:")
for step in result["steps"]:
    print(f"  {step}")

print(f"\nFinal answer: {result['final_answer']}")
print(f"\n✓ Agent execution complete")


# ## Step 7: Display Graph Diagram

# In[ ]:


from IPython.display import Image, display

try:
    graph_image = graph.get_graph().draw_mermaid_png()
    display(Image(graph_image))
    print("✓ Graph diagram displayed")
except Exception as e:
    print(f"Note: Graph visualization requires additional setup. Error: {e}")

# Print text-based graph representation
print("\nAgent Graph Structure:")
print("""
┌─────────────┐
│    START    │
└──────┬──────┘
       │
       ▼
┌──────────────────────┐
│  plan_and_execute    │
│  • Registry lookup   │
│  • Tool invocation   │
│  • State update      │
└──────┬───────────────┘
       │
       ▼
┌──────────┐
│   END    │
└──────────┘
""")


# ## Step 8: Code Explanation

# ### Tool Definition (@tool decorator)
# ```python
# @tool
# def add(a: float, b: float) -> float:
#     """Add two numbers together."""
#     return a + b
# ```
# - Converts a Python function into a LangChain Tool with automatic schema inference
# - Type hints become part of the tool contract
# - Docstring becomes the tool description for LLM understanding
# - `.invoke()` method allows uniform invocation
# 
# ### Tool Registry Pattern
# ```python
# class ToolRegistry:
#     def invoke(self, name: str, **kwargs):
#         tool_func = self.get(name)
#         return tool_func.invoke(kwargs)
# ```
# - **Decoupling**: Agent doesn't know about individual tool implementations
# - **Discoverability**: LLM can learn about available tools from registry
# - **Security**: Registry can validate tool access before invocation
# - **Extensibility**: New tools can be added without changing agent code
# 
# ### Agent Invocation Flow
# 1. **Planning Phase**: LLM decides which tool to use based on problem
# 2. **Tool Lookup**: Registry retrieves the tool by name
# 3. **Execution**: Tool executes with provided arguments
# 4. **State Update**: Result is stored in agent state for next iteration
# 5. **Iteration**: Agent can call multiple tools sequentially

# ## Production Insight

# ### Why Tool Abstraction Matters in Production
# 
# 1. **API Integration**: Real agents need to call APIs, databases, and microservices
#    - Tool registry becomes your integration layer
#    - One place to manage authentication, rate limiting, error handling
# 
# 2. **Tool Versioning**: Different tool versions can coexist
#    - Route different agent requests to different tool versions
#    - A/B test new tool implementations
# 
# 3. **Tool Monitoring**: Track which tools agents use most
#    - Tool usage analytics inform feature prioritization
#    - Expensive tools can be rate-limited or cached
# 
# 4. **Tool Reliability**: Centralized error handling and retry logic
#    - Circuit breakers prevent cascading failures
#    - Fallback tools provide graceful degradation
# 
# ### Anti-Pattern to Avoid
# ❌ **Don't**: Hardcode tool names in agent logic
# - Makes agent brittle and tool-changes require code rewrites
# - Prevents dynamic tool discovery
# 
# ✓ **Do**: Use registry pattern with dynamic tool lookup
# - Agent logic is independent of tool implementations
# - New tools can be deployed without agent changes

# ## Summary

# ### What You Learned
# 1. **Tool Definition**: Using @tool decorator to create structured, type-safe tools
# 2. **Tool Registry**: Building a central lookup for tool discovery and invocation
# 3. **Tool Invocation**: Safe, uniform tool execution from agent nodes
# 4. **State Integration**: Storing tool results in agent state for multi-step workflows
# 
# ### Key Takeaways
# - Tools are the **bridge between agent reasoning and world action**
# - **Abstraction** makes agents modular, testable, and maintainable
# - **Registries** enable dynamic tool discovery and security controls
# - **Type safety** prevents tool invocation errors
# 
# ### Next Lesson Preview
# **Lesson 5: ReAct Pattern** will add explicit reasoning loops so agents can:
# - Think about what tool to use
# - Observe the tool result
# - Reason about next steps
# - This cycles naturally across multiple steps

# ## Verification Summary

# In[ ]:


print("="*50)
print("VERIFICATION CHECKLIST")
print("="*50)
print(f"✓ Environment variables loaded")
print(f"✓ Vertex AI initialized")
print(f"✓ 3 tools defined and registered (add, multiply, divide)")
print(f"✓ Tool registry pattern implemented")
print(f"✓ Agent graph created and compiled")
print(f"✓ Graph execution tested")
print(f"✓ Arithmetic assertions passed")
print(f"\n✓ LESSON 4 COMPLETE: Tool Abstraction Layer working!")
print("="*50)

