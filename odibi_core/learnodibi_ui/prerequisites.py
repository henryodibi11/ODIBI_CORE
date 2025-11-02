"""
Prerequisites System - Check learner readiness before starting lessons
"""

PREREQUISITES = {
    "DEVELOPER_WALKTHROUGH_PHASE_1.md": {
        "knowledge": [
            "Basic Python syntax (variables, functions, classes)",
            "Familiarity with DataFrames (Pandas basics)"
        ],
        "setup": [
            "Python 3.8+ installed",
            "ODIBI CORE installed (pip install odibi-core)",
            "Code editor ready (VS Code, PyCharm, etc.)"
        ],
        "prior_lessons": []
    },
    
    "DEVELOPER_WALKTHROUGH_PHASE_2.md": {
        "knowledge": [
            "Completed Phase 1",
            "Understanding of Pandas DataFrames",
            "Basic knowledge of PySpark (helpful but not required)"
        ],
        "setup": [
            "Phase 1 concepts mastered",
            "Access to Spark (optional for testing)"
        ],
        "prior_lessons": ["DEVELOPER_WALKTHROUGH_PHASE_1.md"]
    },
    
    "DEVELOPER_WALKTHROUGH_PHASE_3.md": {
        "knowledge": [
            "Completed Phases 1-2",
            "JSON file format",
            "Configuration management concepts"
        ],
        "setup": [
            "Text editor for editing JSON/config files"
        ],
        "prior_lessons": [
            "DEVELOPER_WALKTHROUGH_PHASE_1.md",
            "DEVELOPER_WALKTHROUGH_PHASE_2.md"
        ]
    },
    
    "DEVELOPER_WALKTHROUGH_FUNCTIONS.md": {
        "knowledge": [
            "Completed Phases 1-3",
            "Understanding of engine detection pattern",
            "Basic NumPy operations"
        ],
        "setup": [
            "NumPy installed",
            "Understanding of safe operations (division by zero, etc.)"
        ],
        "prior_lessons": [
            "DEVELOPER_WALKTHROUGH_PHASE_1.md",
            "DEVELOPER_WALKTHROUGH_PHASE_2.md"
        ]
    },
    
    "DEVELOPER_WALKTHROUGH_PHASE_9.md": {
        "knowledge": [
            "Completed Phases 1-8",
            "Command-line basics",
            "API design concepts"
        ],
        "setup": [
            "Terminal/command prompt access",
            "Understanding of CLIs"
        ],
        "prior_lessons": [
            "DEVELOPER_WALKTHROUGH_PHASE_1.md",
            "DEVELOPER_WALKTHROUGH_PHASE_2.md",
            "DEVELOPER_WALKTHROUGH_PHASE_3.md"
        ]
    }
}


def get_prerequisites(lesson_id: str):
    """Get prerequisites for a lesson"""
    return PREREQUISITES.get(lesson_id, {
        "knowledge": [],
        "setup": [],
        "prior_lessons": []
    })


def check_prerequisites_met(lesson_id: str, completed_lessons: list) -> tuple:
    """
    Check if prerequisites are met
    
    Returns:
        (all_met: bool, missing: list)
    """
    prereqs = get_prerequisites(lesson_id)
    prior_lessons = prereqs.get("prior_lessons", [])
    
    missing = [lesson for lesson in prior_lessons if lesson not in completed_lessons]
    
    return (len(missing) == 0, missing)
