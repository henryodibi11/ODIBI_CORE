"""
UI Helpers - Utility components for LearnODIBI Studio
Handles copy buttons, syntax highlighting, quizzes, and other interactive elements
"""

import streamlit as st
import pyperclip
from typing import List, Dict, Optional, Any
import json
from pathlib import Path
import re


class InteractiveHelpers:
    """Helper utilities for interactive UI elements"""
    
    @staticmethod
    def code_block_with_copy(code: str, language: str = "python", key: str = None) -> None:
        """Display code block with copy button"""
        # Display code block
        st.code(code, language=language)
        
        # Copy button below code block
        if st.button("📋 Copy Code", key=f"copy_{key}", use_container_width=True, help="Copy to clipboard"):
            # Use pyperclip for reliable cross-platform copying
            try:
                import pyperclip
                pyperclip.copy(code)
                st.toast("✅ Copied to clipboard!", icon="📋")
                st.success("Code copied! Paste it in your editor.")
            except ImportError:
                # Fallback: Show code in a text area for manual copy
                st.info("💡 Pyperclip not installed. Select and copy the code below:")
                st.text_area("Code to copy:", value=code, height=150, key=f"manual_copy_{key}")
            except Exception as e:
                # Fallback for any other errors
                st.warning("⚠️ Automatic copy failed. Select and copy the code manually:")
                st.text_area("Code to copy:", value=code, height=150, key=f"fallback_copy_{key}")
    
    @staticmethod
    def expandable_section(title: str, content: str, icon: str = "💡", expanded: bool = False, key: str = None):
        """Create expandable section with custom styling"""
        with st.expander(f"{icon} {title}", expanded=expanded):
            st.markdown(content)
    
    @staticmethod
    def checkpoint_quiz(
        question: str,
        options: List[str],
        correct_answer: int,
        explanation: str,
        key: str
    ) -> bool:
        """
        Display a multiple-choice quiz checkpoint
        
        Args:
            question: The question text
            options: List of answer options
            correct_answer: Index of correct answer (0-based)
            explanation: Explanation shown after answering
            key: Unique key for this quiz
            
        Returns:
            True if answered correctly, False otherwise
        """
        st.markdown(f"### 📘 Checkpoint Quiz")
        st.markdown(f"**{question}**")
        
        # Initialize session state for this quiz
        quiz_key = f"quiz_{key}"
        answered_key = f"quiz_answered_{key}"
        
        if answered_key not in st.session_state:
            st.session_state[answered_key] = False
        
        # Show options as radio buttons
        selected = st.radio(
            "Select your answer:",
            options=options,
            key=quiz_key,
            index=None if not st.session_state[answered_key] else correct_answer
        )
        
        # Check answer button
        if not st.session_state[answered_key]:
            if st.button("Check Answer", key=f"check_{key}"):
                if selected is None:
                    st.warning("Please select an answer first!")
                else:
                    selected_index = options.index(selected)
                    st.session_state[answered_key] = True
                    
                    if selected_index == correct_answer:
                        st.success("✅ Correct!")
                        st.markdown(f"**Explanation:** {explanation}")
                        return True
                    else:
                        st.error(f"❌ Incorrect. The correct answer is: {options[correct_answer]}")
                        st.markdown(f"**Explanation:** {explanation}")
                        return False
        else:
            # Show result
            selected_index = options.index(selected) if selected else -1
            if selected_index == correct_answer:
                st.success("✅ You got this right!")
            else:
                st.info(f"💡 Correct answer: {options[correct_answer]}")
            st.markdown(f"**Explanation:** {explanation}")
            
            # Reset button
            if st.button("Try Again", key=f"reset_{key}"):
                st.session_state[answered_key] = False
                st.rerun()
        
        return st.session_state.get(answered_key, False)
    
    @staticmethod
    def reflection_prompt(prompt: str, key: str) -> Optional[str]:
        """Display a reflection text input for learners"""
        st.markdown("### 💭 Reflection")
        st.markdown(f"**{prompt}**")
        
        reflection = st.text_area(
            "Your thoughts:",
            key=f"reflection_{key}",
            height=100,
            help="Take a moment to reflect on what you've learned"
        )
        
        if reflection:
            st.info("💡 Great reflection! This helps solidify your learning.")
        
        return reflection if reflection else None
    
    @staticmethod
    def progress_badge(completed: int, total: int, label: str = "Progress") -> None:
        """Display a progress badge with animation"""
        percentage = (completed / total * 100) if total > 0 else 0
        
        # Color based on progress
        if percentage >= 100:
            color = "#4CAF50"  # Green
            icon = "🎓"
            animation = "bounce"
        elif percentage >= 75:
            color = "#F5B400"  # Gold
            icon = "⭐"
            animation = "pulse"
        elif percentage >= 50:
            color = "#2196F3"  # Blue
            icon = "📚"
            animation = "pulse"
        else:
            color = "#9E9E9E"  # Gray
            icon = "📖"
            animation = "none"
        
        st.markdown(f"""
        <style>
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-10px); }}
            }}
            @keyframes pulse {{
                0%, 100% {{ transform: scale(1); }}
                50% {{ transform: scale(1.05); }}
            }}
            .progress-badge {{
                animation: {animation} 2s ease-in-out infinite;
            }}
        </style>
        <div class='progress-badge' style='background: {color}; padding: 1rem; border-radius: 12px; text-align: center; box-shadow: 0 4px 12px rgba(0,0,0,0.15);'>
            <span style='font-size: 2.5rem; display: block; margin-bottom: 0.5rem;'>{icon}</span>
            <h3 style='margin: 0; color: white; font-size: 2rem;'>{percentage:.0f}%</h3>
            <p style='margin: 0.5rem 0 0 0; color: white; font-size: 0.9em;'>{label}: {completed}/{total}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def try_it_yourself_note(context: str = "") -> None:
        """Display 'Try It Yourself' note instead of run button"""
        note = f"""
        <div style='background: linear-gradient(135deg, #F5B40022, #00796B22); 
                    padding: 1.5rem; border-radius: 8px; border-left: 4px solid #F5B400;'>
            <h4 style='margin-top: 0; color: #F5B400;'>🧪 Try It Yourself</h4>
            <p style='margin-bottom: 0;'>
                {context if context else 
                "Copy this code and run it in your own Python environment to see the results. "
                "Experiment with different values and parameters to deepen your understanding!"}
            </p>
        </div>
        """
        st.markdown(note, unsafe_allow_html=True)
    
    @staticmethod
    def common_mistakes_section(mistakes: List[Dict[str, str]], key: str) -> None:
        """
        Display common mistakes section
        
        Args:
            mistakes: List of dicts with 'mistake' and 'solution' keys
            key: Unique key for this section
        """
        with st.expander("⚠️ Common Mistakes", expanded=False):
            for i, item in enumerate(mistakes):
                st.markdown(f"**Mistake #{i+1}:** {item['mistake']}")
                st.markdown(f"**Solution:** {item['solution']}")
                if i < len(mistakes) - 1:
                    st.markdown("---")
    
    @staticmethod
    def why_it_matters_section(content: str) -> None:
        """Display 'Why It Matters' section"""
        with st.expander("💡 Why It Matters", expanded=False):
            st.markdown(content)


class ProgressTracker:
    """Manages learner progress tracking"""
    
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path / "progress.json"
        self.progress = self._load_progress()
    
    def _load_progress(self) -> Dict:
        """Load progress from JSON file"""
        if not self.storage_path.exists():
            return {
                "lessons_completed": [],
                "steps_completed": {},
                "quizzes_passed": [],
                "total_time_minutes": 0,
                "badges_earned": [],
                "last_lesson": None,
                "last_step": 0
            }
        
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {
                "lessons_completed": [],
                "steps_completed": {},
                "quizzes_passed": [],
                "total_time_minutes": 0,
                "badges_earned": [],
                "last_lesson": None,
                "last_step": 0
            }
    
    def save_progress(self) -> None:
        """Save progress to JSON file"""
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.progress, f, indent=2)
    
    def mark_step_complete(self, lesson: str, step: int) -> None:
        """Mark a step as completed"""
        if lesson not in self.progress["steps_completed"]:
            self.progress["steps_completed"][lesson] = []
        
        if step not in self.progress["steps_completed"][lesson]:
            self.progress["steps_completed"][lesson].append(step)
        
        self.save_progress()
    
    def mark_lesson_complete(self, lesson: str) -> None:
        """Mark entire lesson as completed"""
        if lesson not in self.progress["lessons_completed"]:
            self.progress["lessons_completed"].append(lesson)
        
        # Award badge
        self._award_badge(f"completed_{lesson}")
        self.save_progress()
    
    def mark_quiz_passed(self, quiz_id: str) -> None:
        """Mark quiz as passed"""
        if quiz_id not in self.progress["quizzes_passed"]:
            self.progress["quizzes_passed"].append(quiz_id)
        self.save_progress()
    
    def _award_badge(self, badge_name: str) -> None:
        """Award a badge"""
        if badge_name not in self.progress["badges_earned"]:
            self.progress["badges_earned"].append(badge_name)
    
    def get_completion_percentage(self, lesson: str, total_steps: int) -> float:
        """Get completion percentage for a lesson"""
        completed = len(self.progress["steps_completed"].get(lesson, []))
        return (completed / total_steps * 100) if total_steps > 0 else 0
    
    def get_badges(self) -> List[str]:
        """Get earned badges"""
        return self.progress["badges_earned"]
    
    def reset_progress(self) -> None:
        """Reset all progress"""
        self.progress = {
            "lessons_completed": [],
            "steps_completed": {},
            "quizzes_passed": [],
            "total_time_minutes": 0,
            "badges_earned": [],
            "last_lesson": None,
            "last_step": 0
        }
        self.save_progress()
    
    def update_last_position(self, lesson: str, step: int) -> None:
        """Update last visited position"""
        self.progress["last_lesson"] = lesson
        self.progress["last_step"] = step
        self.save_progress()


class SyntaxHighlighter:
    """Enhanced syntax highlighting utilities"""
    
    @staticmethod
    def highlight_code(code: str, language: str = "python") -> str:
        """
        Return code with syntax highlighting metadata
        (Streamlit handles actual highlighting via st.code)
        """
        return code
    
    @staticmethod
    def extract_imports(code: str) -> List[str]:
        """Extract import statements from Python code"""
        import_pattern = r'^(?:from\s+[\w.]+\s+)?import\s+[\w.,\s]+(?:\s+as\s+\w+)?'
        imports = re.findall(import_pattern, code, re.MULTILINE)
        return imports
    
    @staticmethod
    def extract_functions(code: str) -> List[str]:
        """Extract function definitions from Python code"""
        func_pattern = r'^def\s+(\w+)\s*\('
        functions = re.findall(func_pattern, code, re.MULTILINE)
        return functions
    
    @staticmethod
    def extract_variables(code: str) -> List[str]:
        """Extract variable assignments from Python code"""
        var_pattern = r'^(\w+)\s*='
        variables = re.findall(var_pattern, code, re.MULTILINE)
        return variables
