"""
Unit tests for unit_conversion module.

Tests comprehensive engineering unit conversions:
- convert_pressure (11 units)
- convert_temperature (4 units)
- convert_flow (mass and volume, multiple units)
- convert_power (10 units)
- convert_energy (10 units)
- convert_density (3 units)
"""

import pytest
from odibi_core.functions import unit_conversion


# ============================================================================
# Pressure Conversion Tests
# ============================================================================


def test_convert_pressure_psi_to_bar():
    """Test pressure conversion from psi to bar."""
    result = unit_conversion.convert_pressure(100.0, "psi", "bar")
    assert abs(result - 6.89476) < 0.001


def test_convert_pressure_bar_to_kpa():
    """Test pressure conversion from bar to kPa."""
    result = unit_conversion.convert_pressure(2.5, "bar", "kPa")
    assert abs(result - 250.0) < 0.1


def test_convert_pressure_psia_to_atm():
    """Test pressure conversion from psia to atm."""
    result = unit_conversion.convert_pressure(14.696, "psia", "atm")
    assert abs(result - 1.0) < 0.01


def test_convert_pressure_pa_to_mpa():
    """Test pressure conversion from Pa to MPa."""
    result = unit_conversion.convert_pressure(1000000.0, "Pa", "MPa")
    assert abs(result - 1.0) < 0.001


def test_convert_pressure_torr_to_mmhg():
    """Test pressure conversion from torr to mmHg (same units)."""
    result = unit_conversion.convert_pressure(760.0, "torr", "mmHg")
    assert abs(result - 760.0) < 0.1


def test_convert_pressure_inh2o_to_pa():
    """Test pressure conversion from inH2O to Pa."""
    result = unit_conversion.convert_pressure(1.0, "inH2O", "Pa")
    assert abs(result - 248.84) < 0.1


def test_convert_pressure_inhg_to_psi():
    """Test pressure conversion from inHg to psi."""
    result = unit_conversion.convert_pressure(29.92, "inHg", "psi")
    assert abs(result - 14.696) < 0.1


def test_convert_pressure_mbar_to_bar():
    """Test pressure conversion from mbar to bar."""
    result = unit_conversion.convert_pressure(1000.0, "mbar", "bar")
    assert abs(result - 1.0) < 0.001


def test_convert_pressure_identity():
    """Test pressure conversion with same input and output units."""
    result = unit_conversion.convert_pressure(100.0, "psi", "psi")
    assert abs(result - 100.0) < 0.001


def test_convert_pressure_zero():
    """Test pressure conversion with zero value."""
    result = unit_conversion.convert_pressure(0.0, "bar", "psi")
    assert abs(result) < 0.001


def test_convert_pressure_invalid_from_unit():
    """Test pressure conversion raises ValueError with invalid source unit."""
    with pytest.raises(ValueError, match="Unsupported source pressure unit"):
        unit_conversion.convert_pressure(100.0, "invalid", "bar")


def test_convert_pressure_invalid_to_unit():
    """Test pressure conversion raises ValueError with invalid target unit."""
    with pytest.raises(ValueError, match="Unsupported target pressure unit"):
        unit_conversion.convert_pressure(100.0, "bar", "invalid")


# ============================================================================
# Temperature Conversion Tests
# ============================================================================


def test_convert_temperature_c_to_f():
    """Test temperature conversion from Celsius to Fahrenheit."""
    result = unit_conversion.convert_temperature(100.0, "C", "F")
    assert abs(result - 212.0) < 0.01


def test_convert_temperature_f_to_k():
    """Test temperature conversion from Fahrenheit to Kelvin."""
    result = unit_conversion.convert_temperature(32.0, "F", "K")
    assert abs(result - 273.15) < 0.01


def test_convert_temperature_k_to_c():
    """Test temperature conversion from Kelvin to Celsius."""
    result = unit_conversion.convert_temperature(300.0, "K", "C")
    assert abs(result - 26.85) < 0.01


