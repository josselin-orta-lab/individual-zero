"""Parameterized Stage-2 panel runner: the exact Stage-2.1 transport (ADR-0019).

Historical Stage-2.1 runner with active sealed ENGINEERING rehearsals only.
The exact scientific DEVELOPMENT 80/81 panel has already executed once;
its old owner lift has been consumed, and `execute` is permanently closed.
Historical original G/R receipts remain source-pinned at their executed SHA.
New selected studies require a separate prospective entrypoint and owner lift. Every life of every arm passes the admission
guard; scientific cohorts fail closed before any World is built.

    python -m i3.lab.stage2_panel rehearse PLAN.json
    # Historical `run` route now fails closed, even with the old lift.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from statistics import mean
import sys

from . import stage2_admission as ADM
from . import two_phase_panel as TP
from ..modules.genome import generation_zero
from ..runtime.life import REPLAY_GATE_POLICIES, run_life

SCHEMA = "i3-stage2-panel-runner/v1"
NAMESPACES = ("scientific", "engineering")
FIXED = "reference"


def load_plan(plan_path) -> dict:
    plan = json.loads(Path(plan_path).read_text())
    if plan.get("schema") != "i3-stage2-panel-plan/v1":
        raise ValueError("unknown panel plan schema")
    if plan["arms"][0] != FIXED or not set(plan["arms"][1:]) <= set(REPLAY_GATE_POLICIES):
        raise ValueError("plan arms must be FIXED followed by declared replay-gate policies")
    if plan["engineering"]["cohort"] != "engineering":
        raise ValueError("rehearsal namespace must be the engineering cohort")
    if plan["scientific"]["cohort"] == "engineering":
        raise ValueError("scientific namespace cannot be the engineering cohort")
    return plan


def cases(plan: dict, namespace: str) -> list:
    if namespace not in NAMESPACES:
        raise ValueError("namespace must be scientific or engineering")
    ns = plan[namespace]
    rows = []
    for f, family in enumerate(plan["families"]):
        for w, index in enumerate(ns["indices"]):
            for g, genome_seed in enumerate(ns["genome_seeds"]):
                life_seed = ns["life_seed_base"] + 1000 * f + 10 * w + g
                for policy in plan["arms"]:
                    rows.append({"cohort": ns["cohort"], "family": family, "index": index,
                                 "genome_seed": genome_seed, "life_seed": life_seed,
                                 "policy": policy, "block": f"{family}-{index}-g{genome_seed}"})
    return rows


def make_run_case(plan_path):
    plan = load_plan(plan_path)

    def run_case(case):
        ticket, spec = ADM.admit(case["cohort"], case["family"], case["index"], plan_path)
        gated = case["policy"] in REPLAY_GATE_POLICIES
        life = run_life(generation_zero(case["genome_seed"]), spec, case["life_seed"],
                        plan["horizon"], protocol=plan["protocol_id"],
                        decision_policy=case["policy"],
                        admission=ticket if gated else None)
        life["admission_receipt"] = ticket.receipt()
        return life
    return run_case


def make_invariants(plan: dict, fingerprint: str):
    horizon = plan["horizon"]

    def invariants(identity, life):
        ca = life["cognitive_accounting"]
        policy = life["manifest"].get("experimental_policy", {}).get("name", FIXED)
        receipt = life["admission_receipt"]
        return {
            "no_unpaid_energy": ca["totals"]["energy"]["unpaid"] <= 1e-12,
            "no_unpaid_vigilance": ca["totals"]["vigilance"]["unpaid"] <= 1e-12,
            "no_shortfall": ca["shortfall_steps"] == 0,
            "settled": ca["status"] == "SETTLED_FOR_DECLARED_WORK",
            "within_horizon": 0 < life["steps_lived"] <= horizon,
            "declared_policy": policy == identity["policy"],
            "gate_summary_iff_gate": (identity["policy"] != FIXED) == ("replay_gate" in life),
            "admission_bound_to_world": (
                receipt["world_name"] == life["world"] and
                receipt["world_sha256"] == life["manifest"]["world_sha256"]),
            "admission_cohort_matches": receipt["cohort"] == identity["cohort"],
            "admission_fingerprint_matches": receipt["transport_fingerprint"] == fingerprint,
        }
    return invariants


def reduce_row(identity, life):
    n = life["steps_lived"]
    ca = life["cognitive_accounting"]
    sleep = life["actions"].get("dormir", 0)
    return {
        **identity,
        "steps_lived": n, "terminal": life["terminal"], "death_causes": life["death_causes"],
        "energy_per_step": ca["totals"]["energy"]["paid"] / n,
        "vigilance_per_step": ca["totals"]["vigilance"]["paid"] / n,
        "replays": ca["replays_executed"], "sleep_steps": sleep, "sleep_fraction": sleep / n,
        "inactive_fraction": ca["inactive_steps"] / n,
        "drinks": life["drinks"], "meals": life["meals"],
        "first_drink_step": life["first_drink_step"], "mean_step_ms": life["mean_step_ms"],
        "replay_gate": life.get("replay_gate"),
    }


def summarize(plan: dict, rows: list) -> dict:
    by_arm = {}
    for arm in plan["arms"]:
        rs = [r for r in rows if r["policy"] == arm]
        lived = sum(r["steps_lived"] for r in rs)
        sleeps = sum(r["sleep_steps"] for r in rs)
        by_arm[arm] = {
            "lives": len(rs),
            "censored_at_horizon": sum(r["terminal"] == "censored" for r in rs),
            "mean_steps_lived": mean(r["steps_lived"] for r in rs),
            "energy_per_lived_step": sum(r["energy_per_step"] * r["steps_lived"] for r in rs) / lived,
            "vigilance_per_lived_step": sum(r["vigilance_per_step"] * r["steps_lived"] for r in rs) / lived,
            "replays_per_sleep_step": (sum(r["replays"] for r in rs) / sleeps) if sleeps else None,
            "sleep_fraction": sleeps / lived,
            "inactive_fraction": sum(r["inactive_fraction"] * r["steps_lived"] for r in rs) / lived,
            "lives_with_a_drink": sum(r["drinks"] > 0 for r in rs),
        }
    gate = plan["arms"][1]
    return {"by_arm": by_arm,
            "random_equal_mean_parameter": {
                "definition": f"pooled replays per sleep step of {gate} in this pilot",
                "value": by_arm[gate]["replays_per_sleep_step"]}}


def rehearse(plan_path) -> dict:
    """ADR-0017/ADR-0019 sealed rehearsal on the engineering namespace only."""
    plan = load_plan(plan_path)
    fingerprint = ADM.transport_fingerprint(plan_path)
    report = TP.sealed_rehearsal(cases(plan, "engineering"), make_run_case(plan_path),
                                 reduce_row, make_invariants(plan, fingerprint))
    report.update(runner=SCHEMA, protocol_id=plan["protocol_id"],
                  transport_fingerprint=fingerprint,
                  plan_sha256=sha256(Path(plan_path).read_bytes()).hexdigest(),
                  namespace="engineering")
    return report


def execute(plan_path, archive_dir):
    """The DEVELOPMENT 80/81 source-locked permission was consumed once.

    This retained pilot executor is permanently closed. New selected studies
    must use a separately authorized, prospectively scoped source-locked path
    with its own irreversible pre-exposure claim. Engineering rehearsals are
    still supported by `rehearse`; none of this path can open a science World.
    """
    raise PermissionError(
        "DEVELOPMENT 80/81 closed without retry; legacy scientific runner exhausted")

def main(argv):
    if len(argv) == 3 and argv[1] == "rehearse":
        print(json.dumps(rehearse(argv[2]), sort_keys=True, indent=1))
    elif len(argv) == 5 and argv[1] == "run":
        result = execute(argv[2], argv[3])
        Path(argv[4]).write_text(json.dumps(result, sort_keys=True, separators=(",", ":")) + "\n")
        print(json.dumps({k: v for k, v in result.items() if k != "rows"}, sort_keys=True, indent=1))
    else:
        raise SystemExit("usage: rehearse PLAN | run PLAN ARCHIVE OUT")


if __name__ == "__main__":
    main(sys.argv)
