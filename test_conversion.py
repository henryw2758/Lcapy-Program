#!/usr/bin/env python3
"""Quick test of KiCAD to Lcapy conversion."""

import sys
sys.path.insert(0, 'C:\\VT\\GitHub\\Lcapy-Program\\lcapy')

from lcapy.kicad.converter import KiCADConverter

# Test conversion
test_file = 'C:\\VT\\GitHub\\Lcapy-Program\\lcapy\\lcapy\\tests\\test_kicad.sch'

print("Loading KiCAD file...")
converter = KiCADConverter(test_file)

print("Converting to netlist...")
netlist, components = converter.convert()

print("\n" + "="*60)
print("EXTRACTED COMPONENTS:")
print("="*60)
for comp in components:
    print(f"  {comp['reference']:5} | Type: {comp['type']:3} | Value: {comp['value']:10} | Nodes: {comp['nodes']}")

print("\n" + "="*60)
print("GENERATED LCAPY NETLIST:")
print("="*60)
print(netlist)

print("\n" + "="*60)
print("Saving netlist to file...")
converter.save_netlist('C:\\VT\\GitHub\\Lcapy-Program\\test_output.txt')
print("Done!")
