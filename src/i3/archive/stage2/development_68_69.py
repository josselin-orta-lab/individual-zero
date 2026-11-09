"""ARCHIVED Stage-2.1 supplied DEVELOPMENT pilot 68/69, not a live runner.

Protocol: docs/studies/stage2-replay-gate-development-68-69/PROTOCOL.md,
committed with this code before the rehearsal and the single execution.
"""
from __future__ import annotations

import json
from statistics import mean
import sys

from i3.lab import engineering_cohort as ENG
from i3.lab import p2_ecologies as P2
from i3.lab import two_phase_panel as TP
from i3.modules.genome import generation_zero
from i3.runtime.life import run_life

PROTOCOL_ID = "STAGE2_1_REPLAY_GATE_DEVELOPMENT_68_69"
FAMILIES = ("stable", "depletion", "pulse")
INDICES = (68, 69)
GENOME_SEEDS = (909, 910)
LIFE_BASE = 7_520_000
REHEARSAL_INDICES = (0, 1)
REHEARSAL_GENOME_SEEDS = (90_001, 90_002)
REHEARSAL_LIFE_BASE = 9_000_000
ARMS = ("reference", "p13_replay_gate_v1", "p13_replay_gate_zero_perceived_cost_v1")
HORIZON = 400


def cases(kind: str = "development"):
    if kind not in ("development", "engineering"):
        raise ValueError("cohort must be development or engineering")
    dev = kind == "development"
    rows = []
    for f, family in enumerate(FAMILIES):
        for w, index in enumerate(INDICES if dev else REHEARSAL_INDICES):
            for g, gseed in enumerate(GENOME_SEEDS if dev else REHEARSAL_GENOME_SEEDS):
                life_seed = (LIFE_BASE if dev else REHEARSAL_LIFE_BASE) + 1000 * f + 10 * w + g
                world_seed = (P2.COHORTS["development"][index] if dev
                              else ENG.ENGINEERING[index])
                for policy in ARMS:
                    rows.append({"cohort": kind, "family": family, "index": index,
                                 "world_seed": world_seed, "genome_seed": gseed,
                                 "life_seed": life_seed, "policy": policy,
                                 "block": f"{family}-{index}-g{gseed}"})
    return rows


def run_case(case):
    if case["cohort"] == "development":
        ENG.assert_not_engineering(case["world_seed"])
        spec = P2.world_for(case["family"], "development", case["index"])
    else:
        spec = ENG.engineering_world(case["family"], case["index"])
    return run_life(generation_zero(case["genome_seed"]), spec, case["life_seed"],
                    HORIZON, protocol=PROTOCOL_ID, decision_policy=case["policy"])


def invariants(identity, life):
    ca = life["cognitive_accounting"]
    policy = life["manifest"].get("experimental_policy", {}).get("name", "reference")
    return {
        "no_unpaid_energy": ca["totals"]["energy"]["unpaid"] <= 1e-12,
        "no_unpaid_vigilance": ca["totals"]["vigilance"]["unpaid"] <= 1e-12,
        "no_shortfall": ca["shortfall_steps"] == 0,
        "settled": ca["status"] == "SETTLED_FOR_DECLARED_WORK",
        "within_horizon": 0 < life["steps_lived"] <= HORIZON,
        "declared_policy": policy == identity["policy"],
        "gate_summary_iff_gate": (identity["policy"] != "reference") == ("replay_gate" in life),
    }


def reduce_row(identity, life):
    n = life["steps_lived"]
    ca = life["cognitive_accounting"]
    sleep = life["actions"].get("dormir", 0)
    return {
        **identity,
        "steps_lived": n, "terminal": life["terminal"],
        "death_causes": life["death_causes"],
        "energy_per_step": ca["totals"]["energy"]["paid"] / n,
        "vigilance_per_step": ca["totals"]["vigilance"]["paid"] / n,
        "replays": ca["replays_executed"], "sleep_steps": sleep,
        "sleep_fraction": sleep / n,
        "inactive_fraction": ca["inactive_steps"] / n,
        "drinks": life["drinks"], "meals": life["meals"],
        "first_drink_step": life["first_drink_step"],
        "mean_step_ms": life["mean_step_ms"],
        "replay_gate": life.get("replay_gate"),
    }


