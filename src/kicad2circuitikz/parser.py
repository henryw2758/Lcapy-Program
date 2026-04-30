"""KiCAD .sch file parser - Basic prototype."""

import re
from typing import List, Tuple, Optional
from .base_parser import Component, Wire


class KicadParser:
    """Parse KiCAD v5 .sch files."""

    SCALE_FACTOR = 200  # KiCAD units to cm

    def __init__(self):
        self.components: List[Component] = []
        self.wires: List[Wire] = []
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for parsing."""
        self.pats = {
            'wire': re.compile(r"(wire)", re.IGNORECASE),
            'wirepts': re.compile(r"\s+([-+]?\d+)\s+([-+]?\d+)\s+([-+]?\d+)\s+([-+]?\d+)", re.IGNORECASE),
            'comp': re.compile(r"(\$comp)", re.IGNORECASE),
            'endcomp': re.compile(r"(\$endcomp)", re.IGNORECASE),
            'L': re.compile(r"(L)\s+(.+):\s*(.+)\s+(.+)", re.IGNORECASE),
            'P': re.compile(r"(P)\s+([-+]?\d+)\s+([-+]?\d+)", re.IGNORECASE),
            'F1': re.compile(r"(F\s1)\s+\"(.+)\"", re.IGNORECASE),
            'dir': re.compile(r"^\s+([-+]?\d+)\s+([-+]?\d+)\s+([-+]?\d+)\s+([-+]?\d+)", re.IGNORECASE),
        }

    def parse_file(self, filename: str):
        """Parse a KiCAD .sch file."""
        with open(filename, 'r') as f:
            content = f.read()
            self._parse_content(content)

    def parse_string(self, content: str):
        """Parse KiCAD .sch content from string."""
        self._parse_content(content)

    def _parse_content(self, content: str):
        """Parse KiCAD content."""
        lines = content.split('\n')
        i = 0

        while i < len(lines):
            line = lines[i]

            # Parse wire
            if self.pats['wire'].search(line):
                self._parse_wire(lines, i)
                i += 1

            # Parse component
            elif self.pats['comp'].search(line):
                i = self._parse_component(lines, i)

            i += 1

    def _parse_wire(self, lines: List[str], i: int):
        """Parse a wire segment."""
        if i + 1 < len(lines):
            result = self.pats['wirepts'].search(lines[i + 1])
            if result:
                x1, y1, x2, y2 = [int(result.group(j)) for j in range(1, 5)]
                self.wires.append(Wire(x1, y1, x2, y2))

    def _parse_component(self, lines: List[str], i: int) -> int:
        """Parse a component block. Returns the line index after $endcomp."""
        device = ""
        label = ""
        value = ""
        position: Optional[Tuple[int, int]] = None
        rotation_matrix = [1, 0, 0, 1]

        j = i + 1
        while j < len(lines) and not self.pats['endcomp'].search(lines[j]):
            line = lines[j]

            # Extract device type and label
            result = self.pats['L'].search(line)
            if result:
                device = result.group(3)
                label = result.group(4)

            # Extract position
            result = self.pats['P'].search(line)
            if result:
                position = (int(result.group(2)), int(result.group(3)))

            # Extract value (F1 field)
            result = self.pats['F1'].search(line)
            if result:
                value = result.group(2)

            # Extract rotation matrix
            result = self.pats['dir'].search(line)
            if result:
                rotation_matrix = [int(result.group(k)) for k in range(1, 5)]

            j += 1

        if position and device:
            rotation = self._matrix_to_angle(rotation_matrix)
            comp = Component(label, device, value, position[0], position[1], rotation)
            self.components.append(comp)

        return j  # Return index after $endcomp

    def _matrix_to_angle(self, matrix: List[int]) -> int:
        """Convert rotation matrix to angle in degrees."""
        a, b, c, d = matrix
        if a == 1 and b == 0:
            return 0
        elif a == 0 and b == 1:
            return 270
        elif a == -1 and b == 0:
            return 180
        elif a == 0 and b == -1:
            return 90
        return 0

    def get_components(self) -> List[Component]:
        """Get all parsed components."""
        return self.components

    def get_wires(self) -> List[Wire]:
        """Get all parsed wires."""
        return self.wires
