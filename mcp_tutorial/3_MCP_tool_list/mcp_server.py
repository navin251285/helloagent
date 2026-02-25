#!/usr/bin/env python3
import json
import sys


def main() -> None:
    request = json.loads(sys.stdin.readline())
    method = request.get("method", "")
    if method == "tools/list":
        result = {
            "tools": [
                {
                    "name": "c_to_f",
                    "description": "Convert Celsius to Fahrenheit.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {"c": {"type": "number"}},
                        "required": ["c"],
                    },
                }
            ]
        }
        response = {"jsonrpc": "2.0", "id": request.get("id", 1), "result": result}
        sys.stdout.write(json.dumps(response))
        return

    if method == "tools/call":
        params = request.get("params", {})
        args = params.get("arguments", {})
        c = float(args.get("c", 0))
        f = c * 9 / 5 + 32
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id", 1),
            "result": {"content": [{"type": "text", "text": str(f)}]},
        }
        sys.stdout.write(json.dumps(response))
        return

    error = {"code": -32601, "message": "Method not found"}
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": request.get("id", 1), "error": error}))


if __name__ == "__main__":
    main()
