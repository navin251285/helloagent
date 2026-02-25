#!/usr/bin/env python3
import sys


def main() -> None:
    line = sys.stdin.readline().strip()
    c = float(line) if line else 0.0
    f = c * 9 / 5 + 32
    sys.stdout.write(str(f))


if __name__ == "__main__":
    main()
