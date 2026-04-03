"""Generate SVG/PNG from KiCAD schematic."""

import xml.etree.ElementTree as ET
import math
from pathlib import Path


class SVGCircuitGenerator:
    """Generate SVG from KiCAD schematic."""
    
    SCALE = 10.0
    WIRE_WIDTH = 2
    VSOURCE_RADIUS = 25.4
    RESISTOR_BODY_HALF = 25.4
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        from .converter import KiCADConverter
        self.converter = KiCADConverter(filepath)
        self.converter.convert()
    
    def generate_svg(self, output_file: str):
        all_points = []
        
        for wire in self.converter.wires:
            all_points.append(wire["start"])
            all_points.append(wire["end"])
        for junction in self.converter.junctions:
            all_points.append(junction)
        for ref, comp in self.converter.components:
            x, y = comp.get("at", (0, 0))
            all_points.append((x, y))
        
        if all_points:
            min_x = min(p[0] for p in all_points) - 30
            max_x = max(p[0] for p in all_points) + 30
            min_y = min(p[1] for p in all_points) - 30
            max_y = max(p[1] for p in all_points) + 30
        else:
            min_x = min_y = 0
            max_x = max_y = 200
        
        width = max_x - min_x
        height = max_y - min_y
        pixel_width = int(width * self.SCALE)
        pixel_height = int(height * self.SCALE)
        
        svg = ET.Element("svg", {
            "width": str(pixel_width),
            "height": str(pixel_height),
            "xmlns": "http://www.w3.org/2000/svg"
        })
        ET.SubElement(svg, "rect", {"width": str(pixel_width), "height": str(pixel_height), "fill": "white"})
        
        g = ET.SubElement(svg, "g", {"transform": f"translate({-min_x * self.SCALE}, {-min_y * self.SCALE})"})
        
        for wire in self.converter.wires:
            x1, y1 = wire["start"]
            x2, y2 = wire["end"]
            self._add_wire(g, x1 * self.SCALE, y1 * self.SCALE, x2 * self.SCALE, y2 * self.SCALE)
        
        for junction in self.converter.junctions:
            self._add_junction(g, junction[0] * self.SCALE, junction[1] * self.SCALE)
        
        for ref, comp in self.converter.components:
            self._draw_component(g, ref, comp)
        
        ET.ElementTree(svg).write(output_file, encoding="utf-8", xml_declaration=True)
        return True
    
    def _add_wire(self, svg, x1, y1, x2, y2):
        ET.SubElement(svg, "line", {
            "x1": str(x1), "y1": str(y1),
            "x2": str(x2), "y2": str(y2),
            "stroke": "black", "stroke-width": str(self.WIRE_WIDTH)
        })
    
    def _add_junction(self, svg, x, y):
        ET.SubElement(svg, "circle", {
            "cx": str(x), "cy": str(y), "r": "5",
            "fill": "black"
        })
    
    def _draw_component(self, svg, ref, comp):
        x, y = comp.get("at", (0, 0))
        rotation = comp.get("rotation", 0)
        comp_type = comp.get("type", "")
        value = comp.get("value", "")
        
        x = x * self.SCALE
        y = y * self.SCALE
        
        adjusted_rotation = rotation
        if comp_type == "R":
            adjusted_rotation = rotation - 90
        
        g = ET.SubElement(svg, "g", {"transform": f"rotate({adjusted_rotation}, {x}, {y})"})
        
        if comp_type == "R":
            self._draw_resistor(g, x, y)
        elif comp_type == "V":
            self._draw_voltage_source(g, x, y)
        elif comp_type == "GND" or "GND" in ref or comp.get("lib_id", "").endswith(":0"):
            self._draw_ground(g, x, y, 25)
        else:
            self._draw_box(g, x, y, 30)
        
        label_offset = 35
        ET.SubElement(g, "text", {
            "x": str(x), "y": str(y - label_offset),
            "text-anchor": "middle", "font-size": "14",
            "font-family": "Arial", "font-weight": "bold", "fill": "blue"
        }).text = ref
        
        if value:
            ET.SubElement(g, "text", {
                "x": str(x), "y": str(y + label_offset + 5),
                "text-anchor": "middle", "font-size": "12",
                "font-family": "Arial", "fill": "red"
            }).text = value
    
    def _draw_resistor(self, svg, x, y):
        half_size = self.RESISTOR_BODY_HALF
        points = []
        num_zigs = 6
        zig_height = half_size * 0.4
        segment_width = (half_size * 2) / num_zigs
        
        for i in range(num_zigs + 1):
            px = x - half_size + (i * segment_width)
            if i == 0 or i == num_zigs:
                py = y
            else:
                py = y + (zig_height if i % 2 == 1 else -zig_height)
            points.append(f"{px:.1f},{py:.1f}")
        
        ET.SubElement(svg, "polyline", {
            "points": " ".join(points),
            "fill": "none", "stroke": "black", "stroke-width": str(self.WIRE_WIDTH)
        })
    
    def _draw_voltage_source(self, svg, x, y):
        radius = self.VSOURCE_RADIUS
        ET.SubElement(svg, "circle", {
            "cx": str(x), "cy": str(y), "r": str(radius),
            "fill": "none", "stroke": "black", "stroke-width": str(self.WIRE_WIDTH)
        })
        ET.SubElement(svg, "text", {
            "x": str(x), "y": str(y - radius * 0.3),
            "text-anchor": "middle", "font-size": "16",
            "font-family": "Arial", "font-weight": "bold", "fill": "black"
        }).text = "+"
        ET.SubElement(svg, "text", {
            "x": str(x), "y": str(y + radius * 0.6),
            "text-anchor": "middle", "font-size": "20",
            "font-family": "Arial", "font-weight": "bold", "fill": "black"
        }).text = "-"
    
    def _draw_ground(self, svg, x, y, size):
        ET.SubElement(svg, "line", {
            "x1": str(x), "y1": str(y - size),
            "x2": str(x), "y2": str(y),
            "stroke": "black", "stroke-width": str(self.WIRE_WIDTH)
        })
        widths = [size, size * 0.7, size * 0.4]
        for i, w in enumerate(widths):
            ET.SubElement(svg, "line", {
                "x1": str(x - w), "y1": str(y + i * 6),
                "x2": str(x + w), "y2": str(y + i * 6),
                "stroke": "black", "stroke-width": str(self.WIRE_WIDTH)
            })
    
    def _draw_box(self, svg, x, y, size):
        ET.SubElement(svg, "rect", {
            "x": str(x - size), "y": str(y - size),
            "width": str(size * 2), "height": str(size * 2),
            "fill": "none", "stroke": "black", "stroke-width": str(self.WIRE_WIDTH)
        })


