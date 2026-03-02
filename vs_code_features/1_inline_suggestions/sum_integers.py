from numpy import subtract


def sum_two_integers(a, b):
    """
    Sum two integers and return the result.
    
    Args:
        a (int): First integer
        b (int): Second integer
    
        Returns:    
        int: Sum of a and b
    """
    return a + b

def subtract_two_integers(a, b):
    """
    Subtract two integers and return the result.
    
    Args:
        a (int): First integer
        b (int): Second integer
    
        Returns:    
        int: Difference of a and b
    """
    return a - b
    
def multiply_two_integers(a, b):
    """
    Multiply two integers and return the result.
    
    Args:
        a (int): First integer
        b (int): Second integer
    
        Returns:    
        int: Product of a and b
    """
    return a * b

if __name__ == "__main__":
    # Example usage
    num1 = int(input("Enter first integer: "))
    num2 = int(input("Enter second integer: "))
    
    result = sum_two_integers(num1, num2)
    print(f"The sum of {num1} and {num2} is: {result}")

    subtract_result = subtract_two_integers(num1, num2)
    print(f"The difference of {num1} and {num2} is: {subtract_result}")

    multiply_result = multiply_two_integers(num1, num2) 
    