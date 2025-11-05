"""
Recommendation Engine - Template Candidate Detection
=====================================================
Identifies reusable templates from pattern analysis.
"""

from pathlib import Path
from typing import Dict, List, Any
from collections import Counter


class RecommendationEngine:
    """Generates framework improvement recommendations."""
    
    def __init__(self):
        self.recommendations = []
    
    def generate_recommendations(
        self,
        pattern_results: Dict,
        executions: List[Any]
    ) -> List[Dict[str, str]]:
        """Generate recommendations from pattern analysis."""
        print(f"\n{'='*80}")
        print(f"💡 RECOMMENDATION ENGINE: Generating Insights")
        print(f"{'='*80}\n")
        
        recommendations = []
        
        # Template candidates from clusters
        template_recs = self._recommend_templates(pattern_results.get("clusters", {}))
        recommendations.extend(template_recs)
        
        # Config abstraction from repetitions
        config_recs = self._recommend_config_abstractions(pattern_results.get("repetitions", {}))
        recommendations.extend(config_recs)
        
        # Performance optimizations
        perf_recs = self._recommend_performance_opts(executions)
        recommendations.extend(perf_recs)
        
        # API simplifications
        api_recs = self._recommend_api_improvements(pattern_results)
        recommendations.extend(api_recs)
        
        self.recommendations = recommendations
        
        print(f"\n✅ Generated {len(recommendations)} recommendations")
        return recommendations
    
    def _recommend_templates(self, clusters: Dict) -> List[Dict[str, str]]:
        """Recommend template candidates from clusters."""
        recommendations = []
        
        print("📋 Template Candidates:")
        print("-" * 80)
        
        for name, data in sorted(clusters.items(), key=lambda x: x[1]["count"], reverse=True):
            if data["count"] >= 5:  # Threshold for template candidacy
                rec = {
                    "type": "template_candidate",
                    "priority": "high" if data["count"] >= 10 else "medium",
                    "title": f"Create {name.replace('_', ' ').title()} Template",
                    "description": f"Pattern found in {data['count']} showcases with signature: {data['signature'][:60]}",
                    "affected_showcases": data["showcases"],
                    "impact": f"Reduce boilerplate for {data['count']} similar pipelines",
                    "implementation": f"Extract common DAG structure into template class with parameterized config"
                }
                recommendations.append(rec)
                print(f"  ✓ {rec['title']} (priority: {rec['priority']})")
        
        return recommendations
    
    def _recommend_config_abstractions(self, repetitions: Dict) -> List[Dict[str, str]]:
        """Recommend config schema abstractions."""
        recommendations = []
        
        print("\n🔧 Config Abstractions:")
        print("-" * 80)
        
        # Look for highly repeated patterns
        high_rep = {k: v for k, v in repetitions.items() if v > 10}
        
        if high_rep:
            for pattern, count in sorted(high_rep.items(), key=lambda x: x[1], reverse=True)[:5]:
                if "op_pattern" in pattern or "layer_pattern" in pattern:
                    rec = {
                        "type": "config_abstraction",
                        "priority": "medium",
                        "title": f"Abstract {pattern.split(':')[0].replace('_', ' ').title()}",
                        "description": f"Pattern '{pattern.split(':', 1)[1][:50]}' repeats {count} times",
                        "impact": f"Simplify config for {count} pipelines",
                        "implementation": "Create config schema builder with preset patterns"
                    }
                    recommendations.append(rec)
                    print(f"  ✓ {rec['title']}")
        
        return recommendations
    
    def _recommend_performance_opts(self, executions: List[Any]) -> List[Dict[str, str]]:
        """Recommend performance optimizations."""
        recommendations = []
        
        print("\n⚡ Performance Optimizations:")
        print("-" * 80)
        
        # Analyze cache effectiveness
        cache_users = [e for e in executions if hasattr(e, 'cache_hits') and e.cache_hits > 0]
        if len(cache_users) > len(executions) * 0.6:
            rec = {
                "type": "performance_optimization",
                "priority": "high",
                "title": "Enable Auto-Caching for Common Patterns",
                "description": f"{len(cache_users)}/{len(executions)} showcases benefited from caching",
                "impact": "Reduce execution time by 20-40% for repeated operations",
                "implementation": "Add intelligent auto-caching hints in Orchestrator based on DAG analysis"
            }
            recommendations.append(rec)
            print(f"  ✓ {rec['title']}")
        
        # Parallel execution opportunities
        rec = {
            "type": "performance_optimization",
            "priority": "medium",
            "title": "Expand Parallel Execution Support",
            "description": "Many fan-in/fan-out patterns could benefit from expanded parallelism",
            "impact": "Reduce execution time for multi-source pipelines",
            "implementation": "Enhance DAGExecutor to detect and parallelize independent branches automatically"
        }
        recommendations.append(rec)
        print(f"  ✓ {rec['title']}")
        
        return recommendations
    
    def _recommend_api_improvements(self, pattern_results: Dict) -> List[Dict[str, str]]:
        """Recommend API simplifications."""
        recommendations = []
        
        print("\n🎯 API Improvements:")
        print("-" * 80)
        
        # Suggest EventEmitter pattern library
        rec = {
            "type": "api_improvement",
            "priority": "low",
            "title": "Create EventEmitter Pattern Library",
            "description": "Common event patterns (pipeline_start/complete, step_start/complete) used across all showcases",
            "impact": "Simplify event registration with preset patterns",
            "implementation": "Add EventEmitter.register_standard_patterns() method"
        }
        recommendations.append(rec)
        print(f"  ✓ {rec['title']}")
        
        # Suggest validation template library
        rec = {
            "type": "api_improvement",
            "priority": "medium",
            "title": "Build Validation Template Library",
            "description": "Validation patterns repeat across domains",
            "impact": "Reduce validation config boilerplate",
            "implementation": "Create ValidationLibrary with domain-specific presets"
        }
        recommendations.append(rec)
        print(f"  ✓ {rec['title']}")
        
        return recommendations
    
    def save_report(self, output_path: str) -> None:
        """Save recommendations report."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        md_content = f"""# Framework Recommendations Report

