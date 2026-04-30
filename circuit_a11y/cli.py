"""Command-line interface for circuit_a11y."""

import argparse
import sys

from . import run, IMAGE_FORMATS


def main():
    parser = argparse.ArgumentParser(
        prog="circuit-a11y",
        description=(
            "Generate an accessible circuit diagram and alt-text description "
            "from a KiCAD schematic and SPICE netlist."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s schematic.kicad_sch circuit.cir
  %(prog)s schematic.kicad_sch circuit.cir -f svg -o output/
  %(prog)s schematic.kicad_sch circuit.cir --no-rename -v
        """,
    )

    parser.add_argument(
        "schematic",
        help="KiCAD schematic file (.kicad_sch or .sch)",
    )
    parser.add_argument(
        "netlist",
        help="SPICE netlist file (.cir, .net, or .spice)",
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default=None,
        help="Output directory (default: same directory as netlist)",
    )
    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=IMAGE_FORMATS,
        default="pdf",
        help="Image output format (default: pdf)",
    )
    parser.add_argument(
        "--no-rename",
        action="store_true",
        help="Keep original node names in alt-text instead of renaming to simple numbers",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show progress information",
    )

    args = parser.parse_args()

    try:
        result = run(
            schematic=args.schematic,
            netlist=args.netlist,
            output_dir=args.output_dir,
            image_format=args.format,
            no_rename=args.no_rename,
            verbose=args.verbose,
        )
        print(f"Image:    {result['image_path']}", file=sys.stderr)
        print(f"Alt-text: {result['alt_text_path']}", file=sys.stderr)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
