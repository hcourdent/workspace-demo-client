import re
from fractions import Fraction

def main(input_string: str, multiplier: int = 1) -> str:
    # Function to find and multiply numbers within the string
    def replace_numbers(match):
        # Extract the number from the match
        number_str = match.group(0)
        # Check if the number is a fraction
        if "/" in number_str:
            # Convert fraction to a Fraction object, multiply, and convert back to string
            result = str(Fraction(number_str) * effective_multiplier)
        else:
            # Convert to float, multiply, and convert back to string
            # Using float to handle both integers and decimals
            result = str(float(number_str) * effective_multiplier)
        return result

    # Check if multiplier is None, empty, or 0; if so, use 1 instead
    effective_multiplier = 1 if not multiplier else multiplier

    # Regular expression to match integers, decimals, and fractions
    number_pattern = r"\d+\.?\d*\/?\d*"

    # Replace all numbers in the input string using the replace_numbers function
    result_string = re.sub(number_pattern, replace_numbers, input_string)

    return result_string