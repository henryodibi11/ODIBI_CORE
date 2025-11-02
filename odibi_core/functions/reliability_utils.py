"""
Reliability Utilities - Industrial systems reliability and availability metrics.

Provides functions for calculating MTBF, MTTR, availability, failure rates,
and reliability metrics commonly used in industrial asset management and
maintenance engineering.
"""

from typing import List, Optional
import math


def mean_time_between_failures(
    total_operating_time: float,
    number_of_failures: int
) -> float:
    """
    Calculate Mean Time Between Failures (MTBF).

    MTBF = Total Operating Time / Number of Failures

    Args:
        total_operating_time: Total time equipment was operational (hours)
        number_of_failures: Count of failures during the period

    Returns:
        float: MTBF in hours

    Raises:
        ValueError: If number_of_failures is zero

    Examples:
        >>> # Equipment ran 8760 hours with 4 failures
        >>> mean_time_between_failures(8760.0, 4)
        2190.0

        >>> # Equipment ran 1000 hours with 2 failures
        >>> mean_time_between_failures(1000.0, 2)
        500.0
    """
    if number_of_failures == 0:
        raise ValueError("Number of failures must be greater than zero")
    
    return total_operating_time / number_of_failures


def mttr(
    total_repair_time: float,
    number_of_repairs: int
) -> float:
    """
    Calculate Mean Time To Repair (MTTR).

    MTTR = Total Repair Time / Number of Repairs

    Args:
        total_repair_time: Sum of all repair durations (hours)
        number_of_repairs: Count of repair events

    Returns:
        float: MTTR in hours

    Raises:
        ValueError: If number_of_repairs is zero

    Examples:
        >>> # 4 repairs taking total of 20 hours
        >>> mttr(20.0, 4)
        5.0

        >>> # 10 repairs taking total of 35 hours
        >>> mttr(35.0, 10)
        3.5
    """
    if number_of_repairs == 0:
        raise ValueError("Number of repairs must be greater than zero")
    
    return total_repair_time / number_of_repairs


def availability_index(
    mtbf: float,
    mttr_value: float
) -> float:
    """
    Calculate system availability index.

    Availability = MTBF / (MTBF + MTTR)

    Args:
        mtbf: Mean time between failures (hours)
        mttr_value: Mean time to repair (hours)

    Returns:
        float: Availability as decimal (0.0 to 1.0)

    Examples:
        >>> # MTBF=2000h, MTTR=10h
        >>> availability_index(2000.0, 10.0)
        0.995

        >>> # MTBF=100h, MTTR=5h
        >>> availability_index(100.0, 5.0)
        0.952
    """
    if mtbf < 0 or mttr_value < 0:
        raise ValueError("MTBF and MTTR must be non-negative")
    
    if mtbf + mttr_value == 0:
        return 0.0
    
    return mtbf / (mtbf + mttr_value)


def failure_rate(mtbf: float) -> float:
    """
    Calculate failure rate (lambda) from MTBF.

    Failure Rate (λ) = 1 / MTBF

    Args:
        mtbf: Mean time between failures (hours)

    Returns:
        float: Failure rate (failures per hour)

    Raises:
        ValueError: If MTBF is zero or negative

    Examples:
        >>> # MTBF = 2000 hours
        >>> failure_rate(2000.0)
        0.0005

        >>> # MTBF = 10000 hours
        >>> failure_rate(10000.0)
        0.0001
    """
    if mtbf <= 0:
        raise ValueError("MTBF must be positive")
    
    return 1.0 / mtbf


def reliability_at_time(
    time: float,
    mtbf: float,
    distribution: str = "exponential"
) -> float:
    """
    Calculate reliability at a specific time.

    For exponential distribution: R(t) = e^(-λt) = e^(-t/MTBF)

    Args:
        time: Operating time (hours)
        mtbf: Mean time between failures (hours)
        distribution: Failure distribution model (currently supports "exponential")

    Returns:
        float: Reliability at time t (0.0 to 1.0)

    Raises:
        ValueError: If time or MTBF is negative
        NotImplementedError: If distribution is not supported

    Examples:
        >>> # Reliability after 1000 hours with MTBF=10000
        >>> reliability_at_time(1000.0, 10000.0)
        0.9048

        >>> # Reliability after 5000 hours with MTBF=10000
        >>> reliability_at_time(5000.0, 10000.0)
        0.6065
    """
    if time < 0 or mtbf <= 0:
        raise ValueError("Time and MTBF must be non-negative")
    
    if distribution.lower() == "exponential":
        lambda_rate = failure_rate(mtbf)
        return math.exp(-lambda_rate * time)
    else:
        raise NotImplementedError(f"Distribution '{distribution}' not yet supported")


