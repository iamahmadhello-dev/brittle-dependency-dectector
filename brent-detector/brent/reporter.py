import json
import csv
import os
from datetime import datetime


def generate_json_report(project_path, top_brents, metrics, graph):
    """
    Generate a JSON report of Brent analysis results.
    
    Args:
        project_path: Path to the analyzed project
        top_brents: List of top Brents (module, score, data)
        metrics: Dictionary of all metrics for all modules
        graph: NetworkX graph object
    
    Returns:
        Dictionary containing the report
    """
    report = {
        "timestamp": datetime.now().isoformat(),
        "project_path": project_path,
        "summary": {
            "total_modules": graph.number_of_nodes(),
            "total_dependencies": graph.number_of_edges(),
            "top_brents_count": len(top_brents),
        },
        "top_brents": [
            {
                "rank": i,
                "module": module,
                "score": float(score),
                "incoming_dependencies": data["incoming_dependencies"],
                "outgoing_dependencies": data["outgoing_dependencies"],
                "degree_centrality": float(data["degree_centrality"]),
                "betweenness_centrality": float(data["betweenness_centrality"]),
                "closeness_centrality": float(data["closeness_centrality"]),
                "pagerank": float(data["pagerank"]),
                "eigenvector_centrality": float(data["eigenvector_centrality"]),
                "in_cycle": bool(data["in_cycle"]),
                "scc_size": data["scc_size"],
            }
            for i, (module, score, data) in enumerate(top_brents, start=1)
        ],
        "all_modules": [
            {
                "module": module,
                "incoming_dependencies": data["incoming_dependencies"],
                "outgoing_dependencies": data["outgoing_dependencies"],
                "degree_centrality": float(data["degree_centrality"]),
                "betweenness_centrality": float(data["betweenness_centrality"]),
                "closeness_centrality": float(data["closeness_centrality"]),
                "pagerank": float(data["pagerank"]),
                "eigenvector_centrality": float(data["eigenvector_centrality"]),
                "in_cycle": bool(data["in_cycle"]),
                "scc_size": data["scc_size"],
            }
            for module, data in sorted(metrics.items())
        ],
    }
    return report


def save_json_report(report, output_path):
    """Save report as JSON file."""
    with open(output_path, "w") as f:
        json.dump(report, f, indent=2)
    print(f"✅ JSON report saved to: {output_path}")


