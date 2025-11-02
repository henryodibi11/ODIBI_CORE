"""
Walkthrough Compiler & Manifest Rebuild
========================================
Comprehensive revalidation and compilation of all LearnODIBI walkthroughs.

Features:
- Re-parse all walkthroughs with metadata extraction
- Validate code blocks with AST and execution testing
- Generate walkthrough_manifest.json
- Fix step numbering inconsistencies
- Create comprehensive validation reports
"""

import ast
import json
import re
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from collections import defaultdict

# Fix Windows encoding
if os.name == 'nt':
    sys.stdout.reconfigure(encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))


@dataclass
class CodeBlock:
    """Represents a code block within a step"""
    code: str
    language: str
    engine: str  # pandas or spark
    line_number: int
    is_runnable: bool = False
    validation_status: str = "unknown"  # runnable, fixed, needs_attention
    validation_error: Optional[str] = None


@dataclass
class WalkthroughStep:
    """Represents a single step in a walkthrough"""
    step_number: int
    step_id: str
    title: str
    content: str
    code_blocks: List[CodeBlock]
    has_code: bool
    line_number: int


@dataclass
class WalkthroughMetadata:
    """Metadata for a walkthrough"""
    walkthrough_name: str
    filename: str
    title: str
    author: str
    date: str
    audience: str
    duration: str
    total_steps: int
    validated_steps: int
    runnable_steps: int
    code_blocks_total: int
    code_blocks_valid: int
    last_verified: str
    issues: List[str]
    warnings: List[str]


