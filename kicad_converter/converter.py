"""KiCAD to Lcapy Schematic netlist converter.

Produces an Lcapy Schematic-format netlist with drawing hints
(right/up/down/left) so that Lcapy can draw the circuit natively
via circuitikz.  Falls back to explicit node positions (XX directive)
when the auto-placer cannot handle the topology (e.g. closed loops).
"""

from typing import List, Tuple, Dict, Any, Optional
from .parser import KiCADSchematic
from .netlist_extractor import NetlistExtractor


COMPONENT_TYPE_MAP = {
    'Device:R': 'R',
    'Device:R_US': 'R',
    'Device:R_Small': 'R',
    'Device:C': 'C',
    'Device:C_Small': 'C',
    'Device:L': 'L',
    'Device:L_Small': 'L',
    'Simulation_SPICE:VDC': 'V',
    'Simulation_SPICE:VAC': 'V',
    'Simulation_SPICE:IDC': 'I',
    'Simulation_SPICE:IAC': 'I',
}


class KiCADConverter:
    """Convert a KiCAD schematic to an Lcapy Schematic netlist."""

    def __init__(self, kicad_file: str):
        self.kicad_file = kicad_file
        self.schematic = KiCADSchematic(kicad_file)

    def convert(self) -> Tuple[str, List[Tuple[str, Dict[str, Any]]]]:
        """Run the full conversion pipeline.

        Returns (lcapy_netlist_string, components_list).
        """
        components = self._extract_components()
        extractor, pin_indices = self._build_connectivity(components)
        nets = extractor.get_nets()
        pin_node_names = self._assign_node_names(components, nets, pin_indices)
        netlist = self._generate_netlist(components, pin_node_names)
        comp_tuples = [
            (c['reference'], c) for c in components if c['type'] != 'GND'
        ]
        return netlist, comp_tuples

    # ------------------------------------------------------------------
    # 1. Component extraction
    # ------------------------------------------------------------------

    def _extract_components(self) -> List[Dict[str, Any]]:
        """Return component dicts with pin world-coordinates."""
        components = []
        for symbol in self.schematic.symbols:
            lib_id = symbol.get('lib_id', '')
            ref = symbol.get('reference', '')
            value = symbol.get('value', '')

            if not ref or not lib_id:
                continue

            comp_type = self._classify(lib_id, ref)
            if comp_type is None:
                continue

            pin_coords = self.schematic.get_pin_world_coords(symbol)

            components.append({
                'reference': ref,
                'type': comp_type,
                'value': value,
                'lib_id': lib_id,
                'pins': pin_coords,
                'at': symbol.get('at', (0, 0)),
                'rotation': symbol.get('rotation', 0),
            })
        return components

    @staticmethod
    def _classify(lib_id: str, ref: str) -> Optional[str]:
        if 'GND' in lib_id or (ref.startswith('#') and 'GND' in ref.upper()):
            return 'GND'
        if lib_id in COMPONENT_TYPE_MAP:
            return COMPONENT_TYPE_MAP[lib_id]
        if ref and not ref.startswith('#'):
            ch = ref[0].upper()
            if ch in 'RCLVI':
                return ch
        return None

    # ------------------------------------------------------------------
    # 2. Connectivity / net extraction
    # ------------------------------------------------------------------

    def _build_connectivity(
        self,
        components: List[Dict],
    ) -> Tuple[NetlistExtractor, Dict[Tuple[str, str], int]]:
        extractor = NetlistExtractor(tolerance=0.01)

        for wire in self.schematic.wires:
            extractor.add_wire_endpoints(wire)

        pin_indices: Dict[Tuple[str, str], int] = {}
        for comp in components:
            ref = comp['reference']
            for pin_num, (x, y) in comp['pins'].items():
                idx = extractor.add_pin(x, y)
                pin_indices[(ref, pin_num)] = idx

        return extractor, pin_indices

    # ------------------------------------------------------------------
    # 3. Node-name assignment (0 = ground, then 1, 2, …)
    # ------------------------------------------------------------------

    def _assign_node_names(
        self,
        components: List[Dict],
        nets: Dict[int, int],
        pin_indices: Dict[Tuple[str, str], int],
    ) -> Dict[str, Dict[str, str]]:
        net_to_name: Dict[int, str] = {}

        gnd_nets: set = set()
        for comp in components:
            if comp['type'] == 'GND':
                ref = comp['reference']
                for pin_num in comp['pins']:
                    idx = pin_indices.get((ref, pin_num))
                    if idx is not None:
                        gnd_nets.add(nets[idx])

        counter = 0
        for nid in gnd_nets:
            net_to_name[nid] = '0'
        counter = 1

        for idx in range(len(nets)):
            nid = nets[idx]
            if nid not in net_to_name:
                net_to_name[nid] = str(counter)
                counter += 1

        pin_node_names: Dict[str, Dict[str, str]] = {}
        for comp in components:
            ref = comp['reference']
            mapping: Dict[str, str] = {}
            for pin_num in comp['pins']:
                idx = pin_indices.get((ref, pin_num))
                if idx is not None:
                    mapping[pin_num] = net_to_name[nets[idx]]
            pin_node_names[ref] = mapping

        return pin_node_names

    # ------------------------------------------------------------------
    # 4. Direction hints
    # ------------------------------------------------------------------

    @staticmethod
    def _direction(p1: Tuple[float, float], p2: Tuple[float, float]) -> str:
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        if abs(dx) >= abs(dy):
            return 'right' if dx >= 0 else 'left'
        return 'down' if dy >= 0 else 'up'

    # ------------------------------------------------------------------
    # 5. Lcapy Schematic netlist generation
    # ------------------------------------------------------------------

    @staticmethod
    def _clean_value(comp: Dict) -> Optional[str]:
        value = comp.get('value', '')
        if not value:
            return None
        lib_id = comp.get('lib_id', '')
        lib_name = lib_id.split(':')[-1] if ':' in lib_id else lib_id
        if value == lib_name:
            return None
        if value.upper() in ('0', 'GND'):
            return None
        return value

    def _generate_netlist(
        self,
        components: List[Dict],
        pin_node_names: Dict[str, Dict[str, str]],
    ) -> str:
        lines: List[str] = []

        for comp in components:
            ref = comp['reference']
            ctype = comp['type']
            if ctype == 'GND':
                continue

            node_map = pin_node_names.get(ref, {})
            pin_numbers = sorted(comp['pins'].keys(), key=lambda p: (len(p), p))
            if len(pin_numbers) < 2:
                continue

            n1_pin, n2_pin = pin_numbers[0], pin_numbers[1]
            n1 = node_map.get(n1_pin, '?')
            n2 = node_map.get(n2_pin, '?')

            p1 = comp['pins'][n1_pin]
            p2 = comp['pins'][n2_pin]
            d = self._direction(p1, p2)

            value = self._clean_value(comp)
            if ctype in ('V', 'I'):
                lines.append(f'{ref} {n1} {n2}; {d}')
            elif value:
                lines.append(f'{ref} {n1} {n2} {value}; {d}')
            else:
                lines.append(f'{ref} {n1} {n2}; {d}')

        return '\n'.join(lines)

    def convert_with_positions(self) -> Tuple[str, List[Tuple[str, Dict[str, Any]]]]:
        """Like convert(), but prepends an XX directive with node positions
        derived from KiCAD coordinates.  Use this when the auto-placer
        fails on loop topologies."""
        components = self._extract_components()
        extractor, pin_indices = self._build_connectivity(components)
        nets = extractor.get_nets()
        pin_node_names = self._assign_node_names(components, nets, pin_indices)

        hint_netlist = self._generate_netlist(components, pin_node_names)
        xx_line = self._generate_xx_directive(components, pin_node_names, nets, pin_indices)
        netlist = xx_line + '\n' + hint_netlist if xx_line else hint_netlist

        comp_tuples = [
            (c['reference'], c) for c in components if c['type'] != 'GND'
        ]
        return netlist, comp_tuples

    def _generate_xx_directive(
        self,
        components: List[Dict],
        pin_node_names: Dict[str, Dict[str, str]],
        nets: Dict[int, int],
        pin_indices: Dict[Tuple[str, str], int],
    ) -> str:
        node_world: Dict[str, Tuple[float, float]] = {}

        for comp in components:
            ref = comp['reference']
            for pin_num in comp['pins']:
                idx = pin_indices.get((ref, pin_num))
                if idx is None:
                    continue
                net_id = nets[idx]
                node_name = pin_node_names.get(ref, {}).get(pin_num)
                if node_name is None:
                    continue
                if node_name not in node_world:
                    node_world[node_name] = comp['pins'][pin_num]

        if not node_world:
            return ''

        xs = [p[0] for p in node_world.values()]
        ys = [p[1] for p in node_world.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        span_x = max_x - min_x if max_x != min_x else 1
        span_y = max_y - min_y if max_y != min_y else 1

        parts = []
        for name, (x, y) in node_world.items():
            gx = (x - min_x) / span_x * 4.0
            gy = -(y - min_y) / span_y * 4.0
            parts.append(f'{name} @({gx:.2f},{gy:.2f})')

        return 'XX ; nodes={' + ', '.join(parts) + '}'

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------

    def save_netlist(self, filepath: str):
        netlist, _ = self.convert()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(netlist)

    def get_netlist(self) -> str:
        netlist, _ = self.convert()
        return netlist

    def get_components(self) -> List[Tuple[str, Dict[str, Any]]]:
        _, components = self.convert()
        return components
