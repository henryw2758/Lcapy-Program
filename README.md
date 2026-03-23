# KiCAD to Lcapy Converter

Convert KiCAD 6+ schematic files (.kicad_sch) to Lcapy circuit netlists and diagrams automatically.

## Features

- **Accurate Conversion**: Parses KiCAD schematic files and generates valid Lcapy netlists
- **Diagram Generation**: Creates SVG and PNG circuit diagrams that match your KiCAD layout
- **Component Support**: Handles resistors, capacitors, inductors, voltage sources, current sources, and ground connections
- **GUI Application**: Simple desktop application - just upload a file and get results
- **CLI Tools**: Command-line interface for automation and scripting

## Installation

### Prerequisites
- Python 3.8+
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd Lcapy-Program
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install lcapy in development mode:
```bash
pip install -e lcapy
```

## Usage

### GUI Application (Recommended)

Run the desktop application:
```bash
python kicad2lcapy_gui.py
```

**How to use:**
1. Click "Browse..." to select your .kicad_sch file
2. (Optional) Choose output directory
3. Select which outputs you want (SVG, PNG, Netlist)
4. Click "CONVERT"
5. Get instant results with netlist preview

**Outputs:**
- `*_netlist.txt` - Lcapy-ready netlist format
- `*_diagram.svg` - Vector diagram (scalable)
- `*_diagram.png` - Raster diagram (high resolution)

### Command-Line Interface

For automated workflows:

```bash
python kicad2lcapy_cli.py circuit.kicad_sch
```

**Options:**
- `-o, --output` - Output filename prefix
- `-f, --format` - Diagram format (svg, png, pdf)
- `-n, --netlist` - Save netlist to file
- `-s, --show-netlist` - Print netlist to console
- `--no-diagram` - Skip diagram generation
- `-v, --verbose` - Detailed output

**Examples:**
```bash
# Generate all outputs
python kicad2lcapy_cli.py circuit.kicad_sch

# Only netlist, no diagrams
python kicad2lcapy_cli.py circuit.kicad_sch --no-diagram

# Show netlist and exit
python kicad2lcapy_cli.py circuit.kicad_sch --show-netlist --no-diagram

# Custom output filename
python kicad2lcapy_cli.py circuit.kicad_sch -o my_circuit
```

## Project Structure

```
├── kicad2lcapy_cli.py          # Command-line interface
├── kicad2lcapy_gui.py          # Desktop GUI application
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── LICENSE                      # License information
│
└── lcapy/
    └── lcapy/
        ├── kicad/               # Main converter module
        │   ├── __init__.py
        │   ├── parser.py        # KiCAD S-expression parser
        │   ├── converter.py     # Netlist generator
        │   ├── component_map.py # Component type mapping
        │   └── diagram_generator.py  # SVG/PNG diagram creation
        │
        └── tests/
            ├── test_kicad_converter.py
            └── test_kicad.sch
```

## How It Works

### 1. Parsing
- Reads KiCAD 6+ S-expression format
- Extracts symbols, wires, junctions, and properties
- Preserves exact component positions and rotations

### 2. Component Mapping
- Maps KiCAD library IDs to Lcapy component types
- Extracts component values from properties
- Handles pin definitions and connections

### 3. Net Tracing
- Traces wires to determine electrical connections
- Groups coordinates into logical networks
- Assigns node names for Lcapy

### 4. Netlist Generation
- Creates Lcapy-compatible netlist format
- Generates node names (n1, n2, gnd, etc.)
- Uses component references and values

### 5. Diagram Generation
- Creates SVG diagram using original KiCAD coordinates
- Scales appropriately for screen display
- Also generates PNG raster version
- No LaTeX required

## Supported Components

| Component | KiCAD Symbols | Lcapy Type |
|-----------|--------------|-----------|
| Resistor | R_US, R | R |
| Capacitor | C_US, C | C |
| Inductor | L_US, L, L_Iron | L |
| Voltage Source | VDC, VAC, Battery_Cell | V |
| Current Source | IDC, IAC | I |
| Ground | GND, 0 | 0 (node 0) |
| Diode | D, D_US | D |

## Output Format

### Netlist Example
```
V1 n1 n2 dc 1
R1 n2 n3 1k
```

### SVG Diagram
- Vector-based, scalable
- Shows component symbols, wires, and connections
- Matches original KiCAD layout
- Can be edited in any SVG editor

### PNG Diagram
- Raster image, high resolution
- Ready for presentations and reports
- Matches SVG layout

## Troubleshooting

**"No file selected" error**
- Make sure file ends with `.kicad_sch`
- File must be KiCAD 6.0+

**Diagram generation fails but netlist works**
- Netlist is still valid for Lcapy
- Check that Pillow is installed: `pip install Pillow`

**Missing components in diagram**
- Unsupported component types are skipped
- Check supported components list above

## Testing

Run the test suite:
```bash
pytest lcapy/lcapy/tests/test_kicad_converter.py -v
```

## License

See LICENSE file for details.

## Contributing

Contributions welcome! Please ensure:
- Code follows existing style
- Tests pass: `pytest lcapy/lcapy/tests/`
- Documentation is updated

## Support

For issues or questions, please open an issue on the project repository.
