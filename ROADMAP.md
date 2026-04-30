# KiCAD to Circuitikz - Development Roadmap

## Overview

This is a **mildly working prototype** for converting KiCAD schematics to Circuitikz LaTeX code and visual outputs.

**Current Status**: Phase 1-4 partially complete (basic functionality working, known limitations)

---

## Progress Tracking

### ✅ Phase 1: Core Parser (KiCAD v5)
**Status**: Complete

- [x] Implement `parser.py` for KiCAD v5 .sch files
- [x] Parse wire segments
- [x] Parse components (`$comp` to `$endcomp` blocks)
- [x] Extract component properties (label, value, position, rotation)
- [x] Extract component type (R, C, L, VDC, VSIN, IDC, ISIN, D, Q_NPN, etc.)
- [x] Handle power/ground symbols
- [x] Create data models (Component, Wire classes)
- [x] Add basic tests

**Output**: Parsed Python objects representing circuit topology

---

### ✅ Phase 2: KiCAD v6+ Support
**Status**: Complete

- [x] Implement `kicad_v6_parser.py` for .kicad_sch files (S-expression format)
- [x] Parse S-expression format
- [x] Handle new symbol library format
- [x] Extract same data as v5 parser
- [x] Auto-detect v5 vs v6 format
- [x] Add v6 sample file (test.kicad_sch)

**Output**: Unified parser that handles both v5 and v6 formats

---

### ⚠️ Phase 3: Component Mapping
**Status**: Partially Complete

- [x] Define KiCAD → Circuitikz type mappings (basic components)
- [x] Handle value parsing (numeric extraction)
- [x] Handle label extraction
- [x] Create position mapper with scaling
- [x] Create rotation mapper (basic 0°, 90°, 180°, 270°)
- [ ] **Needs improvement**: More accurate coordinate transformation
- [ ] **Needs improvement**: Better component sizing
- [ ] **Needs improvement**: Handle arbitrary rotation angles
- [ ] **Needs improvement**: Pin position calculation after rotation

**Known Issues**:
- Scale factor may not be optimal for all circuits
- Component sizes are approximate
- Complex rotations may not render correctly

---

### ⚠️ Phase 4: Circuitikz Export
**Status**: Partially Complete

- [x] Implement `exporter.py` for Circuitikz LaTeX code
- [x] Generate `\begin{circuitikz}` wrapper
- [x] Convert wires to `\draw` commands
- [x] Convert components using `to[TYPE]` syntax
- [x] Handle special components (ground) with `node[]`
- [x] Apply coordinate scaling and Y-axis flip
- [x] Wrap in complete LaTeX document
- [ ] **Needs improvement**: Better component positioning
- [ ] **Needs improvement**: Wire routing
- [ ] **Needs improvement**: Connection points accuracy

**Known Issues**:
- Component positions may not match KiCAD exactly
- Wires may not connect perfectly to components
- No automatic layout adjustment

---

### ✅ Phase 5: PDF/PNG/SVG Export
**Status**: Complete

- [x] Implement `pdf_exporter.py` using matplotlib
- [x] Draw components (R, C, L, V, ground, etc.)
- [x] Draw wires
- [x] Support PDF output (vector)
- [x] Support PNG output (300 DPI)
- [x] Support SVG output (vector)
- [x] No external tools required
- [ ] **Needs improvement**: Better visual quality
- [ ] **Needs improvement**: More accurate component symbols
- [ ] **Needs improvement**: Better wire routing

**Advantage**: No pdflatex or ImageMagick required!

---

### ⚠️ Phase 6: Netlist Export
**Status**: Partially Complete

- [x] Implement basic netlist exporter
- [x] List components with types and values
- [x] List wire segments with coordinates
- [x] Save as text file
- [ ] **Not implemented**: Actual node mapping
- [ ] **Not implemented**: Circuit topology analysis
- [ ] **Not implemented**: SPICE format output
- [ ] **Not implemented**: Connection verification

**Current Output**: Component and wire listing (not a true netlist)

**Planned**: Real netlist with node connectivity

---

### ⚠️ Phase 7: CLI and Usability
**Status**: Partially Complete

- [x] Implement `gui.py` with Tkinter
- [x] File browser for input selection
- [x] Output directory and name selection
- [x] Format selection checkboxes
- [x] Progress indication
- [x] Output preview area
- [x] Implement `test.py` CLI script
- [ ] **Needs improvement**: Better error messages
- [ ] **Needs improvement**: Batch processing
- [ ] **Needs improvement**: Command-line arguments
- [ ] **Needs improvement**: Configuration file support

---

## Future Phases (Not Started)

### Phase 8: Enhanced Component Support
- [ ] PNP, PMOS transistors
- [ ] Op-amps
- [ ] Transformers
- [ ] Switches (SPST, SPDT, etc.)
- [ ] Potentiometers
- [ ] Coupled inductors
- [ ] Custom symbols

### Phase 9: Advanced Features
- [ ] Multi-page schematic support
- [ ] Hierarchical sheet support
- [ ] Subcircuit (.subckt) extraction
- [ ] Component library management
- [ ] Custom component mapping configuration
- [ ] Template system for output

### Phase 10: Quality Improvements
- [ ] Accurate node mapping in netlist
- [ ] Automatic layout adjustment
- [ ] Wire routing optimization
- [ ] Better error handling and validation
- [ ] Unit tests
- [ ] Performance optimization

---

## Known Limitations (Current Prototype)

1. **Positioning**: Component positions are approximate
2. **Netlist**: No actual circuit connectivity analysis
3. **Complex circuits**: Multi-page/hierarchical schematics not supported
4. **Component coverage**: Basic components only
5. **Rotation**: Limited rotation support
6. **Error handling**: Minimal validation
7. **Documentation**: Incomplete

---

## Component Coverage

### ✅ Fully Supported
- Resistors (R, R_US)
- Capacitors (C)
- Inductors (L)
- Voltage sources (VDC, VSIN)
- Current sources (IDC, ISIN)
- Diodes (D, D_ZENER, D_SCHOTTKY)
- LEDs (LED)
- Ground symbols

### ⚠️ Partially Supported
- Transistors (NPN, NMOS) - basic parsing, limited rendering

### ❌ Not Supported
- PNP, PMOS transistors
- Op-amps
- Transformers
- Switches
- Potentiometers
- Custom symbols

---

## Next Steps (Priority Order)

1. **Fix positioning** - Improve coordinate scaling and component placement
2. **Better netlist** - Implement actual node mapping
3. **More components** - Add missing component types
4. **Error handling** - Better validation and error messages
5. **Documentation** - Add examples and usage guide
6. **Testing** - Add unit tests

---

## Contributing

This is early-stage software. If you want to contribute:

1. Pick a task from the "Needs improvement" sections above
2. Check the relevant module (parser, exporter, etc.)
3. Write tests for your changes
4. Update this ROADMAP.md with your progress
5. Submit a pull request

---

## Reference Implementation

- Original reference: [uwezi/circuitikz_import](https://github.com/uwezi/circuitikz_import)
- KiCAD v5 .sch format documentation
- KiCAD v6+ .kicad_sch format (S-expression)
- Circuitikz documentation: [CTAN circuitikz](https://ctan.org/pkg/circuitikz)
