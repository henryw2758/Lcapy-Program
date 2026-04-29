"""PDF/PNG/SVG exporter using matplotlib (no pdflatex required)."""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List
from .base_parser import Component, Wire
import math
import numpy as np


class PDFExporter:
    """Export circuits to PDF/PNG/SVG using matplotlib (no LaTeX required)."""

    # Component sizes (in KiCAD mm units)
    COMPONENT_SIZE = 2.0
    WIRE_WIDTH = 0.5
    FONT_SIZE = 3

    def __init__(self, scale: float = 0.05):
        """
        Initialize exporter.

        Args:
            scale: Scale factor for coordinates (KiCAD mm to output units)
        """
        self.scale = scale

    def export(self, components: List[Component], wires: List[Wire], filename: str):
        """
        Export circuit to file based on extension.

        Args:
            components: List of components
            wires: List of wires
            filename: Output filename (.pdf, .png, or .svg)
        """
        if filename.endswith('.pdf'):
            self._export_pdf(components, wires, filename)
        elif filename.endswith('.png'):
            self._export_png(components, wires, filename)
        elif filename.endswith('.svg'):
            self._export_svg(components, wires, filename)
        else:
            # Default to PDF
            self._export_pdf(components, wires, filename)

    def _export_pdf(self, components: List[Component], wires: List[Wire], filename: str):
        """Export to PDF."""
        self._export_figure(components, wires, filename, 'pdf', dpi=300)
        print(f"[OK] PDF saved to: {filename}")

    def _export_png(self, components: List[Component], wires: List[Wire], filename: str):
        """Export to PNG."""
        self._export_figure(components, wires, filename, 'png', dpi=300)
        print(f"[OK] PNG saved to: {filename}")

    def _export_svg(self, components: List[Component], wires: List[Wire], filename: str):
        """Export to SVG."""
        self._export_figure(components, wires, filename, 'svg', dpi=300)
        print(f"[OK] SVG saved to: {filename}")

    def _export_figure(self, components: List[Component], wires: List[Wire], filename: str, format: str, dpi: int):
        """Export to figure file."""
        fig, ax = plt.subplots(figsize=(12, 10))

        # Calculate bounds
        all_x = [comp.x for comp in components] + [w.x1 for w in wires] + [w.x2 for w in wires]
        all_y = [comp.y for comp in components] + [w.y1 for w in wires] + [w.y2 for w in wires]

        if not all_x:
            print("[WARNING] No components or wires to draw")
            plt.close(fig)
            return

        # Apply scale and calculate bounds with margin
        x_scaled = [x * self.scale for x in all_x]
        y_scaled = [y * self.scale for y in all_y]

        margin = max(2.0, (max(x_scaled) - min(x_scaled)) * 0.1)
        ax.set_xlim(min(x_scaled) - margin, max(x_scaled) + margin)
        ax.set_ylim(min(y_scaled) - margin, max(y_scaled) + margin)
        ax.set_aspect('equal')

        # Flip Y axis (KiCAD Y is down, matplotlib Y is up)
        ax.invert_yaxis()

        # Remove axes
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

        # Draw wires
        for wire in wires:
            x1 = wire.x1 * self.scale
            y1 = wire.y1 * self.scale
            x2 = wire.x2 * self.scale
            y2 = wire.y2 * self.scale

            ax.plot([x1, x2], [y1, y2], 'k-', linewidth=1.5, solid_capstyle='round')

        # Draw components
        for comp in components:
            self._draw_component(ax, comp)

        plt.tight_layout(pad=0.5)
        plt.savefig(filename, format=format, bbox_inches='tight', pad_inches=0.2, dpi=dpi)
        plt.close(fig)

    def _draw_component(self, ax, comp: Component):
        """Draw a single component."""
        x = comp.x * self.scale
        y = comp.y * self.scale
        angle = comp.rotation

        # Component label
        if comp.name and not comp.name.startswith('#'):
            ax.text(x, y - 0.5, comp.name, fontsize=self.FONT_SIZE,
                   ha='center', va='center', rotation=-angle, bbox=dict(boxstyle='round,pad=0.2', facecolor='white', alpha=0.8))

        # Draw based on type
        if comp.type == 'VDC' or comp.type == 'V':
            self._draw_voltage_source(ax, x, y, angle, comp.value)
        elif comp.type == 'R' or comp.type == 'R_US':
            self._draw_resistor(ax, x, y, angle, comp.value)
        elif comp.type == 'C':
            self._draw_capacitor(ax, x, y, angle, comp.value)
        elif comp.type == 'L':
            self._draw_inductor(ax, x, y, angle, comp.value)
        elif comp.type == '0' or 'GND' in comp.type.upper() or comp.name.startswith('#GND'):
            self._draw_ground(ax, x, y, angle)
        else:
            # Generic component box
            box = patches.Rectangle((x - 0.4, y - 0.4), 0.8, 0.8,
                                  linewidth=1.5, edgecolor='black', facecolor='lightgray', alpha=0.5)
            ax.add_patch(box)
            if comp.value:
                ax.text(x, y + 0.6, comp.value, fontsize=self.FONT_SIZE-1,
                       ha='center', va='center', rotation=-angle)

    def _draw_voltage_source(self, ax, x, y, angle, value):
        """Draw a voltage source symbol."""
        circle = patches.Circle((x, y), 0.5, linewidth=1.5, edgecolor='black', facecolor='white')
        ax.add_patch(circle)

        # Draw + and - signs
        sign_offset = 0.2
        if angle == 0:
            ax.text(x, y + sign_offset, '+', fontsize=self.FONT_SIZE+2, ha='center', va='center', weight='bold')
            ax.text(x, y - sign_offset, '-', fontsize=self.FONT_SIZE+2, ha='center', va='center', weight='bold')
        elif angle == 90:
            ax.text(x - sign_offset, y, '+', fontsize=self.FONT_SIZE+2, ha='center', va='center', weight='bold')
            ax.text(x + sign_offset, y, '-', fontsize=self.FONT_SIZE+2, ha='center', va='center', weight='bold')
        elif angle == 180:
            ax.text(x, y - sign_offset, '+', fontsize=self.FONT_SIZE+2, ha='center', va='center', weight='bold')
            ax.text(x, y + sign_offset, '-', fontsize=self.FONT_SIZE+2, ha='center', va='center', weight='bold')
        elif angle == 270:
            ax.text(x + sign_offset, y, '+', fontsize=self.FONT_SIZE+2, ha='center', va='center', weight='bold')
            ax.text(x - sign_offset, y, '-', fontsize=self.FONT_SIZE+2, ha='center', va='center', weight='bold')

        if value:
            ax.text(x + 0.8, y, value, fontsize=self.FONT_SIZE-1,
                   ha='left', va='center', rotation=-angle, bbox=dict(boxstyle='round,pad=0.1', facecolor='yellow', alpha=0.3))

    def _draw_resistor(self, ax, x, y, angle, value):
        """Draw a resistor symbol."""
        # Simple zigzag pattern
        length = 1.2
        n_zigs = 5
        zig_height = 0.2

        # Calculate zigzag points
        points = []
        for i in range(n_zigs + 1):
            px = -length/2 + (length / n_zigs) * i
            py = zig_height if i % 2 == 1 and i not in [0, n_zigs] else -zig_height if i % 2 == 0 and i not in [0, n_zigs] else 0
            points.append((px, py))

        # Rotate points
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)
        rotated_points = []
        for px, py in points:
            rx = px * cos_a - py * sin_a + x
            ry = px * sin_a + py * cos_a + y
            rotated_points.append((rx, ry))

        # Draw zigzag
        xs, ys = zip(*rotated_points)
        ax.plot(xs, ys, 'k-', linewidth=1.5, solid_capstyle='round')

        # Draw leads
        lead_length = 0.4
        x1, y1 = rotated_points[0]
        x2, y2 = rotated_points[-1]

        # Extend first lead
        dx1 = -lead_length * cos_a
        dy1 = -lead_length * sin_a
        ax.plot([x1 - dx1, x1], [y1 - dy1, y1], 'k-', linewidth=1.5, solid_capstyle='round')

        # Extend second lead
        dx2 = lead_length * cos_a
        dy2 = lead_length * sin_a
        ax.plot([x2, x2 + dx2], [y2, y2 + dy2], 'k-', linewidth=1.5, solid_capstyle='round')

        if value:
            ax.text(x, y + 0.4, value, fontsize=self.FONT_SIZE-1,
                   ha='center', va='center', rotation=-angle, bbox=dict(boxstyle='round,pad=0.1', facecolor='yellow', alpha=0.3))

    def _draw_capacitor(self, ax, x, y, angle, value):
        """Draw a capacitor symbol."""
        # Two parallel plates
        plate_width = 0.8
        plate_height = 0.05
        gap = 0.2

        # Calculate plate positions
        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        # Top plate
        for dx in [-plate_width/2, plate_width/2]:
            px = x + (dx * cos_a - gap/2 * sin_a)
            py = y + (dx * sin_a + gap/2 * cos_a)
            ax.plot([x + (dx * cos_a - (gap/2+plate_height) * sin_a),
                    x + (dx * cos_a - (gap/2-plate_height) * sin_a)],
                   [y + (dx * sin_a + (gap/2+plate_height) * cos_a),
                    y + (dx * sin_a + (gap/2-plate_height) * cos_a)],
                   'k-', linewidth=2, solid_capstyle='round')

        # Bottom plate
        for dx in [-plate_width/2, plate_width/2]:
            ax.plot([x + (dx * cos_a + (gap/2+plate_height) * sin_a),
                    x + (dx * cos_a + (gap/2-plate_height) * sin_a)],
                   [y + (dx * sin_a - (gap/2+plate_height) * cos_a),
                    y + (dx * sin_a - (gap/2-plate_height) * cos_a)],
                   'k-', linewidth=2, solid_capstyle='round')

        if value:
            ax.text(x + 0.8, y, value, fontsize=self.FONT_SIZE-1,
                   ha='left', va='center', rotation=-angle, bbox=dict(boxstyle='round,pad=0.1', facecolor='yellow', alpha=0.3))

    def _draw_inductor(self, ax, x, y, angle, value):
        """Draw an inductor symbol (loops)."""
        n_loops = 3
        loop_width = 0.8
        loop_height = 0.25

        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        for i in range(n_loops):
            # Draw semi-circle loop
            t = np.linspace(0, math.pi, 30)
            start_x = -loop_width/2 + (loop_width / n_loops) * i
            loop_center_x = start_x + (loop_width / n_loops) / 2

            lx = loop_center_x + (loop_width/n_loops/2) * np.cos(t)
            ly = loop_height * np.sin(t)

            # Rotate and translate
            loop_x, loop_y = [], []
            for j in range(len(t)):
                rx = lx[j] * cos_a - ly[j] * sin_a + x
                ry = lx[j] * sin_a + ly[j] * cos_a + y
                loop_x.append(rx)
                loop_y.append(ry)

            ax.plot(loop_x, loop_y, 'k-', linewidth=1.5, solid_capstyle='round')

        # Draw leads
        lead_length = 0.4
        dx = lead_length * cos_a
        dy = lead_length * sin_a
        ax.plot([x - dx, x], [y - dy, y], 'k-', linewidth=1.5, solid_capstyle='round')
        ax.plot([x, x + dx], [y, y + dy], 'k-', linewidth=1.5, solid_capstyle='round')

        if value:
            ax.text(x, y + 0.4, value, fontsize=self.FONT_SIZE-1,
                   ha='center', va='center', rotation=-angle, bbox=dict(boxstyle='round,pad=0.1', facecolor='yellow', alpha=0.3))

    def _draw_ground(self, ax, x, y, angle):
        """Draw a ground symbol."""
        # Three horizontal lines of decreasing width
        line_lengths = [0.6, 0.4, 0.2]
        line_spacing = 0.15

        rad = math.radians(angle)
        cos_a, sin_a = math.cos(rad), math.sin(rad)

        # Draw vertical line first
        ax.plot([x, x], [y, y - line_spacing], 'k-', linewidth=1.5, solid_capstyle='round')

        # Draw horizontal lines
        for i, length in enumerate(line_lengths):
            y_offset = -(i + 1) * line_spacing
            y_pos = y + y_offset

            # Rotate line
            x1 = x + (-length/2 * cos_a)
            y1 = y_pos + (-length/2 * sin_a)
            x2 = x + (length/2 * cos_a)
            y2 = y_pos + (length/2 * sin_a)

            ax.plot([x1, x2], [y1, y2], 'k-', linewidth=2, solid_capstyle='round')
