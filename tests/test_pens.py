"""Tests for /pens endpoints."""


def test_create_pen(client):
    resp = client.post("/pens/", json={
        "name": "Test-Pen-1",
        "capacity": 25,
        "pen_type": "finishing",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test-Pen-1"
    assert data["capacity"] == 25


def test_create_duplicate_pen(client):
    client.post("/pens/", json={"name": "Dup-Pen", "capacity": 10})
    resp = client.post("/pens/", json={"name": "Dup-Pen", "capacity": 20})
    assert resp.status_code == 409


def test_list_pens(client):
    client.post("/pens/", json={"name": "List-Pen-A", "capacity": 10})
    client.post("/pens/", json={"name": "List-Pen-B", "capacity": 20})
    resp = client.get("/pens/")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 2
    # PenOccupancy should have current_count
    assert "current_count" in data[0]


def test_get_pen(client):
    r = client.post("/pens/", json={"name": "Get-Pen", "capacity": 15})
    pen_id = r.json()["id"]
    resp = client.get(f"/pens/{pen_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Get-Pen"
    assert resp.json()["current_count"] == 0


def test_get_pen_not_found(client):
    resp = client.get("/pens/9999")
    assert resp.status_code == 404


def test_pen_occupancy(client):
    r = client.post("/pens/", json={"name": "Occ-Pen", "capacity": 30})
    pen_id = r.json()["id"]
    # Add two pigs to this pen
    client.post("/pigs/", json={"ear_tag": "OCC-001", "category": "finisher", "pen_id": pen_id})
    client.post("/pigs/", json={"ear_tag": "OCC-002", "category": "finisher", "pen_id": pen_id})
    resp = client.get(f"/pens/{pen_id}")
    assert resp.json()["current_count"] == 2


def test_update_pen(client):
    r = client.post("/pens/", json={"name": "Upd-Pen", "capacity": 10})
    pen_id = r.json()["id"]
    resp = client.patch(f"/pens/{pen_id}", json={"capacity": 40})
    assert resp.status_code == 200
    assert resp.json()["capacity"] == 40


def test_update_pen_not_found(client):
    resp = client.patch("/pens/9999", json={"capacity": 10})
    assert resp.status_code == 404
