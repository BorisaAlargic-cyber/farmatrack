"""HTTP client wrapper — all Streamlit pages call the FastAPI backend through here."""

import requests
from typing import Any, Optional
from config import get_settings

BASE = get_settings().API_BASE_URL


def _url(path: str) -> str:
    return f"{BASE}{path}"


def _handle(resp: requests.Response) -> Any:
    if resp.status_code >= 400:
        detail = resp.json().get("detail", resp.text) if resp.headers.get("content-type", "").startswith("application/json") else resp.text
        raise RuntimeError(f"API error {resp.status_code}: {detail}")
    if resp.status_code == 204:
        return None
    return resp.json()


# ── Dashboard ──────────────────────────────────────────────
def get_summary() -> dict:
    return _handle(requests.get(_url("/dashboard/summary")))


# ── Pigs ───────────────────────────────────────────────────
def list_pigs(category: Optional[str] = None, pen_id: Optional[int] = None, active_only: bool = True) -> list[dict]:
    params: dict = {"active_only": active_only}
    if category:
        params["category"] = category
    if pen_id is not None:
        params["pen_id"] = pen_id
    return _handle(requests.get(_url("/pigs/"), params=params))


def get_pig(pig_id: int) -> dict:
    return _handle(requests.get(_url(f"/pigs/{pig_id}")))


def create_pig(data: dict) -> dict:
    return _handle(requests.post(_url("/pigs/"), json=data))


def update_pig(pig_id: int, data: dict) -> dict:
    return _handle(requests.patch(_url(f"/pigs/{pig_id}"), json=data))


def deactivate_pig(pig_id: int) -> dict:
    return _handle(requests.delete(_url(f"/pigs/{pig_id}")))


# ── Pens ───────────────────────────────────────────────────
def list_pens() -> list[dict]:
    return _handle(requests.get(_url("/pens/")))


def create_pen(data: dict) -> dict:
    return _handle(requests.post(_url("/pens/"), json=data))


def update_pen(pen_id: int, data: dict) -> dict:
    return _handle(requests.patch(_url(f"/pens/{pen_id}"), json=data))


# ── Health ─────────────────────────────────────────────────
def list_health_records(pig_id: Optional[int] = None) -> list[dict]:
    params = {}
    if pig_id is not None:
        params["pig_id"] = pig_id
    return _handle(requests.get(_url("/health/"), params=params))


def create_health_record(data: dict) -> dict:
    return _handle(requests.post(_url("/health/"), json=data))


def update_health_record(record_id: int, data: dict) -> dict:
    return _handle(requests.patch(_url(f"/health/{record_id}"), json=data))


def delete_health_record(record_id: int):
    return _handle(requests.delete(_url(f"/health/{record_id}")))


# ── Farrowings ─────────────────────────────────────────────
def list_farrowings(sow_id: Optional[int] = None) -> list[dict]:
    params = {}
    if sow_id is not None:
        params["sow_id"] = sow_id
    return _handle(requests.get(_url("/farrowings/"), params=params))


def create_farrowing(data: dict) -> dict:
    return _handle(requests.post(_url("/farrowings/"), json=data))


def update_farrowing(farrowing_id: int, data: dict) -> dict:
    return _handle(requests.patch(_url(f"/farrowings/{farrowing_id}"), json=data))


# ── Scan ───────────────────────────────────────────────────
def scan_text(raw_text: str, source: str = "ear_tag") -> dict:
    return _handle(requests.post(_url("/scan/"), json={"raw_text": raw_text, "source": source}))


def scan_image(file_bytes: bytes, filename: str) -> dict:
    files = {"file": (filename, file_bytes)}
    return _handle(requests.post(_url("/scan/image"), files=files))


def list_scan_logs() -> list[dict]:
    return _handle(requests.get(_url("/scan/logs")))
