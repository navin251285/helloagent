#!/usr/bin/env python3
"""
MCP HTTP Client - Multi-Tool Orchestration Demo
Demonstrates calling multiple tools in sequence with shared state
Uses HTTP JSON-RPC instead of stdio
"""

import json
import urllib.request
from typing import Any, Dict


class MultiToolOrchestrationHTTPClient:
    """HTTP client that orchestrates multiple MCP tool calls"""
    
    def __init__(self, server_url: str = "http://127.0.0.1:3000"):
        self.server_url = server_url
        self.results = {}
    
    def call_server(self, method: str, params: Dict[str, Any] = None) -> Dict:
        """Make HTTP POST request to MCP server"""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": method,
            "params": params or {}
        }
        
        data = json.dumps(request).encode("utf-8")
        req = urllib.request.Request(self.server_url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            body = response.read().decode("utf-8")
        
        return json.loads(body)
    
    def list_tools(self):
        """List all available tools"""
        print("=" * 60)
        print("AVAILABLE TOOLS")
        print("=" * 60)
        
        response = self.call_server("list_tools")
        tools = response.get("result", [])
        
        for tool in tools:
            print(f"\n📊 {tool['name']}")
            print(f"   Description: {tool['description']}")
            print(f"   Parameters: {', '.join(tool['parameters'])}")
        
        print("\n" + "=" * 60 + "\n")
    
    def call_tool(self, tool_name: str, arguments: dict, step_number: int, step_description: str):
        """Call a tool and display results"""
        print(f"\n{'─' * 60}")
        print(f"STEP {step_number}: {step_description}")
        print(f"{'─' * 60}")
        print(f"Tool: {tool_name}")
        print(f"Arguments: {arguments}")
        print()
        
        response = self.call_server(
            "call_tool",
            {"name": tool_name, "arguments": arguments}
        )
        
        result_data = response.get("result", {})
        
        print(f"✓ Result: {result_data['result']}")
        print(f"  Version: {result_data['version']}")
        print(f"  Shared State: {result_data['shared_state']}")
        
        # Store result for later use
        self.results[tool_name] = result_data['result']
        
        return result_data['result']
    
    def run_orchestration_demo(self):
        """Run the complete multi-tool orchestration workflow"""
        print("\n" + "=" * 60)
        print("MULTI-TOOL ORCHESTRATION WORKFLOW")
        print("=" * 60)
        print("Demonstrating: Inter-tool dependencies and shared state")
        print("=" * 60)
        
        # Step 1: Sum
        sum_result = self.call_tool(
            "tool_sum",
            {"a": 3, "b": 5},
            1,
            "Calculate Sum"
        )
        
        # Step 2: Multiply (uses last_sum from shared state)
        multiply_result = self.call_tool(
            "tool_multiply",
            {"a": 2, "b": 4},
            2,
            "Multiply (with dependency on last_sum)"
        )
        
        # Step 3: Subtract
        subtract_result = self.call_tool(
            "tool_subtract",
            {"a": 20, "b": 5},
            3,
            "Subtract"
        )
        
        # Step 4: Divide
        divide_result = self.call_tool(
            "tool_divide",
            {"a": 16, "b": 4},
            4,
            "Divide"
        )
        
        # Step 5: Average (using all previous results)
        average_result = self.call_tool(
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


    def interactive_mode(self):
        """Run in interactive mode with menu"""
        print("\n" + "=" * 60)
        print("INTERACTIVE MODE - CALCULATOR")
        print("=" * 60)
        print("Works like a calculator with running accumulator.")
        print("Enter '0' for first number to use current accumulator.")
        print("Type 'quit' or 'exit' to stop and see final result.\n")
        
        while True:
            print("\n" + "─" * 60)
            print("MENU:")
            print("─" * 60)
            print("1. tool_sum - Sum two numbers")
            print("2. tool_multiply - Multiply (enter 0 for first number to use accumulator)")
            print("3. tool_subtract - Subtract (enter 0 for first number to use accumulator)")
            print("4. tool_divide - Divide (enter 0 for first number to use accumulator)")
            print("5. tool_average - Average a list of numbers")
            print("6. list_tools - Show all available tools")
            print("7. show_state - Show current accumulator and history")
            print("8. demo - Run the full orchestration demo")
            print("9. quit - Exit and show final result")
            print("─" * 60)
            
            choice = input("\nSelect an option (1-9): ").strip()
            
            if choice in ['9', 'quit', 'exit', 'q']:
                # Show final result
                print("\n" + "=" * 60)
                print("FINAL RESULT")
                print("=" * 60)
                try:
                    response = self.call_server("call_tool", {"name": "get_state", "arguments": {}})
                    shared_state = response.get("result", {}).get("shared_state", {})
                    accumulator = shared_state.get("accumulator", 0)
                    history = shared_state.get("history", [])
                    
                    print(f"\nFinal Accumulator Value: {accumulator}\n")
                    
                    if history:
                        print("Operation History:")
                        for i, op in enumerate(history, 1):
                            print(f"  {i}. {op}")
                    else:
                        print("No operations performed.")
                    
                    print("=" * 60)
                except:
                    pass
                    
                print("✓ Goodbye!\n")
                break
            
            try:
                if choice == '1':
                    a = float(input("Enter first number (a): "))
                    b = float(input("Enter second number (b): "))
                    result = self.call_tool("tool_sum", {"a": a, "b": b}, 0, f"Sum {a} + {b}")
                    
                elif choice == '2':
                    a = float(input("Enter first number (a, 0=use accumulator): "))
                    b = float(input("Enter second number (b): "))
                    result = self.call_tool("tool_multiply", {"a": a, "b": b}, 0, f"Multiply {a} * {b}")
                    
                elif choice == '3':
                    a = float(input("Enter first number (a, 0=use accumulator): "))
                    b = float(input("Enter second number (b): "))
                    result = self.call_tool("tool_subtract", {"a": a, "b": b}, 0, f"Subtract {a} - {b}")
                    
                elif choice == '4':
                    a = float(input("Enter numerator (a, 0=use accumulator): "))
                    b = float(input("Enter denominator (b): "))
                    result = self.call_tool("tool_divide", {"a": a, "b": b}, 0, f"Divide {a} / {b}")
                    
                elif choice == '5':
                    numbers_str = input("Enter numbers separated by commas (e.g., 1,2,3,4): ")
                    numbers = [float(x.strip()) for x in numbers_str.split(',')]
                    result = self.call_tool("tool_average", {"numbers": numbers}, 0, f"Average of {numbers}")
                    
                elif choice == '6':
                    self.list_tools()
                    
                elif choice == '7':
                    response = self.call_server("call_tool", {"name": "tool_sum", "arguments": {"a": 0, "b": 0}})
                    shared_state = response.get("result", {}).get("shared_state", {})
                    accumulator = shared_state.get("accumulator", 0)
                    history = shared_state.get("history", [])
                    
                    print("\n" + "─" * 60)
                    print(f"📊 Current Accumulator: {accumulator}")
                    print("─" * 60)
                    if history:
                        print("Operation History:")
                        for i, op in enumerate(history, 1):
                            print(f"  {i}. {op}")
                    else:
                        print("  (no operations yet)")
                    print("─" * 60)
                    
                elif choice == '8':
                    self.run_orchestration_demo()
                    
                else:
                    print("❌ Invalid choice. Please select 1-9.")
                    
            except ValueError as e:
                print(f"❌ Invalid input: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")


def main():
    """Run the demo"""
    print("=" * 60)
    print("Connecting to MCP HTTP Server...")
    print("=" * 60)
    
    try:
        client = MultiToolOrchestrationHTTPClient()
        print("✓ Connected to http://127.0.0.1:3000\n")
        
        # Ask user what mode they want
        print("Choose mode:")
        print("1. Interactive mode (call tools one by one)")
        print("2. Demo mode (run full orchestration workflow)")
        
        mode = input("\nSelect mode (1 or 2): ").strip()
        
        if mode == '1':
            client.interactive_mode()
        else:
            # List available tools
            client.list_tools()
            
            # Run orchestration workflow
            client.run_orchestration_demo()
        
    except urllib.error.URLError as e:
        print(f"❌ Error: Cannot connect to server")
        print(f"   Make sure the server is running: python mcp_server_http.py")
        print(f"   Details: {e}")
    except KeyboardInterrupt:
        print("\n\n✓ Interrupted by user. Goodbye!\n")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
