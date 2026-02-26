import random
import csv
import json
from datetime import datetime, timedelta

# Sample data for realistic generation
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Barbara", "David", "Elizabeth", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley",
    "Steven", "Kimberly", "Paul", "Emily", "Andrew", "Donna", "Joshua", "Michelle",
    "Kenneth", "Dorothy", "Kevin", "Carol", "Brian", "Amanda", "George", "Melissa",
    "Edward", "Deborah", "Ronald", "Stephanie", "Timothy", "Rebecca", "Jason", "Sharon",
    "Jeffrey", "Laura", "Ryan", "Cynthia", "Jacob", "Kathleen", "Gary", "Amy",
    "Nicholas", "Shirley", "Eric", "Angela", "Jonathan", "Helen", "Stephen", "Anna",
    "Larry", "Brenda", "Justin", "Pamela", "Scott", "Nicole", "Brandon", "Emma",
    "Benjamin", "Samantha", "Samuel", "Katherine", "Raymond", "Christine", "Gregory", "Debra",
    "Frank", "Rachel", "Alexander", "Catherine", "Patrick", "Carolyn", "Raymond", "Janet",
    "Jack", "Ruth", "Dennis", "Maria", "Jerry", "Heather", "Tyler", "Diane"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson"
]

SYMPTOMS_LIST = [
    "chest pain", "shortness of breath", "dizziness", "fatigue", "nausea",
    "headache", "palpitations", "sweating", "weakness", "numbness in limbs",
    "blurred vision", "confusion", "difficulty breathing", "abdominal pain",
    "back pain", "joint pain", "swelling in legs", "cough", "fever", "chills"
]

MEDICAL_CONDITIONS = [
    "hypertension", "diabetes", "high cholesterol", "obesity", "heart disease",
    "stroke history", "kidney disease", "liver problems", "thyroid disorder",
    "asthma", "arthritis", "depression", "anxiety", "sleep apnea"
]

MEDICATIONS = [
    "metformin", "lisinopril", "amlodipine", "atorvastatin", "metoprolol",
    "losartan", "omeprazole", "albuterol", "gabapentin", "hydrochlorothiazide",
    "levothyroxine", "ibuprofen", "aspirin", "insulin", "warfarin"
]

VISIT_OUTCOMES = [
    "prescribed medication and advised rest",
    "recommended lifestyle changes and diet modification",
    "ordered additional tests and follow-up in 2 weeks",
    "adjusted medication dosage",
    "referred to specialist for further evaluation",
    "emergency treatment provided, condition stabilized",
    "blood pressure controlled with medication",
    "blood sugar levels monitored and managed",
    "physical therapy recommended",
    "scheduled for surgery consultation"
]


def calculate_symptom_score(symptoms):
    """Calculate symptom severity score (0-10)"""
    symptom_weights = {
        "chest pain": 10,
        "shortness of breath": 9,
        "difficulty breathing": 9,
        "confusion": 8,
        "numbness in limbs": 8,
        "palpitations": 7,
        "dizziness": 7,
        "blurred vision": 6,
        "sweating": 5,
        "nausea": 5,
        "weakness": 5,
        "fatigue": 4,
        "headache": 4,
        "abdominal pain": 6,
        "back pain": 3,
        "joint pain": 3,
        "swelling in legs": 5,
        "cough": 3,
        "fever": 6,
        "chills": 5
    }
    
    symptom_list = [s.strip() for s in symptoms.split(",")]
    if not symptom_list:
        return 0
    
    total_score = sum(symptom_weights.get(s, 3) for s in symptom_list)
    avg_score = total_score / len(symptom_list)
    return min(10, avg_score)


def calculate_bp_risk(bp_str):
    """Calculate blood pressure risk score (0-10)"""
    try:
        systolic, diastolic = map(int, bp_str.split("/"))
        
        if systolic >= 180 or diastolic >= 120:
            return 10
        elif systolic >= 160 or diastolic >= 100:
            return 8
        elif systolic >= 140 or diastolic >= 90:
            return 6
        elif systolic >= 130 or diastolic >= 85:
            return 4
        elif systolic >= 120 or diastolic >= 80:
            return 2
        else:
            return 0
    except:
        return 0


def calculate_sugar_risk(sugar_level):
    """Calculate blood sugar risk score (0-10)"""
    if sugar_level >= 300:
        return 10
    elif sugar_level >= 250:
        return 8
    elif sugar_level >= 200:
        return 7
    elif sugar_level >= 180:
        return 6
    elif sugar_level >= 140:
        return 4
    elif sugar_level >= 126:
        return 3
    elif sugar_level >= 100:
        return 1
    else:
        return 0