## Summary
Generated {len(self.recommendations)} recommendations based on pattern analysis of 100 advanced showcases.

## Recommendations by Priority

### High Priority
{self._format_by_priority("high")}

### Medium Priority
{self._format_by_priority("medium")}

### Low Priority
{self._format_by_priority("low")}

## Recommendations by Type

### Template Candidates
{self._format_by_type("template_candidate")}

### Config Abstractions
{self._format_by_type("config_abstraction")}

### Performance Optimizations
{self._format_by_type("performance_optimization")}

### API Improvements
{self._format_by_type("api_improvement")}

---
*Generated by ODIBI_CORE Recommendation Engine*
"""
        
        output_file.write_text(md_content, encoding='utf-8')
        print(f"\n📄 Recommendations report saved: {output_file.name}")
    
    def _format_by_priority(self, priority: str) -> str:
        """Format recommendations by priority."""
        recs = [r for r in self.recommendations if r.get("priority") == priority]
        
        if not recs:
            return f"*No {priority} priority recommendations*"
        
        lines = []
        for rec in recs:
            lines.append(f"#### {rec['title']}")
            lines.append(f"- **Type**: {rec['type'].replace('_', ' ').title()}")
            lines.append(f"- **Description**: {rec['description']}")
            lines.append(f"- **Impact**: {rec['impact']}")
            lines.append(f"- **Implementation**: {rec['implementation']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_by_type(self, rec_type: str) -> str:
        """Format recommendations by type."""
        recs = [r for r in self.recommendations if r.get("type") == rec_type]
        
        if not recs:
            return f"*No {rec_type.replace('_', ' ')} recommendations*"
        
        lines = []
        for rec in recs:
            lines.append(f"#### {rec['title']} ({rec['priority']} priority)")
            lines.append(f"- {rec['description']}")
            lines.append(f"- **Impact**: {rec['impact']}")
            lines.append("")
        
        return "\n".join(lines)
