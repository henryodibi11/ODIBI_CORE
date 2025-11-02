"""
Psychrometric Utilities - Moist air property calculations.

Provides functions for humidity calculations, dew point, wet bulb temperature,
and moist air enthalpy. Supports both SI and IP (Imperial) units using psychrolib
library with fallback approximations when library is unavailable.
"""

from typing import Literal, Optional
import math

# Optional dependency handling
try:
    import psychrolib
    PSYCHROLIB_AVAILABLE = True
except ImportError:
    PSYCHROLIB_AVAILABLE = False


def humidity_ratio(
    dry_bulb_temp: float,
    relative_humidity: float,
    pressure: float = 101325.0,
    units: Literal["SI", "IP"] = "SI"
) -> float:
    """
    Calculate humidity ratio (absolute humidity) of moist air.

    Args:
        dry_bulb_temp: Dry bulb temperature (°C for SI, °F for IP)
        relative_humidity: Relative humidity as decimal (0.0 to 1.0)
        pressure: Atmospheric pressure (Pa for SI, psi for IP)
        units: Unit system - "SI" or "IP"

    Returns:
        float: Humidity ratio (kg_water/kg_dry_air for SI, lb_water/lb_dry_air for IP)

    Examples:
        >>> # 25°C, 50% RH at sea level
        >>> humidity_ratio(25.0, 0.5, 101325.0, "SI")
        0.00988

        >>> # 77°F, 50% RH at sea level
        >>> humidity_ratio(77.0, 0.5, 14.696, "IP")
        0.00988
    """
    if PSYCHROLIB_AVAILABLE:
        if units == "SI":
            psychrolib.SetUnitSystem(psychrolib.SI)
        else:
            psychrolib.SetUnitSystem(psychrolib.IP)
        
        return psychrolib.GetHumRatio(dry_bulb_temp, relative_humidity, pressure)
    else:
        # Fallback approximation using Antoine equation
        return _humidity_ratio_approx(dry_bulb_temp, relative_humidity, pressure, units)


def _humidity_ratio_approx(
    dry_bulb_temp: float,
    relative_humidity: float,
    pressure: float,
    units: str
) -> float:
    """Approximate humidity ratio calculation without psychrolib."""
    # Convert to SI if needed
    if units == "IP":
        temp_c = (dry_bulb_temp - 32.0) * 5.0 / 9.0
        pressure_pa = pressure * 6894.76
    else:
        temp_c = dry_bulb_temp
        pressure_pa = pressure

    # Saturation vapor pressure (Magnus formula)
    pws = 611.2 * math.exp(17.62 * temp_c / (243.12 + temp_c))
    pw = relative_humidity * pws

    # Humidity ratio
    return 0.621945 * pw / (pressure_pa - pw)


def dew_point(
    dry_bulb_temp: float,
    relative_humidity: float,
    units: Literal["SI", "IP"] = "SI"
) -> float:
    """
    Calculate dew point temperature.

    Args:
        dry_bulb_temp: Dry bulb temperature (°C for SI, °F for IP)
        relative_humidity: Relative humidity as decimal (0.0 to 1.0)
        units: Unit system - "SI" or "IP"

    Returns:
        float: Dew point temperature (°C for SI, °F for IP)

    Examples:
        >>> # 25°C, 50% RH
        >>> dew_point(25.0, 0.5, "SI")
        13.9

        >>> # 77°F, 50% RH
        >>> dew_point(77.0, 0.5, "IP")
        57.1
    """
    if PSYCHROLIB_AVAILABLE:
        if units == "SI":
            psychrolib.SetUnitSystem(psychrolib.SI)
        else:
            psychrolib.SetUnitSystem(psychrolib.IP)
        
        return psychrolib.GetTDewPointFromRelHum(dry_bulb_temp, relative_humidity)
    else:
        return _dew_point_approx(dry_bulb_temp, relative_humidity, units)


def _dew_point_approx(
    dry_bulb_temp: float,
    relative_humidity: float,
    units: str
) -> float:
    """Approximate dew point using Magnus-Tetens formula."""
    # Convert to SI if needed
    if units == "IP":
        temp_c = (dry_bulb_temp - 32.0) * 5.0 / 9.0
    else:
        temp_c = dry_bulb_temp

    # Magnus-Tetens approximation
    a = 17.27
    b = 237.7
    alpha = ((a * temp_c) / (b + temp_c)) + math.log(relative_humidity)
    dew_c = (b * alpha) / (a - alpha)

    # Convert back to IP if needed
    if units == "IP":
        return dew_c * 9.0 / 5.0 + 32.0
    else:
        return dew_c


def wet_bulb_temperature(
    dry_bulb_temp: float,
    relative_humidity: float,
    pressure: float = 101325.0,
    units: Literal["SI", "IP"] = "SI"
) -> float:
    """
    Calculate wet bulb temperature.

    Args:
        dry_bulb_temp: Dry bulb temperature (°C for SI, °F for IP)
        relative_humidity: Relative humidity as decimal (0.0 to 1.0)
        pressure: Atmospheric pressure (Pa for SI, psi for IP)
        units: Unit system - "SI" or "IP"

    Returns:
        float: Wet bulb temperature (°C for SI, °F for IP)

    Examples:
        >>> # 25°C, 50% RH at sea level
        >>> wet_bulb_temperature(25.0, 0.5, 101325.0, "SI")
        17.8

        >>> # 77°F, 50% RH at sea level
        >>> wet_bulb_temperature(77.0, 0.5, 14.696, "IP")
        64.0
    """
    if PSYCHROLIB_AVAILABLE:
        if units == "SI":
            psychrolib.SetUnitSystem(psychrolib.SI)
        else:
            psychrolib.SetUnitSystem(psychrolib.IP)
        
        return psychrolib.GetTWetBulbFromRelHum(dry_bulb_temp, relative_humidity, pressure)
    else:
        return _wet_bulb_approx(dry_bulb_temp, relative_humidity, pressure, units)


