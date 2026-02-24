# Prime Checker

This repo contains two separate apps:

- backend: FastAPI service that checks if a number is prime
- frontend: Vite + React UI for the prime checker

## Backend

From the repo root:

```bash
cd backend
pip install -r requirements.txt
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

API endpoints:

- GET  /is_prime?n=17
- POST /is_prime  {"n": 17}

## Frontend

From the repo root:

```bash
cd frontend
npm install
npm run dev
```

The UI will be available at:

- http://localhost:5173/

By default, the UI calls the backend at:

- http://<current-host>:8000/is_prime

If you want to override it, set `VITE_API_URL` before running the UI.
