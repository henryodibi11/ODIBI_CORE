"""
Batch Planner - Generate 100 Unique Advanced Showcases
=======================================================
Plans and generates diverse scenarios across 4 batches.
"""

import json
import random
import sys
import io
from pathlib import Path
from typing import List, Dict, Any, Set
from .scenario_spec import ScenarioSpec, ShowcaseMetadata
from .domain_knowledge import get_all_domains, sample_scenario_elements
from .graph_builder import GraphBuilder
from .explanation_generator import ExplanationGenerator

# Set UTF-8 encoding for Windows
if sys.platform == 'win32' and hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


class BatchPlanner:
    """Plans and generates 100 unique showcase scenarios."""
    
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        self.graph_builder = GraphBuilder()
        self.explanation_gen = ExplanationGenerator()
        self.fingerprints: Set[str] = set()
        self.generated_count = 0
    
    def generate_all(
        self,
        count: int = 100,
        out_dir: str = "D:/projects/odibi_core/resources/configs/advanced_showcases"
    ) -> List[ShowcaseMetadata]:
        """Generate all showcase configs and metadata."""
        print(f"\n{'='*80}")
        print(f"🎯 BATCH PLANNER: Generating {count} Advanced Showcases")
        print(f"{'='*80}\n")
        
        out_path = Path(out_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        
        all_metadata = []
        
        # Batch 1: Domain-based (30)
        print("📦 Batch 1: Domain-based showcases (30)")
        batch1 = self._generate_domain_batch(30, out_path)
        all_metadata.extend(batch1)
        
        # Batch 2: Format-based (30)
        print("\n📦 Batch 2: Format-based showcases (30)")
        batch2 = self._generate_format_batch(30, out_path)
        all_metadata.extend(batch2)
        
        # Batch 3: Transformation-heavy (30)
        print("\n📦 Batch 3: Transformation-heavy showcases (30)")
        batch3 = self._generate_transform_batch(30, out_path)
        all_metadata.extend(batch3)
        
        # Batch 4: Performance studies (10)
        print("\n📦 Batch 4: Performance & caching studies (10)")
        batch4 = self._generate_performance_batch(10, out_path)
        all_metadata.extend(batch4)
        
        print(f"\n{'='*80}")
        print(f"✅ Generated {len(all_metadata)} unique showcases")
        print(f"📁 Output: {out_path}")
        print(f"{'='*80}\n")
        
        return all_metadata
    
    def _generate_domain_batch(self, count: int, out_path: Path) -> List[ShowcaseMetadata]:
        """Generate domain-focused showcases (3 per domain)."""
        metadata_list = []
        domains = get_all_domains()
        per_domain = count // len(domains)
        
        for domain in domains:
            for i in range(per_domain):
                self.generated_count += 1
                showcase_id = self.generated_count
                
                # Sample scenario elements
                scenario_elem = sample_scenario_elements(domain, seed=self.seed + showcase_id)
                
                # Pick archetype
                archetypes = [
                    "multi_source_conformance",
                    "windowed_kpi",
                    "quality_branch"
                ]
                archetype = random.choice(archetypes)
                
                # Create spec
                spec = ScenarioSpec(
                    id=showcase_id,
                    domain=domain,
                    batch_type="domain",
                    archetype=archetype,
                    dag_topology=self.graph_builder.ARCHETYPES[archetype]["topology"],
                    complexity_level=random.choice(["moderate", "high"]),
                    formats=set(scenario_elem["formats"]),
                    kpis=scenario_elem["kpis"],
                    windows={scenario_elem["window"]: scenario_elem["window"]},
                    entities=scenario_elem["entities"],
                    problem_statement=scenario_elem["problem"],
                    design_rationale=scenario_elem["design_rationale"],
                    trade_offs=scenario_elem["trade_off"]
                )
                
                # Check uniqueness
                if spec.fingerprint in self.fingerprints:
                    # Mutate to make unique
                    spec.formats.add(random.choice(["CSV", "JSON", "PARQUET"]))
                
                self.fingerprints.add(spec.fingerprint)
                
                # Build pipeline
                steps, dag_sig = self.graph_builder.build(spec)
                
                # Generate metadata
                metadata = self._create_metadata(spec, scenario_elem)
                
                # Write files
                self._write_showcase(showcase_id, steps, metadata, out_path)
                
                metadata_list.append(metadata)
                print(f"  ✓ [{showcase_id:03d}] {domain}: {archetype} ({spec.complexity_level})")
        
        return metadata_list
    
    def _generate_format_batch(self, count: int, out_path: Path) -> List[ShowcaseMetadata]:
        """Generate format-diversity showcases."""
        metadata_list = []
        
        format_combos = [
            {"CSV", "JSON"},
            {"JSON", "PARQUET"},
            {"CSV", "PARQUET"},
            {"CSV", "JSON", "PARQUET"},
            {"PARQUET", "AVRO"},
            {"JSON", "AVRO"},
            {"CSV", "PARQUET", "AVRO"},
            {"CSV", "JSON", "PARQUET", "AVRO"}
        ]
        
        domains = get_all_domains()
        
        for i in range(count):
            self.generated_count += 1
            showcase_id = self.generated_count
            
            domain = domains[i % len(domains)]
            scenario_elem = sample_scenario_elements(domain, seed=self.seed + showcase_id)
            
            # Pick diverse format combo
            formats = format_combos[i % len(format_combos)]
            
            # Archetype based on format count
            if len(formats) >= 3:
                archetype = "multi_source_conformance"
            else:
                archetype = random.choice(["windowed_kpi", "parallel_transform"])
            
            spec = ScenarioSpec(
                id=showcase_id,
                domain=domain,
                batch_type="format",
                archetype=archetype,
                dag_topology=self.graph_builder.ARCHETYPES[archetype]["topology"],
                complexity_level=random.choice(["moderate", "high"]),
                formats=formats,
                kpis=scenario_elem["kpis"],
                windows={scenario_elem["window"]: scenario_elem["window"]},
                entities=scenario_elem["entities"],
                problem_statement=scenario_elem["problem"],
                design_rationale=scenario_elem["design_rationale"],
                trade_offs=scenario_elem["trade_off"]
            )
            
            self.fingerprints.add(spec.fingerprint)
            
            steps, dag_sig = self.graph_builder.build(spec)
            metadata = self._create_metadata(spec, scenario_elem)
            self._write_showcase(showcase_id, steps, metadata, out_path)
            
            metadata_list.append(metadata)
            print(f"  ✓ [{showcase_id:03d}] {domain}: {', '.join(formats)} formats")
        
        return metadata_list
    
    def _generate_transform_batch(self, count: int, out_path: Path) -> List[ShowcaseMetadata]:
        """Generate transformation-heavy showcases."""
        metadata_list = []
        
        heavy_archetypes = [
            "star_schema",
            "scd2_merge",
            "streaming_enrich",
            "hierarchical_agg",
            "anomaly_detection"
        ]
        
        domains = get_all_domains()
        
        for i in range(count):
            self.generated_count += 1
            showcase_id = self.generated_count
            
            domain = domains[i % len(domains)]
            scenario_elem = sample_scenario_elements(domain, seed=self.seed + showcase_id)
            
            archetype = heavy_archetypes[i % len(heavy_archetypes)]
            
            spec = ScenarioSpec(
                id=showcase_id,
                domain=domain,
                batch_type="transformation",
                archetype=archetype,
                dag_topology=self.graph_builder.ARCHETYPES[archetype]["topology"],
                complexity_level=random.choice(["high", "extreme"]),
                formats=set(scenario_elem["formats"][:2]),
                kpis=scenario_elem["kpis"],
                windows={scenario_elem["window"]: scenario_elem["window"]},
                entities=scenario_elem["entities"],
                problem_statement=scenario_elem["problem"],
                design_rationale=scenario_elem["design_rationale"],
                trade_offs=scenario_elem["trade_off"]
            )
            
            self.fingerprints.add(spec.fingerprint)
            
            steps, dag_sig = self.graph_builder.build(spec)
            metadata = self._create_metadata(spec, scenario_elem)
            self._write_showcase(showcase_id, steps, metadata, out_path)
            
            metadata_list.append(metadata)
            print(f"  ✓ [{showcase_id:03d}] {domain}: {archetype} ({spec.complexity_level})")
        
        return metadata_list
    
    def _generate_performance_batch(self, count: int, out_path: Path) -> List[ShowcaseMetadata]:
        """Generate performance comparison showcases."""
        metadata_list = []
        
        domains = get_all_domains()
        
        for i in range(count):
            self.generated_count += 1
            showcase_id = self.generated_count
            
            domain = domains[i % len(domains)]
            scenario_elem = sample_scenario_elements(domain, seed=self.seed + showcase_id)
            
            archetype = random.choice(["multi_source_conformance", "windowed_kpi", "star_schema"])
            
            # Alternate cache settings
            cache_enabled = (i % 2 == 0)
            
            spec = ScenarioSpec(
                id=showcase_id,
                domain=domain,
                batch_type="performance",
                archetype=archetype,
                dag_topology=self.graph_builder.ARCHETYPES[archetype]["topology"],
                complexity_level="high",
                formats=set(scenario_elem["formats"][:2]),
                kpis=scenario_elem["kpis"],
                windows={scenario_elem["window"]: scenario_elem["window"]},
                entities=scenario_elem["entities"],
                problem_statement=scenario_elem["problem"],
                design_rationale=scenario_elem["design_rationale"],
                trade_offs=scenario_elem["trade_off"],
                perf={
                    "cache_enabled": cache_enabled,
                    "parallel": True,
                    "max_workers": 4 if i % 2 == 0 else 2
                }
            )
            
            self.fingerprints.add(spec.fingerprint)
            
            steps, dag_sig = self.graph_builder.build(spec)
            metadata = self._create_metadata(spec, scenario_elem)
            self._write_showcase(showcase_id, steps, metadata, out_path)
            
            metadata_list.append(metadata)
            cache_str = "WITH cache" if cache_enabled else "NO cache"
            print(f"  ✓ [{showcase_id:03d}] {domain}: {archetype} ({cache_str})")
        
        return metadata_list
    
    def _create_metadata(self, spec: ScenarioSpec, scenario_elem: Dict[str, Any]) -> ShowcaseMetadata:
        """Create showcase metadata from spec."""
        # Generate title
        title = f"{spec.domain} {spec.archetype.replace('_', ' ').title()} Pipeline"
        
        # Generate backstory and goal using explanation generator
        temp_metadata = ShowcaseMetadata(
            showcase_id=spec.id,
            title=title,
            domain=spec.domain,
            backstory="",  # Will be filled
            data_goal="",  # Will be filled
            dag_topology=spec.dag_topology,
            complexity_level=spec.complexity_level,
            batch_type=spec.batch_type,
            archetype=spec.archetype,
            kpis=spec.kpis,
            formats=list(spec.formats),
            errors_injected=spec.error_injections,
            windows=spec.windows,
            perf_toggles=spec.perf,
            entities=spec.entities,
            problem_statement=spec.problem_statement,
            design_rationale=spec.design_rationale,
            trade_offs=spec.trade_offs
        )
        
        backstory = self.explanation_gen.generate_backstory(temp_metadata, scenario_elem)
        data_goal = self.explanation_gen.generate_data_goal(temp_metadata, scenario_elem)
        
        temp_metadata.backstory = backstory
        temp_metadata.data_goal = data_goal
        
        return temp_metadata
    
    def _write_showcase(
        self,
        showcase_id: int,
        steps: List[Dict[str, Any]],
        metadata: ShowcaseMetadata,
        out_path: Path
    ) -> None:
        """Write showcase config and metadata files."""
        # Write config (steps) - ConfigLoader expects array, not dict
        config_file = out_path / f"advanced_showcase_{showcase_id:03d}.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(steps, f, indent=2)
        
        # Write metadata
        metadata_file = out_path / f"advanced_showcase_{showcase_id:03d}_metadata.json"
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata.to_dict(), f, indent=2)


if __name__ == "__main__":
    planner = BatchPlanner()
    planner.generate_all(count=100)
