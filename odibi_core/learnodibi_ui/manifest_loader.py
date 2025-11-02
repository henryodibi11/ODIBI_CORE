"""
Manifest Loader - Load and query walkthrough manifest
"""
import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime


class ManifestLoader:
    """Loads and provides access to walkthrough manifest data"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.manifest_path = project_root / "walkthrough_manifest.json"
        self.manifest = self._load_manifest()
    
    def _load_manifest(self) -> Dict:
        """Load manifest JSON file"""
        if not self.manifest_path.exists():
            return {
                "generated": datetime.now().isoformat(),
                "total_walkthroughs": 0,
                "walkthroughs": [],
                "totals": {
                    "total_steps": 0,
                    "total_code_blocks": 0,
                    "valid_code_blocks": 0,
                    "runnable_steps": 0
                }
            }
        
        try:
            with open(self.manifest_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Could not load manifest: {e}")
            return {
                "generated": datetime.now().isoformat(),
                "total_walkthroughs": 0,
                "walkthroughs": [],
                "totals": {
                    "total_steps": 0,
                    "total_code_blocks": 0,
                    "valid_code_blocks": 0,
                    "runnable_steps": 0
                }
            }
    
    def get_all_walkthroughs(self) -> List[Dict]:
        """Get all walkthrough metadata"""
        return self.manifest.get("walkthroughs", [])
    
    def get_walkthrough(self, filename: str) -> Optional[Dict]:
        """Get specific walkthrough by filename"""
        for wt in self.manifest.get("walkthroughs", []):
            if wt["filename"] == filename:
                return wt
        return None
    
    def get_walkthrough_by_name(self, name: str) -> Optional[Dict]:
        """Get specific walkthrough by name"""
        for wt in self.manifest.get("walkthroughs", []):
            if wt["walkthrough_name"] == name:
                return wt
        return None
    
    def get_totals(self) -> Dict:
        """Get overall statistics"""
        return self.manifest.get("totals", {})
    
    def is_fresh(self, max_age_hours: int = 24) -> bool:
        """Check if manifest is fresh (recently generated)"""
        try:
            generated_str = self.manifest.get("generated")
            if not generated_str:
                return False
            
            generated = datetime.fromisoformat(generated_str)
            age = datetime.now() - generated
            return age.total_seconds() / 3600 < max_age_hours
        except Exception:
            return False
    
    def get_walkthrough_list_for_ui(self) -> List[Dict]:
        """Get simplified list for UI dropdown"""
        walkthroughs = []
        for wt in self.get_all_walkthroughs():
            walkthroughs.append({
                "filename": wt["filename"],
                "title": wt["title"],
                "steps": wt["total_steps"],
                "duration": wt.get("duration", "Unknown"),
                "has_issues": wt.get("has_issues", False),
                "code_coverage": (wt["code_blocks_valid"] / wt["code_blocks_total"] * 100)
                                  if wt["code_blocks_total"] > 0 else 100
            })
        return walkthroughs
    
    def reload(self):
        """Reload manifest from disk"""
        self.manifest = self._load_manifest()
