#!/usr/bin/env python3
"""
Test script to verify calculator accumulator behavior
Tests:
1. 10 + 5 = 15
2. 0 * 2 = 30 (uses accumulator 15)
3. 0 - 5 = 25 (uses accumulator 30)
4. get_state to check final result (should be 25 with 3 operations in history)
"""

import urllib.request
import json

def call_tool(name, arguments):
    """Call a tool via HTTP"""
    url = "http://127.0.0.1:3000"
    request_data = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "call_tool",
        "params": {
            "name": name,
            "arguments": arguments
        }
    }
    
    req = urllib.request.Request(
        url,
        data=json.dumps(request_data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    
    with urllib.request.urlopen(req) as response:
        result = json.loads(response.read().decode('utf-8'))
        return result["result"]

def main():
    print("Testing Calculator Accumulator\n")
    print("=" * 60)
    
    # Test 1: 10 + 5 = 15
    print("1. Testing: 10 + 5")
    result = call_tool("tool_sum", {"a": 10, "b": 5})
    print(f"   Result: {result['result']}")
    print(f"   Accumulator: {result['shared_state']['accumulator']}")
    print(f"   History: {result['shared_state']['history']}")
    print()
    
    # Test 2: 0 * 2 (should use accumulator 15)
    print("2. Testing: 0 * 2 (should multiply accumulator by 2)")
    result = call_tool("tool_multiply", {"a": 0, "b": 2})
    print(f"   Result: {result['result']}")
    print(f"   Accumulator: {result['shared_state']['accumulator']}")
    print(f"   History: {result['shared_state']['history']}")
    print()
    
    # Test 3: 0 - 5 (should subtract 5 from accumulator)
    print("3. Testing: 0 - 5 (should subtract 5 from accumulator)")
    result = call_tool("tool_subtract", {"a": 0, "b": 5})
    print(f"   Result: {result['result']}")
    print(f"   Accumulator: {result['shared_state']['accumulator']}")
    print(f"   History: {result['shared_state']['history']}")
    print()
    
    # Test 4: get_state (should not add to history)
    print("4. Testing: get_state (should NOT pollute history)")
    result = call_tool("get_state", {})
    print(f"   Result: {result['result']}")
    print(f"   Accumulator: {result['shared_state']['accumulator']}")
    print(f"   History: {result['shared_state']['history']}")
    print()
    
    print("=" * 60)
    print("FINAL RESULT")
    print("=" * 60)
    print(f"Final Accumulator: {result['shared_state']['accumulator']}")
    print(f"Number of Operations: {len(result['shared_state']['history'])}")
    print("\nOperation History:")
    for i, op in enumerate(result['shared_state']['history'], 1):
        print(f"  {i}. {op}")
    print("=" * 60)
    
    # Verify
    expected_accumulator = 25
    expected_operations = 3
    actual_accumulator = result['shared_state']['accumulator']
    actual_operations = len(result['shared_state']['history'])
    
    print("\nVerification:")
    if actual_accumulator == expected_accumulator:
        print(f"✓ Accumulator is correct: {actual_accumulator}")
    else:
        print(f"✗ Accumulator mismatch: expected {expected_accumulator}, got {actual_accumulator}")
    
    if actual_operations == expected_operations:
        print(f"✓ History count is correct: {actual_operations}")
    else:
        print(f"✗ History count mismatch: expected {expected_operations}, got {actual_operations}")

if __name__ == "__main__":
    main()
