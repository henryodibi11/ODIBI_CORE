"""
Unit tests for thermo_utils module.

Tests thermodynamic calculations and unit conversions:
- psia_to_mpa, mpa_to_psia
- fahrenheit_to_kelvin, kelvin_to_fahrenheit
- kj_kg_to_btu_lb, btu_lb_to_kj_kg
- steam_enthalpy_btu_lb (with/without iapws)
- feedwater_enthalpy_btu_lb
- saturation_temperature, saturation_pressure
"""

import pytest
import math
from unittest.mock import MagicMock, patch
from odibi_core.functions import thermo_utils


# ============================================================================
# Unit Conversion Tests - Pressure
# ============================================================================


def test_psia_to_mpa_standard():
    """Test psia to MPa conversion for standard atmospheric pressure."""
    result = thermo_utils.psia_to_mpa(14.696)
    assert abs(result - 0.101325) < 0.0001


def test_psia_to_mpa_round_values():
    """Test psia to MPa conversion with round values."""
    result = thermo_utils.psia_to_mpa(100.0)
    assert abs(result - 0.689476) < 0.0001


def test_psia_to_mpa_zero():
    """Test psia to MPa conversion with zero."""
    result = thermo_utils.psia_to_mpa(0.0)
    assert result == 0.0


def test_mpa_to_psia_standard():
    """Test MPa to psia conversion for standard atmospheric pressure."""
    result = thermo_utils.mpa_to_psia(0.101325)
    assert abs(result - 14.696) < 0.001


def test_mpa_to_psia_round_trip():
    """Test MPa to psia round trip conversion."""
    original = 500.0
    converted = thermo_utils.psia_to_mpa(original)
    back = thermo_utils.mpa_to_psia(converted)
    assert abs(back - original) < 0.001


# ============================================================================
# Unit Conversion Tests - Temperature
# ============================================================================


def test_fahrenheit_to_kelvin_boiling_point():
    """Test °F to K conversion for boiling point of water."""
    result = thermo_utils.fahrenheit_to_kelvin(212.0)
    assert abs(result - 373.15) < 0.01


def test_fahrenheit_to_kelvin_freezing_point():
    """Test °F to K conversion for freezing point of water."""
    result = thermo_utils.fahrenheit_to_kelvin(32.0)
    assert abs(result - 273.15) < 0.01


def test_fahrenheit_to_kelvin_negative():
    """Test °F to K conversion with negative temperature."""
    result = thermo_utils.fahrenheit_to_kelvin(-40.0)
    # -40°F = -40°C = 233.15K
    assert abs(result - 233.15) < 0.01


def test_kelvin_to_fahrenheit_boiling_point():
    """Test K to °F conversion for boiling point of water."""
    result = thermo_utils.kelvin_to_fahrenheit(373.15)
    assert abs(result - 212.0) < 0.01


def test_kelvin_to_fahrenheit_absolute_zero():
    """Test K to °F conversion for absolute zero."""
    result = thermo_utils.kelvin_to_fahrenheit(0.0)
    assert abs(result - (-459.67)) < 0.01


def test_temperature_round_trip():
    """Test temperature conversion round trip."""
    original = 77.0
    kelvin = thermo_utils.fahrenheit_to_kelvin(original)
    back = thermo_utils.kelvin_to_fahrenheit(kelvin)
    assert abs(back - original) < 0.01


# ============================================================================
# Unit Conversion Tests - Enthalpy
# ============================================================================


def test_kj_kg_to_btu_lb_typical_steam():
    """Test kJ/kg to BTU/lb conversion for typical steam enthalpy."""
    result = thermo_utils.kj_kg_to_btu_lb(2500.0)
    assert abs(result - 1074.8) < 0.5


def test_kj_kg_to_btu_lb_zero():
    """Test kJ/kg to BTU/lb conversion with zero."""
    result = thermo_utils.kj_kg_to_btu_lb(0.0)
    assert result == 0.0


def test_btu_lb_to_kj_kg_typical_steam():
    """Test BTU/lb to kJ/kg conversion for typical steam enthalpy."""
    result = thermo_utils.btu_lb_to_kj_kg(1074.85)
    assert abs(result - 2500.0) < 0.5


def test_enthalpy_round_trip():
    """Test enthalpy conversion round trip."""
    original = 2000.0
    btu = thermo_utils.kj_kg_to_btu_lb(original)
    back = thermo_utils.btu_lb_to_kj_kg(btu)
    assert abs(back - original) < 0.01


# ============================================================================
# Steam Enthalpy Tests - Without IAPWS
# ============================================================================


@patch('odibi_core.functions.thermo_utils.IAPWS_AVAILABLE', False)
def test_steam_enthalpy_no_iapws():
    """Test steam_enthalpy raises ImportError without iapws."""
    with pytest.raises(ImportError, match="iapws library required"):
        thermo_utils.steam_enthalpy_btu_lb(100.0, quality=1.0)


@patch('odibi_core.functions.thermo_utils.IAPWS_AVAILABLE', False)
def test_feedwater_enthalpy_no_iapws():
    """Test feedwater_enthalpy raises ImportError without iapws."""
    with pytest.raises(ImportError, match="iapws library required"):
        thermo_utils.feedwater_enthalpy_btu_lb(1000.0, 300.0)


