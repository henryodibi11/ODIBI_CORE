"""
UI Teaching Engine - Core lesson loading and rendering logic
Handles dynamic lesson structure, content rendering, and learning flow
"""

import streamlit as st
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple
from dataclasses import dataclass
from odibi_core.learnodibi_ui.manifest_loader import ManifestLoader
from odibi_core.learnodibi_ui.walkthrough_parser import WalkthroughParser, WalkthroughStep
import json


@dataclass
class LessonMetadata:
    """Metadata for a lesson"""
    lesson_id: str
    title: str
    description: str
    phase: str
    duration: str
    total_steps: int
    difficulty: str
    tags: List[str]


class TeachingEngine:
    """Core engine for teaching and lesson management"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.manifest_loader = ManifestLoader(project_root)
        self.walkthroughs_dir = project_root / "docs" / "walkthroughs"
        self.parser = WalkthroughParser(self.walkthroughs_dir)
    
    def get_all_lessons(self) -> List[LessonMetadata]:
        """Get all available lessons with metadata"""
        lessons = []
        walkthroughs = self.manifest_loader.get_all_walkthroughs()
        
        for wt in walkthroughs:
            # Extract phase from filename
            phase = self._extract_phase(wt['filename'])
            
            # Determine difficulty
            difficulty = self._determine_difficulty(wt)
            
            lesson = LessonMetadata(
                lesson_id=wt['filename'],
                title=wt['title'],
                description=wt.get('audience', ''),
                phase=phase,
                duration=wt.get('duration', 'Unknown'),
                total_steps=wt['total_steps'],
                difficulty=difficulty,
                tags=self._extract_tags(wt)
            )
            lessons.append(lesson)
        
        return lessons
    
    def get_lessons_by_phase(self) -> Dict[str, List[LessonMetadata]]:
        """Get lessons grouped by phase"""
        all_lessons = self.get_all_lessons()
        phases = {}
        
        for lesson in all_lessons:
            if lesson.phase not in phases:
                phases[lesson.phase] = []
            phases[lesson.phase].append(lesson)
        
        return phases
    
    def get_lesson(self, lesson_id: str) -> Optional[Any]:
        """Load and parse a specific lesson"""
        lesson_path = self.walkthroughs_dir / lesson_id
        
        if not lesson_path.exists():
            return None
        
        try:
            walkthrough = self.parser.parse_walkthrough(lesson_path)
            return walkthrough
        except Exception as e:
            st.error(f"Error loading lesson: {e}")
            return None
    
    def get_lesson_navigation_tree(self) -> Dict[str, Any]:
        """
        Build hierarchical navigation tree
        Structure: Phase → Lesson → Steps
        """
        phases = self.get_lessons_by_phase()
        tree = {}
        
        for phase_name, lessons in sorted(phases.items()):
            tree[phase_name] = {
                "title": self._format_phase_title(phase_name),
                "lessons": []
            }
            
            for lesson in lessons:
                tree[phase_name]["lessons"].append({
                    "id": lesson.lesson_id,
                    "title": lesson.title,
                    "steps": lesson.total_steps,
                    "duration": lesson.duration,
                    "difficulty": lesson.difficulty
                })
        
        return tree
    
    def get_next_lesson(self, current_lesson_id: str) -> Optional[LessonMetadata]:
        """Get the next lesson in sequence"""
        all_lessons = self.get_all_lessons()
        
        for i, lesson in enumerate(all_lessons):
            if lesson.lesson_id == current_lesson_id:
                if i < len(all_lessons) - 1:
                    return all_lessons[i + 1]
                break
        
        return None
    
    def get_previous_lesson(self, current_lesson_id: str) -> Optional[LessonMetadata]:
        """Get the previous lesson in sequence"""
        all_lessons = self.get_all_lessons()
        
        for i, lesson in enumerate(all_lessons):
            if lesson.lesson_id == current_lesson_id:
                if i > 0:
                    return all_lessons[i - 1]
                break
        
        return None
    
    def search_lessons(self, query: str) -> List[LessonMetadata]:
        """Search lessons by keyword"""
        query = query.lower()
        all_lessons = self.get_all_lessons()
        
        results = []
        for lesson in all_lessons:
            if (query in lesson.title.lower() or 
                query in lesson.description.lower() or
                any(query in tag.lower() for tag in lesson.tags)):
                results.append(lesson)
        
        return results
    
    def _extract_phase(self, filename: str) -> str:
        """Extract phase from filename"""
        if "PHASE_1" in filename:
            return "Phase 1"
        elif "PHASE_2" in filename:
            return "Phase 2"
        elif "PHASE_3" in filename:
            return "Phase 3"
        elif "PHASE_4" in filename:
            return "Phase 4"
        elif "PHASE_5" in filename:
            return "Phase 5"
        elif "PHASE_6" in filename:
            return "Phase 6"
        elif "PHASE_7" in filename:
            return "Phase 7"
        elif "PHASE_8" in filename:
            return "Phase 8"
        elif "PHASE_9" in filename:
            return "Phase 9"
        elif "FUNCTIONS" in filename:
            return "Functions"
        elif "LEARNODIBI" in filename:
            return "LearnODIBI"
        else:
            return "General"
    
    def _format_phase_title(self, phase: str) -> str:
        """Format phase name for display"""
        phase_titles = {
            "Phase 1": "🔧 Phase 1: Core Architecture",
            "Phase 2": "⚙️ Phase 2: Dual-Engine Support",
            "Phase 3": "📋 Phase 3: Configuration System",
            "Phase 4": "📚 Phase 4: Documentation",
            "Phase 5": "🚀 Phase 5: Parallel Execution",
            "Phase 6": "📡 Phase 6: Streaming Data",
            "Phase 7": "☁️ Phase 7: Cloud Integration",
            "Phase 8": "📊 Phase 8: Observability",
            "Phase 9": "🛠️ Phase 9: SDK & CLI",
            "Functions": "🔍 Functions Library",
            "LearnODIBI": "🎓 LearnODIBI Platform",
            "General": "📖 General Topics"
        }
        return phase_titles.get(phase, phase)
    
    def _determine_difficulty(self, walkthrough: Dict) -> str:
        """Determine difficulty level based on metadata"""
        total_steps = walkthrough.get('total_steps', 0)
        runnable_steps = walkthrough.get('runnable_steps', 0)
        
        # Simple heuristic
        if total_steps <= 10:
            return "Beginner"
        elif total_steps <= 20:
            return "Intermediate"
        else:
            return "Advanced"
    
    def _extract_tags(self, walkthrough: Dict) -> List[str]:
        """Extract relevant tags from walkthrough metadata"""
        tags = []
        
        title = walkthrough.get('title', '').lower()
        audience = walkthrough.get('audience', '').lower()
        
        # Extract from title
        if 'functions' in title:
            tags.append('Functions')
        if 'sdk' in title:
            tags.append('SDK')
        if 'cli' in title:
            tags.append('CLI')
        if 'streaming' in title or 'stream' in title:
            tags.append('Streaming')
        if 'parallel' in title:
            tags.append('Parallel')
        if 'cloud' in title:
            tags.append('Cloud')
        if 'config' in title:
            tags.append('Configuration')
        
        # Extract from audience
        if 'developer' in audience:
            tags.append('Developer')
        if 'beginner' in audience:
            tags.append('Beginner')
        
        return tags if tags else ['General']
    
    def generate_lesson_summary(self, lesson_id: str) -> Dict[str, Any]:
        """Generate comprehensive summary of a lesson"""
        walkthrough = self.get_lesson(lesson_id)
        if not walkthrough:
            return {}
        
        metadata = self.manifest_loader.get_walkthrough(lesson_id)
        
        return {
            "title": walkthrough.title,
            "description": walkthrough.description,
            "total_steps": len(walkthrough.steps),
            "runnable_steps": metadata.get('runnable_steps', 0) if metadata else 0,
            "duration": walkthrough.duration,
            "author": walkthrough.author,
            "code_blocks": metadata.get('code_blocks_total', 0) if metadata else 0,
            "code_coverage": (
                metadata.get('code_blocks_valid', 0) / metadata.get('code_blocks_total', 1) * 100
            ) if metadata and metadata.get('code_blocks_total', 0) > 0 else 100,
            "has_issues": metadata.get('has_issues', False) if metadata else False,
            "last_verified": metadata.get('last_verified', 'Unknown') if metadata else 'Unknown'
        }


class LessonRenderer:
    """Handles rendering of lesson content with proper formatting"""
    
    def __init__(self, colors: Dict[str, str]):
        self.colors = colors
    
    def render_lesson_header(self, lesson: Any) -> None:
        """Render lesson header with metadata"""
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, {self.colors['primary']}22, {self.colors['secondary']}22); 
                    padding: 2rem; border-radius: 12px; margin-bottom: 2rem; border-left: 6px solid {self.colors['primary']};'>
            <h1 style='color: {self.colors['primary']}; margin: 0; font-size: 2.5rem;'>{lesson.title}</h1>
            <p style='color: {self.colors['text_secondary']}; margin-top: 1rem; font-size: 1.1em;'>
                👤 {lesson.author} | ⏱️ {lesson.duration}
            </p>
            <p style='margin-top: 1rem; font-size: 1.05em; line-height: 1.6;'>{lesson.description}</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_step_header(self, step: WalkthroughStep, step_num: int, total_steps: int) -> None:
        """Render step header with progress"""
        st.markdown(f"""
        <div style='background: {self.colors['surface']}; padding: 1.5rem; border-radius: 8px; 
                    border-left: 6px solid {self.colors['primary']}; margin-bottom: 1.5rem;'>
            <div style='display: flex; justify-content: space-between; align-items: center;'>
                <h2 style='color: {self.colors['primary']}; margin: 0;'>
                    Step {step_num}: {step.title}
                </h2>
                <span style='background: {self.colors['primary']}; color: {self.colors['background']}; 
                             padding: 0.5rem 1rem; border-radius: 20px; font-weight: bold;'>
                    {step_num}/{total_steps}
                </span>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_overview_section(self, overview: str) -> None:
        """Render lesson overview section"""
        st.markdown(f"""
        <div style='background: {self.colors['info']}22; padding: 1.5rem; border-radius: 8px; 
                    border-left: 4px solid {self.colors['info']}; margin: 1.5rem 0;'>
            <h3 style='color: {self.colors['info']}; margin-top: 0;'>📋 Overview</h3>
            <div style='line-height: 1.8;'>
                {overview}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_summary_section(self, summary: str) -> None:
        """Render lesson summary section"""
        st.markdown(f"""
        <div style='background: {self.colors['success']}22; padding: 1.5rem; border-radius: 8px; 
                    border-left: 4px solid {self.colors['success']}; margin: 1.5rem 0;'>
            <h3 style='color: {self.colors['success']}; margin-top: 0;'>✅ Summary</h3>
            <div style='line-height: 1.8;'>
                {summary}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def render_step_explanation(self, explanation: str) -> None:
        """Render step explanation"""
        st.markdown("### 📖 Explanation")
        st.markdown(f"""
        <div style='line-height: 1.8; padding: 1rem 0;'>
            {explanation}
        </div>
        """, unsafe_allow_html=True)
    
    def render_empty_state(self, message: str, icon: str = "📚") -> None:
        """Render empty state message"""
        st.markdown(f"""
        <div style='text-align: center; padding: 4rem 2rem; color: {self.colors['text_secondary']};'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>{icon}</div>
            <h3 style='color: {self.colors['text_secondary']};'>{message}</h3>
        </div>
        """, unsafe_allow_html=True)
