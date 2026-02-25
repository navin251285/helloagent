#!/usr/bin/env python3
import asyncio
import csv
import json
import random
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel


CSV_PATH = Path(__file__).with_name("patients.csv")
app = FastAPI()


class StreamRequest(BaseModel):
    number: int


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


async def event_stream(user_input: int):
    operation = random.choice(["+", "-"])
    server_number = random.randint(1, 5)
    message = {"stage": "operation_selected", "operation": operation, "number": server_number}
    yield f"data: {json.dumps(message)}\n\n"
    await asyncio.sleep(2)

    if operation == "+":
        final_score = user_input + server_number
    else:
        final_score = user_input - server_number

    calculating = json.dumps({"stage": "calculating"})
    yield f"data: {calculating}\n\n"
    await asyncio.sleep(2)

    final_payload = json.dumps({"stage": "final", "value": final_score})
    yield f"data: {final_payload}\n\n"
    await asyncio.sleep(1)

    updated_id = None
    if 1 <= final_score <= 100:
        if update_patient(final_score):
            updated_id = final_score

    updated_payload = json.dumps({"stage": "updated", "updated_id": updated_id})
    yield f"data: {updated_payload}\n\n"


@app.post("/stream")
async def stream(request: StreamRequest):
    return StreamingResponse(event_stream(request.number), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=3000)
