"""
Empirical evaluation script for Brent Detector.
Tests the tool on multiple open-source projects and generates evaluation metrics.
"""

import os
import sys
import json
import time
import csv
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from brent.scanner import get_python_files
from brent.parser import extract_imports
from brent.graph_builder import build_dependency_graph
from brent.metrics import calculate_metrics
from brent.brent_ranker import rank_brents


class EmpiricalEvaluator:
    """
    Empirical evaluation framework for testing Brent Detector on multiple projects.
    """

    def __init__(self, output_dir="evaluation_results"):
        """Initialize evaluator."""
        self.output_dir = output_dir
        self.results = []
        os.makedirs(output_dir, exist_ok=True)

    def evaluate_project(self, project_path, project_name):
        """
        Evaluate a single project.
        
        Args:
            project_path: Path to the project directory
            project_name: Name of the project
        
        Returns:
            Dictionary with evaluation metrics
        """
        print(f"\n{'='*50}")
        print(f"Evaluating: {project_name}")
        print(f"Path: {project_path}")
        print(f"{'='*50}")

        if not os.path.isdir(project_path):
            print(f"❌ Error: Path does not exist: {project_path}")
            return None

        try:
            # Step 1: Scan files
            print("\n[1/5] Scanning Python files...")
            start_time = time.time()
            files = get_python_files(project_path)
            scan_time = time.time() - start_time
            print(f"✅ Found {len(files)} Python files in {scan_time:.2f}s")

            if not files:
                print("⚠️  No Python files found")
                return None

            # Step 2: Build graph
            print("\n[2/5] Building dependency graph...")
            start_time = time.time()
            graph = build_dependency_graph(files, extract_imports, project_path)
            graph_time = time.time() - start_time
            print(f"✅ Built graph with {graph.number_of_nodes()} nodes and "
                  f"{graph.number_of_edges()} edges in {graph_time:.2f}s")

            if graph.number_of_nodes() == 0:
                print("⚠️  Empty graph - no modules found")
                return None

            # Step 3: Calculate metrics
            print("\n[3/5] Calculating metrics...")
            start_time = time.time()
            metrics = calculate_metrics(graph)
            metrics_time = time.time() - start_time
            print(f"✅ Calculated metrics for {len(metrics)} modules in {metrics_time:.2f}s")

            # Step 4: Rank Brents
            print("\n[4/5] Ranking Brents...")
            start_time = time.time()
            top_brents = rank_brents(metrics, top_percentage=0.05)
            rank_time = time.time() - start_time
            print(f"✅ Identified {len(top_brents)} Brents in {rank_time:.2f}s")

            # Step 5: Calculate statistics
            print("\n[5/5] Computing statistics...")
            total_time = scan_time + graph_time + metrics_time + rank_time

            # Compute additional statistics
            in_degrees = [metrics[m]["in_degree"] for m in metrics]
            out_degrees = [metrics[m]["out_degree"] for m in metrics]
            centralities = [metrics[m]["centrality"] for m in metrics]

            stats = {
                "project_name": project_name,
                "project_path": project_path,
                "num_files": len(files),
                "num_modules": graph.number_of_nodes(),
                "num_dependencies": graph.number_of_edges(),
                "num_brents": len(top_brents),
                "avg_in_degree": sum(in_degrees) / len(in_degrees) if in_degrees else 0,
                "avg_out_degree": sum(out_degrees) / len(out_degrees) if out_degrees else 0,
                "avg_centrality": sum(centralities) / len(centralities) if centralities else 0,
                "max_in_degree": max(in_degrees) if in_degrees else 0,
                "max_out_degree": max(out_degrees) if out_degrees else 0,
                "scan_time_s": scan_time,
                "graph_time_s": graph_time,
                "metrics_time_s": metrics_time,
                "rank_time_s": rank_time,
                "total_time_s": total_time,
                "top_brents": [
                    {
                        "module": m,
                        "score": float(s),
                        "in_degree": d["in_degree"],
                    }
                    for m, s, d in top_brents[:5]
                ],
            }

            print("\n📊 Project Statistics:")
            print(f"   Files           : {stats['num_files']}")
            print(f"   Modules         : {stats['num_modules']}")
            print(f"   Dependencies    : {stats['num_dependencies']}")
            print(f"   Brents Found    : {stats['num_brents']}")
            print(f"   Avg In-Degree   : {stats['avg_in_degree']:.2f}")
            print(f"   Max In-Degree   : {stats['max_in_degree']}")
            print(f"   Processing Time : {stats['total_time_s']:.3f}s")

            self.results.append(stats)
            return stats

        except Exception as e:
            print(f"❌ Error evaluating project: {e}")
            import traceback
            traceback.print_exc()
            return None

    def save_evaluation_report(self):
        """Save evaluation report to JSON and CSV."""
        if not self.results:
            print("No evaluation results to save")
            return

        # Save JSON report
        json_path = os.path.join(self.output_dir, "evaluation_report.json")
        with open(json_path, "w") as f:
            json.dump({"evaluations": self.results}, f, indent=2)
        print(f"\n✅ JSON report saved: {json_path}")

        # Save CSV summary
        csv_path = os.path.join(self.output_dir, "evaluation_summary.csv")
        with open(csv_path, "w", newline="") as f:
            if self.results:
                fieldnames = [
                    "project_name",
                    "num_files",
                    "num_modules",
                    "num_dependencies",
                    "num_brents",
                    "avg_in_degree",
                    "avg_out_degree",
                    "avg_centrality",
                    "total_time_s",
                ]
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for result in self.results:
                    writer.writerow({k: result.get(k, "") for k in fieldnames})
        print(f"✅ CSV summary saved: {csv_path}")

    def print_summary(self):
        """Print summary statistics."""
        if not self.results:
            print("No results to summarize")
            return

        print("\n" + "="*60)
        print("EMPIRICAL EVALUATION SUMMARY")
        print("="*60)

        total_files = sum(r["num_files"] for r in self.results)
        total_modules = sum(r["num_modules"] for r in self.results)
        total_deps = sum(r["num_dependencies"] for r in self.results)
        total_brents = sum(r["num_brents"] for r in self.results)
        total_time = sum(r["total_time_s"] for r in self.results)

        print(f"\nProjects Evaluated      : {len(self.results)}")
        print(f"Total Python Files      : {total_files}")
        print(f"Total Modules           : {total_modules}")
        print(f"Total Dependencies      : {total_deps}")
        print(f"Total Brents Identified : {total_brents}")
        print(f"Total Processing Time   : {total_time:.3f}s")
        print(f"Average Time per Project: {total_time/len(self.results):.3f}s")

        print("\nPer-project Summary:")
        print("-" * 60)
        for result in self.results:
            print(f"{result['project_name']:<30} | "
                  f"Modules: {result['num_modules']:<4} | "
                  f"Brents: {result['num_brents']:<3} | "
                  f"Time: {result['total_time_s']:.3f}s")


