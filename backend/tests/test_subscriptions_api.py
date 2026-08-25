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


def test_create_normalizes_yearly_cost(client, auth):
    res = client.post(
        "/subscriptions",
        json=_payload(name="Adobe", cost=120, billing_cycle="Yearly"),
        headers=auth,
    )
    assert res.status_code == 201, res.text
    data = res.json()
    assert data["monthly_rate"] == 10.0
    assert data["status"] == "active"
    assert data["renewing_soon"] is True


def test_metrics_exclude_paused_from_burn_but_keep_row(client, auth):
    yearly = client.post(
        "/subscriptions",
        json=_payload(name="Adobe", cost=120, billing_cycle="Yearly"),
        headers=auth,
    ).json()
    monthly = client.post(
        "/subscriptions", json=_payload(name="Spotify", cost=199), headers=auth
    ).json()

    before = client.get("/metrics", headers=auth).json()
    assert before["monthly_burn_rate"] == 209.0
    assert before["upcoming_renewals_count"] == 2
    assert before["active_count"] == 2

    paused = client.patch(
        f"/subscriptions/{yearly['id']}/status", json={"status": "paused"}, headers=auth
    )
    assert paused.status_code == 200
    assert paused.json()["id"] == yearly["id"]
    assert paused.json()["status"] == "paused"

    listed = client.get("/subscriptions", headers=auth).json()
    ids = {row["id"] for row in listed}
    assert yearly["id"] in ids
    assert monthly["id"] in ids

    after = client.get("/metrics", headers=auth).json()
    assert after["monthly_burn_rate"] == 199.0
    assert after["paused_count"] == 1
    assert after["upcoming_renewals_count"] == 2


def test_unpause_restores_burn(client, auth):
    created = client.post("/subscriptions", json=_payload(cost=199), headers=auth).json()
    client.patch(
        f"/subscriptions/{created['id']}/status", json={"status": "paused"}, headers=auth
    )
    assert client.get("/metrics", headers=auth).json()["monthly_burn_rate"] == 0
    client.patch(
        f"/subscriptions/{created['id']}/status", json={"status": "active"}, headers=auth
    )
    assert client.get("/metrics", headers=auth).json()["monthly_burn_rate"] == 199.0


def test_rejects_past_renewal_date(client, auth):
    res = client.post(
        "/subscriptions",
        json=_payload(renewal_date=(TODAY - timedelta(days=2)).isoformat()),
        headers=auth,
    )
    assert res.status_code == 422


def test_validation_rejects_bad_payloads(client, auth):
    assert client.post("/subscriptions", json=_payload(name="  "), headers=auth).status_code == 422
    assert client.post("/subscriptions", json=_payload(cost=-1), headers=auth).status_code == 422
    assert (
        client.post("/subscriptions", json=_payload(billing_cycle="Weekly"), headers=auth).status_code
        == 422
    )


def test_unauthenticated_is_rejected(client):
    assert client.get("/metrics").status_code == 401
    assert client.get("/subscriptions").status_code == 401
