#!/usr/bin/env python3
"""
KiCAD to Lcapy Converter
Convert KiCAD schematic files to Lcapy netlists.
"""

import sys
import argparse
from pathlib import Path

# Add lcapy to path
sys.path.insert(0, str(Path(__file__).parent / 'lcapy'))

from lcapy.kicad.converter import KiCADConverter


def main():
    parser = argparse.ArgumentParser(
        description='Convert KiCAD schematic to Lcapy netlist'
    )
    parser.add_argument('input', help='KiCAD schematic file (.kicad_sch)')
    parser.add_argument('-o', '--output', help='Output netlist filename')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # Verify input file
    input_path = Path(args.input)
    if not input_path.exists():
        print(f'Error: File not found: {input_path.name}', file=sys.stderr)
        sys.exit(1)
    
    if not input_path.suffix == '.kicad_sch':
        print(f'Error: File must be .kicad_sch format', file=sys.stderr)
        sys.exit(1)
    
    # Set output filename
    output_file = args.output if args.output else f'{input_path.stem}_netlist.txt'
    
    try:
        if args.verbose:
            print(f'Converting: {input_path.name}')
        
        # Convert
        converter = KiCADConverter(str(input_path))
        netlist, components = converter.convert()
        
        if args.verbose:
            print(f'Found {len(components)} components')
        
        # Save netlist
        converter.save_netlist(output_file)
        
        # Print result
        print(f'Success: Netlist saved to {output_file}')
        print(f'\nNetlist:\n{netlist}')
        
        return 0
    
    except Exception as e:
        print(f'Error: {e}', file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
