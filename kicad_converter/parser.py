"""KiCAD S-expression parser for .kicad_sch files.

Parses KiCAD 6+ S-expression format and extracts circuit information
including pin world-coordinates from library symbol definitions.
"""

import math
from typing import List, Dict, Tuple, Any, Optional


class SExprParser:
    """Parse S-expression format used by KiCAD."""

    def __init__(self, content: str):
        self.content = content
        self.pos = 0
        self.length = len(content)

    def _skip_whitespace(self):
        while self.pos < self.length:
            if self.content[self.pos].isspace():
                self.pos += 1
            else:
                break

    def _read_string(self) -> str:
        if self.content[self.pos] != '"':
            raise ValueError(f"Expected quote at position {self.pos}")

        self.pos += 1
        start = self.pos

        while self.pos < self.length and self.content[self.pos] != '"':
            if self.content[self.pos] == '\\':
                self.pos += 2
            else:
                self.pos += 1

        result = self.content[start:self.pos]
        self.pos += 1
        return result

    def _read_atom(self) -> str:
        start = self.pos

        while self.pos < self.length:
            ch = self.content[self.pos]
            if ch.isspace() or ch in '()':
                break
            self.pos += 1

        return self.content[start:self.pos]

    def parse(self) -> Any:
        self._skip_whitespace()

        if self.pos >= self.length:
            return None

        ch = self.content[self.pos]

        if ch == '(':
            self.pos += 1
            elements = []

            while True:
                self._skip_whitespace()
                if self.pos >= self.length:
                    raise ValueError("Unexpected end of input")

                if self.content[self.pos] == ')':
                    self.pos += 1
                    break

                elements.append(self.parse())

            return elements

        elif ch == '"':
            return self._read_string()

        else:
            return self._read_atom()


