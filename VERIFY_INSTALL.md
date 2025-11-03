# Verify ODIBI CORE Installation

## Quick Test

After installing with `pip install -e .` (or from PyPI), verify everything works:

### 1. Test Package Import
```bash
python -c "import odibi_core; print(f'ODIBI CORE v{odibi_core.__version__} installed successfully')"
```

### 2. Test Walkthroughs Available
```bash
python -c "from odibi_core.learnodibi_ui.walkthrough_parser import get_walkthrough_parser; parser = get_walkthrough_parser(); wts = parser.list_walkthroughs(); print(f'✓ Found {len(wts)} walkthroughs')"
```

### 3. Test Code Executor
```bash
python -c "from odibi_core.learnodibi_ui.code_executor import CodeExecutor; e = CodeExecutor(); r = e.execute('x=42'); print(f'✓ Executor works: {r[\"success\"]}')"
```

### 4. Launch LearnODIBI UI
```bash
python -c "from odibi_core.learnodibi import launch_ui; print('✓ LearnODIBI ready to launch'); launch_ui()"
```

Or simply:
```bash
learnodibi
```

## Expected Output

All tests should pass:
```
✓ ODIBI CORE v1.1.0 installed successfully
✓ Found 12 walkthroughs  
✓ Executor works: True
✓ LearnODIBI ready to launch
```

## Troubleshooting

### "No walkthroughs found!"
**Cause**: Walkthroughs not included in package  
**Fix**: Ensure `odibi_core/docs/walkthroughs/` contains DEVELOPER_WALKTHROUGH_*.md files

Check with:
```bash
python -c "from pathlib import Path; import odibi_core; pkg_path = Path(odibi_core.__file__).parent; wt_path = pkg_path / 'docs' / 'walkthroughs'; print(f'Walkthrough path: {wt_path}'); print(f'Exists: {wt_path.exists()}'); print(f'Files: {len(list(wt_path.glob(\"*.md\")))}')"
```

### "Module not found: odibi_core"
**Cause**: Package not installed  
**Fix**: Run `pip install -e .` from project root

### "Import Error: learnodibi"
**Cause**: Missing streamlit dependency  
**Fix**: Run `pip install streamlit>=1.32.0`

## Clean Reinstall

If issues persist:
```bash
pip uninstall -y odibi-core
pip cache purge
pip install -e .
```

Then re-run verification tests.
