# KiCAD to Lcapy Converter

A standalone Python tool that converts KiCAD 6+ schematic files (`.kicad_sch`) into Lcapy-compatible SPICE netlists, with visual output in SVG and PNG formats. Includes a GUI and command-line interface.

## Prerequisites

- **Python 3.8+** — [Download](https://www.python.org/downloads/)
- **Pillow** — Required for PNG output (SVG works without it)
- **KiCAD 6+** — For creating `.kicad_sch` files (not needed to run the converter)

## Quick Start

```bash
# Clone the branch
git clone -b KiCAD-to-Lcapy https://github.com/yourusername/Lcapy-Program.git
cd Lcapy-Program

# Install dependencies
pip install -r requirements.txt

# Run the GUI
python kicad_gui.py

# Or use the command line
python kicad_to_lcapy.py test.kicad_sch
```

Windows users can double-click `run_gui.bat` to launch the GUI.

## Installation

### Step 1: Get the code

```bash
git clone -b KiCAD-to-Lcapy https://github.com/yourusername/Lcapy-Program.git
cd Lcapy-Program
```

### Step 2: Install Python dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `Pillow>=9.0.0` — for PNG image generation

If you only need SVG output and netlists, you can skip this step.

### Step 3: Verify it works

```bash
python kicad_to_lcapy.py test.kicad_sch
```

You should see output like:
```
Converting: test.kicad_sch
Components found:
  V1: V = 1
  R1: R = R_US

Netlist saved: test_netlist.txt
SVG saved: test_output.svg
PNG saved: test_output.png
```

## Usage

### GUI Application

```bash
python kicad_gui.py
```

Or double-click `run_gui.bat` on Windows.

**How to use the GUI:**

1. Click **Browse...** next to "KiCAD File" and select a `.kicad_sch` file
2. The output folder will default to the same directory as the input file — change it if needed
3. Check the output formats you want:
   - **Netlist (.txt)** — Lcapy-compatible SPICE netlist
   - **SVG** — Vector graphic of the schematic
   - **PNG** — Raster image of the schematic (requires Pillow)
   - **PDF** — PDF export (requires Pillow)
4. Click **Convert**
5. A dialog will show which files were created

### Command Line

```bash
python kicad_to_lcapy.py <input.kicad_sch> [output_directory]
```

**Examples:**

```bash
# Convert to same directory as input file
python kicad_to_lcapy.py test.kicad_sch

# Convert to a specific output directory
python kicad_to_lcapy.py test.kicad_sch ./output

# Convert a file in another directory
python kicad_to_lcapy.py /path/to/my/circuit.kicad_sch
```

### Using as a Python Module

You can import the converter into your own Python scripts:

```python
import sys
sys.path.insert(0, '/path/to/Lcapy-Program')

from kicad_converter.converter import KiCADConverter
from kicad_converter.svg_generator import SVGCircuitGenerator, PNGCircuitGenerator

# Parse and convert
converter = KiCADConverter('my_circuit.kicad_sch')
netlist, components = converter.convert()

# Access results
print(netlist)
for ref, comp in components:
    print(f"{ref}: {comp['type']} = {comp['value']} at {comp['at']}")

# Save netlist
converter.save_netlist('output_netlist.txt')

# Generate SVG
svg_gen = SVGCircuitGenerator('my_circuit.kicad_sch')
svg_gen.generate_svg('output.svg')

# Generate PNG (requires Pillow)
png_gen = PNGCircuitGenerator('my_circuit.kicad_sch')
png_gen.generate_png('output.png')
```

**Available classes:**

| Class | Source | Description |
|-------|--------|-------------|
| `KiCADConverter` | `kicad_converter.converter` | Parses schematic, generates netlist |
| `KiCADSchematic` | `kicad_converter.parser` | Low-level S-expression parser |
| `SVGCircuitGenerator` | `kicad_converter.svg_generator` | Creates SVG from schematic |
| `PNGCircuitGenerator` | `kicad_converter.svg_generator` | Creates PNG from schematic |

**KiCADConverter attributes after `convert()`:**

| Attribute | Type | Description |
|-----------|------|-------------|
| `components` | `List[Tuple[str, Dict]]` | List of (reference, component_data) tuples |
| `wires` | `List[Dict]` | Wire segments with `start` and `end` coordinate tuples |
| `junctions` | `List[Tuple[float, float]]` | Junction point coordinates |
| `netlist` | `str` | Generated SPICE netlist text |

**Component data dictionary keys:**

| Key | Type | Description |
|-----|------|-------------|
| `reference` | `str` | Component reference designator (e.g. "R1", "V1") |
| `type` | `str` | Lcapy type code: R, C, L, V, I, or GND |
| `value` | `str` | Component value from schematic |
| `at` | `Tuple[float, float]` | Position in mm (x, y) |
| `rotation` | `float` | Rotation in degrees |
| `lib_id` | `str` | KiCAD library symbol ID |
| `pins` | `List[Dict]` | Pin data from schematic |

## Output Files

The converter generates up to 4 output files (based on the base name of the input):

| File | Format | Description |
|------|--------|-------------|
| `*_netlist.txt` | Text | Lcapy-compatible SPICE netlist |
| `*.svg` | SVG | Vector schematic visualization |
| `*.png` | PNG | Raster schematic visualization |
| `*.pdf` | PDF | PDF export (converted from PNG) |

**Example netlist output** (`test_netlist.txt`):
```
V1 1 2 dc 1
R1 3 4 R_US
```

Format: `<reference> <node1> <node2> [dc] <value>`

## Project Structure

```
Lcapy-Program/
├── README.md                    # This documentation
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies (Pillow)
├── .gitignore                   # Git ignore rules
│
├── kicad_converter/             # Standalone converter package
│   ├── __init__.py              # Exports KiCADConverter, SVGCircuitGenerator, PNGCircuitGenerator
│   ├── parser.py                # S-expression parser (KiCADSchematic, SExprParser)
│   ├── converter.py             # Netlist converter (KiCADConverter)
│   └── svg_generator.py         # SVG/PNG visualization generators
│
├── kicad_gui.py                 # GUI application (tkinter)
├── kicad_to_lcapy.py            # Command-line interface
├── run_gui.bat                  # Windows GUI launcher
├── run_converter.bat            # Windows CLI launcher
│
├── test.kicad_sch               # Test schematic (V1 + R1 circuit)
├── demo.kicad_sch               # Demo schematic
│
└── lcapy/                       # Lcapy library (git submodule, unchanged)
    └── ...                      # https://github.com/mph-/lcapy
```

## How It Works

### 1. Parsing (`kicad_converter/parser.py`)

The `SExprParser` class reads KiCAD's S-expression format (parenthesized text like `(symbol (lib_id "Device:R") ...)`). The `KiCADSchematic` class walks the parsed tree and extracts:

- **Symbols** — Components with library ID, position, rotation, reference, value, and pin data
- **Wires** — Connection lines with start and end coordinate points
- **Junctions** — Connection dots where wires meet

### 2. Conversion (`kicad_converter/converter.py`)

The `KiCADConverter` class:
1. Extracts wires, junctions, and components from parsed data
2. Maps KiCAD library symbols to Lcapy types (see supported components table below)
3. Generates a SPICE netlist with node numbering

### 3. Visualization (`kicad_converter/svg_generator.py`)

`SVGCircuitGenerator` and `PNGCircuitGenerator`:
1. Calculate bounding box from all component/wire coordinates
2. Draw wires as black lines
3. Draw junctions as filled black circles
4. Draw components with schematic-style shapes:
   - **Resistors** — Zigzag pattern (rotated for vertical/horizontal)
   - **Voltage sources** — Circle with + and − labels
   - **Ground** — Standard ground symbol (vertical line + horizontal bars)
5. Label each component with its reference (blue) and value (red)

## Supported Components

| KiCAD Library Symbol | Lcapy Type | Description |
|---------------------|------------|-------------|
| `Device:R` | `R` | Resistor |
| `Device:R_US` | `R` | Resistor (US zigzag symbol) |
| `Device:C` | `C` | Capacitor |
| `Device:L` | `L` | Inductor |
| `Simulation_SPICE:VDC` | `V` | DC Voltage Source |
| `Simulation_SPICE:VAC` | `V` | AC Voltage Source |
| `Simulation_SPICE:IDC` | `I` | DC Current Source |
| `Simulation_SPICE:IAC` | `I` | AC Current Source |
| `Simulation_SPICE:0` | `GND` | Ground reference |

Components with unknown library symbols will be mapped by their reference prefix (R, C, L, V, I) if the reference doesn't start with `#`.

Ground symbols (references starting with `#`, like `#GND01`) are included in the component list and visualization but excluded from the netlist.

## Adding Support for New Components

### Mapping a new KiCAD symbol

Edit `kicad_converter/converter.py` in the `_get_component_type` method:

```python
mapping = {
    'Device:R': 'R',
    'Device:R_US': 'R',
    'Device:C': 'C',
    'Device:L': 'L',
    'Simulation_SPICE:VDC': 'V',
    'YourLibrary:YourSymbol': 'X',  # Add your new mapping
}
```

### Adding a new visual shape

Edit `kicad_converter/svg_generator.py`:

1. Add a draw method to both `SVGCircuitGenerator` and `PNGCircuitGenerator`
2. Add the type check in `_draw_component` (SVG) and the component loop (PNG)

For example, to add a capacitor:

```python
# In SVGCircuitGenerator:
def _draw_capacitor(self, svg, x, y):
    gap = 8
    plate_h = 20
    ET.SubElement(svg, "line", {
        "x1": str(x - gap), "y1": str(y - plate_h),
        "x2": str(x - gap), "y2": str(y + plate_h),
        "stroke": "black", "stroke-width": "3"
    })
    ET.SubElement(svg, "line", {
        "x1": str(x + gap), "y1": str(y - plate_h),
        "x2": str(x + gap), "y2": str(y + plate_h),
        "stroke": "black", "stroke-width": "3"
    })
```

Then add to `_draw_component`:
```python
elif comp_type == "C":
    self._draw_capacitor(g, x, y)
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'kicad_converter'`

You must run scripts from the project root directory, or add the project root to `sys.path`:

```python
import sys
sys.path.insert(0, '/path/to/Lcapy-Program')
```

### `ModuleNotFoundError: No module named 'PIL'`

PNG generation requires Pillow:
```bash
pip install Pillow
```

SVG and netlist generation work without Pillow.

### PNG generation fails but SVG works

Same as above — install Pillow.

### Components are missing from the output

- Check that component references are valid (start with R, C, L, V, or I)
- Check that `lib_id` matches a supported symbol (see Supported Components table)
- Ground symbols are intentionally excluded from the netlist
- Components without a reference or `lib_id` are skipped

### Wires don't connect to component pins

This is a known limitation. The current wire drawing uses exact coordinates from the KiCAD file. Small gaps may appear between wire endpoints and component pin locations. This is cosmetic and does not affect netlist accuracy.

### `File not found` or `Invalid file type`

- Ensure the input file has a `.kicad_sch` extension
- Use the full file path if running from a different directory

## Limitations

- **KiCAD 6+ format only** — Does not support older `.sch` format (KiCAD 5 and below)
- **Sequential node numbering** — Netlist nodes are numbered sequentially (1, 2, 3...) rather than using actual net names from KiCAD
- **No hierarchical schematic support** — Only flat schematics are supported
- **No subcircuit support** — Complex components (op-amps, ICs) are not fully handled
- **Wire-to-component gaps** — Visual output may show small gaps between wires and component pins
- **Basic component shapes only** — Only resistors, voltage sources, and ground have custom shapes; other types show as boxes
- **No net connectivity analysis** — The converter does not trace which pins connect to which nets; node numbering is per-component, not per-net

## Development

### Running a quick test

```bash
python kicad_to_lcapy.py test.kicad_sch
```

### Testing the parser independently

```python
from kicad_converter.parser import KiCADSchematic

schematic = KiCADSchematic('test.kicad_sch')
data = schematic.get_circuit_data()

print(f"Symbols: {len(data['symbols'])}")
print(f"Wires: {len(data['wires'])}")
print(f"Junctions: {len(data['junctions'])}")

for sym in data['symbols']:
    print(f"  {sym.get('reference', '?')}: {sym.get('lib_id', '?')}")
```

### File encoding

All `.kicad_sch` files are read as UTF-8. Output files are written as UTF-8.

### Coordinate system

KiCAD uses millimeters internally. Coordinates are stored as `(x, y)` tuples. The SVG/PNG generators scale coordinates by a factor of 10 (configurable via `SCALE` class attribute) to produce readable output.

## Files You Can Delete

These files are generated at runtime and can be safely deleted:
- `*_netlist.txt` — Generated netlist files
- `*_output.svg` — Generated SVG files
- `*_output.png` — Generated PNG files
- `*.pdf` — Generated PDF files
- `nul` — Windows artifact, safe to delete

The `.gitignore` file is configured to ignore these.

## License

MIT License — see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built for use with the [Lcapy](https://github.com/mph-/lcapy) symbolic circuit analysis library
- KiCAD S-expression format based on [KiCAD documentation](https://dev-docs.kicad.org/en/file-formats/sexpr-schematic/)
