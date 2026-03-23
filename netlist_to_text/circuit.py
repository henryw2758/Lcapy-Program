"""Circuit class for analyzing and describing circuits."""


from typing import List, Set, Dict
from .element import Element
from .parser import parse_netlist_file, parse_lcapy_netlist


class Circuit:
    """Represents a circuit with elements and analysis capabilities."""

    def __init__(self):
        self.elements: List[Element] = []
        self.nodes: Set[str] = set()

    def add_element(self, element: Element):
        """Add an element to the circuit.
        
        Args:
            element: Element object to add
        """
        self.elements.append(element)
        self.nodes.add(element.first_node)
        self.nodes.add(element.second_node)

    def get_unique_nodes(self) -> Set[str]:
        """Get set of unique nodes in the circuit."""
        return self.nodes

    def count_elements_by_type(self) -> Dict[str, int]:
        """Count elements by their type.
        
        Returns:
            Dictionary mapping element type to count
        """
        counts = {}
        for elem in self.elements:
            elem_type = elem.get_element_type()
            counts[elem_type] = counts.get(elem_type, 0) + 1
        return counts

    def is_rotatable(self, element: Element) -> bool:
        """Check if element can be rotated (node order doesn't matter).
        
        Rotatable elements: R, L, C
        
        Args:
            element: Element to check
            
        Returns:
            True if rotatable, False otherwise
        """
        if not element or not element.name:
            return False
        prefix = element.name[0].upper()
        return prefix in {"R", "L", "C"}

    def is_multi_terminal(self, element: Element) -> bool:
        """Check if element is multi-terminal (cannot be in series/parallel).
        
        Multi-terminal elements have more than 2 main connections.
        For analog-only, this is primarily for future expansion.
        
        Args:
            element: Element to check
            
        Returns:
            True if multi-terminal, False otherwise
        """
        # For analog-only version, all supported elements are 2-terminal
        # This method is for future expansion
        return False

    def is_passive(self, element: Element) -> bool:
        """Check if element is a passive component (R, L, C).
        
        Passive components can be in true series/parallel connections.
        Active components (V, I sources) should not form series chains.
        
        Args:
            element: Element to check
            
        Returns:
            True if passive, False otherwise
        """
        if not element or not element.name:
            return False
        prefix = element.name[0].upper()
        return prefix in {"R", "L", "C"}

    def find_parallel_connections(self):
        """Identify and mark parallel connections between elements.
        
        Two elements are parallel if they connect the same two nodes.
        For rotatable elements (R, L, C), node order doesn't matter.
        """
        n = len(self.elements)
        
        for i in range(n):
            elem1 = self.elements[i]
            
            if elem1.parallel_connection_present:
                continue  # Already marked as parallel
            
            for j in range(i + 1, n):
                elem2 = self.elements[j]
                
                if elem2.parallel_connection_present:
                    continue  # Already marked as parallel
                
                # Check if they share the same nodes
                same_nodes = (
                    elem1.first_node == elem2.first_node and
                    elem1.second_node == elem2.second_node
                )
                
                # Check if nodes are swapped (for rotatable elements)
                swapped_nodes = False
                if self.is_rotatable(elem1) and self.is_rotatable(elem2):
                    swapped_nodes = (
                        elem1.first_node == elem2.second_node and
                        elem1.second_node == elem2.first_node
                    )
                
                if same_nodes or swapped_nodes:
                    # Mark as parallel connection and track the other element
                    elem1.set_parallel_connection(
                        elem2.name,
                        elem2.get_value_text() if elem2.value else elem2.get_element_type(elem2.name)
                    )
                    # Mark elem2 as having a parallel description
                    elem2.parallel_connection_present = True

    def find_series_connections(self):
        """Identify and mark series connections between elements.
        
        Two elements are in series if they share a node that has
        exactly 2 element connections.
        Only marks series connections between passive components (R, L, C).
        """
        # Track which elements have been marked to avoid duplicates
        marked_elements = set()
        
        # Build node to elements mapping
        node_connections: Dict[str, List[Element]] = {}
        
        for elem in self.elements:
            # Skip elements already marked as parallel or series
            if elem.parallel_connection_present or elem.series_connection_present:
                continue
            
            # Skip multi-terminal elements
            if self.is_multi_terminal(elem):
                continue
            
            # Map element to its nodes
            for node in [elem.first_node, elem.second_node]:
                if node not in node_connections:
                    node_connections[node] = []
                node_connections[node].append(elem)
        
        # Find nodes with exactly 2 connections (series junction)
        for node, elems in node_connections.items():
            if len(elems) == 2:
                elem1, elem2 = elems[0], elems[1]
                
                # Only mark series if both are passive components
                if not (self.is_passive(elem1) and self.is_passive(elem2)):
                    continue
                
                # Skip if already marked as parallel
                if (elem1.parallel_connection_present or 
                    elem2.parallel_connection_present):
                    continue
                
                # Check if already marked (either element)
                if elem1 in marked_elements or elem2 in marked_elements:
                    continue
                
                # Skip if either is already marked as series
                if (elem1.series_connection_present or 
                    elem2.series_connection_present):
                    continue
                
                # Mark as series (only on first element to avoid duplicate descriptions)
                elem1.set_series_connection(
                    elem2.name,
                    node,
                    elem2.get_value_text() if elem2.value else elem2.get_element_type(elem2.name)
                )
                
                # Mark both elements as processed and mark elem2 as having a series description
                marked_elements.add(elem1)
                marked_elements.add(elem2)
                elem2.series_connection_present = True

    def sort_elements_by_nodes(self):
        """Sort elements in ascending order by their first node value.
        
        This helps create logical descriptions where elements are
        described in order of their nodal connections.
        """
        def node_sort_key(elem):
            """Convert node to sortable integer.
            
            'ground' -> 0
            'node X' -> X
            """
            node = elem.first_node
            if node == "ground":
                return 0
            if node.startswith("node "):
                try:
                    return int(node.split()[1])
                except (ValueError, IndexError):
                    pass
            return float('inf')  # Put unknown nodes last
        
        self.elements.sort(key=node_sort_key)

    def generate_description(self) -> str:
        """Generate human-readable description of the circuit.
        
        Returns:
            String describing the circuit and all its elements
        """
        description = ""
        
        # Summary line
        num_elements = len(self.elements)
        num_nodes = len(self.nodes)
        description += f"There are {num_elements} elements and {num_nodes} nodes in this circuit.\n\n"
        
        # Analyze connections
        self.find_parallel_connections()
        self.find_series_connections()
        
        # Sort elements for logical output
        self.sort_elements_by_nodes()
        
        # Generate descriptions for each element
        # Elements that are part of parallel/series connections
        # will generate combined descriptions, others generate individual descriptions
        for elem in self.elements:
            description += elem.to_description()
            description += "\n"
        
        return description

    def from_netlist_file(self, filename: str):
        """Load circuit from a SPICE netlist file.
        
        Args:
            filename: Path to SPICE netlist file
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        self.elements = parse_netlist_file(filename)
        self.nodes = set()
        for elem in self.elements:
            self.nodes.add(elem.first_node)
            self.nodes.add(elem.second_node)

    def from_lcapy(self, lcapy_circuit):
        """Load circuit from a Lcapy Netlist object.
        
        Args:
            lcapy_circuit: Lcapy Netlist or Circuit object
            
        Returns:
            True if successful, False otherwise
        """
        self.elements = parse_lcapy_netlist(lcapy_circuit)
        self.nodes = set()
        for elem in self.elements:
            self.nodes.add(elem.first_node)
            self.nodes.add(elem.second_node)
        
        return len(self.elements) > 0

    def __repr__(self):
        return f"Circuit(elements={len(self.elements)}, nodes={len(self.nodes)})"