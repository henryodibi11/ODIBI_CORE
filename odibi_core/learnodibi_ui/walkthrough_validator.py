"""
Walkthrough Code Validator - Reads validation reports and provides pre-flight checking
"""
from pathlib import Path
from typing import Dict, Optional
import re


class WalkthroughValidator:
    """Reads and caches walkthrough validation reports"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.validation_data = self._load_validation_report()
    
    def _load_validation_report(self) -> Dict[str, dict]:
        """Load the LEARNODIBI_RERUN_RESULTS.md report"""
        report_path = self.project_root / "LEARNODIBI_RERUN_RESULTS.md"
        
        if not report_path.exists():
            return {}
        
        try:
            content = report_path.read_text(encoding='utf-8')
            data = {}
            
            # Parse the markdown table
            in_table = False
            for line in content.split('\n'):
                if line.startswith('| File |'):
                    in_table = True
                    continue
                if line.startswith('|------'):
                    continue
                if not line.startswith('|') or line.startswith('|**'):
                    in_table = False
                    continue
                
                if in_table:
                    parts = [p.strip() for p in line.split('|')]
                    if len(parts) >= 6:
                        file_name = parts[1]
                        try:
                            total_blocks = int(parts[2])
                            syntax_valid = int(parts[3])
                            syntax_invalid = int(parts[4])
                            status = parts[5]
                            
                            data[file_name] = {
                                'total_blocks': total_blocks,
                                'syntax_valid': syntax_valid,
                                'syntax_invalid': syntax_invalid,
                                'status': status
                            }
                        except ValueError:
                            continue
            
            return data
        except Exception as e:
            print(f"Warning: Could not load validation report: {e}")
            return {}
    
    def get_file_status(self, filename: str) -> Optional[dict]:
        """Get validation status for a specific walkthrough file"""
        return self.validation_data.get(filename)
    
    def get_coverage_stats(self) -> dict:
        """Get overall coverage statistics"""
        if not self.validation_data:
            return {
                'total_files': 0,
                'total_blocks': 0,
                'valid_blocks': 0,
                'invalid_blocks': 0,
                'coverage_pct': 0.0
            }
        
        total_blocks = sum(v['total_blocks'] for v in self.validation_data.values())
        valid_blocks = sum(v['syntax_valid'] for v in self.validation_data.values())
        invalid_blocks = sum(v['syntax_invalid'] for v in self.validation_data.values())
        
        return {
            'total_files': len(self.validation_data),
            'total_blocks': total_blocks,
            'valid_blocks': valid_blocks,
            'invalid_blocks': invalid_blocks,
            'coverage_pct': (valid_blocks / total_blocks * 100) if total_blocks > 0 else 0.0
        }
    
    def has_known_issues(self, filename: str) -> bool:
        """Check if a walkthrough file has known validation issues"""
        file_status = self.get_file_status(filename)
        if not file_status:
            return False
        return file_status['syntax_invalid'] > 0
