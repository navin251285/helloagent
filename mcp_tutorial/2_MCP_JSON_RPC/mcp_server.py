#!/usr/bin/env python3
import json
import sys


def main() -> None:
    request = json.loads(sys.stdin.readline())
    params = request.get("params", {})
    c = float(params.get("c", 0))
    f = c * 9 / 5 + 32
    response = {"jsonrpc": "2.0", "id": request.get("id", 1), "result": {"f": f}}
    sys.stdout.write(json.dumps(response))


if __name__ == "__main__":
    main()
