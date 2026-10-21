# Purpose: build a five-year national AI strategy budget workbook (by pillar and by
#          financing source) with live Excel formulas, and print a Markdown summary.
# Book: National AI Strategy in Practice, Chapter 10
# Licence: MIT (see LICENSE)
"""Strategy budget builder.

Run:
    python3 finance/build_budget.py
    python3 finance/build_budget.py --inputs my_inputs.yaml --out my-budget.xlsx

The workbook has six sheets:
    Read me            what the workbook is and how the sheets link
    Line items         every costed item, by pillar and year (the only typed numbers)
    Financing shares   share of each pillar paid by each source (rows add to 100%)
    By pillar          SUMIFS over the line items
    By source          SUMPRODUCT of pillar totals and financing shares
    Summary            five-year totals, shares and a balance check

Totals are Excel formulas, so a ministry team can change a line item in Excel and
every total updates. The Markdown summary printed here is calculated in Python from
the same inputs, so the book can quote it.
"""

import argparse
import sys
from pathlib import Path

import yaml
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

HERE = Path(__file__).resolve().parent
DEFAULT_INPUTS = HERE / "budget_inputs.yaml"
DEFAULT_OUT = HERE / "strategy-budget.xlsx"

# The compute planner lives in ../planner. Adding it to the import path lets this
# script reuse the planner's figures instead of retyping them.
sys.path.insert(0, str(HERE.parent / "planner"))
import compute_planner  # noqa: E402

MONEY = '#,##0;[Red]-#,##0'
PERCENT = '0%'
BOLD = Font(bold=True)


def load_inputs(path=DEFAULT_INPUTS):
    """Read the budget inputs file."""
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def compute_line_items(inputs, assumptions_path=compute_planner.DEFAULT_ASSUMPTIONS):
    """Turn the planner's capex and annual opex into two phased budget lines."""
    cfg = inputs["compute"]
    data = compute_planner.load_assumptions(assumptions_path)
    scenario = next(s for s in data["scenarios"] if s["name"] == cfg["planner_scenario"])
    result = compute_planner.plan(scenario, data["common"])
    capex = [round(result["total_capex"] * share) for share in cfg["capex_phasing"]]
    opex = [round(result["annual_opex"] * share) for share in cfg["opex_phasing"]]
    return [
        ["Compute", "National inference and research cluster: capex",
         "From compute planner", *capex],
        ["Compute", "National inference and research cluster: opex",
         "From compute planner", *opex],
    ]


def all_line_items(inputs):
    """Planner-derived compute lines plus the typed line items, grouped by pillar order."""
    items = compute_line_items(inputs) + [list(row) for row in inputs["line_items"]]
    order = {name: i for i, name in enumerate(inputs["pillars"])}
    for row in items:
        if row[0] not in order:
            raise ValueError(f"Line item {row[1]!r} has unknown pillar {row[0]!r}")
    return sorted(items, key=lambda row: order[row[0]])


def validate_shares(inputs):
    """Every pillar needs a financing row that adds up to 100%."""
    for pillar in inputs["pillars"]:
        shares = inputs["financing_shares"].get(pillar)
        if shares is None or len(shares) != len(inputs["sources"]):
            raise ValueError(f"Financing shares missing or wrong length for {pillar!r}")
        if abs(sum(shares) - 1.0) > 1e-9:
            raise ValueError(f"Financing shares for {pillar!r} add to {sum(shares)}, not 1.0")


def totals(inputs, items):
    """Python version of the workbook arithmetic, used for the Markdown summary and tests."""
    n_years = len(inputs["years"])
    by_pillar = {p: [0.0] * n_years for p in inputs["pillars"]}
    for row in items:
        for y in range(n_years):
            by_pillar[row[0]][y] += row[3 + y]
    by_source = {s: [0.0] * n_years for s in inputs["sources"]}
    for pillar, amounts in by_pillar.items():
        for j, source in enumerate(inputs["sources"]):
            for y in range(n_years):
                by_source[source][y] += amounts[y] * inputs["financing_shares"][pillar][j]
    return by_pillar, by_source


