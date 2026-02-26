#!/usr/bin/env python3
"""
Quick demo of enhanced WebSocket communication logging
Shows all the detailed logs visible on the client
"""
import asyncio
import sys
sys.path.insert(0, '.')

from mcp_client import MCPWebSocketClient


async def demo_enhanced_logging():
    """Demonstrate the enhanced WebSocket communication logs"""
    print("=" * 80)
    print("📡 ENHANCED WEBSOCKET COMMUNICATION DEMO")
    print("=" * 80)
    print("\nThis demo shows all WebSocket communication details you'll now see:")
    print("  • Connection establishment")
    print("  • Request/response tracking")
    print("  • Tool call progress")
    print("  • Ollama LLM inference status")
    print("=" * 80)
    
    client = MCPWebSocketClient()
    
    try:
        # Connect - you'll see detailed connection logs
        await client.connect()
        
        # Search - you'll see request/response logs
        print("\n" + "▼" * 80)
        print("DEMO: Searching for 'diabetes'")
        print("▼" * 80)
        
        result = await client.call_tool("search_patients_by_disease", {
            "disease_keyword": "diabetes"
        })
        
        # Show first result
        search_text = result[0]["text"]
        print("\n📄 Search Result Preview:")
        print(search_text.split('\n')[0])  # Just the header
        print(search_text.split('\n')[2])  # First patient
        
        print("\n" + "=" * 80)
        print("✅ DEMO COMPLETE")
        print("=" * 80)
        print("\nNow when you run the client, you'll see:")
        print("  [WebSocket →] Sending: <method>")
        print("  [WebSocket →] Params: <parameters>")
        print("  [WebSocket ←] Waiting for response...")
        print("  [WebSocket ←] Response received: <method> → Success")
        print("  [Tool Call] <tool_name>(...)")
        print("  [Tool Result] <result summary>")
        print("  [Progress] <current operation>")
        print("\nAll WebSocket communication is now visible! 🎉")
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(demo_enhanced_logging())
