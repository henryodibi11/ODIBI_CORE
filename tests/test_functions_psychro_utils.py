"""
Unit tests for psychro_utils module.

Tests psychrometric calculations for moist air:
- humidity_ratio
- dew_point
- wet_bulb_temperature
- enthalpy_moist_air
- relative_humidity
Tests both with psychrolib and fallback approximation modes.
"""

import pytest
import math
from unittest.mock import patch
from odibi_core.functions import psychro_utils


# ============================================================================
# Humidity Ratio Tests
# ============================================================================


def test_humidity_ratio_si_moderate_conditions():
    """Test humidity ratio in SI units at moderate conditions."""
    # 25°C, 50% RH at sea level
    result = psychro_utils.humidity_ratio(25.0, 0.5, 101325.0, "SI")
    # Expected approximately 0.00988 kg/kg
    assert 0.009 < result < 0.011


def test_humidity_ratio_ip_moderate_conditions():
    """Test humidity ratio in IP units at moderate conditions."""
    # 77°F, 50% RH at sea level
    result = psychro_utils.humidity_ratio(77.0, 0.5, 14.696, "IP")
    # Expected approximately 0.00988 lb/lb
    assert 0.009 < result < 0.011


def test_humidity_ratio_si_dry_air():
    """Test humidity ratio with very low RH."""
    # 25°C, 10% RH
    result = psychro_utils.humidity_ratio(25.0, 0.1, 101325.0, "SI")
    # Should be much lower than 50% RH
    assert 0.001 < result < 0.003


def test_humidity_ratio_si_saturated():
    """Test humidity ratio at 100% RH (saturated)."""
    # 25°C, 100% RH
    result = psychro_utils.humidity_ratio(25.0, 1.0, 101325.0, "SI")
    # Should be approximately 0.0198 kg/kg at saturation
    assert 0.018 < result < 0.022


def test_humidity_ratio_high_temp():
    """Test humidity ratio at high temperature."""
    # 40°C, 60% RH - higher temp means more moisture capacity
    result = psychro_utils.humidity_ratio(40.0, 0.6, 101325.0, "SI")
    assert result > 0.02


def test_humidity_ratio_zero_rh():
    """Test humidity ratio with 0% RH."""
    result = psychro_utils.humidity_ratio(25.0, 0.0, 101325.0, "SI")
    assert abs(result) < 0.0001


@patch('odibi_core.functions.psychro_utils.PSYCHROLIB_AVAILABLE', False)
def test_humidity_ratio_fallback_si():
    """Test humidity ratio fallback calculation in SI units."""
    result = psychro_utils.humidity_ratio(25.0, 0.5, 101325.0, "SI")
    # Fallback should give reasonable approximation
    assert 0.009 < result < 0.011


@patch('odibi_core.functions.psychro_utils.PSYCHROLIB_AVAILABLE', False)
def test_humidity_ratio_fallback_ip():
    """Test humidity ratio fallback calculation in IP units."""
    result = psychro_utils.humidity_ratio(77.0, 0.5, 14.696, "IP")
    # Fallback should give reasonable approximation
    assert 0.009 < result < 0.011


# ============================================================================
# Dew Point Tests
# ============================================================================


def test_dew_point_si_moderate():
    """Test dew point in SI units at moderate conditions."""
    # 25°C, 50% RH
    result = psychro_utils.dew_point(25.0, 0.5, "SI")
    # Expected approximately 13.9°C
    assert 13 < result < 15


def test_dew_point_ip_moderate():
    """Test dew point in IP units at moderate conditions."""
    # 77°F, 50% RH
    result = psychro_utils.dew_point(77.0, 0.5, "IP")
    # Expected approximately 57°F
    assert 55 < result < 59


def test_dew_point_high_rh():
    """Test dew point at high relative humidity."""
    # 25°C, 90% RH - dew point should be close to dry bulb
    result = psychro_utils.dew_point(25.0, 0.9, "SI")
    assert result > 22


def test_dew_point_low_rh():
    """Test dew point at low relative humidity."""
    # 25°C, 20% RH - dew point should be much lower
    result = psychro_utils.dew_point(25.0, 0.2, "SI")
    assert result < 10


