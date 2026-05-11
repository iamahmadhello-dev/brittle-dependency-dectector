"""
Metrics Tracker
Tracks brittle dependency metrics over time
"""

import json
import os
from datetime import datetime
from typing import Dict, List
import subprocess


class MetricsTracker:
    """Tracks dependency metrics across time/versions."""
    
    def __init__(self, metrics_file: str = "brent_metrics_history.json"):
        """
        Initialize tracker.
        
        Args:
            metrics_file: Path to metrics history file
        """
        self.metrics_file = metrics_file
        self.history = self._load_history()
    
    def _load_history(self) -> List[Dict]:
        """Load existing metrics history."""
        if os.path.exists(self.metrics_file):
            try:
                with open(self.metrics_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Could not load metrics history: {e}")
                return []
        return []
    
    def record_metrics(self, metrics_data: Dict, git_hash: str = None) -> None:
        """
        Record new metrics snapshot.
        
        Args:
            metrics_data: Current metrics from analysis
            git_hash: Git commit hash (auto-detected if not provided)
        """
        if git_hash is None:
            git_hash = self._get_git_commit()
        
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "git_commit": git_hash,
            "metrics": metrics_data,
        }
        
        self.history.append(snapshot)
        self._save_history()
    
    def _get_git_commit(self) -> str:
        """Get current git commit hash."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()[:7]  # Short hash
        except:
            return "unknown"
    
    def analyze_trends(self) -> Dict:
        """
        Analyze metric trends over time.
        
        Returns:
            Dictionary with trend analysis
        """
        if len(self.history) < 2:
            return {"status": "insufficient_data", "required": 2, "available": len(self.history)}
        
        trends = {
            "total_snapshots": len(self.history),
            "timespan": {
                "first": self.history[0]["timestamp"],
                "last": self.history[-1]["timestamp"],
            },
            "metric_changes": {},
            "alerts": [],
        }
        
        # Compare first and last
        first_metrics = self.history[0].get("metrics", {})
        last_metrics = self.history[-1].get("metrics", {})
        
        # Track key metrics
        key_metrics = ["total_modules", "total_dependencies", "cycles_count", "large_sccs"]
        
        for metric in key_metrics:
            first_value = first_metrics.get(metric, 0)
            last_value = last_metrics.get(metric, 0)
            
            if first_value > 0:
                change_percent = ((last_value - first_value) / first_value) * 100
            else:
                change_percent = 0 if last_value == 0 else 100
            
            trends["metric_changes"][metric] = {
                "first": first_value,
                "last": last_value,
                "change_percent": change_percent,
                "trend": "📈 increasing" if change_percent > 5 else "📉 decreasing" if change_percent < -5 else "→ stable"
            }
            
            # Generate alerts
            if metric in ["cycles_count", "large_sccs"] and change_percent > 10:
                trends["alerts"].append(
                    f"⚠️  {metric} increased by {change_percent:.1f}% - architectural fragility growing!"
                )
        
        return trends
    
    def predict_refactoring_need(self) -> Dict:
        """
        Predict if system needs refactoring based on trend.
        
        Returns:
            Prediction with confidence level
        """
        analysis = self.analyze_trends()
        
        if "metric_changes" not in analysis:
            return {"prediction": "unknown", "reason": "insufficient_data"}
        
        fragility_score = 0
        factors = []
        
        # Check cycle trend
        cycles_change = analysis["metric_changes"].get("cycles_count", {}).get("change_percent", 0)
        if cycles_change > 20:
            fragility_score += 2
            factors.append("Rapid cycle increase")
        elif cycles_change > 0:
            fragility_score += 1
            factors.append("Growing cycles")
        
        # Check hotspot trend
        hotspots_change = analysis["metric_changes"].get("large_sccs", {}).get("change_percent", 0)
        if hotspots_change > 20:
            fragility_score += 2
            factors.append("Hotspot growth")
        elif hotspots_change > 0:
            fragility_score += 1
            factors.append("Emerging hotspots")
        
        # Check module/dependency ratio
        modules_change = analysis["metric_changes"].get("total_modules", {}).get("change_percent", 0)
        deps_change = analysis["metric_changes"].get("total_dependencies", {}).get("change_percent", 0)
        
        if deps_change > modules_change + 20:
            fragility_score += 1
            factors.append("Dependencies growing faster than modules")
        
        # Determine prediction
        if fragility_score >= 4:
            prediction = "🔴 URGENT REFACTORING NEEDED"
            confidence = "HIGH"
        elif fragility_score >= 2:
            prediction = "🟡 REFACTORING RECOMMENDED"
            confidence = "MEDIUM"
        else:
            prediction = "🟢 SYSTEM STABLE"
            confidence = "HIGH"
        
        return {
            "prediction": prediction,
            "confidence": confidence,
            "fragility_score": fragility_score,
            "factors": factors,
            "recommendation": self._get_recommendation(fragility_score)
        }
    
    def _get_recommendation(self, fragility_score: int) -> str:
        """Get recommendation based on fragility score."""
        if fragility_score >= 4:
            return "Plan major architectural refactoring immediately"
        elif fragility_score >= 2:
            return "Schedule refactoring for next sprint"
        else:
            return "Continue current refactoring pace, monitor closely"
    
    def generate_report(self, output_path: str = "metrics_evolution.json") -> str:
        """
        Generate comprehensive metrics evolution report.
        
        Args:
            output_path: Path to save report
        
        Returns:
            Path to saved report
        """
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_snapshots": len(self.history),
            "snapshots": self.history,
            "trend_analysis": self.analyze_trends(),
            "refactoring_prediction": self.predict_refactoring_need(),
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"✅ Metrics report saved to: {output_path}")
        return output_path
    
    def _save_history(self) -> None:
        """Save metrics history to file."""
        with open(self.metrics_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def print_summary(self) -> None:
        """Print metrics summary."""
        if not self.history:
            print("No metrics history found")
            return
        
        print("\n" + "="*80)
        print("METRICS EVOLUTION SUMMARY")
        print("="*80)
        
        trends = self.analyze_trends()
        prediction = self.predict_refactoring_need()
        
        print(f"\nSnapshots collected: {trends['total_snapshots']}")
        print(f"Timespan: {trends['timespan']['first']} to {trends['timespan']['last']}")
        
        print("\nMetric Trends:")
        for metric, change_data in trends["metric_changes"].items():
            print(f"\n  {metric}:")
            print(f"    First: {change_data['first']}")
            print(f"    Last: {change_data['last']}")
            print(f"    Change: {change_data['change_percent']:+.1f}% {change_data['trend']}")
        
        print("\n" + "="*80)
        print("REFACTORING PREDICTION")
        print("="*80)
        print(f"\nPrediction: {prediction['prediction']}")
        print(f"Confidence: {prediction['confidence']}")
        print(f"Fragility Score: {prediction['fragility_score']}/4")
        print(f"Recommendation: {prediction['recommendation']}")
        
        if prediction.get("factors"):
            print("\nConcerning Factors:")
            for factor in prediction["factors"]:
                print(f"  • {factor}")
        
        if trends.get("alerts"):
            print("\nAlerts:")
            for alert in trends["alerts"]:
                print(f"  {alert}")


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Track brittle dependency metrics over time")
    parser.add_argument("--project", required=True, help="Project directory")
    parser.add_argument("--metrics-file", default="brent_metrics_history.json", help="Metrics history file")
    parser.add_argument("--action", choices=["append", "analyze", "predict"], default="analyze", help="Action to perform")
    parser.add_argument("--output", help="Output file path")
    
    args = parser.parse_args()
    
    tracker = MetricsTracker(args.metrics_file)
    
    if args.action == "append":
        # This would be called from CI with actual metrics data
        print("Use this tracker by importing and calling record_metrics()")
    elif args.action == "analyze":
        tracker.print_summary()
        if args.output:
            tracker.generate_report(args.output)
    elif args.action == "predict":
        prediction = tracker.predict_refactoring_need()
        print(f"\n{prediction['prediction']}")
        print(f"Confidence: {prediction['confidence']}")


if __name__ == "__main__":
    main()
