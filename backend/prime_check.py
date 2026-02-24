#!/usr/bin/env python3
"""Simple prime-checking utility.

Usage:
  python3 prime_check.py 17
  python3 prime_check.py     # then input an integer when prompted
"""
import sys
import math

def is_prime(n: int) -> bool:
    """Return True if n is prime, False otherwise."""
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False
    limit = math.isqrt(n)
    for i in range(3, limit + 1, 2):
        if n % i == 0:
            return False
    return True

def main() -> None:
    if len(sys.argv) >= 2:
        s = sys.argv[1]
    else:
        s = input("Enter an integer: ").strip()
    try:
        n = int(s)
    except ValueError:
        print(f"Invalid integer: {s}")
        sys.exit(2)
    if is_prime(n):
        print(f"{n} is prime")
    else:
        print(f"{n} is not prime")

if __name__ == "__main__":
    main()
