"""
Project Scaffolder - Create learning projects with proper structure
"""

import os
from pathlib import Path
from typing import Dict, List, Optional
import json


class ProjectScaffolder:
    """Scaffold new ODIBI CORE learning projects"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Dict]:
        """Load project templates"""
        return {
            "basic": {
                "name": "Basic Pipeline",
                "description": "Simple Bronze → Silver → Gold pipeline",
                "files": self._get_basic_template()
            },
            "transformation": {
                "name": "Transformation Focus",
                "description": "Focus on data transformations",
                "files": self._get_transformation_template()
            },
            "functions": {
                "name": "Functions Playground",
                "description": "Explore ODIBI functions",
                "files": self._get_functions_template()
            }
        }
    
    def validate_path(self, path: str) -> tuple[bool, str]:
        """
        Validate project path
        
        Returns:
            (is_valid, message)
        """
        path_obj = Path(path)
        
        # Check if path is absolute
        if not path_obj.is_absolute():
            return False, "Please provide an absolute path (e.g., /d:/projects/my_project)"
        
        # Check if parent directory exists
        if not path_obj.parent.exists():
            return False, f"Parent directory does not exist: {path_obj.parent}"
        
        # Check if path already exists
        if path_obj.exists():
            if list(path_obj.iterdir()):
                return False, f"Directory already exists and is not empty: {path}"
            else:
                return True, "Directory exists but is empty (will use it)"
        
        return True, "Path is valid and ready to create"
    
    def create_project(
        self, 
        path: str, 
        template: str = "basic",
        project_name: Optional[str] = None
    ) -> Dict[str, List[str]]:
        """
        Create a new learning project
        
        Args:
            path: Absolute path where project should be created
            template: Template name (basic, transformation, functions)
            project_name: Optional custom project name
            
        Returns:
            Dictionary with created files and logs
        """
        path_obj = Path(path)
        
        # Validate
        is_valid, message = self.validate_path(path)
        if not is_valid:
            raise ValueError(message)
        
        # Create directory
        path_obj.mkdir(parents=True, exist_ok=True)
        
        # Get template
        template_data = self.templates.get(template, self.templates["basic"])
        if project_name is None:
            project_name = path_obj.name
        
        # Track created items
        created = {
            "folders": [],
            "files": [],
            "logs": []
        }
        
        # Create structure
        created["logs"].append(f"Creating project: {project_name}")
        created["logs"].append(f"Location: {path}")
        created["logs"].append(f"Template: {template_data['name']}")
        
        # Create folders
        folders = [
            "configs",
            "data/bronze",
            "data/silver", 
            "data/gold",
            "notebooks",
            "logs"
        ]
        
        for folder in folders:
            folder_path = path_obj / folder
            folder_path.mkdir(parents=True, exist_ok=True)
            created["folders"].append(str(folder_path))
            created["logs"].append(f"✅ Created folder: {folder}")
        
        # Create files from template
        for filename, content in template_data["files"].items():
            file_path = path_obj / filename
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Replace placeholders
            if isinstance(content, str):
                content = content.replace("{{PROJECT_NAME}}", project_name)
            
            # Write file
            if isinstance(content, dict):
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(content, f, indent=2)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            created["files"].append(str(file_path))
            created["logs"].append(f"✅ Created file: {filename}")
        
        # Create README
        readme_content = self._generate_readme(project_name, template_data)
        readme_path = path_obj / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        created["files"].append(str(readme_path))
        created["logs"].append("✅ Created README.md")
        
        created["logs"].append("")
        created["logs"].append("🎉 Project created successfully!")
        created["logs"].append(f"📁 Total folders: {len(created['folders'])}")
        created["logs"].append(f"📄 Total files: {len(created['files'])}")
        
        return created
    
    def _get_basic_template(self) -> Dict[str, str]:
        """Get basic template files"""
        return {
            "run_project.py": '''"""
{{PROJECT_NAME}} - ODIBI CORE Learning Project
"""

from pathlib import Path
import pandas as pd

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"

def main():
    """Run the learning project"""
    print("🚀 Starting {{PROJECT_NAME}}...")
    
    # Bronze: Load raw data
    print("\\n📥 Bronze Layer - Loading raw data...")
    bronze_data = pd.DataFrame({
        'id': [1, 2, 3],
        'value': [10, 20, 30]
    })
    bronze_path = DATA_DIR / "bronze" / "raw_data.csv"
    bronze_data.to_csv(bronze_path, index=False)
    print(f"✅ Saved: {bronze_path}")
    
    # Silver: Transform data
    print("\\n🔄 Silver Layer - Transforming data...")
    silver_data = bronze_data.copy()
    silver_data['value_squared'] = silver_data['value'] ** 2
    silver_path = DATA_DIR / "silver" / "transformed_data.csv"
    silver_data.to_csv(silver_path, index=False)
    print(f"✅ Saved: {silver_path}")
    
    # Gold: Aggregate data
    print("\\n📊 Gold Layer - Aggregating data...")
    gold_data = pd.DataFrame({
        'total': [silver_data['value'].sum()],
        'total_squared': [silver_data['value_squared'].sum()],
        'count': [len(silver_data)]
    })
    gold_path = DATA_DIR / "gold" / "aggregated_data.csv"
    gold_data.to_csv(gold_path, index=False)
    print(f"✅ Saved: {gold_path}")
    
    print("\\n✨ Pipeline complete!")
    print(f"\\nResults:\\n{gold_data}")

if __name__ == "__main__":
    main()
''',
            "configs/pipeline_config.json": {
                "pipeline_name": "{{PROJECT_NAME}}",
                "engine": "pandas",
                "layers": ["bronze", "silver", "gold"]
            }
        }
    
    def _get_transformation_template(self) -> Dict[str, str]:
        """Get transformation template files"""
        files = self._get_basic_template()
        files["notebooks/transformations.ipynb"] = json.dumps({
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": ["# {{PROJECT_NAME}} Transformations\n", "\n", "Explore ODIBI CORE transformations"]
                },
                {
                    "cell_type": "code",
                    "metadata": {},
                    "source": ["import pandas as pd\n", "from odibi_core import functions\n", "\n", "# Your transformations here"]
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 4
        }, indent=2)
        return files
    
    def _get_functions_template(self) -> Dict[str, str]:
        """Get functions template files"""
        files = self._get_basic_template()
        files["explore_functions.py"] = '''"""
