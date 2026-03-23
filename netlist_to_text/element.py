"""Element class representing a circuit component."""

from .utils import spell_out_multiplier


class Element:
    """Represents a circuit element with its properties and connection info."""

    def __init__(
        self,
        name,
        first_node,
        second_node,
        value=None,
        third_node=None,
        para1=None,
        para2=None
    ):
        self.name = name
        self.first_node = self.convert_node_text(first_node)
        self.second_node = self.convert_node_text(second_node)
        self.third_node = self.convert_node_text(third_node) if third_node else None
        self.value = value
        self.para1 = para1
        self.para2 = para2
        self.parallel_connection_present = False
        self.parallel_connection_text = ""
        self.series_connection_present = False
        self.series_connection_text = ""

    def convert_node_text(self, node):
        """Convert SPICE node notation to readable text.
        
        Examples:
            '0' -> 'ground'
            'N001' -> 'node 1'
            '1' -> 'node 1'
            '0_1' -> 'ground' (Lcapy: underscore suffix is same node)
            '1_1' -> 'node 1' (Lcapy: underscore suffix is same node)
            'N001_1' -> 'node 1' (Lcapy: underscore suffix is same node)
        """
        if node is None:
            return None
        
        # Handle Lcapy's underscore notation for wire routing
        # e.g., "0_1" is the same as "0" (ground)
        # e.g., "1_1" is the same as "1" (node 1)
        if "_" in node:
            # Strip off the underscore and any suffix after it
            parts = node.split("_")
            # Use the first part (the actual node number)
            node = parts[0]
        
        if node == "0":
            return "ground"
        if node.startswith("N0"):
            try:
                return f"node {int(node[2:])}"
            except (ValueError, IndexError):
                pass
        if node.isdigit():
            return f"node {node}"
        return node

    def get_element_type(self, element_name=None):
        """Return element type string based on name prefix.
        
        Args:
            element_name: If provided, get type for this name instead of self.name
        """
        name = element_name if element_name else self.name
        if not name:
            return "element"
        prefix = name[0].upper()
        type_map = {
            "R": "resistor",
            "L": "inductor",
            "C": "capacitor",
            "V": "voltage source",
            "I": "current source",
            "G": "conductance",
        }
        return type_map.get(prefix, "element")

    def get_element_unit(self, element_name=None):
        """Return unit string based on element type.
        
        Args:
            element_name: If provided, get unit for this name instead of self.name
        """
        name = element_name if element_name else self.name
        if not name:
            return ""
        prefix = name[0].upper()
        unit_map = {
            "V": "Volt",
            "R": "Ohm",
            "C": "Farad",
            "I": "Amp",
            "L": "Henry",
            "G": "Siemen",
        }
        return unit_map.get(prefix, "")

    def get_direction_text(self):
        """Return text describing current/voltage direction."""
        if not self.name:
            return ""
        if self.name.startswith("V"):
            return (
                f"The positive terminal of the voltage source is connected to {self.first_node} "
                f"and negative terminal is connected to {self.second_node}.\n"
            )
        elif self.name.startswith("I"):
            return (
                f"The current from the current source is flowing from {self.first_node} "
                f"to {self.second_node}.\n"
            )
        return ""

    def get_value_text(self):
        """Return formatted value text with unit."""
        if not self.value:
            return ""
        
        # Handle waveform specifications
        waveform_keywords = ["PULSE", "EXP", "SINE", "SFFM"]
        for keyword in waveform_keywords:
            if keyword in str(self.value).upper():
                waveform_map = {
                    "PULSE": "with a waveform described by a pulse waveform",
                    "EXP": "with a waveform described by an exponential waveform",
                    "SINE": "with a waveform described by a sine waveform",
                }
                return waveform_map.get(keyword, "") + ","
        
        # Spell out multipliers for accessibility (e.g., '1e-3' -> '1 milli')
        spelled_value = spell_out_multiplier(self.value)
        
        # Regular value with unit
        unit = self.get_element_unit()
        if unit:
            return f"{spelled_value} {unit}"
        return ""

    def set_parallel_connection(self, elem2_name, elem2_value):
        """Set parallel connection information."""
        self.parallel_connection_present = True
        self.parallel_connection_text = (
            f"Between {self.first_node} and {self.second_node}, "
            f"a {self.get_value_text()} {self.get_element_type()} labelled {self.name} "
            f"is connected in parallel with a {elem2_value} {self.get_element_type(elem2_name)} "
            f"labelled {elem2_name}.\n"
        )
        self.parallel_connection_text += self.get_direction_text()

    def set_series_connection(self, elem2_name, shared_node, elem2_value):
        """Set series connection information."""
        self.series_connection_present = True
        
        # Determine node1, node2, node3 based on which node is shared
        nodes = [self.first_node, self.second_node]
        if shared_node == self.first_node:
            node1 = self.second_node
            node3 = self.first_node
        else:
            node1 = self.first_node
            node3 = self.second_node
        
        self.series_connection_text = (
            f"Between {node1} and {node3}, "
            f"a {self.get_value_text()} {self.get_element_type()} labelled {self.name} "
            f"is connected in series with a {elem2_value} {self.get_element_type(elem2_name)} "
            f"labelled {elem2_name}, these elements are connected at {node3}.\n"
        )
        self.series_connection_text += self.get_direction_text()

    def to_description(self):
        """Generate full description string for this element."""
        desc = ""
        
        if self.parallel_connection_present:
            desc += self.parallel_connection_text
        elif self.series_connection_present:
            desc += self.series_connection_text
        else:
            value_text = self.get_value_text()
            if value_text:
                desc += (
                    f"Between {self.first_node} and {self.second_node}, "
                    f"a {value_text} {self.get_element_type()} labelled {self.name} is connected.\n"
                )
            else:
                desc += (
                    f"Between {self.first_node} and {self.second_node}, "
                    f"a {self.get_element_type()} labelled {self.name} is connected.\n"
                )
            desc += self.get_direction_text()
        
        return desc

    def __repr__(self):
        return f"Element(name={self.name}, nodes=({self.first_node}, {self.second_node}), value={self.value})"
