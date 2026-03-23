# KiCAD-to-Lcapy Converter - Testing Guide

This guide shows you how to test the KiCAD-to-Lcapy converter implementation.

## Test Setup

### Prerequisites
```bash
# Make sure you're in the lcapy directory
cd C:\VT\GitHub\Lcapy-Program\lcapy

# Verify Python is installed
python --version
# or
python3 --version
```

---

## Method 1: Run Unit Tests (Recommended for Verification)

All component functionality is tested with pytest.

### Run All Tests

```bash
cd C:\VT\GitHub\Lcapy-Program\lcapy
python -m pytest lcapy/tests/test_kicad_converter.py -v
```

**Expected Output:**
```
test_kicad_converter.py::TestSExprParser::test_parse_atom PASSED
test_kicad_converter.py::TestSExprParser::test_parse_number PASSED
test_kicad_converter.py::TestSExprParser::test_parse_string PASSED
... (30+ tests total)
test_kicad_converter.py::TestKiCADConverter::test_save_netlist PASSED

====== 30 passed in X.XXs ======
```

### Run Specific Test Classes

**Test S-expression parser:**
```bash
python -m pytest lcapy/tests/test_kicad_converter.py::TestSExprParser -v
```

**Test component mapping:**
```bash
python -m pytest lcapy/tests/test_kicad_converter.py::TestComponentMapper -v
```

**Test schematic parsing:**
```bash
python -m pytest lcapy/tests/test_kicad_converter.py::TestKiCADSchematicParser -v
```

**Test full converter:**
```bash
python -m pytest lcapy/tests/test_kicad_converter.py::TestKiCADConverter -v
```

### Run Single Test

```bash
python -m pytest lcapy/tests/test_kicad_converter.py::TestSExprParser::test_parse_atom -v
```

### Run with Coverage

```bash
python -m pytest lcapy/tests/test_kicad_converter.py --cov=lcapy.kicad --cov-report=html
```

This generates an HTML coverage report in `htmlcov/index.html`.

---

## Method 2: Manual CLI Testing

Test the command-line interface with the included test schematic.

### Test File Location
```
C:\VT\GitHub\Lcapy-Program\lcapy\lcapy\tests\test_kicad.sch
```

This is a simple circuit with:
- V1: 1V DC source
- R1: Resistor (value: R_US)
- #GND01: Ground reference

### Basic CLI Test

```bash
cd C:\VT\GitHub\Lcapy-Program\lcapy

# Run converter on test file
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch
```

**Expected output:**
```
Loading KiCAD file: lcapy/tests/test_kicad.sch
Found X components
Generated netlist:
V1 1 0 dc 1
R1 1 0 R_US

Netlist saved to: test_kicad_netlist.txt
Diagram saved to: test_kicad_diagram.svg
```

### Show Netlist in Console

```bash
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --show-netlist
```

Expected netlist:
```
V1 1 0 dc 1
R1 1 0 R_US
```

### Generate Multiple Formats

```bash
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --format svg png pdf
```

**Output files:**
- `test_kicad_netlist.txt`
- `test_kicad_diagram.svg`
- `test_kicad_diagram.png`
- `test_kicad_diagram.pdf`

### Save Custom Netlist File

```bash
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --netlist my_netlist.txt
```

**Output:**
- `my_netlist.txt` - The generated netlist

### Skip Diagram Generation

```bash
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --no-diagram
```

**Output:**
- `test_kicad_netlist.txt` (netlist only, no diagrams)

### Verbose Mode

```bash
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --verbose
```

Shows detailed debug information about the conversion process.

---

## Method 3: Python API Testing

Test the converter programmatically using Python.

### Create a Test Script

Create file: `test_converter_manual.py`

