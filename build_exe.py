#!/usr/bin/env python3
"""Build kicad2lcapy.exe using PyInstaller.

Creates a standalone Windows executable from the CLI tool.
"""

import subprocess
import sys
from pathlib import Path

script = Path(__file__).parent / "kicad2lcapy_cli.py"
output_dir = Path(__file__).parent / "dist"

print("Building kicad2lcapy.exe...")
print("=" * 60)

# PyInstaller command
cmd = [
    sys.executable, "-m", "PyInstaller",
    "--onefile",                    # Single executable file
    "--windowed",                   # No console window
    "--name", "kicad2lcapy",       # Output name
    "--distpath", str(output_dir), # Output directory
    str(script)
]

print(f"Command: {' '.join(cmd)}")
print()

result = subprocess.run(cmd)

if result.returncode == 0:
    exe_file = output_dir / "kicad2lcapy.exe"
    print()
    print("=" * 60)
    print("SUCCESS! Executable created:")
    print(f"  {exe_file.name}")
    print()
    print("Usage:")
    print("  kicad2lcapy.exe circuit.kicad_sch")
    print("  kicad2lcapy.exe circuit.kicad_sch --show-netlist")
    print("  kicad2lcapy.exe circuit.kicad_sch --format svg png pdf")
    print()
else:
    print("Build failed!")
    sys.exit(1)