def mission_reliability(
    component_reliabilities: List[float],
    configuration: str = "series"
) -> float:
    """
    Calculate system reliability for components in series or parallel.

    Series: R_sys = R1 × R2 × ... × Rn
    Parallel: R_sys = 1 - (1-R1) × (1-R2) × ... × (1-Rn)

    Args:
        component_reliabilities: List of individual component reliabilities (0.0 to 1.0)
        configuration: "series" or "parallel"

    Returns:
        float: System reliability (0.0 to 1.0)

    Raises:
        ValueError: If reliabilities are out of range or configuration is invalid

    Examples:
        >>> # Three components in series with R=0.95 each
        >>> mission_reliability([0.95, 0.95, 0.95], "series")
        0.857

        >>> # Two components in parallel with R=0.90 each
        >>> mission_reliability([0.90, 0.90], "parallel")
        0.99
    """
    if not component_reliabilities:
        raise ValueError("Component reliabilities list cannot be empty")
    
    for r in component_reliabilities:
        if not 0.0 <= r <= 1.0:
            raise ValueError(f"Reliability must be between 0.0 and 1.0, got {r}")
    
    if configuration.lower() == "series":
        result = 1.0
        for r in component_reliabilities:
            result *= r
        return result
    
    elif configuration.lower() == "parallel":
        result = 1.0
        for r in component_reliabilities:
            result *= (1.0 - r)
        return 1.0 - result
    
    else:
        raise ValueError(f"Configuration must be 'series' or 'parallel', got '{configuration}'")


def expected_failures(
    lambda_rate: float,
    time_period: float
) -> float:
    """
    Calculate expected number of failures in a time period.

    Expected Failures = λ × t

    Args:
        lambda_rate: Failure rate (failures per hour)
        time_period: Time period duration (hours)

    Returns:
        float: Expected number of failures

    Examples:
        >>> # Failure rate 0.0001/hr over 1000 hours
        >>> expected_failures(0.0001, 1000.0)
        0.1

        >>> # Failure rate 0.002/hr over 500 hours
        >>> expected_failures(0.002, 500.0)
        1.0
    """
    if lambda_rate < 0 or time_period < 0:
        raise ValueError("Failure rate and time period must be non-negative")
    
    return lambda_rate * time_period


def weibull_reliability(
    time: float,
    characteristic_life: float,
    shape_parameter: float
) -> float:
    """
    Calculate reliability using Weibull distribution.

    R(t) = e^(-(t/η)^β)
    where η = characteristic life, β = shape parameter

    Args:
        time: Operating time
        characteristic_life: Characteristic life (η) - scale parameter
        shape_parameter: Shape parameter (β) - determines failure mode
                        β < 1: infant mortality
                        β = 1: random failures (exponential)
                        β > 1: wear-out failures

    Returns:
        float: Reliability at time t (0.0 to 1.0)

    Examples:
        >>> # Wear-out failures (β=2.5) at t=1000, η=5000
        >>> weibull_reliability(1000.0, 5000.0, 2.5)
        0.924

        >>> # Random failures (β=1.0) at t=1000, η=5000
        >>> weibull_reliability(1000.0, 5000.0, 1.0)
        0.819
    """
    if time < 0 or characteristic_life <= 0 or shape_parameter <= 0:
        raise ValueError("Invalid parameters for Weibull distribution")
    
    return math.exp(-math.pow(time / characteristic_life, shape_parameter))


__all__ = [
    "mean_time_between_failures",
    "mttr",
    "availability_index",
    "failure_rate",
    "reliability_at_time",
    "mission_reliability",
    "expected_failures",
    "weibull_reliability",
]
