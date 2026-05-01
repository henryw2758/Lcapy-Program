"""Circuitikz exporter - Convert parsed KiCAD v6 components to LaTeX."""

import math
import re
from typing import List
from .base_parser import Component, Wire


class CircuitikzExporter:
    """Export parsed KiCAD v6 data to Circuitikz LaTeX code."""

    SCALE_FACTOR = 4.0  # mm to circuitikz cm (equivalent to sf=0.25: 1/0.25=4.0)
    NORMALIZE_MARGIN = 0.5  # cm

    # Pin distances in KiCAD mm (from symbol library definitions)
    TERMINAL_OFFSETS = {
        'R': (0, 3.81),
        'C': (0, 3.81),
        'L': (0, 3.81),
        'VDC': (0, 5.08),
        'VSIN': (0, 5.08),
        'IDC': (0, 5.08),
        'ISIN': (0, 5.08),
        'D': (3.81, 0),
        'D_Zener': (3.81, 0),
        'D_Schottky': (3.81, 0),
        'LED': (3.81, 0),
    }

    DEVICE_MAP = {
        'R': 'R',
        'C': 'C',
        'L': 'american inductor',
        'D': 'Do',
        'D_Zener': 'zDo',
        'D_Schottky': 'sDo',
        'LED': 'leDo',
        'VDC': 'V',
        'VSIN': 'sV',
        'IDC': 'I',
        'ISIN': 'sI',
        'Earth': 'ground',
        '0': 'ground',
    }

    VOLTAGE_SOURCES = {'V', 'sV'}
    CURRENT_SOURCES = {'I', 'sI'}

    def __init__(self, scale: float = None):
        self.scale = scale if scale is not None else self.SCALE_FACTOR

    def export(self, components: List[Component], wires: List[Wire]) -> str:
        """Export components and wires to Circuitikz LaTeX code."""
        raw_lines = []

        for wire in wires:
            raw_lines.append(self._export_wire(wire))

        for comp in components:
            raw_lines.append(self._export_component(comp))

        normalized = self._normalize_coordinates(raw_lines)

        lines = [r"\begin{circuitikz}[american]"]
        lines.extend("  " + row for row in normalized)
        lines.append(r"\end{circuitikz}")

        return '\n'.join(lines)

    def _export_component(self, comp: Component) -> str:
        """Export a single component to Circuitikz."""
        ck_type = self._map_device_type(comp.type)

        if ck_type == 'ground':
            return self._export_ground(comp)

        offset = self.TERMINAL_OFFSETS.get(comp.type, (0, 3.81))

        # Voltage sources have reversed pin order so the + terminal
        # appears at the first draw coordinate (matching KiCAD convention)
        if ck_type in self.VOLTAGE_SOURCES:
            x1, y1 = self._rotate_point(-offset[0], -offset[1], -comp.rotation)
            x2, y2 = self._rotate_point(offset[0], offset[1], -comp.rotation)
        else:
            x1, y1 = self._rotate_point(offset[0], offset[1], -comp.rotation)
            x2, y2 = self._rotate_point(-offset[0], -offset[1], -comp.rotation)

        x1_cm = (comp.x + x1) / self.scale
        y1_cm = -(comp.y + y1) / self.scale
        x2_cm = (comp.x + x2) / self.scale
        y2_cm = -(comp.y + y2) / self.scale

        label = f"${comp.name}$" if comp.name else ""
        value = f"${comp.value}$" if comp.value else ""

        if ck_type in self.VOLTAGE_SOURCES:
            return f"\\draw ({x1_cm:.4f},{y1_cm:.4f}) to[{ck_type}, v={label}, a={value}] ({x2_cm:.4f},{y2_cm:.4f});"
        elif ck_type in self.CURRENT_SOURCES:
            return f"\\draw ({x1_cm:.4f},{y1_cm:.4f}) to[{ck_type}, i={label}, a={value}] ({x2_cm:.4f},{y2_cm:.4f});"
        else:
            return f"\\draw ({x1_cm:.4f},{y1_cm:.4f}) to[{ck_type}, l={label}, a={value}] ({x2_cm:.4f},{y2_cm:.4f});"

    def _export_ground(self, comp: Component) -> str:
        """Export a ground symbol."""
        x_cm = comp.x / self.scale
        y_cm = -comp.y / self.scale
        rot = int((-comp.rotation) % 360)
        return f"\\draw ({x_cm:.4f},{y_cm:.4f}) node[ground, rotate={rot}]{{}};"

    def _export_wire(self, wire: Wire) -> str:
        """Export a wire segment."""
        x1_cm = wire.x1 / self.scale
        y1_cm = -wire.y1 / self.scale
        x2_cm = wire.x2 / self.scale
        y2_cm = -wire.y2 / self.scale

        return f"\\draw ({x1_cm:.4f},{y1_cm:.4f}) -- ({x2_cm:.4f},{y2_cm:.4f});"

    def _normalize_coordinates(self, lines: List[str]) -> List[str]:
        """Shift all coordinates so the bounding box starts at (margin, margin)."""
        coord_re = re.compile(r'\((-?[0-9]+\.[0-9]+),(-?[0-9]+\.[0-9]+)\)')

        all_x, all_y = [], []
        for line in lines:
            if line.startswith('%'):
                continue
            for mx, my in coord_re.findall(line):
                all_x.append(float(mx))
                all_y.append(float(my))

        if not all_x:
            return lines

        shift_x = self.NORMALIZE_MARGIN - min(all_x)
        shift_y = self.NORMALIZE_MARGIN - min(all_y)

        def replacer(m):
            return '({:.4f},{:.4f})'.format(
                float(m.group(1)) + shift_x,
                float(m.group(2)) + shift_y
            )

        return [coord_re.sub(replacer, line) for line in lines]

    def _map_device_type(self, device: str) -> str:
        """Map KiCAD device type to Circuitikz type."""
        if device in self.DEVICE_MAP:
            return self.DEVICE_MAP[device]

        for key, value in self.DEVICE_MAP.items():
            if key in device:
                return value

        print(f"Warning: Unknown device type '{device}', using as-is")
        return device

    def _rotate_point(self, x: float, y: float, rotation: int) -> tuple:
        """Rotate a point by the given angle (degrees)."""
        rad = math.radians(rotation)
        new_x = x * math.cos(rad) - y * math.sin(rad)
        new_y = x * math.sin(rad) + y * math.cos(rad)
        return (new_x, new_y)
