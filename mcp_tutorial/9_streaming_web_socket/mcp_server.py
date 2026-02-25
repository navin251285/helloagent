#!/usr/bin/env python3
import asyncio
import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, WebSocket


CSV_PATH = Path(__file__).with_name("patients.csv")
app = FastAPI()


def update_patient(patient_id: int) -> bool:
    day_after_tomorrow = (datetime.now() + timedelta(days=2)).strftime("%d-%m-%Y")
    ist_timestamp = (datetime.utcnow() + timedelta(hours=5, minutes=30)).strftime("%d-%m-%Y %H:%M")

    rows = []
    updated = False
    with CSV_PATH.open("r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if int(row["id"]) == patient_id:
                row["operation"] = "YES"
                row["time"] = "11 AM"
                row["date"] = day_after_tomorrow
                row["timestamp"] = ist_timestamp
                updated = True
            rows.append(row)

    with CSV_PATH.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["id", "name", "age", "operation", "time", "date", "timestamp"],
        )
        writer.writeheader()
        writer.writerows(rows)

    return updated


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    data = await websocket.receive_text()
    payload = json.loads(data)
    user_input = int(payload.get("number", 0))

    operation = random.choice(["+", "-"])
    server_number = random.randint(1, 5)
    await websocket.send_text(
        json.dumps({"stage": "operation_selected", "operation": operation, "number": server_number})
    )
    await asyncio.sleep(2)

    if operation == "+":
        final_score = user_input + server_number
    else:
        final_score = user_input - server_number

    await websocket.send_text(json.dumps({"stage": "calculating"}))
    await asyncio.sleep(2)

    await websocket.send_text(json.dumps({"stage": "final", "value": final_score}))
    await asyncio.sleep(1)

    updated_id = None
    if 1 <= final_score <= 100:
        if update_patient(final_score):
            updated_id = final_score

    await websocket.send_text(json.dumps({"stage": "updated", "updated_id": updated_id}))
    await websocket.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=3000)
