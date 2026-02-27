#!/usr/bin/env python3
"""
MCP Client - Multi-Tool Orchestration Demo
Demonstrates calling multiple tools in sequence with shared state
"""

import asyncio
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run_orchestration_demo():
    """Run the complete multi-tool orchestration workflow"""
    
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"],
    )
    
    print("=" * 60)
    print("Connecting to MCP Server...")
    print("=" * 60)
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize session
            await session.initialize()
            print("✓ Connected to MCP Server\n")
            
            # List available tools
            print("=" * 60)
            print("AVAILABLE TOOLS")
            print("=" * 60)
            
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"\n📊 {tool.name}")
                print(f"   Description: {tool.description}")
            
            print("\n" + "=" * 60 + "\n")
            
            # Start orchestration workflow
            print("\n" + "=" * 60)
            print("MULTI-TOOL ORCHESTRATION WORKFLOW")
            print("=" * 60)
            print("Demonstrating: Inter-tool dependencies and shared state")
            print("=" * 60)
            
            results = {}
            
            # Helper function to call tool
            async def call_tool(tool_name, arguments, step_number, step_description):
                print(f"\n{'─' * 60}")
                print(f"STEP {step_number}: {step_description}")
                print(f"{'─' * 60}")
                print(f"Tool: {tool_name}")
                print(f"Arguments: {arguments}")
                print()
                
                result = await session.call_tool(tool_name, arguments)
                
                # Parse result
                result_text = result.content[0].text
                result_data = json.loads(result_text)
                
                print(f"✓ Result: {result_data['result']}")
                print(f"  Version: {result_data['version']}")
                print(f"  Shared State: {result_data['shared_state']}")
                
                results[tool_name] = result_data['result']
                return result_data['result']
            
            # Step 1: Sum
            sum_result = await call_tool(
                "tool_sum",
                {"a": 3, "b": 5},
                1,
                "Calculate Sum"
            )
            
            # Step 2: Multiply (uses last_sum from shared state)
            multiply_result = await call_tool(
                "tool_multiply",
                {"a": 2, "b": 4},
                2,
                "Multiply (with dependency on last_sum)"
            )
            
            # Step 3: Subtract
            subtract_result = await call_tool(
                "tool_subtract",
                {"a": 20, "b": 5},
                3,
                "Subtract"
            )
            
            # Step 4: Divide
            divide_result = await call_tool(
                "tool_divide",
                {"a": 16, "b": 4},
                4,
                "Divide"
            )
            
            # Step 5: Average (using all previous results)
            average_result = await call_tool(
                "tool_average",
                {"numbers": [sum_result, multiply_result, subtract_result, divide_result]},
                5,
                "Calculate Average of all results"
            )
            
            # Final Summary
            print("\n" + "=" * 60)
            print("ORCHESTRATION COMPLETE - FINAL SUMMARY")
            print("=" * 60)
            print(f"Step 1: Sum           = {sum_result}")
            print(f"Step 2: Multiply      = {multiply_result}")
            print(f"Step 3: Subtract      = {subtract_result}")
            print(f"Step 4: Divide        = {divide_result}")
            print(f"Step 5: Average       = {average_result}")
            print("=" * 60)
            print()
            
            # Explain the inter-tool dependency
            print("📌 KEY OBSERVATION:")
            print(f"   tool_multiply used last_sum ({sum_result}) from shared state")
            print(f"   Expected: 2 * 4 = 8")
            print(f"   Actual: (2 + {sum_result}) * 4 = {multiply_result}")
            print(f"   This demonstrates inter-tool dependency!")
            print("=" * 60 + "\n")
    
    print("✓ Disconnected from MCP Server\n")


async def main():
    """Run the demo"""
    try:
        await run_orchestration_demo()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
