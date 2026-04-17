# KiCAD to Circuitikz Converter

Convert KiCAD Eeschema schematic files (`.sch`) to high-quality Circuitikz LaTeX drawings and netlists.

## Purpose

This tool extracts the structural information from KiCAD schematics and generates:
1. **Circuitikz LaTeX code** - For use in LaTeX documents or Manim animations
2. **Netlist output** - Component-to-node mapping (no circuit analysis)

**Note**: This is a standalone conversion tool. It does not perform circuit analysis or calculations.

## Features

- **KiCAD v5 support** - Parse `.sch` files from KiCAD 5.x
- **KiCAD v6+ support** - Parse `.kicad_sch` files from KiCAD 6+ (planned)
- **Component mapping** - Automatic conversion to Circuitikz equivalents
- **Multiple output formats**:
  - Raw LaTeX with Circuitikz code
  - Manim-compatible MathTex format
  - Simple netlist (component-node mapping)
- **Supported components**:
  - Passive: Resistors, Capacitors, Inductors
  - Sources: Voltage (DC, AC), Current (DC, AC)
  - Semiconductors: Diodes, LEDs, Transistors (NPN, NMOS)
  - Symbols: Ground, power rails

## Installation

```bash
# Clone the repository
git clone <repo-url>
cd kicad2circuitikz

# Install (coming soon)
pip install .
```

## Usage (Planned)

```bash
# Convert KiCAD schematic to Circuitikz
kicad2circuitikz input.sch -o output.tex

# Generate netlist only
kicad2circuitikz input.sch --netlist -o output.net

# Manim format
kicad2circuitikz input.sch --manim -o output.py
```

## Example

### Input (KiCAD v5 .sch)
```
$comp
L Device:R R1
U 1 1 61234567
P 5000 3000
F 0 "R1" V 4793 3000 50  0000 C CNN
F 1 "1k" V 4884 3000 50  0000 C CNN
	1    5000 3000
	1    0    0    -1
$endcomp
```

### Output (Circuitikz)
```latex
\begin{circuitikz}
  \draw (25.00,-15.00) to[R, l=$R1$, a=$1k$] (25.00,-16.50);
\end{circuitikz}
```

### Output (Netlist)
```
R1 N1 N2 1k
```

## Project Structure

```
src/kicad2circuitikz/
├── parsers/      # KiCAD file parsers (v5, v6)
├── mappers/      # Component and coordinate mapping
├── exporters/    # Output generators (Circuitikz, netlist)
└── cli.py        # Command-line interface
```

## Development

See [ROADMAP.md](ROADMAP.md) for detailed development plan and progress.

## Reference

Based on [uwezi/circuitikz_import](https://github.com/uwezi/circuitikz_import) for KiCAD v5.1.5, with modernization and extensions.

## License

[To be determined]
