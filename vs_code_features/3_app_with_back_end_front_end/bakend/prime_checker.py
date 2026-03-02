import math


def is_prime(number: int) -> bool:
    if number <= 1:
        return False
    if number <= 3:
        return True
    if number % 2 == 0 or number % 3 == 0:
        return False

    limit = int(math.isqrt(number))
    candidate = 5
    while candidate <= limit:
        if number % candidate == 0 or number % (candidate + 2) == 0:
            return False
        candidate += 6

    return True
