#!/usr/bin/env python3
"""Direct test without needing full installation."""

import sys
from pathlib import Path

# Add paths
repo_root = Path(__file__).parent
lcapy_dir = repo_root / "lcapy"
sys.path.insert(0, str(lcapy_dir))

print("=" * 70)
print("KiCAD-to-Lcapy Converter - Direct Test")
print("=" * 70)
print()

# Test 1: Import converter
print("Test 1: Importing KiCAD converter module...")
try:
    from lcapy.kicad.converter import KiCADConverter
    print("✓ Successfully imported KiCADConverter")
except Exception as e:
    print(f"✗ Failed to import: {e}")
    sys.exit(1)

print()

# Test 2: Load test file
print("Test 2: Loading test KiCAD file...")
test_file = lcapy_dir / "lcapy" / "tests" / "test_kicad.sch"
print(f"   File: {test_file}")
print(f"   Exists: {test_file.exists()}")

if not test_file.exists():
    print(f"✗ Test file not found!")
    sys.exit(1)

try:
    converter = KiCADConverter(str(test_file))
    print(f"✓ Successfully loaded KiCAD file")
except Exception as e:
    print(f"✗ Failed to load: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 3: Convert to netlist
print("Test 3: Converting to netlist...")
try:
    netlist, components = converter.convert()
    print(f"✓ Conversion successful")
    print(f"  - Components found: {len(components)}")
    print(f"  - Netlist lines: {len(netlist.strip().split(chr(10)))}")
except Exception as e:
    print(f"✗ Conversion failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# Test 4: Show components
print("Test 4: Extracted Components")
print("-" * 70)
print(f"{'Reference':<10} {'Type':<6} {'Value':<12} {'Nodes':<15}")
print("-" * 70)
for comp in components:
    ref = comp['reference']
    ctype = comp['type']
    val = comp['value']
    nodes = str(comp['nodes'])
    print(f"{ref:<10} {ctype:<6} {val:<12} {nodes:<15}")

print()

# Test 5: Show netlist
print("Test 5: Generated Lcapy Netlist")
print("-" * 70)
print(netlist)
print("-" * 70)

print()

# Test 6: Save netlist
print("Test 6: Saving netlist to file...")
output_file = repo_root / "test_output_netlist.txt"
try:
    converter.save_netlist(str(output_file))
    file_size = output_file.stat().st_size
    print(f"✓ Netlist saved: {output_file}")
    print(f"  - File size: {file_size} bytes")
    
    # Read and display
    with open(output_file, 'r') as f:
        content = f.read()
    print(f"  - Content preview: {content[:50]}...")
except Exception as e:
    print(f"✗ Failed to save: {e}")
    sys.exit(1)

print()
print("=" * 70)
print("ALL TESTS PASSED! ✓✓✓")
print("=" * 70)
print()
print("Summary:")
print("  ✓ KiCAD parser working")
print("  ✓ File loading working")
print("  ✓ Conversion working")
print("  ✓ Netlist generation working")
print("  ✓ File saving working")
print()
print(f"Generated file: {output_file}")
print()
print("Next: Try the CLI with a full installation, or use this test script directly.")
