"""Tests for /dashboard/summary endpoint."""

from datetime import date


def test_summary_empty_db(client):
    resp = client.get("/dashboard/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_active_pigs"] == 0
    assert data["by_category"] == {}
    assert data["sick_or_quarantined"] == 0
    assert data["total_farrowings"] == 0
    assert data["avg_live_born"] == 0.0
    assert data["pen_utilisation"] == []
    assert data["health_distribution"] == {}


def test_summary_with_data(client):
    # Create a pen
    r = client.post("/pens/", json={"name": "Sum-Pen", "capacity": 20})
    pen_id = r.json()["id"]

    # Create pigs in different categories
    client.post("/pigs/", json={"ear_tag": "SOW-500", "category": "sow", "pen_id": pen_id})
    client.post("/pigs/", json={"ear_tag": "FIN-500", "category": "finisher", "pen_id": pen_id})
    client.post("/pigs/", json={"ear_tag": "PIG-500", "category": "piglet"})

    resp = client.get("/dashboard/summary")
    data = resp.json()
    assert data["total_active_pigs"] == 3
    assert data["by_category"]["sow"] == 1
    assert data["by_category"]["finisher"] == 1
    assert data["by_category"]["piglet"] == 1


def test_summary_health_distribution(client):
    pid_resp = client.post("/pigs/", json={"ear_tag": "SOW-501", "category": "sow"})
    pid = pid_resp.json()["id"]
    client.post("/health/", json={"pig_id": pid, "status": "sick", "record_date": str(date.today())})
    client.post("/health/", json={"pig_id": pid, "status": "quarantined", "record_date": str(date.today())})

    resp = client.get("/dashboard/summary")
    data = resp.json()
    assert data["sick_or_quarantined"] >= 2
    assert "sick" in data["health_distribution"]


def test_summary_pen_utilisation(client):
    r = client.post("/pens/", json={"name": "Util-Pen", "capacity": 10})
    pen_id = r.json()["id"]
    client.post("/pigs/", json={"ear_tag": "UT-001", "category": "finisher", "pen_id": pen_id})
    client.post("/pigs/", json={"ear_tag": "UT-002", "category": "finisher", "pen_id": pen_id})

    resp = client.get("/dashboard/summary")
    data = resp.json()
    util = [p for p in data["pen_utilisation"] if p["name"] == "Util-Pen"]
    assert len(util) == 1
    assert util[0]["current"] == 2
    assert util[0]["utilisation_pct"] == 20.0


def test_summary_farrowing_stats(client):
    sow_resp = client.post("/pigs/", json={"ear_tag": "SOW-502", "category": "sow"})
    sow_id = sow_resp.json()["id"]
    client.post("/farrowings/", json={
        "sow_id": sow_id,
        "farrowing_date": str(date.today()),
        "live_born": 12,
        "stillborn": 1,
    })
    resp = client.get("/dashboard/summary")
    data = resp.json()
    assert data["total_farrowings"] >= 1
    assert data["avg_live_born"] > 0
