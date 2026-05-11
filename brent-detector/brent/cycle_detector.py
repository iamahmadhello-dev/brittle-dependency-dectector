"""
Cycle Detection in Dependency Graphs
Detects circular dependencies using Johnson's algorithm
"""

import networkx as nx
from typing import List, Set, Tuple


class CycleDetector:
    """Detects all cycles in a dependency graph using Johnson's algorithm."""
    
    def __init__(self, graph):
        """
        Initialize cycle detector.
        
        Args:
            graph: NetworkX DiGraph object (dependency graph)
        """
        self.graph = graph
        self.cycles = []
        self.all_cycles_found = False
    
    def find_all_cycles(self) -> List[List[str]]:
        """
        Find all simple cycles in the graph using Johnson's algorithm.
        
        Returns:
            List of cycles, where each cycle is a list of module names
            Example: [['module_a', 'module_b', 'module_c', 'module_a'], ...]
        """
        if self.all_cycles_found:
            return self.cycles
        
        try:
            # NetworkX has built-in cycle finding
            self.cycles = [list(cycle) for cycle in nx.simple_cycles(self.graph)]
            self.all_cycles_found = True
        except Exception as e:
            print(f"⚠️  Error finding cycles: {e}")
            self.cycles = []
        
        return self.cycles
    
    def get_cycle_count(self) -> int:
        """Get total number of cycles found."""
        if not self.all_cycles_found:
            self.find_all_cycles()
        return len(self.cycles)
    
    def get_modules_in_cycles(self) -> Set[str]:
        """Get all modules that are part of any cycle."""
        if not self.all_cycles_found:
            self.find_all_cycles()
        
        modules_in_cycles = set()
        for cycle in self.cycles:
            modules_in_cycles.update(cycle[:-1])  # Exclude the duplicate last element
        
        return modules_in_cycles
    
    def get_cycle_edges(self) -> List[Tuple[str, str]]:
        """Get all edges that are part of cycles."""
        if not self.all_cycles_found:
            self.find_all_cycles()
        
        cycle_edges = set()
        for cycle in self.cycles:
            for i in range(len(cycle) - 1):
                cycle_edges.add((cycle[i], cycle[i + 1]))
        
        return list(cycle_edges)
    
    def is_module_in_cycle(self, module: str) -> bool:
        """Check if a specific module is part of any cycle."""
        modules_in_cycles = self.get_modules_in_cycles()
        return module in modules_in_cycles
    
    def get_cycles_for_module(self, module: str) -> List[List[str]]:
        """Get all cycles that contain a specific module."""
        if not self.all_cycles_found:
            self.find_all_cycles()
        
        return [cycle for cycle in self.cycles if module in cycle[:-1]]
    
    def get_cycle_complexity(self, cycle: List[str]) -> int:
        """Get complexity (length) of a cycle."""
        return len(cycle) - 1  # Exclude duplicate last element
    
    def get_complexity_distribution(self) -> dict:
        """Get distribution of cycle complexities."""
        if not self.all_cycles_found:
            self.find_all_cycles()
        
        distribution = {}
        for cycle in self.cycles:
            complexity = self.get_cycle_complexity(cycle)
            distribution[complexity] = distribution.get(complexity, 0) + 1
        
        return distribution
    
    def print_cycles(self) -> None:
        """Print all detected cycles in readable format."""
        if not self.all_cycles_found:
            self.find_all_cycles()
        
        if not self.cycles:
            print("✅ No cycles found - dependency graph is acyclic!")
            return
        
        print(f"\n🔴 Found {len(self.cycles)} cycle(s):")
        for i, cycle in enumerate(self.cycles, 1):
            cycle_str = " → ".join(cycle)
            print(f"  Cycle {i}: {cycle_str}")
    
    def get_summary(self) -> dict:
        """Get summary statistics about cycles."""
        if not self.all_cycles_found:
            self.find_all_cycles()
        
        modules_in_cycles = self.get_modules_in_cycles()
        
        return {
            "total_cycles": len(self.cycles),
            "modules_in_cycles": len(modules_in_cycles),
            "is_acyclic": len(self.cycles) == 0,
            "cycle_complexity_distribution": self.get_complexity_distribution(),
            "longest_cycle_length": max([len(c) for c in self.cycles], default=0),
        }