def test_convert_temperature_c_to_r():
    """Test temperature conversion from Celsius to Rankine."""
    result = unit_conversion.convert_temperature(0.0, "C", "R")
    assert abs(result - 491.67) < 0.01


def test_convert_temperature_r_to_f():
    """Test temperature conversion from Rankine to Fahrenheit."""
    result = unit_conversion.convert_temperature(671.67, "R", "F")
    assert abs(result - 212.0) < 0.01


def test_convert_temperature_identity():
    """Test temperature conversion with same input and output units."""
    result = unit_conversion.convert_temperature(25.0, "C", "C")
    assert abs(result - 25.0) < 0.01


def test_convert_temperature_negative():
    """Test temperature conversion with negative values."""
    result = unit_conversion.convert_temperature(-40.0, "C", "F")
    # -40°C = -40°F
    assert abs(result - (-40.0)) < 0.01


def test_convert_temperature_absolute_zero():
    """Test temperature conversion from absolute zero."""
    result = unit_conversion.convert_temperature(0.0, "K", "C")
    assert abs(result - (-273.15)) < 0.01


def test_convert_temperature_invalid_from_unit():
    """Test temperature conversion raises ValueError with invalid source unit."""
    with pytest.raises(ValueError, match="Unsupported temperature unit"):
        unit_conversion.convert_temperature(100.0, "X", "C")


def test_convert_temperature_invalid_to_unit():
    """Test temperature conversion raises ValueError with invalid target unit."""
    with pytest.raises(ValueError, match="Unsupported temperature unit"):
        unit_conversion.convert_temperature(100.0, "C", "X")


# ============================================================================
# Mass Flow Conversion Tests
# ============================================================================


def test_convert_flow_mass_kg_h_to_kg_s():
    """Test mass flow conversion from kg/h to kg/s."""
    result = unit_conversion.convert_flow(1000.0, "kg/h", "kg/s", "mass")
    assert abs(result - 0.2778) < 0.001


def test_convert_flow_mass_lb_s_to_kg_s():
    """Test mass flow conversion from lb/s to kg/s."""
    result = unit_conversion.convert_flow(100.0, "lb/s", "kg/s", "mass")
    assert abs(result - 45.3592) < 0.01


def test_convert_flow_mass_lb_hr_to_kg_s():
    """Test mass flow conversion from lb/hr to kg/s."""
    result = unit_conversion.convert_flow(5000.0, "lb/hr", "kg/s", "mass")
    assert abs(result - 0.630) < 0.01


def test_convert_flow_mass_ton_h_to_kg_s():
    """Test mass flow conversion from t/h to kg/s."""
    result = unit_conversion.convert_flow(1.0, "t/h", "kg/s", "mass")
    assert abs(result - 0.2778) < 0.001


def test_convert_flow_mass_identity():
    """Test mass flow conversion with same units."""
    result = unit_conversion.convert_flow(100.0, "kg/s", "kg/s", "mass")
    assert abs(result - 100.0) < 0.001


# ============================================================================
# Volume Flow Conversion Tests
# ============================================================================


def test_convert_flow_volume_m3_h_to_m3_s():
    """Test volume flow conversion from m3/h to m3/s."""
    result = unit_conversion.convert_flow(3600.0, "m3/h", "m3/s", "volume")
    assert abs(result - 1.0) < 0.001


def test_convert_flow_volume_cfm_to_m3_h():
    """Test volume flow conversion from cfm to m3/h."""
    result = unit_conversion.convert_flow(100.0, "cfm", "m3/h", "volume")
    assert abs(result - 169.9) < 1.0


def test_convert_flow_volume_l_s_to_m3_s():
    """Test volume flow conversion from L/s to m3/s."""
    result = unit_conversion.convert_flow(1000.0, "L/s", "m3/s", "volume")
    assert abs(result - 1.0) < 0.001


