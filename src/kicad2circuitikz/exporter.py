"""Circuitikz exporter - Convert parsed components to LaTeX."""

from typing import List
from .parser import Component, Wire


class CircuitikzExporter:
    """Export parsed KiCAD data to Circuitikz LaTeX code."""

    # KiCAD device type to Circuitikz type mapping
    DEVICE_MAP = {
        # v5 format
        'R': 'R',
        'C': 'C',
        'L': 'american inductor',
        'D': 'Do',
        'D_ZENER': 'zDo',
        'D_SCHOTTKY': 'sDo',
        'LED': 'leDo',
        'VDC': 'V',
        'VSIN': 'sV',
        'IDC': 'I',
        'ISIN': 'sI',
        'Earth': 'ground',
        # v6 format (Simulation_SPICE:xxx)
        'VDC': 'V',
        'VSIN': 'sV',
        'IDC': 'I',
        'ISIN': 'sI',
        '0': 'ground',
        'R_US': 'R',
        'R_EU': 'european resistor',
    }

    # Component terminal offsets (in KiCAD units)
    TERMINAL_OFFSETS = {
        'R': (0, 150),
        'C': (0, 150),
        'L': (0, 150),
        'VDC': (0, 200),
        'VSIN': (0, 200),
        'IDC': (0, 200),
        'ISIN': (0, 200),
        'D': (150, 0),
        'D_ZENER': (150, 0),
        'D_SCHOTTKY': (150, 0),
        'LED': (150, 0),
    }

    def __init__(self, scale: float = 200.0):
        """
        Initialize exporter.

        Args:
            scale: KiCAD units to cm conversion factor (default: 200)
        """
        self.scale = scale

    def export(self, components: List[Component], wires: List[Wire]) -> str:
        """
        Export components and wires to Circuitikz LaTeX code.

        Args:
            components: List of parsed components
            wires: List of parsed wires

        Returns:
            Circuitikz LaTeX code string
        """
        lines = []
        lines.append(r"\begin{circuitikz}")

        # Export components
        for comp in components:
            lines.append(self._export_component(comp))

        # Export wires
        for wire in wires:
            lines.append(self._export_wire(wire))

        lines.append(r"\end{circuitikz}")

        return '\n'.join(lines)

    def _export_component(self, comp: Component) -> str:
        """Export a single component to Circuitikz."""
        # Map device type to Circuitikz type
        ck_type = self._map_device_type(comp.type)

        # If it's a ground symbol, use node syntax
        if ck_type == 'ground':
            return self._export_ground(comp)

        # Calculate terminal positions based on rotation
        offset = self.TERMINAL_OFFSETS.get(comp.type, (100, 0))
        x1, y1 = self._rotate_point(offset[0], offset[1], comp.rotation)
        x2, y2 = self._rotate_point(-offset[0], -offset[1], comp.rotation)

        # Convert to cm coordinates (flip Y axis)
        x1_cm = (comp.x + x1) / self.scale
        y1_cm = -(comp.y + y1) / self.scale
        x2_cm = (comp.x + x2) / self.scale
        y2_cm = -(comp.y + y2) / self.scale

        # Build Circuitikz command
        label = f"${comp.name}$" if comp.name else ""
        value = f"${comp.value}$" if comp.value else ""

        return f"  \\draw ({x1_cm:.2f},{y1_cm:.2f}) to[{ck_type}, l={label}, a={value}] ({x2_cm:.2f},{y2_cm:.2f});"

    def _export_ground(self, comp: Component) -> str:
        """Export a ground symbol."""
        x_cm = comp.x / self.scale
        y_cm = -comp.y / self.scale
        return f"  \\draw ({x_cm:.2f},{y_cm:.2f}) node[ground, rotate={comp.rotation}]{{}};"

    def _export_wire(self, wire: Wire) -> str:
        """Export a wire segment."""
        x1_cm = wire.x1 / self.scale
        y1_cm = -wire.y1 / self.scale
        x2_cm = wire.x2 / self.scale
        y2_cm = -wire.y2 / self.scale

        return f"  \\draw ({x1_cm:.2f},{y1_cm:.2f}) -- ({x2_cm:.2f},{y2_cm:.2f});"

    def _map_device_type(self, device: str) -> str:
        """Map KiCAD device type to Circuitikz type."""
        # Try exact match first
        if device in self.DEVICE_MAP:
            return self.DEVICE_MAP[device]

        # Try partial match (e.g., "Q_NPN_BCE" should match if we had transistor support)
        for key, value in self.DEVICE_MAP.items():
            if key in device:
                return value

        # Default: return as-is with warning
        print(f"Warning: Unknown device type '{device}', using as-is")
        return device

    def _rotate_point(self, x: int, y: int, rotation: int) -> tuple:
        """Rotate a point by the given angle (degrees)."""
        import math
        rad = math.radians(rotation)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        new_x = round(x * cos_a - y * sin_a)
        new_y = round(x * sin_a + y * cos_a)

        return (new_x, new_y)
