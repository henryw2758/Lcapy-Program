# KiCAD to Lcapy Converter

Convert KiCAD schematic files (.kicad_sch) to Lcapy circuit netlists.

## Installation

```bash
pip install -r requirements.txt
pip install -e lcapy
```

## Usage

```bash
python convert.py circuit.kicad_sch
```

**Options:**
- `-o, --output` - Output filename (default: `circuit_netlist.txt`)
- `-v, --verbose` - Show detailed output

**Example:**
```bash
python convert.py test.kicad_sch -o my_circuit.txt -v
```

## Output

Generates a netlist file compatible with Lcapy:

```
V1 n1 n2 dc 1
R1 n2 n3 1k
```

## Features

- Parses KiCAD 6+ S-expression format
- Extracts components and connections
- Generates valid Lcapy netlist
- Handles resistors, capacitors, inductors, voltage/current sources, and ground

## License

See LICENSE file.
