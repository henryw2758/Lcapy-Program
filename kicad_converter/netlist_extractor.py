"""Extract electrical nets from KiCAD schematic connectivity.

Uses Union-Find with spatial proximity to merge wire endpoints and
pin endpoints into electrical nodes.
"""

from typing import Dict, List, Tuple, Optional


class NetlistExtractor:
    """Build a connectivity graph and assign electrical net IDs."""

    def __init__(self, tolerance: float = 0.01):
        self.tolerance = tolerance
        self._points: List[Tuple[float, float]] = []
        self._parent: List[int] = []
        self._bucket: Dict[Tuple[int, int], List[int]] = {}

    def _find(self, i: int) -> int:
        while self._parent[i] != i:
            self._parent[i] = self._parent[self._parent[i]]
            i = self._parent[i]
        return i

    def _union(self, i: int, j: int):
        ri, rj = self._find(i), self._find(j)
        if ri != rj:
            self._parent[ri] = rj

    def _bucket_key(self, x: float, y: float) -> Tuple[int, int]:
        r = self.tolerance
        return (int(x / r), int(y / r))

    def _get_or_add(self, x: float, y: float) -> int:
        bk = self._bucket_key(x, y)
        for idx in self._bucket.get(bk, []):
            ex, ey = self._points[idx]
            if abs(x - ex) <= self.tolerance and abs(y - ey) <= self.tolerance:
                return idx
        new_idx = len(self._points)
        self._points.append((x, y))
        self._parent.append(new_idx)
        self._bucket.setdefault(bk, []).append(new_idx)
        return new_idx

    def add_wire_endpoints(self, wire: dict):
        pts = wire.get('pts', [])
        if len(pts) >= 2:
            i1 = self._get_or_add(*pts[0])
            i2 = self._get_or_add(*pts[-1])
            self._union(i1, i2)

    def add_pin(self, x: float, y: float) -> int:
        return self._get_or_add(x, y)

    def get_nets(self) -> Dict[int, int]:
        root_to_net: Dict[int, int] = {}
        net_id = 0
        nets: Dict[int, int] = {}
        for i in range(len(self._points)):
            root = self._find(i)
            if root not in root_to_net:
                root_to_net[root] = net_id
                net_id += 1
            nets[i] = root_to_net[root]
        return nets
