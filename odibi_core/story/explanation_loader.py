"""
Explanation loader for step narratives.

Loads and manages step-level explanations that provide context in generated stories.
Supports JSON, Markdown, and Python dict formats.
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StepExplanation:
    """
    Container for step explanation content.

    Attributes:
        step_name: Name of the step this explains
        purpose: What the step does
        details: How it works (list of bullet points or paragraphs)
        formulas: Optional formulas or calculations
        added_columns: Columns added by this step
        result: Expected outcome
        notes: Additional notes or warnings
    """

    def __init__(
        self,
        step_name: str,
        purpose: str = "",
        details: List[str] = None,
        formulas: Dict[str, str] = None,
        added_columns: List[str] = None,
        result: str = "",
        notes: List[str] = None,
    ):
        self.step_name = step_name
        self.purpose = purpose
        self.details = details or []
        self.formulas = formulas or {}
        self.added_columns = added_columns or []
        self.result = result
        self.notes = notes or []

    def to_markdown(self) -> str:
        """
        Convert explanation to Markdown format.

        Returns:
            Markdown string

        Example:
            >>> md = explanation.to_markdown()
        """
        lines = []

        if self.purpose:
            lines.append("**Purpose:**")
            lines.append(self.purpose)
            lines.append("")

        if self.details:
            lines.append("**Details:**")
            for detail in self.details:
                if not detail.startswith("-"):
                    lines.append(f"- {detail}")
                else:
                    lines.append(detail)
            lines.append("")

        if self.formulas:
            lines.append("**Formulas:**")
            lines.append("")
            lines.append("| Column | Formula |")
            lines.append("|--------|---------|")
            for col, formula in self.formulas.items():
                lines.append(f"| `{col}` | {formula} |")
            lines.append("")

        if self.added_columns:
            lines.append("**Added Columns:**")
            for col in self.added_columns:
                lines.append(f"- `{col}`")
            lines.append("")

        if self.result:
            lines.append("**Result:**")
            lines.append(self.result)
            lines.append("")

        if self.notes:
            lines.append("**Notes:**")
            for note in self.notes:
                if not note.startswith("-"):
                    lines.append(f"- {note}")
                else:
                    lines.append(note)
            lines.append("")

        return "\n".join(lines)


class ExplanationLoader:
    """
    Load step explanations from various sources.

    Supports:
    - JSON file (array of explanation objects)
    - Markdown files (one per step)
    - Python dict (inline in config metadata)

    Example:
        >>> loader = ExplanationLoader()
        >>> explanations = loader.load("explanations.json")
        >>> exp = explanations.get("calc_efficiency")
        >>> print(exp.to_markdown())
    """

    def load(self, source: str) -> Dict[str, StepExplanation]:
        """
        Load explanations from source.

        Args:
            source: Path to JSON file, directory of Markdown files, or dict

        Returns:
            Dict mapping step_name → StepExplanation

        Example:
            >>> explanations = loader.load("project/explanations.json")
            >>> exp = explanations["filter_high_value"]
        """
        if isinstance(source, dict):
            return self._load_from_dict(source)

        path = Path(source)

        if not path.exists():
            logger.warning(f"Explanation source not found: {source}")
            return {}

        if source.endswith(".json"):
            return self._load_from_json(source)
        elif path.is_dir():
            return self._load_from_markdown_dir(source)
        else:
            logger.warning(f"Unknown explanation format: {source}")
            return {}

    def _load_from_json(self, json_path: str) -> Dict[str, StepExplanation]:
        """
        Load from JSON file.

        Expected format:
        [
            {
                "step_name": "calc_efficiency",
                "purpose": "Calculate boiler efficiency",
                "details": ["Uses IAPWS-97", "Converts units"],
                "formulas": {"Efficiency": "(output / input) × 100"},
                "result": "Adds efficiency column"
            },
            ...
        ]
        """
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        explanations = {}
        for item in data:
            exp = StepExplanation(
                step_name=item["step_name"],
                purpose=item.get("purpose", ""),
                details=item.get("details", []),
                formulas=item.get("formulas", {}),
                added_columns=item.get("added_columns", []),
                result=item.get("result", ""),
                notes=item.get("notes", []),
            )
            explanations[exp.step_name] = exp

        logger.info(f"Loaded {len(explanations)} explanations from JSON")
        return explanations

    def _load_from_dict(self, data: Dict[str, Any]) -> Dict[str, StepExplanation]:
        """
        Load from Python dict.

        Format: step_name → explanation text or dict
        """
        explanations = {}

        for step_name, content in data.items():
            if isinstance(content, str):
                # Simple string explanation
                exp = StepExplanation(step_name=step_name, purpose=content)
            elif isinstance(content, dict):
                # Structured explanation
                exp = StepExplanation(
                    step_name=step_name,
                    purpose=content.get("purpose", ""),
                    details=content.get("details", []),
                    formulas=content.get("formulas", {}),
                    added_columns=content.get("added_columns", []),
                    result=content.get("result", ""),
                    notes=content.get("notes", []),
                )
            else:
                continue

            explanations[step_name] = exp

        return explanations

    def _load_from_markdown_dir(self, dir_path: str) -> Dict[str, StepExplanation]:
        """
        Load from directory of Markdown files.

        Each file named {step_name}.md contains the explanation.
        """
        explanations = {}
        md_files = Path(dir_path).glob("*.md")

        for md_file in md_files:
            step_name = md_file.stem
            content = md_file.read_text(encoding="utf-8")

            # Parse Markdown sections
            exp = self._parse_markdown(step_name, content)
            explanations[step_name] = exp

        logger.info(f"Loaded {len(explanations)} explanations from Markdown")
        return explanations

    def _parse_markdown(self, step_name: str, content: str) -> StepExplanation:
        """
        Parse Markdown content into StepExplanation.

        Looks for sections: **Purpose:**, **Details:**, **Result:**
        """
        lines = content.split("\n")
        purpose = ""
        details = []
        result = ""
        current_section = None

        for line in lines:
            line = line.strip()

            if line.startswith("**Purpose:**"):
                current_section = "purpose"
                continue
            elif line.startswith("**Details:**"):
                current_section = "details"
                continue
            elif line.startswith("**Result:**"):
                current_section = "result"
                continue

            if current_section == "purpose" and line:
                purpose += line + " "
            elif current_section == "details" and line:
                if line.startswith("-"):
                    details.append(line[1:].strip())
                else:
                    details.append(line)
            elif current_section == "result" and line:
                result += line + " "

        return StepExplanation(
            step_name=step_name,
            purpose=purpose.strip(),
            details=details,
            result=result.strip(),
        )
