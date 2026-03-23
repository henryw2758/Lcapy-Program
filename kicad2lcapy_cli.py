#!/usr/bin/env python3
"""
KiCAD to Lcapy Converter - CLI Tool

Converts KiCAD schematic files to Lcapy circuit netlists.
Can be built as standalone .exe with no file paths exposed.
"""

import sys
import os
from pathlib import Path
import argparse


def get_base_path():
    """Get base path regardless of how script is run."""
    if getattr(sys, 'frozen', False):
        # Running as compiled exe
        return Path(sys.executable).parent
    else:
        # Running as script
        return Path(__file__).parent


def main():
    parser = argparse.ArgumentParser(
        prog='kicad2lcapy',
        description='Convert your KiCAD schematics to Lcapy netlists',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  kicad2lcapy circuit.kicad_sch
  kicad2lcapy circuit.kicad_sch --format svg png pdf
  kicad2lcapy circuit.kicad_sch --show-netlist
  kicad2lcapy circuit.kicad_sch --no-diagram
        """
    )
    
    parser.add_argument('input', help='Input KiCAD file (.kicad_sch)')
    parser.add_argument('-o', '--output', help='Output base filename')
    parser.add_argument('-f', '--format', nargs='+', 
                       choices=['svg', 'png', 'pdf'], default=['svg'],
                       help='Output formats (default: svg)')
    parser.add_argument('-n', '--netlist', help='Save netlist to file')
    parser.add_argument('-s', '--show-netlist', action='store_true',
                       help='Print netlist to console')
    parser.add_argument('--no-diagram', action='store_true',
                       help='Skip diagram generation')
    parser.add_argument('-v', '--verbose', action='store_true',
                       help='Verbose output')
    
    args = parser.parse_args()
    
    # Validate input file
    input_file = Path(args.input)
    if not input_file.exists():
        print(f"ERROR: File not found: {input_file.name}")
        sys.exit(1)
    
    if not input_file.suffix.lower() == '.kicad_sch':
        print(f"WARNING: File extension is {input_file.suffix}, expected .kicad_sch")
    
    # Set output base
    output_base = args.output if args.output else input_file.stem
    
    # Set netlist file
    netlist_file = args.netlist if args.netlist else f"{output_base}_netlist.txt"
    
    try:
        # Load the converter module
        base = get_base_path()
        sys.path.insert(0, str(base))
        sys.path.insert(0, str(base / 'lcapy'))
        from lcapy.kicad.converter import KiCADConverter
        
        if args.verbose:
            print(f"[*] Processing: {input_file.name}")
        
        # Do the conversion
        converter = KiCADConverter(str(input_file))
        netlist, components = converter.convert()
        
        if args.verbose:
            print(f"[*] Found {len(components)} component(s)")
        
        # Print netlist to console if user asked
        if args.show_netlist:
            print("\nGenerated Netlist:")
            print("=" * 60)
            print(netlist)
            print("=" * 60)
            print()
        
        # Write netlist to file
        converter.save_netlist(netlist_file)
        print(f"[OK] Netlist saved: {netlist_file}")
        
        # Create diagrams in selected formats
        if not args.no_diagram:
            try:
                from lcapy import Circuit
                cct = Circuit(netlist)
                
                for fmt in args.format:
                    output_file = f"{output_base}_diagram.{fmt}"
                    try:
                        cct.draw(output_file)
                        print(f"[OK] Diagram saved: {output_file}")
                    except Exception as e:
                        print(f"[WARN] {fmt.upper()} failed: {e}")
            
            except ImportError:
                print("[WARN] Lcapy not available - skipping diagram generation")
        
        if args.verbose:
            print("[*] Conversion complete!")
        
        print("\nConversion completed successfully!")
        
    except Exception as e:
        print(f"ERROR: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
