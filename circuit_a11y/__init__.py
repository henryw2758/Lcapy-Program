"""circuit_a11y - Accessible circuit visualization pipeline.

Generates high-quality circuit diagrams and accessible alt-text
descriptions from KiCAD schematics and SPICE netlists.
"""

__version__ = "0.1.0"

import os
import sys
from typing import Dict, Optional

IMAGE_FORMATS = ("pdf", "png", "svg", "tex")


def run(
    schematic: str,
    netlist: str,
    output_dir: Optional[str] = None,
    image_format: str = "pdf",
    no_rename: bool = False,
    verbose: bool = False,
) -> Dict[str, str]:
    """Run the accessibility pipeline.

    Parses a KiCAD schematic to produce a circuit image, and parses a
    SPICE netlist to produce accessible alt-text.  Both outputs are
    written to *output_dir*.

    Args:
        schematic: Path to a KiCAD schematic (.kicad_sch or .sch).
        netlist:   Path to a SPICE netlist (.cir, .net, .spice).
        output_dir: Directory for output files.  Defaults to the
                    netlist file's parent directory.
        image_format: One of 'pdf', 'png', 'svg', 'tex'.
        no_rename:  If True, keep original KiCAD-style node names
                    instead of renaming them to simple numbers.
        verbose:    Print progress information to stderr.

    Returns:
        Dict with keys:
            'image_path'      - path to the generated image/tex file
            'alt_text_path'   - path to the generated alt-text file
            'alt_text'        - the alt-text string itself

    Raises:
        FileNotFoundError: If schematic or netlist file doesn't exist.
        ValueError: If image_format is not recognised.
    """
    if image_format not in IMAGE_FORMATS:
        raise ValueError(
            f"Unsupported image format '{image_format}'. "
            f"Choose from: {', '.join(IMAGE_FORMATS)}"
        )

    if not os.path.isfile(schematic):
        raise FileNotFoundError(f"Schematic file not found: {schematic}")
    if not os.path.isfile(netlist):
        raise FileNotFoundError(f"Netlist file not found: {netlist}")

    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(netlist))
    os.makedirs(output_dir, exist_ok=True)

    base = os.path.splitext(os.path.basename(netlist))[0]

    # --- Stage 1: Generate circuit image from schematic ---
    if verbose:
        print(f"[1/2] Generating {image_format.upper()} image from schematic...", file=sys.stderr)

    image_path = _generate_image(schematic, output_dir, base, image_format, verbose)

    if verbose:
        print(f"       Image saved to: {image_path}", file=sys.stderr)

    # --- Stage 2: Generate alt-text from netlist ---
    if verbose:
        print(f"[2/2] Generating alt-text from netlist...", file=sys.stderr)

    alt_text = _generate_alt_text(netlist, no_rename, verbose)

    alt_text_filename = f"{base}_alt_text.txt"
    alt_text_path = os.path.join(output_dir, alt_text_filename)
    with open(alt_text_path, "w") as f:
        f.write(alt_text)

    if verbose:
        print(f"       Alt-text saved to: {alt_text_path}", file=sys.stderr)

    return {
        "image_path": image_path,
        "alt_text_path": alt_text_path,
        "alt_text": alt_text,
    }


def _generate_image(schematic: str, output_dir: str, base: str,
                    image_format: str, verbose: bool) -> str:
    """Parse a KiCAD schematic and export a circuit image.

    Returns the path to the generated file.
    """
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
    from kicad2circuitikz import parse_schematic, CircuitikzExporter, PDFExporter

    components, wires, parser_used = parse_schematic(schematic)

    if verbose:
        print(f"       Parsed {len(components)} components, {len(wires)} wires "
              f"(parser: {type(parser_used).__name__})", file=sys.stderr)

    if image_format == "tex":
        exporter = CircuitikzExporter()
        latex_code = exporter.export(components, wires)
        filename = os.path.join(output_dir, f"{base}.tex")
        with open(filename, "w") as f:
            f.write(latex_code)
        return filename

    exporter = PDFExporter()
    filename = os.path.join(output_dir, f"{base}.{image_format}")
    exporter.export(components, wires, filename)
    return filename


def _generate_alt_text(netlist: str, no_rename: bool,
                       verbose: bool) -> str:
    """Parse a SPICE netlist and generate accessible alt-text.

    Returns the description string.
    """
    from netlist_to_text.circuit import Circuit

    circuit = Circuit()
    circuit.from_netlist_file(netlist)

    if verbose:
        print(f"       Parsed {len(circuit.elements)} elements, "
              f"{len(circuit.nodes)} nodes", file=sys.stderr)

    if not no_rename:
        mapping = circuit.rename_nodes()
        if mapping:
            print("       Renamed nodes:", file=sys.stderr)
            for original, renamed in mapping.items():
                print(f"         {original} -> {renamed}", file=sys.stderr)

    return circuit.generate_description()
