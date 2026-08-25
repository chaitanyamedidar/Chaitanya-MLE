"""Date Intersect Calculator — days until next billing vs a fixed server date."""

from __future__ import annotations

from datetime import date

URGENT_WINDOW_DAYS = 7


def days_to_renewal(renewal_date: date, today: date | None = None) -> int:
    current = today if today is not None else date.today()
    return (renewal_date - current).days


def is_renewing_soon(days: int) -> bool:
    return 0 <= days <= URGENT_WINDOW_DAYS


def is_overdue(days: int) -> bool:
    return days < 0
