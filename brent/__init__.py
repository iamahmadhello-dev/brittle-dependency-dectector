"""
Brent Detector - Static Analysis Tool for Identifying Critical Software Modules

A tool for identifying critical, highly-depended-upon modules in Python codebases
using formal dependency graph analysis.

Main components:
- scanner: Discovers Python files in projects
- parser: Extracts dependencies via AST
- graph_builder: Constructs dependency graphs
- metrics: Computes importance metrics
- brent_ranker: Identifies and ranks critical modules
- reporter: Generates analysis reports
"""

__version__ = "1.0.0"
__author__ = "FYP Student"
__license__ = "MIT"

from .scanner import get_python_files
from .parser import extract_imports
from .graph_builder import build_dependency_graph
from .metrics import calculate_metrics
from .brent_ranker import rank_brents
from .reporter import (
    generate_json_report,
    save_json_report,
    generate_csv_report,
    generate_html_report,
)

__all__ = [
    "get_python_files",
    "extract_imports",
    "build_dependency_graph",
    "calculate_metrics",
    "rank_brents",
    "generate_json_report",
    "save_json_report",
    "generate_csv_report",
    "generate_html_report",
]
