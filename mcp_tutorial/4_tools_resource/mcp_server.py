#!/usr/bin/env python3
import json
import random
import sys


def main() -> None:
    request = json.loads(sys.stdin.readline())
    method = request.get("method", "")
    
    if method == "random_op":
        params = request.get("params", {})
        number = int(params.get("number", 0))
        rand_num = random.randint(1, 5)
        op = random.choice(["+", "-"])
        value = number + rand_num if op == "+" else number - rand_num
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id", 1),
            "result": {
                "input": number,
                "operation": op,
                "random": rand_num,
                "value": value,
            },
        }
        sys.stdout.write(json.dumps(response))
        return

    error = {"code": -32601, "message": "Method not found"}
    sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": request.get("id", 1), "error": error}))


if __name__ == "__main__":
    main()