class KiCADSchematic:
    """Parse and extract circuit information from KiCAD schematic."""

    def __init__(self, filename: str):
        self.filename = filename
        with open(filename, 'r', encoding='utf-8') as f:
            self.content = f.read()

        parser = SExprParser(self.content)
        self.root = parser.parse()

        self.symbols = []
        self.wires = []
        self.junctions = []
        self.lib_symbols = {}
        self.lib_pin_defs = {}

        self._extract_data()
        self._extract_lib_pin_defs()

    def _extract_data(self):
        if not isinstance(self.root, list):
            return

        for item in self.root:
            if not isinstance(item, list) or len(item) == 0:
                continue

            key = item[0]

            if key == 'symbol':
                self._parse_symbol(item)
            elif key == 'wire':
                self._parse_wire(item)
            elif key == 'junction':
                self._parse_junction(item)
            elif key == 'lib_symbols':
                self._parse_lib_symbols(item)

    def _parse_lib_symbols(self, item: list):
        for lib_symbol in item[1:]:
            if isinstance(lib_symbol, list) and len(lib_symbol) > 0:
                if lib_symbol[0] == 'symbol':
                    symbol_id = lib_symbol[1] if len(lib_symbol) > 1 else None
                    self.lib_symbols[symbol_id] = lib_symbol

    def _extract_lib_pin_defs(self):
        """Extract pin connection points from lib_symbols.

        Each pin's (at x y) gives its connection point in local symbol
        coordinates.  These are stored for later transformation to
        world coordinates by get_pin_world_coords().
        """
        for lib_id, lib_data in self.lib_symbols.items():
            pins = {}
            for item in lib_data[1:]:
                if isinstance(item, list) and len(item) > 0 and item[0] == 'symbol':
                    pins.update(self._find_pins_in_element(item))
            self.lib_pin_defs[lib_id] = pins

    def _find_pins_in_element(self, element) -> Dict[str, Tuple[float, float]]:
        """Recursively find pin (number, connection-point) pairs."""
        pins = {}
        if not isinstance(element, list) or len(element) < 2:
            return pins
        if element[0] == 'pin':
            pin_number = None
            pin_at = None
            for sub in element[1:]:
                if isinstance(sub, list) and len(sub) > 0:
                    if sub[0] == 'number' and len(sub) >= 2:
                        pin_number = str(sub[1])
                    elif sub[0] == 'at' and len(sub) >= 3:
                        try:
                            pin_at = (float(sub[1]), float(sub[2]))
                        except (ValueError, TypeError):
                            pass
            if pin_number is not None and pin_at is not None:
                pins[pin_number] = pin_at
        for sub in element[1:]:
            if isinstance(sub, list):
                pins.update(self._find_pins_in_element(sub))
        return pins

    def get_pin_world_coords(self, symbol: dict) -> Dict[str, Tuple[float, float]]:
        """Compute world coordinates for a placed symbol's pins.

        Transforms the local pin connection points from the library
        definition by the symbol's placement (at) position and rotation.
        """
        lib_id = symbol.get('lib_id')
        if not lib_id:
            return {}

        lib_pins = self.lib_pin_defs.get(lib_id, {})
        if not lib_pins:
            return {}

        at = symbol.get('at')
        if not at:
            return {}

        sx, sy = at
        rotation = symbol.get('rotation', 0)
        theta = math.radians(rotation)
        cos_t = math.cos(theta)
        sin_t = math.sin(theta)

        world_pins = {}
        for pin_number, (lx, ly) in lib_pins.items():
            wx = sx + lx * cos_t - ly * sin_t
            wy = sy + lx * sin_t + ly * cos_t
            world_pins[pin_number] = (wx, wy)

        return world_pins

    def _parse_symbol(self, item: list):
        symbol = {
            'lib_id': None,
            'at': None,
            'rotation': 0,
            'unit': None,
            'reference': None,
            'value': None,
            'properties': {},
            'pins': [],
            'uuid': None
        }

        i = 1
        while i < len(item):
            element = item[i]

            if isinstance(element, list):
                cmd = element[0] if element else None

                if cmd == 'lib_id':
                    symbol['lib_id'] = element[1] if len(element) > 1 else None

                elif cmd == 'at':
                    if len(element) >= 3:
                        try:
                            symbol['at'] = (float(element[1]), float(element[2]))
                            if len(element) >= 4:
                                symbol['rotation'] = float(element[3])
                        except (ValueError, TypeError):
                            pass

                elif cmd == 'unit':
                    symbol['unit'] = element[1] if len(element) > 1 else None

                elif cmd == 'property':
                    if len(element) >= 3:
                        prop_name = element[1]
                        prop_value = element[2]
                        symbol['properties'][prop_name] = prop_value

                        if prop_name == 'Reference':
                            symbol['reference'] = prop_value
                        elif prop_name == 'Value':
                            symbol['value'] = prop_value

                elif cmd == 'pin':
                    pin_info = self._parse_pin(element)
                    if pin_info:
                        symbol['pins'].append(pin_info)

                elif cmd == 'uuid':
                    symbol['uuid'] = element[1] if len(element) > 1 else None

            i += 1

        if symbol['lib_id'] or symbol['reference']:
            self.symbols.append(symbol)

    def _parse_pin(self, element: list) -> Optional[Dict]:
        if len(element) < 3:
            return None

        pin = {
            'type': element[1],
            'number': element[2],
            'at': None,
            'length': None,
            'name': None
        }

        for i in range(3, len(element)):
            sub = element[i]
            if isinstance(sub, list) and len(sub) > 0:
                cmd = sub[0]

                if cmd == 'at' and len(sub) >= 3:
                    try:
                        pin['at'] = (float(sub[1]), float(sub[2]))
                    except (ValueError, TypeError):
                        pass

                elif cmd == 'length' and len(sub) >= 2:
                    try:
                        pin['length'] = float(sub[1])
                    except (ValueError, TypeError):
                        pass

                elif cmd == 'name' and len(sub) >= 2:
                    pin['name'] = sub[1]

        return pin

    def _parse_wire(self, item: list):
        wire = {
            'pts': [],
            'stroke': None,
            'uuid': None
        }

        for element in item[1:]:
            if isinstance(element, list):
                cmd = element[0] if element else None

                if cmd == 'pts':
                    for pt in element[1:]:
                        if isinstance(pt, list) and pt[0] == 'xy' and len(pt) >= 3:
                            try:
                                wire['pts'].append((float(pt[1]), float(pt[2])))
                            except (ValueError, TypeError):
                                pass

                elif cmd == 'uuid':
                    wire['uuid'] = element[1] if len(element) > 1 else None

        if wire['pts']:
            self.wires.append(wire)

    def _parse_junction(self, item: list):
        junction = {
            'at': None,
            'uuid': None
        }

        for element in item[1:]:
            if isinstance(element, list):
                cmd = element[0] if element else None

                if cmd == 'at' and len(element) >= 3:
                    try:
                        junction['at'] = (float(element[1]), float(element[2]))
                    except (ValueError, TypeError):
                        pass

                elif cmd == 'uuid':
                    junction['uuid'] = element[1] if len(element) > 1 else None

        if junction['at']:
            self.junctions.append(junction)

    def get_circuit_data(self) -> Dict[str, Any]:
        return {
            'symbols': self.symbols,
            'wires': self.wires,
            'junctions': self.junctions,
            'lib_symbols': self.lib_symbols
        }
