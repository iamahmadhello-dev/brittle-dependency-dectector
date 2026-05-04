"""
Tool Comparison Framework
Compares Brent Detector with other dependency analysis tools
"""

import json
from typing import Dict, List
from datetime import datetime


class ToolComparison:
    """Compares Brent Detector with other tools."""
    
    def __init__(self):
        """Initialize comparison framework."""
        self.tools = {
            "brent_detector": {
                "name": "Brent Detector",
                "type": "Brittle Dependency Detector",
                "open_source": True,
                "cost": 0,
                "features": [
                    "Cycle detection",
                    "SCC analysis",
                    "Centrality metrics",
                    "Fragility scoring",
                    "Graph visualization",
                    "HTML/CSV/JSON reporting",
                    "Hotspot detection",
                ],
                "languages": ["Python"],
                "capabilities": {
                    "cycles": True,
                    "metrics": True,
                    "visualization": True,
                    "hotspots": True,
                    "evolution_tracking": False,
                    "refactoring_suggestions": False,
                }
            },
            "codescene": {
                "name": "CodeScene",
                "type": "Architectural Analysis",
                "open_source": False,
                "cost": "Paid (trial available)",
                "features": [
                    "Code hotspot detection",
                    "Architecture visualization",
                    "Temporal coupling analysis",
                    "Risk assessment",
                    "Knowledge loss warnings",
                ],
                "languages": ["Multiple"],
                "capabilities": {
                    "cycles": False,
                    "metrics": True,
                    "visualization": True,
                    "hotspots": True,
                    "evolution_tracking": True,
                    "refactoring_suggestions": True,
                }
            },
            "structure101": {
                "name": "Structure101",
                "type": "Architecture Analyzer",
                "open_source": False,
                "cost": "Paid",
                "features": [
                    "Dependency graph visualization",
                    "Architecture violations",
                    "Design pattern detection",
                    "Code metrics",
                    "Refactoring guidance",
                ],
                "languages": ["Java", "C#", "Python (limited)"],
                "capabilities": {
                    "cycles": True,
                    "metrics": True,
                    "visualization": True,
                    "hotspots": False,
                    "evolution_tracking": False,
                    "refactoring_suggestions": True,
                }
            },
            "jdepend": {
                "name": "JDepend",
                "type": "Dependency Analyzer",
                "open_source": True,
                "cost": 0,
                "features": [
                    "Package metrics",
                    "Dependency analysis",
                    "Cycle detection",
                    "Design metrics",
                ],
                "languages": ["Java"],
                "capabilities": {
                    "cycles": True,
                    "metrics": True,
                    "visualization": False,
                    "hotspots": False,
                    "evolution_tracking": False,
                    "refactoring_suggestions": False,
                }
            },
            "networkx_based": {
                "name": "NetworkX Tools",
                "type": "Graph Analysis Library",
                "open_source": True,
                "cost": 0,
                "features": [
                    "Graph algorithms",
                    "Centrality metrics",
                    "Community detection",
                    "SCC analysis",
                ],
                "languages": ["Python"],
                "capabilities": {
                    "cycles": True,
                    "metrics": True,
                    "visualization": False,
                    "hotspots": True,
                    "evolution_tracking": False,
                    "refactoring_suggestions": False,
                }
            }
        }
        self.comparison_results = []
    
    def compare_brent_with(self, tool_name: str) -> Dict:
        """
        Compare Brent Detector with another tool.
        
        Args:
            tool_name: Name of tool to compare with
        
        Returns:
            Comparison dictionary
        """
        if tool_name not in self.tools:
            return {"error": f"Tool {tool_name} not found"}
        
        brent = self.tools["brent_detector"]
        other = self.tools[tool_name]
        
        comparison = {
            "brent_detector_vs": tool_name,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "brent_better": [],
                "tool_better": [],
                "equivalent": [],
            },
            "detailed_comparison": {}
        }
        
        # Compare capabilities
        brent_caps = brent["capabilities"]
        other_caps = other["capabilities"]
        
        for capability, brent_has in brent_caps.items():
            other_has = other_caps.get(capability, False)
            
            if brent_has and not other_has:
                comparison["summary"]["brent_better"].append(capability)
            elif other_has and not brent_has:
                comparison["summary"]["tool_better"].append(capability)
            elif brent_has and other_has:
                comparison["summary"]["equivalent"].append(capability)
        
        # Detailed comparison
        comparison["detailed_comparison"] = {
            "cost": {
                "brent": brent["cost"],
                "other": other["cost"],
                "advantage": "Brent" if brent["cost"] == 0 else other["name"]
            },
            "language_support": {
                "brent": brent["languages"],
                "other": other["languages"],
            },
            "features": {
                "brent": len(brent["features"]),
                "other": len(other["features"]),
            }
        }
        
        self.comparison_results.append(comparison)
        return comparison
    
    def generate_comparison_matrix(self) -> Dict:
        """Generate capability comparison matrix for all tools."""
        capabilities = [
            "cycles",
            "metrics",
            "visualization",
            "hotspots",
            "evolution_tracking",
            "refactoring_suggestions"
        ]
        
        matrix = {
            "timestamp": datetime.now().isoformat(),
            "capabilities": capabilities,
            "tools": {}
        }
        
        for tool_name, tool_info in self.tools.items():
            matrix["tools"][tool_name] = {
                "name": tool_info["name"],
                "open_source": tool_info["open_source"],
                "cost": tool_info["cost"],
                "capabilities": tool_info["capabilities"]
            }
        
        return matrix
    
    def print_comparison_matrix(self) -> None:
        """Print tool comparison matrix."""
        matrix = self.generate_comparison_matrix()
        
        print("\n" + "="*100)
        print("TOOL COMPARISON MATRIX")
        print("="*100)
        
        # Header
        print("\nTool Comparison:")
        print(f"{'Tool':<20} {'Type':<25} {'Open Source':<15} {'Cost':<20}")
        print("-"*80)
        
        for tool_name, tool_info in matrix["tools"].items():
            tool = self.tools[tool_name]
            print(f"{tool['name']:<20} {tool['type']:<25} {str(tool['open_source']):<15} {tool['cost']:<20}")
        
        # Capabilities
        print("\n" + "="*100)
        print("CAPABILITY COMPARISON")
        print("="*100)
        
        capabilities = matrix["capabilities"]
        tools_list = list(matrix["tools"].keys())
        
        # Print capabilities table
        header = f"{'Capability':<30}"
        for tool_name in tools_list:
            header += f"{'│ ' + self.tools[tool_name]['name']:<18}"
        
        print("\n" + header)
        print("-" * len(header))
        
        for capability in capabilities:
            row = f"{capability:<30}"
            for tool_name in tools_list:
                has_capability = matrix["tools"][tool_name]["capabilities"].get(capability, False)
                symbol = "✅" if has_capability else "❌"
                row += f"│ {symbol:<17}"
            print(row)
    
    def save_comparison_report(self, output_path: str = "tool_comparison.json") -> str:
        """Save comparison report to file."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "comparison_matrix": self.generate_comparison_matrix(),
            "detailed_comparisons": self.comparison_results,
            "recommendation": {
                "for_python_projects": "Brent Detector (open source, focused, free)",
                "for_enterprise": "CodeScene or Structure101 (comprehensive, paid)",
                "for_academia": "Brent Detector + NetworkX (research-friendly)",
            }
        }
        
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Comparison report saved to: {output_path}")
        return output_path
