from __future__ import annotations

from calendar import monthrange
from collections import defaultdict
from datetime import date
from pathlib import Path

import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline

from app.engines.cost import monthly_rate
from app.models.subscription import Subscription

CATALOG_PATH = Path(__file__).resolve().parents[2] / "data" / "saas_catalog.csv"
ESSENTIAL = {"Cloud", "Productivity"}



def _load_catalog() -> list[tuple[str, str, float]]:
    rows: list[tuple[str, str, float]] = []
    with CATALOG_PATH.open(encoding="utf-8") as handle:
        next(handle)
        for line in handle:
            name, category, typical = line.strip().split(",", 2)
            rows.append((name, category, float(typical)))
    return rows


_CATALOG = _load_catalog()
_CATEGORY_CLF = Pipeline(
    [
        ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ("clf", LogisticRegression(max_iter=400)),
    ]
)
_CATEGORY_CLF.fit([n for n, _, _ in _CATALOG], [c for _, c, _ in _CATALOG])

_typical = np.array([[p] for _, _, p in _CATALOG], dtype=float)
_ISO = IsolationForest(contamination=0.15, random_state=42)
_ISO.fit(_typical)


def categorize(name: str) -> tuple[str, float]:
    proba = _CATEGORY_CLF.predict_proba([name])[0]
    idx = int(np.argmax(proba))
    return str(_CATEGORY_CLF.classes_[idx]), float(proba[idx])


def _add_months(value: date, months: int) -> date:
    year = value.year + (value.month - 1 + months) // 12
    month = (value.month - 1 + months) % 12 + 1
    day = min(value.day, monthrange(year, month)[1])
    return date(year, month, day)


def _charges_in_window(sub: Subscription, start: date, end: date) -> list[tuple[date, float]]:
    charges: list[tuple[date, float]] = []
    cursor = sub.renewal_date
    step = 1 if sub.billing_cycle == "Monthly" else 12
    guard = 0
    while cursor < start and guard < 120:
        cursor = _add_months(cursor, step)
        guard += 1
    while cursor <= end and guard < 180:
        charges.append((cursor, float(sub.cost)))
        cursor = _add_months(cursor, step)
        guard += 1
    return charges


def build_insights(subs: list[Subscription], today: date | None = None) -> dict:
    current = today or date.today()
    labeled = []
    for sub in subs:
        category, confidence = categorize(sub.name)
        labeled.append(
            {
                "id": sub.id,
                "name": sub.name,
                "status": sub.status,
                "cost": sub.cost,
                "billing_cycle": sub.billing_cycle,
                "renewal_date": sub.renewal_date.isoformat(),
                "monthly_rate": monthly_rate(sub.cost, sub.billing_cycle),
                "category": category,
                "confidence": round(confidence, 3),
            }
        )

    spend: dict[str, float] = defaultdict(float)
    names_by_cat: dict[str, list[str]] = defaultdict(list)
    active = [row for row in labeled if row["status"] == "active"]
    for row in active:
        spend[row["category"]] += row["monthly_rate"]
        names_by_cat[row["category"]].append(row["name"])
    total = sum(spend.values()) or 1.0
    categories = [
        {
            "category": cat,
            "monthly_spend": round(amount, 2),
            "share": round(amount / total, 3),
            "names": names_by_cat[cat],
        }
        for cat, amount in sorted(spend.items(), key=lambda item: item[1], reverse=True)
    ]

    anomalies = []
    if active:
        flags = _ISO.predict([[row["monthly_rate"]] for row in active])
        high_cut = float(np.median(_typical))
        for row, flag in zip(active, flags, strict=True):
            if flag == -1 and row["monthly_rate"] >= high_cut:
                anomalies.append(
                    {
                        "id": row["id"],
                        "name": row["name"],
                        "monthly_rate": row["monthly_rate"],
                        "category": row["category"],
                        "reason": "Monthly cost is high versus typical catalog prices",
                    }
                )

    overlaps = []
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in labeled:
        grouped[row["category"]].append(row)
    for cat, group in grouped.items():
        unique_names = {item["name"] for item in group}
        if len(unique_names) < 2:
            continue
        monthly = round(sum(item["monthly_rate"] for item in group if item["status"] == "active"), 2)
        overlaps.append(
            {
                "category": cat,
                "names": sorted(unique_names),
                "monthly_spend": monthly,
                "suggestion": (
                    f"You have {len(unique_names)} {cat} services. "
                    f"Pausing one trims part of {monthly:.2f}/mo."
                ),
            }
        )

    ranked = sorted(active, key=lambda row: row["monthly_rate"], reverse=True)
    non_essential = [row for row in ranked if row["category"] not in ESSENTIAL] or ranked
    pause_recommendations = [
        {
            "id": row["id"],
            "name": row["name"],
            "category": row["category"],
            "monthly_rate": row["monthly_rate"],
            "savings_if_paused": row["monthly_rate"],
        }
        for row in non_essential[:2]
    ]

    window_end = _add_months(current, 3)
    buckets: dict[str, float] = defaultdict(float)
    labels: dict[str, list[str]] = defaultdict(list)
    for sub in subs:
        if sub.status != "active":
            continue
        for when, amount in _charges_in_window(sub, current, window_end):
            key = when.strftime("%Y-%m")
            buckets[key] += amount
            labels[key].append(sub.name)
    cashflow = [
        {
            "month": key,
            "amount": round(amount, 2),
            "names": labels[key],
        }
        for key, amount in sorted(buckets.items())
    ]

    return {
        "categories": categories,
        "anomalies": anomalies,
        "overlaps": overlaps,
        "pause_recommendations": pause_recommendations,
        "cashflow": cashflow,
    }
