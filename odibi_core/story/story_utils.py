"""
HTML utilities for story generation.

Provides lightweight HTML helpers without external dependencies.
"""

from typing import Any, Dict, List
import html


def render_table(
    data: List[Dict[str, Any]], max_rows: int = 20, caption: str = None
) -> str:
    """
    Render data as HTML table.

    Args:
        data: List of dicts with table data
        max_rows: Maximum rows to display
        caption: Optional table caption

    Returns:
        HTML table string
    """
    if not data:
        return "<p><em>No data</em></p>"

    # Limit rows
    data = data[:max_rows]

    # Extract columns
    columns = list(data[0].keys()) if data else []

    html_parts = ['<table class="data-table">']

    if caption:
        html_parts.append(f"<caption>{html.escape(caption)}</caption>")

    # Header
    html_parts.append("<thead><tr>")
    for col in columns:
        html_parts.append(f"<th>{html.escape(str(col))}</th>")
    html_parts.append("</tr></thead>")

    # Body
    html_parts.append("<tbody>")
    for row in data:
        html_parts.append("<tr>")
        for col in columns:
            value = row.get(col, "")
            html_parts.append(f"<td>{html.escape(str(value))}</td>")
        html_parts.append("</tr>")
    html_parts.append("</tbody>")

    html_parts.append("</table>")

    return "".join(html_parts)


def render_schema_diff(schema_diff: Dict[str, Any]) -> str:
    """
    Render schema diff as HTML.

    Args:
        schema_diff: Dict with added_columns, removed_columns, changed_types

    Returns:
        HTML string
    """
    if not schema_diff:
        return "<p><em>No schema changes</em></p>"

    html_parts = ['<div class="schema-diff">']

    # Added columns
    if schema_diff.get("added_columns"):
        html_parts.append('<div class="schema-added">')
        html_parts.append("<strong>Added Columns:</strong>")
        html_parts.append("<ul>")
        for col in schema_diff["added_columns"]:
            html_parts.append(f'<li class="added">+ {html.escape(col)}</li>')
        html_parts.append("</ul>")
        html_parts.append("</div>")

    # Removed columns
    if schema_diff.get("removed_columns"):
        html_parts.append('<div class="schema-removed">')
        html_parts.append("<strong>Removed Columns:</strong>")
        html_parts.append("<ul>")
        for col in schema_diff["removed_columns"]:
            html_parts.append(f'<li class="removed">- {html.escape(col)}</li>')
        html_parts.append("</ul>")
        html_parts.append("</div>")

    # Changed types
    if schema_diff.get("changed_types"):
        html_parts.append('<div class="schema-changed">')
        html_parts.append("<strong>Type Changes:</strong>")
        html_parts.append("<ul>")
        for change in schema_diff["changed_types"]:
            col = change["column"]
            before = change["before"]
            after = change["after"]
            html_parts.append(
                f'<li class="changed">~ {html.escape(col)}: '
                f"{html.escape(str(before))} → {html.escape(str(after))}</li>"
            )
        html_parts.append("</ul>")
        html_parts.append("</div>")

    html_parts.append("</div>")

    return "".join(html_parts)


def render_collapsible(title: str, content: str, default_open: bool = False) -> str:
    """
    Render collapsible section.

    Args:
        title: Section title
        content: HTML content
        default_open: Whether section is open by default

    Returns:
        HTML string with details/summary tags
    """
    open_attr = " open" if default_open else ""

    return f"""
<details{open_attr}>
    <summary><strong>{html.escape(title)}</strong></summary>
    <div class="collapsible-content">
        {content}
    </div>
</details>
"""


