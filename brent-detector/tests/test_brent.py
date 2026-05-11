"""
Unit tests for Brent Detector components.
"""

import unittest
import tempfile
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brent.scanner import get_python_files
from brent.parser import extract_imports
from brent.graph_builder import build_dependency_graph, _find_matching_modules
from brent.metrics import calculate_metrics
from brent.brent_ranker import rank_brents


class TestScanner(unittest.TestCase):
    """Test the file scanner."""

    def setUp(self):
        """Create a temporary directory with test Python files."""
        self.test_dir = tempfile.TemporaryDirectory()
        
        # Create test Python files
        self.file1 = os.path.join(self.test_dir.name, "module1.py")
        with open(self.file1, "w") as f:
            f.write("# Test file 1\n")
        
        self.file2 = os.path.join(self.test_dir.name, "module2.py")
        with open(self.file2, "w") as f:
            f.write("# Test file 2\n")
        
        # Create subdirectory with Python file
        subdir = os.path.join(self.test_dir.name, "subdir")
        os.makedirs(subdir)
        self.file3 = os.path.join(subdir, "module3.py")
        with open(self.file3, "w") as f:
            f.write("# Test file 3\n")
    
    def tearDown(self):
        """Clean up temporary directory."""
        self.test_dir.cleanup()
    
    def test_find_python_files(self):
        """Test finding Python files."""
        files = get_python_files(self.test_dir.name)
        self.assertEqual(len(files), 3)
        
        # Check that all files are found
        filenames = [os.path.basename(f) for f in files]
        self.assertIn("module1.py", filenames)
        self.assertIn("module2.py", filenames)
        self.assertIn("module3.py", filenames)
    
    def test_no_python_files(self):
        """Test directory with no Python files."""
        empty_dir = tempfile.TemporaryDirectory()
        files = get_python_files(empty_dir.name)
        self.assertEqual(len(files), 0)
        empty_dir.cleanup()


class TestParser(unittest.TestCase):
    """Test the import parser."""

    def setUp(self):
        """Create test Python files with imports."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.project_root = self.test_dir.name
    
    def tearDown(self):
        """Clean up temporary directory."""
        self.test_dir.cleanup()
    
    def test_extract_standard_imports(self):
        """Test extracting standard library imports."""
        test_file = os.path.join(self.test_dir.name, "test.py")
        with open(test_file, "w") as f:
            f.write("""
import os
import sys
import json
""")
        
        imports = extract_imports(test_file, self.project_root)
        self.assertIn("os", imports)
        self.assertIn("sys", imports)
        self.assertIn("json", imports)
    
    def test_extract_from_imports(self):
        """Test extracting 'from' imports."""
        test_file = os.path.join(self.test_dir.name, "test.py")
        with open(test_file, "w") as f:
            f.write("""
from os import path
from django import db
from myapp.models import User
""")
        
        imports = extract_imports(test_file, self.project_root)
        self.assertIn("os", imports)
        self.assertIn("django", imports)
        self.assertIn("myapp.models", imports)
    
    def test_invalid_syntax(self):
        """Test handling of files with syntax errors."""
        test_file = os.path.join(self.test_dir.name, "test.py")
        with open(test_file, "w") as f:
            f.write("this is not valid python !!!")
        
        # Should not raise exception, just return empty list
        imports = extract_imports(test_file, self.project_root)
        self.assertEqual(imports, [])


class TestGraphMatching(unittest.TestCase):
    """Test module matching in graph building."""
    
    def test_exact_match(self):
        """Test exact module name matching."""
        modules = {"app", "app.models", "app.views", "utils"}
        matches = _find_matching_modules("app", modules)
        self.assertIn("app", matches)
        self.assertIn("app.models", matches)
        self.assertIn("app.views", matches)
        self.assertNotIn("utils", matches)
    
    def test_submodule_match(self):
        """Test submodule matching."""
        modules = {"app", "app.models", "app.models.user"}
        matches = _find_matching_modules("app.models", modules)
        self.assertIn("app.models", matches)
        self.assertIn("app.models.user", matches)
    
    def test_no_match(self):
        """Test when there's no match."""
        modules = {"app", "utils"}
        matches = _find_matching_modules("nonexistent", modules)
        self.assertEqual(len(matches), 0)


class TestMetrics(unittest.TestCase):
    """Test metric calculations."""
    
    def setUp(self):
        """Create a simple test graph."""
        import networkx as nx
        
        self.graph = nx.DiGraph()
        self.graph.add_edges_from([
            ("a", "b"),
            ("a", "c"),
            ("b", "c"),
            ("d", "b"),
        ])
    
    def test_calculate_metrics(self):
        """Test that metrics are calculated correctly."""
        metrics = calculate_metrics(self.graph)
        
        # Check that all nodes have metrics
        self.assertEqual(len(metrics), 4)
        
        # Check specific metrics
        self.assertEqual(metrics["a"]["incoming_dependencies"], 0)
        self.assertEqual(metrics["a"]["outgoing_dependencies"], 2)
        
        self.assertEqual(metrics["b"]["incoming_dependencies"], 2)  # a and d depend on b
        self.assertEqual(metrics["b"]["outgoing_dependencies"], 1)
        
        self.assertEqual(metrics["c"]["incoming_dependencies"], 2)  # a and b depend on c
        self.assertEqual(metrics["c"]["outgoing_dependencies"], 0)
    
    def test_centrality_computation(self):
        """Test that centrality is computed."""
        metrics = calculate_metrics(self.graph)
        
        for node, data in metrics.items():
            # Centrality should be between 0 and 1
            self.assertGreaterEqual(data["centrality"], 0)
            self.assertLessEqual(data["centrality"], 1)


class TestRanker(unittest.TestCase):
    """Test Brent ranking."""
    
    def setUp(self):
        """Create test metrics."""
        self.metrics = {
            "module_a": {"incoming_dependencies": 5, "outgoing_dependencies": 1, "centrality": 0.5},
            "module_b": {"incoming_dependencies": 2, "outgoing_dependencies": 3, "centrality": 0.3},
            "module_c": {"incoming_dependencies": 1, "outgoing_dependencies": 2, "centrality": 0.1},
        }
    
    def test_top_5_percent(self):
        """Test selecting top 5% of Brents."""
        top_brents = rank_brents(self.metrics, top_percentage=0.05)
        # 5% of 3 = 0.15, rounded up to 1
        self.assertEqual(len(top_brents), 1)
        self.assertEqual(top_brents[0][0], "module_a")
    
    def test_top_50_percent(self):
        """Test selecting top 50% of Brents."""
        top_brents = rank_brents(self.metrics, top_percentage=0.5)
        # 50% of 3 = 1.5, rounded up to 2
        self.assertEqual(len(top_brents), 2)
        self.assertEqual(top_brents[0][0], "module_a")
    
    def test_ranking_uses_score(self):
        """Test that modules are ranked by score."""
        top_brents = rank_brents(self.metrics, top_percentage=1.0)
        
        # module_a should be highest (score = 0.7*5 + 0.3*0.5 = 3.65)
        # module_b should be second (score = 0.7*2 + 0.3*0.3 = 1.49)
        # module_c should be third (score = 0.7*1 + 0.3*0.1 = 0.73)
        
        self.assertEqual(top_brents[0][0], "module_a")
        self.assertEqual(top_brents[1][0], "module_b")
        self.assertEqual(top_brents[2][0], "module_c")


if __name__ == "__main__":
    unittest.main()
