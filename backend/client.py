"""Simple client to call FastAPI endpoints.

Run the server first:

    uvicorn api:app --host 0.0.0.0 --port 8000

Then run this client:

    python3 client.py                          # default: localhost
    python3 client.py http://your-gcp-ip:8000 # remote server

Or set API_URL env var:

    export API_URL=http://your-gcp-ip:8000
    python3 client.py
"""
import os
import sys
import requests

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/is_prime")

# Allow override via CLI argument
if len(sys.argv) > 1:
    API_URL = sys.argv[1].rstrip("/") + "/is_prime"

def get_base():
    return API_URL

def call_get(n: int):
    r = requests.get(get_base(), params={"n": n})
    r.raise_for_status()
    return r.json()

def call_post(n: int):
    r = requests.post(get_base(), json={"n": n})
    r.raise_for_status()
    return r.json()

def main() -> None:
    print(f"Connecting to: {get_base()}\n")
    for n in (17, 18, 19):
        print("GET", call_get(n))
    print("POST", call_post(23))

if __name__ == "__main__":
    main()
