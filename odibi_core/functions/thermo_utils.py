"""
Thermodynamic Utilities - Steam and thermal property calculations.

Provides functions for steam enthalpy, saturation properties, and thermodynamic
calculations using the IAPWS library. Includes unit conversion helpers for common
engineering units (psia→MPa, °F→K, kJ/kg→BTU/lb).
"""

from typing import Optional

# Optional dependency handling
try:
    from iapws import IAPWS97
    IAPWS_AVAILABLE = True
except ImportError:
    IAPWS_AVAILABLE = False


# Unit Conversion Helpers
def psia_to_mpa(pressure_psia: float) -> float:
    """
    Convert pressure from psia to MPa.

    Args:
        pressure_psia: Pressure in pounds per square inch absolute

    Returns:
        float: Pressure in megapascals

    Examples:
        >>> psia_to_mpa(14.696)  # 1 atm
        0.101325
    """
    return pressure_psia * 0.00689476


def mpa_to_psia(pressure_mpa: float) -> float:
    """
    Convert pressure from MPa to psia.

    Args:
        pressure_mpa: Pressure in megapascals

    Returns:
        float: Pressure in pounds per square inch absolute

    Examples:
        >>> mpa_to_psia(0.101325)  # 1 atm
        14.696
    """
    return pressure_mpa / 0.00689476


def fahrenheit_to_kelvin(temp_f: float) -> float:
    """
    Convert temperature from Fahrenheit to Kelvin.

    Args:
        temp_f: Temperature in degrees Fahrenheit

    Returns:
        float: Temperature in Kelvin

    Examples:
        >>> fahrenheit_to_kelvin(212.0)  # Boiling point of water
        373.15
    """
    return (temp_f - 32.0) * 5.0 / 9.0 + 273.15


def kelvin_to_fahrenheit(temp_k: float) -> float:
    """
    Convert temperature from Kelvin to Fahrenheit.

    Args:
        temp_k: Temperature in Kelvin

    Returns:
        float: Temperature in degrees Fahrenheit

    Examples:
        >>> kelvin_to_fahrenheit(373.15)  # Boiling point of water
        212.0
    """
    return (temp_k - 273.15) * 9.0 / 5.0 + 32.0


def kj_kg_to_btu_lb(enthalpy_kj_kg: float) -> float:
    """
    Convert specific enthalpy from kJ/kg to BTU/lb.

    Args:
        enthalpy_kj_kg: Specific enthalpy in kilojoules per kilogram

    Returns:
        float: Specific enthalpy in BTU per pound

    Examples:
        >>> kj_kg_to_btu_lb(2500.0)  # Typical steam enthalpy
        1074.85
    """
    return enthalpy_kj_kg * 0.42992


def btu_lb_to_kj_kg(enthalpy_btu_lb: float) -> float:
    """
    Convert specific enthalpy from BTU/lb to kJ/kg.

    Args:
        enthalpy_btu_lb: Specific enthalpy in BTU per pound

    Returns:
        float: Specific enthalpy in kilojoules per kilogram

    Examples:
        >>> btu_lb_to_kj_kg(1074.85)
        2500.0
    """
    return enthalpy_btu_lb / 0.42992


# Thermodynamic Property Functions
def steam_enthalpy_btu_lb(
    pressure_psia: float,
    temperature_f: Optional[float] = None,
    quality: Optional[float] = None
) -> float:
    """
    Calculate steam specific enthalpy in BTU/lb.

    Args:
        pressure_psia: Steam pressure in psia
        temperature_f: Steam temperature in °F (optional, for superheated)
        quality: Steam quality 0-1 (optional, for saturated steam)

    Returns:
        float: Specific enthalpy in BTU/lb

    Raises:
        ImportError: If iapws library is not installed
        ValueError: If neither temperature nor quality is provided

    Examples:
        >>> # Saturated steam at 100 psia
        >>> steam_enthalpy_btu_lb(100.0, quality=1.0)
        1187.2

        >>> # Superheated steam at 500 psia, 600°F
        >>> steam_enthalpy_btu_lb(500.0, temperature_f=600.0)
        1298.4
    """
    if not IAPWS_AVAILABLE:
        raise ImportError(
            "iapws library required for thermodynamic calculations. "
            "Install with: pip install iapws"
        )

    pressure_mpa = psia_to_mpa(pressure_psia)

    if temperature_f is not None:
        # Superheated or compressed liquid
        temp_k = fahrenheit_to_kelvin(temperature_f)
        steam = IAPWS97(P=pressure_mpa, T=temp_k)
    elif quality is not None:
        # Saturated steam
        steam = IAPWS97(P=pressure_mpa, x=quality)
    else:
        raise ValueError("Either temperature_f or quality must be provided")

    # Convert from kJ/kg to BTU/lb
    return kj_kg_to_btu_lb(steam.h)


