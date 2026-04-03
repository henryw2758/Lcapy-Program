"""KiCAD to Lcapy netlist converter."""

from typing import List, Tuple, Dict, Any, Optional
from .parser import KiCADSchematic


class KiCADConverter:
    """Converter from KiCAD schematic to Lcapy netlist."""

    def __init__(self, kicad_file: str):
        self.kicad_file = kicad_file
        self.schematic = KiCADSchematic(kicad_file)
        self.circuit_data = self.schematic.get_circuit_data()
        
        self.components: List[Tuple[str, Dict[str, Any]]] = []
        self.wires: List[Dict[str, Any]] = []
        self.junctions: List[Tuple[float, float]] = []
        self.netlist = ""
        self.node_counter = 1

    def convert(self):
        self._extract_wires()
        self._extract_junctions()
        self._extract_components()
        self._generate_netlist()
        return self.netlist, self.components

    def _extract_wires(self):
        for wire in self.circuit_data.get('wires', []):
            pts = wire.get('pts', [])
            if len(pts) >= 2:
                self.wires.append({'start': pts[0], 'end': pts[-1]})

    def _extract_junctions(self):
        for junction in self.circuit_data.get('junctions', []):
            at = junction.get('at')
            if at:
                self.junctions.append(at)

    def _extract_components(self):
        for symbol in self.circuit_data.get('symbols', []):
            lib_id = symbol.get('lib_id', '')
            ref = symbol.get('reference', '')
            value = symbol.get('value', '')
            at = symbol.get('at', (0, 0))
            rotation = symbol.get('rotation', 0)
            
            if not ref or not lib_id:
                continue
            
            comp_type = self._get_component_type(lib_id, ref)
            if not comp_type:
                continue
            
            self.components.append((ref, {
                'reference': ref,
                'type': comp_type,
                'value': value,
                'at': at,
                'rotation': rotation,
                'lib_id': lib_id,
                'pins': symbol.get('pins', [])
            }))

    def _get_component_type(self, lib_id: str, ref: str) -> Optional[str]:
        if lib_id == 'Simulation_SPICE:0' or 'GND' in ref.upper():
            return 'GND'
        
        mapping = {
            'Device:R': 'R',
            'Device:R_US': 'R',
            'Device:C': 'C',
            'Device:L': 'L',
            'Simulation_SPICE:VDC': 'V',
            'Simulation_SPICE:VAC': 'V',
            'Simulation_SPICE:IDC': 'I',
            'Simulation_SPICE:IAC': 'I',
        }
        
        if lib_id in mapping:
            return mapping[lib_id]
        
        if ref and not ref.startswith('#'):
            first_char = ref[0].upper()
            if first_char in 'RCLVI':
                return first_char
        
        return None

    def _generate_netlist(self):
        lines = []
        
        for ref, comp in self.components:
            comp_type = comp['type']
            value = comp['value'] or '1'
            
            if comp_type == 'GND':
                continue
            
            node1 = self.node_counter
            node2 = self.node_counter + 1
            self.node_counter += 2
            
            if comp_type == 'V':
                line = f'{ref} {node1} {node2} dc {value}'
            elif comp_type == 'I':
                line = f'{ref} {node1} {node2} dc {value}'
            else:
                line = f'{ref} {node1} {node2} {value}'
            
            lines.append(line)
        
        self.netlist = '\n'.join(lines)

    def save_netlist(self, filepath: str):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(self.netlist)

    def get_netlist(self) -> str:
        return self.netlist

    def get_components(self):
        return self.components