class PNGCircuitGenerator:
    """Generate PNG from KiCAD schematic."""
    
    SCALE = 10.0
    WIRE_WIDTH = 2
    RESISTOR_LENGTH = 50
    VSOURCE_RADIUS = 25
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        from .converter import KiCADConverter
        self.converter = KiCADConverter(filepath)
        self.converter.convert()
    
    def generate_png(self, output_file: str):
        try:
            from PIL import Image, ImageDraw, ImageFont
        except ImportError:
            raise ImportError("PIL required. Install: pip install Pillow")
        
        all_points = []
        for wire in self.converter.wires:
            all_points.append(wire["start"])
            all_points.append(wire["end"])
        for junction in self.converter.junctions:
            all_points.append(junction)
        for ref, comp in self.converter.components:
            x, y = comp.get("at", (0, 0))
            all_points.append((x, y))
        
        if all_points:
            min_x = min(p[0] for p in all_points) - 30
            max_x = max(p[0] for p in all_points) + 30
            min_y = min(p[1] for p in all_points) - 30
            max_y = max(p[1] for p in all_points) + 30
        else:
            min_x = min_y = 0
            max_x = max_y = 200
        
        width = int((max_x - min_x) * self.SCALE)
        height = int((max_y - min_y) * self.SCALE)
        
        img = Image.new("RGB", (width, height), "white")
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 14)
            font_small = ImageFont.truetype("arial.ttf", 12)
        except:
            font = ImageFont.load_default()
            font_small = font
        
        def tx(x): return int((x - min_x) * self.SCALE)
        def ty(y): return int((y - min_y) * self.SCALE)
        
        for wire in self.converter.wires:
            draw.line([(tx(wire["start"][0]), ty(wire["start"][1])),
                       (tx(wire["end"][0]), ty(wire["end"][1]))], fill="black", width=self.WIRE_WIDTH)
        
        for j in self.converter.junctions:
            r = 5
            draw.ellipse([tx(j[0])-r, ty(j[1])-r, tx(j[0])+r, ty(j[1])+r], fill="black")
        
        for ref, comp in self.converter.components:
            x, y = comp.get("at", (0, 0))
            comp_type = comp.get("type", "")
            value = comp.get("value", "")
            rotation = comp.get("rotation", 0)
            cx, cy = tx(x), ty(y)
            
            if comp_type == "R":
                self._draw_resistor_png(draw, cx, cy, self.RESISTOR_LENGTH, rotation - 90)
            elif comp_type == "V":
                r = self.VSOURCE_RADIUS
                draw.ellipse([cx-r, cy-r, cx+r, cy+r], outline="black", width=self.WIRE_WIDTH)
                draw.text((cx, cy - r//2), "+", fill="black", font=font, anchor="mm")
                draw.text((cx, cy + r//2), "-", fill="black", font=font, anchor="mm")
            elif comp_type == "GND" or "GND" in ref:
                s = 25
                draw.line([(cx, cy-s), (cx, cy)], fill="black", width=self.WIRE_WIDTH)
                for i, w in enumerate([s, int(s*0.7), int(s*0.4)]):
                    draw.line([(cx-w, cy+i*6), (cx+w, cy+i*6)], fill="black", width=self.WIRE_WIDTH)
            
            draw.text((cx, cy-40), ref, fill="blue", font=font, anchor="mm")
            if value:
                draw.text((cx, cy+45), value, fill="red", font=font_small, anchor="mm")
        
        img.save(output_file)
        return True
    
    def _draw_resistor_png(self, draw, x, y, size, rotation):
        rad = math.radians(rotation)
        cos_r, sin_r = math.cos(rad), math.sin(rad)
        
        def rotate_point(px, py):
            dx, dy = px - x, py - y
            return (x + dx * cos_r - dy * sin_r, y + dx * sin_r + dy * cos_r)
        
        points = []
        num_zigs = 6
        zig_height = size * 0.4
        segment_width = (size * 2) / num_zigs
        
        for i in range(num_zigs + 1):
            px = x - size + (i * segment_width)
            if i == 0 or i == num_zigs:
                py = y
            else:
                py = y + (zig_height if i % 2 == 1 else -zig_height)
            points.append(rotate_point(px, py))
        
        for i in range(len(points) - 1):
            draw.line([points[i], points[i+1]], fill="black", width=self.WIRE_WIDTH)
