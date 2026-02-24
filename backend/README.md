Prime Checker (FastAPI)

This repository contains a small FastAPI app that checks whether a number is prime.

Files of interest:

- `api.py` — FastAPI application
- `client.py` — simple client that calls the API
- `prime_check.py` — prime checking logic
- `Dockerfile` — container image definition
- `cloudbuild.yaml` — Cloud Build pipeline for building and deploying to Cloud Run

Quick local build (requires Docker):

```bash
docker build -t prime-checker:latest .
docker run --rm -p 8080:8080 -e PORT=8080 prime-checker:latest
# then, in another shell:
curl "http://127.0.0.1:8080/is_prime?n=17"
```

If you get a permission error when building ("permission denied while trying to connect to the Docker daemon"), either run the build with `sudo` or add your user to the `docker` group:

```bash
# run with sudo (may prompt for your password)
sudo docker build -t prime-checker:latest .

# OR add your user to the docker group (log out/in after):
sudo usermod -aG docker $USER
```

Build & deploy using Google Cloud Build + Cloud Run (recommended when you can't run Docker locally):

```bash
# from repository root
gcloud builds submit --config cloudbuild.yaml --substitutions=_REGION=us-central1

# or to explicitly set project and region
gcloud builds submit --config cloudbuild.yaml --project=PROJECT_ID \
  --substitutions=_REGION=us-central1
```

This will build the image, push it to Container Registry, and deploy to Cloud Run.

Notes:
- The container listens on `$PORT` (default 8080) for compatibility with Cloud Run.
- The `Dockerfile` uses `gunicorn` with `uvicorn` workers for production.
# Prime Number Checker API

Simple FastAPI application to check if a number is prime.

## Files
- `prime_check.py` — Core logic with `is_prime()` function and CLI
- `api.py` — FastAPI server with GET/POST endpoints
- `client.py` — Python client to call the API
- `requirements.txt` — Dependencies

## Setup

Install dependencies:
```bash
pip install -r requirements.txt
```

## Running on Remote Code Server (GCP)

### 1. Start the server (on code server)
```bash
cd path/to/project
uvicorn api:app --host 0.0.0.0 --port 8000
```

### 2. Access from local machine

**Option A: SSH Port Forwarding (Recommended)**
```bash
ssh -L 8000:localhost:8000 your-gcp-user@your-gcp-ip
```
Then access: `http://localhost:8000`

**Option B: Direct access via remote IP**
If firewall allows, use remote IP directly:
```bash
http://your-gcp-ip:8000
```

### 3. Test from local machine

After port forwarding is set up, run:
```bash
python3 client.py
```

Or use `curl`:
```bash
curl "http://localhost:8000/is_prime?n=17"
curl -X POST http://localhost:8000/is_prime -H "Content-Type: application/json" -d '{"n":23}'
```

## API Endpoints

**GET /is_prime**
```
Query parameter: n (integer)
Response: {"n": <number>, "is_prime": <boolean>}
```

**POST /is_prime**
```
Body: {"n": <number>}
Response: {"n": <number>, "is_prime": <boolean>}
```

## Example
```bash
# GET request
curl "http://localhost:8000/is_prime?n=17"
# Output: {"n":17,"is_prime":true}

# POST request
curl -X POST http://localhost:8000/is_prime \
  -H "Content-Type: application/json" \
  -d '{"n":18}'
# Output: {"n":18,"is_prime":false}
```
