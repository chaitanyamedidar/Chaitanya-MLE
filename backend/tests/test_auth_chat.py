def test_demo_login(client):
    res = client.post("/auth/login", json={"email": "demo@quantiphi.dev", "password": "Demo@123"})
    assert res.status_code == 200
    body = res.json()
    assert body["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {body['access_token']}"})
    assert me.status_code == 200
    assert me.json()["email"] == "demo@quantiphi.dev"


def test_bad_login(client):
    res = client.post("/auth/login", json={"email": "demo@quantiphi.dev", "password": "wrong-pass"})
    assert res.status_code == 401


from datetime import date, timedelta


def test_chat_uses_ledger_numbers(client, auth):
    client.post(
        "/subscriptions",
        json={
            "name": "Spotify",
            "cost": 199,
            "billing_cycle": "Monthly",
            "renewal_date": (date.today() + timedelta(days=5)).isoformat(),
        },
        headers=auth,
    )
    res = client.post("/chat", json={"message": "what is my monthly burn"}, headers=auth)
    assert res.status_code == 200
    body = res.json()
    assert "199" in body["reply"]
    assert body["source"] in {"intent", "gemini-2.5-flash"}
