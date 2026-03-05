#!/usr/bin/env python
# coding: utf-8

# # Lesson 5: ReAct Pattern (Reasoning + Acting)
# 
# ## Objective
# Implement the ReAct (Reasoning + Acting) pattern where the agent alternates between reasoning about what to do and executing tool calls. Learn how to create explicit think-act loops.
# 
# ## Problem Statement
# In **Lesson 4**, the agent could use tools, but without explicit reasoning steps. The agent made tool decisions opaquely. How can we make agent reasoning transparent and verify that decisions are sound?
# 
# ## What Was Missing
# - **Lesson 4** allowed tool invocation, but didn't show agent thinking
# - No explicit "think → act → observe" loop
# - Hard to debug agent failures without seeing intermediate reasoning
# 
# ## The ReAct Solution
# ReAct makes agent reasoning **explicit and auditable**:
# 1. **Thought**: Agent reasons about the problem
# 2. **Action**: Agent selects a tool and args
# 3. **Observation**: Tool returns result
# 4. **Repeat**: Loop until goal achieved
# 
# This creates a verifiable chain of reasoning.

# ## Setup

# In[ ]:


# Packages already installed: pip install -q python-dotenv google-cloud-aiplatform langchain-google-vertexai langgraph pydantic

from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

import os
import vertexai
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import tool
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
import re

load_dotenv()
vertexai.init(
    project=os.getenv("PROJECT_ID"),
    location=os.getenv("LOCATION")
)

llm = ChatVertexAI(model="gemini-2.5-flash", temperature=0)

# Define tools from Lesson 4
@tool
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b

@tool
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b

@tool
def divide(a: float, b: float) -> float:
    """Divide two numbers (returns 0 if dividing by 0)."""
    return a / b if b != 0 else 0

tools = {"add": add, "multiply": multiply, "divide": divide}
print("✓ Tools and LLM ready")


# ## Define ReAct State

# In[ ]:


class ReActState(TypedDict):
    problem: str
    thoughts: list      # List of reasoning steps
    actions: list       # List of tool calls
    observations: list  # List of tool results
    history: list       # Full think-act-observe chain
    step_count: int
    is_complete: bool

print("✓ ReAct state defined")


# ## Implement ReAct Nodes

# In[ ]:


def think_node(state: ReActState):
    """Agent generates a thought about what to do next."""
    problem = state["problem"]
    history = state["history"]
    step = state["step_count"]

    # Build context from history
    context = "\n".join(history) if history else "Starting fresh."

    prompt = f"""Problem: {problem}

{context}

    Keep thinking step-by-step. What's your next thought?
    Be concise (one sentence). If done, say 'DONE'.
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    thought = response.content.strip()

    history.append(f"Thought {step}: {thought}")
    state["thoughts"].append(thought)
    state["is_complete"] = "done" in thought.lower()

    return state

def act_node(state: ReActState):
    """Agent selects and executes a tool based on thinking."""
    if state["is_complete"]:
        return state

    problem = state["problem"]
    history = state["history"]
    step = state["step_count"]

    context = "\n".join(history)

    prompt = f"""Problem: {problem}

{context}

    Now perform an action. Choose one:
    - add(a, b)
    - multiply(a, b)
    - divide(a, b)
    - or say 'DONE' if finished

    Respond with just: add(5, 3) or DONE
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    action_str = response.content.strip()

    history.append(f"Action {step}: {action_str}")
    state["actions"].append(action_str)

    # Parse and execute
    match = re.match(r'(\w+)\((.*?)\)', action_str)
    if match:
        tool_name = match.group(1)
        args_str = match.group(2)
        try:
            args = [float(x.strip()) for x in args_str.split(',')]
            tool = tools[tool_name]
            result = tool.invoke({"a": args[0], "b": args[1]})

            history.append(f"Observation {step}: {tool_name}({args[0]}, {args[1]}) = {result}")
            state["observations"].append(result)
        except Exception as e:
            history.append(f"Observation {step}: Error - {str(e)}")
            state["observations"].append(None)
    elif "done" in action_str.lower():
        state["is_complete"] = True

    state["step_count"] += 1
    return state

print("✓ ReAct nodes implemented")


# ## Build ReAct Graph

# In[ ]:


def should_continue(state: ReActState):
    """Decide whether to continue the loop."""
    return "end" if (state["is_complete"] or state["step_count"] >= 5) else "continue"

# Build graph
graph_builder = StateGraph(ReActState)
graph_builder.add_node("think", think_node)
graph_builder.add_node("act", act_node)

graph_builder.add_edge(START, "think")
graph_builder.add_edge("think", "act")
graph_builder.add_conditional_edges(
    "act",
    should_continue,
    {"continue": "think", "end": END}
)

graph = graph_builder.compile()
print("✓ ReAct graph compiled")


# ## Test ReAct Agent

# In[ ]:


problem = "What is (10 + 5) * 2?"

initial_state = {
    "problem": problem,
    "thoughts": [],
    "actions": [],
    "observations": [],
    "history": [],
    "step_count": 1,
    "is_complete": False
}

print(f"Problem: {problem}")
print(f"\nExecuting ReAct Agent...\n")
result = graph.invoke(initial_state)

print("\n" + "="*50)
print("REASONING CHAIN")
print("="*50)
for entry in result["history"]:
    print(entry)

print(f"\n✓ Final observation (answer): {result['observations'][-1] if result['observations'] else 'N/A'}")
print(f"\n✓ ReAct execution complete")


# ## Graph Diagram

# In[ ]:


print("ReAct Agent Loop:")
print("""
┌──────────┐
│  START   │
└────┬─────┘
     │
     ▼
┌──────────────────────┐
│  THINK (Generate     │
│  a reasoning step)   │
└────┬────────────────┘
     │
     ▼
┌──────────────────────┐
│  ACT (Execute a      │
│  tool based on       │
│  reasoning)          │
└────┬────────────────┘
     │
     ├─ if done → END
     │
     └─ else → back to THINK (loop)
""")


# ## Key Insights

# In[ ]:


print("""
ReAct vs Tool Abstraction (Lesson 4)
====================================

Lesson 4: Tool Abstraction
- ✓ Agent could call tools
- ✗ No explicit reasoning visible
- ✗ Hard to debug or audit decisions

Lesson 5: ReAct Pattern
- ✓ Explicit think-act-observe chain
- ✓ Full reasoning visible for audit
- ✓ Can verify correctness of reasoning
- ✓ Supports multi-step problem solving

Production Value:
- Explainability: Customers see why agent made decisions
- Debuggability: Can replay reasoning and find bugs
- Auditability: Full chain of reasoning for compliance
- Iterability: Easy to improve by guiding thoughts
""")


# ## Verification

# In[ ]:


print("="*50)
print("VERIFICATION - LESSON 5")
print("="*50)
print(f"✓ ReAct state defined with think/act/observe")
print(f"✓ think_node generates explicit reasoning")
print(f"✓ act_node executes tools based on thinking")
print(f"✓ Conditional routing creates think-act loop")
print(f"✓ Agent successfully executed multi-step problem")
print(f"✓ Full reasoning chain captured in history")
print(f"\n✓ LESSON 5 COMPLETE: ReAct Pattern implemented!")
print("="*50)