@patch('odibi_core.functions.thermo_utils.IAPWS_AVAILABLE', False)
def test_saturation_temperature_no_iapws():
    """Test saturation_temperature raises ImportError without iapws."""
    with pytest.raises(ImportError, match="iapws library required"):
        thermo_utils.saturation_temperature(14.696)


@patch('odibi_core.functions.thermo_utils.IAPWS_AVAILABLE', False)
def test_saturation_pressure_no_iapws():
    """Test saturation_pressure raises ImportError without iapws."""
    with pytest.raises(ImportError, match="iapws library required"):
        thermo_utils.saturation_pressure(212.0)


# ============================================================================
# Steam Enthalpy Tests - With IAPWS (Mocked)
# ============================================================================


@pytest.mark.skipif(not thermo_utils.IAPWS_AVAILABLE, reason="iapws not installed")
def test_steam_enthalpy_saturated():
    """Test steam enthalpy for saturated steam (quality=1.0)."""
    # This test requires iapws to be installed
    result = thermo_utils.steam_enthalpy_btu_lb(100.0, quality=1.0)
    # Approximate expected value for saturated steam at 100 psia
    assert 1180 < result < 1195


@pytest.mark.skipif(not thermo_utils.IAPWS_AVAILABLE, reason="iapws not installed")
def test_steam_enthalpy_superheated():
    """Test steam enthalpy for superheated steam."""
    result = thermo_utils.steam_enthalpy_btu_lb(500.0, temperature_f=600.0)
    # Approximate expected value for superheated steam at 500 psia, 600°F
    assert 1280 < result < 1310


@pytest.mark.skipif(not thermo_utils.IAPWS_AVAILABLE, reason="iapws not installed")
def test_steam_enthalpy_saturated_liquid():
    """Test steam enthalpy for saturated liquid (quality=0.0)."""
    result = thermo_utils.steam_enthalpy_btu_lb(100.0, quality=0.0)
    # Saturated liquid should have lower enthalpy than saturated vapor
    assert 290 < result < 310


def test_steam_enthalpy_no_params():
    """Test steam_enthalpy raises ValueError without temperature or quality."""
    if thermo_utils.IAPWS_AVAILABLE:
        with pytest.raises(ValueError, match="Either temperature_f or quality must be provided"):
            thermo_utils.steam_enthalpy_btu_lb(100.0)


# ============================================================================
# Feedwater Enthalpy Tests
# ============================================================================


@pytest.mark.skipif(not thermo_utils.IAPWS_AVAILABLE, reason="iapws not installed")
def test_feedwater_enthalpy_typical():
    """Test feedwater enthalpy at typical conditions."""
    result = thermo_utils.feedwater_enthalpy_btu_lb(1000.0, 300.0)
    # Approximate expected value for feedwater at 1000 psia, 300°F
    assert 260 < result < 280


@pytest.mark.skipif(not thermo_utils.IAPWS_AVAILABLE, reason="iapws not installed")
def test_feedwater_enthalpy_low_pressure():
    """Test feedwater enthalpy at low pressure."""
    result = thermo_utils.feedwater_enthalpy_btu_lb(14.696, 100.0)
    # Low pressure, low temperature feedwater
    assert 60 < result < 80


# ============================================================================
# Saturation Properties Tests
# ============================================================================


@pytest.mark.skipif(not thermo_utils.IAPWS_AVAILABLE, reason="iapws not installed")
def test_saturation_temperature_atmospheric():
    """Test saturation temperature at atmospheric pressure."""
    result = thermo_utils.saturation_temperature(14.696)
    # Should be close to 212°F (boiling point at 1 atm)
    assert abs(result - 212.0) < 1.0


@pytest.mark.skipif(not thermo_utils.IAPWS_AVAILABLE, reason="iapws not installed")
def test_saturation_temperature_high_pressure():
    """Test saturation temperature at high pressure."""
    result = thermo_utils.saturation_temperature(100.0)
    # Higher pressure means higher saturation temperature
    assert result > 300.0


@pytest.mark.skipif(not thermo_utils.IAPWS_AVAILABLE, reason="iapws not installed")
def test_saturation_pressure_boiling_point():
    """Test saturation pressure at boiling point."""
    result = thermo_utils.saturation_pressure(212.0)
    # Should be close to 14.696 psia (1 atm)
    assert abs(result - 14.696) < 0.5


@pytest.mark.skipif(not thermo_utils.IAPWS_AVAILABLE, reason="iapws not installed")
def test_saturation_pressure_high_temperature():
    """Test saturation pressure at high temperature."""
    result = thermo_utils.saturation_pressure(400.0)
    # Higher temperature means higher saturation pressure
    assert result > 200.0


# ============================================================================
# Edge Cases and Validation
# ============================================================================


def test_psia_to_mpa_negative():
    """Test psia to MPa with negative value (vacuum)."""
    # While physically unusual, should handle mathematically
    result = thermo_utils.psia_to_mpa(-10.0)
    assert result < 0.0


def test_fahrenheit_to_kelvin_extreme_high():
    """Test °F to K with extreme high temperature."""
    result = thermo_utils.fahrenheit_to_kelvin(1000.0)
    assert result > 500.0


def test_kj_kg_to_btu_lb_large_value():
    """Test kJ/kg to BTU/lb with large enthalpy value."""
    result = thermo_utils.kj_kg_to_btu_lb(5000.0)
    assert result > 2000.0
