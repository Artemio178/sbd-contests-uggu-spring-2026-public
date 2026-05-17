# Отчёт оценки решения (прозрачный артефакт)

Текстовый отчёт о решении по критерию **C17:** [solution.md](solution.md).

**Расшифровка уровней 0–3:** [criteria_rubric.md](criteria_rubric.md).

**Участник / команда:** _указать_  
**Коммит / тег:** _указать_  
**Дата прогона:** 2026-05-17

> Баллы ниже — оценка по структуре репозитория и `scripts/evaluate_contest_score.py`.  
> Перед сдачей выполните `make tests-all` и `make evaluate-score` и при необходимости скорректируйте таблицу.

## 1. Автоматические проверки

| Проверка | Результат | Примечание |
|----------|-----------|------------|
| `make tests-all` (pytest) | OK* | `src_starting_point/tests`, `src_solution/tests`, `tests` |
| Покрытие общее (регулятор/АБУ) | — | поле `coverage_percent` после `make certify-abu` |
| Покрытие тестами безопасности | — | `security_coverage_percent` ≥ 70 (по умолчанию) |
| Сертификация (`make certify-abu` или API) | — | `certificate_id` = SHA-256 архива |

\* Ожидается при успешном прогоне в среде Pipenv (Linux / WSL2).

## 2. Лог сертификации (фрагмент)

```
# После: bash scripts/prepare_certification_bundle_solution.sh && make certify-abu
Результат сертификации: успешно
Стоимость (усл. ед.): <estimated_cost>
Сертификат (SHA-256 пакета): <64 hex>
security_coverage_percent: <≥ 70>
```

## 3. Баллы по 22 критериям (макс. 3 за критерий)

Источник имён: `make evaluate-score` (`scripts/evaluate_contest_score.py`).

| № | Критерий | Баллы (0–3) |
|---|----------|-------------|
| 1 | C01: Все тесты репозитория (включая тесты решения) завершаются успешно | 3.0 |
| 2 | C02: Наличие тестов безопасности (tests/security/ или src_starting_point/tests/security/) | 3.0 |
| 3 | C03: Маркер security в pytest.ini и использование в тестах | 3.0 |
| 4 | C04: Покрытие тестами event_log / журнал | 1.0 |
| 5 | C05: Пример sga.json | 3.0 |
| 6 | C06: SBOM TCB / OTHER в примерах | 3.0 |
| 7 | C07: Скрипт prepare_certification_bundle.sh | 3.0 |
| 8 | C08: Сквозной автотест ЦР–АБУ (`tests/test_e2e_abu_dm_scenario.py`) | 3.0 |
| 9 | C09: Оформление кода в src_solution (flake8, PEP8) | 3.0 |
| 10 | C10: Решение: event_log в src_solution | 3.0 |
| 11 | C11: Решение: зависимости в src_solution (непустой манифест для высоких уровней) | 3.0 |
| 12 | C12: Тесты репозитория импортируют src_solution (AST) | 3.0 |
| 13 | C13: docs/security_tests.md привязан к решению (src_solution) | 3.0 |
| 14 | C14: numpy в SBOM решения (SBOM_TCB vs SBOM_OTHER) | 3.0 |
| 15 | C15: Тесты: event_log и src_solution (импорты) | 3.0 |
| 16 | C16: Покрытие src_solution/abu/tcb тестами | 3.0 |
| 17 | C17: Отчёт docs/solution.md | 3.0 |
| 18 | C18: security_monitor, policies в src_solution; тесты политик | 1.0 |
| 19 | C19: изоляция доменов; монитор запросов/ответов | 0.0 |
| 20 | C20: Стоимость сертификации — место в рейтинге (жюри: 3/2/1/0) | 0.0 |
| 21 | C21: Экспертно — соответствие политик архитектуре АБУ (жюри) | 0.0 |
| 22 | C22: Экспертно — полнота отчёта и воспроизводимость (жюри) | 0.0 |

**Итого (сумма):** 52.0 / 66  

**Итоговая шкала 10–20 (нормализация `10 + (raw/66)×10`):** **17.88**

*Пояснения к автоматической части:*  
- **C04:** в `src_starting_point/tests/test_event_log.py` одна тестовая функция (по скрипту — 1 балл).  
- **C12/C15:** три файла в `tests/` с импортом `src_solution` и `event_log`.  
- **C14:** numpy только в `src_solution/sbom/SBOM_OTHER.cdx.json`.  
- **C16:** при покрытии ДВБ ≥ 80% (тесты в `tests/test_src_solution_tcb_*.py`).  
- **C18:** декларация `ipc_policies.json`, без отдельного `security_monitor`.  
- **C20–C22:** заполняет жюри.

## 4. Tie-break (при равенстве итога)

1. Больший балл за автоматическую часть  
2. Учёт C20–C22  
3. Более ранняя успешная сдача  
4. Меньше предупреждений в отчёте сертификации  
5. Решение жюри  

См. [contest_regulations.md](contest_regulations.md).

## 5. Апелляция

Срок и контакт: по объявлению жюри соревнований.
