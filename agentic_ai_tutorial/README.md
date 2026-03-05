# Agentic AI Tutorial (LangGraph + Google Vertex AI)

This folder contains a full Python lesson series (`Lesson_0` to `Lesson_66`) for learning Agentic AI with:
- LangGraph
- Google Vertex AI (Gemini)
- Simple arithmetic examples with increasing architectural complexity

## 1. Prerequisites

- Python 3.10+
- `pip`
- Google Cloud project with Vertex AI API enabled
- Access to run `gcloud` commands

## 2. Create Environment And Install All Dependencies

Run these commands from `agentic_ai_tutorial`:

```bash
python3 -m venv agentic_ai_tutorial
source agentic_ai_tutorial/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 3. Configure Environment Variables

Copy `.env_example` to `.env` and update values:

```bash
cp .env_example .env
```

Then edit `.env` in this folder:

```dotenv
PROJECT_ID=your-gcp-project-id
LOCATION=us-central1
```

Important: Never commit `.env`. It is ignored by `.gitignore`.

## 4. Authenticate To Google Cloud (Application Default Credentials)

```bash
gcloud auth application-default login
gcloud config set project "$PROJECT_ID"
```

If Vertex AI API is not enabled yet:

```bash
gcloud services enable aiplatform.googleapis.com
```

## 5. Register Jupyter Kernel

```bash
python -m ipykernel install --user --name agentic-ai --display-name "Python (agentic-ai)"
```

## 6. Run Lessons

```bash
cd .converted_py
python Lesson_0_What_is_an_Agent.py
```

Run any lesson script, for example:
- `Lesson_0_What_is_an_Agent.py`
- `Lesson_53_Budget_Aware_Agents.py`
- `Lesson_66_Production_Grade_Agentic_AI_Architecture.py`

## 7. Quick Dependency Check

```bash
python -c "import os, vertexai, langgraph; from dotenv import load_dotenv; from langchain_google_vertexai import ChatVertexAI; print('OK')"
```

## 8. Common Issues

- `source agentic_ai_tutorial/bin/activate` fails:
  - Ensure you run it from `agentic_ai_tutorial` after creating `agentic_ai_tutorial`.
- Vertex auth errors:
  - Re-run `gcloud auth application-default login`.
- Project/location errors:
  - Verify `.env` values and ensure the project has Vertex AI enabled.

## 9. Core Dependencies Included

- `python-dotenv`
- `google-cloud-aiplatform`
- `vertexai`
- `langchain-google-vertexai`
- `langchain-core`
- `langgraph`
- `pydantic`
- `IPython`
