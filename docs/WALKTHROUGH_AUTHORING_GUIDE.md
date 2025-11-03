# Walkthrough Authoring Guide - Code Block Best Practices

## 🎯 Quick Reference

### Code Fence Tags

| Tag | Purpose | Shows Run Button? | Example Use Case |
|-----|---------|-------------------|------------------|
| ````python[run]` | Interactive demo | ✅ Yes | Pandas operations students should try |
| ````python[pandas]` | Pandas-specific runnable | ✅ Yes | DataFrame transformations |
| ````python[spark]` | Spark-specific runnable | ✅ Yes | Spark DataFrame operations |
| ````python[demo]` | Teaching fragment | ❌ No | Class method to add to file |
| ````python` (no tag) | **DEFAULT: Teaching fragment** | ❌ No | Code structure examples |
| ````bash` | Shell commands | ❌ No | Installation instructions |

---

## 📖 When to Use Each Tag

### Use `[run]` or `[pandas]` for:
✅ Complete, self-contained examples  
✅ Code that demonstrates a concept through output  
✅ Checkpoint exercises for students to validate understanding  
✅ Interactive experiments (modify and re-run)

**Example**:
````markdown
```python[run]
import pandas as pd
df = pd.DataFrame({'name': ['Alice', 'Bob'], 'age': [25, 30]})
print(df.describe())
```
````

### Use `[demo]` or no tag for:
✅ Class/method definitions students write in files  
✅ Partial code snippets showing structure  
✅ Code with dependencies on surrounding file context  
✅ Multi-file code that can't run standalone

**Example**:
````markdown
```python[demo]
class NodeBase(ABC):
    def __init__(self, step: Step):
        self.step = step
    
    @abstractmethod
    def run(self, data_map: Dict) -> Dict:
        pass
```
````

---

## ✅ Runnable Code Checklist

Before tagging as `[run]`:

- [ ] Code has all necessary imports
- [ ] No references to `self` without class context
- [ ] No `return` statements outside functions
- [ ] Brackets/parentheses are balanced
- [ ] Code can execute in isolation
- [ ] Output is meaningful for learning

---

## 🎨 UI Behavior

### Teaching Fragment (`[demo]` or untagged)
```
📖 Teaching Example
💡 This is teaching content showing code structure to create in your files.
   It's not meant to run interactively here. Use the Copy button.

[Code display]
[Copy button]
```

### Runnable Code (`[run]`, `[pandas]`, `[spark]`)
```
✅ Pre-flight Check: PASSED

[Code display]
[Run Code button] [Reset button]

[Output display area]
[Modify & Experiment section]
```

---

## 🚨 Common Mistakes

### ❌ Don't Do This
````markdown
Step 3: Add this method to NodeBase

```python
def run(self, data_map):
    return data_map
```
````

**Problem**: Untagged python → treated as runnable → fails with "self not defined"

### ✅ Do This Instead
````markdown
Step 3: Add this method to NodeBase

```python[demo]
def run(self, data_map):
    return data_map
```
````

Or, make it runnable:
````markdown
Step 3: Test the Node concept

```python[run]
from odibi_core.core.node import NodeBase, Step

class TestNode(NodeBase):
    def run(self, data_map):
        print(f"Processing: {data_map}")
        return data_map

# Try it
step = Step(layer='test', name='demo', type='function', engine='pandas', value='test')
node = TestNode(step, None, None, None)
result = node.run({'input': 'data'})
```
````

---

## 📊 Validation

### Test Your Walkthrough
```bash
python validate_all_walkthroughs.py
```

**Expected output**:
- All `[demo]` blocks: skipped (no execution attempt)
- All `[run]` blocks: executed and passed
- Success rate: 90%+

### Fix Failing Blocks
1. Check error message
2. Add missing imports
3. Make code self-contained
4. Or re-tag as `[demo]` if it's teaching structure

---

## 💡 Pro Tips

1. **Default to [demo]**: When in doubt, use `[demo]` tag explicitly
2. **One runnable per concept**: Don't overwhelm with too many interactive blocks
3. **Progressive complexity**: Early walkthroughs have more `[run]`, advanced ones more `[demo]`
4. **Copy-paste test**: If you can't copy-paste the code into a fresh Python file and run it, tag as `[demo]`

---

## 🎓 Philosophy

> Developer walkthroughs teach BUILDING a framework (architecture, structure, design).  
> Interactive blocks serve as checkpoints, not the primary teaching method.

**Teaching fragments (majority)**: "Here's the code to write in node.py"  
**Interactive blocks (minority)**: "Run this to verify you understand the concept"

---

## 📚 Examples from Real Walkthroughs

### Good Teaching Fragment
````markdown
### Step 5: Create NodeBase Contract

**Create**: `odibi_core/core/node.py`

```python[demo]
from abc import ABC, abstractmethod
from typing import Dict, Any

class NodeBase(ABC):
    """Base class for all ODIBI nodes."""
    
    @abstractmethod
    def run(self, data_map: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the node operation."""
        pass
```

**Why this works**: Shows the interface students need to implement. Not meant to run standalone.
````

### Good Interactive Block
````markdown
### Step 12: Test Your First Node

Now let's verify the concept works end-to-end:

```python[run]
import pandas as pd
from odibi_core import PandasEngineContext

# Create a simple DataFrame
df = pd.DataFrame({'value': [1, 2, 3, 4, 5]})

# Use the engine context
ctx = PandasEngineContext()
result = ctx.sql("SELECT AVG(value) as mean FROM data", data=df)
print(f"Mean: {result['mean'].iloc[0]}")
```

**Expected output**: `Mean: 3.0`
````

---

## 🔗 Related Docs

- [Full Validation Report](../LEARNODIBI_EXECUTION_VALIDATION_REPORT.md)
- [Upgrade Summary](../LEARNODIBI_UPGRADE_SUMMARY.md)
- [Parser Implementation](../odibi_core/learnodibi_ui/walkthrough_parser.py)

---

**Last Updated**: 2025-11-02  
**Applies To**: All DEVELOPER_WALKTHROUGH_*.md files