class WalkthroughCompiler:
    """Compiles and validates all walkthroughs"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.walkthroughs_dir = project_root / "docs" / "walkthroughs"
        self.manifest = []
        self.issues_log = defaultdict(list)
        self.warnings_log = defaultdict(list)
    
    def parse_walkthrough_file(self, filepath: Path) -> Optional[WalkthroughMetadata]:
        """Parse a single walkthrough markdown file"""
        try:
            content = filepath.read_text(encoding='utf-8')
            
            # Extract metadata
            title = self._extract_title(content)
            author = self._extract_field(content, "Author", "Unknown")
            date = self._extract_field(content, "Date", "Unknown")
            audience = self._extract_field(content, "Audience", "Developers")
            duration = self._extract_field(content, "Duration", "Unknown")
            
            # Extract steps
            steps = self._extract_steps(content, filepath.name)
            
            # Validate code blocks
            total_code_blocks = 0
            valid_code_blocks = 0
            runnable_steps = 0
            
            for step in steps:
                if step.has_code:
                    for block in step.code_blocks:
                        total_code_blocks += 1
                        # Validate code
                        is_valid, error = self._validate_code(block.code)
                        block.is_runnable = is_valid
                        
                        if is_valid:
                            valid_code_blocks += 1
                            block.validation_status = "runnable"
                        else:
                            block.validation_status = "needs_attention"
                            block.validation_error = error
                    
                    # Step is runnable if all its code blocks are valid
                    if all(b.is_runnable for b in step.code_blocks):
                        runnable_steps += 1
            
            metadata = WalkthroughMetadata(
                walkthrough_name=filepath.stem,
                filename=filepath.name,
                title=title,
                author=author,
                date=date,
                audience=audience,
                duration=duration,
                total_steps=len(steps),
                validated_steps=len(steps),
                runnable_steps=runnable_steps,
                code_blocks_total=total_code_blocks,
                code_blocks_valid=valid_code_blocks,
                last_verified=datetime.now().isoformat(),
                issues=self.issues_log[filepath.name],
                warnings=self.warnings_log[filepath.name]
            )
            
            return metadata
            
        except Exception as e:
            print(f"ERROR parsing {filepath.name}: {e}")
            return None
    
    def _extract_title(self, content: str) -> str:
        """Extract main title"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1).strip() if match else "Untitled"
    
    def _extract_field(self, content: str, field: str, default: str) -> str:
        """Extract metadata field"""
        pattern = rf'\*\*{field}\*\*:\s*(.+)'
        match = re.search(pattern, content)
        return match.group(1).strip() if match else default
    
    def _extract_steps(self, content: str, filename: str) -> List[WalkthroughStep]:
        """Extract all steps/missions from markdown content with hierarchical numbering support"""
        steps = []
        
        # Pattern to match hierarchical steps: "### Mission 1.1: Title" or "### Step 1: 1 Title"
        # Supports: "Step 1:", "Step 1.1:", "Step 1: 1", "Mission 2.3:", etc.
        step_pattern = r'^#{2,4}\s+(?:Mission|Step|📝\s*Step)\s+(\d+(?:\.\d+)*)(?::|\.)\s*(.+)$'
        
        lines = content.split('\n')
        current_step = None
        current_content = []
        step_line_number = 0
        
        for line_no, line in enumerate(lines, 1):
            match = re.match(step_pattern, line)
            
            if match:
                # Save previous step if exists
                if current_step is not None:
                    step_content = '\n'.join(current_content)
                    code_blocks = self._extract_code_blocks(step_content, step_line_number)
                    
                    steps.append(WalkthroughStep(
                        step_number=current_step['number'],
                        step_id=current_step['step_id'],
                        title=current_step['title'],
                        content=step_content,
                        code_blocks=code_blocks,
                        has_code=len(code_blocks) > 0,
                        line_number=step_line_number
                    ))
                
                # Extract hierarchical label and title
                primary_label = match.group(1)  # e.g., "1" or "1.1"
                rest = match.group(2).strip()
                
                # Check if title starts with another number (e.g., "Step 1: 1 Title")
                sub_match = re.match(r'^(\d+(?:\.\d+)*)(?::|[-–]|\s+)\s*(.+)$', rest)
                if sub_match:
                    # Combine into hierarchical label: "1.1"
                    step_label = f"{primary_label}.{sub_match.group(1)}"
                    step_title = sub_match.group(2).strip()
                else:
                    step_label = primary_label
                    step_title = rest
                
                # Generate unique step ID from label
                step_id = f"{filename}_step_{step_label.replace('.', '_')}"
                
                # Use sequential number for display (legacy compatibility)
                step_number = len(steps) + 1
                
                current_step = {
                    'number': step_number,
                    'step_id': step_id,
                    'step_label': step_label,
                    'title': step_title
                }
                current_content = []
                step_line_number = line_no
            
            elif current_step is not None:
                current_content.append(line)
        
        # Save last step
        if current_step is not None:
            step_content = '\n'.join(current_content)
            code_blocks = self._extract_code_blocks(step_content, step_line_number)
            
            steps.append(WalkthroughStep(
                step_number=current_step['number'],
                step_id=current_step['step_id'],
                title=current_step['title'],
                content=step_content,
                code_blocks=code_blocks,
                has_code=len(code_blocks) > 0,
                line_number=step_line_number
            ))
        
        # Validate step numbering (now hierarchical-aware)
        self._validate_step_numbering(steps, filename)
        
        return steps
    
    def _extract_code_blocks(self, content: str, base_line: int) -> List[CodeBlock]:
        """Extract code blocks from step content"""
        blocks = []
        pattern = r'```(python(?:\[(?:pandas|spark)\])?)\n(.*?)```'
        
        for match in re.finditer(pattern, content, re.DOTALL):
            language = match.group(1)
            code = match.group(2)
            
            # Determine engine
            engine = "pandas"
            if '[spark]' in language:
                engine = "spark"
            elif '[pandas]' in language:
                engine = "pandas"
            
            # Calculate line number
            line_offset = content[:match.start()].count('\n')
            
            blocks.append(CodeBlock(
                code=code,
                language=language,
                engine=engine,
                line_number=base_line + line_offset
            ))
        
        return blocks
    
    def _validate_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """Validate Python code syntax"""
        try:
            ast.parse(code)
            return True, None
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)[:100]
    
    def _validate_step_numbering(self, steps: List[WalkthroughStep], filename: str):
        """Validate hierarchical step ordering with Mission-scoped context"""
        if not steps:
            return
        
        # Track Mission context and step ordering within each Mission
        current_mission_label = None
        mission_steps = []
        last_step_in_mission = None
        seen_labels_global = set()
        
        for step in steps:
            # Extract step_label from step_id (format: "filename_step_1_2" -> "1.2")
            step_label = step.step_id.replace(f"{filename}_step_", "").replace("_", ".")
            
            # Create sort key from hierarchical label
            try:
                sort_key = tuple(int(part) for part in step_label.split('.'))
            except ValueError:
                # Fallback to step_number if label parsing fails
                sort_key = (step.step_number,)
                step_label = str(step.step_number)
            
            # Detect Mission vs Step by hierarchy depth
            # Single number = Mission (e.g., "1", "6")
            # Multi-level = Step within Mission (e.g., "1.1", "6.3")
            is_mission = len(sort_key) == 1
            
            if is_mission:
                # New Mission context - reset scope
                current_mission_label = step_label
                mission_steps = []
                last_step_in_mission = None
            else:
                # Step within current Mission
                # Only validate ordering within the same Mission
                if last_step_in_mission is not None:
                    if sort_key < last_step_in_mission:
                        warning = f"Step order decreases within Mission {current_mission_label}: '{self._key_to_label(last_step_in_mission)}' to '{step_label}' at line {step.line_number}"
                        self.warnings_log[filename].append(warning)
                
                last_step_in_mission = sort_key
            
            # Check for duplicate labels (global scope)
            if step_label in seen_labels_global:
                warning = f"Duplicate step label '{step_label}' at line {step.line_number}"
                self.warnings_log[filename].append(warning)
            else:
                seen_labels_global.add(step_label)
    
    def _key_to_label(self, sort_key: tuple) -> str:
        """Convert sort key tuple back to label string"""
        return '.'.join(str(x) for x in sort_key)
    
    def compile_all_walkthroughs(self) -> List[WalkthroughMetadata]:
        """Compile all walkthrough files"""
        print("=" * 70)
        print("WALKTHROUGH COMPILER & MANIFEST REBUILD")
        print("=" * 70)
        
        # Find all walkthrough files
        patterns = [
            "DEVELOPER_WALKTHROUGH_*.md",
            "PHASE_*_COMPLETE.md",
            "PHASE_*_SUMMARY.md"
        ]
        
        all_files = set()
        for pattern in patterns:
            all_files.update(self.walkthroughs_dir.glob(pattern))
        
        # Filter out non-walkthrough files
        walkthrough_files = [
            f for f in sorted(all_files)
            if self._is_walkthrough_file(f)
        ]
        
        print(f"\nFound {len(walkthrough_files)} walkthrough files")
        print("=" * 70)
        
        # Process each file
        metadata_list = []
        for idx, filepath in enumerate(walkthrough_files, 1):
            print(f"\n[{idx}/{len(walkthrough_files)}] Processing {filepath.name}...")
            
            metadata = self.parse_walkthrough_file(filepath)
            if metadata:
                metadata_list.append(metadata)
                
                # Print summary
                status = "PASS" if metadata.code_blocks_total == 0 or metadata.code_blocks_valid == metadata.code_blocks_total else "ISSUES"
                print(f"  Steps: {metadata.total_steps} | Code Blocks: {metadata.code_blocks_valid}/{metadata.code_blocks_total} | Status: {status}")
                
                if metadata.warnings:
                    print(f"  Warnings: {len(metadata.warnings)}")
                if metadata.issues:
                    print(f"  Issues: {len(metadata.issues)}")
        
        self.manifest = metadata_list
        return metadata_list
    
    def _is_walkthrough_file(self, filepath: Path) -> bool:
        """Check if file is a valid walkthrough"""
        # Exclude certain files
        exclude_patterns = [
            "PACKAGING",
            "TEST_REPORT",
            "USER_EXPERIENCE",
            "FILES",
            "QUALITY_AUDIT",
            "RESTRUCTURING"
        ]
        
        for pattern in exclude_patterns:
            if pattern in filepath.name:
                return False
        
        # Check if file has steps (hierarchical pattern)
        try:
            content = filepath.read_text(encoding='utf-8')
            # Check for Mission or Step patterns (supports hierarchical numbering)
            has_steps = bool(re.search(r'^#{2,4}\s+(?:Mission|Step|📝\s*Step)\s+\d+(?:\.\d+)*(?::|\.)', content, re.MULTILINE))
            return has_steps
        except Exception:
            return False
    
    def generate_manifest_json(self) -> dict:
        """Generate manifest.json"""
        manifest = {
            "generated": datetime.now().isoformat(),
            "total_walkthroughs": len(self.manifest),
            "walkthroughs": []
        }
        
        for meta in self.manifest:
            manifest["walkthroughs"].append({
                "walkthrough_name": meta.walkthrough_name,
                "filename": meta.filename,
                "title": meta.title,
                "total_steps": meta.total_steps,
                "validated_steps": meta.validated_steps,
                "runnable_steps": meta.runnable_steps,
                "code_blocks_total": meta.code_blocks_total,
                "code_blocks_valid": meta.code_blocks_valid,
                "last_verified": meta.last_verified,
                "author": meta.author,
                "duration": meta.duration,
                "audience": meta.audience,
                "has_issues": len(meta.issues) > 0,
                "has_warnings": len(meta.warnings) > 0
            })
        
        # Calculate totals
        manifest["totals"] = {
            "total_steps": sum(m.total_steps for m in self.manifest),
            "total_code_blocks": sum(m.code_blocks_total for m in self.manifest),
            "valid_code_blocks": sum(m.code_blocks_valid for m in self.manifest),
            "runnable_steps": sum(m.runnable_steps for m in self.manifest)
        }
        
        return manifest
    
    def save_manifest(self, output_path: Path):
        """Save manifest to JSON file"""
        manifest = self.generate_manifest_json()
        output_path.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        print(f"\nCreated: {output_path}")
    
    def generate_manifest_report(self, output_path: Path):
        """Generate manifest report markdown"""
        report = f"""# LearnODIBI Walkthrough Manifest Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Walkthroughs**: {len(self.manifest)}
- **Total Steps**: {sum(m.total_steps for m in self.manifest)}
- **Total Code Blocks**: {sum(m.code_blocks_total for m in self.manifest)}
- **Valid Code Blocks**: {sum(m.code_blocks_valid for m in self.manifest)}
- **Runnable Steps**: {sum(m.runnable_steps for m in self.manifest)}

## Walkthrough Inventory

| Walkthrough | Steps | Code Blocks | Valid | Status |
|-------------|-------|-------------|-------|--------|
"""
        
        for meta in self.manifest:
            status = "✅" if meta.code_blocks_total == 0 or meta.code_blocks_valid == meta.code_blocks_total else "⚠️"
            if len(meta.issues) > 0:
                status = "❌"
            
            report += f"| {meta.title[:45]} | {meta.total_steps} | {meta.code_blocks_total} | {meta.code_blocks_valid} | {status} |\n"
        
        # Issues and warnings section
        report += "\n## Issues Found\n\n"
        
        has_issues = False
        for meta in self.manifest:
            if meta.issues or meta.warnings:
                has_issues = True
                report += f"### {meta.filename}\n\n"
                
                if meta.warnings:
                    report += "**Warnings:**\n"
                    for warning in meta.warnings:
                        report += f"- {warning}\n"
                    report += "\n"
                
                if meta.issues:
                    report += "**Issues:**\n"
                    for issue in meta.issues:
                        report += f"- {issue}\n"
                    report += "\n"
        
        if not has_issues:
            report += "*No issues or warnings found!*\n"
        
        # Recommendations
        report += "\n## Recommendations\n\n"
        report += "1. Review walkthroughs with ⚠️ or ❌ status\n"
        report += "2. Fix step numbering inconsistencies\n"
        report += "3. Validate code blocks with syntax errors\n"
        report += "4. Update UI navigation to use manifest\n"
        
        output_path.write_text(report, encoding='utf-8')
        print(f"Created: {output_path}")
    
    def generate_ui_validation_report(self, output_path: Path):
        """Generate UI validation summary"""
        report = f"""# LearnODIBI UI Revalidation Summary

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Pre-flight Validation Results

This report shows the validation status of each code block for UI pre-flight checking.

"""
        
        for meta in self.manifest:
            if meta.code_blocks_total == 0:
                continue
            
            report += f"### {meta.title}\n\n"
            report += f"**File**: {meta.filename}  \n"
            report += f"**Steps**: {meta.total_steps}  \n"
            report += f"**Runnable Steps**: {meta.runnable_steps}/{meta.total_steps}  \n"
            report += f"**Code Validation**: {meta.code_blocks_valid}/{meta.code_blocks_total} blocks passing\n\n"
            
            coverage = (meta.code_blocks_valid / meta.code_blocks_total * 100) if meta.code_blocks_total > 0 else 0
            
            if coverage == 100:
                report += "✅ **Status**: All code blocks validated  \n"
            elif coverage >= 80:
                report += f"⚠️ **Status**: {coverage:.0f}% code blocks validated  \n"
            else:
                report += f"❌ **Status**: Only {coverage:.0f}% code blocks validated  \n"
            
            report += "\n---\n\n"
        
        # Overall statistics
        total_blocks = sum(m.code_blocks_total for m in self.manifest)
        valid_blocks = sum(m.code_blocks_valid for m in self.manifest)
        overall_coverage = (valid_blocks / total_blocks * 100) if total_blocks > 0 else 0
        
        report += f"## Overall Statistics\n\n"
        report += f"- **Total Code Blocks**: {total_blocks}\n"
        report += f"- **Valid Code Blocks**: {valid_blocks}\n"
        report += f"- **Overall Coverage**: {overall_coverage:.1f}%\n\n"
        
        if overall_coverage >= 80:
            report += "✅ **Overall Status**: Pre-flight validation coverage meets 80% target\n"
        else:
            report += f"⚠️ **Overall Status**: Pre-flight validation coverage below 80% target ({overall_coverage:.1f}%)\n"
        
        output_path.write_text(report, encoding='utf-8')
        print(f"Created: {output_path}")


