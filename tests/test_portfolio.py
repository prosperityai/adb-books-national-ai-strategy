# Purpose: tests for portfolio/score_portfolio.py (scores, quadrants, waves).
# Book: National AI Strategy in Practice, Chapter 3
# Licence: MIT (see LICENSE)
import pytest
import score_portfolio as sp


def uc(id_, value, feas, data, risk, months=6, cost=100):
    return {"id": id_, "use_case": id_, "value": value, "feasibility": feas,
            "data_readiness": data, "risk": risk, "months": months, "cost_usd": cost}


def test_weighted_score_bounds_and_risk_flip():
    assert sp.weighted_score(uc("a", 5, 5, 5, 1)) == pytest.approx(100)
    assert sp.weighted_score(uc("b", 1, 1, 1, 5)) == pytest.approx(20)
    # value 4, feas 3, data 2, risk 4 -> 20*(.35*4+.25*3+.25*2+.15*2) = 59
    assert sp.weighted_score(uc("c", 4, 3, 2, 4)) == pytest.approx(59)


def test_quadrants():
    assert sp.quadrant(uc("f", 5, 4, 4, 2)) == "Flagship"
    assert sp.quadrant(uc("q", 3, 4, 4, 2)) == "Quick win"
    assert sp.quadrant(uc("l", 5, 2, 2, 4)) == "Long bet"
    assert sp.quadrant(uc("d", 2, 2, 2, 5)) == "Drop"


def test_waves_respect_rules_and_capacity():
    cases = [uc(f"f{i}", 5, 4, 4, 2, months=6) for i in range(3)]
    cases += [uc("long_flagship", 5, 4, 4, 2, months=18), uc("bet", 5, 1, 1, 5),
              uc("drop", 1, 1, 1, 5)]
    ranked = {u["id"]: u for u in sp.score_portfolio(cases, per_wave=2)}
    assert ranked["drop"]["wave"] is None
    assert ranked["bet"]["wave"] == 3
    wave1 = [u for u in ranked.values() if u["wave"] == 1]
    assert len(wave1) == 2                       # capacity limit
    assert ranked["long_flagship"]["wave"] >= 2  # longer than 12 months


def test_example_csv_loads():
    rows = sp.read_use_cases(sp.__file__.replace("score_portfolio.py", "use_cases.example.csv"))
    assert 12 <= len(rows) <= 15
    assert "## Delivery waves" in sp.render(sp.score_portfolio(rows))
