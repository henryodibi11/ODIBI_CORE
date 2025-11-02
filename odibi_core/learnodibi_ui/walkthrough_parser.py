"""
Walkthrough Parser - Extract and render engine-aware step-by-step lessons
Supports python[pandas] and python[spark] code fence notation
"""

import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class WalkthroughStep:
    """Represents a single step in a walkthrough"""
    step_number: int
    title: str
    explanation: str
    code: Optional[str]
    language: Optional[str]
    engine: Optional[str]  # "pandas" or "spark"
    is_runnable: bool
    related_files: List[str]
    tags: List[str]
    
    # Support for dual-engine steps
    code_pandas: Optional[str] = None
    code_spark: Optional[str] = None
    
    # Teaching mode support
    is_demo: bool = False  # If True, this is a teaching example (not executed)
    
    # Hierarchical numbering support (Phase 10)
    label: Optional[str] = None  # Hierarchical display label (e.g., "6.3.1")
    heading_type: Optional[str] = None  # "Mission" | "Step" | "Exercise"
    step_id: Optional[str] = None  # Stable unique ID for manifest validation
    source_line: Optional[int] = None  # Line number in source markdown


@dataclass
class Walkthrough:
    """Represents a complete walkthrough document"""
    title: str
    filename: str
    description: str
    author: str
    date: str
    audience: str
    duration: str
    steps: List[WalkthroughStep]
    overview: str


