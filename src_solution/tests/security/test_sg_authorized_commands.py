"""Тесты, связанные с SG_ADS_Authorized_critical_commands."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import src_solution.abu.tcb.app as app_mod
from src_solution.abu.tcb.app import app
from src_solution.abu.tcb.safety import enforce_depth_cap, enforce_rpm_cap


@pytest.fixture(autouse=True)
def _reset_mission() -> None:
    app_mod._mission = None
    yield
    app_mod._mission = None


@pytest.mark.security
def test_depth_rpm_caps_enforced() -> None:
    """Критичные ограничения глубины и оборотов (ДВБ)."""
    assert enforce_depth_cap(10.0, 20.0) is True
    assert enforce_depth_cap(25.0, 20.0) is False
    assert enforce_rpm_cap(100.0, 200.0) is True


@pytest.mark.security
def test_mission_requires_post_not_get() -> None:
    """Команды миссии только через объявленный API."""
    c = TestClient(app)
    r = c.post("/api/v1/missions", json={"target_depth_m": 5.0, "max_rpm": 200.0})
    assert r.status_code == 200
