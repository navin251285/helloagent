# MCP Tools & Resources Demo (HTTP + JWT)

This folder mirrors 5_http_server, but adds a simple JWT verification step.

## Run the server

```bash
python3 mcp_server.py
```

The server listens on http://127.0.0.1:3000 and requires `Authorization: Bearer <token>`.

## Run the client

```bash
python3 mcp_client.py
```

Enter a patient ID between 1 and 100. The server generates a random number (1-5) and a random operation (+ or -), applies it to the input, and returns the result. The client updates the record for the computed result if it is within 1-100. If the result is out of range, no record is updated.

## Example

```
Enter patient ID (1-100): 9
Input: 9
Server operation: -4
Computed result: 5
Patient ID 5 updated successfully!
```
