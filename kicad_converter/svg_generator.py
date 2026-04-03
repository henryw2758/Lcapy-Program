"""Draw circuits using Lcapy's built-in circuitikz renderer."""

import sys
from pathlib import Path


def _ensure_lcapy_on_path():
    repo_root = Path(__file__).resolve().parent.parent
    lcapy_dir = repo_root / 'lcapy'
    if lcapy_dir.exists() and str(lcapy_dir) not in sys.path:
        sys.path.insert(0, str(lcapy_dir))


def _load_schematic(netlist_string: str):
    _ensure_lcapy_on_path()
    from lcapy.schematic import Schematic

    sch = Schematic()
    for line in netlist_string.strip().splitlines():
        line = line.strip()
        if line:
            sch.add(line)
    return sch


def _compute_node_positions(kicad_file: str):
    from .converter import KiCADConverter

    conv = KiCADConverter(kicad_file)
    components = conv._extract_components()
    extractor, pin_indices = conv._build_connectivity(components)
    nets = extractor.get_nets()
    pin_node_names = conv._assign_node_names(components, nets, pin_indices)

    node_world = {}
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
        return {}

    xs = [p[0] for p in node_world.values()]
    ys = [p[1] for p in node_world.values()]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    span_x = max_x - min_x if max_x != min_x else 1
    span_y = max_y - min_y if max_y != min_y else 1

    from lcapy.schemmisc import Pos
    positions = {}
    for name, (x, y) in node_world.items():
        gx = (x - min_x) / span_x * 4.0
        gy = -(y - min_y) / span_y * 4.0
        positions[name] = Pos(gx, gy)
    return positions


def draw_with_lcapy(netlist_string: str, output_file: str, fmt: str = 'svg',
                    kicad_file: str = None, **kwargs):
    _ensure_lcapy_on_path()

    try:
        sch = _load_schematic(netlist_string)
        sch.draw(output_file, **kwargs)
        return
    except RuntimeError as exc:
        if 'loop' not in str(exc).lower():
            raise

    if kicad_file is None:
        raise

    positions = _compute_node_positions(kicad_file)
    if not positions:
        raise

    sch = _load_schematic(netlist_string)
    sch.node_positions = positions
    sch.draw(output_file, **kwargs)


class SVGCircuitGenerator:
    def __init__(self, filepath: str, netlist_string: str = None):
        self.filepath = filepath
        self.netlist_string = netlist_string

    def generate_svg(self, output_file: str):
        if self.netlist_string is None:
            from .converter import KiCADConverter
            conv = KiCADConverter(self.filepath)
            self.netlist_string, _ = conv.convert()
        draw_with_lcapy(self.netlist_string, output_file, fmt='svg',
                        kicad_file=self.filepath)


class PNGCircuitGenerator:
    def __init__(self, filepath: str, netlist_string: str = None):
        self.filepath = filepath
        self.netlist_string = netlist_string

    def generate_png(self, output_file: str):
        if self.netlist_string is None:
            from .converter import KiCADConverter
            conv = KiCADConverter(self.filepath)
            self.netlist_string, _ = conv.convert()
        draw_with_lcapy(self.netlist_string, output_file, fmt='png',
                        kicad_file=self.filepath)