def build_workbook(inputs, items):
    """Create the workbook. Every total is a formula, not a typed number."""
    years, pillars, sources = inputs["years"], inputs["pillars"], inputs["sources"]
    n_years, n_p, n_s = len(years), len(pillars), len(sources)
    wb = Workbook()

    # Read me.
    ws = wb.active
    ws.title = "Read me"
    notes = [
        f"National AI strategy budget: {inputs['country']}",
        "ILLUSTRATIVE: example figures for a fictional country. Replace with your own costing.",
        f"Currency: {inputs['currency']}. Years: {', '.join(years)}.",
        "Type numbers only on 'Line items' and 'Financing shares'. Every other sheet is formulas.",
        "Compute lines come from planner/compute_planner.py (see the planner assumptions).",
        "Book: National AI Strategy in Practice, Chapter 10. Licence: MIT.",
    ]
    for i, text in enumerate(notes, start=1):
        ws.cell(row=i, column=1, value=text).font = BOLD if i == 1 else Font()
    ws.column_dimensions["A"].width = 95

    # Line items: columns A pillar, B item, C basis, D.. years, then total.
    li = wb.create_sheet("Line items")
    li.append(["Pillar", "Item", "Basis", *years, "Total"])
    for r, row in enumerate(items, start=2):
        li.append(row)
        first, last = get_column_letter(4), get_column_letter(3 + n_years)
        li.cell(row=r, column=4 + n_years, value=f"=SUM({first}{r}:{last}{r})")
    last_item_row = len(items) + 1

    # Financing shares: A pillar, B.. sources, then a check column.
    fs = wb.create_sheet("Financing shares")
    fs.append(["Pillar", *sources, "Check (must be 100%)"])
    for r, pillar in enumerate(pillars, start=2):
        fs.append([pillar, *inputs["financing_shares"][pillar]])
        fs.cell(row=r, column=2 + n_s,
                value=f"=SUM(B{r}:{get_column_letter(1 + n_s)}{r})")

    # By pillar: SUMIFS of line items for each pillar and year.
    bp = wb.create_sheet("By pillar")
    bp.append(["Pillar", *years, "Total"])
    for r, pillar in enumerate(pillars, start=2):
        bp.cell(row=r, column=1, value=pillar)
        for y in range(n_years):
            col = get_column_letter(4 + y)
            bp.cell(row=r, column=2 + y, value=(
                f"=SUMIFS('Line items'!{col}$2:{col}${last_item_row},"
                f"'Line items'!$A$2:$A${last_item_row},$A{r})"))
        bp.cell(row=r, column=2 + n_years,
                value=f"=SUM(B{r}:{get_column_letter(1 + n_years)}{r})")
    total_row = n_p + 2
    bp.cell(row=total_row, column=1, value="Total").font = BOLD
    for c in range(2, 3 + n_years):
        col = get_column_letter(c)
        bp.cell(row=total_row, column=c, value=f"=SUM({col}2:{col}{n_p + 1})").font = BOLD

    # By source: for each source and year, SUMPRODUCT(pillar amounts, pillar shares).
    bs = wb.create_sheet("By source")
    bs.append(["Source", *years, "Total"])
    for r, source in enumerate(sources, start=2):
        share_col = get_column_letter(r)  # column B holds the first source, C the second...
        bs.cell(row=r, column=1, value=source)
        for y in range(n_years):
            col = get_column_letter(2 + y)
            bs.cell(row=r, column=2 + y, value=(
                f"=SUMPRODUCT('By pillar'!{col}$2:{col}${n_p + 1},"
                f"'Financing shares'!{share_col}$2:{share_col}${n_p + 1})"))
        bs.cell(row=r, column=2 + n_years,
                value=f"=SUM(B{r}:{get_column_letter(1 + n_years)}{r})")
    src_total_row = n_s + 2
    bs.cell(row=src_total_row, column=1, value="Total").font = BOLD
    for c in range(2, 3 + n_years):
        col = get_column_letter(c)
        bs.cell(row=src_total_row, column=c,
                value=f"=SUM({col}2:{col}{n_s + 1})").font = BOLD

    # Summary: five-year totals and shares, with a balance check.
    sm = wb.create_sheet("Summary")
    total_col = get_column_letter(2 + n_years)
    sm.append(["Five-year total by pillar", inputs["currency"], "Share"])
    for i, pillar in enumerate(pillars):
        r = i + 2
        sm.append([pillar, f"='By pillar'!{total_col}{r}",
                   f"=B{r}/'By pillar'!{total_col}{total_row}"])
    sm.append(["Total", f"='By pillar'!{total_col}{total_row}", f"=SUM(C2:C{n_p + 1})"])
    start = n_p + 4
    sm.cell(row=start, column=1, value="Five-year total by source").font = BOLD
    for i, source in enumerate(sources):
        r = start + 1 + i
        sm.cell(row=r, column=1, value=source)
        sm.cell(row=r, column=2, value=f"='By source'!{total_col}{i + 2}")
        sm.cell(row=r, column=3, value=f"=B{r}/'By source'!{total_col}{src_total_row}")
    check_row = start + n_s + 2
    sm.cell(row=check_row, column=1, value="Check: pillars minus sources (must be 0)")
    sm.cell(row=check_row, column=2,
            value=(f"=ROUND('By pillar'!{total_col}{total_row}"
                   f"-'By source'!{total_col}{src_total_row},0)"))

    # Formatting: bold headers, money and percent formats, readable widths.
    for sheet in (li, fs, bp, bs, sm):
        for cell in sheet[1]:
            cell.font = BOLD
        sheet.column_dimensions["A"].width = 34
        for col in range(2, sheet.max_column + 1):
            sheet.column_dimensions[get_column_letter(col)].width = 16
    li.column_dimensions["B"].width = 46
    li.column_dimensions["C"].width = 30
    for sheet, first_col in ((li, 4), (bp, 2), (bs, 2)):
        for row in sheet.iter_rows(min_row=2, min_col=first_col):
            for cell in row:
                cell.number_format = MONEY
    for row in fs.iter_rows(min_row=2, min_col=2):
        for cell in row:
            cell.number_format = PERCENT
    for row in sm.iter_rows(min_row=2):
        row[1].number_format = MONEY
        row[2].number_format = PERCENT
    return wb


