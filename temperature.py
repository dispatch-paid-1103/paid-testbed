"""Temperature unit conversion between Celsius, Fahrenheit and Kelvin."""

import math

_ABSOLUTE_ZERO = {"C": -273.15, "F": -459.67, "K": 0.0}


def _validate_unit(unit: str) -> str:
    """Return the normalised unit symbol, or raise ValueError if unknown."""
    normalised = unit.strip().upper()
    if normalised not in _ABSOLUTE_ZERO:
        raise ValueError(
            f"Unknown temperature unit {unit!r}; expected one of 'C', 'F', 'K'"
        )
    return normalised


def _to_kelvin(value: float, unit: str) -> float:
    if unit == "C":
        return value + 273.15
    if unit == "F":
        return (value - 32) * 5 / 9 + 273.15
    return value


def _from_kelvin(kelvin: float, unit: str) -> float:
    if unit == "C":
        return kelvin - 273.15
    if unit == "F":
        return (kelvin - 273.15) * 9 / 5 + 32
    return kelvin


def convert(value: float, from_unit: str, to_unit: str) -> float:
    """Convert a temperature between Celsius, Fahrenheit and Kelvin.

    Units are given as "C", "F" or "K" (case-insensitive).

    Raises:
        ValueError: if a unit is unknown, if the value is not finite, or if the
            value is below absolute zero in its source unit.
    """
    source = _validate_unit(from_unit)
    target = _validate_unit(to_unit)

    if not math.isfinite(value):
        raise ValueError(f"Temperature must be a finite number, got {value!r}")
    # Check in the source unit so the absolute-zero boundary is exact.
    if value < _ABSOLUTE_ZERO[source]:
        raise ValueError(
            f"Temperature {value!r} {source} is below absolute zero"
        )

    if source == target:
        return float(value)
    return _from_kelvin(_to_kelvin(value, source), target)
