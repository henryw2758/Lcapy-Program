"""Command-line interface for netlist-to-text."""


import argparse
import sys
from typing import Optional
from .circuit import Circuit
from .parser import detect_format


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Generate descriptive text from circuit netlists for accessibility",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Read SPICE netlist file
  %(prog)s circuit.net
  
  # Read and save to file
  %(prog)s circuit.net -o description.txt
  
  # Auto-detect format
  %(prog)s input_file -f auto
  
  # Force SPICE format
  %(prog)s my_circuit.txt -f spice
        """
    )
    
    parser.add_argument(
        "input",
        help="Input file (SPICE netlist or Lcapy script)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=str,
        help="Output file (default: print to stdout)"
    )
    
    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=["spice", "lcapy", "auto"],
        default="auto",
        help="Input format (default: auto-detect)"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show parsing details and debug information"
    )
    
    parser.add_argument(
        "--no-rename",
        action="store_true",
        help="Keep original node names instead of renaming complex ones to simple numbers"
    )
    
    args = parser.parse_args()
    
    # Create circuit object
    circuit = Circuit()
    
    # Detect format if auto
    input_format = args.format
    if input_format == "auto":
        input_format = detect_format(args.input)
        if args.verbose:
            print(f"Detected format: {input_format}", file=sys.stderr)
        
        if input_format == "unknown":
            print("Error: Could not detect input format. Please specify with -f option.", 
                  file=sys.stderr)
            sys.exit(1)
    
    # Parse input
    try:
        if input_format == "lcapy":
            # Try to import and parse Lcapy script
            try:
                import importlib.util
                spec = importlib.util.spec_from_file_location("lcapy_script", args.input)
                lcapy_module = importlib.util.module_from_spec(spec)
                
                # Execute the module to populate its namespace
                spec.loader.exec_module(lcapy_module)
                
                # Try to find a Circuit or netlist variable
                lcapy_cct = None
                for attr_name in dir(lcapy_module):
                    attr = getattr(lcapy_module, attr_name)
                    # Check if it's a Lcapy circuit object
                    if hasattr(attr, 'elements') and hasattr(attr, 'nodes'):
                        lcapy_cct = attr
                        break
                
                if lcapy_cct is None:
                    print("Error: Could not find a Lcapy Circuit object in the script.", 
                          file=sys.stderr)
                    sys.exit(1)
                
                if args.verbose:
                    print(f"Loaded Lcapy circuit with {len(lcapy_cct.elements)} elements", 
                          file=sys.stderr)
                
                success = circuit.from_lcapy(lcapy_cct)
                if not success:
                    print("Error: Failed to parse Lcapy circuit.", file=sys.stderr)
                    sys.exit(1)
                    
            except ImportError:
                print("Error: Lcapy not installed. Install with: pip install lcapy", 
                      file=sys.stderr)
                print("Or use SPICE format instead.", file=sys.stderr)
                sys.exit(1)
            except Exception as e:
                print(f"Error loading Lcapy script: {e}", file=sys.stderr)
                sys.exit(1)
        
        else:  # SPICE format
            if args.verbose:
                print(f"Parsing SPICE netlist: {args.input}", file=sys.stderr)
            
            circuit.from_netlist_file(args.input)
    
    except FileNotFoundError:
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)
    
    # Rename complex nodes to simple numbers (default behaviour)
    if not args.no_rename:
        mapping = circuit.rename_nodes()
        if mapping:
            print("Renamed nodes:", file=sys.stderr)
            for original, renamed in mapping.items():
                print(f"  {original} -> {renamed}", file=sys.stderr)
    
    # Generate description
    if args.verbose:
        print(f"Generating description for {len(circuit.elements)} elements...", 
              file=sys.stderr)
    
    description = circuit.generate_description()
    
    # Output
    if args.output:
        try:
            with open(args.output, "w") as f:
                f.write(description)
            if args.verbose:
                print(f"Description written to: {args.output}", file=sys.stderr)
        except IOError as e:
            print(f"Error writing to file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(description)


if __name__ == "__main__":
    main()