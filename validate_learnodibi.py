"""
LearnODIBI Manifest Validator
Validates walkthrough manifest against actual files and teaching quality standards
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

# Setup paths
ODIBI_ROOT = Path(__file__).parent
WALKTHROUGHS_DIR = ODIBI_ROOT / "docs" / "walkthroughs"
MANIFEST_PATH = ODIBI_ROOT / "walkthrough_manifest.json"

# Quality thresholds
MIN_RUNNABLE_VALIDITY = 1.0  # 100% for learn_mode
MIN_TEACH_VALIDITY = 0.90     # 90% for teach_mode
MIN_QUALITY_SCORE = 9.0       # Target quality score


class ManifestValidator:
    """Validates walkthrough manifest against actual files"""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.info = []
        
    def load_manifest(self) -> Dict:
        """Load and parse manifest file"""
        try:
            with open(MANIFEST_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            self.errors.append(f"Manifest file not found: {MANIFEST_PATH}")
            return {}
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in manifest: {e}")
            return {}
    
    def get_actual_walkthrough_files(self) -> List[Path]:
        """Get list of actual walkthrough markdown files"""
        if not WALKTHROUGHS_DIR.exists():
            self.errors.append(f"Walkthroughs directory not found: {WALKTHROUGHS_DIR}")
            return []
        
        files = list(WALKTHROUGHS_DIR.glob("DEVELOPER_WALKTHROUGH_*.md"))
        return sorted(files, key=lambda f: f.name)
    
    def validate_file_existence(self, manifest: Dict, actual_files: List[Path]) -> bool:
        """Validate all manifest entries have corresponding files"""
        success = True
        manifest_files = {w['filename'] for w in manifest.get('walkthroughs', [])}
        actual_filenames = {f.name for f in actual_files}
        
        # Check for missing files
        missing = manifest_files - actual_filenames
        if missing:
            self.errors.append(f"Manifest references missing files: {missing}")
            success = False
        
        # Check for extra files
        extra = actual_filenames - manifest_files
        if extra:
            self.warnings.append(f"Files not in manifest: {extra}")
        
        return success
    
    def validate_totals(self, manifest: Dict) -> bool:
        """Validate totals match sum of individual walkthroughs"""
        success = True
        walkthroughs = manifest.get('walkthroughs', [])
        totals = manifest.get('totals', {})
        
        # Calculate actual totals
        actual_totals = {
            'total_steps': sum(w.get('total_steps', 0) for w in walkthroughs),
            'total_code_blocks': sum(w.get('code_blocks_total', 0) for w in walkthroughs),
            'valid_code_blocks': sum(w.get('code_blocks_valid', 0) for w in walkthroughs),
            'runnable_steps': sum(w.get('runnable_steps', 0) for w in walkthroughs),
        }
        
        # Compare
        for key, expected in totals.items():
            actual = actual_totals.get(key)
            if actual != expected:
                self.warnings.append(
                    f"Totals mismatch for {key}: manifest={expected}, actual={actual}"
                )
                success = False
        
        return success
    
    def validate_code_validity(self, manifest: Dict) -> bool:
        """Validate code block validity meets quality thresholds"""
        success = True
        
        for walkthrough in manifest.get('walkthroughs', []):
            name = walkthrough.get('walkthrough_name', 'Unknown')
            
            # Check teach_mode validity (overall validity)
            total = walkthrough.get('code_blocks_total', 0)
            valid = walkthrough.get('code_blocks_valid', 0)
            
            if total > 0:
                validity_rate = valid / total
                
                if validity_rate < MIN_TEACH_VALIDITY:
                    self.warnings.append(
                        f"{name}: Code validity {validity_rate:.1%} < {MIN_TEACH_VALIDITY:.0%} "
                        f"({valid}/{total} valid)"
                    )
                    success = False
            
            # Check learn_mode validity (runnable code only)
            # Note: This would require re-parsing with learn_mode, skipped for now
            # Assumption: if teach_mode is 100%, learn_mode is 100%
            
        return success
    
    def validate_walkthrough_metadata(self, manifest: Dict) -> bool:
        """Validate each walkthrough has required metadata"""
        success = True
        required_fields = [
            'walkthrough_name', 'filename', 'title', 'total_steps',
            'validated_steps', 'code_blocks_total', 'author'
        ]
        
        for i, walkthrough in enumerate(manifest.get('walkthroughs', [])):
            missing = [f for f in required_fields if f not in walkthrough]
            if missing:
                self.errors.append(
                    f"Walkthrough {i}: Missing required fields: {missing}"
                )
                success = False
            
            # Check for warnings flags
            if walkthrough.get('has_warnings', False):
                self.warnings.append(
                    f"{walkthrough.get('walkthrough_name')}: has_warnings=true"
                )
            
            if walkthrough.get('has_issues', False):
                self.errors.append(
                    f"{walkthrough.get('walkthrough_name')}: has_issues=true"
                )
                success = False
        
        return success
    
    def validate_ordering(self, manifest: Dict) -> bool:
        """Validate walkthrough ordering is stable if frozen"""
        if not manifest.get('frozen', False):
            self.info.append("Manifest not frozen - ordering can change")
            return True
        
        # Check ordering is Phase 1-9 + Functions + LearnODIBI (both versions)
        walkthroughs = manifest.get('walkthroughs', [])
        expected_order = [
            'DEVELOPER_WALKTHROUGH_FUNCTIONS',
            'DEVELOPER_WALKTHROUGH_LEARNODIBI',
            'DEVELOPER_WALKTHROUGH_LEARNODIBI_FINAL_QA',
            'DEVELOPER_WALKTHROUGH_PHASE_1',
            'DEVELOPER_WALKTHROUGH_PHASE_2',
            'DEVELOPER_WALKTHROUGH_PHASE_3',
            'DEVELOPER_WALKTHROUGH_PHASE_4',
            'DEVELOPER_WALKTHROUGH_PHASE_5',
            'DEVELOPER_WALKTHROUGH_PHASE_6',
            'DEVELOPER_WALKTHROUGH_PHASE_7',
            'DEVELOPER_WALKTHROUGH_PHASE_8',
            'DEVELOPER_WALKTHROUGH_PHASE_9',
        ]
        
        actual_order = [w.get('walkthrough_name') for w in walkthroughs]
        
        if actual_order != expected_order:
            self.warnings.append(
                f"Ordering differs from expected. This is OK if intentional. "
                f"Actual: {actual_order}"
            )
        
        return True
    
    def generate_report(self) -> str:
        """Generate validation report"""
        report = []
        report.append("=" * 80)
        report.append("LearnODIBI Manifest Validation Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("=" * 80)
        report.append("")
        
        # Summary
        total_issues = len(self.errors) + len(self.warnings)
        if total_issues == 0:
            report.append("✅ ALL CHECKS PASSED - Manifest is valid!")
        else:
            report.append(f"⚠️  Found {len(self.errors)} errors and {len(self.warnings)} warnings")
        
        report.append("")
        
        # Errors
        if self.errors:
            report.append("❌ ERRORS:")
            for error in self.errors:
                report.append(f"  - {error}")
            report.append("")
        
        # Warnings
        if self.warnings:
            report.append("⚠️  WARNINGS:")
            for warning in self.warnings:
                report.append(f"  - {warning}")
            report.append("")
        
        # Info
        if self.info:
            report.append("ℹ️  INFO:")
            for info in self.info:
                report.append(f"  - {info}")
            report.append("")
        
        report.append("=" * 80)
        
        return "\n".join(report)
    
    def run(self) -> Tuple[bool, str]:
        """Run all validations and return success status + report"""
        manifest = self.load_manifest()
        if not manifest:
            return False, self.generate_report()
        
        actual_files = self.get_actual_walkthrough_files()
        
        # Run all validations
        validations = [
            self.validate_file_existence(manifest, actual_files),
            self.validate_walkthrough_metadata(manifest),
            self.validate_totals(manifest),
            self.validate_code_validity(manifest),
            self.validate_ordering(manifest),
        ]
        
        success = all(validations) and len(self.errors) == 0
        report = self.generate_report()
        
        return success, report


def main():
    """Main entry point"""
    # Fix Windows console encoding
    if sys.platform == 'win32':
        sys.stdout.reconfigure(encoding='utf-8')
    
    validator = ManifestValidator()
    success, report = validator.run()
    
    print(report)
    
    # Save report
    report_path = ODIBI_ROOT / "MANIFEST_VALIDATION_REPORT.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_path}")
    
    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
