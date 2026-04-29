"""KiCAD v6+ .kicad_sch file parser."""

import re
from typing import List, Optional, Tuple
from .base_parser import Component, Wire


class KicadV6Parser:
    """Parse KiCAD v6+ .kicad_sch files (S-expression format)."""

    SCALE_FACTOR = 39.37  # mm to cm (KiCAD v6 uses mm)

    def __init__(self):
        self.components: List[Component] = []
        self.wires: List[Wire] = []

    def parse_file(self, filename: str):
        """Parse a KiCAD v6 .kicad_sch file."""
        with open(filename, 'r') as f:
            content = f.read()
            self._parse_content(content)

    def parse_string(self, content: str):
        """Parse KiCAD v6 content from string."""
        self._parse_content(content)

    def _parse_content(self, content: str):
        """Parse KiCAD v6 S-expression content."""

        # Extract component instances (symbols)
        # Pattern: (symbol (lib_id "Library:Name") (at x y rotation) ... (property "Reference" "R1") ... (property "Value" "1k") ...)
        symbol_pattern = r'\(symbol\s*\([^)]*lib_id\s*"([^"]+)"[^)]*\)\s*\(at\s+([-+]?\d+\.?\d*)\s+([-+]?\d+\.?\d*)\s+(\d+)\)(.*?)\n\s*\)'

        for match in re.finditer(symbol_pattern, content, re.DOTALL):
            lib_id = match.group(1)
            x = int(float(match.group(2)))
            y = int(float(match.group(3)))
            rotation = int(match.group(4))
            symbol_body = match.group(5)

            # Extract properties
            reference = self._extract_property(symbol_body, "Reference")
            raw_value = self._extract_property(symbol_body, "Value")

            if reference:
                # Extract device name from lib_id (e.g., "Simulation_SPICE:VDC" -> "VDC")
                if ':' in lib_id:
                    device_name = lib_id.split(':')[1]
                else:
                    device_name = lib_id

                # Clean up reference (remove #GND prefix, etc.)
                display_name = reference
                if reference.startswith('#'):
                    display_name = reference.split('_')[0] if '_' in reference else reference

                # Clean value
                value = self._clean_value(raw_value, device_name)

                comp = Component(
                    name=display_name,
                    type=device_name,
                    value=value,
                    x=x,
                    y=y,
                    rotation=rotation
                )
                self.components.append(comp)

        # Extract wires
        # KiCAD v6 wire format: (wire ... (pts (xy x1 y1) (xy x2 y2)) ...)
        # Simple approach: find all (xy ...) patterns that are in wire blocks
        wire_blocks = re.finditer(r'\(wire', content)

        for wire_match in wire_blocks:
            # Get the position of this (wire
            start_pos = wire_match.start()

            # Find the matching closing parenthesis for this wire block
            # Count parentheses from the start
            paren_count = 0
            i = start_pos + 5  # Skip "(wire"
            while i < len(content):
                if content[i] == '(':
                    paren_count += 1
                elif content[i] == ')':
                    if paren_count == 0:
                        break
                    paren_count -= 1
                i += 1

            wire_content = content[start_pos:i]

            # Extract (xy x y) pairs from this wire block
            xy_matches = re.findall(r'\(xy\s+([-+]?\d+\.?\d*)\s+([-+]?\d+\.?\d*)\)', wire_content)

            # Create wire segments between consecutive points
            for j in range(len(xy_matches) - 1):
                x1 = int(float(xy_matches[j][0]))
                y1 = int(float(xy_matches[j][1]))
                x2 = int(float(xy_matches[j + 1][0]))
                y2 = int(float(xy_matches[j + 1][1]))

                self.wires.append(Wire(x1, y1, x2, y2))

    def _extract_property(self, content: str, prop_name: str) -> str:
        """Extract a property value from S-expression content."""
        # Pattern to match (property "Name" "Value" ...)
        # Need to handle nested parentheses in the property block
        pattern = r'\(property\s+"' + re.escape(prop_name) + r'"\s*"([^"]*)"'

        # Try to find the property - search in chunks since there might be nested content
        match = re.search(pattern, content)
        if match:
            return match.group(1)

        # Alternative: try multiline search
        pattern = r'\(property\s+"' + re.escape(prop_name) + r'"[^)]*"([^"]*)"'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            return match.group(1)

        return ""

    def _clean_value(self, value: str, device_type: str) -> str:
        """Clean up component value based on device type."""
        # Ground/0V reference has no meaningful value
        if device_type == '0':
            return ''

        # Remove units from value (e.g., "1V" -> "1")
        if value:
            # Try to extract just the numeric part
            import re
            match = re.match(r'([0-9.]+)', value)
            if match:
                return match.group(1)

        return value

    def get_components(self) -> List[Component]:
        """Get all parsed components."""
        return self.components

    def get_wires(self) -> List[Wire]:
        """Get all parsed wires."""
        return self.wires