def test_dew_point_saturated():
    """Test dew point at 100% RH (saturated)."""
    # When RH=100%, dew point should equal dry bulb temp
    result = psychro_utils.dew_point(25.0, 1.0, "SI")
    assert abs(result - 25.0) < 0.5


@patch('odibi_core.functions.psychro_utils.PSYCHROLIB_AVAILABLE', False)
def test_dew_point_fallback_si():
    """Test dew point fallback calculation in SI units."""
    result = psychro_utils.dew_point(25.0, 0.5, "SI")
    # Magnus-Tetens approximation should be accurate
    assert 13 < result < 15


@patch('odibi_core.functions.psychro_utils.PSYCHROLIB_AVAILABLE', False)
def test_dew_point_fallback_ip():
    """Test dew point fallback calculation in IP units."""
    result = psychro_utils.dew_point(77.0, 0.5, "IP")
    assert 55 < result < 59


# ============================================================================
# Wet Bulb Temperature Tests
# ============================================================================


def test_wet_bulb_si_moderate():
    """Test wet bulb temperature in SI units at moderate conditions."""
    # 25°C, 50% RH
    result = psychro_utils.wet_bulb_temperature(25.0, 0.5, 101325.0, "SI")
    # Expected approximately 17-18°C
    assert 16 < result < 19


def test_wet_bulb_ip_moderate():
    """Test wet bulb temperature in IP units at moderate conditions."""
    # 77°F, 50% RH
    result = psychro_utils.wet_bulb_temperature(77.0, 0.5, 14.696, "IP")
    # Expected approximately 63-65°F
    assert 62 < result < 66


def test_wet_bulb_saturated():
    """Test wet bulb at 100% RH (should equal dry bulb)."""
    result = psychro_utils.wet_bulb_temperature(25.0, 1.0, 101325.0, "SI")
    # When saturated, wet bulb ≈ dry bulb
    assert abs(result - 25.0) < 1.0


def test_wet_bulb_low_rh():
    """Test wet bulb at low RH (should be much lower than dry bulb)."""
    # 30°C, 20% RH - significant evaporative cooling
    result = psychro_utils.wet_bulb_temperature(30.0, 0.2, 101325.0, "SI")
    assert result < 20


@patch('odibi_core.functions.psychro_utils.PSYCHROLIB_AVAILABLE', False)
def test_wet_bulb_fallback_si():
    """Test wet bulb fallback calculation (Stull's formula)."""
    result = psychro_utils.wet_bulb_temperature(25.0, 0.5, 101325.0, "SI")
    # Stull's formula should be accurate to ±1°C
    assert 16 < result < 19


@patch('odibi_core.functions.psychro_utils.PSYCHROLIB_AVAILABLE', False)
def test_wet_bulb_fallback_ip():
    """Test wet bulb fallback calculation in IP units."""
    result = psychro_utils.wet_bulb_temperature(77.0, 0.5, 14.696, "IP")
    assert 62 < result < 66


# ============================================================================
# Enthalpy Moist Air Tests
# ============================================================================


def test_enthalpy_si_typical():
    """Test moist air enthalpy in SI units."""
    # 25°C, W=0.01 kg/kg
    result = psychro_utils.enthalpy_moist_air(25.0, 0.01, "SI")
    # Expected approximately 50-51 kJ/kg
    assert 49 < result < 52


def test_enthalpy_ip_typical():
    """Test moist air enthalpy in IP units."""
    # 77°F, W=0.01 lb/lb
    result = psychro_utils.enthalpy_moist_air(77.0, 0.01, "IP")
    # Expected approximately 21-22 BTU/lb
    assert 21 < result < 23


def test_enthalpy_dry_air():
    """Test enthalpy with zero humidity ratio (dry air)."""
    result = psychro_utils.enthalpy_moist_air(25.0, 0.0, "SI")
    # Dry air enthalpy ≈ 1.006 * T
    assert 24 < result < 26


def test_enthalpy_high_humidity():
    """Test enthalpy with high humidity ratio."""
    # Higher humidity means higher enthalpy
    result = psychro_utils.enthalpy_moist_air(30.0, 0.02, "SI")
    assert result > 80


