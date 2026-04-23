# KiCAD to Circuitikz Converter

Convert KiCAD Eeschema schematic files to Circuitikz LaTeX code, PDF, PNG, SVG, and netlist.

> **Status**: Mildly Working Prototype - See [ROADMAP.md](ROADMAP.md) for development progress

## Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

**Requirements:**
- Python 3.8+
- matplotlib (for PDF/PNG/SVG generation)

That's it! No pdflatex, ImageMagick, or other external tools required.

### Running the Tool

#### GUI (Recommended)

```bash
python gui.py
```

The GUI provides:
- **File browser** - Select KiCAD schematic files (.sch or .kicad_sch)
- **Auto-detection** - Automatically detects KiCAD v5 vs v6 format
- **Output selection** - Choose formats: LaTeX, Netlist, PDF, PNG, SVG
- **Progress tracking** - Real-time conversion status
- **Preview** - View generated Circuitikz code

**GUI Features:**
1. **Input Section**
   - Click "Browse..." to select a KiCAD schematic file
   - Supports both `.sch` (v5) and `.kicad_sch` (v6+) formats
   - Output directory and name auto-populate based on input file

2. **Output Format Selection**
   - ☑ **Circuitikz/LaTeX (.tex)** - LaTeX code with Circuitikz commands
   - ☑ **Netlist (.txt)** - Component and wire listing
   - ☑ **PDF (.pdf)** - Vector quality circuit diagram
   - ☑ **PNG (.png)** - High-res raster image (300 DPI)
   - ☐ **SVG (.svg)** - Vector graphics for web

3. **Conversion**
   - Click "Convert" to generate selected formats
   - Progress bar shows conversion status
   - Output area displays messages and preview

4. **Output Area**
   - Shows conversion progress
   - Displays any errors or warnings
   - Shows preview of generated Circuitikz code

#### Command Line

```bash
# Basic usage
python test.py your_file.sch

# Save to specific file
python test.py your_file.sch output.tex
```

## Output Formats

### 1. Circuitikz/LaTeX (.tex)

Generates LaTeX code using the Circuitikz package.

**Use cases:**
- LaTeX documents and papers
- Academic publications
- Manim animations

**Example output:**
```latex
\begin{circuitikz}
  \draw (0.48,-1.52) to[V, l=$V1$, a=1] (0.48,0.47);
  \draw (0.54,-0.57) node[ground, rotate=0]{};
  \draw (0.53,-0.98) to[R, l=$R1$, a=1k] (0.53,0.01);
  \draw (0.55,-0.48) -- (0.58,-0.48);
  ...
\end{circuitikz}
```

**To use in LaTeX:**
```latex
\documentclass{article}
\usepackage{circuitikz}
\begin{document}
  % Paste the generated code here
\end{document}
```

### 2. Netlist (.txt)

Generates a text file listing components and wires.

**Use cases:**
- Understanding circuit structure
- Debugging conversion issues
- Manual circuit analysis

**Example output:**
```
============================================================
NETLIST for: my_circuit.kicad_sch
============================================================

COMPONENTS:
----------------------------------------
  V1         | VDC             | Value: 5V
  R1         | R_US            | Value: 1k
  R2         | R_US            | Value: 2k

WIRES:
----------------------------------------
  Wire  1: ( 110,   97) -> ( 116,   97)
  Wire  2: (  97,   97) -> ( 102,   97)
  Wire  3: ( 107,  110) -> ( 116,  110)
  ...

============================================================
Total: 3 components, 7 wires
============================================================
```

**Note**: This is a component/wire listing, not a full SPICE netlist with node connectivity.

### 3. PDF (.pdf)

Generates a vector PDF circuit diagram using matplotlib.

**Use cases:**
- High-quality print documents
- Vector graphics for publications
- Scalable diagrams

**Features:**
- Vector quality (no pixelation at any zoom)
- No external tools required (matplotlib only)
- Components drawn with standard symbols
- Wires shown as black lines

### 4. PNG (.png)

Generates a high-resolution raster image.

**Use cases:**
- Web pages and presentations
- Quick previews
- Non-vector formats

**Features:**
- 300 DPI for good quality
- Suitable for web and documents
- No external tools required

### 5. SVG (.svg)

Generates scalable vector graphics.

**Use cases:**
- Web graphics (resizable without quality loss)
- Vector graphics software (Inkscape, Illustrator)
- Modern web browsers

**Features:**
- Vector format
- Resizable
- Web-friendly

## How It Works

### File Format Detection

The tool automatically detects KiCAD file format:
- `.sch` → KiCAD v5 parser (text-based format)
- `.kicad_sch` → KiCAD v6+ parser (S-expression format)

### Parsing Process

1. **Read file** - Load the KiCAD schematic
2. **Extract components** - Parse component blocks
   - Extract name (reference designator)
   - Extract type (R, C, L, V, etc.)
   - Extract value (1k, 5V, etc.)
   - Extract position (x, y coordinates)
   - Extract rotation (0°, 90°, 180°, 270°)

