"""Tests for utils module."""

import pytest
from netlist_to_text.utils import spell_out_multiplier


class TestSpellOutMultiplier:
    """Test unit multiplier spelling for accessibility."""

    def test_suffix_kilo(self):
        """Test kilo suffix."""
        assert spell_out_multiplier("1k") == "1 kilo"
        assert spell_out_multiplier("10k") == "10 kilo"
        assert spell_out_multiplier("2.5k") == "2.5 kilo"

    def test_suffix_milli(self):
        """Test milli suffix."""
        assert spell_out_multiplier("1m") == "1 milli"
        assert spell_out_multiplier("10m") == "10 milli"

    def test_suffix_micro(self):
        """Test micro suffix."""
        assert spell_out_multiplier("1u") == "1 micro"
        assert spell_out_multiplier("10u") == "10 micro"

    def test_suffix_nano(self):
        """Test nano suffix."""
        assert spell_out_multiplier("1n") == "1 nano"
        assert spell_out_multiplier("100n") == "100 nano"

    def test_scientific_milli(self):
        """Test scientific notation for milli."""
        assert spell_out_multiplier("1e-3") == "1 milli"
        assert spell_out_multiplier("10e-3") == "10 milli"

    def test_scientific_micro(self):
        """Test scientific notation for micro."""
        assert spell_out_multiplier("1e-6") == "1 micro"
        assert spell_out_multiplier("10e-6") == "10 micro"

    def test_scientific_nano(self):
        """Test scientific notation for nano."""
        assert spell_out_multiplier("1e-9") == "1 nano"
        assert spell_out_multiplier("100e-9") == "100 nano"

    def test_scientific_kilo(self):
        """Test scientific notation for kilo."""
        assert spell_out_multiplier("1e3") == "1 kilo"
        assert spell_out_multiplier("10e3") == "10 kilo"

    def test_scientific_mega(self):
        """Test scientific notation for mega."""
        assert spell_out_multiplier("1e6") == "1 mega"
        assert spell_out_multiplier("10e6") == "10 mega"

    def test_plain_number(self):
        """Test plain number without multiplier."""
        assert spell_out_multiplier("10") == "10"
        assert spell_out_multiplier("100") == "100"
        assert spell_out_multiplier("1.5") == "1.5"

    def test_scientific_intermediate_exponents(self):
        """Test intermediate exponents (close to standard multipliers)."""
        # 1e-4 = 0.1 milli, approximate as milli
        assert spell_out_multiplier("1e-4") == "1 milli"
        # 1e-5 = 0.01 milli, approximate as milli
        assert spell_out_multiplier("1e-5") == "1 milli"

    def test_empty_value(self):
        """Test empty value."""
        assert spell_out_multiplier("") == ""
        assert spell_out_multiplier(None) is None

    def test_case_insensitive(self):
        """Test that scientific notation is case insensitive."""
        assert spell_out_multiplier("1E-3") == "1 milli"
        assert spell_out_multiplier("1e+3") == "1 kilo"
