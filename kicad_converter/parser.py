"""KiCAD S-expression parser for .kicad_sch files.

Parses KiCAD 6+ S-expression format and extracts circuit information.
"""

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
        
        self._extract_data()

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
