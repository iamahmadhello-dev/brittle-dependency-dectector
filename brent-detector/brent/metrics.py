import networkx as nx
from brent.cycle_detector import CycleDetector
from brent.scc_analyzer import SCCAnalyzer


def calculate_metrics(graph):
    """
    Calculate comprehensive graph metrics for dependency analysis.
    
    Returns a dictionary with:
    - incoming_dependencies: Number of modules that depend on this module
    - outgoing_dependencies: Number of modules this module depends on
    - degree_centrality: Basic centrality (0-1)
    - betweenness_centrality: Intermediary importance (0-1)
    - closeness_centrality: Network proximity (0-1)
    - pagerank: Importance based on network structure (0-1)
    - in_cycle: Whether module is part of any cycle
    - scc_size: Size of the SCC this module belongs to
    """
    metrics = {}

    # Basic metrics
    incoming_dependencies = dict(graph.in_degree())
    outgoing_dependencies = dict(graph.out_degree())
    
    # Centrality metrics
    degree_centrality = nx.degree_centrality(graph)
    betweenness_centrality = _safe_calculate(nx.betweenness_centrality, graph)
    closeness_centrality = _safe_calculate(nx.closeness_centrality, graph)
    pagerank = nx.pagerank(graph, alpha=0.85)
    
    # Try eigenvector centrality (might not converge for some graphs)
    eigenvector_centrality = _safe_calculate(nx.eigenvector_centrality, graph, max_iter=1000)
    
    # Cycle and SCC analysis
    cycle_detector = CycleDetector(graph)
    modules_in_cycles = cycle_detector.get_modules_in_cycles()
    
    scc_analyzer = SCCAnalyzer(graph)
    scc_analyzer.find_sccs()

    for node in graph.nodes():
        scc = scc_analyzer.get_scc_for_module(node)
        
        metrics[node] = {
            "incoming_dependencies": incoming_dependencies.get(node, 0),
            "outgoing_dependencies": outgoing_dependencies.get(node, 0),
            "degree_centrality": degree_centrality.get(node, 0),
            "betweenness_centrality": betweenness_centrality.get(node, 0),
            "closeness_centrality": closeness_centrality.get(node, 0),
            "pagerank": pagerank.get(node, 0),
            "eigenvector_centrality": eigenvector_centrality.get(node, 0),
            "in_cycle": node in modules_in_cycles,
            "scc_size": len(scc),
        }

    return metrics


def _safe_calculate(centrality_func, graph, **kwargs):
    """
    Safely calculate centrality metric with fallback.
    
    Some centrality metrics may fail to converge or for edge cases.
    Returns empty dict if calculation fails.
    """
    try:
        return centrality_func(graph, **kwargs)
    except Exception as e:
        print(f"⚠️  Warning: Could not calculate {centrality_func.__name__}: {e}")
        # Return default values
        return {node: 0.0 for node in graph.nodes()}


def normalize_metrics(metrics: dict) -> dict:
    """
    Normalize all centrality metrics to 0-1 range.
    
    Args:
        metrics: Dictionary of metrics from calculate_metrics()
    
    Returns:
        Dictionary with normalized metrics
    """
    normalized = {}
    
    # Get max values for normalization
    centrality_fields = [
        "betweenness_centrality",
        "closeness_centrality",
        "pagerank",
        "eigenvector_centrality"
    ]
    
    max_values = {field: 0.0 for field in centrality_fields}
    for module_metrics in metrics.values():
        for field in centrality_fields:
            if field in module_metrics:
                max_values[field] = max(max_values[field], module_metrics[field])
    
    # Normalize
    for module, module_metrics in metrics.items():
        normalized[module] = module_metrics.copy()
        for field in centrality_fields:
            if field in module_metrics and max_values[field] > 0:
                normalized[module][field] = module_metrics[field] / max_values[field]
    
    return normalized