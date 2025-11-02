"""
Unit tests for reliability_utils module.

Tests reliability and availability metrics:
- mean_time_between_failures
- mttr
- availability_index
- failure_rate
- reliability_at_time
- mission_reliability
- expected_failures
- weibull_reliability
"""

import pytest
import math
from odibi_core.functions import reliability_utils


# ============================================================================
# MTBF Tests
# ============================================================================


def test_mtbf_typical_case():
    """Test MTBF calculation with typical values."""
    # 8760 hours (1 year) with 4 failures
    result = reliability_utils.mean_time_between_failures(8760.0, 4)
    assert result == 2190.0


def test_mtbf_single_failure():
    """Test MTBF with single failure."""
    result = reliability_utils.mean_time_between_failures(1000.0, 1)
    assert result == 1000.0


def test_mtbf_many_failures():
    """Test MTBF with many failures."""
    result = reliability_utils.mean_time_between_failures(10000.0, 50)
    assert result == 200.0


def test_mtbf_zero_failures():
    """Test MTBF raises ValueError with zero failures."""
    with pytest.raises(ValueError, match="Number of failures must be greater than zero"):
        reliability_utils.mean_time_between_failures(1000.0, 0)


def test_mtbf_high_reliability():
    """Test MTBF for highly reliable equipment."""
    # Very few failures
    result = reliability_utils.mean_time_between_failures(100000.0, 2)
    assert result == 50000.0


# ============================================================================
# MTTR Tests
# ============================================================================


def test_mttr_typical_case():
    """Test MTTR calculation with typical values."""
    # 4 repairs taking 20 hours total
    result = reliability_utils.mttr(20.0, 4)
    assert result == 5.0


def test_mttr_single_repair():
    """Test MTTR with single repair."""
    result = reliability_utils.mttr(3.5, 1)
    assert result == 3.5


def test_mttr_quick_repairs():
    """Test MTTR with many quick repairs."""
    result = reliability_utils.mttr(35.0, 10)
    assert result == 3.5


def test_mttr_zero_repairs():
    """Test MTTR raises ValueError with zero repairs."""
    with pytest.raises(ValueError, match="Number of repairs must be greater than zero"):
        reliability_utils.mttr(10.0, 0)


def test_mttr_long_repair():
    """Test MTTR with long single repair."""
    result = reliability_utils.mttr(48.0, 1)
    assert result == 48.0


# ============================================================================
# Availability Index Tests
# ============================================================================


def test_availability_high_mtbf():
    """Test availability with high MTBF and low MTTR."""
    # MTBF=2000h, MTTR=10h
    result = reliability_utils.availability_index(2000.0, 10.0)
    assert abs(result - 0.995) < 0.001


def test_availability_moderate():
    """Test availability with moderate MTBF and MTTR."""
    # MTBF=100h, MTTR=5h
    result = reliability_utils.availability_index(100.0, 5.0)
    assert abs(result - 0.952) < 0.001


def test_availability_low():
    """Test availability with low MTBF."""
    # Frequent failures
    result = reliability_utils.availability_index(50.0, 10.0)
    assert abs(result - 0.833) < 0.001


def test_availability_perfect():
    """Test availability approaches 1.0 with very high MTBF."""
    result = reliability_utils.availability_index(100000.0, 1.0)
    assert result > 0.99999


def test_availability_negative_mtbf():
    """Test availability raises ValueError with negative MTBF."""
    with pytest.raises(ValueError, match="MTBF and MTTR must be non-negative"):
        reliability_utils.availability_index(-100.0, 5.0)


def test_availability_negative_mttr():
    """Test availability raises ValueError with negative MTTR."""
    with pytest.raises(ValueError, match="MTBF and MTTR must be non-negative"):
        reliability_utils.availability_index(100.0, -5.0)


def test_availability_both_zero():
    """Test availability with both MTBF and MTTR zero."""
    result = reliability_utils.availability_index(0.0, 0.0)
    assert result == 0.0


# ============================================================================
# Failure Rate Tests
# ============================================================================


def test_failure_rate_typical():
    """Test failure rate calculation."""
    # MTBF=2000 hours
    result = reliability_utils.failure_rate(2000.0)
    assert abs(result - 0.0005) < 0.0001


def test_failure_rate_high_mtbf():
    """Test failure rate with high MTBF (low failure rate)."""
    result = reliability_utils.failure_rate(10000.0)
    assert abs(result - 0.0001) < 0.00001


def test_failure_rate_low_mtbf():
    """Test failure rate with low MTBF (high failure rate)."""
    result = reliability_utils.failure_rate(100.0)
    assert abs(result - 0.01) < 0.001


def test_failure_rate_zero_mtbf():
    """Test failure rate raises ValueError with zero MTBF."""
    with pytest.raises(ValueError, match="MTBF must be positive"):
        reliability_utils.failure_rate(0.0)


