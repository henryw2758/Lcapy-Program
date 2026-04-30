"""Netlist to Text - Convert circuit netlists to descriptive text.

This package converts SPICE-like netlists (from Lcapy or other sources)
into human-readable descriptions for accessibility purposes.
"""

__version__ = "0.1.0"
__author__ = "Ported from NetlistToText by johnjhealy"

from .element import Element
from .circuit import Circuit

__all__ = ["Element", "Circuit"]
