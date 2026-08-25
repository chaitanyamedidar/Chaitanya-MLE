import pytest

from app.engines.cost import monthly_rate


def test_monthly_passthrough():
    assert monthly_rate(649.0, "Monthly") == 649.0


def test_yearly_normalized_to_monthly():
    assert monthly_rate(120.0, "Yearly") == 10.0


def test_yearly_rounds_to_cents():
    assert monthly_rate(119.0, "Yearly") == 9.92


def test_rejects_non_positive_cost():
    with pytest.raises(ValueError):
        monthly_rate(0, "Monthly")
    with pytest.raises(ValueError):
        monthly_rate(-10, "Yearly")


def test_rejects_unknown_cycle():
    with pytest.raises(ValueError):
        monthly_rate(10, "Weekly")