Explore ODIBI CORE Functions
"""

from odibi_core import functions
import pandas as pd

# Example: Temperature conversion
celsius = 25
fahrenheit = functions.celsius_to_fahrenheit(celsius)
print(f"{celsius}°C = {fahrenheit}°F")

# Example: Data quality
df = pd.DataFrame({'a': [1, 2, None], 'b': [4, None, 6]})
completeness = functions.calculate_completeness(df)
print(f"Data completeness: {completeness}%")

# Explore more functions!
'''
        return files
    
    def _generate_readme(self, project_name: str, template_data: Dict) -> str:
        """Generate project README"""
        return f"""# {project_name}

**Description**: {template_data['description']}

## Structure

```
{project_name}/
├── configs/               # Configuration files
├── data/
│   ├── bronze/           # Raw data
│   ├── silver/           # Transformed data
│   └── gold/             # Aggregated data
├── notebooks/            # Jupyter notebooks
├── logs/                 # Log files
├── run_project.py        # Main pipeline script
└── README.md             # This file
```

## Getting Started

1. **Install ODIBI CORE** (if not already installed):
   ```bash
   pip install odibi-core
   ```

2. **Run the pipeline**:
   ```bash
   python run_project.py
   ```

3. **Explore the data**:
   - Check `data/` folders for outputs
   - Review `logs/` for execution details

## Learning Resources

- **Documentation**: See ODIBI CORE docs
- **Examples**: Check `notebooks/` for interactive examples
- **Functions**: Explore `odibi_core.functions` module

## Next Steps

- Modify `run_project.py` to add your own logic
- Create custom transformations
- Experiment with different data sources
- Try Spark engine for larger datasets

---

**Created with**: ODIBI CORE LearnODIBI Studio
"""