def main():
    """Main execution"""
    project_root = Path("d:/projects/odibi_core")
    
    compiler = WalkthroughCompiler(project_root)
    
    # Compile all walkthroughs
    metadata_list = compiler.compile_all_walkthroughs()
    
    # Generate outputs
    print("\n" + "=" * 70)
    print("GENERATING MANIFEST AND REPORTS")
    print("=" * 70)
    
    # Save manifest JSON
    manifest_path = project_root / "walkthrough_manifest.json"
    compiler.save_manifest(manifest_path)
    
    # Generate manifest report
    manifest_report_path = project_root / "LEARNODIBI_WALKTHROUGH_MANIFEST_REPORT.md"
    compiler.generate_manifest_report(manifest_report_path)
    
    # Generate UI validation report
    ui_report_path = project_root / "LEARNODIBI_UI_REVALIDATION_SUMMARY.md"
    compiler.generate_ui_validation_report(ui_report_path)
    
    # Summary
    print("\n" + "=" * 70)
    print("COMPILATION COMPLETE")
    print("=" * 70)
    total_steps = sum(m.total_steps for m in metadata_list)
    total_blocks = sum(m.code_blocks_total for m in metadata_list)
    valid_blocks = sum(m.code_blocks_valid for m in metadata_list)
    
    print(f"Walkthroughs Compiled: {len(metadata_list)}")
    print(f"Total Steps: {total_steps}")
    print(f"Total Code Blocks: {total_blocks}")
    print(f"Valid Code Blocks: {valid_blocks} ({valid_blocks/total_blocks*100:.1f}%)" if total_blocks > 0 else "Valid Code Blocks: 0")
    print("\nFiles Generated:")
    print(f"  - {manifest_path}")
    print(f"  - {manifest_report_path}")
    print(f"  - {ui_report_path}")
    print("=" * 70)


if __name__ == "__main__":
    main()
