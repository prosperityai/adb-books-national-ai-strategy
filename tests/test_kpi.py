# Purpose: tests for kpi/report.py (RAG logic).
# Book: National AI Strategy in Practice, Chapter 12
# Licence: MIT (see LICENSE)
import datetime as dt

import report

UP = {"baseline": 0, "target": 100, "direction": "up"}
DOWN = {"baseline": 50, "target": 10, "direction": "down"}


def test_rag_up_kpi_at_half_time():
    assert report.rag_status(UP, 45, 0.5)[0] == "GREEN"   # 90% of expected
    assert report.rag_status(UP, 30, 0.5)[0] == "AMBER"   # 60%
    assert report.rag_status(UP, 29, 0.5)[0] == "RED"
    assert report.rag_status(UP, 100, 0.1)[0] == "GREEN"  # target met early


def test_rag_down_kpi_and_wrong_direction():
    status, progress = report.rag_status(DOWN, 30, 0.5)   # fell 20 of 40
    assert status == "GREEN" and progress == 0.5
    assert report.rag_status(DOWN, 55, 0.5)[0] == "RED"   # moving the wrong way
    assert report.rag_status(DOWN, 8, 0.5)[0] == "GREEN"


def test_missing_value_is_no_data():
    assert report.rag_status(UP, None, 0.5) == ("NO DATA", None)


def test_elapsed_fraction():
    start, end = dt.date(2026, 7, 1), dt.date(2031, 6, 30)
    assert report.elapsed_fraction(start, end, dt.date(2028, 6, 30)) == 0.4
    assert report.elapsed_fraction(start, end, dt.date(2020, 1, 1)) == 0.0


def test_example_framework():
    framework = report.load_yaml(report.DEFAULT_FRAMEWORK)
    assert 14 <= len(framework["kpis"]) <= 18
    assert {k["level"] for k in framework["kpis"]} == set(report.LEVELS)
    for k in framework["kpis"]:
        for field in ("baseline", "target", "data_source", "frequency", "owner"):
            assert k[field] is not None
    values = report.load_yaml(report.HERE / "example-values.yaml")
    rows, elapsed = report.build_report(framework, values)
    assert elapsed == 0.4
    assert {r["status"] for r in rows} <= {"GREEN", "AMBER", "RED", "NO DATA"}