def test_failure_rate_negative_mtbf():
    """Test failure rate raises ValueError with negative MTBF."""
    with pytest.raises(ValueError, match="MTBF must be positive"):
        reliability_utils.failure_rate(-100.0)


# ============================================================================
# Reliability at Time Tests
# ============================================================================


def test_reliability_at_time_exponential():
    """Test reliability calculation with exponential distribution."""
    # R(1000) with MTBF=10000
    result = reliability_utils.reliability_at_time(1000.0, 10000.0)
    # R(t) = e^(-t/MTBF) = e^(-0.1) ≈ 0.9048
    assert abs(result - 0.9048) < 0.001


def test_reliability_at_time_half_life():
    """Test reliability at half MTBF."""
    result = reliability_utils.reliability_at_time(5000.0, 10000.0)
    # R(0.5*MTBF) = e^(-0.5) ≈ 0.6065
    assert abs(result - 0.6065) < 0.001


def test_reliability_at_zero_time():
    """Test reliability at t=0 (should be 1.0)."""
    result = reliability_utils.reliability_at_time(0.0, 10000.0)
    assert abs(result - 1.0) < 0.0001


def test_reliability_at_mtbf():
    """Test reliability at t=MTBF (should be e^-1)."""
    result = reliability_utils.reliability_at_time(10000.0, 10000.0)
    # R(MTBF) = e^(-1) ≈ 0.3679
    assert abs(result - 0.3679) < 0.001


def test_reliability_negative_time():
    """Test reliability raises ValueError with negative time."""
    with pytest.raises(ValueError, match="Time and MTBF must be non-negative"):
        reliability_utils.reliability_at_time(-100.0, 1000.0)


def test_reliability_unsupported_distribution():
    """Test reliability raises NotImplementedError for unsupported distribution."""
    with pytest.raises(NotImplementedError, match="Distribution 'weibull' not yet supported"):
        reliability_utils.reliability_at_time(1000.0, 10000.0, distribution="weibull")


# ============================================================================
# Mission Reliability Tests
# ============================================================================


def test_mission_reliability_series_identical():
    """Test series system reliability with identical components."""
    # Three components in series with R=0.95 each
    result = reliability_utils.mission_reliability([0.95, 0.95, 0.95], "series")
    # R_sys = 0.95^3 ≈ 0.857
    assert abs(result - 0.857375) < 0.001


def test_mission_reliability_series_different():
    """Test series system reliability with different components."""
    result = reliability_utils.mission_reliability([0.9, 0.95, 0.99], "series")
    # R_sys = 0.9 * 0.95 * 0.99 ≈ 0.846
    assert abs(result - 0.84645) < 0.001


def test_mission_reliability_parallel_identical():
    """Test parallel system reliability with identical components."""
    # Two components in parallel with R=0.90 each
    result = reliability_utils.mission_reliability([0.90, 0.90], "parallel")
    # R_sys = 1 - (1-0.9)^2 = 1 - 0.01 = 0.99
    assert abs(result - 0.99) < 0.001


def test_mission_reliability_parallel_different():
    """Test parallel system reliability with different components."""
    result = reliability_utils.mission_reliability([0.8, 0.9, 0.95], "parallel")
    # R_sys = 1 - (1-0.8)*(1-0.9)*(1-0.95)
    expected = 1 - (0.2 * 0.1 * 0.05)
    assert abs(result - expected) < 0.001


def test_mission_reliability_single_component():
    """Test system reliability with single component."""
    result = reliability_utils.mission_reliability([0.95], "series")
    assert result == 0.95


def test_mission_reliability_perfect_components():
    """Test reliability with perfect components (R=1.0)."""
    result = reliability_utils.mission_reliability([1.0, 1.0, 1.0], "series")
    assert result == 1.0


def test_mission_reliability_failed_component_series():
    """Test series system with one failed component (R=0)."""
    result = reliability_utils.mission_reliability([0.9, 0.0, 0.95], "series")
    assert result == 0.0


def test_mission_reliability_failed_component_parallel():
    """Test parallel system with one failed component."""
    result = reliability_utils.mission_reliability([0.9, 0.0], "parallel")
    assert result == 0.9


def test_mission_reliability_empty_list():
    """Test mission reliability raises ValueError with empty list."""
    with pytest.raises(ValueError, match="Component reliabilities list cannot be empty"):
        reliability_utils.mission_reliability([], "series")


def test_mission_reliability_invalid_value():
    """Test mission reliability raises ValueError with invalid reliability."""
    with pytest.raises(ValueError, match="Reliability must be between 0.0 and 1.0"):
        reliability_utils.mission_reliability([0.5, 1.5], "series")


