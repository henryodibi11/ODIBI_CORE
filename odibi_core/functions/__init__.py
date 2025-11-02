"""
General-purpose data engineering utilities for ODIBI CORE.

This module provides engine-agnostic functions that work seamlessly
across both Pandas and Spark DataFrames, plus domain-specific engineering
utilities organized into the following categories:

Engine-Agnostic DataFrame Operations:
- data_ops: DataFrame manipulation (joins, filters, grouping, pivots)
- math_utils: Mathematical operations (z-scores, normalization, aggregations, outliers)
- string_utils: Text processing (case conversion, regex, tokenization)
- datetime_utils: Date/time operations (parsing, extraction, arithmetic)
- validation_utils: Data quality checks (schema validation, missing data, duplicates)
- conversion_utils: Type casting and transformations (boolean coercion, JSON parsing)
- helpers: ODIBI-specific utilities (metadata, parity checking, column resolution)

Domain-Specific Engineering Utilities:
- thermo_utils: Thermodynamic calculations (steam enthalpy, saturation properties)
- psychro_utils: Psychrometric functions (humidity, dew point, wet bulb)
- reliability_utils: Reliability metrics (MTBF, MTTR, availability, failure rates)
- unit_conversion: Engineering unit conversions (pressure, temperature, flow, power)
"""

# Legacy registry support (domain-specific functions)
from odibi_core.functions.registry import FUNCTION_REGISTRY, resolve_function

# Engine-agnostic utilities
from odibi_core.functions import data_ops
from odibi_core.functions import math_utils
from odibi_core.functions import string_utils
from odibi_core.functions import datetime_utils
from odibi_core.functions import validation_utils
from odibi_core.functions import conversion_utils
from odibi_core.functions import helpers

# Domain-specific engineering utilities
from odibi_core.functions import thermo_utils
from odibi_core.functions import psychro_utils
from odibi_core.functions import reliability_utils
from odibi_core.functions import unit_conversion

__all__ = [
    # Legacy
    "FUNCTION_REGISTRY",
    "resolve_function",
    # Engine-agnostic submodules
    "data_ops",
    "math_utils",
    "string_utils",
    "datetime_utils",
    "validation_utils",
    "conversion_utils",
    "helpers",
    # Domain-specific submodules
    "thermo_utils",
    "psychro_utils",
    "reliability_utils",
    "unit_conversion",
]