def main():
    """Main evaluation script."""
    if len(sys.argv) < 2:
        print("Usage: python evaluation.py <project_path> [project_name]")
        print("   or: python evaluation.py --demo [flask|docs|tests]")
        print("   or: python evaluation.py --list-demos")
        print("\nOptions:")
        print("  --demo [option]  Run evaluation on included demo project")
        print("  --list-demos     List available demo projects")
        print("\nDemo Options:")
        print("  flask            Flask framework (default)")
        print("  docs             Flask documentation project")
        print("  tests            Flask test suite")
        return

    evaluator = EmpiricalEvaluator()

    if sys.argv[1] == "--list-demos":
        print("\n📚 Available Demo Projects:")
        print("-" * 50)
        
        base_path = os.path.join(os.path.dirname(__file__), "..", "data", "flask")
        
        demos = {
            "flask": os.path.join(base_path, "src", "flask"),
            "tests": os.path.join(base_path, "tests"),
            "docs": os.path.join(base_path, "docs"),
        }
        
        for name, path in demos.items():
            exists = "✅" if os.path.isdir(path) else "❌"
            print(f"{exists} {name:<15} → {path}")
        
        return

    if sys.argv[1] == "--demo":
        # Use the included demo projects
        base_path = os.path.join(os.path.dirname(__file__), "..", "data", "flask")
        
        demo_name = sys.argv[2] if len(sys.argv) > 2 else "flask"
        
        demos = {
            "flask": ("Flask Framework", os.path.join(base_path, "src", "flask")),
            "tests": ("Flask Test Suite", os.path.join(base_path, "tests")),
            "docs": ("Flask Documentation", os.path.join(base_path, "docs")),
        }
        
        if demo_name not in demos:
            print(f"❌ Unknown demo: {demo_name}")
            print(f"Available: {', '.join(demos.keys())}")
            return
        
        project_name, project_path = demos[demo_name]
        
        if os.path.isdir(project_path):
            evaluator.evaluate_project(project_path, project_name)
        else:
            print(f"❌ Demo project not found at {project_path}")
            return
    else:
        project_path = sys.argv[1]
        project_name = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(project_path)
        evaluator.evaluate_project(project_path, project_name)

    evaluator.save_evaluation_report()
    evaluator.print_summary()


if __name__ == "__main__":
    main()
