# KiCAD-to-Lcapy Converter - Quick Start Guide

## 30-Second Setup

The KiCAD-to-Lcapy converter is already built and ready to use!

### Files Created:
- ✅ `lcapy/lcapy/kicad/` - Core converter module
- ✅ `lcapy/lcapy/scripts/kicad_converter.py` - CLI tool  
- ✅ `lcapy/lcapy/tests/test_kicad_converter.py` - Test suite
- ✅ `README_KICAD_CONVERTER.md` - Full documentation
- ✅ Test file: `lcapy/lcapy/tests/test_kicad.sch`

## Run It Right Now

### 1. Convert Your KiCAD File

```bash
# From lcapy directory
python -m lcapy.scripts.kicad_converter your_circuit.kicad_sch
```

**Output files:**
- `your_circuit_netlist.txt` - Lcapy netlist format
- `your_circuit_diagram.svg` - Vector diagram
- `your_circuit_diagram.png` - PNG image (300 DPI)
- `your_circuit_diagram.pdf` - PDF document

### 2. Specify Output Formats (Pick What You Want)

```bash
# Generate all formats
python -m lcapy.scripts.kicad_converter circuit.kicad_sch --format svg png pdf

# Generate only SVG
python -m lcapy.scripts.kicad_converter circuit.kicad_sch --format svg

# Generate only PNG
python -m lcapy.scripts.kicad_converter circuit.kicad_sch --format png
```

### 3. See the Generated Netlist

```bash
python -m lcapy.scripts.kicad_converter circuit.kicad_sch --show-netlist
```

Output:
```
V1 1 0 dc 12
R1 1 2 1k
C1 2 0 10u
```

### 4. Use in Python Code

```python
from lcapy.kicad.converter import KiCADConverter
from lcapy import Circuit

# Convert KiCAD file
converter = KiCADConverter('circuit.kicad_sch')
netlist, components = converter.convert()

# Use with Lcapy
cct = Circuit(netlist)
cct.draw('my_circuit.svg')  # Creates SVG diagram
```

## Full CLI Options

```bash
python -m lcapy.scripts.kicad_converter <input.kicad_sch> [options]

Options:
  -o, --output TEXT        Output base filename
  -f, --format [svg|png|pdf]  Output formats (can use multiple)
  -n, --netlist TEXT       Save netlist to file
  -s, --show-netlist       Print netlist to console
  --no-diagram             Skip diagram generation
  -v, --verbose            Verbose output
```

## Typical Workflows

### Workflow 1: Quick Diagram Export
```bash
python -m lcapy.scripts.kicad_converter circuit.kicad_sch
# → circuit_diagram.svg
```

### Workflow 2: Get Netlist for Analysis
```bash
python -m lcapy.scripts.kicad_converter circuit.kicad_sch --show-netlist --netlist my.txt
# → Shows netlist in console + saves to my.txt
```

### Workflow 3: All Formats + Netlist
```bash
python -m lcapy.scripts.kicad_converter circuit.kicad_sch \
  --format svg png pdf \
  --netlist netlist.txt \
  --show-netlist
```

### Workflow 4: Integration with Netlist-to-Text
```bash
# Generate netlist
python -m lcapy.scripts.kicad_converter circuit.kicad_sch --netlist circuit.net

# Use with text generator (future branch)
python text_generator.py circuit.net --output description.txt
```

## Supported Components

The converter automatically recognizes:

| KiCAD Symbol | Lcapy Type | Example |
|---|---|---|
| Device:R_US | R | 1k, 10k, 100k |
| Device:C_US | C | 10u, 100n, 1p |
| Device:L_US | L | 100m, 1u |
| Simulation_SPICE:VDC | V | dc 5, dc 12 |
| Simulation_SPICE:IAC | I | ac 1 |
| Simulation_SPICE:0 | GND | Ground (node 0) |
| Device:D_US | D | Diode |

## Example: Simple RC Circuit

**KiCAD file** contains:
- V1: 5V DC source
- R1: 1kΩ resistor  
- C1: 10µF capacitor
- GND: Ground reference

**Command:**
```bash
python -m lcapy.scripts.kicad_converter rc_circuit.kicad_sch --show-netlist
```

**Output netlist:**
```
V1 1 0 dc 5
R1 1 2 1k
C1 2 0 10u
```

**Generated files:**
- `rc_circuit_diagram.svg` - Circuit diagram
- `rc_circuit_netlist.txt` - Netlist file

## Testing

Run all tests:
```bash
cd lcapy
python -m pytest lcapy/tests/test_kicad_converter.py -v
```

Test specific feature:
```bash
# Test parser only
pytest lcapy/tests/test_kicad_converter.py::TestSExprParser -v

# Test full conversion
pytest lcapy/tests/test_kicad_converter.py::TestKiCADConverter -v
```

## Troubleshooting

### Issue: "File not found"
```bash
# Make sure file exists and path is correct
python -m lcapy.scripts.kicad_converter ./circuits/my_circuit.kicad_sch
```

### Issue: "Unknown component type" warning
- Component is not in the mapping
- Add it to `lcapy/kicad/component_map.py` if using custom symbols
- Or use standard KiCAD library symbols

### Issue: Empty netlist
- Check KiCAD file has components
- Verify components have node connections (wires)
- Use `--verbose` flag for debugging

### Issue: PNG generation fails
```bash
# Install image conversion support
pip install cairosvg pillow
```

## Next: Using Netlists

The generated netlist can be used with:

### Lcapy Analysis
```python
from lcapy import Circuit

cct = Circuit(netlist_text)
print(cct)  # View circuit
# Use Lcapy analysis methods...
```

### Netlist-to-Text Generation
```bash
# Pass netlist to text generator (when available on that branch)
python text_generator.py circuit_netlist.txt --output description.txt
```

## Full Documentation

See `README_KICAD_CONVERTER.md` for:
- Complete API reference
- Advanced options
- Architecture details
- Contributing guide
- Troubleshooting tips

## Key Files

```
lcapy/lcapy/kicad/
├── __init__.py              # Module initialization
├── parser.py                # S-expression parser
├── component_map.py         # Symbol mapping
└── converter.py             # Main converter

lcapy/lcapy/scripts/
└── kicad_converter.py       # CLI tool

lcapy/lcapy/tests/
├── test_kicad_converter.py  # Tests
└── test_kicad.sch           # Test file
```

## That's It!

You're ready to convert KiCAD schematics to Lcapy netlists!

```bash
python -m lcapy.scripts.kicad_converter your_circuit.kicad_sch
```

For questions, see `README_KICAD_CONVERTER.md` 📖

---

**Status**: ✅ Complete and ready to use!
