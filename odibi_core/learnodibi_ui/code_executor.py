"""
Code Executor - Safe engine-aware execution with pre-flight validation
Supports Pandas and Spark with isolated namespaces
"""

import sys
import io
import ast
import traceback
import json
from contextlib import redirect_stdout, redirect_stderr
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np


class PreFlightResult:
    """Result of pre-flight syntax validation"""
    def __init__(self, passed: bool, error_msg: str = "", line_no: int = None):
        self.passed = passed
        self.error_msg = error_msg
        self.line_no = line_no
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'passed': self.passed,
            'error_msg': self.error_msg,
            'line_no': self.line_no
        }


class CodeExecutor:
    """Execute code snippets safely with engine-aware isolation"""
    
    def __init__(self, engine: str = "pandas"):
        """
        Initialize executor with specified engine
        
        Args:
            engine: "pandas" or "spark"
        """
        self.engine = engine.lower()
        self.global_namespace = self._initialize_namespace()
        self.execution_log = []
    
    def _initialize_namespace(self) -> Dict[str, Any]:
        """Initialize execution namespace with engine-specific imports and mock data"""
        namespace = {
            '__builtins__': __builtins__,
            'pd': pd,
            'pandas': pd,
            'np': np,
            'numpy': np,
        }
        
        # Auto-inject common typing imports (prevents NameError for type hints)
        from typing import Dict, List, Any, Optional, Tuple, Union
        namespace['Dict'] = Dict
        namespace['List'] = List
        namespace['Any'] = Any
        namespace['Optional'] = Optional
        namespace['Tuple'] = Tuple
        namespace['Union'] = Union
        
        # Bootstrap mock data to prevent NameError in walkthroughs
        namespace['df'] = pd.DataFrame({
            'a': [1, 2, 3, 4, 5],
            'b': [10, 20, 30, 40, 50],
            'c': [100, 200, 300, 400, 500],
            'category': ['A', 'B', 'A', 'C', 'B'],
            'value': [1.1, 2.2, 3.3, 4.4, 5.5]
        })
        
        namespace['sample_data'] = {
            'numbers': [1, 2, 3, 4, 5],
            'letters': ['A', 'B', 'C', 'D', 'E'],
            'data': [[1, 2], [3, 4], [5, 6]]
        }
        
        namespace['sample_df'] = namespace['df'].copy()
        namespace['data'] = namespace['sample_data']
        
        # Always load ODIBI CORE modules
        try:
            import odibi_core
            namespace['odibi_core'] = odibi_core
        except ImportError:
            pass
        
        try:
            from odibi_core import functions
            namespace['functions'] = functions
        except ImportError:
            pass
        
        try:
            from odibi_core.core.node import Node
            namespace['Node'] = Node
        except ImportError:
            pass
        
        try:
            from odibi_core.engine import EngineContext, PandasEngineContext
            namespace['EngineContext'] = EngineContext
            namespace['PandasEngineContext'] = PandasEngineContext
        except ImportError:
            pass
        
        # Only load Spark if engine is "spark"
        if self.engine == "spark":
            try:
                from pyspark.sql import SparkSession
                from odibi_core.engine import SparkEngineContext
                namespace['SparkSession'] = SparkSession
                namespace['SparkEngineContext'] = SparkEngineContext
                
                # Try to get or create Spark session
                try:
                    spark = SparkSession.builder.appName("LearnODIBI").getOrCreate()
                    namespace['spark'] = spark
                except:
                    pass  # Spark may not be available
            except ImportError:
                pass
        
        return namespace
    
    def set_engine(self, engine: str):
        """Change execution engine and reinitialize namespace"""
        self.engine = engine.lower()
        self.global_namespace = self._initialize_namespace()
    
    def preflight_check(self, code: str) -> PreFlightResult:
        """
        Pre-flight syntax validation using AST parsing
        
        Args:
            code: Python code to validate
            
        Returns:
            PreFlightResult with validation status
        """
        try:
            ast.parse(code)
            return PreFlightResult(passed=True)
        except SyntaxError as e:
            return PreFlightResult(
                passed=False,
                error_msg=f"Syntax Error: {e.msg}",
                line_no=e.lineno
            )
        except Exception as e:
            return PreFlightResult(
                passed=False,
                error_msg=f"Parse Error: {str(e)}"
            )
    
    def execute(
        self, 
        code: str, 
        context: Optional[Dict[str, Any]] = None,
        reset_namespace: bool = False
    ) -> Dict[str, Any]:
        """
        Execute code and return structured results
        
        Args:
            code: Python code to execute
            context: Additional context variables
            reset_namespace: If True, reset namespace before execution
            
        Returns:
            Dictionary with:
                - success: bool
                - output: str (captured stdout)
                - error: str (error message if failed)
                - result: Any (last expression result)
                - variables: Dict (new variables created)
                - df_preview: DataFrame preview if result is a DataFrame
                - preflight: PreFlightResult
        """
        # Pre-flight check
        preflight = self.preflight_check(code)
        
        if not preflight.passed:
            return {
                'success': False,
                'output': '',
                'error': preflight.error_msg,
                'result': None,
                'variables': {},
                'stderr': '',
                'df_preview': None,
                'preflight': preflight.to_dict()
            }
        
        # Reset namespace if requested
        if reset_namespace:
            self.global_namespace = self._initialize_namespace()
        
        # Create isolated execution namespace
        exec_namespace = self.global_namespace.copy()
        if context:
            exec_namespace.update(context)
        
        # Track initial variables
        initial_vars = set(exec_namespace.keys())
        
        # Capture stdout/stderr
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        result = None
        success = True
        error = None
        
        try:
            # Split code into statements
            code_lines = code.strip().split('\n')
            
            # Execute all but last line
            if len(code_lines) > 1:
                exec_code = '\n'.join(code_lines[:-1])
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    exec(exec_code, exec_namespace)
            
            # Evaluate last line (might be an expression)
            last_line = code_lines[-1].strip()
            if last_line:
                with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                    try:
                        # Try to eval (for expressions)
                        result = eval(last_line, exec_namespace)
                    except SyntaxError:
                        # If that fails, exec it instead
                        exec(last_line, exec_namespace)
                        result = None
        
        except Exception as e:
            success = False
            error = self._format_error(e)
        
        # Get new variables
        new_vars = {}
        for key in exec_namespace:
            if key not in initial_vars and not key.startswith('_'):
                new_vars[key] = exec_namespace[key]
        
        # Update global namespace with new variables
        self.global_namespace.update(new_vars)
        
        # Create DataFrame preview if result is a DataFrame
        df_preview = None
        if isinstance(result, pd.DataFrame):
            df_preview = {
                'shape': result.shape,
                'columns': list(result.columns),
                'head': result.head(5).to_dict('records'),
                'dtypes': {col: str(dtype) for col, dtype in result.dtypes.items()}
            }
        
        # Log execution
        self._log_execution(code, success, error)
        
        return {
            'success': success,
            'output': stdout_capture.getvalue(),
            'error': error,
            'result': result,
            'variables': new_vars,
            'stderr': stderr_capture.getvalue(),
            'df_preview': df_preview,
            'preflight': preflight.to_dict()
        }
    
    def _format_error(self, exception: Exception) -> str:
        """Format exception with collapsible trace"""
        error_lines = traceback.format_exception(type(exception), exception, exception.__traceback__)
        
        # Extract just the error message and last few lines
        error_msg = f"{type(exception).__name__}: {str(exception)}"
        
        # Get relevant traceback (skip internal executor frames)
        relevant_trace = []
        for line in error_lines:
            if 'code_executor.py' not in line and '<string>' not in line:
                relevant_trace.append(line)
        
        if relevant_trace:
            trace_str = ''.join(relevant_trace)
            return f"{error_msg}\n\nTraceback:\n{trace_str}"
        else:
            return error_msg
    
    def _log_execution(self, code: str, success: bool, error: Optional[str]):
        """Log execution to error log file"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'engine': self.engine,
            'code_snippet': code[:100] + '...' if len(code) > 100 else code,
            'success': success,
            'error': error
        }
        
        self.execution_log.append(log_entry)
        
        # Write to file if error occurred
        if not success:
            log_file = Path(__file__).parent / 'ui_error_log.json'
            try:
                existing_logs = []
                if log_file.exists():
                    with open(log_file, 'r', encoding='utf-8') as f:
                        existing_logs = json.load(f)
                
                existing_logs.append(log_entry)
                
                # Keep only last 100 entries
                existing_logs = existing_logs[-100:]
                
                with open(log_file, 'w', encoding='utf-8') as f:
                    json.dump(existing_logs, f, indent=2)
            except Exception:
                pass  # Silent fail for logging
    
    def reset_namespace(self):
        """Reset execution namespace to initial state"""
        self.global_namespace = self._initialize_namespace()
    
    def add_to_namespace(self, **kwargs):
        """Add variables to execution namespace"""
        self.global_namespace.update(kwargs)
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get execution log for this session"""
        return self.execution_log


