# Purpose: tests for readiness/score.py (weighted scoring and gap ranking).
# Book: National AI Strategy in Practice, Chapter 2
# Licence: MIT (see LICENSE)
import pytest
import score

TINY = {
    "pillars": [
        {"id": "a", "name": "A", "weight": 0.6, "indicators": [
            {"id": "I1", "name": "One", "weight": 1, "levels": {0: "", 1: "", 4: ""}},
            {"id": "I2", "name": "Two", "weight": 3, "levels": {0: "", 1: "next"}},
        ]},
        {"id": "b", "name": "B", "weight": 0.4, "indicators": [
            {"id": "I3", "name": "Three", "weight": 1, "levels": {2: "", 3: "up"}},
        ]},
    ]
}


def assessment(i1=4, i2=0, i3=2):
    return {"scores": {"I1": {"score": i1, "evidence": "x"},
                       "I2": {"score": i2, "evidence": ""},
                       "I3": {"score": i3, "evidence": "y"}}}


def test_hand_computed_scores():
    r = score.score_assessment(TINY, assessment())
    assert r["pillars"][0]["score"] == pytest.approx(1.0)   # (1*4 + 3*0) / 4
    assert r["pillars"][1]["score"] == pytest.approx(2.0)
    assert r["overall"] == pytest.approx(1.4)               # 0.6*1 + 0.4*2


def test_gap_ranking_by_weight_times_gap():
    gaps = score.score_assessment(TINY, assessment())["gaps"]
    assert [g["id"] for g in gaps] == ["I2", "I3", "I1"]
    assert gaps[0]["priority"] == pytest.approx(0.6 * 0.75 * 4)
    assert gaps[0]["next_level"] == "next"


def test_rejects_bad_scores_and_missing_indicators():
    with pytest.raises(ValueError):
        score.score_assessment(TINY, assessment(i1=5))
    bad = assessment()
    del bad["scores"]["I3"]
    with pytest.raises(ValueError):
        score.score_assessment(TINY, bad)


def test_flags_scores_without_evidence():
    r = score.score_assessment(TINY, assessment(i2=2))
    assert r["missing_evidence"] == ["I2"]


def test_real_scorecard_is_complete_and_example_scores():
    card = score.load_yaml(score.DEFAULT_SCORECARD)
    assert len(card["pillars"]) == 6
    for pillar in card["pillars"]:
        assert 4 <= len(pillar["indicators"]) <= 6
        for ind in pillar["indicators"]:
            assert sorted(ind["levels"]) == [0, 1, 2, 3, 4]
            assert ind["evidence"] and ind["weight"] > 0
    example = score.load_yaml(score.HERE / "example-assessment.yaml")
    result = score.score_assessment(card, example)
    assert 0 <= result["overall"] <= 4
    assert "| Pillar |" in score.render(result, "Example Republic")
