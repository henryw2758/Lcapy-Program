# How to Test the KiCAD-to-Lcapy CLI

## Quick Start - Copy & Paste These Commands

### Step 1: Navigate to the lcapy directory
```cmd
cd C:\VT\GitHub\Lcapy-Program\lcapy
```

### Step 2: Run the converter on the test file
```cmd
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --show-netlist
```

**Expected output:**
```
Loading KiCAD file: lcapy/tests/test_kicad.sch
Netlist saved to: test_kicad_netlist.txt
Generated Lcapy Netlist:
==================================================
V1 1 0 dc 1
R1 1 0 R_US
==================================================
```

---

## Step-by-Step Testing

### Test 1: Basic Conversion
**Command:**
```cmd
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch
```

**What happens:**
- Reads the test KiCAD file
- Converts to netlist
- Generates SVG diagram
- Saves netlist.txt

**Files created:**
- `test_kicad_netlist.txt`
- `test_kicad_diagram.svg`

---

### Test 2: Show Netlist in Console
**Command:**
```cmd
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --show-netlist
```

**Output shows the netlist:**
```
V1 1 0 dc 1
R1 1 0 R_US
```

---

### Test 3: Generate Multiple Formats
**Command:**
```cmd
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --format svg png pdf
```

**Files created:**
- `test_kicad_netlist.txt`
- `test_kicad_diagram.svg`
- `test_kicad_diagram.png`
- `test_kicad_diagram.pdf`

---

### Test 4: Custom Output Filename
**Command:**
```cmd
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --output my_circuit
```

**Files created:**
- `my_circuit_netlist.txt`
- `my_circuit_diagram.svg`

---

### Test 5: Save Netlist Only
**Command:**
```cmd
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --no-diagram
```

**Output:**
- `test_kicad_netlist.txt` (no diagrams)

---

### Test 6: Verbose Mode (See Details)
**Command:**
```cmd
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --verbose
```

**Shows detailed debug output**

---

## Full Example with All Options

```cmd
python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch ^
  --output test_complete ^
  --format svg png pdf ^
  --netlist test_complete_netlist.txt ^
  --show-netlist ^
  --verbose
```

This command:
- Converts the file
- Outputs to `test_complete_*` files
- Generates SVG, PNG, and PDF
- Saves netlist to `test_complete_netlist.txt`
- Shows netlist in console
- Displays verbose debug info

---

## Verify Results

### List generated files:
```cmd
dir /b test_kicad*.* test_complete*.*
```

### View the netlist:
```cmd
type test_kicad_netlist.txt
```

### Check file sizes:
```cmd
dir test_kicad*.* test_complete*.*
```

---

## Test with Your Own KiCAD File

Once you verify the test works, use your own file:

```cmd
python -m lcapy.scripts.kicad_converter YOUR_FILE.kicad_sch --show-netlist
```

Replace `YOUR_FILE.kicad_sch` with your actual KiCAD file path.

---

## Troubleshooting

### Command not found
```cmd
# Make sure you're in the lcapy directory
cd C:\VT\GitHub\Lcapy-Program\lcapy
python -m lcapy.scripts.kicad_converter --help
```

### File not found
```cmd
# Make sure the test file exists
dir lcapy\tests\test_kicad.sch
```

### Module import error
```cmd
# Reinstall in development mode
cd C:\VT\GitHub\Lcapy-Program\lcapy
pip install -e .
```

### PNG/PDF generation fails
```cmd
# Install additional dependencies
pip install cairosvg pillow
```

---

## Success Indicators

✅ **You're successful when you see:**
- Command runs without errors
- Netlist displayed correctly
- Output files are created
- File sizes > 0 bytes

---

## Common Commands Summary

| What you want | Command |
|---|---|
| Basic test | `python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch` |
| See netlist | `python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --show-netlist` |
| All formats | `python -m lcapy.scripts.kicad_converter lcapy/tests/test_kicad.sch --format svg png pdf` |
| Help | `python -m lcapy.scripts.kicad_converter --help` |
| Your file | `python -m lcapy.scripts.kicad_converter YOUR_FILE.kicad_sch` |

---

## Next Steps

1. **Run a test command** from above
2. **Check the output files** created
3. **View the netlist** with `type filename.txt`
4. **Try with your own KiCAD file**

That's it! You're testing the CLI. 🎉
