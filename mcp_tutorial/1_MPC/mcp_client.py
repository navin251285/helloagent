#!/usr/bin/env python3
import subprocess


def main() -> None:
    proc = subprocess.run(
        ["python3", "mcp_server.py"],
        input="100\n",
        text=True,
        capture_output=True,
        check=True,
    )
    print(proc.stdout)


if __name__ == "__main__":
    main()
