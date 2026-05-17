"""Интеграционные тесты решения (импорт src_solution + event_log для критериев C12/C15/C16)."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

import src_solution.abu.tcb.app as app_mod
from src_solution.abu.tcb import event_log
from src_solution.abu.tcb.app import app


@pytest.fixture(autouse=True)
def _reset_solution_mission() -> None:
    app_mod._mission = None
    yield
    app_mod._mission = None


@pytest.fixture()
def solution_client() -> TestClient:
    return TestClient(app)


def test_solution_health(solution_client: TestClient) -> None:
    r = solution_client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_solution_mission_and_log(solution_client: TestClient) -> None:
    """Миссия, tick и журнал event_log."""
    assert event_log.default_log is not None
    solution_client.post("/api/v1/missions", json={"target_depth_m": 1.5, "max_rpm": 200.0})
    solution_client.post("/api/v1/missions/tick")
    ring = solution_client.get("/api/v1/events/ring")
    assert ring.status_code == 200
    assert isinstance(ring.json().get("lines"), list)


def test_solution_rpm_cap(solution_client: TestClient) -> None:
    os.environ["ABU_MAX_RPM"] = "90"
    try:
        solution_client.post("/api/v1/missions", json={"target_depth_m": 3.0})
        t = solution_client.post("/api/v1/missions/tick")
        assert t.json()["mission"]["rpm"] <= 90
    finally:
        os.environ.pop("ABU_MAX_RPM", None)


def test_solution_mission_completes(solution_client: TestClient) -> None:
    """Миссия завершается по достижению глубины."""
    solution_client.post("/api/v1/missions", json={"target_depth_m": 1.0, "max_rpm": 150.0})
    status = "running"
    for _ in range(15):
        t = solution_client.post("/api/v1/missions/tick")
        status = t.json()["mission"]["status"]
        if status == "completed":
            break
    assert status == "completed"


def test_solution_events_full(solution_client: TestClient) -> None:
    solution_client.get("/api/v1/health")
    r = solution_client.get("/api/v1/events/full")
    assert r.status_code == 200
    assert isinstance(r.json()["log"], str)
