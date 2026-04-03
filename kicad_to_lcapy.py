#!/usr/bin/env python3
"""KiCAD to Lcapy netlist converter - command line interface"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from kicad_converter.converter import KiCADConverter
from kicad_converter.svg_generator import draw_with_lcapy


def main():
    if len(sys.argv) < 2:
        print("Usage: python kicad_to_lcapy.py <input.kicad_sch> [output_dir]")
        print("\nOptions:")
        print("  input.kicad_sch  - Path to KiCAD schematic file")
        print("  output_dir       - Output directory (default: same as input file)")
        print("\nExample:")
        print("  python kicad_to_lcapy.py mycircuit.kicad_sch")
        print("  python kicad_to_lcapy.py mycircuit.kicad_sch ./output")
        sys.exit(1)

    input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    if not input_file.endswith('.kicad_sch'):
        print(f"Warning: File may not be a KiCAD schematic: {input_file}")

    if len(sys.argv) >= 3:
        output_dir = sys.argv[2]
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    else:
        output_dir = os.path.dirname(input_file) or '.'

    base_name = Path(input_file).stem
    netlist_file = os.path.join(output_dir, f"{base_name}_netlist.txt")
    svg_file = os.path.join(output_dir, f"{base_name}_output.svg")
    png_file = os.path.join(output_dir, f"{base_name}_output.png")

    print(f"Converting: {input_file}")
    print(f"Output directory: {output_dir}")
    print()

    try:
        converter = KiCADConverter(input_file)
        netlist, components = converter.convert()

        print("Components found:")
        for ref, comp in components:
            if comp['type'] != 'GND':
                print(f"  {ref}: {comp['type']} = {comp.get('value', '?')}")
        print()

        converter.save_netlist(netlist_file)
        print(f"Netlist saved: {netlist_file}")
        print(f"Netlist content:")
        print(netlist)
        print()

        draw_with_lcapy(netlist, svg_file, fmt='svg', kicad_file=input_file)
        print(f"SVG saved: {svg_file}")

        try:
            draw_with_lcapy(netlist, png_file, fmt='png', kicad_file=input_file)
            print(f"PNG saved: {png_file}")
        except Exception as e:
            print(f"Note: PNG generation failed: {e}")

        print()
        print("Conversion complete!")

    except Exception as e:
        print(f"Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
