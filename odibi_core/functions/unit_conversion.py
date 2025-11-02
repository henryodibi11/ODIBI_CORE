"""
Unit Conversion Utilities - Engineering unit conversions.

Provides comprehensive conversion functions for common engineering units
including pressure, temperature, flow, power, and energy. Supports conversion
between SI, Imperial, and common industry units.
"""

from typing import Literal, Dict


# Pressure conversion factors (all to Pascal)
PRESSURE_TO_PA: Dict[str, float] = {
    "Pa": 1.0,
    "kPa": 1000.0,
    "MPa": 1_000_000.0,
    "bar": 100_000.0,
    "mbar": 100.0,
    "psi": 6894.76,
    "psia": 6894.76,
    "psig": 6894.76,  # Note: gauge pressure needs offset
    "atm": 101_325.0,
    "torr": 133.322,
    "mmHg": 133.322,
    "inHg": 3386.39,
    "inH2O": 248.84,
}


# Temperature conversion functions (non-linear, handled separately)


# Flow conversion factors (all to kg/s)
MASS_FLOW_TO_KG_S: Dict[str, float] = {
    "kg/s": 1.0,
    "kg/h": 1.0 / 3600.0,
    "kg/hr": 1.0 / 3600.0,
    "lb/s": 0.453592,
    "lb/h": 0.453592 / 3600.0,
    "lb/hr": 0.453592 / 3600.0,
    "t/h": 1000.0 / 3600.0,
    "ton/h": 1000.0 / 3600.0,
}


# Volumetric flow conversion factors (all to m³/s)
VOL_FLOW_TO_M3_S: Dict[str, float] = {
    "m3/s": 1.0,
    "m3/h": 1.0 / 3600.0,
    "m3/hr": 1.0 / 3600.0,
    "L/s": 0.001,
    "L/min": 0.001 / 60.0,
    "ft3/s": 0.0283168,
    "ft3/min": 0.0283168 / 60.0,
    "cfm": 0.0283168 / 60.0,
    "gal/min": 0.0000631 / 60.0,
    "gpm": 0.0000631 / 60.0,
}


# Power conversion factors (all to Watt)
POWER_TO_W: Dict[str, float] = {
    "W": 1.0,
    "kW": 1000.0,
    "MW": 1_000_000.0,
    "hp": 745.7,
    "bhp": 745.7,
    "BTU/h": 0.293071,
    "BTU/hr": 0.293071,
    "kcal/h": 1.163,
    "ton_refrigeration": 3516.85,
}


# Energy conversion factors (all to Joule)
ENERGY_TO_J: Dict[str, float] = {
    "J": 1.0,
    "kJ": 1000.0,
    "MJ": 1_000_000.0,
    "Wh": 3600.0,
    "kWh": 3_600_000.0,
    "MWh": 3_600_000_000.0,
    "BTU": 1055.06,
    "cal": 4.184,
    "kcal": 4184.0,
    "therm": 105_506_000.0,
}


def convert_pressure(
    value: float,
    from_unit: str,
    to_unit: str,
    gauge_offset: float = 0.0
) -> float:
    """
    Convert pressure between different units.

    Args:
        value: Pressure value to convert
        from_unit: Source unit (Pa, kPa, MPa, bar, psi, psia, psig, atm, torr, mmHg, inHg, inH2O)
        to_unit: Target unit (same options as from_unit)
        gauge_offset: Offset for gauge to absolute conversion (Pa)

    Returns:
        float: Converted pressure value

    Raises:
        ValueError: If units are not supported

    Examples:
        >>> # Convert 100 psi to bar
        >>> convert_pressure(100.0, "psi", "bar")
        6.895

        >>> # Convert 2.5 bar to kPa
        >>> convert_pressure(2.5, "bar", "kPa")
        250.0

        >>> # Convert 14.7 psia to atm
        >>> convert_pressure(14.7, "psia", "atm")
        1.0
    """
    if from_unit not in PRESSURE_TO_PA:
        raise ValueError(f"Unsupported source pressure unit: {from_unit}")
    if to_unit not in PRESSURE_TO_PA:
        raise ValueError(f"Unsupported target pressure unit: {to_unit}")

    # Convert to Pascal (base unit)
    value_pa = value * PRESSURE_TO_PA[from_unit]
    
    # Add gauge offset if needed
    value_pa += gauge_offset
    
    # Convert to target unit
    return value_pa / PRESSURE_TO_PA[to_unit]


