"""Tests for /scan endpoints and tag parsing."""

from services.scan_service import parse_tag


# ── parse_tag unit tests ──────────────────────────────────


def test_parse_sow_tag():
    """SOW prefix must be preserved — O→0 only in digits."""
    tag, conf = parse_tag("SOW-001")
    assert tag == "SOW-001"
    assert conf == 0.90


def test_parse_glt_tag():
    tag, conf = parse_tag("GLT-004")
    assert tag == "GLT-004"
    assert conf == 0.90


def test_parse_fin_tag():
    tag, conf = parse_tag("  fin-003  ")
    assert tag == "FIN-003"
    assert conf == 0.90


def test_parse_pig_tag():
    tag, conf = parse_tag("PIG-012")
    assert tag == "PIG-012"
    assert conf == 0.90


def test_parse_ocr_letter_o_in_digits():
    """OCR might read 0 as O in the numeric part — should correct."""
    tag, conf = parse_tag("FIN-O12")
    assert tag == "FIN-012"
    assert conf >= 0.80


def test_parse_tag_with_spaces():
    tag, conf = parse_tag("  SOW - 007  ")
    assert tag == "SOW-007"
    assert conf == 0.90


def test_parse_tag_garbage():
    tag, conf = parse_tag("????")
    assert conf < 0.5


def test_parse_tag_empty():
    tag, conf = parse_tag("   ")
    assert tag is None or tag == ""
    assert conf < 0.5


# ── API endpoint tests ────────────────────────────────────


def test_scan_endpoint_match(client):
    client.post("/pigs/", json={"ear_tag": "FIN-010", "category": "finisher"})
    resp = client.post("/scan/", json={"raw_text": "FIN-010", "source": "ear_tag"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["pig_id"] is not None
    assert data["ear_tag"] == "FIN-010"


def test_scan_endpoint_sow_match(client):
    """SOW tag scan should match — regression test for O→0 bug."""
    client.post("/pigs/", json={"ear_tag": "SOW-001", "category": "sow"})
    resp = client.post("/scan/", json={"raw_text": "SOW-001", "source": "ear_tag"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["pig_id"] is not None
    assert data["ear_tag"] == "SOW-001"


def test_scan_endpoint_no_match(client):
    resp = client.post("/scan/", json={"raw_text": "XXX-999", "source": "manual"})
    assert resp.status_code == 200
    assert resp.json()["pig_id"] is None


def test_scan_logs(client):
    client.post("/scan/", json={"raw_text": "SOW-001", "source": "ear_tag"})
    resp = client.get("/scan/logs")
    assert resp.status_code == 200
    assert len(resp.json()) >= 1
