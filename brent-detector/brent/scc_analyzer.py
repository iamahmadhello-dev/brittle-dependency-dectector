"""
Strongly Connected Components (SCC) Analysis
Identifies tightly-coupled regions in dependency graphs
"""

import networkx as nx
from typing import List, Dict, Set


class SCCAnalyzer:
    """Analyzes Strongly Connected Components in a dependency graph."""
    
    def __init__(self, graph):
        """
        Initialize SCC analyzer.
        
        Args:
            graph: NetworkX DiGraph object (dependency graph)
        """
        self.graph = graph
        self.sccs = None
        self.scc_map = {}  # Maps module -> SCC index
    
    def find_sccs(self) -> List[Set[str]]:
        """
        Find all Strongly Connected Components using Tarjan's algorithm.
        
        Returns:
            List of SCCs, where each SCC is a set of module names
            Example: [{'module_a', 'module_b'}, {'module_c', 'module_d'}, ...]
        """
        if self.sccs is not None:
            return self.sccs
        
        try:
            # NetworkX uses Tarjan's algorithm internally
            self.sccs = list(nx.strongly_connected_components(self.graph))
            
            # Create mapping for quick lookup
            for scc_index, scc in enumerate(self.sccs):
                for module in scc:
                    self.scc_map[module] = scc_index
        except Exception as e:
            print(f"⚠️  Error finding SCCs: {e}")
            self.sccs = []
        
        return self.sccs
    
    def get_scc_count(self) -> int:
        """Get total number of SCCs."""
        if self.sccs is None:
            self.find_sccs()
        return len(self.sccs)
    
    def get_scc_for_module(self, module: str) -> Set[str]:
        """Get the SCC that contains a specific module."""
        if self.sccs is None:
            self.find_sccs()
        
        if module not in self.scc_map:
            return {module}  # Single module is its own SCC
        
        scc_index = self.scc_map[module]
        return self.sccs[scc_index]
    
    def get_large_sccs(self, min_size: int = 3) -> List[Set[str]]:
        """
        Get SCCs with at least min_size modules (potential hotspots).
        
        Args:
            min_size: Minimum SCC size to return (default 3)
        
        Returns:
            List of large SCCs
        """
        if self.sccs is None:
            self.find_sccs()
        
        return [scc for scc in self.sccs if len(scc) > 1 and len(scc) >= min_size]
    
    def get_scc_size_distribution(self) -> Dict[int, int]:
        """
        Get distribution of SCC sizes.
        
        Returns:
            Dictionary mapping size -> count
            Example: {1: 50, 2: 5, 3: 2} means 50 SCCs of size 1, etc.
        """
        if self.sccs is None:
            self.find_sccs()
        
        distribution = {}
        for scc in self.sccs:
            size = len(scc)
            distribution[size] = distribution.get(size, 0) + 1
        
        return distribution
    
    def is_module_isolated(self, module: str) -> bool:
        """Check if a module is in an SCC by itself (not tightly coupled)."""
        scc = self.get_scc_for_module(module)
        return len(scc) == 1
    
    def get_scc_internal_density(self, scc: Set[str]) -> float:
        """
        Calculate internal density of an SCC (0.0 to 1.0).
        Density = actual_edges / possible_edges
        
        Args:
            scc: Set of modules in the SCC
        
        Returns:
            Density score (0.0 = sparse, 1.0 = fully connected)
        """
        scc_list = list(scc)
        n = len(scc_list)
        
        if n <= 1:
            return 0.0
        
        # Count edges within SCC
        internal_edges = 0
        for node_a in scc_list:
            for node_b in scc_list:
                if node_a != node_b and self.graph.has_edge(node_a, node_b):
                    internal_edges += 1
        
        # Maximum possible edges in a directed graph
        max_edges = n * (n - 1)
        
        return internal_edges / max_edges if max_edges > 0 else 0.0
    
    def get_scc_summary(self) -> dict:
        """
        Get summary statistics about SCCs.
        
        Returns:
            Dictionary with SCC statistics
        """
        if self.sccs is None:
            self.find_sccs()
        
        large_sccs = self.get_large_sccs(min_size=3)
        
        return {
            "total_sccs": len(self.sccs),
            "single_node_sccs": sum(1 for scc in self.sccs if len(scc) == 1),
            "multi_node_sccs": sum(1 for scc in self.sccs if len(scc) > 1),
            "large_sccs_count": len(large_sccs),  # Size >= 3
            "size_distribution": self.get_scc_size_distribution(),
            "largest_scc_size": max([len(scc) for scc in self.sccs], default=0),
            "largest_scc_modules": max(self.sccs, key=len) if self.sccs else set(),
        }
    
    def print_sccs(self, min_size: int = 2) -> None:
        """Print all SCCs with at least min_size modules."""
        if self.sccs is None:
            self.find_sccs()
        
        large_sccs = [scc for scc in self.sccs if len(scc) >= min_size]
        
        if not large_sccs:
            print(f"✅ No SCCs with {min_size}+ modules found!")
            return
        
        print(f"\n🔴 Found {len(large_sccs)} SCC(s) with {min_size}+ modules:")
        for i, scc in enumerate(large_sccs, 1):
            density = self.get_scc_internal_density(scc)
            modules = sorted(list(scc))
            print(f"\n  SCC {i} (size={len(scc)}, density={density:.2f}):")
            for module in modules:
                print(f"    - {module}")