def calculate_age_factor(age):
    """Calculate age risk factor (0-10)"""
    if age >= 80:
        return 10
    elif age >= 70:
        return 8
    elif age >= 60:
        return 6
    elif age >= 50:
        return 4
    elif age >= 40:
        return 2
    else:
        return 1


def calculate_risk_score(symptom_score, bp_risk, sugar_risk, age_factor):
    """
    Calculate final risk score using the formula:
    (0.4 × symptom_score) + (0.3 × bp_risk) + (0.2 × sugar_risk) + (0.1 × age_factor)
    """
    risk_score = (0.4 * symptom_score) + (0.3 * bp_risk) + (0.2 * sugar_risk) + (0.1 * age_factor)
    return round(risk_score, 2)


def generate_bp(age, has_hypertension=False):
    """Generate realistic blood pressure"""
    if has_hypertension or age > 60:
        systolic = random.randint(130, 180)
        diastolic = random.randint(85, 110)
    elif age > 40:
        systolic = random.randint(120, 150)
        diastolic = random.randint(80, 95)
    else:
        systolic = random.randint(100, 135)
        diastolic = random.randint(60, 85)
    return f"{systolic}/{diastolic}"


def generate_sugar(age, has_diabetes=False):
    """Generate realistic blood sugar level"""
    if has_diabetes:
        return random.randint(140, 300)
    elif age > 50 and random.random() < 0.3:
        return random.randint(110, 160)
    else:
        return random.randint(70, 125)


def generate_patient_visit(patient_id, visit_number, total_visits, base_age):
    """Generate a single patient visit record"""
    # Calculate visit date (going backwards from today)
    days_ago = (total_visits - visit_number) * random.randint(30, 90)
    visit_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    
    # Adjust age for past visits
    years_ago = days_ago // 365
    age = base_age - years_ago
    
    # Generate symptoms (2-4 random symptoms)
    num_symptoms = random.randint(2, 4)
    symptoms = ", ".join(random.sample(SYMPTOMS_LIST, num_symptoms))
    
    # Determine if patient has chronic conditions
    has_hypertension = random.random() < 0.3
    has_diabetes = random.random() < 0.25
    
    # Generate vital signs
    bp = generate_bp(age, has_hypertension)
    sugar = generate_sugar(age, has_diabetes)
    
    # Generate medical history
    conditions = []
    if has_hypertension:
        conditions.append("hypertension")
    if has_diabetes:
        conditions.append("diabetes")
    if age > 50 and random.random() < 0.4:
        conditions.append(random.choice(["high cholesterol", "obesity", "arthritis"]))
    
    medical_history = ", ".join(conditions) if conditions else "none"
    
    # Current medications
    num_medications = len(conditions) + random.randint(0, 2)
    medications = ", ".join(random.sample(MEDICATIONS, min(num_medications, 5))) if num_medications > 0 else "none"
    
    # Calculate scores
    symptom_score = calculate_symptom_score(symptoms)
    bp_risk = calculate_bp_risk(bp)
    sugar_risk = calculate_sugar_risk(sugar)
    age_factor = calculate_age_factor(age)
    
    # Base score is the sum of primary risks
    base_score = round((symptom_score + bp_risk + sugar_risk) / 3, 2)
    
    # Risk score using the weighted formula
    risk_score = calculate_risk_score(symptom_score, bp_risk, sugar_risk, age_factor)
    
    # Generate outcome
    outcome = random.choice(VISIT_OUTCOMES)
    
    # Generate doctor's notes
    notes = f"Patient presented with {symptoms}. "
    if medical_history != "none":
        notes += f"History of {medical_history}. "
    notes += f"Current medications: {medications}. "
    notes += f"BP: {bp}, Blood Sugar: {sugar}mg/dL. "
    notes += f"{outcome}."
    
    return {
        "visit_date": visit_date,
        "symptoms": symptoms,
        "bp": bp,
        "sugar": sugar,
        "medical_history": medical_history,
        "current_medications": medications,
        "symptom_score": round(symptom_score, 2),
        "bp_risk": bp_risk,
        "sugar_risk": sugar_risk,
        "age_factor": age_factor,
        "base_score": base_score,
        "risk_score": risk_score,
        "outcome": outcome,
        "notes": notes
    }