def test_mission_reliability_invalid_configuration():
    """Test mission reliability raises ValueError with invalid configuration."""
    with pytest.raises(ValueError, match="Configuration must be 'series' or 'parallel'"):
        reliability_utils.mission_reliability([0.9, 0.95], "hybrid")


# ============================================================================
# Expected Failures Tests
# ============================================================================


def test_expected_failures_typical():
    """Test expected failures calculation."""
    # Failure rate 0.0001/hr over 1000 hours
    result = reliability_utils.expected_failures(0.0001, 1000.0)
    assert abs(result - 0.1) < 0.001


def test_expected_failures_one_failure():
    """Test expected failures equals one."""
    # Failure rate 0.002/hr over 500 hours
    result = reliability_utils.expected_failures(0.002, 500.0)
    assert abs(result - 1.0) < 0.001


def test_expected_failures_many():
    """Test expected failures with high rate."""
    result = reliability_utils.expected_failures(0.01, 500.0)
    assert abs(result - 5.0) < 0.001


def test_expected_failures_zero_rate():
    """Test expected failures with zero failure rate."""
    result = reliability_utils.expected_failures(0.0, 1000.0)
    assert result == 0.0


def test_expected_failures_zero_time():
    """Test expected failures with zero time period."""
    result = reliability_utils.expected_failures(0.001, 0.0)
    assert result == 0.0


def test_expected_failures_negative_rate():
    """Test expected failures raises ValueError with negative rate."""
    with pytest.raises(ValueError, match="Failure rate and time period must be non-negative"):
        reliability_utils.expected_failures(-0.001, 1000.0)


def test_expected_failures_negative_time():
    """Test expected failures raises ValueError with negative time."""
    with pytest.raises(ValueError, match="Failure rate and time period must be non-negative"):
        reliability_utils.expected_failures(0.001, -1000.0)


# ============================================================================
# Weibull Reliability Tests
# ============================================================================


def test_weibull_reliability_wear_out():
    """Test Weibull reliability with wear-out failures (β>1)."""
    # β=2.5 (wear-out) at t=1000, η=5000
    result = reliability_utils.weibull_reliability(1000.0, 5000.0, 2.5)
    # R(t) = e^(-(1000/5000)^2.5) = e^(-(0.2)^2.5)
    expected = math.exp(-math.pow(0.2, 2.5))
    assert abs(result - expected) < 0.001


def test_weibull_reliability_random_failures():
    """Test Weibull reliability with random failures (β=1, exponential)."""
    # β=1.0 reduces to exponential distribution
    result = reliability_utils.weibull_reliability(1000.0, 5000.0, 1.0)
    expected = math.exp(-1000.0 / 5000.0)
    assert abs(result - expected) < 0.001


def test_weibull_reliability_infant_mortality():
    """Test Weibull reliability with infant mortality (β<1)."""
    # β=0.5 (decreasing failure rate)
    result = reliability_utils.weibull_reliability(1000.0, 5000.0, 0.5)
    expected = math.exp(-math.pow(1000.0 / 5000.0, 0.5))
    assert abs(result - expected) < 0.001


def test_weibull_reliability_at_zero():
    """Test Weibull reliability at t=0 (should be 1.0)."""
    result = reliability_utils.weibull_reliability(0.0, 5000.0, 2.5)
    assert abs(result - 1.0) < 0.0001


def test_weibull_reliability_at_characteristic_life():
    """Test Weibull reliability at t=η (characteristic life)."""
    # At t=η, R(η) = e^-1 ≈ 0.3679 for any β
    result = reliability_utils.weibull_reliability(5000.0, 5000.0, 2.5)
    assert abs(result - 0.3679) < 0.001


def test_weibull_reliability_negative_time():
    """Test Weibull raises ValueError with negative time."""
    with pytest.raises(ValueError, match="Invalid parameters for Weibull distribution"):
        reliability_utils.weibull_reliability(-100.0, 5000.0, 2.5)


def test_weibull_reliability_zero_eta():
    """Test Weibull raises ValueError with zero characteristic life."""
    with pytest.raises(ValueError, match="Invalid parameters for Weibull distribution"):
        reliability_utils.weibull_reliability(1000.0, 0.0, 2.5)


def test_weibull_reliability_zero_beta():
    """Test Weibull raises ValueError with zero shape parameter."""
    with pytest.raises(ValueError, match="Invalid parameters for Weibull distribution"):
        reliability_utils.weibull_reliability(1000.0, 5000.0, 0.0)


def test_weibull_reliability_high_beta():
    """Test Weibull reliability with high β (rapid wear-out)."""
    # β=5.0 means very rapid wear-out
    result = reliability_utils.weibull_reliability(4000.0, 5000.0, 5.0)
    # Should be lower reliability due to rapid wear-out
    assert result < 0.5
