#!/usr/bin/env python3
import json
import urllib.request


def main() -> None:
    patient_id = input("Enter patient ID (1-100): ").strip()
    try:
        patient_id = int(patient_id)
    except ValueError:
        print(json.dumps({"error": "Invalid input. Please enter a number."}))
        return

    print(json.dumps({"input": patient_id}))

    request = json.dumps({"number": patient_id}).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:3000/stream", data=request, method="POST")
    req.add_header("Content-Type", "application/json")

    with urllib.request.urlopen(req, timeout=20) as response:
        for raw_line in response:
            line = raw_line.decode("utf-8").strip()
            if not line.startswith("data:"):
                continue
            payload = line.split("data:", 1)[1].strip()
            if not payload:
                continue
            try:
                message = json.loads(payload)
                print(json.dumps(message))
            except json.JSONDecodeError:
                print(json.dumps({"error": "Invalid JSON from server", "raw": payload}))


if __name__ == "__main__":
    main()
