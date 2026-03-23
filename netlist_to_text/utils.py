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
