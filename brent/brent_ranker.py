import math
from typing import List, Tuple, Dict


def rank_brents(metrics, top_percentage=0.05, use_fragility_index=True):
    """
    Rank modules as "Brittle Dependencies" based on dependency criticality.
    
    Args:
        metrics: Dictionary of metrics from brent.metrics.calculate_metrics()
        top_percentage: Percentage of modules to return (default 5%)
        use_fragility_index: If True, use advanced fragility index; if False, use simple score
    
    Returns:
        List of tuples: (module_name, score, metrics_dict)
    """
    scored_modules = []

    if use_fragility_index and all("scc_size" in data for data in metrics.values()):
        # Use advanced fragility index
        scored_modules = _calculate_fragility_index(metrics)
    else:
        # Fallback to original scoring (backward compatible)
        scored_modules = _calculate_brittle_score(metrics)

    # Sort descending by score
    scored_modules.sort(key=lambda x: x[1], reverse=True)

    # Select top % (rounded up)
    top_n = max(1, math.ceil(len(scored_modules) * top_percentage))

    return scored_modules[:top_n]


def _calculate_brittle_score(metrics: Dict) -> List[Tuple[str, float, Dict]]:
    """
    Original scoring formula (backward compatible).
    
    Brittle Score = (0.7 × Incoming Dependencies) + (0.3 × Degree Centrality)
    """
    scored_modules = []

    for module, data in metrics.items():
        # Normalize incoming dependencies
        max_incoming = max([d["incoming_dependencies"] for d in metrics.values()], default=1)
        normalized_incoming = data["incoming_dependencies"] / max_incoming if max_incoming > 0 else 0
        
        # Get centrality (use degree_centrality or centrality for backward compatibility)
        centrality = data.get("degree_centrality", data.get("centrality", 0))
        
        score = (0.7 * normalized_incoming) + (0.3 * centrality)
        scored_modules.append((module, score, data))

    return scored_modules


def _calculate_fragility_index(metrics: Dict) -> List[Tuple[str, float, Dict]]:
    """
    Advanced fragility index combining multiple risk factors.
    
    Fragility Index = 0.35×in-degree + 0.35×cycle-risk + 0.20×scc-risk + 0.10×betweenness
    
    Where:
    - in-degree: Normalized incoming dependencies (higher = more critical)
    - cycle-risk: 1 if in cycle, 0 otherwise (cycles = tight coupling)
    - scc-risk: (scc_size - 1) / (max_scc_size - 1) (larger SCCs = more fragile)
    - betweenness: Normalized betweenness centrality (intermediaries are critical)
    """
    scored_modules = []
    
    # Normalize metrics
    max_incoming = max([d["incoming_dependencies"] for d in metrics.values()], default=1)
    max_betweenness = max([d.get("betweenness_centrality", 0) for d in metrics.values()], default=1)
    max_scc_size = max([d["scc_size"] for d in metrics.values()], default=1)
    
    for module, data in metrics.items():
        # Component 1: In-degree risk (35%)
        in_degree_risk = (data["incoming_dependencies"] / max_incoming) if max_incoming > 0 else 0
        
        # Component 2: Cycle risk (35%) - modules in cycles are more fragile
        cycle_risk = 1.0 if data.get("in_cycle", False) else 0.0
        
        # Component 3: SCC risk (20%) - larger SCCs indicate tighter coupling
        scc_size = data.get("scc_size", 1)
        scc_risk = (scc_size - 1) / (max_scc_size - 1) if max_scc_size > 1 else 0.0
        
        # Component 4: Betweenness centrality (10%) - intermediaries are critical
        betweenness = data.get("betweenness_centrality", 0)
        betweenness_normalized = (betweenness / max_betweenness) if max_betweenness > 0 else 0
        
        # Composite fragility index
        fragility_index = (
            0.35 * in_degree_risk +
            0.35 * cycle_risk +
            0.20 * scc_risk +
            0.10 * betweenness_normalized
        )
        
        scored_modules.append((module, fragility_index, data))
    
    return scored_modules


def get_ranking_explanation(module: str, rank: int, score: float, data: Dict) -> str:
    """
    Get human-readable explanation of why a module was ranked.
    
    Args:
        module: Module name
        rank: Ranking position (1, 2, 3, ...)
        score: Fragility score
        data: Metrics dictionary for this module
    
    Returns:
        Formatted explanation string
    """
    explanation = f"\n🔴 #{rank} {module} (Fragility Score: {score:.4f})\n"
    
    explanation += f"   ├─ Incoming Dependencies: {data['incoming_dependencies']} modules depend on this\n"
    explanation += f"   ├─ Outgoing Dependencies: {data['outgoing_dependencies']} dependencies\n"
    explanation += f"   ├─ In Cycle: {'Yes ⚠️' if data.get('in_cycle', False) else 'No ✅'}\n"
    explanation += f"   ├─ SCC Size: {data.get('scc_size', 1)} (tightly coupled group size)\n"
    explanation += f"   ├─ Betweenness Centrality: {data.get('betweenness_centrality', 0):.4f}\n"
    explanation += f"   └─ PageRank: {data.get('pagerank', 0):.6f}\n"
    
    if data['incoming_dependencies'] > 10:
        explanation += "   ⚠️  HIGH RISK: Many modules depend on this one!\n"
    
    if data.get('in_cycle', False):
        explanation += "   ⚠️  CIRCULAR: Part of dependency cycle!\n"
    
    if data.get('scc_size', 1) > 3:
        explanation += "   ⚠️  HOTSPOT: Part of tightly-coupled region!\n"
    
    return explanation


def print_ranking(ranked_modules: List[Tuple[str, float, Dict]]) -> None:
    """Print ranked modules with explanations."""
    print("\n" + "="*80)
    print("🏆 BRITTLE DEPENDENCY RANKING (Most Fragile Modules)")
    print("="*80)
    
    for rank, (module, score, data) in enumerate(ranked_modules, 1):
        print(get_ranking_explanation(module, rank, score, data))