"""Тесты проверок безопасности (ДВБ)."""

from __future__ import annotations

from src_solution.abu.tcb.safety import (
    enforce_depth_cap,
    enforce_rpm_cap,
    should_emergency_stop,
)


def test_depth_cap() -> None:
    """Лимит глубины."""
    assert enforce_depth_cap(10.0, 20.0) is True
    assert enforce_depth_cap(21.0, 20.0) is False


def test_rpm_cap() -> None:
    """Лимит оборотов."""
    assert enforce_rpm_cap(100.0, 200.0) is True
    assert enforce_rpm_cap(300.0, 200.0) is False


def test_emergency_high_risk() -> None:
    """Высокий риск — стоп."""
    assert should_emergency_stop("high", 0.0) is True


def test_emergency_vibration_score() -> None:
    """Высокая оценка вибрации — стоп."""
    assert should_emergency_stop("low", 0.95, vib_threshold=0.9) is True
