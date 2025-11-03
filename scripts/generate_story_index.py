"""
Generate HTML index for all showcase stories
"""

from pathlib import Path
from datetime import datetime

base_path = Path("D:/projects/odibi_core")
output_path = base_path / "resources/output/creative_showcases"
stories_index = output_path / "SHOWCASE_STORIES_INDEX.html"

# Find all story HTML files
story_dirs = sorted([d for d in output_path.iterdir() if d.is_dir() and d.name.startswith("showcase_")])

html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ODIBI_CORE Creative Showcase Stories</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        
        .header {{
            background: white;
            padding: 40px;
            border-radius: 12px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            margin: 0 0 10px 0;
            color: #667eea;
        }}
        
        .header p {{
            color: #666;
            margin: 5px 0;
        }}
        
        .showcase-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
        }}
        
        .showcase-card {{
            background: white;
            border-radius: 8px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s, box-shadow 0.2s;
        }}
        
        .showcase-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.15);
        }}
        
        .showcase-card h3 {{
            margin: 0 0 10px 0;
            color: #667eea;
            font-size: 18px;
        }}
        
        .showcase-card .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 600;
            margin-right: 5px;
            margin-bottom: 10px;
        }}
        
        .badge.simple {{ background: #dbeafe; color: #1e40af; }}
        .badge.medium {{ background: #fef3c7; color: #92400e; }}
        .badge.advanced {{ background: #fecaca; color: #991b1b; }}
        
        .showcase-card .description {{
            color: #666;
            font-size: 14px;
            margin-bottom: 15px;
        }}
        
        .showcase-card a {{
            display: inline-block;
            background: #667eea;
            color: white;
            text-decoration: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
        }}
        
        .showcase-card a:hover {{
            background: #5568d3;
        }}
        
        .stats {{
            display: flex;
            gap: 30px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #e5e7eb;
        }}
        
        .stat {{
            text-align: center;
        }}
        
        .stat .number {{
            font-size: 32px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat .label {{
            font-size: 14px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎨 ODIBI_CORE Creative Showcase Stories</h1>
        <p><strong>100 Story-Driven Pipelines</strong> demonstrating ODIBI_CORE's native orchestration</p>
        <p>Each story shows data transformations, schema evolution, and pipeline execution flow</p>
        
        <div class="stats">
            <div class="stat">
                <div class="number">{len(story_dirs)}</div>
                <div class="label">Stories Generated</div>
            </div>
            <div class="stat">
                <div class="number">10</div>
                <div class="label">Domains</div>
            </div>
            <div class="stat">
                <div class="number">6</div>
                <div class="label">DAG Topologies</div>
            </div>
        </div>
    </div>
    
    <div class="showcase-grid">
"""

# Add each showcase
for story_dir in story_dirs:
    showcase_num = int(story_dir.name.split("_")[1])
    
    # Find the HTML file in this directory
    html_files = list(story_dir.glob("*.html"))
    if not html_files:
        continue
    
    html_file = html_files[0]
    rel_path = html_file.relative_to(output_path)
    
    # Determine complexity
    if showcase_num <= 20:
        complexity = "simple"
    elif showcase_num <= 70:
        complexity = "medium"
    else:
        complexity = "advanced"
    
    html_content += f"""
        <div class="showcase-card">
            <h3>Showcase #{showcase_num:03d}</h3>
            <span class="badge {complexity}">{complexity.upper()}</span>
            <div class="description">
                Interactive HTML visualization showing pipeline execution, data transformations, and schema evolution
            </div>
            <a href="{rel_path.as_posix()}" target="_blank">View Story →</a>
        </div>
"""

html_content += """
    </div>
    
    <div style="text-align: center; margin-top: 40px; color: white;">
        <p><strong>ODIBI_CORE</strong> | Creative Showcase Suite v1.0</p>
        <p>Generated: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
    </div>
</body>
</html>
"""

stories_index.write_text(html_content, encoding='utf-8')
print(f"Story index created: {stories_index}")
print(f"Open in browser: file:///{stories_index.as_posix()}")