def summarize(rows):
    by_arm = {}
    for arm in ARMS:
        rs = [r for r in rows if r["policy"] == arm]
        sleeps = sum(r["sleep_steps"] for r in rs)
        by_arm[arm] = {
            "lives": len(rs),
            "censored_at_horizon": sum(r["terminal"] == "censored" for r in rs),
            "mean_steps_lived": mean(r["steps_lived"] for r in rs),
            "energy_per_lived_step": sum(r["energy_per_step"] * r["steps_lived"] for r in rs)
                                     / sum(r["steps_lived"] for r in rs),
            "vigilance_per_lived_step": sum(r["vigilance_per_step"] * r["steps_lived"] for r in rs)
                                        / sum(r["steps_lived"] for r in rs),
            "replays_per_sleep_step": (sum(r["replays"] for r in rs) / sleeps) if sleeps else None,
            "sleep_fraction": sum(r["sleep_steps"] for r in rs) / sum(r["steps_lived"] for r in rs),
            "inactive_fraction": sum(r["inactive_fraction"] * r["steps_lived"] for r in rs)
                                 / sum(r["steps_lived"] for r in rs),
            "lives_with_a_drink": sum(r["drinks"] > 0 for r in rs),
        }
    paired = {}
    for arm in ARMS[1:]:
        diffs = []
        for r in rows:
            if r["policy"] != arm:
                continue
            ref = next(x for x in rows if x["policy"] == "reference" and x["block"] == r["block"])
            diffs.append({"block": r["block"],
                          "steps_lived": r["steps_lived"] - ref["steps_lived"],
                          "energy_per_step": r["energy_per_step"] - ref["energy_per_step"],
                          "vigilance_per_step": r["vigilance_per_step"] - ref["vigilance_per_step"],
                          "sleep_fraction": r["sleep_fraction"] - ref["sleep_fraction"],
                          "inactive_fraction": r["inactive_fraction"] - ref["inactive_fraction"]})
        paired[arm] = {
            "blocks": diffs,
            "longer_life_blocks": sum(d["steps_lived"] > 0 for d in diffs),
            "shorter_life_blocks": sum(d["steps_lived"] < 0 for d in diffs),
            "cheaper_energy_blocks": sum(d["energy_per_step"] < 0 for d in diffs),
            "cheaper_vigilance_blocks": sum(d["vigilance_per_step"] < 0 for d in diffs),
        }
    return {"by_arm": by_arm, "paired_against_reference": paired,
            "random_equal_mean_parameter": {
                "definition": "pooled replays per sleep step of p13_replay_gate_v1 in this pilot",
                "value": by_arm["p13_replay_gate_v1"]["replays_per_sleep_step"]}}


def rehearse():
    return TP.sealed_rehearsal(cases("engineering"), run_case, reduce_row, invariants)


def execute(archive_dir):
    g = TP.generate(cases("development"), run_case, archive_dir)
    if g["status"] != "GENERATED":
        return {"generation": {k: g[k] for k in ("status", "planned", "generated", "failure")},
                "status": "ENGINEERING_FAILURE_NOT_A_DEATH"}
    r = TP.reduce(archive_dir, reduce_row)
    if r["status"] != "COMPLETE":
        return {"generation": {k: g[k] for k in ("status", "planned", "generated")},
                "reduction": r, "status": r["status"]}
    checks = {}
    for identity, life in TP.load_sealed(archive_dir):
        for name, ok in invariants(identity, life).items():
            checks[name] = checks.get(name, 0) + (not ok)
    continuation = all(v == 0 for v in checks.values())
    return {"status": "COMPLETE",
            "continuation": "PASS" if continuation else "FAIL",
            "invariant_failures": checks,
            "generation": {k: g[k] for k in ("status", "planned", "generated")},
            "rows": r["rows"], "summary": summarize(r["rows"])}


def main(argv):
    if len(argv) >= 2 and argv[1] == "rehearse":
        print(json.dumps(rehearse(), sort_keys=True, indent=1))
    elif len(argv) == 4 and argv[1] == "run":
        result = execute(argv[2])
        with open(argv[3], "w") as fh:
            fh.write(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
        print(json.dumps({k: v for k, v in result.items() if k != "rows"}, sort_keys=True, indent=1))
    else:
        raise SystemExit("usage: rehearse | run <archive-dir> <out.json>")


if __name__ == "__main__":
    main(sys.argv)
