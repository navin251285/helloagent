#!/usr/bin/env python3
"""
Interactive Demo: Streaming LLM Summary Generation
Demonstrates token-by-token display as Ollama Phi generates clinical summaries
Complete summaries are saved to CSV
"""

import asyncio
import sys
sys.path.append('/home/navinkumar_25_gmail_com/mcp_tutorial/11_mcp_llm_web_socket')

from mcp_client import MCPWebSocketClient, search_patients_by_disease, get_patient_summary, generate_summary, update_summary


async def main():
    client = None
    try:
        print("\n" + "="*100)
        print("🎯 STREAMING LLM DEMO - Interactive Patient Summary Generation")
        print("="*100)
        print("\nThis demo shows:")
        print("  ✓ Real-time streaming tokens from Ollama Phi model")
        print("  ✓ Complete summary saved to CSV (not partial tokens)")
        print("  ✓ Full WebSocket communication with MCP protocol")
        print("\n" + "="*100 + "\n")
        
        # Connect
        client = MCPWebSocketClient()
        await client.connect()
        
        # Search
        print("\n[STEP 1] 🔍 SEARCH FOR PATIENTS")
        print("-" * 100)
        disease_keyword = input("Enter disease/symptom to search for (e.g., 'diabetes', 'hypertension'): ").strip()
        
        if not disease_keyword:
            print("No keyword entered. Exiting.")
            return
        
        print(f"\nSearching for patients with '{disease_keyword}'...\n")
        search_results = await search_patients_by_disease(client, disease_keyword)
        print(search_results)
        
        # Get patient ID from user
        print("\n[STEP 2] 📋 SELECT PATIENT")
        print("-" * 100)
        patient_id = input("Enter patient ID (1-100): ").strip()
        
        if not patient_id or not patient_id.isdigit():
            print("Invalid patient ID. Exiting.")
            return
        
        # Get patient details
        print(f"\nRetrieving patient details...\n")
        patient_info = await get_patient_summary(client, patient_id)
        print(patient_info)
        
        # Generate with streaming
        print("\n[STEP 3] 🚀 GENERATE SUMMARY WITH STREAMING")
        print("-" * 100)
        print(f"\n⏳ Generating clinical summary with real-time token streaming...")
        print(f"📡 Tokens will appear below as the Phi model generates them (30-60 seconds)\n")
        print("-" * 100)
        print()
        
        generated_summary = await generate_summary(client, patient_id)
        
        print("\n" + "-" * 100)
        print(f"\n✅ STREAMING COMPLETE!\n")
        print("="*100)
        print("FINAL SUMMARY:")
        print("="*100)
        print(generated_summary)
        
        # Save to CSV
        print("\n[STEP 4] 💾 SAVE TO CSV")
        print("-" * 100)
        save = input("\nSave this summary to patient_summaries.csv? (y/n): ").strip().lower()
        
        if save == 'y':
            # Extract summary from generated text
            summary_lines = generated_summary.split('\n')
            summary_start = None
            for i, line in enumerate(summary_lines):
                if 'Generated Summary for' in line:
                    summary_start = i + 2
                    break
            
            if summary_start and summary_start < len(summary_lines):
                summary_text = '\n'.join(summary_lines[summary_start:]).strip()
            else:
                summary_text = generated_summary.strip()
            
            summary_text = '\n'.join([ln.strip() for ln in summary_text.split('\n') if ln.strip()])
            
            print(f"\nSaving {len(summary_text)} character summary...")
            update_result = await update_summary(client, patient_id, summary_text)
            
            print("\n" + "="*100)
            print(update_result)
            print("="*100)
            print("\n✅ Summary saved to patient_summaries.csv!")
        else:
            print("\n✗ Summary not saved.")
        
        print("\n" + "="*100)
        print("✅ DEMO COMPLETE!")
        print("="*100 + "\n")
        
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