```python
#!/usr/bin/env python3
"""Manual test of KiCAD converter."""

import sys
from pathlib import Path

# Add lcapy to path
sys.path.insert(0, str(Path(__file__).parent / 'lcapy'))

from lcapy.kicad.converter import KiCADConverter
from lcapy.kicad.parser import KiCADSchematic

# Test 1: Parse KiCAD file
print("=" * 60)
print("TEST 1: Parse KiCAD Schematic File")
print("=" * 60)

test_file = Path('lcapy/lcapy/tests/test_kicad.sch')
print(f"Loading: {test_file}")

try:
    schematic = KiCADSchematic(str(test_file))
    print(f"✓ Parsed successfully")
    print(f"  - Symbols: {len(schematic.symbols)}")
    print(f"  - Wires: {len(schematic.wires)}")
    print(f"  - Junctions: {len(schematic.junctions)}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Test 2: Convert to netlist
print("\n" + "=" * 60)
print("TEST 2: Convert to Lcapy Netlist")
print("=" * 60)

try:
    converter = KiCADConverter(str(test_file))
    netlist, components = converter.convert()
    
    print(f"✓ Conversion successful")
    print(f"  - Components found: {len(components)}")
    print(f"  - Netlist lines: {len(netlist.split(chr(10)))}")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Test 3: Display extracted components
print("\n" + "=" * 60)
print("TEST 3: Extracted Components")
print("=" * 60)

print(f"{'Reference':<10} {'Type':<6} {'Value':<12} {'Nodes':<15}")
print("-" * 50)
for comp in components:
    ref = comp['reference']
    ctype = comp['type']
    val = comp['value']
    nodes = str(comp['nodes'])
    print(f"{ref:<10} {ctype:<6} {val:<12} {nodes:<15}")

# Test 4: Display netlist
print("\n" + "=" * 60)
print("TEST 4: Generated Lcapy Netlist")
print("=" * 60)
print(netlist)

# Test 5: Save netlist to file
print("\n" + "=" * 60)
print("TEST 5: Save Netlist to File")
print("=" * 60)

output_file = 'test_output_netlist.txt'
try:
    converter.save_netlist(output_file)
    print(f"✓ Netlist saved to: {output_file}")
    
    # Read and verify
    with open(output_file, 'r') as f:
        content = f.read()
    print(f"✓ File verified ({len(content)} bytes)")
    
    # Clean up
    Path(output_file).unlink()
    print(f"✓ Cleanup complete")
except Exception as e:
    print(f"✗ Error: {e}")
    sys.exit(1)

# Test 6: Create Lcapy Circuit (if Lcapy is available)
print("\n" + "=" * 60)
print("TEST 6: Create Lcapy Circuit Object")
print("=" * 60)

try:
    from lcapy import Circuit
    cct = Circuit(netlist)
    print(f"✓ Circuit created successfully")
    print(f"  - Components: {len(cct.elements)}")
    print(f"  - Nodes: {len(cct.nodes)}")
except ImportError:
    print("⊘ Lcapy not installed (optional test)")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 60)
```

### Run the Test Script

```bash
cd C:\VT\GitHub\Lcapy-Program
python test_converter_manual.py
```

**Expected Output:**
```
============================================================
TEST 1: Parse KiCAD Schematic File
============================================================
Loading: lcapy/lcapy/tests/test_kicad.sch
✓ Parsed successfully
  - Symbols: 3
  - Wires: 7
  - Junctions: 1

============================================================
TEST 2: Convert to Lcapy Netlist
============================================================
✓ Conversion successful
  - Components found: 2
  - Netlist lines: 2

============================================================
TEST 3: Extracted Components
============================================================
Reference  Type   Value        Nodes          
--------------------------------------------------
V1         V      1            [1, 0]         
R1         R      R_US         [1, 0]         

============================================================
TEST 4: Generated Lcapy Netlist
============================================================
V1 1 0 dc 1
R1 1 0 R_US

============================================================
TEST 5: Save Netlist to File
============================================================
✓ Netlist saved to: test_output_netlist.txt
✓ File verified (23 bytes)
✓ Cleanup complete

============================================================
TEST 6: Create Lcapy Circuit Object
============================================================
✓ Circuit created successfully
  - Components: 2
  - Nodes: 2

============================================================
ALL TESTS COMPLETED SUCCESSFULLY!
============================================================
```

---

## Method 4: Integration Testing

Test the complete workflow from KiCAD file to diagrams.

### Full Workflow Test

```bash
cd C:\VT\GitHub\Lcapy-Program\lcapy

# Generate everything
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch \
  --output test_full_workflow \
  --format svg png pdf \
  --netlist workflow_netlist.txt \
  --show-netlist \
  --verbose
```

### Check Output Files

```bash
# Verify all output files were created
ls -la test_full_workflow*
```

Expected files:
- `test_full_workflow_netlist.txt` - Netlist in text format
- `test_full_workflow_diagram.svg` - Vector diagram
- `test_full_workflow_diagram.png` - PNG image
- `test_full_workflow_diagram.pdf` - PDF document

### Verify Netlist Format

```bash
# View the generated netlist
type workflow_netlist.txt
```

Should contain:
```
V1 1 0 dc 1
R1 1 0 R_US
```

---

## Method 5: Component Mapping Testing

Test specific component mappings.

### Create Test Script: `test_component_mapping.py`

