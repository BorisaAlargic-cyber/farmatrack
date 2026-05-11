"""Tests for /farrowings endpoints."""

from datetime import date


def _create_sow(client, tag="SOW-200"):
    r = client.post("/pigs/", json={"ear_tag": tag, "category": "sow"})
    return r.json()["id"]


def test_create_farrowing(client):
    sow_id = _create_sow(client)
    resp = client.post("/farrowings/", json={
        "sow_id": sow_id,
        "farrowing_date": str(date.today()),
        "live_born": 12,
        "stillborn": 1,
        "mummified": 0,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["live_born"] == 12
    assert data["sow_id"] == sow_id


def test_farrowing_rejects_non_sow(client):
    r = client.post("/pigs/", json={"ear_tag": "FIN-200", "category": "finisher"})
    fin_id = r.json()["id"]
    resp = client.post("/farrowings/", json={
        "sow_id": fin_id,
        "farrowing_date": str(date.today()),
        "live_born": 5,
    })
    assert resp.status_code == 400


def test_list_farrowings_filter(client):
    sow1 = _create_sow(client, "SOW-301")
    sow2 = _create_sow(client, "SOW-302")
    client.post("/farrowings/", json={"sow_id": sow1, "farrowing_date": str(date.today()), "live_born": 10})
    client.post("/farrowings/", json={"sow_id": sow2, "farrowing_date": str(date.today()), "live_born": 8})

    resp = client.get("/farrowings/", params={"sow_id": sow1})
    data = resp.json()
    assert len(data) == 1
    assert data[0]["sow_id"] == sow1


def test_update_farrowing_weaning(client):
    sow_id = _create_sow(client, "SOW-400")
    r = client.post("/farrowings/", json={
        "sow_id": sow_id,
        "farrowing_date": str(date.today()),
        "live_born": 11,
    })
    far_id = r.json()["id"]
    resp = client.patch(f"/farrowings/{far_id}", json={
        "weaned_count": 9,
        "wean_date": str(date.today()),
    })
    assert resp.status_code == 200
    assert resp.json()["weaned_count"] == 9
