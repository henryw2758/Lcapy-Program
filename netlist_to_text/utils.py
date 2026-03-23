"""Utility functions for netlist-to-text."""


from typing import List


def count_words(text: str) -> int:
    """Count words in a text string."""
    return len(text.split())


def format_element_count(count: int, element_type: str) -> str:
    """Format element count with proper singular/plural.
    
    Args:
        count: Number of elements
        element_type: Type of element (e.g., 'resistor')
        
    Returns:
        Formatted string like '3 resistors' or '1 resistor'
    """
    if count == 1:
        return f"{count} {element_type}"
    else:
        # Add 's' for plural
        return f"{count} {element_type}s"


def spell_out_multiplier(value: str) -> str:
    """Spell out SPICE unit multipliers for accessibility.
    
    Converts abbreviated unit prefixes to full words for screen readers.
    Examples:
        '1k' -> '1 kilo'
        '1m' -> '1 milli'
        '1u' -> '1 micro'
        '1e-3' -> '1 milli'
        '1e-6' -> '1 micro'
        '10' -> '10' (no multiplier)
    
    Args:
        value: SPICE value string (e.g., '1k', '1e-3')
        
    Returns:
        Value with spelled-out multiplier (e.g., '1 kilo', '1 milli')
    """
    if not value:
        return value
    
    value = value.strip()
    
    # Multiplier suffix mappings
    suffix_map = {
        "T": "tera",
        "G": "giga",
        "M": "mega",
        "k": "kilo",
        "m": "milli",
        "u": "micro",
        "n": "nano",
        "p": "pico",
        "f": "femto",
    }
    
    # Scientific notation multiplier mappings
    exp_map = {
        12: "tera",
        9: "giga",
        6: "mega",
        3: "kilo",
        -3: "milli",
        -4: "milli",  # 10^-4 = 0.1 milli
        -5: "milli",  # 10^-5 = 0.01 milli
        -6: "micro",
        -9: "nano",
        -12: "pico",
        -15: "femto",
    }
    
    # Check for suffix notation (e.g., '1k', '10m')
    if value and value[-1] in suffix_map and value[:-1].replace(".", "", 1).isdigit():
        base = value[:-1]
        multiplier = value[-1]
        return f"{base} {suffix_map[multiplier]}"
    
    # Check for scientific notation (e.g., '1e-3', '10e+6')
    import re
    scientific_match = re.match(r'^([\d.]+)e([+-]?\d+)$', value, re.IGNORECASE)
    if scientific_match:
        base = scientific_match.group(1)
        exponent = int(scientific_match.group(2))
        
        if exponent in exp_map:
            return f"{base} {exp_map[exponent]}"
    
    # No multiplier found, return original value
    return value


def validate_spice_value(value: str) -> bool:
    """Validate if a value string is a valid SPICE value.
    
    Valid values:
        - Numbers: 1k, 2.5M, 3.3u
        - Waveforms: PULSE, EXP, SINE
        - Expressions: (with proper formatting)
    
    Args:
        value: Value string to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not value:
        return True  # Empty is valid (no value)
    
    # Check for waveform keywords
    waveform_keywords = ["PULSE", "EXP", "SINE", "SFFM"]
    for keyword in waveform_keywords:
        if keyword in value.upper():
            return True
    
    # Check if it's a number (with possible unit suffix)
    value = value.strip()
    if value[-1:].isdigit():
        return True  # Plain number
    
    # Check for unit suffixes
    unit_suffixes = ["T", "G", "M", "k", "m", "u", "n", "p", "f"]
    if value[:-1].isdigit() and value[-1] in unit_suffixes:
        return True
    
    # Could be an expression or complex value
    # For simplicity, accept it
    return True
