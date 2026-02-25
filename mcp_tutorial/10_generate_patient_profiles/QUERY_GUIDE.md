# Patient Profile Query Tool - Usage Guide

## Overview

The `query_patients.py` script provides an interactive interface to search and query patient profiles using semantic embeddings. It supports multiple query types including natural language searches, patient history lookups, and risk-based filtering.

## Installation

Make sure you have run the embedding generation script first:
```bash
python create_embeddings.py
```

This creates the ChromaDB database needed for queries.

## Usage Modes

### 1. Interactive Mode (Recommended)

Simply run the script without arguments:
```bash
python query_patients.py
```

This will:
1. Show example queries first
2. Start interactive mode where you can type queries

### 2. Command-Line Mode

Run with a query as an argument:
```bash
python query_patients.py "patient with chest pain and high blood pressure"
```

## Query Types

### 🔍 Semantic Search (Natural Language)

Search using natural language descriptions of symptoms, conditions, or patient characteristics:

**Examples:**
```
elderly patient with diabetes and high blood sugar
patient with chest pain and dizziness
shortness of breath in female patients
high blood pressure with heart symptoms
```

**With Options:**
```
chest pain --results 10
diabetes --minrisk 6.0 --results 5
high blood pressure --maxrisk 5.0
```

**Available Options:**
- `--results N` : Number of results to show (default: 5)
- `--minrisk X` : Minimum risk score filter
- `--maxrisk Y` : Maximum risk score filter

### 👤 Patient History Lookup

Get complete visit history for a specific patient:

**Syntax:**
```
patient:<ID>
```

**Examples:**
```
patient:1
patient:25
patient:100
```

### ⚠️ High-Risk Patient Search

Find patients above a risk score threshold:

**Syntax:**
```
highrisk:<threshold>
```

**Examples:**
```
highrisk:7.0    # All patients with risk score >= 7.0
highrisk:6.5    # All patients with risk score >= 6.5
highrisk:8.0    # Critical risk patients
```

### 🏥 Condition-Based Search

Search for patients with specific medical conditions:

**Syntax:**
```
condition:<condition_name>
```

**Examples:**
```
condition:diabetes
condition:hypertension
condition:heart disease
condition:obesity
```

## Interactive Mode Commands

When in interactive mode, you can:

1. **Type any natural language query**
   ```
   Enter query: chest pain and shortness of breath
   ```

2. **Use special commands**
   ```
   Enter query: patient:5
   Enter query: highrisk:7.0
   Enter query: condition:diabetes
   ```

3. **Exit the program**
   ```
   Enter query: quit
   Enter query: exit
   Enter query: q
   ```

## Example Session

```bash
$ python query_patients.py

✓ Loaded collection with 356 patient visit records

Loading embedding model: all-MiniLM-L6-v2...
✓ Model loaded successfully

EXAMPLE QUERIES:

================================================================================
SEMANTIC SEARCH RESULTS
================================================================================
Query: patient with chest pain and high blood pressure
Showing top 3 similar cases
================================================================================

1. Joshua Martin (Patient ID: 66) - Similarity: 9.42%
   Visit Date: 2026-02-25
   Demographics: 30 years old, Male
   Risk Score: 5.3 (Base: 5.67)
   Symptoms: chest pain, joint pain
   ...

================================================================================
PATIENT PROFILE SIMILARITY SEARCH - INTERACTIVE MODE
================================================================================

Available Commands:
  1. Type a natural language query (e.g., 'chest pain and high blood pressure')
  2. 'patient:<ID>' - Get history for specific patient (e.g., 'patient:5')
  3. 'highrisk:<threshold>' - Find high-risk patients (e.g., 'highrisk:7.0')
  4. 'condition:<name>' - Find patients with condition (e.g., 'condition:diabetes')
  5. 'quit' or 'exit' - Exit the program

Examples:
  chest pain and dizziness --results 10
  shortness of breath --minrisk 5.0 --results 3
================================================================================

Enter query: elderly patient with diabetes
[Results displayed...]

Enter query: patient:25
[Patient history displayed...]

Enter query: highrisk:7.5
[High-risk patients displayed...]

Enter query: quit
Goodbye!
```

## Output Format

All queries return detailed patient information including:

- **Patient Name & ID**: Unique identifier
- **Similarity Score**: How well the result matches your query (semantic search only)
- **Visit Date**: When the visit occurred
- **Demographics**: Age and gender
- **Risk Score**: Current risk score and base score
- **Symptoms**: Presenting symptoms
- **Vitals**: Blood pressure and blood sugar levels
- **Medical History**: Previous conditions
- **Medications**: Current prescriptions
- **Outcome**: Treatment plan or next steps

## Use Cases

### Clinical Decision Support
```
Enter query: chest pain with elevated blood pressure --minrisk 6.0
```
Find similar high-risk cases for comparison.

### Patient Cohort Analysis
```
Enter query: condition:diabetes
```
Identify all patients with specific conditions.

### Risk Stratification
```
Enter query: highrisk:7.0
```
Prioritize high-risk patients for intervention.

### Historical Pattern Analysis
```
Enter query: patient:45
```
Review complete patient history and progression.

### Symptom-Based Research
```
Enter query: shortness of breath and confusion --results 20
```
Study patterns across similar symptom presentations.

## Tips for Better Results

1. **Be Specific**: "elderly patient with chest pain and diabetes" is better than just "chest pain"

2. **Use Medical Terms**: The system understands medical terminology like "hypertension", "dyspnea", etc.

3. **Combine Filters**: Use risk score filters to narrow results
   ```
   diabetes --minrisk 6.0 --maxrisk 8.0
   ```

4. **Adjust Result Count**: Request more results if needed
   ```
   heart symptoms --results 15
   ```

5. **Explore Patient History**: When you find an interesting case, look up their full history
   ```
   patient:23
   ```

## Performance Notes

- First run loads the embedding model (~1-2 seconds)
- Semantic searches are very fast (<100ms)
- The collection contains 356 patient visit records
- All searches use vector similarity matching for accurate results

## Troubleshooting

**Error: "Could not load patient profiles collection"**
- Solution: Run `python create_embeddings.py` first to generate the database

**No results found**
- Try broader queries
- Remove or adjust risk score filters
- Increase the number of results requested

**Slow performance**
- First load is slower (model initialization)
- Subsequent queries are much faster
- Consider reducing `--results` count for very large result sets

## Advanced Usage

### Batch Queries

Create a file with queries (one per line) and process them:
```bash
while read query; do
    python query_patients.py "$query"
done < queries.txt
```

### Export Results

Redirect output to a file:
```bash
python query_patients.py "diabetes patients" > results.txt
```

### Programmatic Access

Import and use functions in your own Python scripts:
```python
from query_patients import semantic_search, search_by_patient_id

# Perform semantic search
semantic_search("chest pain", n_results=10)

# Get patient history
search_by_patient_id("5")
```

## Related Files

- `generate_patients.py` - Generates the patient dataset
- `create_embeddings.py` - Creates ChromaDB embeddings
- `patients_data.json` - Source patient data
- `chroma_db/` - Vector database directory
- `README.md` - Complete project documentation

## Support

For more information about the patient data structure, risk score calculations, and embedding model details, see the main [README.md](README.md) file.