def test_convert_flow_volume_gpm_to_l_min():
    """Test volume flow conversion from gpm to L/min."""
    result = unit_conversion.convert_flow(10.0, "gpm", "L/min", "volume")
    assert abs(result - 0.631) < 0.01


def test_convert_flow_volume_identity():
    """Test volume flow conversion with same units."""
    result = unit_conversion.convert_flow(50.0, "m3/s", "m3/s", "volume")
    assert abs(result - 50.0) < 0.001


def test_convert_flow_invalid_type():
    """Test flow conversion raises ValueError with invalid flow_type."""
    with pytest.raises(ValueError, match="flow_type must be 'mass' or 'volume'"):
        unit_conversion.convert_flow(100.0, "kg/s", "kg/h", "invalid")


def test_convert_flow_invalid_mass_unit():
    """Test mass flow conversion raises ValueError with invalid unit."""
    with pytest.raises(ValueError, match="Unsupported source mass flow unit"):
        unit_conversion.convert_flow(100.0, "invalid", "kg/s", "mass")


def test_convert_flow_invalid_volume_unit():
    """Test volume flow conversion raises ValueError with invalid unit."""
    with pytest.raises(ValueError, match="Unsupported source volume flow unit"):
        unit_conversion.convert_flow(100.0, "invalid", "m3/s", "volume")


# ============================================================================
# Power Conversion Tests
# ============================================================================


def test_convert_power_kw_to_mw():
    """Test power conversion from kW to MW."""
    result = unit_conversion.convert_power(1000.0, "kW", "MW")
    assert abs(result - 1.0) < 0.001


def test_convert_power_hp_to_kw():
    """Test power conversion from hp to kW."""
    result = unit_conversion.convert_power(500.0, "hp", "kW")
    assert abs(result - 372.85) < 0.1


def test_convert_power_btu_h_to_kw():
    """Test power conversion from BTU/h to kW."""
    result = unit_conversion.convert_power(10000.0, "BTU/h", "kW")
    assert abs(result - 2.931) < 0.01


def test_convert_power_w_to_hp():
    """Test power conversion from W to hp."""
    result = unit_conversion.convert_power(745.7, "W", "hp")
    assert abs(result - 1.0) < 0.001


def test_convert_power_ton_refrigeration_to_kw():
    """Test power conversion from ton_refrigeration to kW."""
    result = unit_conversion.convert_power(1.0, "ton_refrigeration", "kW")
    assert abs(result - 3.517) < 0.01


def test_convert_power_kcal_h_to_w():
    """Test power conversion from kcal/h to W."""
    result = unit_conversion.convert_power(1000.0, "kcal/h", "W")
    assert abs(result - 1163.0) < 1.0


def test_convert_power_bhp_to_kw():
    """Test power conversion from bhp (brake horsepower) to kW."""
    result = unit_conversion.convert_power(100.0, "bhp", "kW")
    assert abs(result - 74.57) < 0.1


def test_convert_power_identity():
    """Test power conversion with same units."""
    result = unit_conversion.convert_power(1000.0, "kW", "kW")
    assert abs(result - 1000.0) < 0.001


def test_convert_power_invalid_from_unit():
    """Test power conversion raises ValueError with invalid source unit."""
    with pytest.raises(ValueError, match="Unsupported source power unit"):
        unit_conversion.convert_power(100.0, "invalid", "kW")


def test_convert_power_invalid_to_unit():
    """Test power conversion raises ValueError with invalid target unit."""
    with pytest.raises(ValueError, match="Unsupported target power unit"):
        unit_conversion.convert_power(100.0, "kW", "invalid")


# ============================================================================
# Energy Conversion Tests
# ============================================================================


def test_convert_energy_kwh_to_mwh():
    """Test energy conversion from kWh to MWh."""
    result = unit_conversion.convert_energy(1000.0, "kWh", "MWh")
    assert abs(result - 1.0) < 0.001


