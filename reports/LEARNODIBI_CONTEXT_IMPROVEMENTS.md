# LearnODIBI Context Display Improvements

**Date**: 2025-11-02  
**Focus**: UI Context Panel Clarity and Key Concepts

---

## Current Context Panel Behavior

### Step Status Indicators
The context panel shows completion status for each step:

- ✅ **Completed** (green) - Step code was successfully executed
- ⏳ **Not Started** (gray) - Step has not been executed yet

**This is working as designed** - steps start as "Not Started" and change to "Completed" when you click "Run This Code" and it executes successfully.

---

## Key Concepts (Tags) Extraction

### How Tags Are Extracted
The parser automatically extracts key concepts from each step by finding:
1. **Bold terms**: `**Concept**` in the markdown
2. **Code terms**: `` `function_name` `` in the explanation

### Current Tag Quality Issues

#### Problem
Some extracted tags are not meaningful:
- Generic words like "Example", "Create", "Test"
- File paths instead of concepts
- Too technical or too vague

#### Examples from Walkthroughs
```
Step 1: Setup Your Workspace
  Current tags: ['Workspace', 'Setup', 'Create']
  Better tags: ['Project Structure', 'Virtual Environment', 'Dependencies']

Step 5: Create NodeBase Contract
  Current tags: ['NodeBase', 'ABC', 'abstractmethod']
  Better tags: ['Abstract Base Class', 'Node Interface', 'Data Pipeline Node']
```

---

## Recommended Improvements

### 1. Enhanced Tag Extraction (High Priority)

**File**: `odibi_core/learnodibi_ui/walkthrough_parser.py`

**Current Logic**:
```python
def _extract_tags(self, text: str) -> List[str]:
    tags = []
    tag_patterns = [
        r'\*\*([A-Z][a-zA-Z\s]+)\*\*',  # Bold terms
        r'`([a-zA-Z_]+)`',              # Code terms
    ]
    # ... deduplicate and limit to 10
```

**Proposed Improvements**:
```python
def _extract_tags(self, text: str) -> List[str]:
    tags = []
    
    # 1. Look for explicit "Key Concepts:" sections
    concepts_match = re.search(r'Key Concepts?:(.+?)(?:\n\n|$)', text, re.DOTALL)
    if concepts_match:
        # Extract bullet points
        concepts = re.findall(r'[-*]\s+(.+)', concepts_match.group(1))
        tags.extend([c.strip() for c in concepts])
    
    # 2. Extract from **bold** terms (but filter common words)
    bold_terms = re.findall(r'\*\*([A-Z][a-zA-Z\s]+)\*\*', text)
    skip_words = {'Example', 'Create', 'Test', 'Note', 'Important', 
                  'Why', 'What', 'How', 'Step', 'Mission', 'Checkpoint'}
    tags.extend([t for t in bold_terms if t not in skip_words and len(t) > 5])
    
    # 3. Extract key function/class names from code blocks
    code_names = re.findall(r'`([A-Z][a-zA-Z0-9_]+)`', text)  # PascalCase only
    tags.extend(code_names)
    
    # 4. Look for "Learn:" or "Teaches:" sections
    learn_match = re.search(r'(?:Learn|Teaches):(.+?)(?:\n\n|$)', text)
    if learn_match:
        tags.extend([item.strip() for item in learn_match.group(1).split(',')])
    
    # Deduplicate, filter, and limit
    seen = set()
    meaningful_tags = []
    for tag in tags:
        tag_clean = tag.strip()
        if (tag_clean and tag_clean not in seen and 
            len(tag_clean) > 3 and 
            not tag_clean.startswith('/')  # Skip file paths
        ):
            seen.add(tag_clean)
            meaningful_tags.append(tag_clean)
            if len(meaningful_tags) >= 8:  # Limit to 8 most relevant
                break
    
    return meaningful_tags
```

### 2. Manual Tag Curation (Medium Priority)

Add explicit tag metadata to walkthrough markdown:

```markdown
### Step 1: Setup Your Workspace

<!-- TAGS: Project Structure, Virtual Environment, Dependencies, Git Setup -->

**Goal**: Set up a clean development environment for ODIBI CORE.

...
```

Parser would extract from HTML comments:
```python
tag_match = re.search(r'<!-- TAGS: (.+?) -->', text)
if tag_match:
    tags = [t.strip() for t in tag_match.group(1).split(',')]
```

### 3. Context Panel Enhancements (Low Priority)

**File**: `odibi_core/learnodibi_ui/pages/0_guided_learning.py`

**Current**:
```python
# Tags
if step.tags:
    st.markdown("**📍 Key Concepts:**")
    for tag in step.tags[:5]:
        st.markdown(f"- {tag}")
```

