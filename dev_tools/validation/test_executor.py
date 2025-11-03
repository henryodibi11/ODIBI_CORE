"""Quick test of CodeExecutor functionality"""
from odibi_core.learnodibi_ui.code_executor import CodeExecutor

# Test 1: Basic pandas operation
print("=== Test 1: Basic Pandas ===")
executor = CodeExecutor(engine='pandas')
result = executor.execute("""
import pandas as pd
df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
print(df)
df
""")
print(f"Success: {result['success']}")
print(f"Output: {result['output']}")
print(f"Result type: {type(result['result'])}")
print()

# Test 2: Session persistence
print("=== Test 2: Session Persistence ===")
result1 = executor.execute("x = 42")
result2 = executor.execute("print(f'x = {x}')")
print(f"Test 2 Success: {result2['success']}")
print(f"Output: {result2['output']}")
print()

# Test 3: Error handling
print("=== Test 3: Error Handling ===")
result = executor.execute("1 / 0")
print(f"Success: {result['success']}")
print(f"Error: {result['error'][:100]}...")
print()

# Test 4: Pre-flight check
print("=== Test 4: Pre-flight Syntax Check ===")
preflight = executor.preflight_check("def bad syntax")
print(f"Preflight passed: {preflight.passed}")
print(f"Error: {preflight.error_msg}")
print()

print("✅ All executor tests complete!")