class WalkthroughParser:
    """Parse markdown walkthroughs into structured lessons with engine support"""
    
    def __init__(self, walkthroughs_dir: Path):
        self.walkthroughs_dir = Path(walkthroughs_dir)
        self._cached_walkthroughs: Dict[str, Walkthrough] = {}
    
    def list_walkthroughs(self) -> List[Dict[str, str]]:
        """List all available walkthroughs"""
        walkthroughs = []
        
        for file in self.walkthroughs_dir.glob("DEVELOPER_WALKTHROUGH_*.md"):
            walkthrough = self.parse_walkthrough(file)
            walkthroughs.append({
                "filename": file.name,
                "title": walkthrough.title,
                "description": walkthrough.description,
                "duration": walkthrough.duration
            })
        
        return sorted(walkthroughs, key=lambda x: x["filename"])
    
    def parse_walkthrough(self, filepath: Path) -> Walkthrough:
        """Parse a walkthrough markdown file"""
        if str(filepath) in self._cached_walkthroughs:
            return self._cached_walkthroughs[str(filepath)]
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Auto-convert old-style engine markers to new code fences
        content = self._auto_convert_engine_markers(content)
        
        # Extract metadata
        title = self._extract_title(content)
        metadata = self._extract_metadata(content)
        overview = self._extract_overview(content)
        steps = self._extract_steps(content, filename=filepath.name)
        
        walkthrough = Walkthrough(
            title=title,
            filename=filepath.name,
            description=metadata.get("description", ""),
            author=metadata.get("author", "Unknown"),
            date=metadata.get("date", ""),
            audience=metadata.get("audience", ""),
            duration=metadata.get("duration", ""),
            steps=steps,
            overview=overview
        )
        
        self._cached_walkthroughs[str(filepath)] = walkthrough
        return walkthrough
    
    def _auto_convert_engine_markers(self, content: str) -> str:
        """
        Auto-convert old-style markers to new code-fence standard
        
        Examples:
            # Pandas version → ```python[pandas]
            # Spark version → ```python[spark]
        """
        # Pattern: # Pandas version followed by code block
        pandas_pattern = r'#\s*Pandas\s+version\s*\n```python\n(.*?)```'
        content = re.sub(
            pandas_pattern,
            r'```python[pandas]\n\1```',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        # Pattern: # Spark version followed by code block
        spark_pattern = r'#\s*Spark\s+version\s*\n```python\n(.*?)```'
        content = re.sub(
            spark_pattern,
            r'```python[spark]\n\1```',
            content,
            flags=re.DOTALL | re.IGNORECASE
        )
        
        return content
    
    def _extract_title(self, content: str) -> str:
        """Extract main title from markdown"""
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return match.group(1).strip() if match else "Untitled Walkthrough"
    
    def _extract_metadata(self, content: str) -> Dict[str, str]:
        """Extract metadata from markdown front matter"""
        metadata = {}
        
        # Look for key-value pairs after the title
        patterns = {
            "author": r'\*\*Author\*\*:\s*(.+)',
            "date": r'\*\*Date\*\*:\s*(.+)',
            "audience": r'\*\*Audience\*\*:\s*(.+)',
            "duration": r'\*\*Duration\*\*:\s*(.+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, content)
            if match:
                metadata[key] = match.group(1).strip()
        
        # Extract description from first paragraph after title
        desc_match = re.search(r'#\s+.+\n\n\*\*(.+)\*\*', content)
        if desc_match:
            metadata["description"] = desc_match.group(1).strip()
        
        return metadata
    
    def _extract_overview(self, content: str) -> str:
        """Extract overview section"""
        match = re.search(
            r'##\s+.*Overview.*\n\n((?:(?!##).)+)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        return match.group(1).strip() if match else ""
    
    def _extract_steps(self, content: str, filename: str = "") -> List[WalkthroughStep]:
        """Extract all steps/missions from the walkthrough with hierarchical numbering support"""
        steps = []
        current_mission_label = None
        
        # Find all Mission, Step, or Exercise sections (hierarchical pattern)
        # Supports: "### Step 1:", "### Step 1 -", "### Step 1 Title", etc.
        # More permissive regex to handle colon, dash, or space after number
        mission_pattern = r'###\s+(Mission|Step|Exercise)\s+(\d+(?:\.\d+)*)(?::|[-–]\s*|\s+)\s*(.+?)\n+((?:(?!###).)+)'
        matches = re.finditer(mission_pattern, content, re.DOTALL)
        
        for match in matches:
            step_type, step_num, title, body = match.groups()
            
            # Compute source line for better warnings
            source_line = content[:match.start()].count('\n') + 1
            
            # Build hierarchical label based on parent Mission context
            step_number = len(steps) + 1
            
            # Update mission context
            if step_type == 'Mission':
                current_mission_label = step_num
                step_label = step_num
            elif step_type in ('Step', 'Exercise'):
                if current_mission_label:
                    step_label = f"{current_mission_label}.{step_num}"
                else:
                    step_label = step_num
            else:
                step_label = step_num
            
            # Check if title starts with another number (e.g., "Step 1: 1 Title")
            sub_match = re.match(r'^(\d+(?:\.\d+)*)(?::|[-–]|\s+)\s*(.+)$', title)
            if sub_match:
                # Append additional hierarchy level: "6.3.1"
                step_label = f"{step_label}.{sub_match.group(1)}"
                title = sub_match.group(2).strip()
            
            # Generate stable step_id for manifest validation
            step_id = f"{Path(filename).stem}:{step_label}:{source_line}"
            
            # Extract code blocks with engine awareness
            code_blocks = self._extract_code_blocks(body)
            
            # Separate by engine
            pandas_blocks = [b for b in code_blocks if b['engine'] == 'pandas']
            spark_blocks = [b for b in code_blocks if b['engine'] == 'spark']
            generic_python_blocks = [b for b in code_blocks if b['engine'] is None and b['language'] in ['python', 'py']]
            
            # Determine primary code and engine
            code = None
            language = None
            engine = None
            code_pandas = None
            code_spark = None
            is_runnable = False
            
            if pandas_blocks:
                # Pandas-specific code
                code_pandas = pandas_blocks[0]['code']
                code = code_pandas
                language = 'python'
                engine = 'pandas'
                is_runnable = True
            
            if spark_blocks:
                # Spark-specific code
                code_spark = spark_blocks[0]['code']
                if code is None:
                    code = code_spark
                    language = 'python'
                    engine = 'spark'
                is_runnable = True
            
            if not code and generic_python_blocks:
                # Generic Python (default to pandas)
                code = generic_python_blocks[0]['code']
                language = 'python'
                engine = 'pandas'
                is_runnable = True
            elif not code and code_blocks:
                # Non-Python code
                code = code_blocks[0]['code']
                language = code_blocks[0]['language']
                engine = None
                is_runnable = False
            
            # Extract related files from text
            related_files = re.findall(r'`([a-zA-Z0-9_/]+\.py)`', body)
            
            # Extract explanation (text before first code block)
            if code_blocks:
                first_block_pos = min(b['position'] for b in code_blocks)
                explanation = body[:first_block_pos].strip()
            else:
                explanation = body.strip()
            
            # Clean up explanation (remove excessive whitespace)
            explanation = re.sub(r'\n{3,}', '\n\n', explanation)
            
            # Check if any code block is marked as demo
            is_demo = any(b.get('is_demo', False) for b in code_blocks)
            
            steps.append(WalkthroughStep(
                step_number=step_number,
                title=title.strip(),
                explanation=explanation,
                code=code,
                language=language,
                engine=engine,
                is_runnable=is_runnable and not is_demo,
                related_files=related_files,
                tags=self._extract_tags(body),
                code_pandas=code_pandas,
                code_spark=code_spark,
                is_demo=is_demo,
                label=step_label,
                heading_type=step_type,
                step_id=step_id,
                source_line=source_line
            ))
        
        return steps
    
    def _extract_code_blocks(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract code blocks with engine awareness and teaching mode tags
        
        Supports:
            ```python[pandas]
            ```python[spark]
            ```python[demo]   # Teaching example, not executable
            ```python[skip]   # Skip validation
            ```python
            ```bash
        """
        blocks = []
        
        # Pattern for engine-aware code fences: ```python[engine]
        engine_pattern = r'```(python|py)\[(\w+)\]\n(.*?)```'
        for match in re.finditer(engine_pattern, text, re.DOTALL):
            language = match.group(1)
            tag = match.group(2).lower()
            code = match.group(3).strip()
            
            # Determine if this is a demo/skip block
            is_demo = tag in ['demo', 'skip', 'example', 'teaching']
            # Only set engine if explicitly pandas or spark (not for demo/skip)
            engine = tag if tag in ['pandas', 'spark'] else None
            
            blocks.append({
                'language': language,
                'is_demo': is_demo,
                'engine': engine,
                'code': code,
                'position': match.start()
            })
        
        # Pattern for regular code fences: ```python
        regular_pattern = r'```(\w+)?\n(.*?)```'
        for match in re.finditer(regular_pattern, text, re.DOTALL):
            # Skip if already captured by engine pattern
            if any(b['position'] == match.start() for b in blocks):
                continue
            
            language = match.group(1) or 'text'
            code = match.group(2).strip()
            
            blocks.append({
                'language': language,
                'engine': None,
                'code': code,
                'position': match.start()
            })
        
        return blocks
    
    def _extract_tags(self, text: str) -> List[str]:
        """Extract meaningful tags/concepts from step text"""
        tags = []
        
        # Skip generic/common phrases
        SKIP_TAGS = {
            'Example', 'Create', 'Test', 'Note', 'Important', 'Why', 'What', 'How',
            'Step', 'Mission', 'Checkpoint', 'Setup', 'Build', 'Run', 'Install',
            'Configure', 'Common Mistake', 'Before you begin', 'Next', 'Previous',
            'Remember', 'Tip', 'Warning', 'Error', 'Success', 'Failed', 'Quiz',
            'Question', 'Answer', 'Solution', 'Implementation', 'Details'
        }
        
        # Priority 1: Look for explicit "Key Concepts:" or learning objectives
        concepts_match = re.search(r'(?:Key Concepts?|What You.*Learn|You.*Learn|Concepts Covered|Learning Objectives?):(.+?)(?:\n\n|###|---)', text, re.DOTALL | re.IGNORECASE)
        if concepts_match:
            concepts = re.findall(r'[-*]\s+\*?\*?(.+?)\*?\*?(?:\n|$)', concepts_match.group(1))
            for c in concepts:
                clean = re.sub(r'\[.*?\]|\(.*?\)|`', '', c).strip().rstrip(':,.')
                if clean and clean not in SKIP_TAGS and 5 < len(clean) < 60:
                    tags.append(clean)
        
        # Priority 1b: Extract from "Why" or "What depends" sections (common in walkthroughs)
        if len(tags) < 3:
            why_sections = re.findall(r'\*\*(?:Why|What depends on this|What you.*learn)\*\*:?\s*\n((?:[-*].*\n?)+)', text, re.IGNORECASE)
            for section in why_sections:
                bullets = re.findall(r'[-*]\s+(.+)', section)
                for bullet in bullets[:2]:
                    clean = re.sub(r'[`\[\]\(\)]', '', bullet).strip()
                    # Extract first meaningful noun phrase
                    if clean and 10 < len(clean) < 70:
                        tags.append(clean)
                        if len(tags) >= 5:
                            break
        
        # Priority 1c: Extract file/class names from "Create:" markers
        if len(tags) < 3:
            create_match = re.search(r'\*\*Create\*\*:?\s+`?([A-Za-z0-9_./]+)`?', text)
            if create_match:
                filename = create_match.group(1)
                # Extract meaningful part (e.g., "NodeBase" from "core/node_base.py")
                parts = filename.replace('.py', '').replace('_', ' ').split('/')
                for part in reversed(parts):
                    if part and part.lower() not in ['core', 'engine', 'node', 'config', 'init']:
                        tags.append(part.title())
                        break
        
        # Priority 2: Technical file types and technologies from title/content
        if len(tags) < 3:
            tech_indicators = re.findall(r'(?:pyproject\.toml|\.gitignore|pytest\.ini|requirements\.txt|Dockerfile|__init__\.py)', text.lower())
            tech_names = {
                'pyproject.toml': 'Python Project Config',
                '.gitignore': 'Git Version Control',
                'pytest.ini': 'Test Configuration',
                'requirements.txt': 'Dependencies',
                'dockerfile': 'Docker Container',
                '__init__.py': 'Python Package'
            }
            for indicator in set(tech_indicators[:2]):
                if indicator in tech_names:
                    tags.append(tech_names[indicator])
        
        # Priority 3: Bold terms (filter generic words)
        if len(tags) < 5:
            bold_terms = re.findall(r'\*\*([A-Z][a-zA-Z\s]+)\*\*', text)
            for term in bold_terms:
                term_clean = term.strip()
                if term_clean not in SKIP_TAGS and 5 < len(term_clean) < 40:
                    tags.append(term_clean)
        
        # Priority 3: PascalCase class/function names from code blocks
        if len(tags) < 5:
            code_names = re.findall(r'`([A-Z][a-zA-Z0-9_]+(?:Node|Engine|Context|Manager|Factory|Provider|Reader|Writer|Transformer|Config|Base|Interface))`', text)
            tags.extend(code_names)
        
        # Priority 4: Key Python/technical terms
        if len(tags) < 5:
            tech_terms = re.findall(r'`(pandas|spark|dataframe|DataFrame|sql|SQL|schema|Schema|pipeline|Pipeline|config|Config)`', text)
            tags.extend([t.capitalize() if t.islower() else t for t in tech_terms])
        
        # Deduplicate and limit
        seen = set()
        unique_tags = []
        for tag in tags:
            tag_clean = tag.strip()
            if (tag_clean and tag_clean.lower() not in [s.lower() for s in SKIP_TAGS] 
                and tag_clean not in seen and len(tag_clean) > 3):
                seen.add(tag_clean)
                unique_tags.append(tag_clean)
                if len(unique_tags) >= 8:
                    break
        
        return unique_tags
    
    def get_step_code_for_engine(self, step: WalkthroughStep, engine: str) -> Optional[str]:
        """
        Get code for specific engine from a step
        
        Args:
            step: WalkthroughStep instance
            engine: "pandas" or "spark"
            
        Returns:
            Code string or None
        """
        engine = engine.lower()
        
        if engine == "pandas" and step.code_pandas:
            return step.code_pandas
        elif engine == "spark" and step.code_spark:
            return step.code_spark
        elif step.engine == engine:
            return step.code
        elif step.engine is None and step.is_runnable:
            # Generic Python, default to pandas
            return step.code
        
        return None


def get_walkthrough_parser(odibi_root: Path = None) -> WalkthroughParser:
    """Get walkthrough parser instance"""
    if odibi_root is None:
        odibi_root = Path(__file__).parent.parent.parent
    
    walkthroughs_dir = odibi_root / "docs" / "walkthroughs"
    return WalkthroughParser(walkthroughs_dir)
