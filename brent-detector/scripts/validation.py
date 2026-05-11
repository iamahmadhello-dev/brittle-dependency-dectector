"""
Validation Framework
Validates analysis results against real-world data (GitHub issues, commits, etc.)
"""

import json
import subprocess
from typing import Dict, List, Tuple
from datetime import datetime


class ValidationFramework:
    """Validates brittle dependency detection against real-world data."""
    
    def __init__(self, project_path: str):
        """
        Initialize validation framework.
        
        Args:
            project_path: Path to project directory (with git history)
        """
        self.project_path = project_path
        self.git_data = {}
        self.validation_results = {}
    
    def extract_commit_history(self, max_commits: int = 100) -> Dict[str, int]:
        """
        Extract commit history from git.
        
        Args:
            max_commits: Maximum number of recent commits to analyze
        
        Returns:
            Dictionary mapping file/module to commit count
        """
        try:
            # Get recent commits
            result = subprocess.run(
                ["git", "log", "--pretty=format:%H", f"-{max_commits}"],
                cwd=self.project_path,
                capture_output=True,
                text=True
            )
            
            if result.returncode != 0:
                print("⚠️  Git not available or not a git repository")
                return {}
            
            commits = result.stdout.strip().split("\n")
            
            # Count file changes per commit
            file_changes = {}
            for commit in commits[:max_commits]:
                result = subprocess.run(
                    ["git", "show", "--name-only", "--pretty=", commit],
                    cwd=self.project_path,
                    capture_output=True,
                    text=True
                )
                
                for file_path in result.stdout.strip().split("\n"):
                    if file_path.endswith(".py"):
                        file_changes[file_path] = file_changes.get(file_path, 0) + 1
            
            # Aggregate to module level
            module_changes = {}
            for file_path, count in file_changes.items():
                module = file_path.replace("/", ".").replace(".py", "").replace(".__init__", "")
                module_changes[module] = module_changes.get(module, 0) + count
            
            self.git_data["file_changes"] = file_changes
            self.git_data["module_changes"] = module_changes
            
            return module_changes
            
        except Exception as e:
            print(f"⚠️  Error extracting commit history: {e}")
            return {}
    
    def validate_against_changes(self, brittle_modules: List[str], change_frequency: Dict[str, int]) -> Dict:
        """
        Validate that detected brittle modules have high change frequency.
        
        RQ1 Validation: "Do modules with high in-degree show higher change frequency?"
        
        Args:
            brittle_modules: List of detected brittle modules
            change_frequency: Dictionary of module -> change count
        
        Returns:
            Validation results with correlation analysis
        """
        if not change_frequency:
            return {"status": "skipped", "reason": "No git data available"}
        
        brittle_changes = []
        non_brittle_changes = []
        
        for module, changes in change_frequency.items():
            if module in brittle_modules:
                brittle_changes.append(changes)
            else:
                non_brittle_changes.append(changes)
        
        result = {
            "validation_type": "RQ1 - Metrics predict fragility",
            "brittle_avg_changes": sum(brittle_changes) / len(brittle_changes) if brittle_changes else 0,
            "non_brittle_avg_changes": sum(non_brittle_changes) / len(non_brittle_changes) if non_brittle_changes else 0,
            "modules_tested": len(brittle_modules) + len(non_brittle_changes),
            "evidence_supports_hypothesis": False,
        }
        
        # Check if brittle modules have MORE changes (supports hypothesis)
        if result["brittle_avg_changes"] > result["non_brittle_avg_changes"]:
            result["evidence_supports_hypothesis"] = True
            ratio = result["brittle_avg_changes"] / result["non_brittle_avg_changes"]
            result["change_ratio"] = ratio
            result["interpretation"] = f"Brittle modules changed {ratio:.2f}x more often ✅"
        else:
            result["interpretation"] = "Brittle modules did NOT show higher change frequency ❌"
        
        self.validation_results["rq1_validation"] = result
        return result
    
    def validate_against_test_coverage(self, brittle_modules: List[str]) -> Dict:
        """
        Validate that brittle modules have adequate test coverage.
        
        Args:
            brittle_modules: List of detected brittle modules
        
        Returns:
            Validation results for test coverage
        """
        # This would require coverage data - simplified version
        result = {
            "validation_type": "RQ2 - Hotspot identification",
            "description": "Brittle modules should have higher test coverage to mitigate risk",
            "recommendation": "Run coverage analysis on detected brittle modules",
            "modules_to_test": brittle_modules[:5],  # Show first 5
        }
        
        self.validation_results["test_coverage"] = result
        return result
    
    def generate_validation_report(self, output_path: str = "validation_report.json") -> str:
        """
        Generate comprehensive validation report.
        
        Args:
            output_path: Path to save report
        
        Returns:
            Path to saved report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "project_path": self.project_path,
            "validation_results": self.validation_results,
            "methodology": {
                "rq1": "Test correlation between detected metrics and actual code changes",
                "rq2": "Test correlation between hotspot detection and known issues",
                "rq3": "Track metric evolution over time versions",
            },
            "recommendations": self._generate_recommendations(),
        }
        
        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)
        
        print(f"\n✅ Validation report saved to: {output_path}")
        return output_path
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        rq1_result = self.validation_results.get("rq1_validation", {})
        if rq1_result.get("evidence_supports_hypothesis"):
            recommendations.append("✅ RQ1 hypothesis supported - metrics successfully predict fragility")
        else:
            recommendations.append("❌ RQ1 hypothesis not fully supported - refine metrics")
        
        recommendations.append("Continue monitoring metrics evolution over time for RQ3")
        recommendations.append("Cross-validate hotspot detection with domain experts")
        
        return recommendations
    
    def print_validation_summary(self) -> None:
        """Print validation summary."""
        print("\n" + "="*80)
        print("VALIDATION SUMMARY")
        print("="*80)
        
        for validation_name, result in self.validation_results.items():
            print(f"\n{validation_name}:")
            for key, value in result.items():
                if key not in ["validation_type"]:
                    print(f"  {key}: {value}")