def get_inline_css() -> str:
    """
    Get inline CSS for story pages.

    Returns:
        CSS string
    """
    return """
<style>
    body {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
        background: #f5f5f5;
        color: #333;
    }
    
    .story-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 8px;
        margin-bottom: 30px;
    }
    
    .story-header h1 {
        margin: 0 0 10px 0;
    }
    
    .story-header .meta {
        opacity: 0.9;
        font-size: 14px;
    }
    
    .step-card {
        background: white;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .step-card h2 {
        margin-top: 0;
        color: #667eea;
    }
    
    .step-card .step-meta {
        font-size: 13px;
        color: #666;
        margin-bottom: 15px;
    }
    
    .step-card.success {
        border-left: 4px solid #10b981;
    }
    
    .step-card.failed {
        border-left: 4px solid #ef4444;
    }
    
    table.data-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 13px;
        margin: 15px 0;
    }
    
    table.data-table th {
        background: #f3f4f6;
        text-align: left;
        padding: 8px 12px;
        font-weight: 600;
        border-bottom: 2px solid #e5e7eb;
    }
    
    table.data-table td {
        padding: 8px 12px;
        border-bottom: 1px solid #e5e7eb;
    }
    
    table.data-table tbody tr:hover {
        background: #f9fafb;
    }
    
    .schema-diff {
        margin: 15px 0;
    }
    
    .schema-diff ul {
        list-style: none;
        padding-left: 0;
    }
    
    .schema-diff li {
        padding: 4px 0;
        font-family: monospace;
        font-size: 13px;
    }
    
    .schema-diff li.added {
        color: #10b981;
    }
    
    .schema-diff li.removed {
        color: #ef4444;
    }
    
    .schema-diff li.changed {
        color: #f59e0b;
    }
    
    details {
        margin: 15px 0;
    }
    
    summary {
        cursor: pointer;
        padding: 10px;
        background: #f3f4f6;
        border-radius: 4px;
        user-select: none;
    }
    
    summary:hover {
        background: #e5e7eb;
    }
    
    .collapsible-content {
        padding: 15px 10px;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 15px;
        margin: 20px 0;
    }
    
    .stat-card {
        background: white;
        padding: 15px;
        border-radius: 6px;
        text-align: center;
    }
    
    .stat-card .value {
        font-size: 32px;
        font-weight: bold;
        color: #667eea;
    }
    
    .stat-card .label {
        font-size: 12px;
        color: #666;
        text-transform: uppercase;
    }
    
    code {
        background: #f3f4f6;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
    }
    
    pre {
        background: #1f2937;
        color: #f3f4f6;
        padding: 15px;
        border-radius: 6px;
        overflow-x: auto;
    }
    
    .footer {
        margin-top: 40px;
        padding-top: 20px;
        border-top: 1px solid #e5e7eb;
        text-align: center;
        color: #666;
        font-size: 12px;
    }
    
    .explanation {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        padding: 15px;
        margin: 15px 0;
        border-radius: 4px;
    }
    
    .explanation p {
        margin: 8px 0;
        line-height: 1.6;
    }
    
    .explanation ul, .explanation ol {
        margin: 8px 0;
        padding-left: 25px;
        line-height: 1.6;
    }
    
    .explanation li {
        margin: 4px 0;
    }
    
    .explanation code {
        background: #fef9c3;
        color: #78350f;
        padding: 2px 6px;
        border-radius: 3px;
        font-family: 'Courier New', Consolas, monospace;
        font-size: 0.9em;
    }
    
    .explanation pre {
        background: #1f2937;
        color: #f3f4f6;
        padding: 12px;
        border-radius: 6px;
        overflow-x: auto;
        margin: 12px 0;
        font-family: 'Courier New', Consolas, monospace;
        font-size: 0.85em;
    }
    
    .explanation pre code {
        background: transparent;
        color: inherit;
        padding: 0;
    }
    
    .explanation table {
        width: 100%;
        margin: 12px 0;
        border-collapse: collapse;
        font-size: 0.9em;
    }
    
    .explanation th {
        background: #fde68a;
        border: 1px solid #e5e7eb;
        padding: 8px 12px;
        text-align: left;
        font-weight: 600;
        color: #92400e;
    }
    
    .explanation td {
        border: 1px solid #e5e7eb;
        padding: 6px 12px;
        background: white;
    }
    
    .explanation tr:hover td {
        background: #fffbeb;
    }
    
    .explanation strong {
        color: #92400e;
        font-weight: 600;
    }
    
    .explanation em {
        color: #b45309;
        font-style: italic;
    }
    
    .explanation h4 {
        color: #92400e;
        margin: 15px 0 8px 0;
        font-size: 1em;
    }
</style>
"""
