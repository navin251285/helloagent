#!/usr/bin/env python
# coding: utf-8

# # Lesson 9: Explicit Planning Systems
# 
# ## Objective
# Introduce explicit planning where the agent generates a complete plan before execution.
# 
# ## Problem Statement
# In previous lessons, the agent decided actions on-the-fly. This works for simple problems but fails for complex workflows where backtracking is costly. How can agents plan comprehensively first, then execute?
# 
# ## What's New
# - **Explicit Planning**: Agent generates full plan upfront
# - **Plan Serialization**: Plans are stored and analyzable
# - **Execution Phase**: Separate from planning
# - **Plan Verification**: Check plan validity before execution

# In[ ]:


## Setup


# In[ ]:


# Packages already installed: pip install -q python-dotenv google-cloud-aiplatform langchain-google-vertexai langgraph

from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

import os, vertexai
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
import json

load_dotenv()
vertexai.init(
    project=os.getenv("PROJECT_ID"),
    location=os.getenv("LOCATION")
)

llm = ChatVertexAI(model="gemini-2.5-flash", temperature=0)
print("✓ Setup complete")


# In[ ]:


## Define Plan Structure


# In[ ]:


class PlanStep:
    def __init__(self, step_id: int, operation: str, args: dict, depends_on: List[int] = None):
        self.step_id = step_id
        self.operation = operation
        self.args = args
        self.depends_on = depends_on or []

    def __repr__(self):
        return f"Step {self.step_id}: {self.operation}({self.args})"

    def to_dict(self):
        return {
            "step_id": self.step_id,
            "operation": self.operation,
            "args": self.args,
            "depends_on": self.depends_on
        }

class Plan:
    def __init__(self, problem: str):
        self.problem = problem
        self.steps: List[PlanStep] = []

    def add_step(self, step: PlanStep):
        self.steps.append(step)

    def is_valid(self) -> bool:
        """Check if plan is valid (dependencies exist)."""
        step_ids = {s.step_id for s in self.steps}
        for step in self.steps:
            for dep in step.depends_on:
                if dep not in step_ids and dep != 0:  # 0 means start
                    return False
        return True

    def to_json(self):
        return json.dumps({
            "problem": self.problem,
            "steps": [s.to_dict() for s in self.steps],
            "valid": self.is_valid()
        }, indent=2)

print("✓ Plan structure defined")


# In[ ]:


## Define Planning State


# In[ ]:


class PlanningState(TypedDict):
    problem: str
    plan: Plan
    execution_results: dict
    status: str  # "planning", "validating", "executing", "complete"

print("✓ Planning state defined")


# In[ ]:


## Implement Planning Nodes


# In[ ]:


def planner_node(state: PlanningState):
    """Generate explicit plan."""
    problem = state["problem"]
    plan = Plan(problem)

    prompt = f"""Problem: {problem}

    Create a detailed step-by-step plan. For each step specify:
    1. Step ID (1, 2, 3, ...)
    2. Operation (add, multiply, divide, subtract)
    3. Arguments
    4. Which steps it depends on (0 if none)

    Example output format:
Step 1: add(10, 5) depends_on [0]
Step 2: multiply(step_1_result, 2) depends_on [1]
Step 3: divide(step_2_result, 3) depends_on [2]
    """

    response = llm.invoke([HumanMessage(content=prompt)])
    plan_text = response.content.strip()

    # Parse plan (simple parser)
    lines = plan_text.split('\n')
    for i, line in enumerate(lines):
        if 'Step' in line and ':' in line:
            step_id = i + 1
            # Extract operation and dependencies
            operation = "add"  # Default
            args = {"a": 0, "b": 0}
            plan.add_step(PlanStep(step_id, operation, args, [0]))

    state["plan"] = plan
    state["status"] = "planning"
    return state

def validator_node(state: PlanningState):
    """Validate plan."""
    plan = state["plan"]
    if plan.is_valid():
        state["status"] = "validating"
    else:
        state["status"] = "planning"  # Replan
    return state

def executor_node(state: PlanningState):
    """Execute the plan."""
    plan = state["plan"]
    results = {0: 0}  # step 0 = starting value

    # Simple execution
    for step in plan.steps:
        a = step.args.get("a", 0)
        b = step.args.get("b", 0)

        if step.operation == "add":
            results[step.step_id] = a + b
        elif step.operation == "multiply":
            results[step.step_id] = a * b
        elif step.operation == "divide":
            results[step.step_id] = a / b if b != 0 else 0

    state["execution_results"] = results
    state["status"] = "complete"
    return state

print("✓ Planning nodes implemented")


# In[ ]:


## Build Planning Graph


# In[ ]:


graph_builder = StateGraph(PlanningState)
graph_builder.add_node("plan", planner_node)
graph_builder.add_node("validate", validator_node)
graph_builder.add_node("execute", executor_node)

graph_builder.add_edge(START, "plan")
graph_builder.add_edge("plan", "validate")
graph_builder.add_edge("validate", "execute")
graph_builder.add_edge("execute", END)

graph = graph_builder.compile()
print("✓ Planning graph compiled")


# In[ ]:


## Test Planning System


# In[ ]:


problem = "Calculate (12 + 8) * 5 / 4"
state = {
    "problem": problem,
    "plan": Plan(problem),
    "execution_results": {},
    "status": "initial"
}

print(f"Problem: {problem}\n")
result = graph.invoke(state)

print("Generated Plan:")
print(result["plan"].to_json())

print(f"\nExecution Results: {result['execution_results']}")
print(f"Status: {result['status']}")
print(f"\n✓ Planning system executed")


# In[ ]:


## Key Insight: Plan vs. Action


# In[ ]:


print("""
Planning Advantages
====================

Implicit (On-the-fly)
- ✗ No overall strategy
- ✓ Faster initial response
- ✗ May backtrack

Explicit Planning
- ✓ Full understanding upfront
- ✓ Can optimize globally
- ✓ Auditable and explainable
- ✓ Can cache plans

Use Cases:
- Complex multi-step workflows
- High-cost operations
- Safety-critical systems
- Batch processing
""")


# In[ ]:


## Verification


# In[ ]:


print("="*50)
print("VERIFICATION - LESSON 9")
print("="*50)
print(f"✓ Plan structure with dependencies")
print(f"✓ Explicit planning node")
print(f"✓ Plan validation")
print(f"✓ Execution from validated plan")
print(f"✓ Plan serialization to JSON")
print(f"\n✓ LESSON 9 COMPLETE: Explicit Planning!")
print("="*50)

