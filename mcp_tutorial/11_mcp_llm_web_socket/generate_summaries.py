import csv
import json
import os

# Simple rule-based summary generation (no external LLM API needed)
def generate_patient_summary(patient_data):
    """Generate a comprehensive summary for a patient using their medical data"""
    
    patient_id = patient_data['patient_id']
    name = patient_data['name']
    age = patient_data['age']
    gender = patient_data['gender']
    current_symptoms = patient_data['current_symptoms']
    current_bp = patient_data['current_bp']
    current_sugar = patient_data['current_sugar']
    risk_score = patient_data['risk_score']
    medical_history = patient_data['medical_history']
    current_medications = patient_data['current_medications']
    
    # Parse visit history
    visit_history = json.loads(patient_data['visit_history'])
    num_visits = len(visit_history)
    
    # Build summary
    summary_parts = []
    
    # Basic info
    summary_parts.append(f"{name} is a {age}-year-old {gender} patient")
    
    # Medical history
    if medical_history and medical_history != 'none':
        summary_parts.append(f"with a history of {medical_history}")
    
    # Risk assessment
    risk_level = "high" if float(risk_score) >= 7.0 else "moderate" if float(risk_score) >= 4.0 else "low"
    summary_parts.append(f"currently at {risk_level} risk (score: {risk_score})")
    
    # Current presentation
    summary_parts.append(f"presenting with {current_symptoms}")
    
    # Vitals
    systolic = int(current_bp.split('/')[0])
    bp_status = "elevated blood pressure" if systolic >= 140 else "normal blood pressure"
    sugar_status = "elevated blood sugar" if int(current_sugar) >= 140 else "normal blood sugar"
    summary_parts.append(f"with {bp_status} ({current_bp}) and {sugar_status} ({current_sugar} mg/dL)")
    
    # Medications
    if current_medications and current_medications != 'none':
        summary_parts.append(f"Currently taking {current_medications}")
    else:
        summary_parts.append("Not currently on any medications")
    
    # Visit history summary
    summary_parts.append(f"Has had {num_visits} documented visit(s)")
    
    # Recent trends
    if num_visits >= 2:
        recent_visit = visit_history[-1]
        previous_visit = visit_history[-2]
        
        recent_risk = float(recent_visit['risk_score'])
        previous_risk = float(previous_visit['risk_score'])
        
        if recent_risk > previous_risk:
            trend = "worsening condition"
        elif recent_risk < previous_risk:
            trend = "improving condition"
        else:
            trend = "stable condition"
        
        summary_parts.append(f"showing {trend} over recent visits")
    
    # Clinical recommendations
    if float(risk_score) >= 7.0:
        summary_parts.append("Requires immediate medical attention and close monitoring")
    elif float(risk_score) >= 5.0:
        summary_parts.append("Needs regular follow-up and medication management")
    else:
        summary_parts.append("Routine monitoring recommended")
    
    # Join all parts into a coherent summary
    summary = ". ".join(summary_parts) + "."
    
    return summary


def main():
    """Read patients_data.csv and generate summaries"""
    
    input_file = "patients_data.csv"
    output_file = "patient_summaries.csv"
    
    print(f"Reading patient data from {input_file}...")
    
    summaries_data = []
    
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            patient_id = row['patient_id']
            name = row['name']
            
            print(f"Generating summary for Patient {patient_id}: {name}")
            
            # Generate summary
            summary = generate_patient_summary(row)
            
            summaries_data.append({
                'patient_id': patient_id,
                'name': name,
                'summary': summary
            })
    
    # Write to CSV
    print(f"\nWriting summaries to {output_file}...")
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['patient_id', 'name', 'summary']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerows(summaries_data)
    
    print(f"✓ Successfully created {output_file} with {len(summaries_data)} patient summaries")
    
    # Display sample
    print("\n" + "="*80)
    print("SAMPLE PATIENT SUMMARY:")
    print("="*80)
    sample = summaries_data[0]
    print(f"Patient ID: {sample['patient_id']}")
    print(f"Name: {sample['name']}")
    print(f"Summary: {sample['summary']}")
    print("="*80)


if __name__ == "__main__":
    main()
