"""Base data models for KiCAD parsers."""

from dataclasses import dataclass
from typing import List, Tuple, Optional


@dataclass
class Component:
    """Represents a component in the schematic."""
    name: str
    type: str
    value: str
    x: float
    y: float
    rotation: int = 0

    def __repr__(self):
        return f"Component({self.name}, {self.type}, {self.value}, pos=({self.x}, {self.y}), rot={self.rotation})"


@dataclass
class Wire:
    """Represents a wire segment."""
    x1: float
    y1: float
    x2: float
    y2: float

    def __repr__(self):
        return f"Wire(({self.x1}, {self.y1}) -> ({self.x2}, {self.y2}))"
