# Data Generation Module - `generate_patients.py`

## 📌 Purpose
Generate a realistic dataset of 100 patient profiles with health metrics for testing and training the semantic search system.

## 🎯 What It Does

Creates `patients_data.csv` with 100 rows containing:
- **Demographics:** ID, name, age, gender
- **Health Metrics:** Blood pressure, blood sugar, risk score
- **Clinical Data:** Current symptoms, medications, medical history, visit history

## 📊 Data Schema

```csv
patient_id,name,age,gender,current_symptoms,current_bp,current_sugar,
current_medications,risk_score,medical_history,visit_history

1,Justin Cox,42,Male,"weakness, headache",130/85,95,"Aspirin, Lisinopril",
3.2,"Hypertension, Obesity","2024-12: Routine checkup, 2024-10: BP elevated"
```

## 🔧 How It Works

### Step 1: Generate Demographics
```python
from faker import Faker
fake = Faker()

for patient_id in range(1, 101):
    name = fake.name()
    age = random(25, 85)
    gender = choice(['Male', 'Female'])
```

### Step 2: Select Symptoms
```python
Common symptom pools:
- Cardiac: "chest pain", "palpitations", "shortness of breath"
- Metabolic: "elevated blood sugar", "elevated BP", "fatigue"
- Respiratory: "cough", "wheezing", "breathing difficulty"
- Neurological: "confusion", "headache", "dizziness"

Each patient gets 3-4 random symptoms
```

### Step 3: Generate Health Metrics
```python
# Blood Pressure (normal ~120/80)
systolic = normal_distribution(120, 20)
diastolic = normal_distribution(80, 12)

# Blood Sugar (normal ~100-125 fasting)
blood_sugar = normal_distribution(120, 40)

# Risk Score (0-10, based on metrics)
risk_score = (
    (systolic - 120) / 30 +
    (blood_sugar - 120) / 80
) / 2
```

### Step 4: Assign Medical History
```python
Common conditions:
- "Hypertension" (40% of patients)
- "Type 2 Diabetes" (35%)
- "Obesity" (45%)
- "High Cholesterol" (30%)
- "Asthma" (20%)

Combine with medications:
- Hypertension → Lisinopril, Metoprolol
- Diabetes → Metformin, Insulin
- Asthma → Albuterol, Budesonide
```

### Step 5: Create Visit History
```python
Generate 2-4 random visit dates with notes:
"2024-12: Routine checkup, BP elevated"
"2024-10: Follow-up for diabetes management"
"2024-08: Lab results reviewed"
```

## 📤 Output

**File:** `patients_data.csv` (in same directory)

**Columns:**
1. `patient_id` - 1 to 100
2. `name` - Generated random name (via Faker)
3. `age` - 25 to 85
4. `gender` - Male/Female
5. `current_symptoms` - 3-4 symptoms, comma-separated
6. `current_bp` - Format: "XXX/XX mmHg"
7. `current_sugar` - Format: "XXX mg/dL"
8. `current_medications` - Comma-separated medication names
9. `risk_score` - 0.0-10.0, calculated from metrics
10. `medical_history` - Comma-separated conditions
11. `visit_history` - Date-based visit notes

## 🚀 Running the Script

```bash
cd /path/to/10_generate_patient_profiles
python3 generate_patients.py

# Output:
# ✓ Generated 100 patient profiles
# ✓ Saved to patients_data.csv
# ✓ File size: ~50KB
```

## ✅ Validation Checks

The script verifies:
- All 100 rows have unique patient IDs (1-100)
- No missing values in required columns
- Age ranges 25-85
- BP format is valid (XXX/XX)
- Risk score is 0-10
- Symptoms and medications are non-empty

## 🔄 Dependencies

```python
faker           # Random data generation
pandas          # CSV writing
csv             # CSV utilities
random          # Random selection
```

## 📝 Example Records

```
ID=1:  Justin Cox, 42M, "weakness, headache", BP: 130/85, Sugar: 95
       Risk: 3.2, Medications: Aspirin, Lisinopril
       History: Hypertension, Obesity
       
ID=11: Jerry Rivera, 59M, "confusion, elevated BP, high sugar", 150/90, 180
       Risk: 8.2, Medications: Metformin, Lisinopril
       History: Type 2 Diabetes, Hypertension
       
ID=45: Janet Torres, 70F, "weakness, elevated BP, high sugar", 160/100, 210
       Risk: 9.1, Medications: Metformin, Enalapril
       History: Type 2 Diabetes, Hypertension, Obesity
```

## 🎲 Randomization

- **Deterministic option:** Set `random.seed(42)` for reproducible results
- **Realistic distribution:** Uses normal distributions for health metrics
- **Symptom combos:** Symptoms weighted by medical plausibility

## 🔌 Integration with Other Modules

This is the **source of truth** for:
- `chroma_setup.py` - Reads patients_data.csv to create embeddings
- `mcp_server.py` - Reads patients_data.csv for patient health data
- `mcp_client.py` - Indirectly (via server)

---

**When to re-generate:**
- First time setup: Always run
- Testing: Only if you want fresh data
- Production: Dataset is static after initial generation
