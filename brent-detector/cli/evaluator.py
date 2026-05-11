"""
Multi-Project Evaluation Framework
Analyzes and compares brittle dependencies across multiple projects
"""

import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict
from datetime import datetime


class ProjectEvaluator:
    """Evaluates multiple Python projects for brittle dependencies."""
    
    def __init__(self, projects_dir: str = None):
        """
        Initialize evaluator.
        
        Args:
            projects_dir: Directory containing multiple projects
        """
        self.projects_dir = projects_dir
        self.results = {}
        self.evaluation_data = []
    
    def evaluate_project(self, project_path: str) -> Dict:
        """
        Run Brent Detector on a single project.
        
        Args:
            project_path: Path to project directory
        
        Returns:
            Dictionary with evaluation results
        """
        project_name = os.path.basename(project_path)
        
        print(f"\n📊 Evaluating project: {project_name}")
        print(f"   Path: {project_path}")
        
        try:
            from brent.scanner import scan_directory
            from brent.parser import extract_imports
            from brent.graph_builder import build_dependency_graph
            from brent.metrics import calculate_metrics, normalize_metrics
            from brent.brent_ranker import rank_brents
            from brent.cycle_detector import CycleDetector
            from brent.scc_analyzer import SCCAnalyzer
            
            # Scan and build graph
            python_files = scan_directory(project_path)
            imports_dict = {}
            for file_path in python_files:
                imports = extract_imports(file_path)
                imports_dict[file_path] = imports
            
            graph = build_dependency_graph(project_path, imports_dict)
            
            # Calculate metrics
            metrics = calculate_metrics(graph)
            metrics = normalize_metrics(metrics)
            
            # Rank modules
            top_modules = rank_brents(metrics, top_percentage=0.10)
            
            # Detect cycles
            cycle_detector = CycleDetector(graph)
            cycles = cycle_detector.find_all_cycles()
            
            # Find SCCs
            scc_analyzer = SCCAnalyzer(graph)
            sccs = scc_analyzer.find_sccs()
            
            result = {
                "project_name": project_name,
                "project_path": project_path,
                "timestamp": datetime.now().isoformat(),
                "statistics": {
                    "total_modules": graph.number_of_nodes(),
                    "total_dependencies": graph.number_of_edges(),
                    "total_files": len(python_files),
                    "cycles_count": len(cycles),
                    "sccs_count": len(sccs),
                    "large_sccs": len([s for s in sccs if len(s) >= 3]),
                },
                "top_modules": [
                    {
                        "rank": i,
                        "module": mod,
                        "fragility_score": float(score),
                        "incoming_dependencies": data.get("incoming_dependencies", 0),
                        "in_cycle": data.get("in_cycle", False),
                        "scc_size": data.get("scc_size", 1),
                    }
                    for i, (mod, score, data) in enumerate(top_modules, 1)
                ],
                "graph_metrics": {
                    "avg_in_degree": sum([data["incoming_dependencies"] for data in metrics.values()]) / len(metrics) if metrics else 0,
                    "avg_out_degree": sum([data["outgoing_dependencies"] for data in metrics.values()]) / len(metrics) if metrics else 0,
                    "density": (graph.number_of_edges() / (graph.number_of_nodes() * (graph.number_of_nodes() - 1))) if graph.number_of_nodes() > 1 else 0,
                }
            }
            
            self.results[project_name] = result
            self.evaluation_data.append(result)
            
            print(f"   ✅ Modules: {result['statistics']['total_modules']}")
            print(f"   ✅ Dependencies: {result['statistics']['total_dependencies']}")
            print(f"   ⚠️  Cycles: {result['statistics']['cycles_count']}")
            print(f"   ⚠️  Hotspots: {result['statistics']['large_sccs']}")
            
            return result
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return {"error": str(e), "project_name": project_name}
    
    def evaluate_multiple_projects(self, project_paths: List[str]) -> Dict:
        """
        Evaluate multiple projects.
        
        Args:
            project_paths: List of project directories
        
        Returns:
            Dictionary with all evaluation results
        """
        print("\n" + "="*80)
        print("MULTI-PROJECT EVALUATION FRAMEWORK")
        print("="*80)
        
        for project_path in project_paths:
            if os.path.isdir(project_path):
                self.evaluate_project(project_path)
        
        return self.results
    
    def generate_comparison_report(self, output_path: str = "evaluation_report.json") -> str:
        """
        Generate comparison report of all evaluated projects.
        
        Args:
            output_path: Path to save report
        
        Returns:
            Path to saved report
        """
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "total_projects": len(self.results),
            "projects": self.evaluation_data,
            "summary": self._create_summary(),
        }
        
        with open(output_path, "w") as f:
            json.dump(comparison, f, indent=2)
        
        print(f"\n✅ Comparison report saved to: {output_path}")
        return output_path
    
    def _create_summary(self) -> Dict:
        """Create summary statistics across all projects."""
        if not self.evaluation_data:
            return {}
        
        total_modules = sum([p["statistics"]["total_modules"] for p in self.evaluation_data])
        total_cycles = sum([p["statistics"]["cycles_count"] for p in self.evaluation_data])
        total_hotspots = sum([p["statistics"]["large_sccs"] for p in self.evaluation_data])
        
        return {
            "total_modules_all_projects": total_modules,
            "total_cycles_all_projects": total_cycles,
            "total_hotspots_all_projects": total_hotspots,
            "highest_risk_project": max(
                self.evaluation_data,
                key=lambda p: p["statistics"]["cycles_count"] + p["statistics"]["large_sccs"],
                default={}
            ).get("project_name", "N/A"),
        }
    
    def print_comparison(self) -> None:
        """Print comparison of all projects."""
        print("\n" + "="*80)
        print("MULTI-PROJECT COMPARISON")
        print("="*80)
        
        for project in self.evaluation_data:
            print(f"\n{project['project_name']}:")
            print(f"  Modules: {project['statistics']['total_modules']}")
            print(f"  Dependencies: {project['statistics']['total_dependencies']}")
            print(f"  Cycles: {project['statistics']['cycles_count']}")
            print(f"  Hotspots: {project['statistics']['large_sccs']}")
            print(f"  Avg In-Degree: {project['graph_metrics']['avg_in_degree']:.2f}")
            print(f"  Density: {project['graph_metrics']['density']:.4f}")