def convert_temperature(
    value: float,
    from_unit: Literal["C", "F", "K", "R"],
    to_unit: Literal["C", "F", "K", "R"]
) -> float:
    """
    Convert temperature between different units.

    Args:
        value: Temperature value to convert
        from_unit: Source unit (C=Celsius, F=Fahrenheit, K=Kelvin, R=Rankine)
        to_unit: Target unit (same options as from_unit)

    Returns:
        float: Converted temperature value

    Raises:
        ValueError: If units are not supported

    Examples:
        >>> # Convert 100°C to °F
        >>> convert_temperature(100.0, "C", "F")
        212.0

        >>> # Convert 32°F to K
        >>> convert_temperature(32.0, "F", "K")
        273.15

        >>> # Convert 300 K to °C
        >>> convert_temperature(300.0, "K", "C")
        26.85
    """
    # First convert to Kelvin (base unit)
    if from_unit == "K":
        temp_k = value
    elif from_unit == "C":
        temp_k = value + 273.15
    elif from_unit == "F":
        temp_k = (value - 32.0) * 5.0 / 9.0 + 273.15
    elif from_unit == "R":
        temp_k = value * 5.0 / 9.0
    else:
        raise ValueError(f"Unsupported temperature unit: {from_unit}")

    # Convert from Kelvin to target unit
    if to_unit == "K":
        return temp_k
    elif to_unit == "C":
        return temp_k - 273.15
    elif to_unit == "F":
        return (temp_k - 273.15) * 9.0 / 5.0 + 32.0
    elif to_unit == "R":
        return temp_k * 9.0 / 5.0
    else:
        raise ValueError(f"Unsupported temperature unit: {to_unit}")


def convert_flow(
    value: float,
    from_unit: str,
    to_unit: str,
    flow_type: Literal["mass", "volume"] = "mass"
) -> float:
    """
    Convert flow rate between different units.

    Args:
        value: Flow rate value to convert
        from_unit: Source unit
        to_unit: Target unit
        flow_type: "mass" or "volume"

    Returns:
        float: Converted flow rate value

    Raises:
        ValueError: If units or flow_type are not supported

    Examples:
        >>> # Convert 1000 kg/h to kg/s
        >>> convert_flow(1000.0, "kg/h", "kg/s", "mass")
        0.278

        >>> # Convert 100 cfm to m3/h
        >>> convert_flow(100.0, "cfm", "m3/h", "volume")
        169.9

        >>> # Convert 5000 lb/hr to kg/s
        >>> convert_flow(5000.0, "lb/hr", "kg/s", "mass")
        0.630
    """
    if flow_type == "mass":
        if from_unit not in MASS_FLOW_TO_KG_S:
            raise ValueError(f"Unsupported source mass flow unit: {from_unit}")
        if to_unit not in MASS_FLOW_TO_KG_S:
            raise ValueError(f"Unsupported target mass flow unit: {to_unit}")
        
        # Convert to kg/s (base unit)
        value_kg_s = value * MASS_FLOW_TO_KG_S[from_unit]
        
        # Convert to target unit
        return value_kg_s / MASS_FLOW_TO_KG_S[to_unit]
    
    elif flow_type == "volume":
        if from_unit not in VOL_FLOW_TO_M3_S:
            raise ValueError(f"Unsupported source volume flow unit: {from_unit}")
        if to_unit not in VOL_FLOW_TO_M3_S:
            raise ValueError(f"Unsupported target volume flow unit: {to_unit}")
        
        # Convert to m³/s (base unit)
        value_m3_s = value * VOL_FLOW_TO_M3_S[from_unit]
        
        # Convert to target unit
        return value_m3_s / VOL_FLOW_TO_M3_S[to_unit]
    
    else:
        raise ValueError(f"flow_type must be 'mass' or 'volume', got '{flow_type}'")


