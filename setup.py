"""Setup configuration for circuit-a11y package."""

from setuptools import setup, find_packages

setup(
    name="circuit-a11y",
    version="0.1.0",
    description="Generate accessible circuit diagrams and alt-text from KiCAD schematics and SPICE netlists",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="",
    url="",
    packages=find_packages(include=["netlist_to_text*", "circuit_a11y*"]),
    package_dir={"kicad2circuitikz": "src/kicad2circuitikz"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Education",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "matplotlib>=3.3.0",
    ],
    extras_require={
        "lcapy": ["lcapy"],
        "png": ["Pillow>=9.0.0"],
    },
    entry_points={
        "console_scripts": [
            "netlist-to-text=netlist_to_text.cli:main",
            "circuit-a11y=circuit_a11y.cli:main",
        ],
    },
)
