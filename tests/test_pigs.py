"""Tests for /pigs endpoints."""


def test_create_and_list_pig(client):
    resp = client.post("/pigs/", json={
        "ear_tag": "SOW-100",
        "category": "sow",
        "breed": "Large White",
        "weight_kg": 200.0,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["ear_tag"] == "SOW-100"
    assert data["category"] == "sow"
    assert data["is_active"] is True

    # List
    resp = client.get("/pigs/")
    assert resp.status_code == 200
    pigs = resp.json()
    assert len(pigs) >= 1
    assert any(p["ear_tag"] == "SOW-100" for p in pigs)


def test_duplicate_ear_tag_rejected(client):
    client.post("/pigs/", json={"ear_tag": "DUP-001", "category": "piglet"})
    resp = client.post("/pigs/", json={"ear_tag": "DUP-001", "category": "piglet"})
    assert resp.status_code == 409


def test_get_pig_not_found(client):
    resp = client.get("/pigs/9999")
    assert resp.status_code == 404


def test_update_pig(client):
    r = client.post("/pigs/", json={"ear_tag": "FIN-050", "category": "finisher", "weight_kg": 80})
    pid = r.json()["id"]
    resp = client.patch(f"/pigs/{pid}", json={"weight_kg": 95.5})
    assert resp.status_code == 200
    assert resp.json()["weight_kg"] == 95.5


def test_deactivate_pig(client):
    r = client.post("/pigs/", json={"ear_tag": "GLT-050", "category": "gilt"})
    pid = r.json()["id"]
    resp = client.delete(f"/pigs/{pid}")
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_filter_by_category(client):
    client.post("/pigs/", json={"ear_tag": "PIG-A01", "category": "piglet"})
    client.post("/pigs/", json={"ear_tag": "SOW-A01", "category": "sow"})
    resp = client.get("/pigs/", params={"category": "piglet"})
    tags = [p["ear_tag"] for p in resp.json()]
    assert "PIG-A01" in tags
    assert "SOW-A01" not in tags
