#!/usr/bin/env python3
"""
Test script to demonstrate LLM streaming functionality
Shows tokens appearing in real-time as Ollama generates the summary
The complete summary is then displayed and saved to CSV
"""

import asyncio
import sys
sys.path.append('/home/navinkumar_25_gmail_com/mcp_tutorial/11_mcp_llm_web_socket')

from mcp_client import MCPWebSocketClient, search_patients_by_disease, generate_summary, update_summary


async def main():
    client = None
    try:
        # Connect to server
        client = MCPWebSocketClient()
        await client.connect()
        
        print("\n" + "="*70)
        print("🎯 STREAMING DEMO: Generate Patient Summary with Real-time Tokens")
        print("="*70)
        
        # Test with Patient ID 25
        patient_id = "25"
        print(f"\n📋 Testing with Patient ID: {patient_id}")
        
        print(f"\n{'='*70}")
        print("Step 1: Generate Summary (with streaming tokens)")
        print(f"{'='*70}")
        
        summary = await generate_summary(client, patient_id)
        
        print(f"\n{'='*70}")
        print("🎉 STREAMING COMPLETE!")
        print(f"{'='*70}")
        print(f"\n📄 Final Summary:\n")
        print(summary)
        
        print(f"\n{'='*70}")
        print("Step 2: Update Summary to CSV")
        print(f"{'='*70}")
        
        result = await update_summary(client, patient_id, summary)
        print(result)
        
        print(f"\n{'='*70}")
        print("✅ STREAMING DEMO COMPLETE!")
        print(f"Summary for Patient {patient_id} has been generated and saved.")
        print(f"{'='*70}\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if client:
            await client.close()


if __name__ == "__main__":
    asyncio.run(main())
