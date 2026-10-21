# Purpose: size national AI compute from real demand: users -> tokens per second ->
#          GPUs -> servers -> power -> capex and opex -> 5-year TCO, compared with
#          renting, plus the engineering team needed to run it.
# Book: National AI Strategy in Practice, Chapters 4, 5 and 7
# Licence: MIT (see LICENSE)
"""Compute planner.

Run:
    python3 planner/compute_planner.py                      # every scenario
    python3 planner/compute_planner.py --scenario "Regional research hub"

The arithmetic, step by step (numbers come from assumptions.yaml):
 1. Daily interactions = users x adoption rate x interactions per user per day
    (or a direct "interactions_per_day" for citizen-facing services).
 2. Average output tokens/s = daily interactions x output tokens / (active hours x 3600).
 3. Peak output tokens/s = average x peak factor. Peaks of all streams are added,
    which assumes they coincide: cautious, and right for a planning figure.
 4. Inference GPUs per model class = peak tokens/s / tokens/s per GPU, plus headroom,
    rounded up to whole model replicas.
 5. Servers = GPUs / 8, rounded up, plus one spare server per pool (N+1).
 6. Research GPUs = research users x GPU-hours per month / (730 hours x utilisation).
 7. IT power = servers x kW per server x (1 + network/storage share).
    Facility power = IT power x PUE.
 8. Capex = servers + networking + storage + facility fit-out.
    Annual opex = electricity + maintenance + software + staff + connectivity.
 9. TCO = capex + years x annual opex (no discounting, no hardware refresh).
10. Renting: what the same useful GPU-hours would cost at cloud list prices, and the
    utilisation at which owning becomes cheaper than renting.
11. Sensitivity: the whole plan re-run with GPU throughput halved, doubled and
    multiplied by six, because throughput is the least certain number in the file.
"""

import argparse
import copy
import math
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
DEFAULT_ASSUMPTIONS = HERE / "assumptions.yaml"
HOURS_PER_YEAR = 8760
HOURS_PER_MONTH = 730
SECONDS_PER_HOUR = 3600