def _wet_bulb_approx(
    dry_bulb_temp: float,
    relative_humidity: float,
    pressure: float,
    units: str
) -> float:
    """Approximate wet bulb using Stull's formula."""
    # Convert to SI if needed
    if units == "IP":
        temp_c = (dry_bulb_temp - 32.0) * 5.0 / 9.0
    else:
        temp_c = dry_bulb_temp

    rh_percent = relative_humidity * 100.0

    # Stull's approximation (accurate to ±1°C)
    tw = temp_c * math.atan(0.151977 * (rh_percent + 8.313659)**0.5) + \
         math.atan(temp_c + rh_percent) - \
         math.atan(rh_percent - 1.676331) + \
         0.00391838 * (rh_percent)**1.5 * math.atan(0.023101 * rh_percent) - 4.686035

    # Convert back to IP if needed
    if units == "IP":
        return tw * 9.0 / 5.0 + 32.0
    else:
        return tw


def enthalpy_moist_air(
    dry_bulb_temp: float,
    humidity_ratio_value: float,
    units: Literal["SI", "IP"] = "SI"
) -> float:
    """
    Calculate specific enthalpy of moist air.

    Args:
        dry_bulb_temp: Dry bulb temperature (°C for SI, °F for IP)
        humidity_ratio_value: Humidity ratio (kg/kg for SI, lb/lb for IP)
        units: Unit system - "SI" or "IP"

    Returns:
        float: Specific enthalpy (kJ/kg for SI, BTU/lb for IP)

    Examples:
        >>> # 25°C, W=0.01 kg/kg
        >>> enthalpy_moist_air(25.0, 0.01, "SI")
        50.5

        >>> # 77°F, W=0.01 lb/lb
        >>> enthalpy_moist_air(77.0, 0.01, "IP")
        21.7
    """
    if PSYCHROLIB_AVAILABLE:
        if units == "SI":
            psychrolib.SetUnitSystem(psychrolib.SI)
        else:
            psychrolib.SetUnitSystem(psychrolib.IP)
        
        return psychrolib.GetMoistAirEnthalpy(dry_bulb_temp, humidity_ratio_value)
    else:
        return _enthalpy_approx(dry_bulb_temp, humidity_ratio_value, units)


def _enthalpy_approx(
    dry_bulb_temp: float,
    humidity_ratio_value: float,
    units: str
) -> float:
    """Approximate moist air enthalpy calculation."""
    if units == "IP":
        # IP units: BTU/lb
        # h = 0.24*T + W*(1061 + 0.444*T)
        return 0.24 * dry_bulb_temp + humidity_ratio_value * (1061.0 + 0.444 * dry_bulb_temp)
    else:
        # SI units: kJ/kg
        # h = 1.006*T + W*(2501 + 1.86*T)
        return 1.006 * dry_bulb_temp + humidity_ratio_value * (2501.0 + 1.86 * dry_bulb_temp)


def relative_humidity(
    dry_bulb_temp: float,
    humidity_ratio_value: float,
    pressure: float = 101325.0,
    units: Literal["SI", "IP"] = "SI"
) -> float:
    """
    Calculate relative humidity from temperature and humidity ratio.

    Args:
        dry_bulb_temp: Dry bulb temperature (°C for SI, °F for IP)
        humidity_ratio_value: Humidity ratio (kg/kg for SI, lb/lb for IP)
        pressure: Atmospheric pressure (Pa for SI, psi for IP)
        units: Unit system - "SI" or "IP"

    Returns:
        float: Relative humidity as decimal (0.0 to 1.0)

    Examples:
        >>> # 25°C, W=0.00988 kg/kg at sea level
        >>> relative_humidity(25.0, 0.00988, 101325.0, "SI")
        0.5

        >>> # 77°F, W=0.00988 lb/lb at sea level
        >>> relative_humidity(77.0, 0.00988, 14.696, "IP")
        0.5
    """
    if PSYCHROLIB_AVAILABLE:
        if units == "SI":
            psychrolib.SetUnitSystem(psychrolib.SI)
        else:
            psychrolib.SetUnitSystem(psychrolib.IP)
        
        return psychrolib.GetRelHumFromHumRatio(dry_bulb_temp, humidity_ratio_value, pressure)
    else:
        return _relative_humidity_approx(dry_bulb_temp, humidity_ratio_value, pressure, units)


def _relative_humidity_approx(
    dry_bulb_temp: float,
    humidity_ratio_value: float,
    pressure: float,
    units: str
) -> float:
    """Approximate relative humidity calculation."""
    # Convert to SI if needed
    if units == "IP":
        temp_c = (dry_bulb_temp - 32.0) * 5.0 / 9.0
        pressure_pa = pressure * 6894.76
    else:
        temp_c = dry_bulb_temp
        pressure_pa = pressure

    # Saturation vapor pressure (Magnus formula)
    pws = 611.2 * math.exp(17.62 * temp_c / (243.12 + temp_c))
    
    # Partial vapor pressure from humidity ratio
    pw = (humidity_ratio_value * pressure_pa) / (0.621945 + humidity_ratio_value)
    
    return min(pw / pws, 1.0)  # Cap at 100%


__all__ = [
    "humidity_ratio",
    "dew_point",
    "wet_bulb_temperature",
    "enthalpy_moist_air",
    "relative_humidity",
]
