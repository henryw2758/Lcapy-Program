"""Simple test script for KiCAD to Circuitikz converter."""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from kicad2circuitikz import KicadParser, CircuitikzExporter


def test_conversion(sch_file: str, output_file: str = None):
    """Test conversion from .sch to Circuitikz."""
    print(f"Parsing {sch_file}...")

    # Parse the .sch file
    parser = KicadParser()
    parser.parse_file(sch_file)

    print(f"Found {len(parser.get_components())} components")
    print(f"Found {len(parser.get_wires())} wires")

    # Print components for debugging
    for comp in parser.get_components():
        print(f"  {comp}")

    # Export to Circuitikz
    exporter = CircuitikzExporter()
    circuitikz_code = exporter.export(
        parser.get_components(),
        parser.get_wires()
    )

    # Output result
    if output_file:
        with open(output_file, 'w') as f:
            f.write(circuitikz_code)
        print(f"\nOutput written to {output_file}")
    else:
        print("\n" + "="*50)
        print(circuitikz_code)
        print("="*50)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test.py <input.sch> [output.tex]")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    test_conversion(input_file, output_file)