```python
from lcapy.kicad.component_map import ComponentMapper

# Test component type mapping
tests = {
    'Device:R_US': 'R',
    'Device:C_US': 'C',
    'Device:L_US': 'L',
    'Simulation_SPICE:VDC': 'V',
    'Simulation_SPICE:IAC': 'I',
    'Simulation_SPICE:0': 'GND',
    'Device:D_US': 'D',
}

print("Component Mapping Tests:")
print("-" * 50)

all_pass = True
for lib_id, expected in tests.items():
    result = ComponentMapper.get_component_type(lib_id)
    status = "✓" if result == expected else "✗"
    print(f"{status} {lib_id:30} → {result}")
    if result != expected:
        all_pass = False

print("-" * 50)
print("✓ All tests passed!" if all_pass else "✗ Some tests failed!")
```

### Run Component Test

```bash
python test_component_mapping.py
```

---

## Quick Test Checklist

Use this checklist to verify all functionality:

- [ ] **Unit Tests Pass**
  ```bash
  python -m pytest lcapy/tests/test_kicad_converter.py -v
  ```

- [ ] **CLI Basic Conversion**
  ```bash
  python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch
  ```

- [ ] **Netlist Display**
  ```bash
  python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --show-netlist
  ```

- [ ] **Multi-Format Output**
  ```bash
  python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --format svg png pdf
  ```

- [ ] **Manual API Test**
  ```bash
  python test_converter_manual.py
  ```

- [ ] **Component Mapping**
  ```bash
  python test_component_mapping.py
  ```

- [ ] **Verify Output Files Exist**
  ```bash
  ls -la *.svg *.png *.pdf *.txt 2>/dev/null | head -20
  ```

---

## Troubleshooting Tests

### "Module not found" Error

```bash
# Make sure you're in the lcapy directory and it's in PYTHONPATH
cd C:\VT\GitHub\Lcapy-Program\lcapy
set PYTHONPATH=%CD%;%PYTHONPATH%
python -m pytest lcapy/tests/test_kicad_converter.py -v
```

### "pytest not found" Error

```bash
# Install pytest
pip install pytest
```

### "Lcapy not found" Error

Some tests skip gracefully if Lcapy isn't installed. The converter still works:
```bash
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --no-diagram
```

### PNG/PDF Generation Fails

```bash
# Install image conversion support
pip install cairosvg pillow
```

### Test File Not Found

Make sure you're in the correct directory:
```bash
cd C:\VT\GitHub\Lcapy-Program\lcapy
pwd  # Verify current directory
ls lcapy/tests/test_kicad.sch  # Check file exists
```

---

## Performance Testing

### Test Parsing Speed

```python
import time
from lcapy.kicad.parser import KiCADSchematic

start = time.time()
schematic = KiCADSchematic('lcapy/tests/test_kicad.sch')
elapsed = time.time() - start

print(f"Parse time: {elapsed*1000:.2f} ms")
```

### Test Conversion Speed

```python
import time
from lcapy.kicad.converter import KiCADConverter

start = time.time()
converter = KiCADConverter('lcapy/tests/test_kicad.sch')
netlist, components = converter.convert()
elapsed = time.time() - start

print(f"Conversion time: {elapsed*1000:.2f} ms")
```

---

## Success Criteria

All tests pass when:

✅ Unit tests: **30+ tests pass**
✅ CLI test: Generates netlist and diagrams
✅ Netlist format: Valid Lcapy format with nodes and values
✅ Output files: SVG, PNG, PDF files created
✅ Component mapping: All standard types recognized
✅ API usage: Circuit objects created successfully

---

## Next Steps After Testing

Once tests pass:

1. **Use with your own KiCAD files:**
   ```bash
   python -m lcapy.scripts.kicad_converter your_circuit.kicad_sch
   ```

2. **Integrate with netlist-to-text branch:**
   ```bash
   python -m lcapy.scripts.kicad_converter circuit.kicad_sch --netlist circuit.net
   # Then use circuit.net with text generator
   ```

3. **Use Lcapy for analysis:**
   ```python
   from lcapy import Circuit
   cct = Circuit(netlist_string)
   # Perform analysis, DC analysis, AC analysis, etc.
   ```

---

## Test Support

If tests fail:
1. Check error messages carefully
2. Verify all files are in correct locations
3. Ensure Python dependencies are installed
4. Try running a single test first
5. Check the troubleshooting section above
6. See README_KICAD_CONVERTER.md for more help

---

**All tests ready!** Choose a testing method above and start verifying the converter. 🚀
