#!/usr/bin/env python3
"""Simple direct test of KiCAD converter."""

import sys
from pathlib import Path

# Add paths
repo_root = Path(__file__).parent
lcapy_dir = repo_root / "lcapy"
sys.path.insert(0, str(lcapy_dir))

print("=" * 70)
print("KiCAD-to-Lcapy Converter - Simple Test")
print("=" * 70)
print()

# Test 1: Import converter
print("Test 1: Importing KiCAD converter...")
try:
    from lcapy.kicad.converter import KiCADConverter
    print("[OK] Successfully imported KiCADConverter")
except Exception as e:
    print(f"[FAILED] Failed to import: {e}")
    sys.exit(1)

print()

# Test 2: Load and convert
print("Test 2: Loading and converting KiCAD file...")
test_file = lcapy_dir / "lcapy" / "tests" / "test_kicad.sch"

if not test_file.exists():
    print(f"[FAILED] Test file not found: {test_file}")
    sys.exit(1)

try:
    converter = KiCADConverter(str(test_file))
    netlist, components = converter.convert()
    print("[OK] Conversion successful")
    print(f"     - Components: {len(components)}")
    print(f"     - Netlist size: {len(netlist)} bytes")
except Exception as e:
    print(f"[FAILED] {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: Display components
print("Test 3: Components Found")
print("-" * 70)
print(f"{'Ref':<10} {'Type':<6} {'Value':<12} {'Nodes':<20}")
print("-" * 70)
for comp in components:
    print(f"{comp['reference']:<10} {comp['type']:<6} {comp['value']:<12} {str(comp['nodes']):<20}")

print()

# Test 4: Display netlist
print("Test 4: Generated Netlist")
print("-" * 70)
print(netlist)
print("-" * 70)

print()

# Test 5: Save netlist
print("Test 5: Saving netlist...")
output_file = repo_root / "test_netlist.txt"
try:
    converter.save_netlist(str(output_file))
    size = output_file.stat().st_size
    print(f"[OK] Saved to: {output_file} ({size} bytes)")
except Exception as e:
    print(f"[FAILED] {e}")
    sys.exit(1)

print()
print("=" * 70)
print("SUCCESS! All tests passed!")
print("=" * 70)
print()
print("The converter is working correctly!")
print(f"Output file: {output_file}")