def execute_code_snippet(
    code: str, 
    context: Optional[Dict[str, Any]] = None,
    engine: str = "pandas"
) -> Tuple[bool, str, Any]:
    """
    Convenience function to execute code snippet
    
    Args:
        code: Code to execute
        context: Additional context
        engine: "pandas" or "spark"
        
    Returns:
        (success, message, result)
    """
    executor = CodeExecutor(engine=engine)
    result = executor.execute(code, context)
    
    if result['success']:
        output_parts = []
        
        if result['output']:
            output_parts.append(result['output'])
        
        if result['result'] is not None:
            output_parts.append(f"Result: {result['result']}")
        
        if result['variables']:
            vars_str = ", ".join(f"{k}={type(v).__name__}" for k, v in result['variables'].items())
            output_parts.append(f"Variables created: {vars_str}")
        
        message = "\n".join(output_parts) if output_parts else "Code executed successfully (no output)"
        
        return True, message, result['result']
    else:
        return False, result['error'], None


def get_function_source(function_name: str, module_name: str = None) -> Optional[str]:
    """Get source code of a function"""
    import inspect
    
    try:
        if module_name:
            module = __import__(module_name, fromlist=[function_name])
            func = getattr(module, function_name)
        else:
            # Try to import from odibi_core.functions
            from odibi_core import functions
            func = getattr(functions, function_name)
        
        return inspect.getsource(func)
    except Exception:
        return None


def get_function_call_stack(function_name: str) -> List[str]:
    """Get call stack for a function (simplified)"""
    import inspect
    
    try:
        from odibi_core import functions
        func = getattr(functions, function_name)
        
        # Get function signature
        sig = inspect.signature(func)
        
        # Get docstring
        doc = inspect.getdoc(func) or "No documentation"
        
        # Build call info
        call_info = [
            f"Function: {function_name}",
            f"Signature: {function_name}{sig}",
            f"Documentation: {doc[:200]}..." if len(doc) > 200 else f"Documentation: {doc}",
        ]
        
        return call_info
    except Exception as e:
        return [f"Could not analyze {function_name}: {str(e)}"]
