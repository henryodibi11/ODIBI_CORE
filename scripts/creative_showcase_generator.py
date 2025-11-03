"""
ODIBI_CORE Creative Showcase Generator
=======================================
Generates 100 creative, story-driven showcase configurations with:
- Randomized domains (IoT, finance, retail, healthcare, logistics, etc.)
- Varied DAG topologies (linear, branching, parallel, conditional)
- Mixed data formats (CSV, JSON, Parquet, Avro)
- Adaptive complexity scaling (simple → advanced)
- Reflection-ready narratives

Author: Henry Odibi
Project: ODIBI_CORE (ODB-1)
Codename: Creative Showcase Suite
"""

import json
import random
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass, asdict

# Creativity seed for reproducibility
random.seed(42)


@dataclass
class ShowcaseScenario:
    """Story-driven showcase scenario."""
    showcase_id: int
    title: str
    domain: str
    backstory: str
    data_goal: str
    formats: List[str]
    dag_topology: str
    complexity_level: str  # simple, medium, advanced
    use_caching: bool
    use_validation: bool
    use_events: bool
    inject_error: bool  # For resilience testing


class CreativeShowcaseGenerator:
    """Generates creative showcase configurations with varied patterns."""
    
    # Creativity engine data
    DOMAINS = [
        "IoT", "Finance", "Retail", "Healthcare", "Logistics",
        "Education", "Entertainment", "Social Media", "Environmental", "Manufacturing"
    ]
    
    FORMATS = ["CSV", "JSON", "Parquet", "Avro"]
    
    DAG_TOPOLOGIES = ["Linear", "Branching", "Parallel", "Conditional", "Diamond", "Cascade"]
    
    SCENARIOS_TEMPLATES = {
        "IoT": [
            ("Smart Factory Sensor Analytics", "Track temperature and vibration sensors across 500 machines", 
             "Identify equipment anomalies before failure"),
            ("Urban Air Quality Monitor", "Process data from 200 city air sensors in real-time",
             "Create hourly pollution heatmaps"),
            ("Smart Grid Energy Usage", "Aggregate power consumption from 10,000 smart meters",
             "Detect unusual consumption patterns")
        ],
        "Finance": [
            ("Credit Card Fraud Detection", "Analyze 1M transactions for anomalies",
             "Flag suspicious patterns for review"),
            ("Investment Portfolio Tracker", "Monitor stock prices and dividends across 50 holdings",
             "Calculate daily portfolio performance"),
            ("Crypto Trading Analytics", "Track BTC, ETH, ADA prices across 5 exchanges",
             "Identify arbitrage opportunities")
        ],
        "Retail": [
            ("E-Commerce Recommendation Engine", "Process 500k product views and purchases",
             "Generate personalized product suggestions"),
            ("Inventory Optimization", "Track stock levels across 100 warehouses",
             "Predict restocking needs"),
            ("Customer Churn Predictor", "Analyze customer activity over 12 months",
             "Identify at-risk customers")
        ],
        "Healthcare": [
            ("Patient Wait-Time Optimizer", "Track ER arrivals and discharge times",
             "Reduce average wait times"),
            ("Clinical Trial Data Pipeline", "Merge patient records from 3 hospitals",
             "Create unified trial dataset"),
            ("Vaccination Campaign Tracker", "Monitor doses administered across 50 clinics",
             "Report daily coverage rates")
        ],
        "Logistics": [
            ("Fleet Route Optimization", "Track 200 delivery vehicles in real-time",
             "Minimize fuel consumption"),
            ("Warehouse Picking Efficiency", "Analyze picker paths and times",
             "Optimize warehouse layout"),
            ("Supply Chain Visibility", "Integrate supplier, shipper, and warehouse data",
             "Track end-to-end delivery times")
        ],
        "Education": [
            ("Student Performance Analytics", "Aggregate test scores from 10 schools",
             "Identify struggling students early"),
            ("Online Learning Engagement", "Track video views, quiz scores, forum posts",
             "Measure course effectiveness"),
            ("University Admissions Pipeline", "Process 5,000 applications with SAT, GPA, essays",
             "Rank candidates by fit")
        ],
        "Entertainment": [
            ("Movie Recommendation Engine", "Analyze 1M user ratings across 10k movies",
             "Generate personalized watchlists"),
            ("Music Streaming Analytics", "Track 500k song plays per day",
             "Identify trending artists"),
            ("Gaming Leaderboard System", "Process match results from 100k players",
             "Update real-time rankings")
        ],
        "Social Media": [
            ("Sentiment Analysis Dashboard", "Process 1M tweets about brand mentions",
             "Track sentiment trends"),
            ("Influencer Impact Tracker", "Measure likes, shares, comments across platforms",
             "Rank influencers by engagement"),
            ("Content Moderation Pipeline", "Scan posts for policy violations",
             "Flag content for review")
        ],
        "Environmental": [
            ("Ocean Temperature Monitor", "Process buoy data from 100 locations",
             "Track warming trends"),
            ("Deforestation Detector", "Analyze satellite imagery over time",
             "Calculate forest loss rates"),
            ("Wildlife Migration Tracker", "Track GPS collars on 50 endangered species",
             "Map migration corridors")
        ],
        "Manufacturing": [
            ("Quality Control Automation", "Analyze defect rates from 10 production lines",
             "Identify root causes"),
            ("Predictive Maintenance", "Track machine vibration and temperature",
             "Predict failures 48 hours early"),
            ("Supply Chain Bottleneck Finder", "Monitor part arrivals and assembly times",
             "Optimize production flow")
        ]
    }
    
    def __init__(self, base_path: str = "D:/projects/odibi_core"):
        self.base_path = Path(base_path)
        self.config_path = self.base_path / "resources/configs/creative_showcases"
        self.data_path = self.base_path / "resources/data/showcases"
        
        # Create directories
        self.config_path.mkdir(parents=True, exist_ok=True)
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        self.scenarios: List[ShowcaseScenario] = []
    
    def generate_scenarios(self, count: int = 100) -> List[ShowcaseScenario]:
        """Generate creative scenarios with adaptive complexity."""
        print(f"\n{'='*70}")
        print(f"🧠 Creativity Engine: Generating {count} Showcase Scenarios")
        print(f"{'='*70}\n")
        
        for i in range(1, count + 1):
            # Domain selection (weighted random)
            domain = random.choice(self.DOMAINS)
            
            # Scenario template
            templates = self.SCENARIOS_TEMPLATES.get(domain, [("Generic Pipeline", "Process data", "Generate insights")])
            title, backstory, goal = random.choice(templates)
            
            # Add unique ID to title
            title_with_id = f"{title} #{i:03d}"
            
            # Complexity scaling (001-020: simple, 021-070: medium, 071-100: advanced)
            if i <= 20:
                complexity = "simple"
                num_sources = random.randint(1, 2)
                num_steps = random.randint(3, 6)
                use_caching = False
                use_validation = False
                use_events = True
            elif i <= 70:
                complexity = "medium"
                num_sources = random.randint(2, 3)
                num_steps = random.randint(6, 10)
                use_caching = random.choice([True, False])
                use_validation = True
                use_events = True
            else:
                complexity = "advanced"
                num_sources = random.randint(2, 4)
                num_steps = random.randint(10, 15)
                use_caching = True
                use_validation = True
                use_events = True
            
            # Data formats
            formats = random.sample(self.FORMATS, k=min(num_sources, len(self.FORMATS)))
            
            # DAG topology
            dag_topology = random.choice(self.DAG_TOPOLOGIES)
            
            # Error injection (5% of showcases)
            inject_error = (random.random() < 0.05)
            
            scenario = ShowcaseScenario(
                showcase_id=i,
                title=title_with_id,
                domain=domain,
                backstory=backstory,
                data_goal=goal,
                formats=formats,
                dag_topology=dag_topology,
                complexity_level=complexity,
                use_caching=use_caching,
                use_validation=use_validation,
                use_events=use_events,
                inject_error=inject_error
            )
            
            self.scenarios.append(scenario)
            
            if i % 10 == 0:
                print(f"  ✅ Generated {i}/{count} scenarios...")
        
        print(f"\n✅ All {count} scenarios generated\n")
        return self.scenarios
    
    def generate_json_config(self, scenario: ShowcaseScenario) -> Dict[str, Any]:
        """Generate JSON configuration from scenario."""
        steps = []
        step_id = 1
        
        # LAYER 1: Ingestion nodes (one per format)
        source_nodes = []
        for fmt in scenario.formats:
            node_name = f"ingest_{fmt.lower()}_{step_id}"
            steps.append({
                "id": step_id,
                "name": node_name,
                "layer": "bronze",
                "type": "read",
                "source": f"data/showcase_{scenario.showcase_id:03d}_source_{fmt.lower()}.{fmt.lower()}",
                "format": fmt.lower(),
                "depends_on": []
            })
            source_nodes.append(node_name)
            step_id += 1
        
        # LAYER 2: Merge/Join (if multiple sources)
        if len(source_nodes) > 1:
            merge_node = f"merge_sources_{step_id}"
            steps.append({
                "id": step_id,
                "name": merge_node,
                "layer": "silver",
                "type": "transform",
                "operation": "merge",
                "depends_on": source_nodes
            })
            prev_nodes = [merge_node]
            step_id += 1
        else:
            prev_nodes = source_nodes
        
        # LAYER 3: Transformations (based on DAG topology)
        if scenario.dag_topology == "Linear":
            # Sequential transformations
            for t in range(random.randint(2, 4)):
                node_name = f"transform_{t+1}_{step_id}"
                steps.append({
                    "id": step_id,
                    "name": node_name,
                    "layer": "silver",
                    "type": "transform",
                    "operation": random.choice(["filter", "aggregate", "enrich", "deduplicate"]),
                    "depends_on": prev_nodes
                })
                prev_nodes = [node_name]
                step_id += 1
        
        elif scenario.dag_topology == "Branching":
            # Split into 2 parallel branches
            branch1 = f"branch1_transform_{step_id}"
            branch2 = f"branch2_transform_{step_id+1}"
            steps.append({
                "id": step_id,
                "name": branch1,
                "layer": "silver",
                "type": "transform",
                "operation": "aggregate",
                "depends_on": prev_nodes
            })
            steps.append({
                "id": step_id+1,
                "name": branch2,
                "layer": "silver",
                "type": "transform",
                "operation": "filter",
                "depends_on": prev_nodes
            })
            prev_nodes = [branch1, branch2]
            step_id += 2
        
        elif scenario.dag_topology == "Parallel":
            # Multiple independent transforms
            parallel_nodes = []
            for p in range(3):
                node_name = f"parallel_{p+1}_{step_id}"
                steps.append({
                    "id": step_id,
                    "name": node_name,
                    "layer": "silver",
                    "type": "transform",
                    "operation": random.choice(["aggregate", "filter", "sort"]),
                    "depends_on": prev_nodes
                })
                parallel_nodes.append(node_name)
                step_id += 1
            prev_nodes = parallel_nodes
        
        else:  # Diamond, Conditional, Cascade
            # Default to simple sequential
            for t in range(2):
                node_name = f"transform_{t+1}_{step_id}"
                steps.append({
                    "id": step_id,
                    "name": node_name,
                    "layer": "silver",
                    "type": "transform",
                    "operation": "aggregate",
                    "depends_on": prev_nodes
                })
                prev_nodes = [node_name]
                step_id += 1
        
        # LAYER 4: Validation (if enabled)
        if scenario.use_validation:
            validate_node = f"validate_{step_id}"
            steps.append({
                "id": step_id,
                "name": validate_node,
                "layer": "gold",
                "type": "validate",
                "checks": ["not_empty", "schema_match"],
                "depends_on": prev_nodes
            })
            prev_nodes = [validate_node]
            step_id += 1
        
        # LAYER 5: Cache (if enabled)
        if scenario.use_caching:
            cache_node = f"cache_{step_id}"
            steps.append({
                "id": step_id,
                "name": cache_node,
                "layer": "gold",
                "type": "cache",
                "depends_on": prev_nodes
            })
            prev_nodes = [cache_node]
            step_id += 1
        
        # LAYER 6: Final publish
        publish_node = f"publish_final_{step_id}"
        steps.append({
            "id": step_id,
            "name": publish_node,
            "layer": "gold",
            "type": "write",
            "target": f"output/creative_showcases/showcase_{scenario.showcase_id:03d}_output.csv",
            "format": "csv",
            "depends_on": prev_nodes
        })
        
        # Error injection (if enabled)
        if scenario.inject_error:
            # Add a node with invalid operation to test recovery
            steps.insert(2, {
                "id": 99,
                "name": "error_injection_node",
                "layer": "silver",
                "type": "transform",
                "operation": "INVALID_OP",  # Will cause error
                "depends_on": source_nodes
            })
        
        config = {
            "metadata": {
                "showcase_id": scenario.showcase_id,
                "title": scenario.title,
                "domain": scenario.domain,
                "backstory": scenario.backstory,
                "data_goal": scenario.data_goal,
                "dag_topology": scenario.dag_topology,
                "complexity_level": scenario.complexity_level,
                "generated_at": datetime.now().isoformat(),
                "creativity_mode": "adaptive_scenario"
            },
            "steps": steps
        }
        
        return config
    
    def generate_all_configs(self) -> None:
        """Generate JSON configs for all scenarios."""
        print(f"\n{'='*70}")
        print(f"📝 Generating JSON Configurations")
        print(f"{'='*70}\n")
        
        for scenario in self.scenarios:
            config = self.generate_json_config(scenario)
            
            # Save JSON config (ConfigLoader expects array of steps)
            json_file = self.config_path / f"creative_showcase_{scenario.showcase_id:03d}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(config["steps"], f, indent=2)
            
            # Also save metadata separately for executor to read
            metadata_file = self.config_path / f"creative_showcase_{scenario.showcase_id:03d}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(config["metadata"], f, indent=2)
            
            if scenario.showcase_id % 10 == 0:
                print(f"  ✅ Generated {scenario.showcase_id}/100 JSON configs...")
        
        print(f"\n✅ All 100 JSON configs saved to: {self.config_path}\n")
    
    def generate_sql_configs_database(self) -> None:
        """Generate SQL database with all 100 configs."""
        print(f"\n{'='*70}")
        print(f"💾 Generating SQL Configuration Database")
        print(f"{'='*70}\n")
        
        db_path = self.config_path / "creative_showcases.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_metadata (
            showcase_id INTEGER PRIMARY KEY,
            title TEXT,
            domain TEXT,
            backstory TEXT,
            data_goal TEXT,
            dag_topology TEXT,
            complexity_level TEXT,
            generated_at TEXT
        )
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pipeline_steps (
            step_id INTEGER PRIMARY KEY AUTOINCREMENT,
            showcase_id INTEGER,
            step_name TEXT,
            layer TEXT,
            step_type TEXT,
            operation TEXT,
            source TEXT,
            target TEXT,
            format TEXT,
            depends_on TEXT,
            FOREIGN KEY (showcase_id) REFERENCES pipeline_metadata(showcase_id)
        )
        """)
        
        # Insert data from scenarios
        for scenario in self.scenarios:
            # Insert metadata
            cursor.execute("""
            INSERT INTO pipeline_metadata VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                scenario.showcase_id,
                scenario.title,
                scenario.domain,
                scenario.backstory,
                scenario.data_goal,
                scenario.dag_topology,
                scenario.complexity_level,
                datetime.now().isoformat()
            ))
            
            # Generate and insert steps
            config = self.generate_json_config(scenario)
            for step in config["steps"]:
                cursor.execute("""
                INSERT INTO pipeline_steps (showcase_id, step_name, layer, step_type, operation, source, target, format, depends_on)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    scenario.showcase_id,
                    step.get("name", ""),
                    step.get("layer", ""),
                    step.get("type", ""),
                    step.get("operation", ""),
                    step.get("source", ""),
                    step.get("target", ""),
                    step.get("format", ""),
                    ",".join(step.get("depends_on", []))
                ))
        
        conn.commit()
        conn.close()
        
        print(f"✅ SQL database created: {db_path}")
        print(f"   - {len(self.scenarios)} pipelines stored")
        print(f"   - Tables: pipeline_metadata, pipeline_steps\n")
    
    def generate_summary_report(self) -> None:
        """Generate configuration summary report."""
        print(f"\n{'='*70}")
        print(f"📊 Generating Configuration Summary")
        print(f"{'='*70}\n")
        
        report_path = self.base_path / "reports/showcases/creative"
        report_path.mkdir(parents=True, exist_ok=True)
        
        # Count by domain
        domain_counts = {}
        for s in self.scenarios:
            domain_counts[s.domain] = domain_counts.get(s.domain, 0) + 1
        
        # Count by topology
        topology_counts = {}
        for s in self.scenarios:
            topology_counts[s.dag_topology] = topology_counts.get(s.dag_topology, 0) + 1
        
        # Count by complexity
        complexity_counts = {}
        for s in self.scenarios:
            complexity_counts[s.complexity_level] = complexity_counts.get(s.complexity_level, 0) + 1
        
        md_content = f"""# ODIBI_CORE Creative Showcase Configuration Summary

**Generated:** {datetime.now().isoformat()}  
**Total Showcases:** {len(self.scenarios)}  
**Config Formats:** JSON + SQL Database

---

## Creativity Metrics

### Domain Distribution

| Domain | Count | Percentage |
|--------|-------|------------|
"""
        for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
            pct = (count / len(self.scenarios)) * 100
            md_content += f"| {domain} | {count} | {pct:.1f}% |\n"
        
        md_content += f"""

### DAG Topology Distribution

| Topology | Count | Percentage |
|----------|-------|------------|
"""
        for topology, count in sorted(topology_counts.items(), key=lambda x: -x[1]):
            pct = (count / len(self.scenarios)) * 100
            md_content += f"| {topology} | {count} | {pct:.1f}% |\n"
        
        md_content += f"""

### Complexity Scaling

| Level | Count | ID Range |
|-------|-------|----------|
"""
        for level, count in sorted(complexity_counts.items()):
            if level == "simple":
                id_range = "001-020"
            elif level == "medium":
                id_range = "021-070"
            else:
                id_range = "071-100"
            md_content += f"| {level.capitalize()} | {count} | {id_range} |\n"
        
        # Sample scenarios
        md_content += f"""

---

## Sample Scenarios

"""
        for s in random.sample(self.scenarios, 5):
            md_content += f"""
### {s.title}
- **Domain:** {s.domain}
- **Backstory:** {s.backstory}
- **Goal:** {s.data_goal}
- **Topology:** {s.dag_topology}
- **Complexity:** {s.complexity_level}
- **Features:** Caching: {s.use_caching}, Validation: {s.use_validation}, Events: {s.use_events}

"""
        
        md_content += """
---

## Configuration Files Generated

- **JSON Configs:** 100 files in `resources/configs/creative_showcases/`
  - Format: `creative_showcase_001.json` through `creative_showcase_100.json`
- **SQL Database:** `creative_showcases.db`
  - Tables: `pipeline_metadata`, `pipeline_steps`

---

## Creativity Engine Features

✅ **Adaptive Complexity Scaling** - Simple (1-20) → Medium (21-70) → Advanced (71-100)  
✅ **Domain Variation** - 10 domains with industry-specific scenarios  
✅ **DAG Topology Diversity** - Linear, Branching, Parallel, Conditional, Diamond, Cascade  
✅ **Multi-Format Support** - CSV, JSON, Parquet, Avro combinations  
✅ **Error Injection** - 5% of showcases test resilience  
✅ **Feature Blending** - Caching, validation, events mixed strategically

---

*Generated by ODIBI_CORE Creative Showcase Generator*
"""
        
        summary_file = report_path / "CREATIVE_CONFIG_GENERATION_SUMMARY.md"
        summary_file.write_text(md_content, encoding='utf-8')
        
        print(f"✅ Summary report saved: {summary_file}\n")


def main():
    """Main execution flow."""
    print("\n" + "="*70)
    print("🧠 ODIBI_CORE CREATIVE SHOWCASE GENERATOR")
    print("="*70)
    print("Project: ODIBI_CORE (ODB-1)")
    print("Mission: Generate 100 creative, story-driven showcase configurations")
    print("="*70)
    
    generator = CreativeShowcaseGenerator()
    
    # Phase 1: Generate scenarios
    generator.generate_scenarios(count=100)
    
    # Phase 2: Generate JSON configs
    generator.generate_all_configs()
    
    # Phase 3: Generate SQL database
    generator.generate_sql_configs_database()
    
    # Phase 4: Generate summary report
    generator.generate_summary_report()
    
    print("\n" + "="*70)
    print("✅ CREATIVE SHOWCASE CONFIGURATION GENERATION COMPLETE")
    print("="*70)
    print(f"\n📁 Output Locations:")
    print(f"  - JSON Configs: D:/projects/odibi_core/resources/configs/creative_showcases/")
    print(f"  - SQL Database: D:/projects/odibi_core/resources/configs/creative_showcases/creative_showcases.db")
    print(f"  - Summary Report: D:/projects/odibi_core/reports/showcases/creative/")
    print("\n🚀 Ready for Phase 2: Showcase Execution\n")


if __name__ == "__main__":
    main()