**Enhanced**:
```python
# Tags with visual badges
if step.tags:
    st.markdown("**📍 Key Concepts:**")
    
    # Show as colored badges instead of bullet list
    tag_html = "<div style='display: flex; flex-wrap: wrap; gap: 0.5rem;'>"
    for tag in step.tags[:5]:
        tag_html += f"""
        <span style='
            background: {COLORS['primary']}; 
            color: white; 
            padding: 0.25rem 0.75rem; 
            border-radius: 12px; 
            font-size: 0.85rem;
        '>{tag}</span>
        """
    tag_html += "</div>"
    st.markdown(tag_html, unsafe_allow_html=True)
```

---

## Immediate Actions (Quick Wins)

### Action 1: Filter Generic Tags
**Effort**: 5 minutes  
**Impact**: Medium

Add filter list to remove generic/meaningless tags:
```python
SKIP_TAGS = {
    'Example', 'Create', 'Test', 'Note', 'Important', 
    'Why', 'What', 'How', 'Step', 'Mission', 'Checkpoint',
    'Setup', 'Build', 'Run', 'Install', 'Configure'
}

# In _extract_tags():
if tag_clean not in SKIP_TAGS and len(tag_clean) > 3:
    meaningful_tags.append(tag_clean)
```

### Action 2: Prioritize Explicit Key Concepts
**Effort**: 10 minutes  
**Impact**: High

Look for "Key Concepts:" sections first:
```python
# Priority 1: Explicit concepts section
concepts_section = re.search(r'(?:Key Concepts?|What You.*Learn):(.+?)(?:\n\n|###)', text, re.DOTALL)
if concepts_section:
    concepts = re.findall(r'[-*]\s+(.+)', concepts_section.group(1))
    return [c.strip() for c in concepts[:8]]
```

### Action 3: Add Fallback to Step Title
**Effort**: 2 minutes  
**Impact**: Low

If no tags extracted, use words from step title:
```python
if not meaningful_tags and step.title:
    # Extract key words from title (ignore common words)
    title_words = [w for w in step.title.split() 
                   if len(w) > 4 and w.lower() not in SKIP_TAGS]
    return title_words[:3]
```

---

## Status Indicator Clarification

### Current Behavior (Correct)
```
⏳ Not Started - Default state, turns green after successful execution
✅ Completed   - Step code ran successfully
```

### Proposed Additional States (Optional)
```
⏳ Not Started - Default state
▶️ In Progress - User clicked "Run" button (during execution)
✅ Completed   - Code ran successfully
❌ Failed      - Code execution failed (show error state)
⚠️ Modified    - User modified code in "Modify & Experiment"
```

**Implementation**:
```python
# In session state
if 'step_status' not in st.session_state:
    st.session_state.step_status = {}  # {step_num: 'not_started'|'running'|'completed'|'failed'}

# During execution
st.session_state.step_status[step.step_number] = 'running'
# ... execute code ...
if result['success']:
    st.session_state.step_status[step.step_number] = 'completed'
else:
    st.session_state.step_status[step.step_number] = 'failed'

# Display
status = st.session_state.step_status.get(step.step_number, 'not_started')
status_display = {
    'not_started': ('⏳', 'Not Started', COLORS['surface']),
    'running': ('▶️', 'Running...', COLORS['info']),
    'completed': ('✅', 'Completed', COLORS['success']),
    'failed': ('❌', 'Error', COLORS['error']),
}
icon, label, color = status_display[status]
st.markdown(f"<div style='background: {color}; ...'>'{icon} {label}</div>", ...)
```

---

## Sample Output After Improvements

### Before
```
📌 Quick Info
⏳ Not Started

🔧 Engine: PANDAS

📍 Key Concepts:
- Create
- Setup
- Example
- Test
- Config
```

### After
```
📌 Quick Info
⏳ Not Started

🔧 Engine: PANDAS

📍 Key Concepts:
[Project Structure] [Virtual Environment] [Git Configuration] 
[Dependency Management] [Testing Setup]
```

---

## Implementation Priority

### High Priority (Do Before Launch)
1. ✅ **Filter generic tags** - Remove "Create", "Example", etc.
2. ✅ **Prioritize explicit Key Concepts sections** - Look for markdown lists under "Key Concepts:"
3. ⚠️ **Test with all 11 walkthroughs** - Verify tag quality

### Medium Priority (Post-Launch Enhancement)
4. Add explicit tag metadata to walkthrough markdown
5. Enhance context panel with badge-style tag display
6. Add more nuanced status indicators (Running, Failed, Modified)

### Low Priority (Future)
7. Add tag search/filter in UI
8. Show related steps with same tags
9. Track "concept mastery" (how many steps with tag X completed)

---

## Next Steps

1. **Quick Fix Now**: Apply filter list for generic tags
2. **Validation**: Run walkthrough_parser on all files and review extracted tags
3. **Documentation**: Update AGENTS.md with tag extraction rules
4. **Testing**: Load a walkthrough in UI and verify tag quality

---

*Document created 2025-11-02 - Tag extraction and context panel improvements*