def test_convert_energy_mj_to_kwh():
    """Test energy conversion from MJ to kWh."""
    result = unit_conversion.convert_energy(1.0, "MJ", "kWh")
    assert abs(result - 0.2778) < 0.001


def test_convert_energy_btu_to_kj():
    """Test energy conversion from BTU to kJ."""
    result = unit_conversion.convert_energy(1000.0, "BTU", "kJ")
    assert abs(result - 1055.06) < 0.1


def test_convert_energy_j_to_wh():
    """Test energy conversion from J to Wh."""
    result = unit_conversion.convert_energy(3600.0, "J", "Wh")
    assert abs(result - 1.0) < 0.001


def test_convert_energy_kcal_to_kj():
    """Test energy conversion from kcal to kJ."""
    result = unit_conversion.convert_energy(1.0, "kcal", "kJ")
    assert abs(result - 4.184) < 0.001


def test_convert_energy_cal_to_j():
    """Test energy conversion from cal to J."""
    result = unit_conversion.convert_energy(1.0, "cal", "J")
    assert abs(result - 4.184) < 0.001


def test_convert_energy_therm_to_mj():
    """Test energy conversion from therm to MJ."""
    result = unit_conversion.convert_energy(1.0, "therm", "MJ")
    assert abs(result - 105.506) < 0.01


def test_convert_energy_mwh_to_gj():
    """Test energy conversion from MWh to GJ (via J)."""
    result = unit_conversion.convert_energy(1.0, "MWh", "kJ")
    assert abs(result - 3600000.0) < 1.0


def test_convert_energy_identity():
    """Test energy conversion with same units."""
    result = unit_conversion.convert_energy(1000.0, "kWh", "kWh")
    assert abs(result - 1000.0) < 0.001


def test_convert_energy_invalid_from_unit():
    """Test energy conversion raises ValueError with invalid source unit."""
    with pytest.raises(ValueError, match="Unsupported source energy unit"):
        unit_conversion.convert_energy(100.0, "invalid", "kWh")


def test_convert_energy_invalid_to_unit():
    """Test energy conversion raises ValueError with invalid target unit."""
    with pytest.raises(ValueError, match="Unsupported target energy unit"):
        unit_conversion.convert_energy(100.0, "kWh", "invalid")


# ============================================================================
# Density Conversion Tests
# ============================================================================


def test_convert_density_kg_m3_to_lb_ft3():
    """Test density conversion from kg/m3 to lb/ft3."""
    result = unit_conversion.convert_density(1000.0, "kg/m3", "lb/ft3")
    assert abs(result - 62.43) < 0.1


def test_convert_density_g_cm3_to_kg_m3():
    """Test density conversion from g/cm3 to kg/m3."""
    result = unit_conversion.convert_density(1.0, "g/cm3", "kg/m3")
    assert abs(result - 1000.0) < 0.1


def test_convert_density_lb_ft3_to_kg_m3():
    """Test density conversion from lb/ft3 to kg/m3."""
    result = unit_conversion.convert_density(62.43, "lb/ft3", "kg/m3")
    assert abs(result - 1000.0) < 1.0


def test_convert_density_identity():
    """Test density conversion with same units."""
    result = unit_conversion.convert_density(1000.0, "kg/m3", "kg/m3")
    assert abs(result - 1000.0) < 0.001


def test_convert_density_water():
    """Test density conversion for water density."""
    # Water: 1 g/cm3 = 1000 kg/m3 = 62.43 lb/ft3
    result1 = unit_conversion.convert_density(1.0, "g/cm3", "lb/ft3")
    assert abs(result1 - 62.43) < 0.1


def test_convert_density_air():
    """Test density conversion for air density."""
    # Air at STP: ~1.225 kg/m3
    result = unit_conversion.convert_density(1.225, "kg/m3", "lb/ft3")
    assert abs(result - 0.0765) < 0.001
