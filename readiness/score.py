# Purpose: score a filled readiness assessment against the six-pillar scorecard and
#          print pillar scores, the overall score and a ranked gap list as Markdown.
# Book: National AI Strategy in Practice, Chapter 2
# Licence: MIT (see LICENSE)
"""Readiness scorer.

Run:
    python3 readiness/score.py readiness/example-assessment.yaml

How the maths works (all scores are on the 0-4 scale):
    pillar score  = sum(indicator weight x score) / sum(indicator weights)
    overall score = sum(pillar weight x pillar score)        (pillar weights add to 1)
    gap           = 4 - score
    priority      = effective weight x gap
    effective weight = pillar weight x (indicator weight / sum of indicator weights in pillar)

The gap list is sorted by priority, so the top rows are the gaps that cost the
country most points: big gaps on heavily weighted indicators.
"""

import argparse
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
DEFAULT_SCORECARD = HERE / "scorecard.yaml"
MAX_SCORE = 4


def load_yaml(path):
    """Read a YAML file and return its contents."""
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def score_assessment(scorecard, assessment):
    """Return a dictionary with pillar results, overall score and gap list.

    Raises ValueError if an indicator is missing or a score is not an integer 0-4,
    because a partial assessment would give a misleading total.
    """
    scores = assessment.get("scores", {})
    total_pillar_weight = sum(p["weight"] for p in scorecard["pillars"])
    if abs(total_pillar_weight - 1.0) > 1e-6:
        raise ValueError(f"Pillar weights must add up to 1.0 (they add to {total_pillar_weight})")

    pillars, gaps, missing_evidence = [], [], []
    for pillar in scorecard["pillars"]:
        weight_sum = sum(ind["weight"] for ind in pillar["indicators"])
        weighted = 0.0
        for ind in pillar["indicators"]:
            entry = scores.get(ind["id"])
            if entry is None:
                raise ValueError(f"No score for indicator {ind['id']} ({ind['name']})")
            value = entry["score"]
            if not isinstance(value, int) or not 0 <= value <= MAX_SCORE:
                raise ValueError(f"Score for {ind['id']} must be a whole number 0-4, got {value}")
            if value > 0 and not str(entry.get("evidence") or "").strip():
                missing_evidence.append(ind["id"])
            weighted += ind["weight"] * value
            effective_weight = pillar["weight"] * ind["weight"] / weight_sum
            gap = MAX_SCORE - value
            gaps.append(
                {
                    "id": ind["id"],
                    "name": ind["name"],
                    "pillar": pillar["name"],
                    "score": value,
                    "gap": gap,
                    "effective_weight": effective_weight,
                    "priority": effective_weight * gap,
                    # The next level up is the concrete target for the action plan.
                    "next_level": ind["levels"].get(value + 1, "Already at top level"),
                }
            )
        pillar_score = weighted / weight_sum
        pillars.append(
            {"id": pillar["id"], "name": pillar["name"], "weight": pillar["weight"],
             "score": pillar_score}
        )

    overall = sum(p["weight"] * p["score"] for p in pillars)
    gaps.sort(key=lambda g: (-g["priority"], g["id"]))
    return {"pillars": pillars, "overall": overall, "gaps": gaps,
            "missing_evidence": missing_evidence}


def md_table(headers, rows):
    """Format rows as a Markdown pipe table (prints cleanly in the book)."""
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def render(result, country, top=10):
    """Return the full Markdown report as a string."""
    out = [f"## Readiness scores: {country}", ""]
    rows = [
        [p["name"], f"{p['weight']:.2f}", f"{p['score']:.2f}", f"{p['score'] / MAX_SCORE:.0%}"]
        for p in result["pillars"]
    ]
    rows.append(["**Overall (weighted)**", "1.00", f"**{result['overall']:.2f}**",
                 f"**{result['overall'] / MAX_SCORE:.0%}**"])
    out.append(md_table(["Pillar", "Weight", "Score (0-4)", "% of max"], rows))
    out += ["", f"## Top {top} gaps, ranked by weight x gap", ""]
    gap_rows = [
        [i, g["id"], g["name"], g["score"], g["gap"], f"{g['priority']:.3f}", g["next_level"]]
        for i, g in enumerate(result["gaps"][:top], start=1)
    ]
    out.append(md_table(["Rank", "ID", "Indicator", "Score", "Gap", "Priority", "Next level"],
                        gap_rows))
    if result["missing_evidence"]:
        out += ["", "Scored without evidence (re-check before publishing): "
                + ", ".join(result["missing_evidence"])]
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Score a national AI readiness assessment.")
    parser.add_argument("assessment", help="Filled assessment YAML file")
    parser.add_argument("--scorecard", default=DEFAULT_SCORECARD, help="Scorecard YAML file")
    parser.add_argument("--top", type=int, default=10, help="Number of gaps to list")
    args = parser.parse_args()

    assessment = load_yaml(args.assessment)
    result = score_assessment(load_yaml(args.scorecard), assessment)
    print(render(result, assessment.get("country", "Unnamed"), top=args.top))


if __name__ == "__main__":
    main()