def load_assumptions(path=DEFAULT_ASSUMPTIONS):
    """Read the assumptions file."""
    with open(path, encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def merged_settings(common, scenario):
    """Copy the common settings and apply any per-scenario overrides (section by section)."""
    settings = copy.deepcopy(common)
    for section, values in (scenario.get("overrides") or {}).items():
        settings.setdefault(section, {}).update(values)
    return settings


def stream_demand(stream):
    """Return daily interactions and average/peak tokens per second for one stream."""
    if "interactions_per_day" in stream:
        daily = stream["interactions_per_day"]
    else:
        daily = (stream["users"] * stream["adoption_rate"]
                 * stream["interactions_per_user_per_day"])
    seconds = stream["active_hours_per_day"] * SECONDS_PER_HOUR
    avg_out = daily * stream["output_tokens"] / seconds
    avg_in = daily * stream["input_tokens"] / seconds
    return {
        "stream": stream["stream"],
        "daily_interactions": daily,
        "avg_output_tps": avg_out,
        "peak_output_tps": avg_out * stream["peak_factor"],
        "peak_input_tps": avg_in * stream["peak_factor"],
        "model_mix": stream["model_mix"],
    }


def size_pool(peak_tps, model, capacity, gpus_per_server):
    """Size one inference pool (one model class)."""
    raw = peak_tps / model["output_tokens_per_s_per_gpu"]
    with_headroom = raw * (1 + capacity["headroom"])
    replica = model["gpus_per_replica"]
    gpus = math.ceil(with_headroom / replica) * replica if peak_tps > 0 else 0
    servers = math.ceil(gpus / gpus_per_server)
    spare = capacity["redundancy_servers_per_pool"] if servers else 0
    return {
        "pool": model["name"],
        "peak_output_tps": peak_tps,
        "tps_per_gpu": model["output_tokens_per_s_per_gpu"],
        "raw_gpus": raw,
        "required_gpus": gpus,
        "servers": servers + spare,
        "installed_gpus": (servers + spare) * gpus_per_server,
    }


def plan(scenario, common):
    """Run the full calculation for one scenario and return every intermediate figure."""
    s = merged_settings(common, scenario)
    hw, cap, fac, costs, rent, talent = (s["hardware"], s["capacity"], s["facility"],
                                         s["costs"], s["rent"], s["talent"])
    per_server = hw["gpus_per_server"]

    # Steps 1-3: demand.
    streams = [stream_demand(st) for st in scenario["demand"]]
    peak_by_class = {key: 0.0 for key in s["model_classes"]}
    for st in streams:
        for key, share in st["model_mix"].items():
            peak_by_class[key] += st["peak_output_tps"] * share

    # Steps 4-5: inference pools.
    pools = [size_pool(peak_by_class[key], model, cap, per_server)
             for key, model in s["model_classes"].items() if peak_by_class[key] > 0]

    # Step 6: research pool (training, fine-tuning, experiments). Batch work can wait
    # for a repair, so no spare server is added.
    research = scenario.get("research") or {"users": 0, "gpu_hours_per_user_per_month": 0,
                                            "target_utilisation": 1}
    gpu_hours = research["users"] * research["gpu_hours_per_user_per_month"]
    r_gpus = math.ceil(gpu_hours / (HOURS_PER_MONTH * research["target_utilisation"]))
    r_servers = math.ceil(r_gpus / per_server)
    pools.append({
        "pool": "Research and fine-tuning",
        "peak_output_tps": None,
        "tps_per_gpu": None,
        "raw_gpus": gpu_hours / (HOURS_PER_MONTH * research["target_utilisation"]),
        "required_gpus": r_gpus,
        "servers": r_servers,
        "installed_gpus": r_servers * per_server,
    })

    servers = sum(p["servers"] for p in pools)
    installed_gpus = sum(p["installed_gpus"] for p in pools)
    required_gpus = sum(p["required_gpus"] for p in pools)

    # Step 7: power.
    it_kw = servers * hw["server_power_kw"] * (1 + hw["network_storage_power_pct"])
    facility_kw = it_kw * fac["pue"]
    annual_kwh = it_kw * hw["average_load_factor"] * HOURS_PER_YEAR * fac["pue"]

    # Step 8: capex and opex.
    server_capex = servers * hw["server_price_usd"]
    capex = {
        "GPU servers": server_capex,
        "Networking": server_capex * hw["networking_pct_of_servers"],
        "Storage": scenario["storage_tb"] * hw["storage_usd_per_tb"],
        "Facility fit-out": it_kw * fac["fitout_usd_per_kw"],
    }
    hardware_capex = capex["GPU servers"] + capex["Networking"] + capex["Storage"]

    engineers = max(talent["minimum_team"], math.ceil(installed_gpus / talent["gpus_per_engineer"]))
    opex = {
        "Electricity": annual_kwh * scenario["electricity_usd_per_kwh"],
        "Maintenance and spares": hardware_capex * costs["maintenance_pct_per_year"],
        "Software licences": installed_gpus * costs["software_usd_per_gpu_year"],
        "Engineering staff": engineers * scenario["engineer_cost_usd_per_year"],
        "Connectivity": scenario["connectivity_usd_per_year"],
    }

    # Step 9: total cost of ownership.
    years = costs["years"]
    total_capex = sum(capex.values())
    annual_opex = sum(opex.values())
    tco = total_capex + years * annual_opex

    # Step 10: build versus rent.
    installed_hours = installed_gpus * HOURS_PER_YEAR * years
    owned_per_installed_hour = tco / installed_hours
    useful_hours = installed_hours * rent["owned_utilisation"]
    rent_rows = []
    for label, rate in (("Neocloud on-demand", rent["neocloud_usd_per_gpu_hour"]),
                        ("Hyperscaler on-demand", rent["hyperscaler_usd_per_gpu_hour"])):
        rent_rows.append({
            "option": label,
            "rate": rate,
            "cost": useful_hours * rate,
            "breakeven_utilisation": owned_per_installed_hour / rate,
        })

    return {
        "name": scenario["name"],
        "note": scenario.get("note", ""),
        "streams": streams,
        "pools": pools,
        "servers": servers,
        "installed_gpus": installed_gpus,
        "required_gpus": required_gpus,
        "it_kw": it_kw,
        "facility_kw": facility_kw,
        "pue": fac["pue"],
        "annual_mwh": annual_kwh / 1000,
        "capex": capex,
        "total_capex": total_capex,
        "opex": opex,
        "annual_opex": annual_opex,
        "years": years,
        "tco": tco,
        "owned_utilisation": rent["owned_utilisation"],
        "owned_per_useful_hour": owned_per_installed_hour / rent["owned_utilisation"],
        "rent": rent_rows,
        "engineers": engineers,
    }


SENSITIVITY_FACTORS = (0.5, 1, 2, 6)


def sensitivity(scenario, common, factors=SENSITIVITY_FACTORS):
    """Re-run the plan with every model's tokens/s per GPU multiplied by each factor."""
    rows = []
    for factor in factors:
        scaled = copy.deepcopy(common)
        for model in scaled["model_classes"].values():
            model["output_tokens_per_s_per_gpu"] *= factor
        result = plan(scenario, scaled)
        inference = sum(p["installed_gpus"] for p in result["pools"]
                        if p["pool"] != "Research and fine-tuning")
        rows.append({"factor": factor, "inference_gpus": inference,
                     "installed_gpus": result["installed_gpus"],
                     "total_capex": result["total_capex"], "tco": result["tco"]})
    return rows


def md_table(headers, rows):
    """Format rows as a Markdown pipe table."""
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    lines += ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join(lines)


def usd(value):
    """Format a dollar figure: $1.23M above a million, otherwise with commas."""
    return f"${value / 1e6:,.2f}M" if abs(value) >= 1e6 else f"${value:,.0f}"


def render(result, sens=None):
    """Return the Markdown report for one scenario (with optional sensitivity rows)."""
    out = [f"## Compute plan: {result['name']}", "", result["note"], "", "### Demand", ""]
    out.append(md_table(
        ["Stream", "Interactions/day", "Avg output tok/s", "Peak output tok/s"],
        [[s["stream"], f"{s['daily_interactions']:,.0f}", f"{s['avg_output_tps']:,.0f}",
          f"{s['peak_output_tps']:,.0f}"] for s in result["streams"]],
    ))
    out += ["", "### Capacity", ""]
    rows = []
    for p in result["pools"]:
        peak = "-" if p["peak_output_tps"] is None else f"{p['peak_output_tps']:,.0f}"
        tps = "-" if p["tps_per_gpu"] is None else f"{p['tps_per_gpu']:,}"
        rows.append([p["pool"], peak, tps, f"{p['raw_gpus']:.1f}", p["required_gpus"],
                     p["servers"], p["installed_gpus"]])
    rows.append(["**Total**", "", "", "", result["required_gpus"], result["servers"],
                 result["installed_gpus"]])
    out.append(md_table(["Pool", "Peak tok/s", "Tok/s per GPU", "Raw GPUs",
                         "GPUs + headroom", "Servers (N+1)", "Installed GPUs"], rows))
    out += ["", "### Power", ""]
    out.append(md_table(["Measure", "Value"], [
        ["IT load (kW)", f"{result['it_kw']:,.0f}"],
        [f"Facility load at PUE {result['pue']} (kW)", f"{result['facility_kw']:,.0f}"],
        ["Annual energy (MWh)", f"{result['annual_mwh']:,.0f}"],
    ]))
    out += ["", f"### Cost and {result['years']}-year TCO (USD)", ""]
    rows = [[f"Capex: {k}", usd(v)] for k, v in result["capex"].items()]
    rows.append(["**Total capex**", f"**{usd(result['total_capex'])}**"])
    rows += [[f"Opex per year: {k}", usd(v)] for k, v in result["opex"].items()]
    rows.append(["**Total opex per year**", f"**{usd(result['annual_opex'])}**"])
    rows.append([f"**{result['years']}-year TCO**", f"**{usd(result['tco'])}**"])
    out.append(md_table(["Item", "Amount"], rows))
    out += ["", f"### Build versus rent at {result['owned_utilisation']:.0%} utilisation", ""]
    rows = [["Own (this plan)", "-", usd(result["tco"]),
             f"${result['owned_per_useful_hour']:.2f}", "-"]]
    rows += [[r["option"], f"${r['rate']:.2f}", usd(r["cost"]), f"${r['rate']:.2f}",
              f"{r['breakeven_utilisation']:.0%}"] for r in result["rent"]]
    out.append(md_table(["Option", "List $/GPU-h", f"{result['years']}-year cost",
                         "$ per useful GPU-h", "Owning wins above"], rows))
    out += ["", "### Talent", "", md_table(["Measure", "Value"], [
        ["Installed GPUs", result["installed_gpus"]],
        ["Engineers needed to operate", result["engineers"]],
    ])]
    if sens:
        out += ["", "### Sensitivity to GPU throughput", ""]
        out.append(md_table(
            ["Throughput x", "Inference GPUs", "Installed GPUs", "Capex",
             f"{result['years']}-year TCO"],
            [[f"{r['factor']:g}", r["inference_gpus"], r["installed_gpus"],
              usd(r["total_capex"]), usd(r["tco"])] for r in sens]))
    return "\n".join(out)


def main():
    parser = argparse.ArgumentParser(description="Size national AI compute from demand.")
    parser.add_argument("--assumptions", default=DEFAULT_ASSUMPTIONS, help="Assumptions YAML")
    parser.add_argument("--scenario", help="Name of one scenario (default: all)")
    args = parser.parse_args()
    data = load_assumptions(args.assumptions)
    scenarios = [s for s in data["scenarios"] if not args.scenario or s["name"] == args.scenario]
    if not scenarios:
        raise SystemExit(f"No scenario named {args.scenario!r}")
    common = data["common"]
    print("\n\n".join(render(plan(s, common), sensitivity(s, common)) for s in scenarios))


if __name__ == "__main__":
    main()
