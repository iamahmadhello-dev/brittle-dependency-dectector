"""
Dependency Graph Visualization
Generates visual representations of dependency graphs with risk indicators
"""

import graphviz
import tempfile
import os
from typing import Dict, Set, List, Tuple


class DependencyVisualizer:
    """Creates visual representations of dependency graphs using Graphviz."""
    
    def __init__(self, graph, metrics: Dict = None):
        """
        Initialize visualizer.
        
        Args:
            graph: NetworkX DiGraph object
            metrics: Dictionary of metrics from brent.metrics.calculate_metrics()
        """
        self.graph = graph
        self.metrics = metrics or {}
        self.cycle_edges = set()
        self.hotspot_modules = set()
    
    def set_cycle_edges(self, cycle_edges: List[Tuple[str, str]]) -> None:
        """Set edges that are part of cycles (for highlighting)."""
        self.cycle_edges = set(cycle_edges)
    
    def set_hotspot_modules(self, hotspot_modules: Set[str]) -> None:
        """Set modules that are part of hotspots (for highlighting)."""
        self.hotspot_modules = hotspot_modules
    
    def get_node_color(self, module: str) -> str:
        """
        Determine node color based on fragility.
        
        Returns:
            Color hex code or named color
        """
        if module not in self.metrics:
            return "#CCCCCC"  # Gray for unknown
        
        data = self.metrics[module]
        in_degree = data.get("incoming_dependencies", 0)
        
        # Color scheme based on in-degree (incoming dependencies)
        if in_degree == 0:
            return "#90EE90"  # Light green - isolated
        elif in_degree <= 2:
            return "#FFFFE0"  # Light yellow - low dependency
        elif in_degree <= 5:
            return "#FFD700"  # Gold - medium dependency
        elif in_degree <= 10:
            return "#FFA500"  # Orange - high dependency
        else:
            return "#FF6B6B"  # Red - very high dependency (brittle)
    
    def get_node_size(self, module: str) -> float:
        """
        Determine node size based on total degree.
        
        Returns:
            Size multiplier (1.0 = default)
        """
        if module not in self.metrics:
            return 1.0
        
        data = self.metrics[module]
        total_degree = data.get("incoming_dependencies", 0) + data.get("outgoing_dependencies", 0)
        
        # Size proportional to degree
        return max(0.5, min(3.0, 0.5 + total_degree * 0.3))
    
    def create_dot_graph(self, max_nodes: int = None) -> graphviz.Digraph:
        """
        Create Graphviz DOT representation of dependency graph.
        
        Args:
            max_nodes: Limit number of nodes (for large graphs)
        
        Returns:
            graphviz.Digraph object
        """
        dot = graphviz.Digraph(format='svg')
        dot.attr(rankdir='LR')
        dot.attr('node', shape='ellipse', fontname='Arial')
        dot.attr('graph', bgcolor='white', splines='curved')
        
        # Limit nodes if necessary
        nodes_to_draw = list(self.graph.nodes())
        if max_nodes and len(nodes_to_draw) > max_nodes:
            # Draw top nodes by degree
            nodes_by_degree = sorted(
                nodes_to_draw,
                key=lambda n: self.graph.degree(n),
                reverse=True
            )
            nodes_to_draw = nodes_by_degree[:max_nodes]
        
        # Draw nodes
        for node in nodes_to_draw:
            color = self.get_node_color(node)
            size = self.get_node_size(node)
            
            label = node.split('.')[-1]  # Show only module name, not full path
            
            # Add metadata as tooltip
            if node in self.metrics:
                data = self.metrics[node]
                tooltip = f"{node}\n"
                tooltip += f"Incoming: {data.get('incoming_dependencies', 0)}\n"
                tooltip += f"Outgoing: {data.get('outgoing_dependencies', 0)}\n"
                tooltip += f"Centrality: {data.get('degree_centrality', 0):.3f}"
                
                dot.node(
                    node,
                    label=label,
                    color=color,
                    style='filled',
                    tooltip=tooltip,
                    fontsize=str(max(8, min(14, 10 * size)))
                )
            else:
                dot.node(node, label=label, color=color, style='filled')
        
        # Draw edges
        for edge in self.graph.edges():
            source, target = edge
            
            # Skip edges not in our node set
            if source not in nodes_to_draw or target not in nodes_to_draw:
                continue
            
            # Style cycle edges differently
            if edge in self.cycle_edges:
                dot.edge(source, target, color='#FF6B6B', style='bold', arrowhead='vee')
            else:
                dot.edge(source, target, color='#666666', arrowhead='vee')
        
        return dot
    
    def generate_svg(self, max_nodes: int = None) -> str:
        """
        Generate SVG representation of the graph.
        
        Args:
            max_nodes: Limit number of nodes displayed
        
        Returns:
            SVG string
        """
        dot = self.create_dot_graph(max_nodes=max_nodes)
        return dot.pipe(format='svg').decode('utf-8')
    
    def save_svg(self, output_path: str, max_nodes: int = None) -> str:
        """
        Save SVG visualization to file.
        
        Args:
            output_path: Path to save SVG file (with or without .svg extension)
            max_nodes: Limit number of nodes
        
        Returns:
            Path to saved file
        """
        # Remove .svg extension if present
        base_path = output_path.replace('.svg', '')
        
        dot = self.create_dot_graph(max_nodes=15)
        dot.render(base_path, format='svg', cleanup=True)
        
        svg_path = f"{base_path}.svg"
        return svg_path
    
    def create_cycle_graph(self, cycles: List[List[str]], max_cycles: int = 100) -> graphviz.Digraph:
        """
        Create a focused visualization showing only cyclic dependencies.
        
        Args:
            cycles: List of cycles from CycleDetector.find_all_cycles()
            max_cycles: Maximum number of cycles to display (large graphs cause layout issues)
        
        Returns:
            graphviz.Digraph showing cycles
        """
        dot = graphviz.Digraph(format='svg')
        dot.attr(rankdir='LR')
        dot.attr('node', shape='box', fontname='Arial', style='filled', fillcolor='#FFE4E1')
        dot.attr('graph', bgcolor='white')
        
        # Limit cycles if too many
        cycles_to_draw = cycles[:max_cycles]
        
        # Collect all nodes in cycles
        nodes_in_cycles = set()
        for cycle in cycles_to_draw:
            for node in cycle[:-1]:  # Exclude duplicate last element
                nodes_in_cycles.add(node)
        
        # Draw nodes
        for node in nodes_in_cycles:
            label = node.split('.')[-1]
            dot.node(node, label=label)
        
        # Draw cycle edges (all in red/bold)
        for cycle in cycles_to_draw:
            for i in range(len(cycle) - 1):
                source = cycle[i]
                target = cycle[i + 1]
                dot.edge(source, target, color='#FF6B6B', style='bold', arrowhead='vee')
        
        return dot
    
    def save_cycle_graph(self, output_path: str, cycles: List[List[str]], max_cycles: int = 100) -> str:
        """
        Save cycle visualization to file.
        
        Args:
            output_path: Path to save SVG file
            cycles: List of cycles
            max_cycles: Maximum number of cycles to display
        
        Returns:
            Path to saved file
        """
        base_path = output_path.replace('.svg', '')
        dot = self.create_cycle_graph(cycles, max_cycles=max_cycles)
        dot.render(base_path, format='svg', cleanup=True)
        return f"{base_path}.svg"
    
    def create_scc_graph(self, sccs: List[Set[str]]) -> graphviz.Digraph:
        """
        Create visualization highlighting Strongly Connected Components.
        
        Args:
            sccs: List of SCCs from SCCAnalyzer.find_sccs()
        
        Returns:
            graphviz.Digraph showing SCCs
        """
        dot = graphviz.Digraph(format='svg')
        dot.attr(rankdir='LR')
        dot.attr('node', shape='ellipse', fontname='Arial')
        dot.attr('graph', bgcolor='white')
        
        # Colors for different SCCs
        colors = ['#FFE4E1', '#E4F0FF', '#E4FFE4', '#FFFFE4', '#F0E4FF']
        
        # Draw nodes grouped by SCC
        for scc_idx, scc in enumerate(sccs):
            if len(scc) > 1:  # Only highlight multi-node SCCs
                color = colors[scc_idx % len(colors)]
                
                for node in scc:
                    label = node.split('.')[-1]
                    dot.node(node, label=label, style='filled', fillcolor=color)
        
        # Draw edges within SCCs with bold style
        for edge in self.graph.edges():
            source, target = edge
            
            # Check if both nodes are in same SCC
            same_scc = False
            for scc in sccs:
                if source in scc and target in scc:
                    same_scc = True
                    break
            
            if same_scc:
                dot.edge(source, target, color='#FF6B6B', style='bold', arrowhead='vee')
            else:
                dot.edge(source, target, color='#999999', arrowhead='vee')
        
        return dot
    
    def save_scc_graph(self, output_path: str, sccs: List[Set[str]]) -> str:
        """
        Save SCC visualization to file.
        
        Args:
            output_path: Path to save SVG file
            sccs: List of SCCs
        
        Returns:
            Path to saved file
        """
        base_path = output_path.replace('.svg', '')
        dot = self.create_scc_graph(sccs)
        dot.render(base_path, format='svg', cleanup=True)
        return f"{base_path}.svg"