def convert_power(
    value: float,
    from_unit: str,
    to_unit: str
) -> float:
    """
    Convert power between different units.

    Args:
        value: Power value to convert
        from_unit: Source unit (W, kW, MW, hp, bhp, BTU/h, kcal/h, ton_refrigeration)
        to_unit: Target unit (same options as from_unit)

    Returns:
        float: Converted power value

    Raises:
        ValueError: If units are not supported

    Examples:
        >>> # Convert 1000 kW to MW
        >>> convert_power(1000.0, "kW", "MW")
        1.0

        >>> # Convert 500 hp to kW
        >>> convert_power(500.0, "hp", "kW")
        372.85

        >>> # Convert 10000 BTU/h to kW
        >>> convert_power(10000.0, "BTU/h", "kW")
        2.931
    """
    if from_unit not in POWER_TO_W:
        raise ValueError(f"Unsupported source power unit: {from_unit}")
    if to_unit not in POWER_TO_W:
        raise ValueError(f"Unsupported target power unit: {to_unit}")

    # Convert to Watt (base unit)
    value_w = value * POWER_TO_W[from_unit]
    
    # Convert to target unit
    return value_w / POWER_TO_W[to_unit]


def convert_energy(
    value: float,
    from_unit: str,
    to_unit: str
) -> float:
    """
    Convert energy between different units.

    Args:
        value: Energy value to convert
        from_unit: Source unit (J, kJ, MJ, Wh, kWh, MWh, BTU, cal, kcal, therm)
        to_unit: Target unit (same options as from_unit)

    Returns:
        float: Converted energy value

    Raises:
        ValueError: If units are not supported

    Examples:
        >>> # Convert 1000 kWh to MWh
        >>> convert_energy(1000.0, "kWh", "MWh")
        1.0

        >>> # Convert 1 MJ to kWh
        >>> convert_energy(1.0, "MJ", "kWh")
        0.278

        >>> # Convert 1000 BTU to kJ
        >>> convert_energy(1000.0, "BTU", "kJ")
        1055.06
    """
    if from_unit not in ENERGY_TO_J:
        raise ValueError(f"Unsupported source energy unit: {from_unit}")
    if to_unit not in ENERGY_TO_J:
        raise ValueError(f"Unsupported target energy unit: {to_unit}")

    # Convert to Joule (base unit)
    value_j = value * ENERGY_TO_J[from_unit]
    
    # Convert to target unit
    return value_j / ENERGY_TO_J[to_unit]


def convert_density(
    value: float,
    from_unit: Literal["kg/m3", "lb/ft3", "g/cm3"],
    to_unit: Literal["kg/m3", "lb/ft3", "g/cm3"]
) -> float:
    """
    Convert density between different units.

    Args:
        value: Density value to convert
        from_unit: Source unit (kg/m3, lb/ft3, g/cm3)
        to_unit: Target unit (same options as from_unit)

    Returns:
        float: Converted density value

    Examples:
        >>> # Convert 1000 kg/m3 to lb/ft3
        >>> convert_density(1000.0, "kg/m3", "lb/ft3")
        62.43

        >>> # Convert 1 g/cm3 to kg/m3
        >>> convert_density(1.0, "g/cm3", "kg/m3")
        1000.0
    """
    # Conversion factors to kg/m3
    to_kg_m3 = {
        "kg/m3": 1.0,
        "lb/ft3": 16.0185,
        "g/cm3": 1000.0,
    }

    # Convert to kg/m3 (base unit)
    value_kg_m3 = value * to_kg_m3[from_unit]
    
    # Convert to target unit
    return value_kg_m3 / to_kg_m3[to_unit]


__all__ = [
    "convert_pressure",
    "convert_temperature",
    "convert_flow",
    "convert_power",
    "convert_energy",
    "convert_density",
]
