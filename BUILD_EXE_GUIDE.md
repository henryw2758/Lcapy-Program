# Building kicad2lcapy.exe - Complete Guide

## Overview

This guide explains how to build a standalone executable (.exe) from the KiCAD-to-Lcapy converter.

**Benefits of .exe:**
- ✅ No Python installation required for end users
- ✅ No file paths exposed in public repos
- ✅ Single executable file to distribute
- ✅ Works like any other Windows program

---

## Prerequisites

You need the following installed:
1. Python 3.8+ 
2. PyInstaller

## Step 1: Install PyInstaller

Open Command Prompt and run:

```cmd
pip install pyinstaller
```

---

## Step 2: Build the Executable

### Option A: Automatic (Recommended)

```cmd
cd C:\VT\GitHub\Lcapy-Program
python build_exe.py
```

This runs PyInstaller with all the right options and creates `kicad2lcapy.exe`

### Option B: Manual

```cmd
cd C:\VT\GitHub\Lcapy-Program
python -m PyInstaller --onefile --windowed --name kicad2lcapy kicad2lcapy_cli.py
```

---

## Step 3: Find Your Executable

After building, the .exe will be in:

```
C:\VT\GitHub\Lcapy-Program\dist\kicad2lcapy.exe
```

---

## Step 4: Test the Executable

```cmd
cd C:\VT\GitHub\Lcapy-Program\dist

# Basic test
kicad2lcapy.exe --help

# Test with your file
kicad2lcapy.exe circuit.kicad_sch --show-netlist
```

---

## Step 5: Distribute the Executable

You can:
1. **Share the .exe file** - Single file, easy to distribute
2. **Create an installer** - Use NSIS or similar for professional installation
3. **Add to PATH** - Make it available globally

### Making it globally available:

```cmd
# Copy to Python Scripts folder
copy C:\VT\GitHub\Lcapy-Program\dist\kicad2lcapy.exe C:\Users\<YourUsername>\AppData\Local\Python\pythoncore-3.14-64\Scripts\

# Now you can run from anywhere:
kicad2lcapy circuit.kicad_sch
```

---

## Usage

Once you have the .exe:

### Basic conversion:
```cmd
kicad2lcapy circuit.kicad_sch
```

### Show netlist:
```cmd
kicad2lcapy circuit.kicad_sch --show-netlist
```

### All formats:
```cmd
kicad2lcapy circuit.kicad_sch --format svg png pdf
```

### Custom output:
```cmd
kicad2lcapy circuit.kicad_sch --output my_circuit
```

### Get help:
```cmd
kicad2lcapy --help
```

---

## Output Files

When you run the .exe, it creates:

```
circuit_netlist.txt       ← Lcapy netlist (plain text)
circuit_diagram.svg       ← Vector diagram (scalable)
circuit_diagram.png       ← PNG image (if Lcapy installed)
circuit_diagram.pdf       ← PDF (if Lcapy installed)
```

**NO FILE PATHS ARE SHOWN** - Perfect for public repositories!

---

## Privacy Protection

The .exe version:
- ✅ Does NOT expose system file paths
- ✅ Does NOT show Python installation paths
- ✅ Does NOT reveal internal directory structure
- ✅ Safe to use in public/shared environments

Output only shows:
```
[OK] Netlist saved: circuit_netlist.txt
[OK] Diagram saved: circuit_diagram.svg
```

No full file paths!

---

## Troubleshooting

### ".exe not found" after building
The .exe is in the `dist` folder:
```
C:\VT\GitHub\Lcapy-Program\dist\kicad2lcapy.exe
```

### "File cannot open" error
Make sure the .kicad_sch file exists in the same directory or provide full filename:
```cmd
kicad2lcapy ..\path\to\circuit.kicad_sch
```

### Build fails with "ModuleNotFoundError"
Install missing dependencies:
```cmd
pip install numpy sympy networkx matplotlib
```

### .exe file is very large
This is normal - PyInstaller bundles Python and all dependencies. File size: ~50-100 MB

### Want smaller .exe?
Use UPX compression:
```cmd
pip install pyinstaller-upx
python -m PyInstaller --upx-dir=C:\path\to\upx kicad2lcapy_cli.py
```

---

## Distribution Options

### 1. Simple Distribution
Just give users the `.exe` file:
- Easy
- Single file
- No installation needed

### 2. Create Installer (NSIS)
Build a professional installer:
- Download NSIS: http://nsis.sourceforge.net/
- Create installer script
- Users run installer
- Adds to Start Menu

### 3. Portable Version
Create portable version:
- Copy .exe to USB drive
- Run from anywhere
- No installation

---

## Advanced: Code Signing

For production use, sign your .exe (optional):

```cmd
# If you have a code signing certificate
signtool sign /f certificate.pfx /p password kicad2lcapy.exe
```

This adds:
- ✅ Trust/security indicator
- ✅ Author verification
- ✅ No "unknown publisher" warning

---

## Summary

| What You Want | Steps |
|---|---|
| **Just the .exe** | Run `python build_exe.py` → Find in `dist/` folder |
| **Test it works** | Run `kicad2lcapy.exe --help` |
| **Distribute it** | Copy `kicad2lcapy.exe` to users |
| **Global availability** | Copy to Python Scripts folder |
| **Professional installer** | Use NSIS + .exe |

---

## Files Involved

```
kicad2lcapy_cli.py        ← Source code (no paths shown)
build_exe.py              ← Build script
dist/
  └─ kicad2lcapy.exe      ← Final executable
```

---

**That's it! You now have a clean, secure, shareable executable!** 🎉
