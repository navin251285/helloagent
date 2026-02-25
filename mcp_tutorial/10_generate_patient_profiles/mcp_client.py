#!/usr/bin/env python3
"""
MCP Client for Patient Management with Chroma DB Search and Ollama Summary Generation
Workflow:
1. User enters disease/symptom keyword
2. Chroma DB searches and returns top 5 matching patients
3. User selects one patient
4. Ollama generates smart summary from patient health data
5. Summary saved to patient_summaries.csv via MCP server
"""

import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def search_patients_by_disease(session, disease_keyword):
    """Call MCP server to search patients by disease"""
    result = await session.call_tool("search_patients_by_disease", {
        "disease_keyword": disease_keyword
    })
    return result.content[0].text


async def get_patient_summary(session, patient_id):
    """Call MCP server to get patient summary"""
    result = await session.call_tool("get_patient_summary", {
        "patient_id": str(patient_id)
    })
    return result.content[0].text


async def generate_summary(session, patient_id):
    """Call MCP server to generate summary using Ollama"""
    result = await session.call_tool("generate_summary", {
        "patient_id": str(patient_id)
    })
    return result.content[0].text


async def update_summary(session, patient_id, summary):
    """Call MCP server to update and save summary"""
    print(f"\n[CLIENT] Calling update_summary with:")
    print(f"[CLIENT]   Patient ID: {patient_id}")
    print(f"[CLIENT]   Summary length: {len(summary)} chars")
    print(f"[CLIENT]   Summary first 100 chars: {summary[:100]}")
    
    result = await session.call_tool("update_patient_summary", {
        "patient_id": str(patient_id),
        "summary": summary
    })
    
    output = result.content[0].text
    print(f"\n[CLIENT] Server response:")
    print(f"{output}")
    return output


async def main():
    """Main client function"""
    
    print("\n" + "="*100)
    print("🏥 PATIENT SUMMARY GENERATION SYSTEM")
    print("="*100)
    print("\nWorkflow: Disease Search → Select Patient → Generate Summary (via Ollama Phi)")
    print("="*100 + "\n")
    
    # Create server parameters for stdio connection
    server_params = StdioServerParameters(
        command="python",
        args=["mcp_server.py"]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the connection
            await session.initialize()
            
            while True:
                # Step 1: Get disease keyword from user
                print("\n" + "-"*100)
                print("STEP 1: SEARCH PATIENTS BY DISEASE/SYMPTOMS")
                print("-"*100)
                disease_keyword = input("\nEnter disease/symptom keyword (e.g., 'diabetes', 'chest pain', 'hypertension'): ").strip()
                
                if not disease_keyword.lower() or disease_keyword.lower() == 'quit':
                    print("\n✓ Exiting system. Goodbye!")
                    break
                
                # Step 2: Search for patients
                print(f"\nSearching for patients with '{disease_keyword}'...")
                search_results = await search_patients_by_disease(session, disease_keyword)
                
                print("\n" + "="*100)
                print(f"SEARCH RESULTS FOR: {disease_keyword.upper()}")
                print("="*100)
                print(search_results)
                
                # Parse results to extract patient IDs
                lines = search_results.split('\n')
                patients = []
                for line in lines:
                    if line.strip().startswith(('1.', '2.', '3.', '4.', '5.')):
                        # Extract patient ID from the line
                        # Format: "1. ID: 11  | Name: Jerry Rivera | Age: 59 | Symptoms: ..."
                        parts = line.split('|')
                        if len(parts) >= 1:
                            # Extract ID from "1. ID: 11  "
                            id_part = parts[0].split(':')[1].strip()
                            patients.append(id_part)
                
                if not patients:
                    print("\nNo patients found. Please try a different search term.")
                    continue
                
                # Step 3: Get user to select a patient
                print("\n" + "-"*100)
                print("STEP 2: SELECT A PATIENT")
                print("-"*100)
                while True:
                    try:
                        choice = input(f"\nSelect patient number (1-{len(patients)}) or 'b' to go back: ").strip()
                        if choice.lower() == 'b':
                            break
                        choice_num = int(choice)
                        if 1 <= choice_num <= len(patients):
                            selected_patient_id = patients[choice_num - 1]
                            break
                        else:
                            print(f"Please enter a number between 1 and {len(patients)}")
                    except ValueError:
                        print(f"Invalid input. Please enter a number between 1 and {len(patients)}")
                else:
                    continue  # Go back to search if user pressed 'b'
                
                # Step 4: Get patient details
                print("\n" + "="*100)
                print(f"PATIENT DETAILS (ID: {selected_patient_id})")
                print("="*100)
                patient_info = await get_patient_summary(session, selected_patient_id)
                print(patient_info)
                
                # Step 5: Generate summary using Ollama
                print("\n" + "-"*100)
                print("STEP 3: GENERATE SUMMARY USING OLLAMA PHI LLM")
                print("-"*100)
                print("\nGenerating clinical summary using Phi model (this may take 30-60 seconds)...")
                
                generated_summary = await generate_summary(session, selected_patient_id)
                
                print("\n" + "="*100)
                print("GENERATED SUMMARY")
                print("="*100)
                print(generated_summary)
                
                # Step 6: Save summary
                print("\n" + "-"*100)
                print("STEP 4: SAVE SUMMARY")
                print("-"*100)
                confirm = input("\nSave this summary to patient_summaries.csv? (y/n): ").strip().lower()
                
                if confirm == 'y':
                    # Extract just the summary part from the generated text
                    summary_lines = generated_summary.split('\n')
                    summary_start = None
                    
                    # Find where the actual summary starts
                    for i, line in enumerate(summary_lines):
                        if 'Generated Summary for' in line:
                            summary_start = i + 2  # Skip title and blank line
                            break
                    
                    # Extract summary text
                    if summary_start and summary_start < len(summary_lines):
                        summary_text = '\n'.join(summary_lines[summary_start:]).strip()
                    else:
                        summary_text = generated_summary.strip()
                    
                    # Clean up multiple blank lines
                    summary_text = '\n'.join([ln.strip() for ln in summary_text.split('\n') if ln.strip()])
                    
                    print(f"\n📝 Extracted summary ({len(summary_text)} characters):")
                    if summary_text:
                        print(f"   {summary_text[:80]}...")
                        print(f"   [DEBUG] Full extracted text length: {len(summary_text)}")
                        print(f"   [DEBUG] First 100 chars: {summary_text[:100]}")
                    else:
                        print(f"   ⚠️  WARNING: Extracted summary is EMPTY!")
                        print(f"   [DEBUG] This means the extraction logic may have failed")
                    
                    if not summary_text or len(summary_text) == 0:
                        print(f"\n❌ ERROR: Cannot save empty summary. Extraction failed.")
                        print(f"   Generated text was:")
                        print(f"   {generated_summary[:200]}")
                        continue
                    
                    update_result = await update_summary(session, selected_patient_id, summary_text)
                    
                    print("\n" + "="*100)
                    print(update_result)
                    print("="*100 + "\n")
                    print("✓ Summary saved successfully!")
                else:
                    print("\n✗ Summary not saved.")
                
                # Ask if user wants to continue
                print("\n" + "-"*100)
                continue_choice = input("Would you like to search for another patient? (y/n): ").strip().lower()
                if continue_choice != 'y':
                    print("\n✓ Thank you for using the Patient Summary System. Goodbye!")
                    break


if __name__ == "__main__":
    asyncio.run(main())
