"""Модульные и API-тесты ДВБ решения (src_solution.abu.tcb) для покрытия и C16."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

import src_solution.abu.tcb.app as app_mod
from src_solution.abu.tcb.app import app
from src_solution.abu.tcb.event_log import EventLevel, EventLog
from src_solution.abu.tcb.safety import (
    enforce_depth_cap,
    enforce_rpm_cap,
    should_emergency_stop,
)


@pytest.fixture(autouse=True)
def _reset_mission() -> None:
    """Изолировать тесты API: одна активная миссия в модуле app."""
    app_mod._mission = None
    yield
    app_mod._mission = None


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


# --- safety.py ---


def test_safety_caps_and_emergency_branches() -> None:
    """Все ветки enforce_* и should_emergency_stop."""
    assert enforce_depth_cap(5.0, 10.0) is True
    assert enforce_depth_cap(11.0, 10.0) is False
    assert enforce_rpm_cap(100.0, 200.0) is True
    assert enforce_rpm_cap(250.0, 200.0) is False
    assert should_emergency_stop("high", 0.0) is True
    assert should_emergency_stop("low", 0.95, vib_threshold=0.9) is True
    assert should_emergency_stop("medium", 0.1) is False
    assert should_emergency_stop("low", 0.1, vib_threshold=0.9) is False


# --- event_log.py ---


def test_event_log_empty_full_tail(tmp_path) -> None:
    """Полный журнал до первой записи — пустая строка."""
    log = EventLog(tmp_path)
    assert log.read_full_tail() == ""


def test_event_log_levels_and_ring_file(tmp_path) -> None:
    """Уровни событий, кольцо и файл снимка кольца."""
    log = EventLog(tmp_path)
    for level in EventLevel:
        log.record(level, f"msg-{level.value}")
    snap = log.ring_snapshot()
    assert len(snap) == len(EventLevel)
    ring_text = (tmp_path / "abu_events_ring.txt").read_text(encoding="utf-8")
    assert "CRITICAL" in ring_text
    tail = log.read_full_tail(max_lines=2)
    assert "CRITICAL" in tail


# --- app.py API ---


def test_status_idle(client: TestClient) -> None:
    r = client.get("/api/v1/status")
    assert r.status_code == 200
    assert r.json()["idle"] is True


def test_current_mission_not_found(client: TestClient) -> None:
    r = client.get("/api/v1/missions/current")
    assert r.status_code == 404


def test_events_full_tail(client: TestClient) -> None:
    client.get("/api/v1/health")
    r = client.get("/api/v1/events/full")
    assert r.status_code == 200
    assert "log" in r.json()


def test_current_mission_after_start(client: TestClient) -> None:
    client.post("/api/v1/missions", json={"target_depth_m": 2.0, "max_rpm": 180.0})
    r = client.get("/api/v1/missions/current")
    assert r.status_code == 200
    assert r.json()["target_depth_m"] == 2.0


def test_status_with_active_mission(client: TestClient) -> None:
    client.post("/api/v1/missions", json={"target_depth_m": 3.0})
    client.post("/api/v1/missions/tick")
    st = client.get("/api/v1/status")
    body = st.json()
    assert body["idle"] is False
    assert "vibration_score" in body
    assert body["mission_status"] in ("running", "completed", "stopped_depth", "stopped_rpm", "emergency")


def test_ai_suggest_endpoint(client: TestClient) -> None:
    r = client.post(
        "/api/v1/ai/suggest",
        json={"depth_m": 8.0, "torque_nm": 2500.0},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["suggested_rpm"] > 0
    assert data["suggested_feed_mm_rev"] > 0


def test_tick_without_mission(client: TestClient) -> None:
    r = client.post("/api/v1/missions/tick")
    assert r.status_code == 400


def test_tick_after_completion_returns_done(client: TestClient) -> None:
    client.post("/api/v1/missions", json={"target_depth_m": 0.5, "max_rpm": 120.0})
    for _ in range(10):
        t = client.post("/api/v1/missions/tick")
        if t.json().get("mission", {}).get("status") == "completed":
            break
    again = client.post("/api/v1/missions/tick")
    assert again.json()["done"] is True
    assert again.json()["status"] == "completed"


def test_invalid_abu_max_rpm_uses_default_cap(client: TestClient) -> None:
    os.environ["ABU_MAX_RPM"] = "not-a-number"
    try:
        client.post("/api/v1/missions", json={"target_depth_m": 2.0})
        t = client.post("/api/v1/missions/tick")
        assert t.status_code == 200
        assert t.json()["mission"]["rpm"] <= 300.0
    finally:
        os.environ.pop("ABU_MAX_RPM", None)


def test_mission_stopped_depth_cap(client: TestClient) -> None:
    client.post("/api/v1/missions", json={"target_depth_m": 5.0})
    with patch("src_solution.abu.tcb.app.enforce_depth_cap", return_value=False):
        t = client.post("/api/v1/missions/tick")
    assert t.json()["mission"]["status"] == "stopped_depth"


def test_mission_stopped_rpm_cap(client: TestClient) -> None:
    client.post("/api/v1/missions", json={"target_depth_m": 5.0})
    with patch("src_solution.abu.tcb.app.enforce_rpm_cap", return_value=False):
        t = client.post("/api/v1/missions/tick")
    assert t.json()["mission"]["status"] == "stopped_rpm"


def test_mission_emergency_stop(client: TestClient) -> None:
    client.post("/api/v1/missions", json={"target_depth_m": 10.0})
    with patch("src_solution.abu.tcb.app.risk_flag", return_value="high"):
        t = client.post("/api/v1/missions/tick")
    assert t.json()["mission"]["status"] == "emergency"
    assert t.json()["risk"] == "high"


def test_mission_high_risk_warning_logged(client: TestClient) -> None:
    client.post("/api/v1/missions", json={"target_depth_m": 4.0})
    with patch("src_solution.abu.tcb.app.risk_flag", return_value="high"):
        client.post("/api/v1/missions/tick")
    ring = client.get("/api/v1/events/ring").json()["lines"]
    assert any("risk_high" in line for line in ring)
