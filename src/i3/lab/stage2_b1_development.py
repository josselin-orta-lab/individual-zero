"""B1 ONE-SHOT exploratory DEVELOPMENT on new known-F0 newborn G0/world pairs.

Owner-delegated operation, not external methodological review or a confirmatory
survival claim. 96 new paired units, each with FIXED then funded GATE at horizon
400. Phase G seals every original before Phase R. Failed G never enters R.
All originals, missingness, adverse and null cases are retained. This runner
cannot address selection, validation, reserve or exhausted DEVELOPMENT 80/81.

Important limitation: a per-workspace claimed run and GH run_attempt guard do
NOT create a global, cryptographic one-shot lock across fresh checkouts.
The operator must archive the execution and close the invocation after launch.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

from . import stage2_survival_b1_sampling as SAMPLE
from . import stage2_survival_b1_worldspec_audit as SPECS
from . import stage2_survival_b1_engineering as ENG
from . import stage2_admission as GUARD
from . import stage2_exact_paired_survival as EXACT
from . import two_phase_panel as TP
from ..modules.genome import generation_zero
from ..runtime.life import run_life

I3 = Path(__file__).resolve().parents[1]
PLAN = (I3 / "docs" / "studies" / "stage2-replay-gate-selected-design"
        / "B1_EXPLORATORY_DEV_PLAN.json")
SCHEMA = "i3-b1-exploratory-development-g-r/v1"
PROTOCOL = "I3_B1_NEW_F0_EXPLORATORY_DEVELOPMENT_2026_11_10"
COHORT = "development"
PAIRS = 96
INDEX_START = 240000
HORIZON = 400
POLICIES = ("reference", "p13_replay_gate_v1")


def _digest(payload) -> str:
    return sha256(json.dumps(payload, sort_keys=True,
                             separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def load_plan() -> dict:
    plan = json.loads(PLAN.read_text())
    expected = {
        "schema": "i3-stage2-b1-exploratory-development/v1",
        "protocol_id": PROTOCOL, "cohort": COHORT,
        "index_start": INDEX_START, "pairs": PAIRS, "horizon": HORIZON,
        "arms": list(POLICIES),
        "status": "FROZEN_PRE_EXPOSURE_PROPOSED",
        "authorized_scope": "OWNER_DELEGATED_DEVELOPMENT_ONLY_2026_11_10",
        "fixed_n_no_replacement": True,
        "no_outcome_adaptive_stop": True,
        "scientific_validation_reserve_permitted": False,
        "repetitions_permitted": False,
        "external_independent_sampling_review": False,
        "source_independent_external_witness": False,
    }
    if any(plan.get(k) != v for k, v in expected.items()):
        raise PermissionError("new B1 DEVELOPMENT plan is not the frozen scope")
    witness = SAMPLE._key(plan["witness"])
    if (plan["witness"] == SAMPLE.PREVIEW_WITNESS or
            sha256(witness).hexdigest() != plan["witness_sha256"]):
        raise PermissionError("B1 witness invalid or reused from synthetic preview")
    return plan


def cases() -> list[dict]:
    plan = load_plan()
    key = SAMPLE._key(plan["witness"])
    units = [
        {
            "pair_id": f"b1-dev-{i:06d}",
            "index": INDEX_START + i,
            "family": SAMPLE._family(key, i),
            "world_seed": SAMPLE._seed(key, i, "world", SAMPLE.WORLD_BASE),
            "genome_seed": SAMPLE._seed(key, i, "genome", SAMPLE.GENOME_BASE),
            "life_seed": SAMPLE._seed(key, i, "life", SAMPLE.LIFE_BASE),
        }
        for i in range(PAIRS)
    ]
    SAMPLE._check_separation(units)
    return [{**unit, "cohort": COHORT, "policy": arm}
            for unit in units for arm in POLICIES]


def match_case(case, fingerprint: str) -> None:
    """Exact source- and allocation-bound guard; no World constructed here."""
    if not isinstance(case, dict) or type(case.get("index")) is not int:
        raise PermissionError("invalid B1 DEVELOPMENT case")
    offset = case["index"] - INDEX_START
    if not 0 <= offset < PAIRS or case.get("policy") not in POLICIES:
        raise PermissionError("outside B1 new-world DEVELOPMENT indices/arms")
    expected = cases()[2 * offset + POLICIES.index(case["policy"])]
    if case != expected or case["cohort"] != COHORT:
        raise PermissionError("not an exact new B1 DEVELOPMENT allocation")
    if fingerprint != ENG.source_fingerprint():
        raise PermissionError("unfrozen B1 DEVELOPMENT source fingerprint")


def _run_case(scheduled: list, fingerprint: str):
    def run(case):
        # Fail before World/genome/Mind if any case is modified or reordered.
        match_case(case, fingerprint)
        offset = case["index"] - INDEX_START
        if case != scheduled[2 * offset + POLICIES.index(case["policy"])]:
            raise PermissionError("source schedule mismatch")
        spec = SPECS._construct_f0_spec(case["family"], case["world_seed"])
        ticket = GUARD.admit_b1_newworld_development(
            case=case, spec=spec, transport_fingerprint=fingerprint)
        life = run_life(
            generation_zero(case["genome_seed"]), spec, case["life_seed"],
            HORIZON, protocol=PROTOCOL, decision_policy=case["policy"],
            admission=(ticket if case["policy"] != "reference" else None),
        )
        life["admission_receipt"] = ticket.receipt()
        return life
    return run


def _reduce_row(identity, life, fingerprint):
    """Reject structural defects *before* releasing an outcome row."""
    ca = life["cognitive_accounting"]
    manifest = life["manifest"]
    receipt = life["admission_receipt"]
    steps = life["steps_lived"]
    is_gate = identity["policy"] != "reference"
    policy = manifest.get("experimental_policy", {}).get("name", "reference")
    checks = {
        "exact_identity": identity["cohort"] == COHORT and
            INDEX_START <= identity["index"] < INDEX_START + PAIRS,
        "paid_energy": ca["totals"]["energy"]["unpaid"] <= 1e-12,
        "paid_vigilance": ca["totals"]["vigilance"]["unpaid"] <= 1e-12,
        "settled": ca["status"] == "SETTLED_FOR_DECLARED_WORK",
        "no_shortfall": ca["shortfall_steps"] == 0,
        "horizon": type(steps) is int and 1 <= steps <= HORIZON,
        "terminal": life["terminal"] in ("dead", "censored"),
        "policy": policy == identity["policy"],
        "replay_gate": ("replay_gate" in life) == is_gate,
        "receipt_cohort": receipt["cohort"] == COHORT,
        "receipt_family_index": receipt["family"] == identity["family"] and
                                receipt["index"] == identity["index"],
        "receipt_world": receipt["world_seed"] == identity["world_seed"] and
                         receipt["world_sha256"] == manifest["world_sha256"] and
                         receipt["world_name"] == life["world"],
        "receipt_source": receipt["transport_fingerprint"] == fingerprint,
        "life_seed": manifest["life_seed"] == identity["life_seed"],
        "horizon_survivor": life["terminal"] != "censored" or steps == HORIZON,
    }
    if not all(checks.values()):
        raise ValueError("B1 original invariant(s) failed: " +
                         ",".join(k for k, ok in checks.items() if not ok))
    return {
        **identity,
        "steps_lived": steps, "terminal": life["terminal"],
        "death_causes": life["death_causes"],
        "paid_energy": ca["totals"]["energy"]["paid"],
        "paid_vigilance": ca["totals"]["vigilance"]["paid"],
        "replays": ca["replays_executed"],
        "sleep_steps": life["actions"].get("dormir", 0),
        "inactive_steps": ca["inactive_steps"],
        "world_sha256": manifest["world_sha256"],
        "genome_sha256": _digest(manifest["genome"]),
        "source_sha256": manifest["source"]["sha256"],
    }


def analyze(scheduled: list, rows: list) -> dict:
    """Finite paired descriptive analysis, not iid certification or NI verdict."""
    if len(scheduled) != 2 * PAIRS or len(rows) != len(scheduled):
        raise ValueError("missing original outcomes: NO_VERDICT")
    if len({r["index"] for r in rows}) != PAIRS:
        raise ValueError("invalid matched pair count")
    all_pairs = []
    for i in range(PAIRS):
        fixed, gate = rows[2 * i:2 * i + 2]
        expected_fixed, expected_gate = scheduled[2 * i:2 * i + 2]
        if any(any(r.get(key) != e.get(key) for key in (
                "index", "cohort", "policy", "family", "world_seed",
                "genome_seed", "life_seed", "pair_id"))
               for r, e in ((fixed, expected_fixed), (gate, expected_gate))):
            raise ValueError("pair identity/order mismatch")
        if any(fixed[k] != gate[k] for k in (
                "world_sha256", "genome_sha256", "life_seed", "source_sha256")):
            raise ValueError("arms not matched to one same-body/world/source")
        all_pairs.append((fixed, gate))

    def stats(pairs):
        n = len(pairs)
        f = [row[0] for row in pairs]
        g = [row[1] for row in pairs]
        fs = [r["terminal"] == "censored" for r in f]
        gs = [r["terminal"] == "censored" for r in g]
        gate_only = sum(gg and not ff for ff, gg in zip(fs, gs))
        fixed_only = sum(ff and not gg for ff, gg in zip(fs, gs))
        both = sum(ff and gg for ff, gg in zip(fs, gs))
        neither = n - gate_only - fixed_only - both
        return {
            "pairs": n, "fixed_horizon_survivors": sum(fs),
            "gate_horizon_survivors": sum(gs),
            "gate_only": gate_only, "fixed_only": fixed_only,
            "both_survive": both, "neither_survive": neither,
            "paired_risk_difference": (gate_only - fixed_only) / n,
            "mean_step_delta": sum(gg["steps_lived"] - ff["steps_lived"]
                                   for ff, gg in pairs) / n,
            "mean_paid_energy_fixed_per_assigned_life":
                sum(x["paid_energy"] for x in f) / n,
            "mean_paid_energy_gate_per_assigned_life":
                sum(x["paid_energy"] for x in g) / n,
            "mean_paid_vigilance_fixed_per_assigned_life":
                sum(x["paid_vigilance"] for x in f) / n,
            "mean_paid_vigilance_gate_per_assigned_life":
                sum(x["paid_vigilance"] for x in g) / n,
            "gate_shorter_lived": sum(gg["steps_lived"] < ff["steps_lived"]
                                     for ff, gg in pairs),
            "gate_longer_lived": sum(gg["steps_lived"] > ff["steps_lived"]
                                    for ff, gg in pairs),
        }

    overall = stats(all_pairs)
    conditional = EXACT.exact_paired_lower_bound(
        pairs=PAIRS, gate_only=overall["gate_only"],
        fixed_only=overall["fixed_only"], alpha=0.05)
    by_family = {
        family: stats([pair for pair in all_pairs if pair[0]["family"] == family])
        for family in SAMPLE.FAMILIES
    }
    if any(not row["pairs"] for row in by_family.values()):
        raise ValueError("family with no observations; not silently excluded")
    return {
        "schema": SCHEMA, "status": "COMPLETE_EXPLORATORY_DEVELOPMENT",
        "primary": overall, "by_family": by_family,
        "conditional_iid_lower_bound_not_scientifically_admitted":
            conditional["simultaneous_one_sided_lower_bound"],
        "conditional_confidence_level": 0.95,
        "iid_sampling_independently_attested": False,
        "external_method_review": False,
        "noninferiority_margin_selected": False,
        "no_generalization_outside_known_F0": True,
        "no_selection_validation_reserve": True,
        "scientific_decision": "EXPLORATORY_ONLY_NOT_CONFIRMATORY",
    }


def execute(destination) -> dict:
    """Historical B1 cohort exhausted; no post-result reenactment permitted."""
    raise PermissionError(
        "B1 DEVELOPMENT 96-pair source executed once at Actions run 42735037051; "
        "cohort CLOSED_NO_RETRY, archive originals instead of generating again")
    if os.getenv("GITHUB_RUN_ATTEMPT", "1") != "1":
        raise PermissionError("attempted Actions retry: no repeat scientific cohort")
    root = Path(destination).resolve()
    if root.exists() and any(root.iterdir()):
        raise PermissionError("B1 DEVELOPMENT source claim already spent in destination")
    root.mkdir(parents=True, exist_ok=True)
    scheduled = cases()
    fingerprint = ENG.source_fingerprint()
    claim = {
        "schema": SCHEMA + "/attempt-claim",
        "status": "CONSUMED_BEFORE_FIRST_BIRTH",
        "source_fingerprint": fingerprint, "plan_sha256": sha256(PLAN.read_bytes()).hexdigest(),
        "pair_count": PAIRS, "life_count": len(scheduled),
        "cohort": COHORT, "index_start": INDEX_START, "no_retry": True,
        "global_irreversible_claim_verified": False,
    }
    (root / "ATTEMPT_CLAIM.json").write_text(json.dumps(claim, sort_keys=True) + "\n")
    original_dir = root / "originals"
    g = TP.generate(scheduled, _run_case(scheduled, fingerprint), original_dir)
    report = {
        "schema": SCHEMA, "planned": len(scheduled), "generated": g["generated"],
        "phase_G": g["status"], "phase_R": None, "reduced": 0,
        "source_fingerprint": fingerprint, "plan_sha256": claim["plan_sha256"],
        "no_retry": True, "experimental_cohort": COHORT,
        "independent_source_attested": False, "scientific_verdict": "NOT_ISSUED",
    }
    if g["status"] != "GENERATED":
        report["status"] = "GENERATION_FAILURE_NO_RETRY"
        report["failure"] = g["failure"]
    else:
        r = TP.reduce(original_dir, lambda identity, life:
                      _reduce_row(identity, life, fingerprint))
        report["phase_R"] = r["status"]
        if r["status"] != "COMPLETE":
            report["status"] = "REDUCTION_DEFECT_PENDING_REPAIR"
            report["failure"] = r.get("failure")
        else:
            report["reduced"] = len(r["rows"])
            report["analysis"] = analyze(scheduled, r["rows"])
            report["status"] = "COMPLETE_EXPLORATORY_DEVELOPMENT"
            (root / "REDUCED_ROWS.json").write_text(
                json.dumps(r["rows"], sort_keys=True, indent=2) + "\n")
    (root / "B1_EXECUTION_REPORT.json").write_text(
        json.dumps(report, sort_keys=True, indent=2) + "\n")
    return report


def main(argv):
    if len(argv) != 3 or argv[1] != "execute":
        raise SystemExit("usage: python -m i3.lab.stage2_b1_development execute FRESH_ARCHIVE_DIR")
    result = execute(argv[2])
    # Show aggregate outcomes only, originals and reduced rows remain sealed.
    print(json.dumps({k: v for k, v in result.items() if k != "failure"},
                     sort_keys=True, indent=2))
    if result["status"] != "COMPLETE_EXPLORATORY_DEVELOPMENT":
        raise SystemExit("B1 failure: no retry, retain full partial archive")


if __name__ == "__main__":
    main(sys.argv)
