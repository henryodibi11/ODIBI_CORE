"""
LearnODIBI - Interactive Teaching Platform for ODIBI Core

This module provides an educational interface to learn ODIBI Core concepts
through interactive walkthroughs, quizzes, and hands-on exercises.
"""

from pathlib import Path
import subprocess
import sys

__version__ = "1.0.0"


def launch_ui(port: int = 8501):
    """
    Launch the LearnODIBI Streamlit UI.
    
    Args:
        port: Port number to run the Streamlit server (default: 8501)
        
    Raises:
        FileNotFoundError: If the LearnODIBI app is not found
        
    Example:
        >>> from odibi_core.learnodibi import launch_ui
        >>> launch_ui(port=8502)
    """
    app_path = Path(__file__).parent.parent / "learnodibi_ui" / "app.py"
    
    if not app_path.exists():
        raise FileNotFoundError(
            f"LearnODIBI app not found at: {app_path}\n"
            f"Please ensure the learnodibi_ui module is installed."
        )
    
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(app_path),
        "--server.port",
        str(port)
    ]
    
    print(f"🚀 Launching LearnODIBI UI on http://localhost:{port}")
    print(f"📚 Interactive learning platform for ODIBI Core")
    print(f"\nPress Ctrl+C to stop the server\n")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 LearnODIBI UI stopped")
    except Exception as e:
        print(f"\n❌ Error launching LearnODIBI: {e}")
        raise


__all__ = ["launch_ui", "__version__"]
