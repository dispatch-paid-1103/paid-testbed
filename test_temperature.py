import pytest

from temperature import convert


@pytest.mark.parametrize(
    "value, from_unit, to_unit, expected",
    [
        (0, "C", "F", 32.0),
        (100, "C", "F", 212.0),
        (0, "C", "K", 273.15),
        (100, "C", "K", 373.15),
        (32, "F", "C", 0.0),
        (212, "F", "C", 100.0),
        (32, "F", "K", 273.15),
        (212, "F", "K", 373.15),
        (273.15, "K", "C", 0.0),
        (0, "K", "C", -273.15),
        (373.15, "K", "F", 212.0),
        (0, "K", "F", -459.67),
        (-40, "C", "F", -40.0),
        (-40, "F", "C", -40.0),
    ],
)
def test_known_conversions(value, from_unit, to_unit, expected):
    assert convert(value, from_unit, to_unit) == pytest.approx(expected)


def test_units_are_case_insensitive():
    assert convert(100, "c", "k") == pytest.approx(373.15)
    assert convert(212, "f", "C") == pytest.approx(100.0)
    assert convert(0, "k", "f") == pytest.approx(-459.67)


def test_units_ignore_surrounding_whitespace():
    assert convert(0, " c ", "F\n") == pytest.approx(32.0)


@pytest.mark.parametrize("unit", ["C", "F", "K", "c"])
def test_identity_conversion(unit):
    result = convert(25, unit, unit)
    assert result == 25.0
    assert isinstance(result, float)


@pytest.mark.parametrize(
    "from_unit, to_unit",
    [("C", "F"), ("C", "K"), ("F", "C"), ("F", "K"), ("K", "C"), ("K", "F")],
)
@pytest.mark.parametrize("value", [0.0, 37.5, 1000.0])
def test_round_trip(value, from_unit, to_unit):
    there = convert(value, from_unit, to_unit)
    assert convert(there, to_unit, from_unit) == pytest.approx(value)


@pytest.mark.parametrize(
    "from_unit, to_unit",
    [("X", "C"), ("C", "Z"), ("", "C"), ("C", ""), ("Celsius", "F"), ("C", "kelvin")],
)
def test_unknown_unit_raises(from_unit, to_unit):
    with pytest.raises(ValueError):
        convert(10, from_unit, to_unit)


def test_unknown_unit_reported_before_bad_value():
    with pytest.raises(ValueError, match="unit"):
        convert(-1000, "X", "C")


@pytest.mark.parametrize(
    "value, from_unit",
    [(-300, "C"), (-273.16, "C"), (-500, "F"), (-459.68, "F"), (-1, "K"), (-0.001, "K")],
)
@pytest.mark.parametrize("to_unit", ["C", "F", "K"])
def test_below_absolute_zero_raises(value, from_unit, to_unit):
    with pytest.raises(ValueError):
        convert(value, from_unit, to_unit)


@pytest.mark.parametrize(
    "value, from_unit",
    [(-273.15, "C"), (-459.67, "F"), (0, "K")],
)
@pytest.mark.parametrize("to_unit", ["C", "F", "K"])
def test_absolute_zero_is_allowed(value, from_unit, to_unit):
    result = convert(value, from_unit, to_unit)
    expected = {"C": -273.15, "F": -459.67, "K": 0.0}[to_unit]
    assert result == pytest.approx(expected, abs=1e-9)


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_non_finite_values_raise(bad):
    with pytest.raises(ValueError):
        convert(bad, "C", "K")
