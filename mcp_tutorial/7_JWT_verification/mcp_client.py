#!/usr/bin/env python3
import base64
import csv
import hashlib
import hmac
import json
import os
import time
import urllib.request
from datetime import datetime, timedelta


JWT_SECRET = "demo-secret"


def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def make_jwt() -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    payload = {"sub": "demo", "iat": int(time.time())}
    header_b64 = base64url_encode(json.dumps(header).encode("utf-8"))
    payload_b64 = base64url_encode(json.dumps(payload).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    signature = hmac.new(JWT_SECRET.encode("utf-8"), signing_input, hashlib.sha256).digest()
    sig_b64 = base64url_encode(signature)
    return f"{header_b64}.{payload_b64}.{sig_b64}"


def get_csv_path() -> str:
    return os.path.join(os.path.dirname(__file__), "patients.csv")


def main() -> None:
    patient_id = input("Enter patient ID (1-100): ").strip()
    try:
        patient_id = int(patient_id)
        if patient_id < 1 or patient_id > 100:
            print("Invalid ID. Must be between 1 and 100.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    response = call_server(patient_id)
    result = response.get("result", {})
    rand_num = result.get("random")
    op = result.get("operation")
    value = result.get("value")

    print(f"Input: {patient_id}")
    print(f"Server operation: {op}{rand_num}")
    print(f"Computed result: {value}")

    if not isinstance(value, int):
        print("Server returned an invalid result.")
        return

    if value < 1 or value > 100:
        print(f"Result {value} is out of range (1-100). No record updated.")
        return

    if update_patient(value):
        print(f"Patient ID {value} updated successfully!")
    else:
        print(f"Patient ID {value} not found. No record updated.")


def call_server(number: int) -> dict:
    request = {"jsonrpc": "2.0", "id": 1, "method": "random_op", "params": {"number": number}}
    data = json.dumps(request).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:3000/", data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {make_jwt()}")
    with urllib.request.urlopen(req, timeout=10) as response:
        body = response.read().decode("utf-8")
    return json.loads(body)


def update_patient(patient_id: int) -> bool:
    day_after_tomorrow = (datetime.now() + timedelta(days=2)).strftime("%d-%m-%Y")
    ist_timestamp = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%d-%m-%Y %H:%M")
    csv_path = get_csv_path()

    rows = []
    updated = False
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["id"]) == patient_id:
                row["operation"] = "YES"
                row["time"] = "11 AM"
                row["date"] = day_after_tomorrow
                row["timestamp"] = ist_timestamp
                updated = True
            rows.append(row)

    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "name", "age", "operation", "time", "date", "timestamp"],
        )
        writer.writeheader()
        writer.writerows(rows)

    return updated


if __name__ == "__main__":
    main()