def generate_csv_report(top_brents, output_path):
    """Generate CSV report of top Brents with all metrics."""
    with open(output_path, "w", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(
            ["Rank", "Module", "Score", "Incoming Dependencies", "Outgoing Dependencies", 
             "Degree Centrality", "Betweenness Centrality", "Closeness Centrality", 
             "PageRank", "Eigenvector Centrality", "In Cycle", "SCC Size"]
        )
        
        for i, (module, score, data) in enumerate(top_brents, start=1):
            writer.writerow(
                [
                    i,
                    module,
                    f"{score:.4f}",
                    data["incoming_dependencies"],
                    data["outgoing_dependencies"],
                    f"{data['degree_centrality']:.6f}",
                    f"{data['betweenness_centrality']:.6f}",
                    f"{data['closeness_centrality']:.6f}",
                    f"{data['pagerank']:.6f}",
                    f"{data['eigenvector_centrality']:.6f}",
                    "Yes" if data['in_cycle'] else "No",
                    data['scc_size'],
                ]
            )
    print(f"✅ CSV report saved to: {output_path}")


def generate_html_report(report, output_path):
    """Generate an interactive HTML report with charts and visualizations for all 9 metrics."""
    
    # Prepare data for charts
    top_brents = report["top_brents"]
    module_names = [b["module"] for b in top_brents]
    scores = [b["score"] for b in top_brents]
    incoming = [b["incoming_dependencies"] for b in top_brents]
    outgoing = [b["outgoing_dependencies"] for b in top_brents]
    degree_centrality = [b.get("degree_centrality", 0) for b in top_brents]
    betweenness_centrality = [b.get("betweenness_centrality", 0) for b in top_brents]
    closeness_centrality = [b.get("closeness_centrality", 0) for b in top_brents]
    pagerank = [b.get("pagerank", 0) for b in top_brents]
    eigenvector_centrality = [b.get("eigenvector_centrality", 0) for b in top_brents]
    in_cycle = [1 if b.get("in_cycle", False) else 0 for b in top_brents]
    scc_size = [b.get("scc_size", 0) for b in top_brents]
    
    # Convert data to JSON for JavaScript
    chart_data = json.dumps({
        "modules": module_names,
        "scores": scores,
        "incoming": incoming,
        "outgoing": outgoing,
        "degree_centrality": degree_centrality,
        "betweenness_centrality": betweenness_centrality,
        "closeness_centrality": closeness_centrality,
        "pagerank": pagerank,
        "eigenvector_centrality": eigenvector_centrality,
        "in_cycle": in_cycle,
        "scc_size": scc_size,
    })
    
    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Brent Detector Analysis Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 40px;
        }}
        
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.5em;
        }}
        
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 0.9em;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        
        .summary-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }}
        
        .summary-card .value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        
        .summary-card .label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        
        h2 {{
            color: #333;
            margin: 40px 0 20px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid #667eea;
        }}
        
        h3 {{
            color: #555;
            margin: 30px 0 15px 0;
            font-size: 1.3em;
            border-left: 4px solid #667eea;
            padding-left: 10px;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin: 30px 0;
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid #eee;
        }}
        
        .chart-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin: 40px 0;
        }}
        
        @media (max-width: 768px) {{
            .chart-row {{
                grid-template-columns: 1fr;
            }}
        }}
        
        .explanation {{
            background: #e3f2fd;
            border-left: 4px solid #2196F3;
            padding: 15px 20px;
            margin: 20px 0;
            border-radius: 4px;
            color: #333;
            line-height: 1.6;
        }}
        
        .explanation strong {{
            color: #1976D2;
        }}
        
        .metric-tooltip {{
            cursor: help;
            position: relative;
            border-bottom: 1px dotted #667eea;
        }}
        
        .table-wrapper {{
            overflow-x: auto;
            margin: 20px 0;
            border-radius: 8px;
            border: 1px solid #ddd;
        }}
        
        table {{
            border-collapse: collapse;
            width: 100%;
            min-width: 900px;
        }}
        
        th, td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
            white-space: nowrap;
        }}
        
        th {{
            background-color: #667eea;
            color: white;
            font-weight: 600;
            position: sticky;
            top: 0;
            z-index: 10;
        }}
        
        tr:nth-child(even) {{
            background-color: #f9f9f9;
        }}
        
        tr:hover {{
            background-color: #f0f0f0;
        }}
        
        @media (max-width: 1024px) {{
            th, td {{
                padding: 10px;
                font-size: 0.95em;
            }}
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}
            
            h1 {{
                font-size: 1.8em;
            }}
            
            .summary {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}
            
            .summary-card .value {{
                font-size: 2em;
            }}
            
            .chart-row {{
                grid-template-columns: 1fr;
                gap: 20px;
            }}
            
            th, td {{
                padding: 8px;
                font-size: 0.9em;
            }}
            
            table {{
                min-width: 600px;
            }}
        }}
        
        @media (max-width: 480px) {{
            .container {{
                padding: 15px;
            }}
            
            h1 {{
                font-size: 1.4em;
            }}
            
            .summary-card .value {{
                font-size: 1.5em;
            }}
            
            th, td {{
                padding: 6px;
                font-size: 0.8em;
            }}
            
            table {{
                min-width: 500px;
            }}
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥 Brent Detector Analysis Report</h1>
        <p class="subtitle">Generated: {report['timestamp']}</p>
        <p class="subtitle">Project: {report['project_path']}</p>
        
        <div class="summary">
            <div class="summary-card">
                <div class="label">Total Modules</div>
                <div class="value">{report['summary']['total_modules']}</div>
            </div>
            <div class="summary-card">
                <div class="label">Total Dependencies</div>
                <div class="value">{report['summary']['total_dependencies']}</div>
            </div>
            <div class="summary-card">
                <div class="label">Critical Modules Found</div>
                <div class="value">{report['summary']['top_brents_count']}</div>
            </div>
        </div>
        
        <h2>📊 What are Brents?</h2>
        <div class="explanation">
            <strong>Brents</strong> are critical modules that many other modules depend on. They represent potential bottlenecks 
            or single points of failure in your codebase. High dependency on a single module means changes to that module 
            could have widespread effects across your system.
        </div>
        
        <h2>📈 All 9 Metrics Explained</h2>
        
        <div class="explanation">
            <strong>1️⃣ Fragility Score (0.0-1.0)</strong><br>
            <em>Range: 0=Low Risk (Green) to 1=High Risk (Red)</em><br>
            Overall brittleness risk score for the module. Formula: 0.35×(Incoming Dependencies) + 0.35×(Cycle Risk) + 0.20×(SCC Risk) + 0.10×(Betweenness Centrality).<br>
            <strong>Why it matters:</strong> Highest scoring modules are most likely to cause system failures when modified.
        </div>
        
        <div class="explanation">
            <strong>2️⃣ Incoming Dependencies (Count: 0-N)</strong><br>
            <em>How many modules depend on THIS module</em><br>
            The number of other modules that import/depend on this module. Higher values indicate this module is more critical.<br>
            <strong>Risk Levels:</strong> 0-2 (Low) | 3-10 (Medium) | 10+ (High - Core Dependency)<br>
            <strong>Why it matters:</strong> High incoming = changes here impact many downstream modules.
        </div>
        
        <div class="explanation">
            <strong>3️⃣ Outgoing Dependencies (Count: 0-N)</strong><br>
            <em>How many modules THIS module depends on</em><br>
            The number of other modules this module relies on. Higher values = tightly coupled to other components.<br>
            <strong>Risk Levels:</strong> 0-2 (Loosely Coupled) | 3-8 (Moderately Coupled) | 8+ (Tightly Coupled)<br>
            <strong>Why it matters:</strong> High outgoing = breaking changes in dependencies could break this module.
        </div>
        
        <div class="explanation">
            <strong>4️⃣ Degree Centrality (0.0-1.0)</strong><br>
            <em>Direct network importance</em><br>
            Measures how well-connected this module is (direct connections / total modules). Shows if it's a "hub" in the architecture.<br>
            <strong>Risk Levels:</strong> 0.0-0.2 (Peripheral) | 0.2-0.5 (Important Node) | 0.5+ (Critical Hub)<br>
            <strong>Why it matters:</strong> Identifies central modules that many others interact with directly.
        </div>
        
        <div class="explanation">
            <strong>5️⃣ Betweenness Centrality (0.0-1.0)</strong><br>
            <em>Bridge importance - shortest path broker</em><br>
            How often this module appears on the shortest dependency paths between other modules. High = module is a "bridge".<br>
            <strong>Risk Levels:</strong> 0.0-0.1 (Not a Bridge) | 0.1-0.3 (Minor Bridge) | 0.3+ (Critical Bridge)<br>
            <strong>Why it matters:</strong> Removing a high-betweenness module would disconnect many module pairs.
        </div>
        
        <div class="explanation">
            <strong>6️⃣ Closeness Centrality (0.0-1.0)</strong><br>
            <em>Network proximity - average distance to other modules</em><br>
            Average shortest path distance from this module to all other modules. High = close to most modules.<br>
            <strong>Risk Levels:</strong> 0.0-0.2 (Isolated/Peripheral) | 0.2-0.5 (Well-Positioned) | 0.5+ (Central Position)<br>
            <strong>Why it matters:</strong> Well-positioned modules have easier access to other parts of the system.
        </div>
        
        <div class="explanation">
            <strong>7️⃣ PageRank (0.0-1.0)</strong><br>
            <em>Network influence - importance propagation</em><br>
            Iterative importance score based on incoming links (like Google PageRank). High = many important modules depend on it.<br>
            <strong>Risk Levels:</strong> 0.0-0.01 (Minor Influence) | 0.01-0.03 (Moderate Influence) | 0.03+ (High Influence)<br>
            <strong>Why it matters:</strong> Shows which modules have highest network influence through dependencies.
        </div>
        
        <div class="explanation">
            <strong>8️⃣ Eigenvector Centrality (0.0-1.0)</strong><br>
            <em>Quality of connections - connected to important modules</em><br>
            Importance based on being connected to OTHER important modules (not just connection count). High = connected to high-quality nodes.<br>
            <strong>Risk Levels:</strong> 0.0-0.2 (Connected to Unimportant) | 0.2-0.5 (Connected to Moderate) | 0.5+ (Connected to Important)<br>
            <strong>Why it matters:</strong> Shows influence through proximity to other influential modules.
        </div>
        
        <div class="explanation">
            <strong>9️⃣ In Cycle / SCC Size</strong><br>
            <em>Circular dependency indicator & coupling region size</em><br>
            <strong>In Cycle:</strong> Yes ⚠️ = Part of circular dependency chain | No ✓ = No circular dependencies<br>
            <strong>SCC Size (Strongly Connected Component):</strong> Size of tightly-coupled region (1=isolated, 2-5=minor coupling, 5+=major hotspot)<br>
            <strong>Why it matters:</strong> Circular dependencies create unmaintainable "knots" - modules can't be changed independently.
        </div>
        
        <h2>⚡ Quick Reference: Metric Risk Levels</h2>
        <div class="table-wrapper">
            <table>
                <thead>
                    <tr style="background-color: #667eea; color: white;">
                        <th>Metric</th>
                        <th style="color: #4CAF50;">✓ Low Risk</th>
                        <th style="color: #FFC107;">⚠️ Medium Risk</th>
                        <th style="color: #F44336;">🔴 High Risk</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td><strong>Fragility Score</strong></td>
                        <td>0.0 - 0.3</td>
                        <td>0.3 - 0.6</td>
                        <td>> 0.6</td>
                    </tr>
                    <tr>
                        <td><strong>Incoming Dependencies</strong></td>
                        <td>0 - 2</td>
                        <td>3 - 10</td>
                        <td>> 10</td>
                    </tr>
                    <tr>
                        <td><strong>Outgoing Dependencies</strong></td>
                        <td>0 - 2</td>
                        <td>3 - 8</td>
                        <td>> 8</td>
                    </tr>
                    <tr>
                        <td><strong>Degree Centrality</strong></td>
                        <td>0.0 - 0.2</td>
                        <td>0.2 - 0.5</td>
                        <td>> 0.5</td>
                    </tr>
                    <tr>
                        <td><strong>Betweenness Centrality</strong></td>
                        <td>0.0 - 0.1</td>
                        <td>0.1 - 0.3</td>
                        <td>> 0.3</td>
                    </tr>
                    <tr>
                        <td><strong>Closeness Centrality</strong></td>
                        <td>< 0.2 (isolated)</td>
                        <td>0.2 - 0.5</td>
                        <td>> 0.5 (central)</td>
                    </tr>
                    <tr>
                        <td><strong>PageRank</strong></td>
                        <td>0.0 - 0.01</td>
                        <td>0.01 - 0.03</td>
                        <td>> 0.03</td>
                    </tr>
                    <tr>
                        <td><strong>Eigenvector Centrality</strong></td>
                        <td>0.0 - 0.2</td>
                        <td>0.2 - 0.5</td>
                        <td>> 0.5</td>
                    </tr>
                    <tr>
                        <td><strong>In Cycle</strong></td>
                        <td>No ✓</td>
                        <td>-</td>
                        <td>Yes ⚠️</td>
                    </tr>
                    <tr>
                        <td><strong>SCC Size</strong></td>
                        <td>1 (isolated)</td>
                        <td>2 - 5</td>
                        <td>> 5 (hotspot)</td>
                    </tr>
                </tbody>
            </table>
        </div>
        
        
        <h3>📊 All 9 Metrics Visualization</h3>
        
        <div class="chart-row">
            <div class="chart-container">
                <canvas id="scoreChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="dependenciesChart"></canvas>
            </div>
        </div>
        
        <div class="chart-row">
            <div class="chart-container">
                <canvas id="centralityChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="betweennessChart"></canvas>
            </div>
        </div>
        
        <div class="chart-row">
            <div class="chart-container">
                <canvas id="closenessChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="pagerankChart"></canvas>
            </div>
        </div>
        
        <div class="chart-row">
            <div class="chart-container">
                <canvas id="eigenvectorChart"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="cycleScCChart"></canvas>
            </div>
        </div>
        
        <div class="table-wrapper">
        <table>
            <tr>
                <th>Rank</th>
                <th>Module</th>
                <th>Score</th>
                <th>Incoming Deps</th>
                <th>Outgoing Deps</th>
                <th>Degree Centrality</th>
                <th>Betweenness</th>
                <th>Closeness</th>
                <th>PageRank</th>
                <th>Eigenvector</th>
                <th>In Cycle</th>
                <th>SCC Size</th>
            </tr>
    """
    
    for brent in top_brents:
        html_content += f"""
            <tr>
                <td><strong>#{brent['rank']}</strong></td>
                <td>{brent['module']}</td>
                <td><strong>{brent['score']:.4f}</strong></td>
                <td>{brent['incoming_dependencies']}</td>
                <td>{brent['outgoing_dependencies']}</td>
                <td>{brent.get('degree_centrality', 0):.6f}</td>
                <td>{brent.get('betweenness_centrality', 0):.6f}</td>
                <td>{brent.get('closeness_centrality', 0):.6f}</td>
                <td>{brent.get('pagerank', 0):.6f}</td>
                <td>{brent.get('eigenvector_centrality', 0):.6f}</td>
                <td>{'✓ Yes' if brent.get('in_cycle', False) else '✗ No'}</td>
                <td>{brent.get('scc_size', 0)}</td>
            </tr>
        """
    
    html_content += f"""
        </table>
        </div>
        
        <div class="footer">
            <p>Generated by Brent Detector - Static dependency analysis tool for Python projects</p>
        </div>
    </div>
    
    <script>
        const chartData = {chart_data};
        
        // Brent Scores Chart
        const scoreCtx = document.getElementById('scoreChart').getContext('2d');
        new Chart(scoreCtx, {{
            type: 'bar',
            data: {{
                labels: chartData.modules,
                datasets: [{{
                    label: 'Brent Score',
                    data: chartData.scores,
                    backgroundColor: [
                        'rgba(102, 126, 234, 0.8)',
                        'rgba(118, 75, 162, 0.8)',
                        'rgba(237, 100, 166, 0.8)',
                        'rgba(255, 154, 158, 0.8)',
                        'rgba(255, 179, 71, 0.8)',
                    ],
                    borderColor: [
                        'rgba(102, 126, 234, 1)',
                        'rgba(118, 75, 162, 1)',
                        'rgba(237, 100, 166, 1)',
                        'rgba(255, 154, 158, 1)',
                        'rgba(255, 179, 71, 1)',
                    ],
                    borderWidth: 2,
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Brent Scores (Higher = More Critical)'
                    }},
                    legend: {{
                        display: true
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Score'
                        }}
                    }},
                    x: {{
                        ticks: {{
                            maxRotation: 45,
                            minRotation: 0
                        }}
                    }}
                }}
            }}
        }});
        
        // Dependencies Comparison Chart
        const depCtx = document.getElementById('dependenciesChart').getContext('2d');
        new Chart(depCtx, {{
            type: 'radar',
            data: {{
                labels: chartData.modules,
                datasets: [
                    {{
                        label: 'Incoming Dependencies',
                        data: chartData.incoming,
                        borderColor: 'rgba(102, 126, 234, 1)',
                        backgroundColor: 'rgba(102, 126, 234, 0.2)',
                        borderWidth: 2
                    }},
                    {{
                        label: 'Outgoing Dependencies',
                        data: chartData.outgoing,
                        borderColor: 'rgba(237, 100, 166, 1)',
                        backgroundColor: 'rgba(237, 100, 166, 0.2)',
                        borderWidth: 2
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Dependency Profile (Incoming vs Outgoing)'
                    }},
                    legend: {{
                        display: true
                    }}
                }},
                scales: {{
                    r: {{
                        beginAtZero: true
                    }}
                }}
            }}
        }});
        
        // Degree Centrality Chart
        const degreeCentralityCtx = document.getElementById('centralityChart').getContext('2d');
        new Chart(degreeCentralityCtx, {{
            type: 'bar',
            data: {{
                labels: chartData.modules,
                datasets: [{{
                    label: 'Degree Centrality',
                    data: chartData.degree_centrality,
                    backgroundColor: 'rgba(75, 192, 192, 0.8)',
                    borderColor: 'rgba(75, 192, 192, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Degree Centrality (Direct Importance)'
                    }}
                }},
                scales: {{
                    y: {{ beginAtZero: true, max: 1 }}
                }}
            }}
        }});
        
        // Betweenness Centrality Chart
        const betweennessCtx = document.getElementById('betweennessChart').getContext('2d');
        new Chart(betweennessCtx, {{
            type: 'bar',
            data: {{
                labels: chartData.modules,
                datasets: [{{
                    label: 'Betweenness Centrality',
                    data: chartData.betweenness_centrality,
                    backgroundColor: 'rgba(54, 162, 235, 0.8)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Betweenness Centrality (Bridge Importance)'
                    }}
                }},
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});
        
        // Closeness Centrality Chart
        const closenessCtx = document.getElementById('closenessChart').getContext('2d');
        new Chart(closenessCtx, {{
            type: 'bar',
            data: {{
                labels: chartData.modules,
                datasets: [{{
                    label: 'Closeness Centrality',
                    data: chartData.closeness_centrality,
                    backgroundColor: 'rgba(255, 206, 86, 0.8)',
                    borderColor: 'rgba(255, 206, 86, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Closeness Centrality (Proximity to Others)'
                    }}
                }},
                scales: {{
                    y: {{ beginAtZero: true, max: 1 }}
                }}
            }}
        }});
        
        // PageRank Chart
        const pagerankCtx = document.getElementById('pagerankChart').getContext('2d');
        new Chart(pagerankCtx, {{
            type: 'bar',
            data: {{
                labels: chartData.modules,
                datasets: [{{
                    label: 'PageRank',
                    data: chartData.pagerank,
                    backgroundColor: 'rgba(153, 102, 255, 0.8)',
                    borderColor: 'rgba(153, 102, 255, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'PageRank Score (Network Influence)'
                    }}
                }},
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});
        
        // Eigenvector Centrality Chart
        const eigenvectorCtx = document.getElementById('eigenvectorChart').getContext('2d');
        new Chart(eigenvectorCtx, {{
            type: 'bar',
            data: {{
                labels: chartData.modules,
                datasets: [{{
                    label: 'Eigenvector Centrality',
                    data: chartData.eigenvector_centrality,
                    backgroundColor: 'rgba(255, 159, 64, 0.8)',
                    borderColor: 'rgba(255, 159, 64, 1)',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Eigenvector Centrality (Connection to Important Nodes)'
                    }}
                }},
                scales: {{
                    y: {{ beginAtZero: true }}
                }}
            }}
        }});
        
        // Cycle and SCC Chart
        const cycleScCCtx = document.getElementById('cycleScCChart').getContext('2d');
        new Chart(cycleScCCtx, {{
            type: 'bubble',
            data: {{
                datasets: chartData.modules.map((module, idx) => ({{
                    label: module,
                    data: [{{
                        x: chartData.scc_size[idx],
                        y: chartData.in_cycle[idx],
                        r: 8 + chartData.scc_size[idx]
                    }}],
                    backgroundColor: chartData.in_cycle[idx] ? 'rgba(255, 99, 132, 0.6)' : 'rgba(75, 192, 192, 0.6)'
                }}))
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Cycle Status vs SCC Size (Red = In Cycle)'
                    }},
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    x: {{
                        title: {{
                            display: true,
                            text: 'SCC Size'
                        }},
                        beginAtZero: true
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'In Cycle (0=No, 1=Yes)'
                        }},
                        min: -0.1,
                        max: 1.1
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
    """
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"✅ HTML report saved to: {output_path}")


def generate_visualization_report(project_path, top_brents, metrics, graph, cycles=None, sccs=None, output_dir="reports"):
    """
    Generate comprehensive HTML report with embedded graph visualizations.
    
    Args:
        project_path: Path to analyzed project
        top_brents: List of top ranked modules
        metrics: Dictionary of all metrics
        graph: NetworkX graph object
        cycles: List of cycles (from CycleDetector)
        sccs: List of SCCs (from SCCAnalyzer)
        output_dir: Directory to save reports
    
    Returns:
        Dictionary with paths to generated files
    """
    try:
        from brent.visualizer import DependencyVisualizer
    except ImportError:
        print("⚠️  Graphviz not available - skipping graph visualizations")
        return {"error": "Graphviz not available"}
    
    os.makedirs(output_dir, exist_ok=True)
    
    visualizer = DependencyVisualizer(graph, metrics)
    
    # Set cycle edges if available
    if cycles:
        cycle_edges = [(cycle[i], cycle[i+1]) for cycle in cycles for i in range(len(cycle)-1)]
        visualizer.set_cycle_edges(cycle_edges)
    
    # Set hotspot modules if available
    if sccs:
        large_sccs = [scc for scc in sccs if len(scc) >= 3]
        hotspot_modules = set()
        for scc in large_sccs:
            hotspot_modules.update(scc)
        visualizer.set_hotspot_modules(hotspot_modules)
    
    results = {}
    
    # Generate main dependency graph
    try:
        graph_path = os.path.join(output_dir, "dependency_graph.svg")
        visualizer.save_svg(graph_path, max_nodes=50)
        results["main_graph"] = graph_path
        print(f"✅ Dependency graph saved to: {graph_path}")
    except Exception as e:
        print(f"⚠️  Could not generate main dependency graph: {e}")
    
    # Generate cycle graph if cycles exist
    if cycles and len(cycles) > 0:
        try:
            cycle_path = os.path.join(output_dir, "cycle_graph.svg")
            visualizer.save_cycle_graph(cycle_path, cycles)
            results["cycle_graph"] = cycle_path
            print(f"✅ Cycle graph saved to: {cycle_path}")
        except Exception as e:
            print(f"⚠️  Could not generate cycle graph: {e}")
    
    # Generate SCC graph if SCCs exist
    if sccs and len(sccs) > 0:
        try:
            scc_path = os.path.join(output_dir, "scc_graph.svg")
            visualizer.save_scc_graph(scc_path, sccs)
            results["scc_graph"] = scc_path
            print(f"✅ SCC graph saved to: {scc_path}")
        except Exception as e:
            print(f"⚠️  Could not generate SCC graph: {e}")
    
    return results


def generate_summary_report(project_path, top_brents, metrics, graph, cycles=None, sccs=None, output_path="brent_summary.txt"):
    """
    Generate text-based summary report of analysis.
    
    Args:
        project_path: Path to analyzed project
        top_brents: List of top ranked modules  
        metrics: Dictionary of metrics
        graph: NetworkX graph object
        cycles: List of cycles
        sccs: List of SCCs
        output_path: Path to save summary
    """
    summary = []
    summary.append("="*80)
    summary.append("BRITTLE DEPENDENCY DETECTOR - ANALYSIS SUMMARY")
    summary.append("="*80)
    summary.append(f"\nProject: {project_path}")
    summary.append(f"Generated: {datetime.now().isoformat()}")
    
    summary.append("\n" + "="*80)
    summary.append("GRAPH STATISTICS")
    summary.append("="*80)
    summary.append(f"Total Modules: {graph.number_of_nodes()}")
    summary.append(f"Total Dependencies: {graph.number_of_edges()}")
    
    if cycles:
        summary.append(f"Circular Dependencies (Cycles): {len(cycles)}")
        if cycles:
            summary.append(f"Longest Cycle Length: {max([len(c) for c in cycles])}")
    
    if sccs:
        large_sccs = [scc for scc in sccs if len(scc) >= 3]
        summary.append(f"Strongly Connected Components: {len(sccs)}")
        summary.append(f"Large SCCs (size >= 3): {len(large_sccs)}")
        if large_sccs:
            max_scc = max(large_sccs, key=len)
            summary.append(f"Largest SCC Size: {len(max_scc)}")
    
    summary.append("\n" + "="*80)
    summary.append(f"TOP {len(top_brents)} BRITTLE DEPENDENCIES")
    summary.append("="*80)
    
    for rank, (module, score, data) in enumerate(top_brents, 1):
        summary.append(f"\n#{rank} {module}")
        summary.append(f"   Fragility Score: {score:.4f}")
        summary.append(f"   Incoming Dependencies: {data.get('incoming_dependencies', 0)}")
        summary.append(f"   Outgoing Dependencies: {data.get('outgoing_dependencies', 0)}")
        summary.append(f"   Degree Centrality: {data.get('degree_centrality', 0):.4f}")
        summary.append(f"   Betweenness Centrality: {data.get('betweenness_centrality', 0):.4f}")
        summary.append(f"   PageRank: {data.get('pagerank', 0):.6f}")
        summary.append(f"   In Cycle: {data.get('in_cycle', False)}")
        summary.append(f"   SCC Size: {data.get('scc_size', 1)}")
    
    summary.append("\n" + "="*80)
    summary.append("RECOMMENDATIONS")
    summary.append("="*80)
    summary.append("\n1. REFACTOR HIGH-DEPENDENCY MODULES")
    summary.append("   - Break down modules with many incoming dependencies")
    summary.append("   - Reduce coupling by extracting interfaces")
    
    summary.append("\n2. RESOLVE CIRCULAR DEPENDENCIES")
    if cycles and len(cycles) > 0:
        summary.append(f"   - Found {len(cycles)} circular dependencies")
        summary.append("   - Break cycles by moving code to new modules")
    else:
        summary.append("   - No cycles detected ✅")
    
    summary.append("\n3. ADDRESS ARCHITECTURAL HOTSPOTS")
    if sccs:
        large_sccs_count = len([s for s in sccs if len(s) >= 3])
        if large_sccs_count > 0:
            summary.append(f"   - Found {large_sccs_count} hotspots (large SCCs)")
            summary.append("   - These regions need architectural refactoring")
        else:
            summary.append("   - No significant hotspots detected ✅")
    
    summary.append("\n" + "="*80 + "\n")
    
    summary_text = "\n".join(summary)
    
    with open(output_path, "w") as f:
        f.write(summary_text)
    
    print(f"✅ Summary report saved to: {output_path}")
    return summary_text


def generate_text_report(top_brents, metrics, output_path):
    """Generate detailed text report with all 9 metrics for each module."""
    
    lines = []
    lines.append("=" * 100)
    lines.append("BRENT DETECTOR - DETAILED ANALYSIS REPORT")
    lines.append("=" * 100)
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    lines.append("METRIC DEFINITIONS:")
    lines.append("-" * 100)
    lines.append("• Fragility Score: Composite risk score (0-1) - Higher = More Fragile")
    lines.append("• Incoming Dependencies: Number of modules that depend on this module")
    lines.append("• Outgoing Dependencies: Number of modules this module depends on")
    lines.append("• Degree Centrality: Direct importance in network (0-1)")
    lines.append("• Betweenness Centrality: Bridge importance - how often module is on path between others (0-1)")
    lines.append("• Closeness Centrality: Proximity to other modules (0-1)")
    lines.append("• PageRank: Network influence score (0-1)")
    lines.append("• Eigenvector Centrality: Connection importance - connected to important nodes (0-1)")
    lines.append("• In Cycle: Whether module is part of circular dependency")
    lines.append("• SCC Size: Size of tightly-coupled region (1=isolated)")
    
    lines.append("\n" + "=" * 100)
    lines.append("TOP BRITTLE MODULES (RANKED)")
    lines.append("=" * 100 + "\n")
    
    for i, (module, score, data) in enumerate(top_brents, 1):
        lines.append(f"#{i}. {module}")
        lines.append("-" * 100)
        lines.append(f"  Fragility Score              : {score:.4f}")
        lines.append(f"  Incoming Dependencies       : {data['incoming_dependencies']}")
        lines.append(f"  Outgoing Dependencies       : {data['outgoing_dependencies']}")
        lines.append(f"  Degree Centrality           : {data['degree_centrality']:.6f}")
        lines.append(f"  Betweenness Centrality      : {data['betweenness_centrality']:.6f}")
        lines.append(f"  Closeness Centrality        : {data['closeness_centrality']:.6f}")
        lines.append(f"  PageRank                    : {data['pagerank']:.6f}")
        lines.append(f"  Eigenvector Centrality      : {data['eigenvector_centrality']:.6f}")
        lines.append(f"  In Cycle                    : {'YES ⚠️ (Part of circular dependency)' if data['in_cycle'] else 'NO ✓ (Not in cycle)'}")
        lines.append(f"  SCC Size                    : {data['scc_size']} (Coupling region size)")
        lines.append("")
    
    lines.append("=" * 100)
    lines.append("SUMMARY STATISTICS")
    lines.append("=" * 100)
    lines.append(f"Total Modules Analyzed      : {len(metrics)}")
    lines.append(f"Top Brents Listed           : {len(top_brents)}")
    lines.append(f"Modules in Cycles           : {sum(1 for m in metrics.values() if m['in_cycle'])}")
    lines.append(f"Average SCC Size            : {sum(m['scc_size'] for m in metrics.values()) / len(metrics):.2f}")
    lines.append(f"Max Incoming Dependencies   : {max(m['incoming_dependencies'] for m in metrics.values())}")
    lines.append(f"Average Incoming Deps       : {sum(m['incoming_dependencies'] for m in metrics.values()) / len(metrics):.2f}")
    lines.append("")
    lines.append("=" * 100)
    
    text_content = "\n".join(lines)
    
    with open(output_path, "w") as f:
        f.write(text_content)
    
    print(f"✅ Text report saved to: {output_path}")
    return text_content


def generate_svg_report(project_path, top_brents, metrics, graph, output_path):
    """Generate SVG visualization report of dependency graph."""
    
    try:
        from brent.visualizer import DependencyVisualizer
    except ImportError:
        print("⚠️  Graphviz/visualizer not available - skipping SVG generation")
        return False
    
    try:
        visualizer = DependencyVisualizer(graph, metrics)
        visualizer.save_svg(output_path, max_nodes=50)
        print(f"✅ SVG report saved to: {output_path}")
        return True
    except Exception as e:
        print(f"⚠️  Could not generate SVG: {e}")
        return False


def generate_text_report(top_brents, metrics, output_path):
    """Generate detailed text report with all 9 metrics for each module."""
    
    lines = []
    lines.append("=" * 100)
    lines.append("BRENT DETECTOR - DETAILED ANALYSIS REPORT")
    lines.append("=" * 100)
    lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    lines.append("METRIC DEFINITIONS:")
    lines.append("-" * 100)
    lines.append("• Fragility Score: Composite risk score (0-1) - Higher = More Fragile")
    lines.append("• Incoming Dependencies: Number of modules that depend on this module")
    lines.append("• Outgoing Dependencies: Number of modules this module depends on")
    lines.append("• Degree Centrality: Direct importance in network (0-1)")
    lines.append("• Betweenness Centrality: Bridge importance - how often module is on path between others (0-1)")
    lines.append("• Closeness Centrality: Proximity to other modules (0-1)")
    lines.append("• PageRank: Network influence score (0-1)")
    lines.append("• Eigenvector Centrality: Connection importance - connected to important nodes (0-1)")
    lines.append("• In Cycle: Whether module is part of circular dependency")
    lines.append("• SCC Size: Size of tightly-coupled region (1=isolated)")
    
    lines.append("\n" + "=" * 100)
    lines.append("TOP BRITTLE MODULES (RANKED)")
    lines.append("=" * 100 + "\n")
    
    for i, (module, score, data) in enumerate(top_brents, 1):
        lines.append(f"#{i}. {module}")
        lines.append("-" * 100)
        lines.append(f"  Fragility Score              : {score:.4f}")
        lines.append(f"  Incoming Dependencies       : {data['incoming_dependencies']}")
        lines.append(f"  Outgoing Dependencies       : {data['outgoing_dependencies']}")
        lines.append(f"  Degree Centrality           : {data['degree_centrality']:.6f}")
        lines.append(f"  Betweenness Centrality      : {data['betweenness_centrality']:.6f}")
        lines.append(f"  Closeness Centrality        : {data['closeness_centrality']:.6f}")
        lines.append(f"  PageRank                    : {data['pagerank']:.6f}")
        lines.append(f"  Eigenvector Centrality      : {data['eigenvector_centrality']:.6f}")
        lines.append(f"  In Cycle                    : {'YES ⚠️ (Part of circular dependency)' if data['in_cycle'] else 'NO ✓ (Not in cycle)'}")
        lines.append(f"  SCC Size                    : {data['scc_size']} (Coupling region size)")
        lines.append("")
    
    lines.append("=" * 100)
    lines.append("SUMMARY STATISTICS")
    lines.append("=" * 100)
    lines.append(f"Total Modules Analyzed      : {len(metrics)}")
    lines.append(f"Top Brents Listed           : {len(top_brents)}")
    lines.append(f"Modules in Cycles           : {sum(1 for m in metrics.values() if m['in_cycle'])}")
    lines.append(f"Average SCC Size            : {sum(m['scc_size'] for m in metrics.values()) / len(metrics):.2f}")
    lines.append(f"Max Incoming Dependencies   : {max(m['incoming_dependencies'] for m in metrics.values())}")
    lines.append(f"Average Incoming Deps       : {sum(m['incoming_dependencies'] for m in metrics.values()) / len(metrics):.2f}")
    lines.append("")
    lines.append("=" * 100)
    
    text_content = "\n".join(lines)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text_content)
    
    print(f"✅ Text report saved to: {output_path}")
    return text_content