3. **Extract wires** - Parse wire segments
   - Start point (x1, y1)
   - End point (x2, y2)

### Export Process

#### For LaTeX/Circuitikz:
1. Map KiCAD component types to Circuitikz types
2. Convert coordinates (KiCAD mm → cm)
3. Flip Y-axis (KiCAD: 0,0 at top-left; Circuitikz: 0,0 at bottom-left)
4. Generate `to[TYPE]` commands for components
5. Generate `\draw --` commands for wires
6. Wrap in `\begin{circuitikz}` block

#### For PDF/PNG/SVG:
1. Use matplotlib to create a figure
2. Draw components as geometric shapes
3. Draw wires as line segments
4. Apply coordinate scaling and Y-axis flip
5. Save in requested format (PDF/PNG/SVG)

## Supported Components

### Passive Components ✅
- **Resistors** (R, R_US) - Zigzag symbol
- **Capacitors** (C) - Parallel plates symbol
- **Inductors** (L) - Loop symbol

### Sources ✅
- **Voltage sources** (VDC, VSIN) - Circle with +/-
- **Current sources** (IDC, ISIN) - Circle with arrow

### Semiconductors ✅
- **Diodes** (D) - Standard diode symbol
- **Zener diodes** (D_ZENER) - Zener symbol
- **Schottky diodes** (D_SCHOTTKY) - Schottky symbol
- **LEDs** (LED) - LED symbol

### Symbols ✅
- **Ground** (GND, 0, Earth) - Ground symbol

### Transistors ⚠️
- **NPN** (Q_NPN) - Basic support, limited rendering
- **NMOS** (Q_NMOS) - Basic support, limited rendering

## Known Limitations

### Positioning
- **Issue**: Component positions are approximate
- **Cause**: Coordinate scaling may not be optimal for all circuits
- **Workaround**: Manual adjustment in LaTeX or using PDF export as reference

### Netlist
- **Issue**: Netlist shows component/wire listing but not actual circuit connectivity
- **Cause**: No node mapping or topology analysis implemented yet
- **Workaround**: Use KiCAD's built-in netlist export for full connectivity

### Complex Circuits
- **Issue**: Multi-page schematics not supported
- **Issue**: Hierarchical sheets not supported
- **Cause**: Parser only handles single-page schematics
- **Workaround**: Export each page separately

### Component Values
- **Issue**: Some component values may not extract correctly
- **Cause**: Value format varies between KiCAD versions
- **Workaround**: Check netlist for extracted values, edit if needed

### Rotation
- **Issue**: Limited rotation support (0°, 90°, 180°, 270° only)
- **Cause**: Arbitrary angles not fully implemented
- **Workaround**: Use only standard rotations in KiCAD

## Troubleshooting

### "No components found"
- **Cause**: File format not recognized or empty schematic
- **Solution**: Check file extension (.sch or .kicad_sch) and ensure schematic has components

### "PDF generation failed"
- **Cause**: matplotlib not installed or import error
- **Solution**: `pip install matplotlib`

### "Circuitikz code won't compile"
- **Cause**: Circuitikz package not installed in LaTeX
- **Solution**: Install circuitikz package: `tlmgr install circuitikz` (TeX Live) or use MiKTeX package manager

### "Components not aligned"
- **Cause**: Coordinate scaling issues
- **Solution**: Try adjusting scale factor in code or use PDF export for reference

### "Wrong component type"
- **Cause**: KiCAD library symbol not in mapping
- **Solution**: Check DEVICE_MAP in exporter.py, add mapping if needed

## Development Status

This is a **mildly working prototype**. See [ROADMAP.md](ROADMAP.md) for:
- Detailed progress tracking
- Phase-by-phase development plan
- Known issues and improvements needed
- Component coverage matrix
- Next steps for contributors

## Example Workflow

1. **Design circuit in KiCAD**
   - Create schematic using supported components
   - Use standard rotations (0°, 90°, 180°, 270°)
   - Keep to single page for now

2. **Export with this tool**
   ```bash
   python gui.py
   # Select your schematic
   # Check desired output formats
   # Click Convert
   ```

3. **Use outputs**
   - **LaTeX**: Paste into your document, compile with pdflatex
   - **PDF**: Use directly in documents or presentations
   - **PNG**: Use in web pages or presentations
   - **SVG**: Edit in vector graphics software
   - **Netlist**: Review for debugging

## Contributing

This is early-stage software. Contributions welcome for:
- Fixing parsing issues
- Improving positioning
- Adding more component types
- Better error messages
- Documentation

See [ROADMAP.md](ROADMAP.md) for detailed development priorities.

## Reference

- Based on [uwezi/circuitikz_import](https://github.com/uwezi/circuitikz_import) for KiCAD v5.1.5
- KiCAD documentation: [kicad.org](https://www.kicad.org/)
- Circuitikz documentation: [CTAN circuitikz](https://ctan.org/pkg/circuitikz)

## License

[To be determined]
