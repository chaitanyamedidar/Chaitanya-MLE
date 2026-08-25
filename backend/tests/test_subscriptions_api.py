from datetime import date, timedelta

TODAY = date.today()


def _payload(**overrides):
    body = {
        "name": "Netflix",
        "cost": 649,
        "billing_cycle": "Monthly",
        "renewal_date": (TODAY + timedelta(days=3)).isoformat(),
    }
    body.update(overrides)
    return body


def test_create_normalizes_yearly_cost(client):
    res = client.post("/subscriptions", json=_payload(name="Adobe", cost=120, billing_cycle="Yearly"))
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["monthly_rate"] == 10.0
    assert data["status"] == "active"
    assert data["renewing_soon"] is True


def test_metrics_exclude_paused_from_burn_but_keep_row(client):
    yearly = client.post(
        "/subscriptions",
        json=_payload(name="Adobe", cost=120, billing_cycle="Yearly"),
    ).json()
    monthly = client.post("/subscriptions", json=_payload(name="Spotify", cost=199)).json()

    before = client.get("/metrics").json()
    assert before["monthly_burn_rate"] == 209.0
    assert before["upcoming_renewals_count"] == 2
    assert before["active_count"] == 2

    paused = client.patch(f"/subscriptions/{yearly['id']}/status", json={"status": "paused"})
    assert paused.status_code == 200
    assert paused.json()["id"] == yearly["id"]
    assert paused.json()["status"] == "paused"

    listed = client.get("/subscriptions").json()
    ids = {row["id"] for row in listed}
    assert yearly["id"] in ids
    assert monthly["id"] in ids

    after = client.get("/metrics").json()
    assert after["monthly_burn_rate"] == 199.0
    assert after["paused_count"] == 1
    assert after["upcoming_renewals_count"] == 2


def test_unpause_restores_burn(client):
    created = client.post("/subscriptions", json=_payload(cost=199)).json()
    client.patch(f"/subscriptions/{created['id']}/status", json={"status": "paused"})
    assert client.get("/metrics").json()["monthly_burn_rate"] == 0
    client.patch(f"/subscriptions/{created['id']}/status", json={"status": "active"})
    assert client.get("/metrics").json()["monthly_burn_rate"] == 199.0


def test_overdue_is_not_soon(client):
    res = client.post(
        "/subscriptions",
        json=_payload(renewal_date=(TODAY - timedelta(days=2)).isoformat()),
    )
    data = res.json()
    assert data["overdue"] is True
    assert data["renewing_soon"] is False
    assert client.get("/metrics").json()["upcoming_renewals_count"] == 0


def test_validation_rejects_bad_payloads(client):
    assert client.post("/subscriptions", json=_payload(name="  ")).status_code == 422
    assert client.post("/subscriptions", json=_payload(cost=-1)).status_code == 422
    assert client.post("/subscriptions", json=_payload(billing_cycle="Weekly")).status_code == 422
