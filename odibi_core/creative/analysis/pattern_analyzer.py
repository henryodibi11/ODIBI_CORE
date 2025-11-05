"""
Pattern Analyzer - DAG Clustering & Repetition Detection
==========================================================
Analyzes 100 showcases to find common patterns and boilerplate.
"""

import json
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict, Counter


class PatternAnalyzer:
    """Analyzes showcase patterns for clustering and optimization."""
    
    def __init__(self):
        self.dag_clusters: Dict[str, List[int]] = defaultdict(list)
        self.config_repetitions: Dict[str, int] = Counter()
        self.step_sequences: List[Tuple[int, List[str]]] = []
    
    def analyze_all(self, config_dir: str) -> Dict[str, any]:
        """Analyze all showcase configs for patterns."""
        config_path = Path(config_dir)
        
        # Find all config files
        config_files = sorted(config_path.glob("advanced_showcase_*.json"))
        config_files = [f for f in config_files if not f.name.endswith("_metadata.json")]
        
        print(f"\n{'='*80}")
        print(f"🔍 PATTERN ANALYZER: Analyzing {len(config_files)} showcases")
        print(f"{'='*80}\n")
        
        # Analyze each config
        for config_file in config_files:
            showcase_id = int(config_file.stem.split("_")[-1])
            self._analyze_config(showcase_id, config_file)
        
        # Cluster DAGs
        clusters = self._cluster_dags()
        
        # Find repetitions
        repetitions = self._find_repetitions()
        
        # Generate insights
        insights = self._generate_insights(clusters, repetitions)
        
        return {
            "clusters": clusters,
            "repetitions": repetitions,
            "insights": insights,
            "total_analyzed": len(config_files)
        }
    
    def _analyze_config(self, showcase_id: int, config_file: Path) -> None:
        """Analyze single config file."""
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        steps = config.get("steps", [])
        
        # Extract step sequence
        step_types = [s.get("operation", "unknown") for s in steps]
        self.step_sequences.append((showcase_id, step_types))
        
        # Count layer patterns
        layers = [s.get("layer", "unknown") for s in steps]
        layer_pattern = "->".join(layers)
        self.config_repetitions[f"layer_pattern:{layer_pattern}"] += 1
        
        # Count operation patterns
        op_pattern = "->".join(step_types)
        self.config_repetitions[f"op_pattern:{op_pattern}"] += 1
        
        # Compute DAG signature for clustering
        dag_sig = self._compute_simple_signature(steps)
        self.dag_clusters[dag_sig].append(showcase_id)
    
    def _compute_simple_signature(self, steps: List[Dict]) -> str:
        """Compute simple DAG signature."""
        # Count by layer
        layer_counts = Counter(s.get("layer", "unknown") for s in steps)
        
        # Count by operation
        op_counts = Counter(s.get("operation", "unknown") for s in steps)
        
        # Build signature
        sig_parts = [
            f"layers:{dict(layer_counts)}",
            f"ops:{dict(op_counts)}"
        ]
        
        return "|".join(sig_parts)
    
    def _cluster_dags(self) -> Dict[str, List[int]]:
        """Cluster DAGs by signature."""
        print("📊 DAG Clustering Results:")
        print("-" * 80)
        
        clusters = {}
        for sig, showcase_ids in sorted(self.dag_clusters.items(), key=lambda x: len(x[1]), reverse=True):
            if len(showcase_ids) > 1:
                cluster_name = f"cluster_{len(clusters)+1}"
                clusters[cluster_name] = {
                    "signature": sig,
                    "count": len(showcase_ids),
                    "showcases": showcase_ids
                }
                print(f"  {cluster_name}: {len(showcase_ids)} showcases - {sig[:60]}...")
        
        print(f"\n  Total clusters: {len(clusters)}")
        return clusters
    
    def _find_repetitions(self) -> Dict[str, any]:
        """Find repeated patterns."""
        print("\n🔁 Repetition Analysis:")
        print("-" * 80)
        
        repetitions = {}
        
        # Find most common n-grams (subsequences)
        ngrams = self._extract_ngrams()
        
        # Report top repetitions
        top_repetitions = sorted(
            [(k, v) for k, v in self.config_repetitions.items() if v > 5],
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        for pattern, count in top_repetitions:
            repetitions[pattern] = count
            print(f"  {pattern}: {count} occurrences")
        
        # N-gram patterns
        if ngrams:
            print(f"\n  Common 3-step sequences:")
            for ngram, count in sorted(ngrams.items(), key=lambda x: x[1], reverse=True)[:5]:
                print(f"    {ngram}: {count} times")
                repetitions[f"ngram:{ngram}"] = count
        
        return repetitions
    
    def _extract_ngrams(self, n: int = 3) -> Counter:
        """Extract n-gram patterns from step sequences."""
        ngrams = Counter()
        
        for showcase_id, seq in self.step_sequences:
            if len(seq) >= n:
                for i in range(len(seq) - n + 1):
                    ngram = "->".join(seq[i:i+n])
                    ngrams[ngram] += 1
        
        return ngrams
    
    def _generate_insights(self, clusters: Dict, repetitions: Dict) -> Dict[str, any]:
        """Generate analytical insights."""
        print("\n💡 Key Insights:")
        print("-" * 80)
        
        insights = {}
        
        # Cluster insights
        if clusters:
            largest_cluster = max(clusters.values(), key=lambda x: x["count"])
            insights["largest_cluster_size"] = largest_cluster["count"]
            insights["largest_cluster_showcases"] = largest_cluster["showcases"]
            print(f"  Largest cluster: {largest_cluster['count']} showcases with similar DAG structure")
        
        # Repetition insights
        if repetitions:
            most_common = max(repetitions.items(), key=lambda x: x[1])
            insights["most_common_pattern"] = most_common[0]
            insights["most_common_count"] = most_common[1]
            print(f"  Most common pattern: {most_common[0]} ({most_common[1]} times)")
        
        # Diversity score
        unique_sigs = len(self.dag_clusters)
        total = sum(len(ids) for ids in self.dag_clusters.values())
        diversity = unique_sigs / total if total > 0 else 0
        insights["diversity_score"] = diversity
        print(f"  Diversity score: {diversity:.2%} ({unique_sigs} unique patterns out of {total} showcases)")
        
        return insights
    
    def save_report(self, results: Dict, output_path: str) -> None:
        """Save pattern analysis report."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        md_content = f"""# Advanced Pattern Analysis Report

## Overview
- **Total Showcases Analyzed**: {results['total_analyzed']}
- **Unique DAG Patterns**: {len(results['clusters'])}
- **Diversity Score**: {results['insights'].get('diversity_score', 0):.2%}

## DAG Clusters

{self._format_clusters(results['clusters'])}

## Common Repetitions

{self._format_repetitions(results['repetitions'])}

## Key Insights

{self._format_insights(results['insights'])}

---
*Generated by ODIBI_CORE Pattern Analyzer*
"""
        
        output_file.write_text(md_content, encoding='utf-8')
        print(f"\n📄 Pattern analysis report saved: {output_file.name}")
    
    def _format_clusters(self, clusters: Dict) -> str:
        """Format clusters for Markdown."""
        if not clusters:
            return "No significant clusters found."
        
        lines = []
        for name, data in sorted(clusters.items(), key=lambda x: x[1]["count"], reverse=True):
            lines.append(f"### {name}")
            lines.append(f"- **Count**: {data['count']} showcases")
            lines.append(f"- **Signature**: `{data['signature']}`")
            lines.append(f"- **Showcases**: {', '.join(map(str, data['showcases'][:10]))}{'...' if len(data['showcases']) > 10 else ''}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_repetitions(self, repetitions: Dict) -> str:
        """Format repetitions for Markdown."""
        if not repetitions:
            return "No significant repetitions found."
        
        lines = []
        for pattern, count in sorted(repetitions.items(), key=lambda x: x[1], reverse=True)[:15]:
            lines.append(f"- **{pattern}**: {count} occurrences")
        
        return "\n".join(lines)
    
    def _format_insights(self, insights: Dict) -> str:
        """Format insights for Markdown."""
        lines = []
        
        if "largest_cluster_size" in insights:
            lines.append(f"- **Largest Cluster**: {insights['largest_cluster_size']} showcases share similar DAG structure")
        
        if "most_common_pattern" in insights:
            lines.append(f"- **Most Common Pattern**: `{insights['most_common_pattern']}` ({insights['most_common_count']} occurrences)")
        
        if "diversity_score" in insights:
            score = insights["diversity_score"]
            assessment = "excellent" if score > 0.7 else "good" if score > 0.5 else "moderate"
            lines.append(f"- **Diversity Assessment**: {assessment.capitalize()} ({score:.1%})")
        
        return "\n".join(lines) if lines else "No insights generated."
