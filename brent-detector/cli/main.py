import sys
import os
import logging

from brent.scanner import get_python_files
from brent.parser import extract_imports
from brent.graph_builder import build_dependency_graph
from brent.metrics import calculate_metrics
from brent.cycle_detector import CycleDetector
from brent.scc_analyzer import SCCAnalyzer
from brent.brent_ranker import rank_brents
from brent.visualizer import DependencyVisualizer
from brent.reporter import (
    generate_json_report,
    save_json_report,
    generate_csv_report,
    generate_html_report,
    generate_text_report,
    generate_svg_report,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m cli.main <project_path> [options]")
        print("\nOptions:")
        print("  --output-dir DIR     Output directory for reports (default: ./reports)")
        print("  --json               Generate JSON report")
        print("  --csv                Generate CSV report")
        print("  --html               Generate HTML report")
        print("  --txt                Generate detailed text report")
        print("  --svg                Generate SVG dependency graph")
        print("  --all                Generate all report formats (JSON, CSV, HTML, TXT, SVG)")
        print("  --top-percent PCT    Top percentage of Brents to show (default: 0.05)")
        return

    project_path = sys.argv[1]
    
    # Parse command-line options
    output_dir = "./reports"
    output_formats = []
    top_percent = 0.05
    
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == "--output-dir" and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == "--json":
            output_formats.append("json")
            i += 1
        elif sys.argv[i] == "--csv":
            output_formats.append("csv")
            i += 1
        elif sys.argv[i] == "--html":
            output_formats.append("html")
            i += 1
        elif sys.argv[i] == "--txt":
            output_formats.append("txt")
            i += 1
        elif sys.argv[i] == "--svg":
            output_formats.append("svg")
            i += 1
        elif sys.argv[i] == "--all":
            output_formats = ["json", "csv", "html", "txt", "svg"]
            i += 1
        elif sys.argv[i] == "--top-percent" and i + 1 < len(sys.argv):
            top_percent = float(sys.argv[i + 1])
            i += 2
        else:
            i += 1

    # Validate project path
    if not os.path.isdir(project_path):
        print(f"❌ Error: Project path '{project_path}' does not exist or is not a directory")
        return

    try:
        print("=================================")
        print("        Brent Detector")
        print("=================================")

        # Step 1: Scan files
        print("\n🔍 Scanning Python files...")
        files = get_python_files(project_path)
        
        if not files:
            print("⚠️  No Python files found in the project")
            return
            
        print(f"✅ Found {len(files)} Python files")

        # Step 2: Build graph
        print("\n📦 Extracting dependencies & building graph...")
        graph = build_dependency_graph(files, extract_imports, project_path)

        print("\n📊 Graph Statistics:")
        print(f"   Nodes (Modules)      : {graph.number_of_nodes()}")
        print(f"   Edges (Dependencies) : {graph.number_of_edges()}")

        if graph.number_of_nodes() == 0:
            print("⚠️  No modules found in dependency graph")
            return

        # Step 3: Calculate metrics
        print("\n⚙️  Calculating graph metrics...")
        metrics = calculate_metrics(graph)

        # Step 4: Detect cycles (Week 1-2)
        print("\n🔄 Detecting circular dependencies...")
        cycle_detector = CycleDetector(graph)
        cycles = cycle_detector.find_all_cycles()
        cycle_edges = cycle_detector.get_cycle_edges()
        modules_in_cycles = cycle_detector.get_modules_in_cycles()
        print(f"   ✓ Found {len(cycles)} cycles")
        print(f"   ✓ {len(modules_in_cycles)} modules involved in cycles")
        print(f"   ✓ {len(cycle_edges)} cycle edges")

        # Step 5: Analyze SCCs/Hotspots (Week 1-2)
        print("\n🌀 Analyzing Strongly Connected Components (hotspots)...")
        scc_analyzer = SCCAnalyzer(graph)
        sccs = scc_analyzer.find_sccs()
        large_sccs = scc_analyzer.get_large_sccs(min_size=2)
        print(f"   ✓ Found {len(sccs)} total SCCs")
        print(f"   ✓ {len(large_sccs)} large SCCs (≥2 modules)")
        if large_sccs:
            largest_scc = max(large_sccs, key=len)
            print(f"   ✓ Largest SCC: {len(largest_scc)} modules")

        # Step 6: Rank Brents
        print("\n🏆 Ranking Brents (Fragility Index calculation)...")
        top_brents = rank_brents(metrics, top_percentage=top_percent)

        # Step 7: Display results
        print("\n🔥 Top Brents:\n")

        for i, (module, score, data) in enumerate(top_brents, start=1):
            print(f"{i}. {module}")
            print(f"   ├─ Fragility Score               : {score:.4f}")
            print(f"   ├─ Incoming Dependencies         : {data['incoming_dependencies']}")
            print(f"   ├─ Outgoing Dependencies         : {data['outgoing_dependencies']}")
            print(f"   ├─ Degree Centrality             : {data['degree_centrality']:.6f}")
            print(f"   ├─ Betweenness Centrality        : {data['betweenness_centrality']:.6f}")
            print(f"   ├─ Closeness Centrality          : {data['closeness_centrality']:.6f}")
            print(f"   ├─ PageRank                      : {data['pagerank']:.6f}")
            print(f"   ├─ Eigenvector Centrality        : {data['eigenvector_centrality']:.6f}")
            print(f"   ├─ In Cycle                      : {'Yes ⚠️' if data['in_cycle'] else 'No ✓'}")
            print(f"   └─ SCC Size (Coupling Region)    : {data['scc_size']}")
            print("-" * 60)

        # Step 8: Generate reports (Week 2-3)
        if output_formats:
            os.makedirs(output_dir, exist_ok=True)
            print(f"\n📄 Generating reports in '{output_dir}'...")
            
            report = generate_json_report(project_path, top_brents, metrics, graph)
            
            if "json" in output_formats:
                json_path = os.path.join(output_dir, "brent_analysis.json")
                save_json_report(report, json_path)
            
            if "csv" in output_formats:
                csv_path = os.path.join(output_dir, "brent_analysis.csv")
                generate_csv_report(top_brents, csv_path)
            
            if "html" in output_formats:
                html_path = os.path.join(output_dir, "brent_analysis.html")
                generate_html_report(report, html_path)
            
            if "txt" in output_formats or "text" in output_formats:
                txt_path = os.path.join(output_dir, "brent_analysis.txt")
                generate_text_report(top_brents, metrics, txt_path)
            
            if "svg" in output_formats:
                svg_path = os.path.join(output_dir, "dependency_graph.svg")
                generate_svg_report(project_path, top_brents, metrics, graph, svg_path)

        # Step 9: Generate SVG visualizations (Week 2-3)
        # Always generate SVG visualizations for visual analysis
        os.makedirs(output_dir, exist_ok=True)
        print(f"\n🎨 Generating SVG visualizations...")
        
        try:
            visualizer = DependencyVisualizer(graph, metrics)
            visualizer.set_cycle_edges(cycle_edges)
            visualizer.set_hotspot_modules(set(m for scc in large_sccs for m in scc))
            
            # Visualization 1: Main dependency graph
            try:
                main_svg = os.path.join(output_dir, "01_main_dependency_graph.svg")
                visualizer.save_svg(main_svg, max_nodes=50)
                print(f"   ✅ Main dependency graph: 01_main_dependency_graph.svg")
            except Exception as e:
                print(f"   ⚠️  Main dependency graph failed: {e}")
            
            # Visualization 2: Cycle graph (focused)
            if cycles:
                try:
                    cycle_svg = os.path.join(output_dir, "02_cycle_graph.svg")
                    visualizer.save_cycle_graph(cycle_svg, cycles, max_cycles=100)
                    print(f"   ✅ Cycle graph: 02_cycle_graph.svg ({len(cycles)} cycles found)")
                except Exception as e:
                    print(f"   ⚠️  Cycle graph failed: {e}")
            
            # Visualization 3: SCC/Hotspot graph
            if large_sccs:
                try:
                    scc_svg = os.path.join(output_dir, "03_scc_hotspot_graph.svg")
                    visualizer.save_scc_graph(scc_svg, sccs)
                    print(f"   ✅ SCC hotspot graph: 03_scc_hotspot_graph.svg")
                except Exception as e:
                    print(f"   ⚠️  SCC graph failed: {e}")
        except Exception as e:
            print(f"   ⚠️  SVG visualization failed: {e}")

        print("\n✅ Analysis Complete.\n")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return


if __name__ == "__main__":
    main()