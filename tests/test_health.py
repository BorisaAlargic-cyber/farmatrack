"""Tests for /health endpoints."""

from datetime import date


def _create_pig(client, tag="PIG-900", category="piglet"):
    r = client.post("/pigs/", json={"ear_tag": tag, "category": category})
    return r.json()["id"]


def test_create_health_record(client):
    pid = _create_pig(client)
    resp = client.post("/health/", json={
        "pig_id": pid,
        "status": "sick",
        "diagnosis": "Respiratory infection",
        "treatment": "Antibiotics 5d",
        "vet_name": "Dr. Petrović",
        "record_date": str(date.today()),
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["pig_id"] == pid
    assert data["status"] == "sick"
    assert data["diagnosis"] == "Respiratory infection"


def test_create_health_record_pig_not_found(client):
    resp = client.post("/health/", json={
        "pig_id": 9999,
        "status": "healthy",
    })
    assert resp.status_code == 400


def test_list_health_records(client):
    pid = _create_pig(client, "PIG-901")
    client.post("/health/", json={"pig_id": pid, "status": "healthy"})
    client.post("/health/", json={"pig_id": pid, "status": "sick"})
    resp = client.get("/health/")
    assert resp.status_code == 200
    assert len(resp.json()) >= 2


def test_list_health_records_filter_by_pig(client):
    p1 = _create_pig(client, "PIG-902")
    p2 = _create_pig(client, "PIG-903")
    client.post("/health/", json={"pig_id": p1, "status": "healthy"})
    client.post("/health/", json={"pig_id": p2, "status": "sick"})
    resp = client.get("/health/", params={"pig_id": p1})
    data = resp.json()
    assert len(data) == 1
    assert data[0]["pig_id"] == p1


def test_get_health_record(client):
    pid = _create_pig(client, "PIG-904")
    r = client.post("/health/", json={"pig_id": pid, "status": "quarantined"})
    rec_id = r.json()["id"]
    resp = client.get(f"/health/{rec_id}")
    assert resp.status_code == 200
    assert resp.json()["status"] == "quarantined"


def test_get_health_record_not_found(client):
    resp = client.get("/health/9999")
    assert resp.status_code == 404


def test_update_health_record(client):
    pid = _create_pig(client, "PIG-905")
    r = client.post("/health/", json={"pig_id": pid, "status": "sick"})
    rec_id = r.json()["id"]
    resp = client.patch(f"/health/{rec_id}", json={
        "status": "treated",
        "treatment": "Anti-inflammatory",
    })
    assert resp.status_code == 200
    assert resp.json()["status"] == "treated"
    assert resp.json()["treatment"] == "Anti-inflammatory"


def test_update_health_record_not_found(client):
    resp = client.patch("/health/9999", json={"status": "healthy"})
    assert resp.status_code == 404


def test_delete_health_record(client):
    pid = _create_pig(client, "PIG-906")
    r = client.post("/health/", json={"pig_id": pid, "status": "sick"})
    rec_id = r.json()["id"]
    resp = client.delete(f"/health/{rec_id}")
    assert resp.status_code == 204
    # Verify gone
    resp = client.get(f"/health/{rec_id}")
    assert resp.status_code == 404


def test_delete_health_record_not_found(client):
    resp = client.delete("/health/9999")
    assert resp.status_code == 404
