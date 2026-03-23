"""Tests for the parser module."""

import pytest
import tempfile
import os
from netlist_to_text.parser import (
    is_comment_or_directive,
    parse_element_name,
    parse_spice_line,
    parse_netlist_file,
    detect_format
)


class TestCommentAndDirectiveDetection:
    """Test detection of comments and directives."""

    def test_empty_line(self):
        """Test empty line detection."""
        assert is_comment_or_directive("") is True
        assert is_comment_or_directive("   ") is True

    def test_comment_line(self):
        """Test comment line detection."""
        assert is_comment_or_directive("* This is a comment") is True
        assert is_comment_or_directive("* Comment") is True
        assert is_comment_or_directive("  * Indented comment") is True

    def test_directive_line(self):
        """Test directive line detection."""
        assert is_comment_or_directive(".model NPN") is True
        assert is_comment_or_directive(".lib diode.lib") is True
        assert is_comment_or_directive(".end") is True
        assert is_comment_or_directive(".tran 1n 10n") is True

    def test_element_line(self):
        """Test that element lines are not skipped."""
        assert is_comment_or_directive("R1 0 1 1k") is False
        assert is_comment_or_directive("C1 1 2 1u") is False
        assert is_comment_or_directive("V1 0 1 10") is False


class TestElementNameParsing:
    """Test element name parsing and cleaning."""

    def test_standard_name(self):
        """Test standard element name."""
        assert parse_element_name("R1") == "R1"
        assert parse_element_name("C10") == "C10"
        assert parse_element_name("V2") == "V2"

    def test_conductance_name(self):
        """Test conductance name conversion (R to Y)."""
        assert parse_element_name("R1G") == "Y1"
        assert parse_element_name("R10G") == "Y10"

    def test_lamp_diode_name(self):
        """Test lamp diode name cleaning."""
        assert "Lamp1" in parse_element_name("DLamp1")
        assert "Lamp2" in parse_element_name("DLamp2")


class TestSpiceLineParsing:
    """Test SPICE line parsing."""

    def test_resistor_line(self):
        """Test resistor line parsing."""
        elem = parse_spice_line("R1 N001 N002 1k")
        assert elem is not None
        assert elem.name == "R1"
        assert elem.first_node == "node 1"
        assert elem.second_node == "node 2"
        assert elem.value == "1k"

    def test_capacitor_line(self):
        """Test capacitor line parsing."""
        elem = parse_spice_line("C1 0 1 1u")
        assert elem is not None
        assert elem.name == "C1"
        assert elem.first_node == "ground"
        assert elem.second_node == "node 1"
        assert elem.value == "1u"

    def test_voltage_source_line(self):
        """Test voltage source line parsing."""
        elem = parse_spice_line("V1 0 1 10")
        assert elem is not None
        assert elem.name == "V1"
        assert elem.first_node == "ground"
        assert elem.second_node == "node 1"
        assert elem.value == "10"

    def test_current_source_line(self):
        """Test current source line parsing."""
        elem = parse_spice_line("I1 N001 N002 1mA")
        assert elem is not None
        assert elem.name == "I1"
        assert elem.value == "1mA"

    def test_inductor_line(self):
        """Test inductor line parsing."""
        elem = parse_spice_line("L1 0 N005 10mH")
        assert elem is not None
        assert elem.name == "L1"
        assert elem.value == "10mH"

    def test_waveform_value(self):
        """Test waveform value parsing."""
        elem = parse_spice_line("V1 0 1 PULSE 0 5 1n")
        assert elem is not None
        assert elem.value == "PULSE 0 5 1n"

    def test_value_with_semicolon(self):
        """Test value with semicolon (Lcapy drawing directives)."""
        elem = parse_spice_line("L1 1 2 1e-3; right, size=1.2")
        assert elem is not None
        assert elem.value == "1e-3"
        # Semicolon and drawing directives should be stripped

    def test_complex_value_with_semicolon(self):
        """Test complex value with semicolon."""
        elem = parse_spice_line("C1 2 3 1e-4; right, size=1.2, color=blue")
        assert elem is not None
        assert elem.value == "1e-4"

    def test_plain_value_without_semicolon(self):
        """Test plain value without semicolon still works."""
        elem = parse_spice_line("R1 0 1 1k")
        assert elem is not None
        assert elem.value == "1k"

    def test_insufficient_parts(self):
        """Test line with insufficient parts."""
        elem = parse_spice_line("R1 N001")  # Only name and one node
        assert elem is None

    def test_unsupported_element(self):
        """Test unsupported element type."""
        elem = parse_spice_line("Q1 1 2 0 NPN")  # BJT not supported
        assert elem is None


class TestFileParsing:
    """Test file parsing functionality."""

    def test_simple_netlist_file(self):
        """Test parsing a simple netlist file."""
        content = """* Simple voltage divider
V1 0 1 10
R1 1 2 1k
R2 2 0 2k
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.net', delete=False) as f:
            f.write(content)
            f.flush()
            
            elements = parse_netlist_file(f.name)
            assert len(elements) == 3
            
            assert elements[0].name == "V1"
            assert elements[1].name == "R1"
            assert elements[2].name == "R2"
            
            os.unlink(f.name)

    def test_file_with_comments(self):
        """Test parsing file with comments and directives."""
        content = """* Test circuit
.model NPN NPN
.lib diodes.lib
V1 0 1 10
* Another comment
R1 1 0 1k
.end
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.net', delete=False) as f:
            f.write(content)
            f.flush()
            
            elements = parse_netlist_file(f.name)
            # Should only parse V1 and R1, skipping comments and directives
            assert len(elements) == 2
            
            assert elements[0].name == "V1"
            assert elements[1].name == "R1"
            
            os.unlink(f.name)

    def test_parallel_resistors(self):
        """Test parsing parallel resistors."""
        content = """* Parallel resistors
R1 0 1 1k
R2 0 1 2k
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.net', delete=False) as f:
            f.write(content)
            f.flush()
            
            elements = parse_netlist_file(f.name)
            assert len(elements) == 2
            
            os.unlink(f.name)

    def test_file_not_found(self):
        """Test handling of non-existent file."""
        with pytest.raises(FileNotFoundError):
            parse_netlist_file("nonexistent_file.net")


class TestFormatDetection:
    """Test input format detection."""

    def test_spice_extension(self):
        """Test SPICE file extension detection."""
        assert detect_format("circuit.net") == 'spice'
        assert detect_format("circuit.cir") == 'spice'
        assert detect_format("circuit.spice") == 'spice'

    def test_lcapy_script(self):
        """Test Lcapy Python script detection."""
        content = """from lcapy import Circuit
cct = Circuit('R1 1 2 1k')
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(content)
            f.flush()
            
            format_detected = detect_format(f.name)
            assert format_detected == 'lcapy'
            
            os.unlink(f.name)

    def test_unknown_format(self):
        """Test unknown format detection."""
        assert detect_format("circuit.txt") == 'unknown'
        assert detect_format("data.dat") == 'unknown'
