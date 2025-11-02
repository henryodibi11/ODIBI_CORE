"""
HTML story generation for pipeline execution visualization.

Generates interactive HTML reports with:
- Step cards (inputs, outputs, timing)
- Schema before/after comparisons
- Sample data tables
- Execution summary
"""

import html as html_module
from typing import Any, Dict, List, Optional
from pathlib import Path
from odibi_core.story.story_utils import (
    render_table,
    render_schema_diff,
    render_collapsible,
    get_inline_css,
)


try:
    import markdown

    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


class StoryGenerator:
    """
    Generate HTML execution stories.

    Creates visual reports for pipeline runs with snapshots, timing, and lineage.

    Example:
        >>> generator = StoryGenerator()
        >>> html = generator.generate_story(tracker.export_lineage())
        >>> with open("stories/pipeline_story.html", "w") as f:
        ...     f.write(html)
    """

    def __init__(
        self,
        output_dir: str = "stories",
        explanations: Optional[Dict[str, Any]] = None,
        dag_builder: Optional[Any] = None,
    ) -> None:
        """
        Initialize story generator.

        Args:
            output_dir: Directory to save story HTML files
            explanations: Dict mapping step_name → StepExplanation or markdown text
            dag_builder: Optional DAG builder instance for dependency visualization
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.explanations = explanations or {}
        self.dag_builder = dag_builder

    def generate_story(self, lineage: Dict[str, Any], max_rows: int = 20) -> str:
        """
        Generate complete HTML story for pipeline execution.

        Args:
            lineage: Lineage dict from tracker.export_lineage()
            max_rows: Maximum data rows to show in tables

        Returns:
            Complete HTML document string

        Example:
            >>> lineage = tracker.export_lineage()
            >>> html = generator.generate_story(lineage)
        """
        steps = lineage.get("steps", [])
        summary = lineage.get("summary", {})
        pipeline_id = lineage.get("pipeline_id", "unknown")
        start_time = lineage.get("start_time", "unknown")

        html_parts = []

        # HTML header
        html_parts.append(self._render_html_header(pipeline_id))

        # Story header
        html_parts.append(self._render_story_header(pipeline_id, start_time, summary))

        # Summary stats
        html_parts.append(self._render_summary_stats(summary))

        # DAG visualization (if available)
        if self.dag_builder:
            html_parts.append(self._render_dag_visualization())

        # Step cards
        for step_data in steps:
            html_parts.append(self._render_step_card(step_data, max_rows=max_rows))

        # Footer
        html_parts.append(self._render_footer())

        # HTML close
        html_parts.append("</body></html>")

        return "\n".join(html_parts)

    def save_story(self, lineage: Dict[str, Any], filename: str = None) -> str:
        """
        Generate and save story to file.

        Args:
            lineage: Lineage dict from tracker
            filename: Output filename (auto-generated if None)

        Returns:
            Path to saved file

        Example:
            >>> path = generator.save_story(tracker.export_lineage())
            >>> print(f"Story saved to: {path}")
        """
        html_content = self.generate_story(lineage)

        if filename is None:
            pipeline_id = lineage.get("pipeline_id", "run")
            filename = f"story_{pipeline_id}.html"

        filepath = self.output_dir / filename

        # Ensure UTF-8 encoding with BOM for Windows compatibility
        with open(filepath, "w", encoding="utf-8-sig") as f:
            f.write(html_content)

        return str(filepath)

    def _render_html_header(self, title: str) -> str:
        """Render HTML header with inline CSS."""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ODIBI Pipeline Story - {html_module.escape(title)}</title>
    {get_inline_css()}
</head>
<body>
"""

    def _render_story_header(
        self, pipeline_id: str, start_time: str, summary: Dict[str, Any]
    ) -> str:
        """Render story header section."""
        total_duration = summary.get("total_duration_ms", 0)
        duration_sec = total_duration / 1000 if total_duration else 0

        return f"""
<div class="story-header">
    <h1>ODIBI CORE Pipeline Story</h1>
    <div class="meta">
        <strong>Pipeline ID:</strong> {html_module.escape(pipeline_id)}<br>
        <strong>Start Time:</strong> {html_module.escape(str(start_time))}<br>
        <strong>Duration:</strong> {duration_sec:.2f}s
    </div>
</div>
"""

    def _render_summary_stats(self, summary: Dict[str, Any]) -> str:
        """Render summary statistics grid."""
        total_steps = summary.get("total_steps", 0)
        success_count = summary.get("success_count", 0)
        failed_count = summary.get("failed_count", 0)
        success_rate = summary.get("success_rate", 0)

        return f"""
<div class="stats-grid">
    <div class="stat-card">
        <div class="value">{total_steps}</div>
        <div class="label">Total Steps</div>
    </div>
    <div class="stat-card">
        <div class="value">{success_count}</div>
        <div class="label">Success</div>
    </div>
    <div class="stat-card">
        <div class="value">{failed_count}</div>
        <div class="label">Failed</div>
    </div>
    <div class="stat-card">
        <div class="value">{success_rate:.1f}%</div>
        <div class="label">Success Rate</div>
    </div>
</div>
"""

    def _render_step_card(self, step_data: Dict[str, Any], max_rows: int = 20) -> str:
        """Render individual step card."""
        step_name = step_data.get("step_name", "unknown")
        layer = step_data.get("layer", "unknown")
        state = step_data.get("state", "pending")
        duration_ms = step_data.get("duration_ms", 0)
        before_snapshot = step_data.get("before_snapshot")
        after_snapshot = step_data.get("after_snapshot")
        schema_diff = step_data.get("schema_diff")
        row_delta = step_data.get("row_delta")
        error_message = step_data.get("error_message")

        state_class = "success" if state == "success" else "failed"

        html_parts = [f'<div class="step-card {state_class}">']

        # Step header
        html_parts.append(f"<h2>{html_module.escape(step_name)}</h2>")
        html_parts.append(
            f'<div class="step-meta">'
            f"<strong>Layer:</strong> {html_module.escape(layer)} | "
            f"<strong>Status:</strong> {html_module.escape(state)} | "
            f"<strong>Duration:</strong> {duration_ms:.2f}ms"
        )
        if row_delta is not None:
            html_parts.append(f" | <strong>Row Delta:</strong> {row_delta:+d}")
        html_parts.append("</div>")

        # Error message
        if error_message:
            html_parts.append(
                f'<div class="error-message" style="color: #ef4444; padding: 10px; '
                f'background: #fee2e2; border-radius: 4px; margin: 10px 0;">'
                f"<strong>Error:</strong> {html_module.escape(error_message)}</div>"
            )

        # Before snapshot
        if before_snapshot:
            before_content = self._render_snapshot(before_snapshot, "Before", max_rows)
            html_parts.append(render_collapsible("Before Snapshot", before_content))

        # After snapshot
        if after_snapshot:
            after_content = self._render_snapshot(after_snapshot, "After", max_rows)
            html_parts.append(
                render_collapsible("After Snapshot", after_content, default_open=True)
            )

        # Schema diff
        if schema_diff:
            diff_html = render_schema_diff(schema_diff)
            html_parts.append(
                render_collapsible("Schema Changes", diff_html, default_open=True)
            )

        # Explanation (if available)
        explanation = self._get_explanation(step_name)
        if explanation:
            explanation_html = self._render_explanation(explanation)
            html_parts.append(
                render_collapsible(
                    "Step Explanation", explanation_html, default_open=True
                )
            )

        html_parts.append("</div>")

        return "\n".join(html_parts)

    def _get_explanation(self, step_name: str) -> Optional[str]:
        """
        Get explanation for a step.

        Args:
            step_name: Name of the step

        Returns:
            Explanation text (Markdown or plain text) or None
        """
        if not self.explanations:
            return None

        exp = self.explanations.get(step_name)
        if not exp:
            return None

        # If it's a StepExplanation object, convert to markdown
        if hasattr(exp, "to_markdown"):
            return exp.to_markdown()

        # Otherwise assume it's a string
        return str(exp)

    def _render_explanation(self, explanation_text: str) -> str:
        """
        Render explanation text as HTML with enhanced Markdown support.

        Args:
            explanation_text: Markdown or plain text

        Returns:
            HTML string with proper formatting
        """
        # Try full Markdown rendering if library available
        if HAS_MARKDOWN:
            try:
                html = markdown.markdown(
                    explanation_text,
                    extensions=["tables", "fenced_code", "nl2br", "codehilite"],
                )
                return f'<div class="explanation">{html}</div>'
            except:
                # Fallback if markdown rendering fails
                pass

        # Manual Markdown → HTML conversion (enhanced)
        lines = explanation_text.split("\n")
        html_lines = []
        in_list = False
        in_code_block = False
        code_lines = []

        for line in lines:
            # Handle code blocks
            if line.strip().startswith("```"):
                if not in_code_block:
                    # Start code block
                    in_code_block = True
                    code_lang = line.strip()[3:].strip() or "text"
                    code_lines = []
                    continue
                else:
                    # End code block
                    in_code_block = False
                    code_content = "\n".join(code_lines)
                    html_lines.append(
                        f"<pre><code>{html_module.escape(code_content)}</code></pre>"
                    )
                    code_lines = []
                    continue

            if in_code_block:
                code_lines.append(line)
                continue

            line = line.strip()

            if not line:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append("<br>")
                continue

            # Bold: **text** → <strong>text</strong>
            import re

            line = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", line)

            # Italic: *text* → <em>text</em>
            line = re.sub(r"\*(.+?)\*", r"<em>\1</em>", line)

            # Code: `text` → <code>text</code>
            line = re.sub(r"`(.+?)`", r"<code>\1</code>", line)

            # List items
            if line.startswith("- "):
                if not in_list:
                    html_lines.append("<ul>")
                    in_list = True
                html_lines.append(f"<li>{line[2:]}</li>")
            else:
                if in_list:
                    html_lines.append("</ul>")
                    in_list = False
                html_lines.append(f"<p>{line}</p>")

        if in_list:
            html_lines.append("</ul>")

        return f'<div class="explanation">{"".join(html_lines)}</div>'

    def _render_snapshot(
        self, snapshot: Dict[str, Any], title: str, max_rows: int
    ) -> str:
        """Render snapshot section."""
        row_count = snapshot.get("row_count", 0)
        schema = snapshot.get("schema", [])
        sample_data = snapshot.get("sample_data", [])

        html_parts = []

        # Metadata
        html_parts.append(
            f"<p><strong>Row Count:</strong> {row_count:,} | "
            f"<strong>Columns:</strong> {len(schema)}</p>"
        )

        # Schema table
        if schema:
            schema_table_data = [
                {"Column": s["column"], "Type": s["type"]} for s in schema
            ]
            html_parts.append(
                render_collapsible(
                    "Schema",
                    render_table(
                        schema_table_data, max_rows=100, caption="Column Schema"
                    ),
                    default_open=False,
                )
            )

        # Sample data
        if sample_data:
            html_parts.append(
                "<h4>Sample Data</h4>"
                + render_table(
                    sample_data,
                    max_rows=max_rows,
                    caption=f"First {len(sample_data)} rows",
                )
            )

        return "\n".join(html_parts)

    def _render_dag_visualization(self) -> str:
        """
        Render DAG dependency graph visualization.

        Returns:
            HTML with DAG visualization
        """
        html_parts = ['<div class="dag-viz">']
        html_parts.append("<h2>📊 Pipeline Dependency Graph</h2>")

        # Get parallel batches
        batches = self.dag_builder.get_parallel_batches()

        # Render level-by-level view
        html_parts.append(
            '<div class="dag-levels" style="padding: 20px; background: #f9fafb; border-radius: 8px;">'
        )
        html_parts.append(
            f"<p><strong>Execution Levels:</strong> {len(batches)} (nodes at same level run in parallel)</p>"
        )

        for level, batch in enumerate(batches):
            html_parts.append(
                f'<div class="dag-level" style="margin: 15px 0; padding: 15px; background: white; border-left: 4px solid #3b82f6; border-radius: 4px;">'
            )
            html_parts.append(f'<h4 style="margin: 0 0 10px 0;">Level {level}</h4>')
            html_parts.append(
                '<div style="display: flex; flex-wrap: wrap; gap: 10px;">'
            )

            for step in batch:
                node = self.dag_builder.dag[step.name]
                deps_text = (
                    ", ".join(node.dependencies) if node.dependencies else "none"
                )

                # Color by layer
                layer_colors = {
                    "ingest": "#e1f5ff",
                    "store": "#fff3e0",
                    "transform": "#f3e5f5",
                    "publish": "#e8f5e9",
                }
                bg_color = layer_colors.get(step.layer, "#fafafa")

                html_parts.append(
                    f'<div class="dag-node" style="padding: 10px 15px; background: {bg_color}; '
                    f'border-radius: 4px; border: 1px solid #e5e7eb; min-width: 150px;">'
                    f"<strong>{html_module.escape(step.name)}</strong><br>"
                    f'<small style="color: #6b7280;">Layer: {html_module.escape(step.layer)}</small><br>'
                    f'<small style="color: #6b7280;">Depends on: {html_module.escape(deps_text)}</small>'
                    f"</div>"
                )

            html_parts.append("</div>")
            html_parts.append("</div>")

        html_parts.append("</div>")

        # Text-based dependency tree
        html_parts.append('<div style="margin-top: 20px;">')
        html_parts.append("<details>")
        html_parts.append(
            '<summary style="cursor: pointer; font-weight: bold;">View Text Representation</summary>'
        )
        html_parts.append(
            f'<pre style="background: #f3f4f6; padding: 15px; border-radius: 4px; overflow-x: auto;">{html_module.escape(self.dag_builder.visualize())}</pre>'
        )
        html_parts.append("</details>")
        html_parts.append("</div>")

        html_parts.append("</div>")

        return "\n".join(html_parts)

    def _render_footer(self) -> str:
        """Render page footer."""
        return """
<div class="footer">
    Generated by ODIBI CORE v1.0 Story Generator (Phase 5: DAG Execution)<br>
    Framework: Node-centric, engine-agnostic, config-driven data engineering
</div>
"""
