# Purpose: score a long-list of AI use cases, place each in a quadrant (quick win,
#          flagship, long bet, drop) and sequence them into delivery waves.
# Book: National AI Strategy in Practice, Chapter 3
# Licence: MIT (see LICENSE)
"""Use-case portfolio scorer.

Run:
    python3 portfolio/score_portfolio.py portfolio/use_cases.example.csv

Inputs (CSV, lines starting with # are ignored): value, feasibility, data_readiness
and risk are scored 1-5. Risk is "bad when high", so it is flipped (6 - risk).

    weighted score (0-100) = 20 x sum(weight x criterion) / sum(weights)
    ease                   = average of feasibility, data_readiness and (6 - risk)

Quadrants (value on one axis, ease on the other). "High value" means value 4 or 5;
"easy" means ease of 3.0 or more on the 1-5 scale:
    Flagship   high value, high ease  -> the strategy's headline deliveries
    Quick win  lower value, high ease -> cheap, fast proof that the programme delivers
    Long bet   high value, low ease   -> fund the data and readiness work first
    Drop       lower value, low ease  -> do not fund in this strategy period

Waves (each wave is roughly 12 months; at most --per-wave projects start in one wave):
    Wave 1: quick wins and flagships that go live within 12 months
    Wave 2: remaining flagships
    Wave 3: long bets (their data-readiness work should start in Wave 1)
    Overflow beyond the per-wave limit moves to the next wave, highest score first.
"""

import argparse
import csv

# Criterion weights. They reflect a finance ministry's view: value and feasibility
# matter most. Change them by recorded decision, and say so in the report.
WEIGHTS = {"value": 0.35, "feasibility": 0.25, "data_readiness": 0.25, "risk": 0.15}
VALUE_THRESHOLD = 4
EASE_THRESHOLD = 3.0
SCORE_FIELDS = ("value", "feasibility", "data_readiness", "risk")


def read_use_cases(path):
    """Read the CSV, skipping comment lines, and convert numbers."""
    with open(path, encoding="utf-8", newline="") as handle:
        lines = [line for line in handle if not line.lstrip().startswith("#")]
    rows = []
    for row in csv.DictReader(lines):
        for field in SCORE_FIELDS:
            row[field] = int(row[field])
            if not 1 <= row[field] <= 5:
                raise ValueError(f"{row['id']}: {field} must be 1-5, got {row[field]}")
        row["cost_usd"] = float(row["cost_usd"])
        row["months"] = int(row["months"])
        rows.append(row)
    return rows


def weighted_score(uc, weights=WEIGHTS):
    """Return the 0-100 weighted score. Risk is flipped so that low risk scores high."""
    criteria = {
        "value": uc["value"],
        "feasibility": uc["feasibility"],
        "data_readiness": uc["data_readiness"],
        "risk": 6 - uc["risk"],
    }
    total = sum(weights[k] * criteria[k] for k in weights)
    return 20 * total / sum(weights.values())


def ease(uc):
    """Average of feasibility, data readiness and flipped risk (1-5 scale)."""
    return (uc["feasibility"] + uc["data_readiness"] + (6 - uc["risk"])) / 3


def quadrant(uc, value_threshold=VALUE_THRESHOLD, ease_threshold=EASE_THRESHOLD):
    """Place a use case in one of four quadrants."""
    high_value = uc["value"] >= value_threshold
    easy = ease(uc) >= ease_threshold
    if high_value and easy:
        return "Flagship"
    if easy:
        return "Quick win"
    if high_value:
        return "Long bet"
    return "Drop"


def assign_waves(use_cases, per_wave=5):
    """Give each funded use case a wave number (1-3+). Dropped cases get None."""
    for uc in use_cases:
        q = uc["quadrant"]
        if q == "Drop":
            uc["wave"] = None
        elif q == "Long bet":
            uc["wave"] = 3
        elif q == "Quick win" or uc["months"] <= 12:
            uc["wave"] = 1
        else:
            uc["wave"] = 2
    # Enforce delivery capacity: a delivery unit cannot start everything at once.
    wave = 1
    while any(uc["wave"] == wave for uc in use_cases):
        in_wave = sorted((uc for uc in use_cases if uc["wave"] == wave),
                         key=lambda u: -u["score"])
        for uc in in_wave[per_wave:]:
            uc["wave"] = wave + 1
        wave += 1
    return use_cases


def score_portfolio(use_cases, per_wave=5):
    """Add score, ease, quadrant and wave to each use case; return sorted by score."""
    for uc in use_cases:
        uc["score"] = weighted_score(uc)
        uc["ease"] = ease(uc)
        uc["quadrant"] = quadrant(uc)
    assign_waves(use_cases, per_wave=per_wave)
    return sorted(use_cases, key=lambda u: (-u["score"], u["id"]))


def md_table(headers, rows):
    """Format rows as a Markdown pipe table."""
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def render(ranked):
    """Return the Markdown report."""
    out = ["## Use-case portfolio, ranked by weighted score", ""]
    rows = [
        [u["id"], u["use_case"], f"{u['score']:.0f}", u["value"], f"{u['ease']:.1f}",
         u["quadrant"], u["wave"] or "-"]
        for u in ranked
    ]
    out.append(md_table(["ID", "Use case", "Score", "Value", "Ease", "Quadrant", "Wave"], rows))

    out += ["", "## Delivery waves", ""]
    wave_rows = []
    waves = sorted({u["wave"] for u in ranked if u["wave"]})
    for w in waves:
        items = [u for u in ranked if u["wave"] == w]
        wave_rows.append([
            f"Wave {w}", len(items), f"${sum(u['cost_usd'] for u in items):,.0f}",
            max(u["months"] for u in items), ", ".join(u["id"] for u in items),
        ])
    dropped = [u for u in ranked if u["wave"] is None]
    wave_rows.append(["Not funded", len(dropped), f"${sum(u['cost_usd'] for u in dropped):,.0f}",
                      "-", ", ".join(u["id"] for u in dropped) or "-"])
    out.append(md_table(["Wave", "Use cases", "Cost to live (USD)", "Longest (months)", "IDs"],
                        wave_rows))
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Score and sequence an AI use-case portfolio.")
    parser.add_argument("csv_file", help="Use-case CSV file")
    parser.add_argument("--per-wave", type=int, default=5, help="Max new projects per wave")
    args = parser.parse_args()
    print(render(score_portfolio(read_use_cases(args.csv_file), per_wave=args.per_wave)))


if __name__ == "__main__":
    main()
