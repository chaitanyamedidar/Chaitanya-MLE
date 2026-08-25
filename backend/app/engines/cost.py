"""Cost Uniformity Engine — normalize any billing cycle to a monthly rate."""

from __future__ import annotations

MONTHLY = "Monthly"
YEARLY = "Yearly"
VALID_CYCLES = (MONTHLY, YEARLY)


def monthly_rate(cost: float, billing_cycle: str) -> float:
    if cost <= 0:
        raise ValueError("cost must be greater than 0")
    if billing_cycle == MONTHLY:
        return round(cost, 2)
    if billing_cycle == YEARLY:
        return round(cost / 12.0, 2)
    raise ValueError(f"billing_cycle must be {MONTHLY} or {YEARLY}")
