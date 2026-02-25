#!/usr/bin/env python3
import asyncio
import json

import websockets


async def run_client() -> None:
    patient_id = input("Enter patient ID (1-100): ").strip()
    try:
        patient_id = int(patient_id)
    except ValueError:
        print(json.dumps({"error": "Invalid input. Please enter a number."}))
        return

    print(json.dumps({"input": patient_id}))

    async with websockets.connect("ws://127.0.0.1:3000/ws") as ws:
        await ws.send(json.dumps({"number": patient_id}))
        async for message in ws:
            try:
                data = json.loads(message)
                print(json.dumps(data))
            except json.JSONDecodeError:
                print(json.dumps({"error": "Invalid JSON from server", "raw": message}))


def main() -> None:
    asyncio.run(run_client())


if __name__ == "__main__":
    main()
