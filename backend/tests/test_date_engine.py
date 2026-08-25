from datetime import date, timedelta

from app.engines.dates import days_to_renewal, is_overdue, is_renewing_soon

TODAY = date(2026, 8, 25)


def test_days_remaining_uses_injected_today():
    assert days_to_renewal(date(2026, 8, 28), TODAY) == 3


def test_renewing_soon_includes_today_and_day_seven():
    assert is_renewing_soon(0) is True
    assert is_renewing_soon(7) is True
    assert is_renewing_soon(8) is False


def test_overdue_is_not_renewing_soon():
    days = days_to_renewal(TODAY - timedelta(days=1), TODAY)
    assert days == -1
    assert is_overdue(days) is True
    assert is_renewing_soon(days) is False
