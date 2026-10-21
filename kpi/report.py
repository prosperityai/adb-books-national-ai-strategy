# Purpose: compare current KPI values with the straight-line path from baseline to
#          target and print a RAG (red/amber/green) status table in Markdown.
# Book: National AI Strategy in Practice, Chapter 12
# Licence: MIT (see LICENSE)
"""KPI RAG report.

Run:
    python3 kpi/report.py kpi/example-values.yaml

The RAG rule:
    elapsed  = time since strategy start / time from start to target date   (0 to 1)
    progress = (current - baseline) / (target - baseline)
               This works for "down" KPIs too: a fall towards a lower target is positive.
    ratio    = progress / elapsed      (how much of the expected progress is done)

    GREEN    target already met, or ratio >= green threshold (default 0.90)
    AMBER    ratio >= amber threshold (default 0.60)
    RED      below that, or moving the wrong way
    NO DATA  no verified current value. Treat as a reporting failure, not as neutral.

Status words, not colours, are printed so the table reads in black and white.
"""

import argparse
import datetime as dt
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
DEFAULT_FRAMEWORK = HERE / "kpi_framework.yaml"
LEVELS = ("input", "output", "outcome", "impact")


def load_yaml(path):
    """Read a YAML file."""
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def elapsed_fraction(start, end, when):
    """Share of the strategy period that has passed, clipped to 0-1."""
    total = (end - start).days
    return min(max((when - start).days / total, 0.0), 1.0)


def target_met(kpi, current):
    """True if the current value has reached the target in the right direction."""
    if kpi["direction"] == "up":
        return current >= kpi["target"]
    return current <= kpi["target"]


def rag_status(kpi, current, elapsed, green=0.90, amber=0.60):
    """Return (status, progress) for one KPI."""
    if current is None:
        return "NO DATA", None
    span = kpi["target"] - kpi["baseline"]
    progress = (current - kpi["baseline"]) / span if span else 1.0
    if target_met(kpi, current):
        return "GREEN", progress
    if progress < 0:
        return "RED", progress
    if elapsed <= 0:
        return "GREEN", progress
    ratio = progress / elapsed
    if ratio >= green:
        return "GREEN", progress
    if ratio >= amber:
        return "AMBER", progress
    return "RED", progress


def build_report(framework, values):
    """Return a list of result rows and the elapsed fraction."""
    when = values["reporting_date"]
    if isinstance(when, str):
        when = dt.date.fromisoformat(when)
    elapsed = elapsed_fraction(framework["strategy_start"], framework["target_date"], when)
    thresholds = framework.get("rag_thresholds", {})
    rows = []
    for kpi in sorted(framework["kpis"], key=lambda k: (LEVELS.index(k["level"]), k["id"])):
        current = (values.get("values") or {}).get(kpi["id"])
        status, progress = rag_status(kpi, current, elapsed, thresholds.get("green", 0.90),
                                      thresholds.get("amber", 0.60))
        rows.append({**kpi, "current": current, "status": status, "progress": progress})
    return rows, elapsed


def md_table(headers, rows):
    """Format rows as a Markdown pipe table."""
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def num(value):
    """Print whole numbers with thousands separators."""
    if value is None:
        return "-"
    return f"{value:,.0f}" if float(value).is_integer() else f"{value:,.1f}"


def render(rows, elapsed, reporting_date):
    """Return the Markdown report."""
    out = [f"## KPI status at {reporting_date}", "",
           f"{elapsed:.0%} of the strategy period has elapsed, so a KPI on track shows "
           f"about {elapsed:.0%} progress from baseline to target.", ""]
    table = [
        [r["id"], r["level"].capitalize(), r["name"], num(r["baseline"]), num(r["target"]),
         num(r["current"]), "-" if r["progress"] is None else f"{r['progress']:.0%}",
         r["status"]]
        for r in rows
    ]
    out.append(md_table(["ID", "Level", "KPI", "Baseline", "Target", "Current", "Progress",
                         "Status"], table))
    out += ["", "## Summary by level", ""]
    statuses = ("GREEN", "AMBER", "RED", "NO DATA")
    summary = [[level.capitalize(), *(sum(1 for r in rows if r["level"] == level
                                          and r["status"] == s) for s in statuses)]
               for level in LEVELS]
    out.append(md_table(["Level", *statuses], summary))
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Print a RAG status report for strategy KPIs.")
    parser.add_argument("values", help="YAML file of current KPI values")
    parser.add_argument("--framework", default=DEFAULT_FRAMEWORK, help="KPI framework YAML")
    args = parser.parse_args()
    values = load_yaml(args.values)
    rows, elapsed = build_report(load_yaml(args.framework), values)
    print(render(rows, elapsed, values["reporting_date"]))


if __name__ == "__main__":
    main()
