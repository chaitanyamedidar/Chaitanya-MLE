from datetime import date, timedelta

from app.ml.insights import build_insights, categorize
from app.models.subscription import Subscription


def _sub(**kwargs) -> Subscription:
    defaults = {
        "id": 1,
        "name": "Netflix",
        "cost": 649,
        "billing_cycle": "Monthly",
        "renewal_date": date.today() + timedelta(days=3),
        "status": "active",
    }
    defaults.update(kwargs)
    row = Subscription(
        name=defaults["name"],
        cost=defaults["cost"],
        billing_cycle=defaults["billing_cycle"],
        renewal_date=defaults["renewal_date"],
        status=defaults["status"],
    )
    row.id = defaults["id"]
    return row


def test_known_name_category():
    category, confidence = categorize("Netflix")
    assert category == "Streaming"
    assert confidence > 0.3


def test_insights_bundle(client):
    client.post(
        "/subscriptions",
        json={
            "name": "Netflix",
            "cost": 649,
            "billing_cycle": "Monthly",
            "renewal_date": (date.today() + timedelta(days=2)).isoformat(),
        },
    )
    client.post(
        "/subscriptions",
        json={
            "name": "Disney+",
            "cost": 299,
            "billing_cycle": "Monthly",
            "renewal_date": (date.today() + timedelta(days=10)).isoformat(),
        },
    )
    data = client.get("/insights").json()
    assert data["categories"]
    assert data["pause_recommendations"]
    assert data["cashflow"]
    cats = {row["category"] for row in data["categories"]}
    assert "Streaming" in cats
    overlap_cats = {row["category"] for row in data["overlaps"]}
    assert "Streaming" in overlap_cats


def test_paused_excluded_from_category_spend():
    today = date.today()
    payload = build_insights(
        [
            _sub(id=1, name="Netflix", cost=649, status="active"),
            _sub(id=2, name="Spotify", cost=119, status="paused"),
        ],
        today,
    )
    names = [n for row in payload["categories"] for n in row["names"]]
    assert "Netflix" in names
    assert "Spotify" not in names
