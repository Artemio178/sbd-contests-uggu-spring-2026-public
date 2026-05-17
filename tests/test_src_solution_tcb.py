"""Покрытие и импорт ДВБ решения (src_solution.abu.tcb)."""

from __future__ import annotations

from src_solution.abu.tcb.event_log import EventLevel, EventLog
from src_solution.abu.tcb.placeholder import tcb_health
from src_solution.abu.tcb.safety import enforce_depth_cap, enforce_rpm_cap


def test_tcb_health() -> None:
    assert tcb_health() == "ok"


def test_tcb_safety_helpers() -> None:
    """Прямой вызов проверок ДВБ."""
    assert enforce_depth_cap(1.0, 2.0)
    assert enforce_rpm_cap(50.0, 100.0)
    assert not enforce_depth_cap(3.0, 2.0)


def test_tcb_event_log_module(tmp_path) -> None:
    """Журнал событий ДВБ: запись и снимок кольца."""
    log = EventLog(tmp_path)
    log.record(EventLevel.WARNING, "tcb-test")
    assert any("tcb-test" in line for line in log.ring_snapshot())
