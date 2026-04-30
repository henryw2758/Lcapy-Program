"""Parser module for SPICE-like netlists."""


from typing import List, Optional
from .element import Element


def is_comment_or_directive(line: str) -> bool:
    """Check if line is a comment or directive.
    
    Comments start with '*'
    Directives start with '.'
    
    Args:
        line: Line to check
        
    Returns:
        True if line should be skipped, False otherwise
    """
    stripped = line.strip()
    if not stripped:
        return True  # Skip empty lines
    if stripped.startswith("*"):
        return True  # Skip comments
    if stripped.startswith("."):
        return True  # Skip directives (.model, .lib, .end, etc.)
    return False


def clean_value(raw_value: str) -> Optional[str]:
    """Clean value string by removing semicolons and drawing directives.
    
    In Lcapy format, values may include drawing directives after semicolons.
    Example: "1e-3; right, size=1.2" -> "1e-3"
    
    Args:
        raw_value: Raw value string from netlist line
        
    Returns:
        Cleaned value string (only the numeric part before semicolon)
    """
    if not raw_value:
        return None
    
    # Split on semicolon and take first part (the actual value)
    if ";" in raw_value:
        clean_value = raw_value.split(";")[0].strip()
        return clean_value if clean_value else None
    
    return raw_value.strip() if raw_value.strip() else None


def parse_element_name(name: str) -> str:
    """Clean and return element name.
    
    Handles special cases:
        - Conductances: 'R1G' -> 'Y1' (convert to Y prefix)
        - Lamp diodes: 'DLamp1' -> 'Lamp1'
    
    Args:
        name: Raw element name from netlist
        
    Returns:
        Cleaned element name
    """
    # Handle conductance (renamed resistor with G suffix)
    if name.startswith("R") and name.endswith("G"):
        return name.replace("R", "Y", 1).replace("G", "", 1)
    
    # Handle lamp diodes
    if "Lamp" in name:
        return name.replace("D", "", 1).replace("§", "").replace("¶", "")
    
    return name


def parse_spice_line(line: str) -> Optional[Element]:
    """Parse a single SPICE netlist line into an Element.
    
    Supported formats:
        2-terminal: R1 N001 N002 1k
        3-terminal (not used in analog-only): Q1 N001 N002 N003 NPN
        
    Args:
        line: SPICE netlist line
        
    Returns:
        Element object or None if line cannot be parsed
    """
    parts = line.strip().split()
    
    if len(parts) < 3:
        return None  # Not enough information
    
    name = parse_element_name(parts[0])
    first_node = parts[1]
    second_node = parts[2]
    
    # Determine value index: KiCAD and some SPICE exports put DC/AC or
    # waveform keywords (PULSE, EXP, SINE, SFFM) in parts[3], pushing
    # the actual value to parts[4].  For DC/AC we only need the magnitude;
    # for waveforms we keep the full keyword+params string.
    source_keywords = {"DC", "AC"}
    waveform_keywords = {"PULSE", "EXP", "SINE", "SFFM"}
    
    value = None
    if len(parts) > 3:
        token3_upper = parts[3].upper()
        if token3_upper in source_keywords:
            # e.g. "V1 node1 node2 DC 1" — value is the next token
            value = clean_value(parts[4]) if len(parts) > 4 else None
        elif token3_upper in waveform_keywords:
            # e.g. "V1 node1 node2 PULSE 0 5 1m 1m 1m 10m 20m"
            value = clean_value(" ".join(parts[3:]))
        else:
            value = clean_value(parts[3])
    
    # Only support 2-terminal elements for analog-only version
    # 3-terminal elements (Q, M, XU, etc.) would require more parsing
    prefix = name[0].upper() if name else ""
    
    # Check if this is a supported element type
    supported_types = {"R", "L", "C", "V", "I", "G", "Y"}
    if prefix not in supported_types:
        return None
    
    return Element(
        name=name,
        first_node=first_node,
        second_node=second_node,
        value=value
    )


def parse_netlist_file(filename: str) -> List[Element]:
    """Parse a SPICE netlist file into a list of Elements.
    
    Args:
        filename: Path to SPICE netlist file
        
    Returns:
        List of Element objects
        
    Raises:
        FileNotFoundError: If file doesn't exist
    """
    elements = []
    
    with open(filename, "r") as f:
        for line in f:
            # Skip comments and directives
            if is_comment_or_directive(line):
                continue
            
            # Parse element
            element = parse_spice_line(line)
            if element:
                elements.append(element)
    
    return elements


def parse_lcapy_netlist(lcapy_circuit) -> List[Element]:
    """Parse a Lcapy Circuit object into a list of Elements.
    
    Args:
        lcapy_circuit: Lcapy Netlist or Circuit object
        
    Returns:
        List of Element objects
    """
    elements = []
    
    try:
        # Try to access elements from Lcapy circuit
        for cpt_name, cpt in lcapy_circuit.elements.items():
            # Extract component information
            name = cpt_name
            
            # Get nodes (Lcapy stores nodes differently)
            nodes = cpt.node_names if hasattr(cpt, "node_names") else []
            if len(nodes) >= 2:
                first_node = str(nodes[0])
                second_node = str(nodes[1])
            else:
                continue  # Skip if not enough nodes
            
            # Get value (Lcapy stores args differently)
            value = None
            if hasattr(cpt, "args") and len(cpt.args) > 0:
                value = str(cpt.args[0])
            
            # Create Element
            element = Element(
                name=name,
                first_node=first_node,
                second_node=second_node,
                value=value
            )
            elements.append(element)
            
    except (AttributeError, TypeError) as e:
        # If Lcapy integration fails, return empty list
        # User can fall back to file-based parsing
        return []
    
    return elements


def detect_format(input_path: str) -> str:
    """Auto-detect input format from file extension and content.
    
    Args:
        input_path: Path to input file
        
    Returns:
        'spice', 'lcapy', or 'unknown'
    """
    # Check extension
    if input_path.endswith(('.net', '.cir', '.spice')):
        return 'spice'
    if input_path.endswith(('.py',)):
        # Could be Lcapy Python script
        try:
            with open(input_path, 'r') as f:
                content = f.read()
                if 'from lcapy import' in content or 'import lcapy' in content:
                    return 'lcapy'
        except Exception:
            pass
    
    return 'unknown'