"""Base data models for KiCAD parsers."""

from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class Component:
    """Represents a component in the schematic."""
    name: str
    type: str
    value: str
    x: int
    y: int
    rotation: int = 0

    def __repr__(self):
        return f"Component({self.name}, {self.type}, {self.value}, pos=({self.x}, {self.y}), rot={self.rotation})"


@dataclass
class Wire:
    """Represents a wire segment."""
    x1: int
    y1: int
    x2: int
    y2: int

    def __repr__(self):
        return f"Wire(({self.x1}, {self.y1}) -> ({self.x2}, {self.y2}))"
