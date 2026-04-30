# Circuit A11y

Generate accessible circuit diagrams and alt-text descriptions from KiCAD schematics and SPICE netlists.

This project combines three tools:

| Tool | Input | Output |
|------|-------|--------|
| **KiCAD-to-Text** | SPICE netlist (`.cir`, `.net`) | Human-readable circuit description |
| **KiCAD-to-Circuitikz** | KiCAD schematic (`.kicad_sch`, `.sch`) | Circuitikz LaTeX, PDF, PNG, SVG |
| **Circuit A11y** | Schematic + netlist | Image + alt-text `.txt` file |

## Installation

```bash
pip install -e .
```

With optional dependencies:

```bash
pip install -e ".[lcapy]"   # Lcapy integration for netlist-to-text
pip install -e ".[png]"     # Pillow for PNG export
```

## Quick Start

### Generate alt-text from a netlist

```bash
netlist-to-text circuit.cir
netlist-to-text circuit.cir -o description.txt
netlist-to-text circuit.cir --no-rename   # keep original node names
```

### Generate a circuit image from a schematic

```bash
# Via Python API
from kicad2circuitikz import parse_schematic, PDFExporter

components, wires, parser = parse_schematic("schematic.kicad_sch")
exporter = PDFExporter()
exporter.export(components, wires, "output.pdf")

# Via GUI
python gui.py
```

### Run the full accessibility pipeline

```bash
# From a KiCAD schematic + SPICE netlist, produce an image + alt-text
python -m circuit_a11y schematic.kicad_sch circuit.cir

# Choose output format
python -m circuit_a11y schematic.kicad_sch circuit.cir -f svg

# Specify output directory and verbose mode
python -m circuit_a11y schematic.kicad_sch circuit.cir -o output/ -v
```

### Python API

```python
from circuit_a11y import run

result = run(
    schematic="schematic.kicad_sch",
    netlist="circuit.cir",
    output_dir="output/",
    image_format="pdf",
)

print(result["image_path"])     # output/circuit.pdf
print(result["alt_text_path"])  # output/circuit_alt_text.txt
print(result["alt_text"])       # the description string
```

## KiCAD-to-Text

Generate human-readable descriptions from SPICE-like circuit netlists for accessibility purposes.

A Python port of the [NetlistToText](https://github.com/johnjhealy/NetlistToText) Java application, designed to work seamlessly with the [Lcapy](https://github.com/mph-/lcapy) circuit analysis library.

### Features

- **SPICE Netlist Parsing**: Read standard SPICE-like netlist files (`.net`, `.cir`, `.spice`)
- **KiCAD Export Support**: Handles KiCAD's SPICE export format (including `DC`/`AC` value keywords and complex node names like `Net-_R1-Pad1_`)
- **Automatic Node Renaming**: Complex node names are renamed to simple numbers by default, with a mapping printed to stderr
- **Analog Component Support**: Resistors, capacitors, inductors, voltage/current sources, and conductances
- **Connection Analysis**: Automatically detects and describes parallel and series connections
- **Waveform Support**: Handles PULSE, EXP, SINE waveforms and other value specifications

### Supported Components

| Prefix | Type | Unit |
|--------|------|------|
| `R` | Resistor | Ohm |
| `L` | Inductor | Henry |
| `C` | Capacitor | Farad |
| `V` | Voltage source | Volt |
| `I` | Current source | Amp |
| `G` | Conductance | Siemen |

### Example Output

```
There are 4 elements and 3 nodes in this circuit.

Between node 1 and ground, a 1 Volt voltage source labelled V1 is connected.
The positive terminal of the voltage source is connected to node 1 and negative terminal is connected to ground.

Between node 1 and node 2, a 500 Ohm resistor labelled R1 is connected.

Between node 2 and ground, a 1 milli Henry inductor labelled L1 is connected in parallel with a 1 micro Farad capacitor labelled C1.
```

## KiCAD-to-Circuitikz

Parse KiCAD schematic files and export to Circuitikz LaTeX or matplotlib-based images.

### Features

- **KiCAD v5 and v6+ Support**: Parses both legacy `.sch` and modern `.kicad_sch` formats
- **Multiple Output Formats**: LaTeX (Circuitikz), PDF, PNG, SVG
- **GUI**: Tkinter-based graphical interface (`python gui.py`)
- **Auto-Detection**: Automatically detects KiCAD file format version

### Example

```python
from kicad2circuitikz import parse_schematic, CircuitikzExporter, PDFExporter

components, wires, parser = parse_schematic("my_circuit.kicad_sch")

# Export to LaTeX
exporter = CircuitikzExporter()
latex_code = exporter.export(components, wires)

# Export to PDF/PNG/SVG (no LaTeX required)
pdf_exporter = PDFExporter()
pdf_exporter.export(components, wires, "output.pdf")
```

## Circuit A11y Pipeline

The `circuit_a11y` package orchestrates both tools to produce an accessible output from a single command.

### CLI

```
python -m circuit_a11y <schematic> <netlist> [options]
```

| Option | Description |
|--------|-------------|
| `-o DIR`, `--output-dir DIR` | Output directory (default: netlist file's parent) |
| `-f FMT`, `--format FMT` | Image format: `pdf`, `png`, `svg`, `tex` (default: `pdf`) |
| `--no-rename` | Keep original node names in alt-text |
| `-v`, `--verbose` | Show progress information |

## Testing

```bash
pip install pytest
pytest tests/
```

## Project Structure

```
Lcapy-Program/
├── netlist_to_text/             # KiCAD-to-Text: netlist to alt-text
├── src/kicad2circuitikz/       # KiCAD-to-Circuitikz: schematic to image
├── circuit_a11y/                # Pipeline: orchestrates both tools
├── tests/                       # Tests for netlist_to_text
├── fixtures/                    # Sample netlist files
├── gui.py                       # KiCAD-to-Circuitikz GUI
└── setup.py                     # Package configuration
```

## Limitations

- **Analog-only**: Supports 2-terminal analog components only (R, L, C, V, I, G)
- **No multi-terminal**: Does not support transistors, op-amps, switches, etc.
- **SPICE subset**: Supports a subset of SPICE syntax focused on analog components
- **No circuit analysis**: Generates descriptions only, does not perform circuit analysis

## License

CC0-1.0 Universal (Public Domain Dedication)

## Acknowledgments

- Original Java implementation: [johnjhealy/NetlistToText](https://github.com/johnjhealy/NetlistToText)
- Circuit analysis: [Lcapy](https://github.com/mph-/lcapy) by Michael Hayes
