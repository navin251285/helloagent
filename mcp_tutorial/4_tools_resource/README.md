# MCP Tools & Resources Demo

Accept a patient ID (1-100). The server generates a random number (1-5) and a random operation (+ or -), applies it to the input, and returns the result. The client updates the record for the computed result if it is within 1-100.

## Run

```bash
python3 mcp_client.py
```

If the computed result is outside 1-100 (e.g., input 1 with operation -3 gives -2), the client reports that no record was updated.

## Example

```
Enter patient ID (1-100): 5
Input: 9
Server operation: -4
Computed result: 5
Patient ID 5 updated successfully!
```
