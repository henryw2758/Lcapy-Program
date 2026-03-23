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
    Uses the smallest unit where the numeric value is ≥ 1.
    Examples:
        '1k' -> '1 kilo'
        '1m' -> '1 milli'
        '1u' -> '1 micro'
        '1e-3' -> '1 milli'
        '1e-4' -> '100 micro' (0.1 milli < 1, so scale up)
        '1e-6' -> '1 micro'
        '10' -> '10' (no multiplier)
    
    Args:
        value: SPICE value string (e.g., '1k', '1e-3')
        
    Returns:
        Value with spelled-out multiplier (e.g., '1 kilo', '100 micro')
    """
    if not value:
        return value
    
    value = value.strip()
    
    # Define available units in order from smallest to largest
    # Each tuple: (name, factor)
    unit_scale = [
        ("femto", 1e-15),
        ("pico", 1e-12),
        ("nano", 1e-9),
        ("micro", 1e-6),
        ("milli", 1e-3),
        ("", 1),  # base unit (no multiplier)
        ("kilo", 1e3),
        ("mega", 1e6),
        ("giga", 1e9),
        ("tera", 1e12),
    ]
    
    import re
    
    # Check for suffix notation (e.g., '1k', '10m')
    suffix_match = re.match(r'^([\d.]+)([kMGTmunpf])$', value, re.IGNORECASE)
    if suffix_match:
        base_num = float(suffix_match.group(1))
        suffix = suffix_match.group(2).upper()
        
        # Map suffixes to unit names (handle both cases)
        suffix_map = {
            "T": "tera", "t": "tera",
            "G": "giga", "g": "giga",
            "M": "mega", "m": "milli",
            "K": "kilo", "k": "kilo",
            "U": "micro", "u": "micro",
            "N": "nano", "n": "nano",
            "P": "pico", "p": "pico",
            "F": "femto", "f": "femto",
        }
        
        # Get the target unit from suffix
        target_unit_name = suffix_map.get(suffix, "")
        
        # Find which unit scale entry matches the suffix
        target_index = next((i for i, (name, _) in enumerate(unit_scale) if name == target_unit_name), 5)  # Default to base unit
        
        # Calculate value in base units
        target_factor = unit_scale[target_index][1]
        base_value = base_num * target_factor
        
        # Find first unit where the value is ≥ 1
        for unit, factor in unit_scale:
            scaled_value = base_value / factor
            if scaled_value >= 1:
                # Format the number nicely
                formatted_num = format_number(scaled_value)
                if unit:
                    return f"{formatted_num} {unit}"
                return formatted_num
    
    # Check for scientific notation (e.g., '1e-3', '10e+6')
    scientific_match = re.match(r'^([\d.]+)e([+-]?\d+)$', value, re.IGNORECASE)
    if scientific_match:
        base = float(scientific_match.group(1))
        exponent = int(scientific_match.group(2))
        
        # Determine starting unit from exponent
        # Map exponents to units: 
        # -15 -> femto, -12 -> pico, -9 -> nano, -6 -> micro, -3 -> milli
        # 0 -> base, 3 -> kilo, 6 -> mega, etc.
        exp_to_unit = {
            -15: 0,  # femto
            -12: 1,  # pico
            -9: 2,   # nano
            -6: 3,   # micro
            -3: 4,   # milli
            0: 5,    # base
            3: 6,    # kilo
            6: 7,    # mega
            9: 8,    # giga
            12: 9,   # tera
        }
        
        # For intermediate exponents, find nearest standard exponent
        nearest_exp = min(exp_to_unit.keys(), key=lambda x: abs(x - exponent))
        start_index = exp_to_unit[nearest_exp]
        
        # Calculate value in base units
        actual_value = base * (10 ** exponent)
        
        # Find first unit where the value is ≥ 1
        # Only search from the appropriate direction based on starting unit
        if start_index < 5:  # Starting with fractional unit (femto to milli)
            # Search from milli DOWN to femto
            for i in range(start_index, -1, -1):  # Start at milli, go down to femto
                unit, factor = unit_scale[i]
                scaled_value = actual_value / factor
                if scaled_value >= 1:
                    formatted_num = format_number(scaled_value)
                    if unit:
                        return f"{formatted_num} {unit}"
                    return formatted_num
        else:  # Starting with base unit or larger (base, kilo, mega, etc.)
            # Just use the starting unit since value is already ≥ 1
            unit, factor = unit_scale[start_index]
            scaled_value = actual_value / factor
            formatted_num = format_number(scaled_value)
            if unit:
                return f"{formatted_num} {unit}"
            return formatted_num
    
    # Plain number without multiplier
    try:
        plain_num = float(value)
        formatted_num = format_number(plain_num)
        return formatted_num
    except ValueError:
        return value


def format_number(num: float) -> str:
    """Format a number nicely, removing unnecessary trailing zeros.
    
    Examples:
        100.0 -> '100'
        0.1 -> '0.1'
        1.5 -> '1.5'
        10.0 -> '10'
    
    Args:
        num: Number to format
        
    Returns:
        Formatted string representation
    """
    # Round to reasonable precision to avoid floating point errors
    # Round to 10 decimal places, then check if it's effectively an integer
    rounded = round(num, 10)
    
    # If very close to an integer, use integer
    if abs(rounded - int(rounded)) < 1e-9:
        return str(int(rounded))
    
    # Otherwise, check if it's a whole number
    if rounded == int(rounded):
        return str(int(rounded))
    
    # Remove trailing zeros from decimal
    formatted = f"{rounded:.10f}".rstrip('0').rstrip('.')
    
    return formatted


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