def feedwater_enthalpy_btu_lb(
    pressure_psia: float,
    temperature_f: float
) -> float:
    """
    Calculate feedwater (liquid water) specific enthalpy in BTU/lb.

    Args:
        pressure_psia: Water pressure in psia
        temperature_f: Water temperature in °F

    Returns:
        float: Specific enthalpy in BTU/lb

    Raises:
        ImportError: If iapws library is not installed

    Examples:
        >>> # Feedwater at 1000 psia, 300°F
        >>> feedwater_enthalpy_btu_lb(1000.0, 300.0)
        269.7
    """
    if not IAPWS_AVAILABLE:
        raise ImportError(
            "iapws library required for thermodynamic calculations. "
            "Install with: pip install iapws"
        )

    pressure_mpa = psia_to_mpa(pressure_psia)
    temp_k = fahrenheit_to_kelvin(temperature_f)

    water = IAPWS97(P=pressure_mpa, T=temp_k)

    # Convert from kJ/kg to BTU/lb
    return kj_kg_to_btu_lb(water.h)


def saturation_temperature(pressure_psia: float) -> float:
    """
    Calculate saturation temperature at given pressure.

    Args:
        pressure_psia: Pressure in psia

    Returns:
        float: Saturation temperature in °F

    Raises:
        ImportError: If iapws library is not installed

    Examples:
        >>> # Saturation temp at atmospheric pressure
        >>> saturation_temperature(14.696)
        212.0

        >>> # Saturation temp at 100 psia
        >>> saturation_temperature(100.0)
        327.8
    """
    if not IAPWS_AVAILABLE:
        raise ImportError(
            "iapws library required for thermodynamic calculations. "
            "Install with: pip install iapws"
        )

    pressure_mpa = psia_to_mpa(pressure_psia)
    steam = IAPWS97(P=pressure_mpa, x=0.0)  # Saturated liquid

    return kelvin_to_fahrenheit(steam.T)


def saturation_pressure(temperature_f: float) -> float:
    """
    Calculate saturation pressure at given temperature.

    Args:
        temperature_f: Temperature in °F

    Returns:
        float: Saturation pressure in psia

    Raises:
        ImportError: If iapws library is not installed

    Examples:
        >>> # Saturation pressure at 212°F (boiling point)
        >>> saturation_pressure(212.0)
        14.696

        >>> # Saturation pressure at 300°F
        >>> saturation_pressure(300.0)
        67.0
    """
    if not IAPWS_AVAILABLE:
        raise ImportError(
            "iapws library required for thermodynamic calculations. "
            "Install with: pip install iapws"
        )

    temp_k = fahrenheit_to_kelvin(temperature_f)
    steam = IAPWS97(T=temp_k, x=0.0)  # Saturated liquid

    return mpa_to_psia(steam.P)


__all__ = [
    # Unit conversion helpers
    "psia_to_mpa",
    "mpa_to_psia",
    "fahrenheit_to_kelvin",
    "kelvin_to_fahrenheit",
    "kj_kg_to_btu_lb",
    "btu_lb_to_kj_kg",
    # Thermodynamic properties
    "steam_enthalpy_btu_lb",
    "feedwater_enthalpy_btu_lb",
    "saturation_temperature",
    "saturation_pressure",
]
