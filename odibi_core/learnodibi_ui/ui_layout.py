"""
UI Layout - Layout and navigation components for LearnODIBI Studio
Handles all UI layout, navigation tree, and structural elements
"""

import streamlit as st
from typing import Dict, List, Optional, Any, Callable
from pathlib import Path


class NavigationTree:
    """Handles hierarchical lesson navigation"""
    
    def __init__(self, tree_data: Dict[str, Any], colors: Dict[str, str]):
        self.tree_data = tree_data
        self.colors = colors
    
    def render(self, on_lesson_select: Callable[[str], None]) -> None:
        """
        Render the navigation tree
        
        Args:
            on_lesson_select: Callback function when lesson is selected
        """
        st.markdown("### 🗺️ Learning Path")
        
        for phase_key, phase_data in sorted(self.tree_data.items()):
            phase_title = phase_data["title"]
            lessons = phase_data["lessons"]
            
            with st.expander(phase_title, expanded=False):
                for lesson in lessons:
                    # Difficulty badge
                    diff_colors = {
                        "Beginner": "#4CAF50",
                        "Intermediate": "#F5B400",
                        "Advanced": "#F44336"
                    }
                    diff_color = diff_colors.get(lesson["difficulty"], "#9E9E9E")
                    
                    # Lesson button
                    lesson_key = f"nav_{lesson['id']}"
                    
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        if st.button(
                            lesson["title"],
                            key=lesson_key,
                            use_container_width=True,
                            help=f"{lesson['steps']} steps • {lesson['duration']}"
                        ):
                            on_lesson_select(lesson["id"])
                    
                    with col2:
                        st.markdown(f"""
                        <div style='background: {diff_color}; color: white; 
                                    padding: 0.3rem 0.5rem; border-radius: 4px; 
                                    text-align: center; font-size: 0.75em; font-weight: bold;'>
                            {lesson['difficulty'][0]}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # Metadata
                    st.caption(f"📊 {lesson['steps']} steps • ⏱️ {lesson['duration']}")


class LessonNavigation:
    """Handles lesson-level navigation (Previous/Next buttons, progress bar)"""
    
    def __init__(self, colors: Dict[str, str]):
        self.colors = colors
    
    def render_step_navigator(
        self,
        current_step: int,
        total_steps: int,
        on_first: Callable,
        on_previous: Callable,
        on_next: Callable,
        on_last: Callable,
        location: str = "top"
    ) -> None:
        """Render step navigation controls"""
        col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
        
        with col1:
            if st.button(
                "⏮️ First",
                disabled=(current_step == 0),
                key=f"first_{location}",
                use_container_width=True
            ):
                on_first()
        
        with col2:
            if st.button(
                "⬅️ Previous",
                disabled=(current_step == 0),
                key=f"prev_{location}",
                use_container_width=True
            ):
                on_previous()
        
        with col3:
            # Progress bar
            progress = (current_step + 1) / total_steps if total_steps > 0 else 0
            st.progress(progress, text=f"Step {current_step + 1} of {total_steps}")
        
        with col4:
            if st.button(
                "Next ➡️",
                disabled=(current_step >= total_steps - 1),
                key=f"next_{location}",
                use_container_width=True
            ):
                on_next()
        
        with col5:
            if st.button(
                "Last ⏭️",
                disabled=(current_step >= total_steps - 1),
                key=f"last_{location}",
                use_container_width=True
            ):
                on_last()
    
    def render_lesson_navigator(
        self,
        prev_lesson: Optional[Any],
        next_lesson: Optional[Any],
        on_prev_lesson: Callable,
        on_next_lesson: Callable
    ) -> None:
        """Render lesson-to-lesson navigation"""
        st.markdown("---")
        st.markdown("### 📚 Navigate Lessons")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if prev_lesson:
                if st.button(
                    f"⬅️ Previous: {prev_lesson.title[:40]}...",
                    key="prev_lesson_btn",
                    use_container_width=True
                ):
                    on_prev_lesson()
            else:
                st.button(
                    "⬅️ No Previous Lesson",
                    key="prev_lesson_btn_disabled",
                    disabled=True,
                    use_container_width=True
                )
        
        with col2:
            if next_lesson:
                if st.button(
                    f"Next: {next_lesson.title[:40]}... ➡️",
                    key="next_lesson_btn",
                    use_container_width=True
                ):
                    on_next_lesson()
            else:
                st.button(
                    "No Next Lesson ➡️",
                    key="next_lesson_btn_disabled",
                    disabled=True,
                    use_container_width=True
                )


class SidebarLayout:
    """Manages sidebar layout and controls"""
    
    def __init__(self, colors: Dict[str, str]):
        self.colors = colors
    
    def render_header(self) -> None:
        """Render sidebar header"""
        st.markdown(f"""
        <div style='text-align: center; padding: 1.5rem 1rem; 
                    background: linear-gradient(135deg, {self.colors['primary']}22, {self.colors['secondary']}22); 
                    border-radius: 12px; margin-bottom: 1rem;'>
            <div style='font-size: 3rem; margin-bottom: 0.5rem;'>🎓</div>
            <h1 style='color: {self.colors['primary']}; margin: 0; font-size: 1.8rem;'>LearnODIBI</h1>
            <h3 style='color: {self.colors['secondary']}; margin: 0.5rem 0 0 0; font-size: 1.2rem;'>Studio</h3>
            <p style='color: {self.colors['text_secondary']}; font-size: 0.9em; margin: 0.5rem 0 0 0;'>
                Self-Guided Learning Platform
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_mode_selector(self, current_mode: str, on_mode_change: Callable[[str], None]) -> None:
        """Render learning mode selector"""
        st.markdown("### 🎯 Learning Mode")
        
        # Explain the difference
        st.markdown(f"""
        <div style='font-size: 0.85em; color: #C0C0C0; margin-bottom: 0.5rem;'>
            <strong>Guided:</strong> Follow lessons 1→11 in order<br/>
            <strong>Explore:</strong> Pick any lesson with filters
        </div>
        """, unsafe_allow_html=True)
        
        mode = st.radio(
            "Choose your path:",
            options=["guided", "explore"],
            format_func=lambda x: "🛤️ Guided Course (Linear)" if x == "guided" else "🔍 Explore (Your Choice)",
            index=0 if current_mode == "guided" else 1,
            key="learning_mode_selector",
            help="Guided: Step-by-step through all lessons\nExplore: Filter and select specific topics"
        )
        
        if mode != current_mode:
            on_mode_change(mode)
    
    def render_theme_toggle(self, current_theme: str, on_theme_change: Callable[[str], None]) -> None:
        """Render theme toggle"""
        st.markdown("### 🎨 Theme")
        
        theme = st.radio(
            "Visual style:",
            options=["light", "dark"],
            format_func=lambda x: "☀️ Light Mode" if x == "light" else "🌙 Dark Mode",
            index=0 if current_theme == "light" else 1,
            key="theme_selector"
        )
        
        if theme != current_theme:
            on_theme_change(theme)
    
    def render_progress_summary(self, completed: int, total: int, badges: List[str]) -> None:
        """Render progress summary"""
        st.markdown("### 📊 Your Progress")
        
        percentage = (completed / total * 100) if total > 0 else 0
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Lessons", f"{completed}/{total}")
        with col2:
            st.metric("Progress", f"{percentage:.0f}%")
        
        st.progress(percentage / 100)
        
        # Badges
        if badges:
            st.markdown("### 🏆 Badges Earned")
            badge_display = " ".join([f"🎖️" for _ in badges[:5]])
            st.markdown(f"<div style='text-align: center; font-size: 1.5rem;'>{badge_display}</div>", unsafe_allow_html=True)
            st.caption(f"{len(badges)} badge(s) earned")


class HomeScreen:
    """Renders the home/landing screen"""
    
    def __init__(self, colors: Dict[str, str]):
        self.colors = colors
    
    def render(
        self,
        on_start_guided: Callable,
        on_explore_lessons: Callable,
        on_view_progress: Callable
    ) -> None:
        """Render home screen"""
        # Hero section
        st.markdown(f"""
        <div style='text-align: center; padding: 3rem 2rem; 
                    background: linear-gradient(135deg, {self.colors['primary']}33, {self.colors['secondary']}33); 
                    border-radius: 16px; margin-bottom: 2rem;'>
            <div style='font-size: 5rem; margin-bottom: 1rem;'>🎓</div>
            <h1 style='color: {self.colors['primary']}; font-size: 3rem; margin: 0;'>LearnODIBI Studio</h1>
            <p style='font-size: 1.3em; color: {self.colors['text_secondary']}; margin-top: 1rem;'>
                Master ODIBI CORE through interactive, self-guided learning
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        st.markdown("### 🚀 Get Started")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            <div style='background: {self.colors['surface']}; padding: 2rem; 
                        border-radius: 12px; text-align: center; height: 100%; 
                        border: 2px solid {self.colors['primary']}22;'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>🛤️</div>
                <h3 style='color: {self.colors['primary']};'>Guided Course</h3>
                <p style='color: {self.colors['text_secondary']}; margin-bottom: 1.5rem;'>
                    Follow a structured learning path from beginner to advanced
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Start Guided Course", key="btn_guided", use_container_width=True, type="primary"):
                on_start_guided()
        
        with col2:
            st.markdown(f"""
            <div style='background: {self.colors['surface']}; padding: 2rem; 
                        border-radius: 12px; text-align: center; height: 100%; 
                        border: 2px solid {self.colors['secondary']}22;'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>🔍</div>
                <h3 style='color: {self.colors['secondary']};'>Explore Lessons</h3>
                <p style='color: {self.colors['text_secondary']}; margin-bottom: 1.5rem;'>
                    Jump to any topic and learn at your own pace
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("Explore Lessons", key="btn_explore", use_container_width=True):
                on_explore_lessons()
        
        with col3:
            st.markdown(f"""
            <div style='background: {self.colors['surface']}; padding: 2rem; 
                        border-radius: 12px; text-align: center; height: 100%; 
                        border: 2px solid {self.colors['info']}22;'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>📊</div>
                <h3 style='color: {self.colors['info']};'>My Progress</h3>
                <p style='color: {self.colors['text_secondary']}; margin-bottom: 1.5rem;'>
                    View your learning journey and achievements
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("View Progress", key="btn_progress", use_container_width=True):
                on_view_progress()
        
        # Features section
        st.markdown("---")
        st.markdown("### ✨ What You'll Learn")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div style='background: {self.colors['surface']}; padding: 1.5rem; 
                        border-radius: 8px; margin-bottom: 1rem;'>
                <h4 style='color: {self.colors['primary']}; margin-top: 0;'>🧠 Core Concepts</h4>
                <ul style='line-height: 1.8;'>
                    <li>5 Canonical Node Types</li>
                    <li>Dual-Engine Architecture (Pandas + Spark)</li>
                    <li>Medallion Pattern (Bronze → Silver → Gold)</li>
                    <li>Configuration-Driven Development</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div style='background: {self.colors['surface']}; padding: 1.5rem; 
                        border-radius: 8px; margin-bottom: 1rem;'>
                <h4 style='color: {self.colors['secondary']}; margin-top: 0;'>⚙️ Practical Skills</h4>
                <ul style='line-height: 1.8;'>
                    <li>Build Real Data Pipelines</li>
                    <li>Use 100+ Built-in Functions</li>
                    <li>Deploy to Production</li>
                    <li>Monitor & Debug Effectively</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        
        # Stats - Cleaner layout
        st.markdown("---")
        st.markdown("### 📈 What's Inside")
        
        st.markdown(f"""
        <div style='background: {self.colors['surface']}; padding: 1.5rem; border-radius: 8px; margin: 1rem 0;'>
            <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 1.5rem;'>
                <div style='text-align: center;'>
                    <div style='font-size: 2rem; color: {self.colors['primary']};'>📚</div>
                    <div style='font-size: 1.8rem; font-weight: bold; color: {self.colors['primary']};'>11</div>
                    <div style='color: {self.colors['text_secondary']};'>Lessons</div>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 2rem; color: {self.colors['secondary']};'>📘</div>
                    <div style='font-size: 1.8rem; font-weight: bold; color: {self.colors['secondary']};'>25+</div>
                    <div style='color: {self.colors['text_secondary']};'>Quizzes</div>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 2rem; color: {self.colors['accent']};'>🚀</div>
                    <div style='font-size: 1.8rem; font-weight: bold; color: {self.colors['accent']};'>15+</div>
                    <div style='color: {self.colors['text_secondary']};'>Challenges</div>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 2rem; color: {self.colors['primary']};'>🎯</div>
                    <div style='font-size: 1.8rem; font-weight: bold; color: {self.colors['primary']};'>4</div>
                    <div style='color: {self.colors['text_secondary']};'>Mini-Projects</div>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 2rem; color: {self.colors['secondary']};'>📄</div>
                    <div style='font-size: 1.8rem; font-weight: bold; color: {self.colors['secondary']};'>5</div>
                    <div style='color: {self.colors['text_secondary']};'>Cheat Sheets</div>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 2rem; color: {self.colors['accent']};'>🎓</div>
                    <div style='font-size: 1.8rem; font-weight: bold; color: {self.colors['accent']};'>1</div>
                    <div style='color: {self.colors['text_secondary']};'>Certificate</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


class ContextPanel:
    """Right-side context panel for tips, notes, and checkpoints"""
    
    def __init__(self, colors: Dict[str, str]):
        self.colors = colors
    
    def render(self, step_data: Optional[Dict[str, Any]] = None) -> None:
        """Render context panel"""
        st.markdown(f"""
        <div style='background: {self.colors['surface']}; padding: 1.5rem; 
                    border-radius: 12px; border: 2px solid {self.colors['primary']}22;'>
            <h3 style='color: {self.colors['primary']}; margin-top: 0;'>📌 Context</h3>
        </div>
        """, unsafe_allow_html=True)
        
        if step_data:
            # Step status
            if step_data.get('completed'):
                st.success("✅ Step Completed")
            else:
                st.info("⏳ In Progress")
            
            st.markdown("---")
            
            # Tags
            if step_data.get('tags'):
                st.markdown("**🏷️ Key Concepts:**")
                for tag in step_data['tags'][:5]:
                    st.markdown(f"- {tag}")
            
            st.markdown("---")
            
            # Tips
            with st.expander("💡 Quick Tips", expanded=True):
                st.markdown("""
                - Read the explanation carefully
                - Try the code examples
                - Experiment with modifications
                - Take notes if helpful
                """)
        else:
            st.info("Select a step to see context information")
