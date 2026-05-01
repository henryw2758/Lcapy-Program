"""KiCAD v6+ .kicad_sch file parser."""

import re
from typing import List, Optional, Tuple
from .base_parser import Component, Wire


class KicadV6Parser:
    """Parse KiCAD v6+ .kicad_sch files (S-expression format)."""

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

    def _find_block_end(self, content: str, start: int) -> int:
        """Find the closing paren that matches the opening paren at start."""
        count = 0
        i = start
        while i < len(content):
            if content[i] == '(':
                count += 1
            elif content[i] == ')':
                count -= 1
                if count == 0:
                    return i
            i += 1
        return len(content) - 1

    def _parse_content(self, content: str):
        """Parse KiCAD v6 S-expression content."""

        # --- Parse symbol instances (component placements) ---
        pos = 0
        while True:
            idx = content.find('(symbol', pos)
            if idx == -1:
                break

            # Check if this is a symbol instance (has (lib_id ...) as child)
            # vs a library symbol definition (has string name as child)
            after = content[idx + 7:].lstrip()
            if after.startswith('(lib_id'):
                block_end = self._find_block_end(content, idx)
                block = content[idx:block_end + 1]
                self._parse_symbol(block)
                pos = block_end + 1
            else:
                pos = idx + 7

        # --- Parse wires ---
        for wire_match in re.finditer(r'\(wire', content):
            start_pos = wire_match.start()
            block_end = self._find_block_end(content, start_pos)
            wire_content = content[start_pos:block_end + 1]

            xy_matches = re.findall(r'\(xy\s+([-+]?\d+\.?\d*)\s+([-+]?\d+\.?\d*)\)', wire_content)

            for j in range(len(xy_matches) - 1):
                x1 = float(xy_matches[j][0])
                y1 = float(xy_matches[j][1])
                x2 = float(xy_matches[j + 1][0])
                y2 = float(xy_matches[j + 1][1])
                self.wires.append(Wire(x1, y1, x2, y2))

    def _parse_symbol(self, block: str):
        """Parse a single symbol instance block."""
        lib_id = self._extract_lib_id(block)
        if not lib_id:
            return

        at = self._extract_at(block)
        if at is None:
            return
        x, y, rotation = at

        reference = self._extract_property(block, "Reference")
        value = self._extract_property(block, "Value")

        if not reference:
            return

        # Extract device name from lib_id (e.g., "Simulation_SPICE:VDC" -> "VDC")
        device_name = lib_id.split(':')[-1] if ':' in lib_id else lib_id

        comp = Component(
            name=reference,
            type=device_name,
            value=value,
            x=x,
            y=y,
            rotation=rotation
        )
        self.components.append(comp)

    def _extract_lib_id(self, block: str) -> str:
        """Extract lib_id value from a symbol block."""
        match = re.search(r'\(lib_id\s+"([^"]+)"', block)
        return match.group(1) if match else ""

    def _extract_at(self, block: str) -> Optional[Tuple[float, float, int]]:
        """Extract (at x y rotation) from a symbol block."""
        match = re.search(r'\(at\s+([-+]?\d+\.?\d*)\s+([-+]?\d+\.?\d*)\s+(\d+)\)', block)
        if match:
            return float(match.group(1)), float(match.group(2)), int(match.group(3))
        return None

    def _extract_property(self, block: str, prop_name: str) -> str:
        """Extract a property value from an S-expression block."""
        pattern = r'\(property\s+"' + re.escape(prop_name) + r'"\s*"([^"]*)"'
        match = re.search(pattern, block)
        return match.group(1) if match else ""

    def get_components(self) -> List[Component]:
        """Get all parsed components."""
        return self.components

    def get_wires(self) -> List[Wire]:
        """Get all parsed wires."""
        return self.wires
