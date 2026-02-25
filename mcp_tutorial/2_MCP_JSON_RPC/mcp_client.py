#!/usr/bin/env python3
import json
import subprocess


def main() -> None:
    request = {"jsonrpc": "2.0", "id": 1, "method": "convert", "params": {"c": 25}}
    proc = subprocess.run(
        ["python3", "mcp_server.py"],
        input=json.dumps(request) + "\n",
        text=True,
        capture_output=True,
        check=True,
    )
    print(proc.stdout)


if __name__ == "__main__":
    main()
