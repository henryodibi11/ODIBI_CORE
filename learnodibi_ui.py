"""
LearnODIBI Studio - Self-Guided Teaching Platform
Main entry point for the interactive learning experience

Usage:
    streamlit run learnodibi_ui.py
"""

import streamlit as st
import sys
from pathlib import Path

# Page configuration MUST be first
st.set_page_config(
    page_title="LearnODIBI Studio",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add odibi_core to path
ODIBI_ROOT = Path(__file__).parent
if str(ODIBI_ROOT) not in sys.path:
    sys.path.insert(0, str(ODIBI_ROOT))

from odibi_core.learnodibi_ui.theme import apply_theme, COLORS, COLORS_DARK, COLORS_LIGHT
from odibi_core.learnodibi_ui.ui_layout import (
    HomeScreen, SidebarLayout, NavigationTree, LessonNavigation, ContextPanel
)
from odibi_core.learnodibi_ui.ui_teaching_engine import TeachingEngine, LessonRenderer
from odibi_core.learnodibi_ui.ui_helpers import (
    InteractiveHelpers, ProgressTracker, SyntaxHighlighter
)
from odibi_core.learnodibi_ui.walkthrough_parser import get_walkthrough_parser
from odibi_core.learnodibi_ui.project_scaffolder import ProjectScaffolder
from odibi_core.learnodibi_ui.quiz_database import get_quiz_for_step
from odibi_core.learnodibi_ui.challenges_database import get_challenge_for_step
from odibi_core.learnodibi_ui.prerequisites import get_prerequisites, check_prerequisites_met
from odibi_core.learnodibi_ui.mini_projects import get_mini_project, get_capstone_project
from odibi_core.learnodibi_ui.cheat_sheets import get_cheat_sheet, generate_downloadable_cheat_sheet
from odibi_core.learnodibi_ui.certificate_generator import generate_certificate, generate_certificate_html

# Initialize session state
def initialize_session():
    """Initialize session state variables"""
    defaults = {
        "screen": "home",  # home, guided, explore, progress, scaffolder, projects, cheatsheets
        "learning_mode": "guided",  # guided, explore
        "current_lesson": None,
        "current_step": 0,
        "completed_steps": set(),
        "teaching_engine": None,
        "progress_tracker": None,
        "parser": None,
        "first_project_created": False,
        "ui_theme": "dark"  # dark, light
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value
    
    # Initialize objects
    if st.session_state.teaching_engine is None:
        st.session_state.teaching_engine = TeachingEngine(ODIBI_ROOT)
    
    if st.session_state.progress_tracker is None:
        st.session_state.progress_tracker = ProgressTracker(ODIBI_ROOT)
    
    if st.session_state.parser is None:
        st.session_state.parser = get_walkthrough_parser(ODIBI_ROOT)

initialize_session()

# Apply theme based on user selection
apply_theme(st.session_state.ui_theme)

# Globals
engine = st.session_state.teaching_engine
progress = st.session_state.progress_tracker
parser = st.session_state.parser
renderer = LessonRenderer(COLORS)
helpers = InteractiveHelpers()


def render_sidebar():
    """Render sidebar with navigation and controls"""
    with st.sidebar:
        sidebar = SidebarLayout(COLORS)
        sidebar.render_header()
        
        st.markdown("---")
        
        # Mode selector
        def on_mode_change(mode):
            st.session_state.learning_mode = mode
            st.rerun()
        
        sidebar.render_mode_selector(
            st.session_state.learning_mode,
            on_mode_change
        )
        
        st.markdown("---")
        
        # Navigation tree (if in explore or guided mode)
        if st.session_state.screen in ["guided", "explore"]:
            tree_data = engine.get_lesson_navigation_tree()
            nav_tree = NavigationTree(tree_data, COLORS)
            nav_tree.render(on_lesson_select=lambda lesson_id: (
                setattr(st.session_state, "current_lesson", lesson_id),
                setattr(st.session_state, "current_step", 0),
                setattr(st.session_state, "screen", "explore")
            ))
            
            st.markdown("---")
        
        # Progress summary
        total_lessons = len(engine.get_all_lessons())
        completed_lessons = len(progress.progress.get("lessons_completed", []))
        badges = progress.get_badges()
        
        sidebar.render_progress_summary(completed_lessons, total_lessons, badges)
        
        st.markdown("---")
        
        # Theme selector
        st.markdown("### 🎨 Theme")
        theme_choice = st.selectbox(
            "Select Theme",
            options=["dark", "light"],
            index=0 if st.session_state.ui_theme == "dark" else 1,
            label_visibility="collapsed"
        )
        if theme_choice != st.session_state.ui_theme:
            st.session_state.ui_theme = theme_choice
            st.rerun()
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚙️ Quick Actions")
        
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.screen = "home"
            st.rerun()
        
        if st.button("📊 My Progress", use_container_width=True):
            st.session_state.screen = "progress"
            st.rerun()
        
        if st.button("🎯 Mini-Projects", use_container_width=True):
            st.session_state.screen = "projects"
            st.rerun()
        
        if st.button("📄 Cheat Sheets", use_container_width=True):
            st.session_state.screen = "cheatsheets"
            st.rerun()
        
        if st.button("🛠️ New Project", use_container_width=True):
            st.session_state.screen = "scaffolder"
            st.rerun()
        
        if st.button("🔄 Reset Progress", use_container_width=True):
            progress.reset_progress()
            st.success("Progress reset!")
            st.rerun()
        
        st.markdown("---")
        
        # Footer
        st.markdown(f"""
        <div style='text-align: center; padding: 1rem; 
                    background: {COLORS['surface']}; border-radius: 8px;'>
            <p style='color: {COLORS['text_secondary']}; font-size: 0.85em; margin: 0;'>
                <strong>LearnODIBI Studio</strong><br/>
                by Henry Odibi<br/>
                <small>Powered by ODIBI CORE</small>
            </p>
        </div>
        """, unsafe_allow_html=True)


def render_home_screen():
    """Render home/landing screen"""
    home = HomeScreen(COLORS)
    home.render(
        on_start_guided=lambda: (
            setattr(st.session_state, "screen", "guided"),
            setattr(st.session_state, "learning_mode", "guided"),
            st.rerun()
        ),
        on_explore_lessons=lambda: (
            setattr(st.session_state, "screen", "explore"),
            setattr(st.session_state, "learning_mode", "explore"),
            st.rerun()
        ),
        on_view_progress=lambda: (
            setattr(st.session_state, "screen", "progress"),
            st.rerun()
        )
    )


def render_guided_mode():
    """Render guided learning mode"""
    st.title("🛤️ Guided Learning Path")
    st.markdown(f"<p style='color: {COLORS['text_secondary']}; font-size: 1.1em;'>Follow the structured course from start to finish</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Get lessons in order
    all_lessons = engine.get_all_lessons()
    
    if not all_lessons:
        renderer.render_empty_state("No lessons available", "📚")
        st.error("Unable to load lessons. Please check that the walkthrough files exist in docs/walkthroughs/")
        return
    
    # If no lesson selected, start with first
    if st.session_state.current_lesson is None:
        st.session_state.current_lesson = all_lessons[0].lesson_id
    
    # Load current lesson
    lesson = engine.get_lesson(st.session_state.current_lesson)
    
    if not lesson:
        st.error("Failed to load lesson")
        return
    
    # Render lesson
    render_lesson_content(lesson, mode="guided")


def render_explore_mode():
    """Render free explore mode"""
    st.title("🔍 Explore Lessons")
    st.markdown(f"<p style='color: {COLORS['text_secondary']}; font-size: 1.1em;'>Jump to any lesson and learn at your own pace</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Filter options
    st.markdown("### 🔍 Filter Lessons")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Phase filter
        all_phases = list(engine.get_lessons_by_phase().keys())
        selected_phase = st.selectbox(
            "📂 By Phase:",
            options=["All Phases"] + sorted(all_phases),
            key="phase_filter"
        )
    
    with col2:
        # Difficulty filter
        selected_difficulty = st.selectbox(
            "📊 By Difficulty:",
            options=["All Levels", "Beginner", "Intermediate", "Advanced"],
            key="difficulty_filter"
        )
    
    # Apply filters
    all_lessons_list = engine.get_all_lessons()
    filtered_lessons = all_lessons_list
    
    if selected_phase != "All Phases":
        filtered_lessons = [l for l in filtered_lessons if l.phase == selected_phase]
    
    if selected_difficulty != "All Levels":
        filtered_lessons = [l for l in filtered_lessons if l.difficulty == selected_difficulty]
    
    if filtered_lessons and (selected_phase != "All Phases" or selected_difficulty != "All Levels"):
        st.success(f"Showing {len(filtered_lessons)} lesson(s)")
        
        for lesson_meta in filtered_lessons:
            with st.container():
                st.markdown(f"""
                <div style='background: {COLORS['surface']}; padding: 1rem; 
                            border-radius: 8px; margin-bottom: 1rem; 
                            border: 2px solid {COLORS['primary']}22;'>
                    <h4 style='color: {COLORS['primary']}; margin-top: 0;'>{lesson_meta.title}</h4>
                    <p style='color: {COLORS['text_secondary']}; font-size: 0.9em;'>{lesson_meta.description}</p>
                    <p style='margin: 0.5rem 0 0 0;'>
                        <span style='background: {COLORS['info']}; color: white; 
                                    padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.85em;'>
                            {lesson_meta.difficulty}
                        </span>
                        <span style='margin-left: 0.5rem; color: {COLORS['text_secondary']};'>
                            📊 {lesson_meta.total_steps} steps • ⏱️ {lesson_meta.duration}
                        </span>
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Start Lesson", key=f"filter_{lesson_meta.lesson_id}", use_container_width=True):
                    st.session_state.current_lesson = lesson_meta.lesson_id
                    st.session_state.current_step = 0
                    st.rerun()
        
        st.markdown("---")
    
    # If lesson selected, show it
    if st.session_state.current_lesson:
        lesson = engine.get_lesson(st.session_state.current_lesson)
        if lesson:
            render_lesson_content(lesson, mode="explore")
    else:
        # Show lesson grid
        st.markdown("### 📚 Browse All Lessons")
        lessons_by_phase = engine.get_lessons_by_phase()
        
        for phase_name, lessons in sorted(lessons_by_phase.items()):
            phase_title = engine._format_phase_title(phase_name)
            st.markdown(f"#### {phase_title}")
            
            cols = st.columns(2)
            for i, lesson_meta in enumerate(lessons):
                with cols[i % 2]:
                    st.markdown(f"""
                    <div style='background: {COLORS['surface']}; padding: 1rem; 
                                border-radius: 8px; margin-bottom: 1rem; 
                                border: 2px solid {COLORS['primary']}22;'>
                        <h4 style='color: {COLORS['primary']}; margin-top: 0;'>{lesson_meta.title}</h4>
                        <p style='color: {COLORS['text_secondary']}; font-size: 0.9em;'>{lesson_meta.description}</p>
                        <p style='margin: 0.5rem 0 0 0;'>
                            <span style='background: {COLORS['info']}; color: white; 
                                        padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.85em;'>
                                {lesson_meta.difficulty}
                            </span>
                            <span style='margin-left: 0.5rem; color: {COLORS['text_secondary']};'>
                                📊 {lesson_meta.total_steps} steps • ⏱️ {lesson_meta.duration}
                            </span>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(f"Start Lesson", key=f"start_{lesson_meta.lesson_id}", use_container_width=True):
                        st.session_state.current_lesson = lesson_meta.lesson_id
                        st.session_state.current_step = 0
                        st.rerun()


def render_lesson_content(lesson, mode="guided"):
    """Render the main lesson content with steps"""
    # Lesson header
    renderer.render_lesson_header(lesson)
    
    # Prerequisites Check
    prereqs = get_prerequisites(st.session_state.current_lesson)
    if prereqs["knowledge"] or prereqs["setup"] or prereqs["prior_lessons"]:
        with st.expander("⚠️ Prerequisites - Check Before Starting", expanded=False):
            completed_lessons = progress.progress.get("lessons_completed", [])
            all_met, missing = check_prerequisites_met(st.session_state.current_lesson, completed_lessons)
            
            if not all_met:
                st.warning("⚠️ You haven't completed some recommended lessons:")
                for lesson_id in missing:
                    lesson_meta = engine.manifest_loader.get_walkthrough(lesson_id)
                    if lesson_meta:
                        st.markdown(f"- ❌ {lesson_meta['title']}")
                st.info("💡 You can continue anyway, but completing prior lessons first is recommended.")
            else:
                st.success("✅ All prerequisite lessons completed!")
            
            if prereqs["knowledge"]:
                st.markdown("**📚 Knowledge Prerequisites:**")
                for item in prereqs["knowledge"]:
                    st.markdown(f"- {item}")
            
            if prereqs["setup"]:
                st.markdown("**⚙️ Setup Requirements:**")
                for item in prereqs["setup"]:
                    st.markdown(f"- {item}")
    
    # Overview
    if lesson.overview:
        with st.expander("📋 Lesson Overview", expanded=False):
            st.markdown(lesson.overview)
    
    st.markdown("##")
    
    # Steps
    if not lesson.steps:
        renderer.render_empty_state("No steps available in this lesson", "📖")
        return
    
    total_steps = len(lesson.steps)
    current_step_idx = st.session_state.current_step
    
    # Navigation
    nav = LessonNavigation(COLORS)
    nav.render_step_navigator(
        current_step_idx,
        total_steps,
        on_first=lambda: setattr(st.session_state, "current_step", 0) or st.rerun(),
        on_previous=lambda: setattr(st.session_state, "current_step", max(0, st.session_state.current_step - 1)) or st.rerun(),
        on_next=lambda: setattr(st.session_state, "current_step", min(total_steps - 1, st.session_state.current_step + 1)) or st.rerun(),
        on_last=lambda: setattr(st.session_state, "current_step", total_steps - 1) or st.rerun(),
        location="top"
    )
    
    st.markdown("##")
    
    # Main content with context panel
    col_main, col_context = st.columns([3, 1])
    
    with col_main:
        # Current step
        step = lesson.steps[current_step_idx]
        renderer.render_step_header(step, current_step_idx + 1, total_steps)
        
        # Explanation
        renderer.render_step_explanation(step.explanation)
        
        # Code
        if step.code:
            st.markdown("### 💻 Code")
            
            # Show code block
            st.code(step.code, language=step.language or "python")
            
            # Enhanced copy button
            st.markdown("##")
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if st.button("📋 COPY CODE TO CLIPBOARD", key=f"copy_step_{current_step_idx}", use_container_width=True, type="primary"):
                    try:
                        import pyperclip
                        pyperclip.copy(step.code)
                        st.toast("✅ Code copied to clipboard!", icon="📋")
                        st.success("✅ Code copied! Paste it in your editor and try it!")
                    except ImportError:
                        st.warning("⚠️ Pyperclip not installed. Install with: pip install pyperclip")
                        st.text_area("Manual copy (select and copy):", value=step.code, height=200, key=f"manual_{current_step_idx}")
                    except Exception as e:
                        st.warning(f"⚠️ Could not copy: {e}. Select and copy manually:")
                        st.text_area("Manual copy (select and copy):", value=step.code, height=200, key=f"fallback_{current_step_idx}")
            
            with col2:
                # Line count info
                line_count = len(step.code.strip().split('\n'))
                st.metric("Lines", line_count)
            
            # Try it yourself note (no code execution)
            helpers.try_it_yourself_note(
                "Copy this code to your local environment and experiment with it!"
            )
        
        # Why it matters
        if hasattr(step, 'notes') and step.notes:
            helpers.why_it_matters_section(step.notes)
        
        st.markdown("##")
        
        # Knowledge Check Quiz (if exists for this step)
        quiz = get_quiz_for_step(st.session_state.current_lesson, current_step_idx + 1)
        if quiz:
            st.markdown("---")
            passed = helpers.checkpoint_quiz(
                question=quiz["question"],
                options=quiz["options"],
                correct_answer=quiz["correct"],
                explanation=quiz["explanation"],
                key=f"quiz_{st.session_state.current_lesson}_{current_step_idx}"
            )
            if passed:
                progress.mark_quiz_passed(f"{st.session_state.current_lesson}_step{current_step_idx}")
        
        # Try This Challenge (if exists for this step)
        challenge = get_challenge_for_step(st.session_state.current_lesson, current_step_idx + 1)
        if challenge:
            st.markdown("---")
            st.markdown(f"### 🚀 Try This: {challenge['title']}")
            
            # Difficulty badge
            diff_colors = {"Beginner": "#10B981", "Intermediate": "#F59E0B", "Advanced": "#EF4444"}
            diff_color = diff_colors.get(challenge['difficulty'], "#6B7280")
            st.markdown(f"""
            <span style='background: {diff_color}; color: white; padding: 0.3rem 0.8rem; 
                         border-radius: 4px; font-size: 0.85em; font-weight: bold;'>
                {challenge['difficulty']}
            </span>
            """, unsafe_allow_html=True)
            
            # Task description
            with st.expander("📋 Challenge Instructions", expanded=True):
                st.markdown(challenge['task'])
            
            # Starter code
            with st.expander("💻 Starter Code", expanded=False):
                st.code(challenge['starter_code'], language="python")
                if st.button("📋 Copy Starter Code", key=f"copy_starter_{current_step_idx}"):
                    try:
                        import pyperclip
                        pyperclip.copy(challenge['starter_code'])
                        st.toast("✅ Starter code copied!", icon="📋")
                    except:
                        st.text_area("Copy manually:", value=challenge['starter_code'], height=150)
            
            # Hints and Solution
            col1, col2 = st.columns(2)
            with col1:
                with st.expander("💡 Need Help?"):
                    st.info("Try breaking the problem into smaller steps. Review the explanation above and look at similar examples.")
            
            with col2:
                with st.expander("✅ View Solution"):
                    st.warning("⚠️ Try solving it yourself first!")
                    st.code(challenge['solution'], language="python")
                    if st.button("📋 Copy Solution", key=f"copy_solution_{current_step_idx}"):
                        try:
                            import pyperclip
                            pyperclip.copy(challenge['solution'])
                            st.toast("✅ Solution copied!", icon="📋")
                        except:
                            st.text_area("Copy manually:", value=challenge['solution'], height=150)
        
        # Mark complete button
        st.markdown("##")
        if st.button("✅ Mark Step Complete", key=f"complete_{current_step_idx}", type="primary"):
            progress.mark_step_complete(st.session_state.current_lesson, current_step_idx)
            st.session_state.completed_steps.add(current_step_idx)
            
            # Check if this is first step ever
            total_completed = sum(len(steps) for steps in progress.progress.get("steps_completed", {}).values())
            if total_completed == 1:
                st.snow()  # Special effect for first step!
                st.success("🌟 First step completed! You're on your way to mastering ODIBI CORE!")
                st.toast("🎯 Keep going! You've got this!", icon="🌟")
            else:
                st.success("Step completed! 🎉")
                st.toast("✅ Step complete!", icon="✨")
            
            # Check milestones (every 10 steps)
            if total_completed % 10 == 0 and total_completed > 0:
                st.balloons()
                st.info(f"🏆 Milestone: {total_completed} steps completed across all lessons!")
            
            # Auto-advance
            if current_step_idx < total_steps - 1:
                st.session_state.current_step += 1
                st.rerun()
            else:
                # Last step - mark lesson complete
                progress.mark_lesson_complete(st.session_state.current_lesson)
                st.balloons()
                st.success("🎓 Lesson Complete! Well done!")
                
                # Check if all lessons are complete
                all_lessons = engine.get_all_lessons()
                completed_lessons = progress.progress.get("lessons_completed", [])
                if len(completed_lessons) == len(all_lessons):
                    st.balloons()
                    st.success("🏆🎓🌟 AMAZING! You've completed ALL lessons! You're now an ODIBI CORE master!")
                    st.toast("🎊 ALL LESSONS COMPLETE! 🎊", icon="🏆")
    
    with col_context:
        # Context panel
        context_panel = ContextPanel(COLORS)
        step_data = {
            "completed": current_step_idx in st.session_state.completed_steps,
            "tags": step.tags if hasattr(step, 'tags') and step.tags else []
        }
        context_panel.render(step_data)
    
    st.markdown("##")
    
    # Bottom navigation
    nav.render_step_navigator(
        current_step_idx,
        total_steps,
        on_first=lambda: setattr(st.session_state, "current_step", 0) or st.rerun(),
        on_previous=lambda: setattr(st.session_state, "current_step", max(0, st.session_state.current_step - 1)) or st.rerun(),
        on_next=lambda: setattr(st.session_state, "current_step", min(total_steps - 1, st.session_state.current_step + 1)) or st.rerun(),
        on_last=lambda: setattr(st.session_state, "current_step", total_steps - 1) or st.rerun(),
        location="bottom"
    )
    
    # Lesson-to-lesson navigation (guided mode only)
    if mode == "guided":
        prev_lesson = engine.get_previous_lesson(st.session_state.current_lesson)
        next_lesson = engine.get_next_lesson(st.session_state.current_lesson)
        
        nav.render_lesson_navigator(
            prev_lesson,
            next_lesson,
            on_prev_lesson=lambda: (
                setattr(st.session_state, "current_lesson", prev_lesson.lesson_id),
                setattr(st.session_state, "current_step", 0),
                st.rerun()
            ),
            on_next_lesson=lambda: (
                setattr(st.session_state, "current_lesson", next_lesson.lesson_id),
                setattr(st.session_state, "current_step", 0),
                st.rerun()
            )
        )


def render_progress_screen():
    """Render progress tracking screen"""
    st.title("📊 My Progress")
    st.markdown(f"<p style='color: {COLORS['text_secondary']}; font-size: 1.1em;'>Track your learning journey</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Check if eligible for certificate
    all_lessons = engine.get_all_lessons()
    total_lessons = len(all_lessons)
    completed_lessons = len(progress.progress.get("lessons_completed", []))
    
    if completed_lessons == total_lessons:
        st.success("🎓 Congratulations! You've completed all lessons and earned your certificate!")
        st.balloons()
        
        # Certificate section
        with st.expander("🏆 View Your Certificate", expanded=True):
            learner_name = st.text_input("Enter your name for the certificate:", placeholder="John Doe")
            
            if learner_name:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Generate certificate
                    cert_data = {
                        "total_lessons": total_lessons,
                        "lessons_completed": progress.progress.get("lessons_completed", []),
                        "steps_completed": progress.progress.get("steps_completed", {}),
                        "badges_earned": progress.get_badges(),
                        "quizzes_passed": progress.progress.get("quizzes_passed", [])
                    }
                    
                    cert_md = generate_certificate(learner_name, cert_data)
                    
                    st.download_button(
                        label="📥 Download Certificate (Markdown)",
                        data=cert_md,
                        file_name=f"ODIBI_Certificate_{learner_name.replace(' ', '_')}.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                
                with col2:
                    cert_html = generate_certificate_html(learner_name, cert_data)
                    st.download_button(
                        label="📥 Download Certificate (HTML)",
                        data=cert_html,
                        file_name=f"ODIBI_Certificate_{learner_name.replace(' ', '_')}.html",
                        mime="text/html",
                        use_container_width=True
                    )
                
                st.markdown("##")
                
                # Preview
                st.markdown("### 📄 Preview")
                st.markdown(cert_md)
        
        st.markdown("---")
    
    # Overall stats
    all_lessons = engine.get_all_lessons()
    total_lessons = len(all_lessons)
    completed_lessons = len(progress.progress.get("lessons_completed", []))
    badges = progress.get_badges()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        helpers.progress_badge(completed_lessons, total_lessons, "Lessons Completed")
    
    with col2:
        total_steps = sum(lesson.total_steps for lesson in all_lessons)
        completed_steps = sum(len(steps) for steps in progress.progress.get("steps_completed", {}).values())
        helpers.progress_badge(completed_steps, total_steps, "Steps Completed")
    
    with col3:
        st.markdown(f"""
        <div style='background: {COLORS['primary']}; padding: 1rem; border-radius: 8px; text-align: center;'>
            <span style='font-size: 2rem;'>🏆</span>
            <h3 style='margin: 0; color: {COLORS['background']};'>{len(badges)}</h3>
            <p style='margin: 0; color: {COLORS['background']}; font-size: 0.9em;'>Badges Earned</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("##")
    
    # Lesson breakdown
    st.markdown("### 📚 Lesson Progress")
    
    for lesson_meta in all_lessons:
        completed = lesson_meta.lesson_id in progress.progress.get("lessons_completed", [])
        step_completion = progress.get_completion_percentage(lesson_meta.lesson_id, lesson_meta.total_steps)
        
        with st.expander(f"{'✅' if completed else '⏳'} {lesson_meta.title}", expanded=False):
            st.progress(step_completion / 100)
            st.caption(f"{step_completion:.0f}% complete")
            
            if st.button("Resume", key=f"resume_{lesson_meta.lesson_id}"):
                st.session_state.current_lesson = lesson_meta.lesson_id
                st.session_state.screen = "explore"
                st.rerun()


def render_scaffolder_screen():
    """Render project scaffolder"""
    st.title("🛠️ Create New Project")
    st.markdown(f"<p style='color: {COLORS['text_secondary']}; font-size: 1.1em;'>Scaffold a new ODIBI CORE project</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    scaffolder = ProjectScaffolder()
    
    # Project details
    col1, col2 = st.columns(2)
    
    with col1:
        project_name = st.text_input("Project Name", placeholder="my_odibi_project")
        project_path = st.text_input("Project Path (absolute)", placeholder="D:/projects/my_odibi_project")
    
    with col2:
        template = st.selectbox("Template", options=["basic", "transformation", "functions"])
        
        template_info = scaffolder.templates.get(template, {})
        if template_info:
            st.info(f"**{template_info['name']}**: {template_info['description']}")
    
    st.markdown("##")
    
    # Create project
    if st.button("🚀 Create Project", type="primary", disabled=not (project_name and project_path)):
        try:
            with st.spinner("Creating project..."):
                result = scaffolder.create_project(project_path, template, project_name)
            
            st.success("✅ Project created successfully!")
            
            with st.expander("📋 Creation Log", expanded=True):
                for log in result["logs"]:
                    st.text(log)
            
            # Celebration!
            st.balloons()
            st.toast(f"🎉 {project_name} is ready to go!", icon="🚀")
            
            # Badge for first project
            if "first_project_created" not in st.session_state:
                st.session_state.first_project_created = True
                st.snow()
                st.info("🌟 First project created! You're building with ODIBI CORE!")
        except Exception as e:
            st.error(f"❌ Error creating project: {e}")


def render_mini_projects_screen():
    """Render mini-projects screen"""
    st.title("🎯 Mini-Projects")
    st.markdown(f"<p style='color: {COLORS['text_secondary']}; font-size: 1.1em;'>Hands-on practice projects for each phase</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Projects grid
    projects = {
        "phase1": get_mini_project("phase1"),
        "phase2": get_mini_project("phase2"),
        "phase3": get_mini_project("phase3"),
        "capstone": get_capstone_project()
    }
    
    for key, project in projects.items():
        if not project:
            continue
        
        # Project card
        st.markdown(f"""
        <div style='background: {COLORS['surface']}; padding: 2rem; border-radius: 12px; 
                    margin-bottom: 1.5rem; border-left: 6px solid {COLORS['primary']};'>
            <h2 style='color: {COLORS['primary']}; margin-top: 0;'>{project['title']}</h2>
            <p style='color: {COLORS['text_secondary']};'>{project['description']}</p>
            <p style='margin: 0.5rem 0;'>
                <span style='background: {COLORS['info']}; color: white; padding: 0.3rem 0.8rem; 
                             border-radius: 4px; margin-right: 0.5rem;'>{project['difficulty']}</span>
                <span style='color: {COLORS['text_secondary']};'>⏱️ {project['duration']}</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # Expandable sections
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.expander("📋 Instructions"):
                st.markdown(project['instructions'])
        
        with col2:
            with st.expander("💻 Starter Code"):
                st.code(project['starter_code'], language="python")
                if st.button("📋 Copy", key=f"copy_starter_{key}"):
                    try:
                        import pyperclip
                        pyperclip.copy(project['starter_code'])
                        st.toast("✅ Starter code copied!", icon="📋")
                    except:
                        st.text_area("Copy:", value=project['starter_code'], height=150)
        
        with col3:
            with st.expander("✅ Solution"):
                if key == "capstone":
                    st.info("💡 Capstone solution is comprehensive. Complete earlier projects first!")
                else:
                    st.warning("⚠️ Try it yourself first!")
                    st.code(project['solution'], language="python")
                    if st.button("📋 Copy Solution", key=f"copy_solution_{key}"):
                        try:
                            import pyperclip
                            pyperclip.copy(project['solution'])
                            st.toast("✅ Solution copied!", icon="📋")
                        except:
                            st.text_area("Copy:", value=project['solution'], height=150)
        
        st.markdown("---")


def render_cheat_sheets_screen():
    """Render cheat sheets screen"""
    st.title("📄 Cheat Sheets")
    st.markdown(f"<p style='color: {COLORS['text_secondary']}; font-size: 1.1em;'>Quick reference guides for each phase</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Select phase
    phase_options = {
        "Phase 1: Core Architecture": "phase1",
        "Phase 2: Dual-Engine Support": "phase2",
        "Phase 3: Configuration System": "phase3",
        "Functions Library": "functions",
        "SDK & CLI": "sdk"
    }
    
    selected_phase = st.selectbox("Select a cheat sheet:", list(phase_options.keys()))
    phase_key = phase_options[selected_phase]
    
    # Download button
    col1, col2 = st.columns([3, 1])
    with col2:
        cheat_sheet_content = generate_downloadable_cheat_sheet(phase_key)
        st.download_button(
            label="📥 Download",
            data=cheat_sheet_content,
            file_name=f"odibi_cheat_sheet_{phase_key}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    st.markdown("##")
    
    # Display cheat sheet
    st.markdown(get_cheat_sheet(phase_key))


def main():
    """Main application entry point"""
    # Render sidebar
    render_sidebar()
    
    # Render main content based on screen
    if st.session_state.screen == "home":
        render_home_screen()
    elif st.session_state.screen == "guided":
        render_guided_mode()
    elif st.session_state.screen == "explore":
        render_explore_mode()
    elif st.session_state.screen == "progress":
        render_progress_screen()
    elif st.session_state.screen == "projects":
        render_mini_projects_screen()
    elif st.session_state.screen == "cheatsheets":
        render_cheat_sheets_screen()
    elif st.session_state.screen == "scaffolder":
        render_scaffolder_screen()
    else:
        render_home_screen()


if __name__ == "__main__":
    main()
