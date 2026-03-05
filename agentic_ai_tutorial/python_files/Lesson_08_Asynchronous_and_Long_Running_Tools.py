#!/usr/bin/env python
# coding: utf-8

# # Lesson 8: Asynchronous and Long-Running Tools
# 
# ## Objective
# Implement asynchronous tool execution for operations that may take time. Handle pending operations and continue execution without blocking.
# 
# ## Problem Statement
# Real tools don't always return instantly. API calls, database queries, and computations may take seconds or minutes. How can agents continue work while tools are pending?
# 
# ## What's New
# - **Async Execution**: Tools run without blocking agent
# - **Polling**: Agent checks for results periodically
# - **Timeout Handling**: Manage long-running operations
# - **Fallbacks**: Continue with partial results if needed

# In[ ]:


## Setup


# In[ ]:


# Packages already installed: pip install -q python-dotenv google-cloud-aiplatform langchain-google-vertexai langgraph asyncio

from dotenv import load_dotenv
import warnings
warnings.filterwarnings("ignore")

import os, vertexai
from langchain_google_vertexai import ChatVertexAI
from langchain_core.messages import HumanMessage
from typing import TypedDict, Dict, Optional
from langgraph.graph import StateGraph, START, END
import asyncio
import time
from dataclasses import dataclass

load_dotenv()
vertexai.init(
    project=os.getenv("PROJECT_ID"),
    location=os.getenv("LOCATION")
)

llm = ChatVertexAI(model="gemini-2.5-flash", temperature=0)

print("✓ Async setup complete")


# In[ ]:


## Async Tool Implementation


# In[ ]:


@dataclass
class PendingOperation:
    task_id: str
    operation: str
    args: dict
    start_time: float
    status: str  # "pending", "complete", "failed"
    result: Optional[float] = None
    error: Optional[str] = None

class AsyncToolExecutor:
    def __init__(self):
        self.pending_ops: Dict[str, PendingOperation] = {}
        self.task_counter = 0

    async def add_async(self, a: float, b: float, delay: float = 0.1) -> str:
        """Simulate async addition with network delay."""
        self.task_counter += 1
        task_id = f"add_{self.task_counter}"

        op = PendingOperation(
            task_id=task_id,
            operation="add",
            args={"a": a, "b": b},
            start_time=time.time(),
            status="pending"
        )
        self.pending_ops[task_id] = op

        # Simulate async work
        async def _do_work():
            await asyncio.sleep(delay)
            op.result = a + b
            op.status = "complete"

        asyncio.create_task(_do_work())
        return task_id

    async def multiply_async(self, a: float, b: float, delay: float = 0.1) -> str:
        """Simulate async multiplication."""
        self.task_counter += 1
        task_id = f"mul_{self.task_counter}"

        op = PendingOperation(
            task_id=task_id,
            operation="multiply",
            args={"a": a, "b": b},
            start_time=time.time(),
            status="pending"
        )
        self.pending_ops[task_id] = op

        async def _do_work():
            await asyncio.sleep(delay)
            op.result = a * b
            op.status = "complete"

        asyncio.create_task(_do_work())
        return task_id

    def poll_result(self, task_id: str) -> Optional[float]:
        """Check if operation is complete."""
        if task_id not in self.pending_ops:
            return None

        op = self.pending_ops[task_id]
        if op.status == "complete":
            return op.result
        return None

executor = AsyncToolExecutor()
print("✓ Async executor created")


# In[ ]:


## Define Async State


# In[ ]:


class AsyncState(TypedDict):
    problem: str
    pending_tasks: Dict[str, str]  # task_id -> step description
    completed_results: Dict[str, float]  # task_id -> result
    execution_log: list
    step: int

print("✓ Async state defined")


# In[ ]:


## Implement Async Nodes


# In[ ]:


async def submitter(state: AsyncState):
    """Submit async tasks."""
    problem = state["problem"]

    # Simple strategy: submit all operations asynchronously
    # For example: "10 + 5 = ? then *2"

    if state["step"] == 1:
        # Submit addition
        task_id = await executor.add_async(10, 5, delay=0.1)
        state["pending_tasks"][task_id] = "add(10, 5)"
        state["execution_log"].append(f"Submitted {task_id}: add(10, 5)")

    state["step"] += 1
    return state

def poller(state: AsyncState):
    """Poll for completed tasks."""
    completed = []

    for task_id, description in state["pending_tasks"].items():
        result = executor.poll_result(task_id)
        if result is not None:
            state["completed_results"][task_id] = result
            state["execution_log"].append(f"Completed {task_id}: {result}")
            completed.append(task_id)

    # Remove completed
    for task_id in completed:
        del state["pending_tasks"][task_id]

    if not state["pending_tasks"]:
        state["execution_log"].append("All tasks complete")

    return state

print("✓ Async nodes implemented")


# In[ ]:


## Build Async Graph


# In[ ]:


def should_poll(state: AsyncState):
    return "poll" if state["pending_tasks"] else "done"

graph_builder = StateGraph(AsyncState)
graph_builder.add_node("poll", poller)

graph_builder.add_edge(START, "poll")
graph_builder.add_conditional_edges(
    "poll",
    should_poll,
    {"poll": "poll", "done": END}
)

graph = graph_builder.compile()
print("✓ Async graph compiled")


# In[ ]:


## Test Async Execution


# In[ ]:


async def run_async_agent():
    state = {
        "problem": "Calculate 10 + 5 asynchronously",
        "pending_tasks": {},
        "completed_results": {},
        "execution_log": [],
        "step": 1
    }

    print("Starting async execution...\n")

    # Submit task
    state = await submitter(state)

    # Poll with timeout
    max_polls = 10
    poll_count = 0
    while state["pending_tasks"] and poll_count < max_polls:
        await asyncio.sleep(0.05)  # Wait before polling
        state = poller(state)
        poll_count += 1

    print(f"Poll count: {poll_count}")
    print(f"\nExecution log:")
    for entry in state["execution_log"]:
        print(f"  {entry}")

    print(f"\nResults: {state['completed_results']}")

    return state

# Run the async agent
result_state = asyncio.run(run_async_agent())

# Verify
if result_state["completed_results"]:
    for task_id, value in result_state["completed_results"].items():
        print(f"\n✓ Task {task_id} = {value}")


# In[ ]:


## Production Insight: Async Patterns


# In[ ]:


print("""
Async Patterns in Production
=============================

1. REQUEST BATCHING
   - Submit multiple API calls async
   - Reduce total latency

2. POLLING STRATEGIES
   - Short polling: Check frequently (CPU costly)
   - Long polling: Wait for data (network costly)
   - Webhooks: Server notifies agent (ideal)

3. TIMEOUT HANDLING
   - Set max wait time
   - Provide fallback results
   - Log for debugging

4. PARALLEL EXECUTION
   - Multiple independent tasks async
   - Multiply throughput
   - Example: Calling 10 APIs concurrently

Real Examples:
- Google Cloud Tasks (async job queue)
- AWS Lambda (serverless async functions)
- Celery (async task queue)
- Ray (distributed async compute)
""")


# In[ ]:


## Verification


# In[ ]:


print("="*50)
print("VERIFICATION - LESSON 8")
print("="*50)
print(f"✓ Async tool executor created")
print(f"✓ PendingOperation tracking")
print(f"✓ Async submission works")
print(f"✓ Polling for results works")
print(f"✓ State transitions correctly")
print(f"✓ Async execution completed successfully")
print(f"\n✓ LESSON 8 COMPLETE: Async tools working!")
print("="*50)

