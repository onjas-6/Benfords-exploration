"""
Number extraction from Wikipedia articles using regex on bytes.
Fast extraction without full UTF-8 decoding.
"""

import re
from typing import List, Tuple


# Regex pattern for numbers (works on bytes)
# Matches integers and decimals starting with 1-9, avoids leading zeros
NUMBER_PATTERN = re.compile(rb'(?<![0-9])[1-9][0-9]{0,15}(?:\.[0-9]+)?(?![0-9])')

# Quick check pattern (faster, for two-pass)
HAS_NUMBER_PATTERN = re.compile(rb'[1-9]')


def quick_has_numbers(text_bytes: bytes) -> bool:
    """
    Fast check if text contains any numbers.
    Used in first pass to skip articles without numbers.
    
    Args:
        text_bytes: Raw bytes of article text
        
    Returns:
        True if text likely contains extractable numbers
    """
    return HAS_NUMBER_PATTERN.search(text_bytes) is not None


def extract_numbers_from_bytes(text_bytes: bytes) -> List[float]:
    """
    Extract all numbers from raw bytes without full UTF-8 decoding.
    
    Args:
        text_bytes: Raw bytes of article text
        
    Returns:
        List of extracted numbers as floats
    """
    numbers = []
    
    for match in NUMBER_PATTERN.finditer(text_bytes):
        try:
            # Convert bytes to string then to float
            num_str = match.group(0).decode('utf-8', errors='ignore')
            # Remove commas if present (e.g., "1,234" -> "1234")
            num_str = num_str.replace(',', '')
            number = float(num_str)
            
            # Sanity check: must be positive and reasonable
            if 0 < number < 1e16:
                numbers.append(number)
        except (ValueError, UnicodeDecodeError):
            # Skip malformed numbers
            continue
    
    return numbers


def extract_numbers_from_text(text: str) -> List[float]:
    """
    Extract numbers from decoded text string.
    
    Args:
        text: Unicode text string
        
    Returns:
        List of extracted numbers as floats
    """
    return extract_numbers_from_bytes(text.encode('utf-8', errors='ignore'))


def get_first_digit(number: float) -> int:
    """
    Extract the first significant digit from a number.
    
    Args:
        number: A positive number
        
    Returns:
        First digit (1-9), or 0 if invalid
    """
    if number <= 0:
        return 0
    
    # Convert to string and get first non-zero digit
    num_str = f"{number:.15g}"  # Use general format to avoid scientific notation issues
    
    for char in num_str:
        if char.isdigit() and char != '0':
            return int(char)
    
    return 0


def get_second_digit(number: float) -> int:
    """
    Extract the second digit from a number (0-9).
    
    Args:
        number: A positive number
        
    Returns:
        Second digit (0-9), or 0 if number has only one digit
    """
    if number <= 0:
        return 0
    
    # Convert to string and get second digit
    num_str = f"{number:.15g}"
    
    # Find first non-zero digit, then get next digit
    found_first = False
    for char in num_str:
        if char.isdigit():
            if not found_first and char != '0':
                found_first = True
            elif found_first:
                return int(char)
    
    return 0


def analyze_number(number: float) -> Tuple[int, int]:
    """
    Get both first and second digits from a number.
    
    Args:
        number: A positive number
        
    Returns:
        Tuple of (first_digit, second_digit)
    """
    return (get_first_digit(number), get_second_digit(number))


# Test function
if __name__ == "__main__":
    # Test cases
    test_numbers = [
        123.456,
        1.5,
        9999,
        0.00123,
        1234567890,
        42,
        3.14159
    ]
    
    print("Testing number extraction:")
    print("-" * 50)
    for num in test_numbers:
        first, second = analyze_number(num)
        print(f"{num:>15} -> first: {first}, second: {second}")
    
    # Test extraction from text
    print("\nTesting extraction from text:")
    print("-" * 50)
    test_text = "The population is 1,234,567 people. Area: 42.5 km². Founded in 1999."
    numbers = extract_numbers_from_text(test_text)
    print(f"Text: {test_text}")
    print(f"Extracted: {numbers}")

