"""
Verify that the walkthrough parser correctly extracts Mission/Step structure.
"""

import re
from pathlib import Path


def parse_walkthrough_structure(filepath: Path) -> dict:
    """
    Parse walkthrough file and extract Mission/Step structure.
    
    Returns:
        dict: {
            "missions": [
                {"number": 1, "title": "...", "steps": [...]},
                ...
            ],
            "total_missions": int,
            "total_steps": int
        }
    """
    content = filepath.read_text(encoding="utf-8")
    
    # Extract missions (### Mission N: or ## 🚀 MISSION N:)
    mission_pattern = r"(?:###|##)\s+(?:🚀\s+)?Mission\s+(\d+):\s+(.+)"
    missions = []
    
    for match in re.finditer(mission_pattern, content, re.IGNORECASE):
        mission_num = int(match.group(1))
        mission_title = match.group(2).strip()
        missions.append({
            "number": mission_num,
            "title": mission_title,
            "steps": []
        })
    
    # Extract steps (### Step N.M:)
    step_pattern = r"###\s+Step\s+(\d+)\.(\d+):\s+(.+)"
    
    for match in re.finditer(step_pattern, content, re.IGNORECASE):
        mission_num = int(match.group(1))
        step_num = int(match.group(2))
        step_title = match.group(3).strip()
        
        # Find corresponding mission
        for mission in missions:
            if mission["number"] == mission_num:
                mission["steps"].append({
                    "number": step_num,
                    "title": step_title
                })
                break
    
    total_steps = sum(len(m["steps"]) for m in missions)
    
    return {
        "missions": missions,
        "total_missions": len(missions),
        "total_steps": total_steps
    }


def verify_walkthrough(filepath: Path, expected_missions: int = None):
    """Verify walkthrough has proper structure."""
    print(f"\n{'='*70}")
    print(f"Verifying: {filepath.name}")
    print(f"{'='*70}\n")
    
    if not filepath.exists():
        print(f"[X] FILE NOT FOUND: {filepath}")
        return False
    
    structure = parse_walkthrough_structure(filepath)
    
    print(f"[*] Structure Analysis:")
    print(f"   Total Missions: {structure['total_missions']}")
    print(f"   Total Steps: {structure['total_steps']}")
    print()
    
    if structure["total_missions"] == 0:
        print("[X] ERROR: No missions found!")
        print("   Expected pattern: ### Mission N: Title")
        return False
    
    if structure["total_steps"] == 0:
        print("[!] WARNING: No steps found!")
        print("   Expected pattern: ### Step N.M: Title")
        print("   (This might be OK for high-level walkthroughs)")
    
    print("[*] Mission Breakdown:\n")
    for mission in structure["missions"]:
        print(f"   Mission {mission['number']}: {mission['title']}")
        print(f"      Steps: {len(mission['steps'])}")
        
        if mission["steps"]:
            for step in mission["steps"]:
                print(f"         {mission['number']}.{step['number']}: {step['title']}")
        else:
            print(f"         (No numbered steps found)")
        print()
    
    # Validation checks
    print("[+] Validation Results:")
    
    # Check 1: Missions are numbered sequentially
    mission_numbers = [m["number"] for m in structure["missions"]]
    expected_numbers = list(range(1, structure["total_missions"] + 1))
    
    if mission_numbers == expected_numbers:
        print("   [OK] Missions numbered sequentially (1, 2, 3, ...)")
    else:
        print(f"   [!] Mission numbering issues: {mission_numbers}")
    
    # Check 2: Each mission has at least one step
    missions_with_steps = sum(1 for m in structure["missions"] if len(m["steps"]) > 0)
    
    if missions_with_steps == structure["total_missions"]:
        print(f"   [OK] All {structure['total_missions']} missions have steps")
    else:
        print(f"   [!] {structure['total_missions'] - missions_with_steps} missions have no numbered steps")
    
    # Check 3: Steps within each mission are numbered sequentially
    all_sequential = True
    for mission in structure["missions"]:
        if mission["steps"]:
            step_numbers = [s["number"] for s in mission["steps"]]
            expected_step_numbers = list(range(1, len(mission["steps"]) + 1))
            if step_numbers != expected_step_numbers:
                print(f"   [!] Mission {mission['number']} step numbering: {step_numbers}")
                all_sequential = False
    
    if all_sequential and structure["total_steps"] > 0:
        print("   [OK] All steps numbered sequentially within missions")
    
    # Check 4: Expected mission count (if provided)
    if expected_missions:
        if structure["total_missions"] == expected_missions:
            print(f"   [OK] Has expected {expected_missions} missions")
        else:
            print(f"   [!] Expected {expected_missions} missions, found {structure['total_missions']}")
    
    print()
    
    if structure["total_missions"] > 0 and structure["total_steps"] > 0:
        print("[OK] WALKTHROUGH STRUCTURE VALID")
        return True
    else:
        print("[!] WALKTHROUGH MAY NEED REVIEW")
        return False


def main():
    """Verify all walkthroughs."""
    walkthroughs_dir = Path("docs/walkthroughs")
    
    print("\n" + "="*70)
    print("ODIBI CORE WALKTHROUGH STRUCTURE VERIFICATION")
    print("="*70)
    
    # Teaching walkthroughs to verify
    teaching_walkthroughs = [
        ("DEVELOPER_WALKTHROUGH_FUNCTIONS.md", 6),  # 6 missions expected
        ("DEVELOPER_WALKTHROUGH_PHASE_1.md", None),
        ("DEVELOPER_WALKTHROUGH_PHASE_2.md", None),
        ("DEVELOPER_WALKTHROUGH_PHASE_3.md", None),
        ("DEVELOPER_WALKTHROUGH_PHASE_4.md", None),
    ]
    
    results = []
    
    for filename, expected_missions in teaching_walkthroughs:
        filepath = walkthroughs_dir / filename
        
        if filepath.exists():
            is_valid = verify_walkthrough(filepath, expected_missions)
            results.append((filename, is_valid))
        else:
            print(f"\n[!] SKIPPED: {filename} (not found)")
            results.append((filename, None))
    
    # Summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70 + "\n")
    
    for filename, is_valid in results:
        if is_valid is None:
            status = "[!] NOT FOUND"
        elif is_valid:
            status = "[OK] VALID"
        else:
            status = "[!] NEEDS REVIEW"
        
        print(f"   {status}  {filename}")
    
    print()


if __name__ == "__main__":
    main()