def md_table(headers, rows):
    """Format rows as a Markdown pipe table."""
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def m(value):
    """USD millions with one decimal place."""
    return f"{value / 1e6:,.1f}"


def render(inputs, by_pillar, by_source):
    """Return the Markdown summary."""
    years = inputs["years"]
    grand = sum(sum(v) for v in by_pillar.values())
    out = [f"## Five-year AI strategy budget: {inputs['country']}", "",
           f"ILLUSTRATIVE. {inputs['currency']} millions.", "",
           "### By pillar", ""]
    rows = [[p, *(m(x) for x in v), m(sum(v)), f"{sum(v) / grand:.0%}"]
            for p, v in by_pillar.items()]
    year_totals = [sum(v[y] for v in by_pillar.values()) for y in range(len(years))]
    rows.append(["**Total**", *(m(x) for x in year_totals), f"**{m(grand)}**", "100%"])
    out.append(md_table(["Pillar", *years, "Total", "Share"], rows))
    out += ["", "### By financing source", ""]
    rows = [[s, *(m(x) for x in v), m(sum(v)), f"{sum(v) / grand:.0%}"]
            for s, v in by_source.items()]
    rows.append(["**Total**", *(m(x) for x in year_totals), f"**{m(grand)}**", "100%"])
    out.append(md_table(["Source", *years, "Total", "Share"], rows))
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Build the strategy budget workbook.")
    parser.add_argument("--inputs", default=DEFAULT_INPUTS, help="Budget inputs YAML")
    parser.add_argument("--out", default=DEFAULT_OUT, help="Workbook to write (.xlsx)")
    args = parser.parse_args()
    inputs = load_inputs(args.inputs)
    validate_shares(inputs)
    items = all_line_items(inputs)
    build_workbook(inputs, items).save(args.out)
    print(render(inputs, *totals(inputs, items)))
    print(f"\nWorkbook written to {Path(args.out).name}")


if __name__ == "__main__":
    main()
