# KiCAD to Lcapy Converter

Convert KiCAD 6+ schematic files (.kicad_sch) to Lcapy circuit netlists.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install lcapy in development mode:
```bash
pip install -e lcapy
```

## Usage

### Basic conversion (generates netlist and SVG diagram):
```bash
python kicad2lcapy_cli.py circuit.kicad_sch
```

### Show netlist in console:
```bash
python kicad2lcapy_cli.py circuit.kicad_sch --show-netlist
```

### Save netlist to file without diagram:
```bash
python kicad2lcapy_cli.py circuit.kicad_sch -n output.txt --no-diagram
```

### Generate PNG diagram instead of SVG:
```bash
python kicad2lcapy_cli.py circuit.kicad_sch --format png
```

### Verbose mode:
```bash
python kicad2lcapy_cli.py circuit.kicad_sch --verbose
```

## Command-line options:

- `input` - Path to .kicad_sch file (required)
- `-o, --output` - Output base filename (default: input filename)
- `-f, --format` - Diagram format: svg, png, or pdf (default: svg)
- `-n, --netlist` - Save netlist to file
- `-s, --show-netlist` - Print netlist to console
- `--no-diagram` - Skip diagram generation
- `-v, --verbose` - Show detailed processing info

## Features

- Parses KiCAD 6+ S-expression format
- Extracts component pin coordinates from library definitions
- Handles component rotation (0°, 90°, 180°, 270°)
- Maps component pins to schematic nets using wire coordinates
- Generates Lcapy netlist format
- Supports voltage sources, resistors, capacitors, inductors, and ground connections
- Generates circuit diagrams in SVG, PNG, or PDF

## Supported components

- Resistors (R_US, R)
- Capacitors (C_US, C)
- Inductors (L_US, L)
- Voltage sources (VDC, VAC)
- Current sources (IDC, IAC)
- Ground connections

## Testing

Run the test suite:
```bash
pytest lcapy/lcapy/tests/test_kicad_converter.py -v
```

## License

See LICENSE file for details.
