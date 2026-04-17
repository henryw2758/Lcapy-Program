# KiCAD to Circuitikz - Branch Roadmap

## Overview

This branch implements a tool to convert KiCAD Eeschema schematic files (`.sch`) into:
1. **Circuitikz LaTeX code** - For high-quality schematic drawings in LaTeX/Manim
2. **Netlist output** - Component-to-node mapping (no analysis, just structure)

**Reference**: Based on [uwezi/circuitikz_import](https://github.com/uwezi/circuitikz_import) for KiCAD v5.1.5, but modernized and extended.

---

## Project Structure

```
kicad2circuitikz/
├── src/kicad2circuitikz/
│   ├── __init__.py
│   ├── cli.py                 # Command-line interface
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── base_parser.py     # Abstract parser interface
│   │   ├── kicad_v5.py        # KiCAD 5.x .sch parser
│   │   └── kicad_v6.py        # KiCAD 6+ .kicad_sch parser (future)
│   ├── mappers/
│   │   ├── __init__.py
│   │   ├── component_map.py   # KiCAD → Circuitikz component mapping
│   │   ├── position_map.py    # Coordinate transformation
│   │   └── rotation_map.py    # Direction/angle handling
│   └── exporters/
│       ├── __init__.py
│       ├── circuitikz.py      # LaTeX/Circuitikz output
│       └── netlist.py         # Netlist output (component-node mapping)
├── tests/
│   ├── samples/
│   │   ├── kicad_v5/          # Sample KiCAD 5 .sch files
│   │   └── kicad_v6/          # Sample KiCAD 6+ .kicad_sch files
│   ├── test_parser.py
│   ├── test_mapper.py
│   └── test_exporter.py
├── examples/                  # Example outputs
├── ROADMAP.md                 # This file
└── README.md
```

---

## Phase 1: Core Parser (KiCAD v5)

**Goal**: Parse KiCAD 5.x `.sch` files into a structured representation

### Tasks
- [ ] Implement `kicad_v5.py` parser
  - [ ] Parse wire segments
  - [ ] Parse components (`$comp` to `$endcomp` blocks)
  - [ ] Extract component properties (label, value, position, rotation)
  - [ ] Extract component type (R, C, L, VDC, VSIN, IDC, ISIN, D, Q_NPN, etc.)
  - [ ] Handle power/ground symbols
  - [ ] Parse connection nodes
- [ ] Create data models
  - [ ] `Component` class - stores component data
  - [ ] `Wire` class - stores wire connections
  - [ ] `Node` class - tracks net connections
- [ ] Add basic tests with sample KiCAD v5 files

**Output**: Parsed Python objects representing circuit topology

---

## Phase 2: Component Mapping

**Goal**: Map KiCAD components to Circuitikz equivalents

### Tasks
- [ ] Create `component_map.py`
  - [ ] Define KiCAD → Circuitikz type mappings
    - `Device:R` → `R` (resistor)
    - `Device:C` → `C` (capacitor)
    - `Device:L` → `american inductor` (inductor)
    - `Device:D` → `Do` (diode)
    - `Device:D_ZENER` → `zDo` (zener diode)
    - `Device:D_SCHOTTKY` → `sDo` (schottky diode)
    - `Device:LED` → `leDo` (LED)
    - `Device:VDC` → `V` (DC voltage source)
    - `Device:VSIN` → `sV` (AC voltage source)
    - `Device:IDC` → `I` (DC current source)
    - `Device:ISIN` → `sI` (AC current source)
    - `Device:Q_NPN_*` → `npn` (NPN transistor)
    - `Device:Q_NMOS_DSG` → `nigfete` (NMOS transistor)
    - `Device:Earth` → `ground` (ground symbol)
  - [ ] Handle value parsing (e.g., "1k" → "1k", "10V" → "10V")
  - [ ] Handle label extraction (F1 field)
- [ ] Create `position_map.py`
  - [ ] Convert KiCAD coordinates (mils) to cm/cm
  - [ ] Handle scale factor (default: 200 KiCAD units = 1 cm)
- [ ] Create `rotation_map.py`
  - [ ] Parse KiCAD rotation matrix `[a b c d]`
  - [ ] Convert to Circuitikz `rotate={angle}` parameter
  - [ ] Determine pin positions after rotation

**Output**: Mapped component data ready for Circuitikz generation

---

## Phase 3: Circuitikz Export

**Goal**: Generate Circuitikz LaTeX code

### Tasks
- [ ] Implement `circuitikz.py` exporter
  - [ ] Generate `\begin{circuitikz}` ... `\end{circuitikz}` wrapper
  - [ ] Convert wires to `\draw (x1,y1) -- (x2,y2);`
  - [ ] Convert components using `to[TYPE, l=LABEL, a=VALUE]` syntax
  - [ ] Handle special components (transistors, ground) with `node[TYPE, rotate={}]`
  - [ ] Apply coordinate scaling (KiCAD units → cm)
  - [ ] Flip Y-axis (KiCAD Y increases downward, Circuitikz Y increases upward)
- [ ] Add output modes
  - [ ] Raw LaTeX output (complete `.tex` file)
  - [ ] Manim format (MathTex with circuitikz environment)
  - [ ] Circuitikz-only code snippet
- [ ] Add tests comparing generated output to expected Circuitikz

**Output**: Valid Circuitikz LaTeX code

---

## Phase 4: Netlist Export

**Goal**: Generate netlist (component-node mapping only, no analysis)

### Tasks
- [ ] Implement `netlist.py` exporter
  - [ ] Extract component names, types, and connected nodes
  - [ ] Build node-to-component mapping
  - [ ] Generate simple netlist format:
    ```
    R1 1 2 1k
    C1 2 3 1uF
    V1 0 1 10V
    ```
  - [ ] Optional: SPICE format output
- [ ] Add tests verifying netlist correctness

**Output**: Component-node netlist (text/SPICE format)

---

## Phase 5: KiCAD v6+ Support (Future)

**Goal**: Support KiCAD 6+ `.kicad_sch` format (S-expression based)

### Tasks
- [ ] Implement `kicad_v6.py` parser
  - [ ] Parse S-expression format
  - [ ] Handle new symbol library format
  - [ ] Extract same data as v5 parser
- [ ] Reuse existing mapper and exporter modules
- [ ] Add v6 sample files and tests

---

## Phase 6: CLI and Usability

**Goal**: Easy-to-use command-line interface

### Tasks
- [ ] Implement `cli.py`
  - [ ] Argument parsing (input file, output format, output file)
  - [ ] Input file detection (v5 vs v6)
  - [ ] Error handling and validation
- [ ] Create installation script (`setup.py` or `pyproject.toml`)
  - [ ] Package as `kicad2circuitikz`
  - [ ] Console script entry point
- [ ] Add example usage in README

---

## Phase 7: Additional Features (Optional)

- [ ] Component library extension (add more component types)
- [ ] Custom component mapping configuration
- [ ] Multi-page schematic support
- [ ] Hierarchical sheet support
- [ ] Subcircuit (.subckt) extraction
- [ ] GUI for preview/editing before export

---

## Component Coverage Goals

### Phase 1-3 (Initial)
- [x] Resistors (R)
- [x] Capacitors (C)
- [x] Inductors (L)
- [x] Voltage sources (DC, AC/SIN)
- [x] Current sources (DC, AC/SIN)
- [x] Diodes (standard, zener, schottky, LED)
- [x] Transistors (NPN, NMOS)
- [x] Ground/Power symbols
- [x] Wires and connections

### Future Extensions
- [ ] PNP, PMOS transistors
- [ ] Op-amps
- [ ] Transformers
- [ ] Switches (SPST, SPDT, etc.)
- [ ] Potentiometers
- [ ] Coupled inductors
- [ ] Custom symbols

---

## Testing Strategy

1. **Unit tests** - Test each parser/mapper/exporter independently
2. **Integration tests** - Test full pipeline: KiCAD file → Circuitikz/Netlist
3. **Sample files** - Include example KiCAD schematics for:
   - Simple voltage divider
   - RC circuit
   - RLC circuit
   - Transistor amplifier
   - Multi-component circuits
4. **Output validation** - Verify generated LaTeX compiles and produces correct drawings

---

## Dependencies

```
- Python 3.8+
- re (standard library)
- numpy (for matrix transformations in rotation handling)
- pytest (for testing)
```

---

## Notes

- No Lcapy circuit analysis - this is purely structural conversion
- Coordinate system: KiCAD uses mils (1 mil = 0.001 inch), Circuitikz uses cm
- Scale factor: 200 KiCAD units = 1 cm (adjustable)
- Y-axis flip required: KiCAD (0,0) is top-left, Circuitikz (0,0) is bottom-left

---

## Progress

- [x] Project structure created
- [x] ROADMAP documented
- [ ] Phase 1: Core Parser (KiCAD v5)
- [ ] Phase 2: Component Mapping
- [ ] Phase 3: Circuitikz Export
- [ ] Phase 4: Netlist Export
- [ ] Phase 5: KiCAD v6+ Support
- [ ] Phase 6: CLI and Usability
- [ ] Phase 7: Additional Features
