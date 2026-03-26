# KiCAD to Lcapy Converter

A Python tool to convert KiCAD schematic files (`.kicad_sch`) to Lcapy netlists with visual output in SVG and PNG formats.

## Features

- Parse KiCAD 6+ S-expression schematic files
- Extract components, wires, and junctions
- Generate Lcapy-compatible netlists
- Create SVG and PNG visualizations of- Simple GUI interface
- Command-line interface

## Requirements

- Python 3.8+
- Pillow (for PNG generation)

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/Lcapy-Program.git
cd Lcapy-Program
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

Or manually:
```bash
pip install Pillow
```

## Usage

### GUI Application (Recommended)

Run the graphical user interface:

```bash
python kicad_gui.py
```

Or on Windows:
```bash
run_gui.bat
```

**GUI Steps:**
1. Click "Browse" to select a `.kicad_sch` file
2. Choose output options (netlist, SVG, PNG)
3. Click "Convert" to generate outputs
4. Files will be created in the same directory as the input file

### Command Line

```bash
python kicad_to_lcapy.py <input.kicad_sch> [output_directory]
```

Or on Windows:
```bash
run_converter.bat
```

## Output Files

The converter generates:

- `*_netlist.txt` - Lcapy-compatible netlist
- `*_output.svg` - SVG schematic visualization
- `*_output.png` - PNG schematic visualization (if Pillow is installed)

### Example

```bash
python kicad_gui.py
# Select: test.kicad_sch
# Output: test_netlist.txt, test_output.svg, test_output.png
```

## Project Structure

```
Lcapy-Program/
├── README.md                   # This file
├── LICENSE                     # MIT License
├── requirements.txt            # Python dependencies
├── .gitignore                  # Git ignore rules
├── kicad_gui.py               # GUI application
├── kicad_to_lcapy.py           # Command-line converter
├── run_gui.bat                 # GUI launcher (Windows)
├── run_converter.bat           # Converter launcher (Windows)
├── test.kicad_sch             # Test schematic file
├── demo.kicad_sch             # Demo schematic file
└── lcapy/                      # Lcapy library
    └── lcapy/
        └── kicad/              # KiCAD converter module
            ├── __init__.py      # Module initialization
            ├── parser.py        # S-expression parser
            ├── converter.py     # Main converter logic
            └── svg_generator.py # SVG/PNG generation
```

## How It Works

### 1. Parsing (`parser.py`)

Reads KiCAD's S-expression format and extracts:
- Component symbols with positions, rotations, values
- Wire connections with start/end points
- Junction points (connection dots)

### 2. Conversion (`converter.py`)

- Maps KiCAD component types to Lcapy types
- Generates Lcapy-compatible netlist format
- Provides structured component data for visualization

### 3. Visualization (`svg_generator.py`)

- Creates SVG/PNG files showing the schematic
- Draws components with proper shapes:
  - Zigzag resistors
  - Circles for voltage sources (+/- symbols)
  - Ground symbols
- Renders wires and junctions
- Applies rotations and positioning from KiCAD

## Supported Components

| KiCAD Symbol | Lcapy Type | Description |
|--------------|------------|-------------|
| Device:R | R | Resistor |
| Device:R_US | R | Resistor (US symbol) |
| Device:C | C | Capacitor |
| Device:L | L | Inductor |
| Simulation_SPICE:VDC | V | DC Voltage Source |
| Simulation_SPICE:VAC | V | AC Voltage Source |
| Simulation_SPICE:IDC | I | DC Current Source |
| Simulation_SPICE:IAC | I | AC Current Source |
| Simulation_SPICE:0 | GND | Ground |

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'lcapy.kicad'`

**Solution:** Ensure you're running from the project root directory and `lcapy` folder is in the Python path.

```bash
cd Lcapy-Program
python kicad_gui.py
```

### No Output Files Generated

**Problem:** Converter runs but no files are created.

**Solution:** 
- Check the input file is a valid `.kicad_sch` file
- Verify you have write permissions in the output directory
- Look for error messages in the console

### Missing Components in Output

**Problem:** Some components don't appear in the netlist or visualization.

**Solution:**
- Verify component reference prefixes (R, C, L, V, I)
- Check that components have valid lib_id values
- Ground symbols are excluded from netlist but shown in visualization

### PNG Generation Fails

**Problem:** SVG works but PNG generation fails.

**Solution:** Install Pillow:
```bash
pip install Pillow
```

## Example Netlist Output

For a simple circuit with a voltage source and resistor:

```
V1 1 2 dc 1
R1 3 4 R_US
```

## Development

### Running Tests

```bash
cd Lcapy-Program
python -c "from lcapy.kicad.converter import KiCADConverter; c=KiCADConverter('test.kicad_sch'); c.convert(); print(c.get_netlist())"
```

### Adding New Component Types

Edit `converter.py` and add mappings to the `_get_component_type` method:

```python
mapping = {
    'Device:R': 'R',
    'YourLibrary:YourComponent': 'X',  # Add new type
}
```

### Customizing Visualization

Edit `svg_generator.py` to:
- Change component sizes
- Modify drawing styles
- Add new component shapes

## Limitations

- Currently supports KiCAD 6+ format only
- Netlist uses sequential node numbering (not actual net names)
- Complex hierarchical schematics not fully supported
- Some component properties may not be preserved

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built for use with the Lcapy circuit analysis library
- KiCAD S-expression format documentation

## Support

For issues, questions, or feature requests:
- Open an issue on GitHub
- Check existing issues for solutions

---

**Note:** This tool is designed to work with the Lcapy symbolic circuit analysis library. For more information about Lcapy, visit: https://lcapy.readthedocs.io/
