#!/usr/bin/env python3
"""
Test script for pattern-based password generation
"""

import itertools
import string

def generate_from_pattern(pattern, char_sets):
    """Generate passwords from a pattern using character sets"""
    # Parse pattern into list of character sets
    sets = []
    i = 0
    while i < len(pattern):
        if pattern[i] == '?':
            if i + 1 < len(pattern):
                char_type = pattern[i + 1]
                if char_type in char_sets:
                    sets.append(char_sets[char_type])
                    i += 2
                else:
                    # Invalid, treat as literal
                    sets.append([pattern[i]])
                    i += 1
            else:
                sets.append([pattern[i]])
                i += 1
        else:
            sets.append([pattern[i]])
            i += 1

    # Generate all combinations
    for combo in itertools.product(*sets):
        yield ''.join(combo)

def test_pattern_generation():
    """Test pattern-based generation"""
    char_sets = {
        'l': string.ascii_lowercase,
        'u': string.ascii_uppercase,
        'd': string.digits,
        's': '!@#$%^&*'
    }

    # Test 1: Simple pattern with lowercase and digits
    print("Test 1: Pattern '?l?l?d?d' (2 lowercase + 2 digits)")
    pattern = "?l?l?d?d"
    count = 0
    for pw in generate_from_pattern(pattern, char_sets):
        if count < 5:
            print(f"  {pw}")
        count += 1
    print(f"  Total combinations: {count}")
    expected = 26 * 26 * 10 * 10  # 67600
    print(f"  Expected: {expected}")
    assert count == expected, f"Expected {expected}, got {count}"
    print("  ✓ PASSED\n")

    # Test 2: Pattern with literal characters
    print("Test 2: Pattern 'pass?d?d' (literal 'pass' + 2 digits)")
    pattern = "pass?d?d"
    count = 0
    for pw in generate_from_pattern(pattern, char_sets):
        if count < 5:
            print(f"  {pw}")
        count += 1
    print(f"  Total combinations: {count}")
    expected = 10 * 10  # 100
    print(f"  Expected: {expected}")
    assert count == expected, f"Expected {expected}, got {count}"
    print("  ✓ PASSED\n")

    # Test 3: Pattern with uppercase
    print("Test 3: Pattern '?u?u?u' (3 uppercase)")
    pattern = "?u?u?u"
    count = 0
    for pw in generate_from_pattern(pattern, char_sets):
        if count < 5:
            print(f"  {pw}")
        count += 1
    print(f"  Total combinations: {count}")
    expected = 26 * 26 * 26  # 17576
    print(f"  Expected: {expected}")
    assert count == expected, f"Expected {expected}, got {count}"
    print("  ✓ PASSED\n")

    # Test 4: Pattern with special characters
    print("Test 4: Pattern '?l?s?d' (lowercase + special + digit)")
    pattern = "?l?s?d"
    count = 0
    for pw in generate_from_pattern(pattern, char_sets):
        if count < 5:
            print(f"  {pw}")
        count += 1
    print(f"  Total combinations: {count}")
    expected = 26 * 8 * 10  # 2080
    print(f"  Expected: {expected}")
    assert count == expected, f"Expected {expected}, got {count}"
    print("  ✓ PASSED\n")

    # Test 5: Empty pattern (generates one empty string)
    print("Test 5: Empty pattern ''")
    pattern = ""
    count = 0
    for pw in generate_from_pattern(pattern, char_sets):
        count += 1
    print(f"  Total combinations: {count}")
    expected = 1  # Empty pattern generates one empty string
    print(f"  Expected: {expected}")
    assert count == expected, f"Expected {expected}, got {count}"
    print("  ✓ PASSED\n")


    print("All tests passed! ✓")

if __name__ == "__main__":
    test_pattern_generation()