@patch('odibi_core.functions.psychro_utils.PSYCHROLIB_AVAILABLE', False)
def test_enthalpy_fallback_si():
    """Test enthalpy fallback calculation in SI units."""
    result = psychro_utils.enthalpy_moist_air(25.0, 0.01, "SI")
    # Approximation: h = 1.006*T + W*(2501 + 1.86*T)
    expected = 1.006 * 25.0 + 0.01 * (2501.0 + 1.86 * 25.0)
    assert abs(result - expected) < 0.1


@patch('odibi_core.functions.psychro_utils.PSYCHROLIB_AVAILABLE', False)
def test_enthalpy_fallback_ip():
    """Test enthalpy fallback calculation in IP units."""
    result = psychro_utils.enthalpy_moist_air(77.0, 0.01, "IP")
    # Approximation: h = 0.24*T + W*(1061 + 0.444*T)
    expected = 0.24 * 77.0 + 0.01 * (1061.0 + 0.444 * 77.0)
    assert abs(result - expected) < 0.1


# ============================================================================
# Relative Humidity Tests
# ============================================================================


def test_relative_humidity_si_typical():
    """Test calculating RH from temperature and humidity ratio (SI)."""
    # 25°C, W≈0.00988 kg/kg should give RH≈0.5
    result = psychro_utils.relative_humidity(25.0, 0.00988, 101325.0, "SI")
    assert 0.48 < result < 0.52


def test_relative_humidity_ip_typical():
    """Test calculating RH from temperature and humidity ratio (IP)."""
    # 77°F, W≈0.00988 lb/lb should give RH≈0.5
    result = psychro_utils.relative_humidity(77.0, 0.00988, 14.696, "IP")
    assert 0.48 < result < 0.52


def test_relative_humidity_dry_air():
    """Test RH with very low humidity ratio."""
    result = psychro_utils.relative_humidity(25.0, 0.001, 101325.0, "SI")
    # Very low humidity ratio means low RH
    assert result < 0.1


def test_relative_humidity_saturated():
    """Test RH with saturation humidity ratio."""
    # Get saturation W first
    w_sat = psychro_utils.humidity_ratio(25.0, 1.0, 101325.0, "SI")
    result = psychro_utils.relative_humidity(25.0, w_sat, 101325.0, "SI")
    # Should be close to 1.0 (100%)
    assert result > 0.95


@patch('odibi_core.functions.psychro_utils.PSYCHROLIB_AVAILABLE', False)
def test_relative_humidity_fallback_si():
    """Test RH fallback calculation in SI units."""
    result = psychro_utils.relative_humidity(25.0, 0.00988, 101325.0, "SI")
    assert 0.48 < result < 0.52


@patch('odibi_core.functions.psychro_utils.PSYCHROLIB_AVAILABLE', False)
def test_relative_humidity_fallback_ip():
    """Test RH fallback calculation in IP units."""
    result = psychro_utils.relative_humidity(77.0, 0.00988, 14.696, "IP")
    assert 0.48 < result < 0.52


# ============================================================================
# Edge Cases
# ============================================================================


def test_humidity_ratio_extreme_low_temp():
    """Test humidity ratio at very low temperature."""
    # -10°C, 50% RH - very low moisture capacity
    result = psychro_utils.humidity_ratio(-10.0, 0.5, 101325.0, "SI")
    assert result < 0.002


def test_humidity_ratio_extreme_high_temp():
    """Test humidity ratio at very high temperature."""
    # 50°C, 70% RH - high moisture capacity
    result = psychro_utils.humidity_ratio(50.0, 0.7, 101325.0, "SI")
    assert result > 0.05


def test_dew_point_near_zero_rh():
    """Test dew point with very low RH (edge case)."""
    # Should not crash, even with very low RH
    result = psychro_utils.dew_point(25.0, 0.01, "SI")
    assert result < 0  # Very low dew point


@patch('odibi_core.functions.psychro_utils.PSYCHROLIB_AVAILABLE', False)
def test_relative_humidity_capped_at_one():
    """Test that RH fallback caps at 1.0."""
    # Use very high humidity ratio that might calculate >100%
    result = psychro_utils.relative_humidity(25.0, 0.05, 101325.0, "SI")
    assert result <= 1.0
