"""KiCAD to Circuitikz converter - Prototype."""

__version__ = "0.1.0"

from .parser import KicadParser
from .kicad_v6_parser import KicadV6Parser
from .exporter import CircuitikzExporter
from .pdf_exporter import PDFExporter

__all__ = ["KicadParser", "KicadV6Parser", "CircuitikzExporter", "PDFExporter", "parse_schematic"]


def parse_schematic(filename: str):
    """
    Auto-detect and parse a KiCAD schematic file.

    Returns: (components, wires, parser_used)
    """
    if filename.endswith('.kicad_sch'):
        # KiCAD v6+ format
        parser = KicadV6Parser()
        parser.parse_file(filename)
        return parser.get_components(), parser.get_wires(), parser
    else:
        # Assume KiCAD v5 format
        parser = KicadParser()
        parser.parse_file(filename)
        return parser.get_components(), parser.get_wires(), parser
