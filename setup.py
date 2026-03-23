"""Setup configuration for netlist-to-text package."""

from setuptools import setup, find_packages

setup(
    name="netlist-to-text",
    version="0.1.0",
    description="Generate descriptive text from circuit netlists for accessibility",
    long_description=open("README.md").read(),
    author="Ported from NetlistToText by johnjhealy",
    url="https://github.com/johnjhealy/NetlistToText",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "lcapy": ["lcapy"],
    },
    entry_points={
        "console_scripts": [
            "netlist-to-text=netlist_to_text.cli:main",
        ],
    },
)
