"""Проверки безопасности (ДВБ); решения принимаются только по данным из недоверенной зоны."""

from __future__ import annotations

from typing import Literal

RiskLevel = Literal["low", "medium", "high"]


def enforce_depth_cap(depth_m: float, max_depth_m: float) -> bool:
    """
    Проверка верхнего предела глубины.

    :param depth_m: текущая глубина
    :param max_depth_m: допустимый максимум
    :returns: True если можно продолжать
    """
    return depth_m <= max_depth_m


def enforce_rpm_cap(rpm: float, max_rpm: float) -> bool:
    """Проверка верхнего предела оборотов."""
    return rpm <= max_rpm


def should_emergency_stop(
    risk: RiskLevel,
    vibration_score: float = 0.0,
    vib_threshold: float = 0.9,
) -> bool:
    """
    Аварийный стоп по уровню риска или оценке вибрации (уже вычисленной в other).

    :param risk: уровень риска
    :param vibration_score: нормированная аномалия вибрации [0, 1]
    :param vib_threshold: порог аномалии
    :returns: True если нужна остановка
    """
    if risk == "high":
        return True
    if vibration_score >= vib_threshold:
        return True
    return False