def generate_patient_profile(patient_id):
    """Generate a complete patient profile with history"""
    # Generate name
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    name = f"{first_name} {last_name}"
    
    # Generate demographics
    age = random.randint(18, 85)
    gender = random.choice(["Male", "Female"])
    
    # Generate visit history (2-5 visits)
    num_visits = random.randint(2, 5)
    visits = []
    
    for visit_num in range(1, num_visits + 1):
        visit = generate_patient_visit(patient_id, visit_num, num_visits, age)
        visits.append(visit)
    
    # Latest visit is the current profile
    latest_visit = visits[-1]
    
    return {
        "patient_id": patient_id,
        "name": name,
        "age": age,
        "gender": gender,
        "current_symptoms": latest_visit["symptoms"],
        "current_bp": latest_visit["bp"],
        "current_sugar": latest_visit["sugar"],
        "base_score": latest_visit["base_score"],
        "risk_score": latest_visit["risk_score"],
        "medical_history": latest_visit["medical_history"],
        "current_medications": latest_visit["current_medications"],
        "visit_history": visits
    }


def save_to_csv(patients, filename="patients_data.csv"):
    """Save patient data to CSV file"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'patient_id', 'name', 'age', 'gender', 'current_symptoms', 'current_bp',
            'current_sugar', 'base_score', 'risk_score', 'medical_history',
            'current_medications', 'visit_history'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for patient in patients:
            # Convert visit history to JSON string for CSV
            patient_data = patient.copy()
            patient_data['visit_history'] = json.dumps(patient_data['visit_history'])
            writer.writerow(patient_data)
    
    print(f"✓ Saved {len(patients)} patient profiles to {filename}")


def save_detailed_csv(patients, filename="patients_detailed.csv"):
    """Save detailed patient visit data to CSV (one row per visit)"""
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = [
            'patient_id', 'name', 'age', 'gender', 'visit_date', 'symptoms', 'bp',
            'sugar', 'medical_history', 'current_medications', 'symptom_score',
            'bp_risk', 'sugar_risk', 'age_factor', 'base_score', 'risk_score',
            'outcome', 'notes'
        ]
        
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        total_visits = 0
        for patient in patients:
            for visit in patient['visit_history']:
                row = {
                    'patient_id': patient['patient_id'],
                    'name': patient['name'],
                    'age': patient['age'],
                    'gender': patient['gender']
                }
                row.update(visit)
                writer.writerow(row)
                total_visits += 1
        
        print(f"✓ Saved {total_visits} patient visits to {filename}")


def main():
    print("Generating 100 patient profiles...")
    patients = []
    
    for i in range(1, 101):
        patient = generate_patient_profile(i)
        patients.append(patient)
        if i % 20 == 0:
            print(f"  Generated {i} patients...")
    
    print(f"\n✓ Generated {len(patients)} patient profiles")
    
    # Save to CSV files
    save_to_csv(patients, "patients_data.csv")
    save_detailed_csv(patients, "patients_detailed.csv")
    
    # Save to JSON for reference
    with open("patients_data.json", 'w', encoding='utf-8') as f:
        json.dump(patients, f, indent=2)
    print(f"✓ Saved patient profiles to patients_data.json")
    
    # Print sample patient
    print("\n" + "="*80)
    print("SAMPLE PATIENT PROFILE:")
    print("="*80)
    sample = patients[0]
    print(f"Patient ID: {sample['patient_id']}")
    print(f"Name: {sample['name']}")
    print(f"Age: {sample['age']}")
    print(f"Gender: {sample['gender']}")
    print(f"Current Symptoms: {sample['current_symptoms']}")
    print(f"Blood Pressure: {sample['current_bp']}")
    print(f"Blood Sugar: {sample['current_sugar']}")
    print(f"Base Score: {sample['base_score']}")
    print(f"Risk Score: {sample['risk_score']}")
    print(f"Medical History: {sample['medical_history']}")
    print(f"Current Medications: {sample['current_medications']}")
    print(f"\nVisit History ({len(sample['visit_history'])} visits):")
    for i, visit in enumerate(sample['visit_history'], 1):
        print(f"\n  Visit {i} ({visit['visit_date']}):")
        print(f"    Symptoms: {visit['symptoms']}")
        print(f"    BP: {visit['bp']}, Sugar: {visit['sugar']}")
        print(f"    Risk Score: {visit['risk_score']}")
        print(f"    Outcome: {visit['outcome']}")
    print("="*80)


if __name__ == "__main__":
    main()
