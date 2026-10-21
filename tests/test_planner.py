# Purpose: tests for planner/compute_planner.py against a hand-computed case.
# Book: National AI Strategy in Practice, Chapters 4, 5 and 7
# Licence: MIT (see LICENSE)
import compute_planner as cp
import pytest

COMMON = {
    "hardware": {"gpus_per_server": 8, "server_power_kw": 10, "average_load_factor": 0.5,
                 "network_storage_power_pct": 0.1, "server_price_usd": 100_000,
                 "networking_pct_of_servers": 0.1, "storage_usd_per_tb": 100},
    "model_classes": {"small": {"name": "Small", "output_tokens_per_s_per_gpu": 1000,
                                "gpus_per_replica": 1}},
    "capacity": {"headroom": 0.25, "redundancy_servers_per_pool": 1},
    "facility": {"pue": 1.5, "fitout_usd_per_kw": 1000},
    "costs": {"maintenance_pct_per_year": 0.1, "software_usd_per_gpu_year": 0, "years": 5},
    "rent": {"neocloud_usd_per_gpu_hour": 2.0, "hyperscaler_usd_per_gpu_hour": 4.0,
             "owned_utilisation": 0.5},
    "talent": {"gpus_per_engineer": 16, "minimum_team": 2},
}
SCENARIO = {
    "name": "Hand case",
    "demand": [{"stream": "Staff", "users": 100_000, "adoption_rate": 0.5,
                "interactions_per_user_per_day": 8, "input_tokens": 1000,
                "output_tokens": 360, "active_hours_per_day": 10, "peak_factor": 2,
                "model_mix": {"small": 1.0}}],
    "research": {"users": 10, "gpu_hours_per_user_per_month": 73, "target_utilisation": 0.5},
    "storage_tb": 10,
    "electricity_usd_per_kwh": 0.1,
    "engineer_cost_usd_per_year": 50_000,
    "connectivity_usd_per_year": 10_000,
}


def test_hand_computed_case():
    r = cp.plan(SCENARIO, COMMON)
    # 100,000 x 0.5 x 8 = 400,000 interactions; x360 / 36,000 s = 4,000 tok/s; x2 peak.
    assert r["streams"][0]["avg_output_tps"] == pytest.approx(4000)
    assert r["streams"][0]["peak_output_tps"] == pytest.approx(8000)
    small, research = r["pools"]
    # 8,000 / 1,000 = 8 GPUs; x1.25 = 10; 2 servers + 1 spare = 3 servers, 24 GPUs.
    assert (small["required_gpus"], small["servers"], small["installed_gpus"]) == (10, 3, 24)
    # 10 x 73 = 730 GPU-h/month / (730 x 0.5) = 2 GPUs -> 1 server.
    assert (research["required_gpus"], research["servers"]) == (2, 1)
    assert r["servers"] == 4 and r["installed_gpus"] == 32
    assert r["it_kw"] == pytest.approx(44)               # 4 x 10 x 1.1
    assert r["facility_kw"] == pytest.approx(66)
    assert r["annual_mwh"] == pytest.approx(289.08)      # 44 x 0.5 x 8760 x 1.5 / 1000
    assert r["total_capex"] == pytest.approx(485_000)    # 400k + 40k + 1k + 44k
    assert r["opex"]["Electricity"] == pytest.approx(28_908)
    assert r["opex"]["Maintenance and spares"] == pytest.approx(44_100)
    assert r["engineers"] == 2
    assert r["annual_opex"] == pytest.approx(183_008)
    assert r["tco"] == pytest.approx(1_400_040)
    neo = r["rent"][0]
    assert neo["cost"] == pytest.approx(32 * 8760 * 5 * 0.5 * 2.0)
    assert neo["breakeven_utilisation"] == pytest.approx(1_400_040 / (32 * 8760 * 5) / 2.0)


def test_overrides_apply_per_scenario():
    scenario = dict(SCENARIO, overrides={"facility": {"pue": 2.0}})
    assert cp.plan(scenario, COMMON)["facility_kw"] == pytest.approx(88)
    assert COMMON["facility"]["pue"] == 1.5      # common settings left untouched


def test_sensitivity_more_throughput_never_needs_more_gpus():
    rows = cp.sensitivity(SCENARIO, COMMON)
    gpus = [row["inference_gpus"] for row in rows]
    assert gpus == sorted(gpus, reverse=True)


def test_shipped_scenarios_run():
    data = cp.load_assumptions()
    assert len(data["scenarios"]) >= 2
    for scenario in data["scenarios"]:
        r = cp.plan(scenario, data["common"])
        assert r["installed_gpus"] > 0 and r["tco"] > r["total_capex"]
        assert "### Build versus rent" in cp.render(r)
