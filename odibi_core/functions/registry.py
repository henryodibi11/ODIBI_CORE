"""
Function registry for dynamic function resolution.

Enables TransformNode to import functions by dotted path (e.g., "thermo.steam.calc_enthalpy").
"""

from typing import Any, Callable, Dict


# Global function registry
FUNCTION_REGISTRY: Dict[str, Callable[..., Any]] = {}


def resolve_function(function_path: str) -> Callable[..., Any]:
    """
    Resolve function by dotted path.

    Args:
        function_path: Dotted path to function (e.g., "thermo.steam.calc_enthalpy")

    Returns:
        Function object

    Raises:
        ImportError: If function not found

    Example:
        >>> func = resolve_function("thermo.steam.steam_enthalpy_btu_lb")
        >>> result = func(pressure_psia=150, temp_f=600)
    """
    # TODO Phase 7: Implement function resolution
    # - Check FUNCTION_REGISTRY first
    # - If not found, try dynamic import:
    #   - Split path: module_path, function_name
    #   - Import: module = importlib.import_module(f"odibi_core.functions.{module_path}")
    #   - Get function: func = getattr(module, function_name)
    # - Cache in registry for future use
    if function_path in FUNCTION_REGISTRY:
        return FUNCTION_REGISTRY[function_path]

    raise ImportError(f"Function not found: {function_path}")


def register_function(path: str, func: Callable[..., Any]) -> None:
    """
    Register function in global registry.

    Args:
        path: Dotted path (e.g., "thermo.steam.calc_enthalpy")
        func: Function to register

    Example:
        >>> register_function("custom.my_func", my_custom_function)
    """
    FUNCTION_REGISTRY[path] = func
