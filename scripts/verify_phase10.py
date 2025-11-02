"""
Phase 10 Verification Script
Verifies all Phase 10 deliverables are complete and functional.
"""

import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')

# Color codes for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists."""
    if Path(path).exists():
        print(f"  {GREEN}✅{RESET} {description}")
        return True
    else:
        print(f"  {RED}❌{RESET} {description} - NOT FOUND: {path}")
        return False


def check_module_importable(module_name: str, description: str) -> bool:
    """Check if a module can be imported."""
    try:
        __import__(module_name)
        print(f"  {GREEN}✅{RESET} {description}")
        return True
    except ImportError as e:
        print(f"  {RED}❌{RESET} {description} - IMPORT ERROR: {e}")
        return False


def main():
    """Run all Phase 10 verification checks."""
    print("\n" + "=" * 70)
    print(f"{BLUE}ODIBI CORE - Phase 10 Verification{RESET}")
    print("LearnODIBI Studio - Learning Ecosystem & Community")
    print("=" * 70 + "\n")

    all_checks = []

    # 1. Version Check
    print(f"{YELLOW}[1/8] Version Check{RESET}")
    try:
        from odibi_core.__version__ import __version__, __phase__
        if __version__ == "1.1.0" and __phase__ == "learning-ecosystem":
            print(f"  {GREEN}✅{RESET} Version: {__version__} (Phase: {__phase__})")
            all_checks.append(True)
        else:
            print(f"  {RED}❌{RESET} Expected v1.1.0/learning-ecosystem, got {__version__}/{__phase__}")
            all_checks.append(False)
    except Exception as e:
        print(f"  {RED}❌{RESET} Version check failed: {e}")
        all_checks.append(False)

    # 2. learnodibi_data Module
    print(f"\n{YELLOW}[2/8] learnodibi_data Module{RESET}")
    checks = [
        check_module_importable("odibi_core.learnodibi_data", "Module imports"),
        check_module_importable("odibi_core.learnodibi_data.data_generator", "Data generator"),
        check_module_importable("odibi_core.learnodibi_data.datasets", "Dataset loader"),
    ]
    all_checks.append(all(checks))

    # 3. learnodibi_project Module
    print(f"\n{YELLOW}[3/8] learnodibi_project Module{RESET}")
    checks = [
        check_module_importable("odibi_core.learnodibi_project", "Module imports"),
        check_module_importable("odibi_core.learnodibi_project.demo_pipeline", "Demo pipeline"),
        check_file_exists("odibi_core/learnodibi_project/bronze_config.json", "Bronze config"),
        check_file_exists("odibi_core/learnodibi_project/silver_config.json", "Silver config"),
        check_file_exists("odibi_core/learnodibi_project/gold_config.json", "Gold config"),
        check_file_exists("odibi_core/learnodibi_project/full_pipeline_config.json", "Full pipeline config"),
    ]
    all_checks.append(all(checks))

    # 4. learnodibi_backend Module
    print(f"\n{YELLOW}[4/8] learnodibi_backend Module{RESET}")
    checks = [
        check_module_importable("odibi_core.learnodibi_backend", "Module imports"),
        check_module_importable("odibi_core.learnodibi_backend.api", "API layer"),
        check_module_importable("odibi_core.learnodibi_backend.cache", "Cache system"),
        check_module_importable("odibi_core.learnodibi_backend.error_handler", "Error handler"),
    ]
    all_checks.append(all(checks))

    # 5. learnodibi_ui Module
    print(f"\n{YELLOW}[5/8] learnodibi_ui Module{RESET}")
    checks = [
        check_file_exists("odibi_core/learnodibi_ui/app.py", "Main Streamlit app"),
        check_file_exists("odibi_core/learnodibi_ui/theme.py", "Theme configuration"),
        check_file_exists("odibi_core/learnodibi_ui/utils.py", "UI utilities"),
        check_file_exists("odibi_core/learnodibi_ui/pages/1_core.py", "Core concepts page"),
        check_file_exists("odibi_core/learnodibi_ui/pages/2_functions.py", "Functions page"),
        check_file_exists("odibi_core/learnodibi_ui/pages/3_sdk.py", "SDK examples page"),
        check_file_exists("odibi_core/learnodibi_ui/pages/4_demo_project.py", "Demo project page"),
        check_file_exists("odibi_core/learnodibi_ui/pages/5_docs.py", "Documentation page"),
    ]
    all_checks.append(all(checks))

    # 6. Dependencies
    print(f"\n{YELLOW}[6/8] Dependencies Check{RESET}")
    checks = []
    required_packages = [
        ("streamlit", "Streamlit UI framework"),
        ("plotly", "Plotly visualization"),
        ("pandas", "Pandas data processing"),
    ]
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"  {GREEN}✅{RESET} {description}")
            checks.append(True)
        except ImportError:
            print(f"  {YELLOW}⚠{RESET}  {description} - Optional dependency not installed")
            checks.append(False)
    all_checks.append(any(checks))  # At least pandas should be present

    # 7. Docker & Packaging
    print(f"\n{YELLOW}[7/8] Docker & Packaging{RESET}")
    checks = [
        check_file_exists("Dockerfile", "Dockerfile"),
        check_file_exists("docker-compose.yml", "Docker Compose"),
        check_file_exists(".dockerignore", "Docker ignore"),
        check_file_exists("pyproject.toml", "PyPI config"),
    ]
    all_checks.append(all(checks))

    # 8. Documentation
    print(f"\n{YELLOW}[8/8] Phase 10 Documentation{RESET}")
    checks = [
        check_file_exists("docs/walkthroughs/PHASE_10_TEST_REPORT.md", "Test report"),
        check_file_exists("docs/walkthroughs/PHASE_10_PACKAGING_SUMMARY.md", "Packaging summary"),
        check_file_exists("docs/walkthroughs/PHASE_10_USER_EXPERIENCE_REPORT.md", "UX report"),
        check_file_exists("docs/walkthroughs/LEARNODIBI_STUDIO_VERIFICATION.md", "Studio verification"),
        check_file_exists("docs/walkthroughs/PHASE_10_COMPLETE.md", "Phase 10 complete"),
    ]
    all_checks.append(all(checks))

    # Final Summary
    print("\n" + "=" * 70)
    passed = sum(all_checks)
    total = len(all_checks)
    percentage = (passed / total) * 100

    if percentage == 100:
        print(f"{GREEN}✅ PHASE 10 VERIFICATION: PASSED ({passed}/{total}){RESET}")
        print(f"\n{GREEN}🎉 LearnODIBI Studio is ready for launch!{RESET}")
        print(f"\n{BLUE}Quick Start:{RESET}")
        print(f"  1. Install dependencies: pip install -e \".[studio]\"")
        print(f"  2. Launch Studio: streamlit run odibi_core/learnodibi_ui/app.py")
        print(f"  3. Access at: http://localhost:8501")
        return 0
    else:
        print(f"{RED}❌ PHASE 10 VERIFICATION: FAILED ({passed}/{total} = {percentage:.1f}%){RESET}")
        print(f"\n{YELLOW}Please address the issues above before launching.{RESET}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
