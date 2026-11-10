"""Prospectively frozen new three-arm Stage-2.1 EXPLORATORY DEVELOPMENT.

64 entirely new known-F0 family WorldSpec/G0/life units, each with
FIXED, funded GATE, funded RANDOM-EQUAL-MEAN. Actual Phase-G full originals
are retained, then verified/reduced in Phase R; no scientific iid/NI claim.

This runner is deliberately scoped to one trusted-main GitHub push AFTER
a repository-wide source/index claim is created; it does not itself mint
independent external methodological approval. The claim/evidence branches
must never be deleted, rerun or overwritten.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys

from . import stage2_survival_b1_sampling as SAMPLE
from . import stage2_survival_b1_worldspec_audit as SPECS
from . import stage2_survival_b1_engineering as SOURCE
from . import stage2_admission as GUARD
from . import stage2_exact_paired_survival as EXACT
from . import two_phase_panel as TP
from ..modules.genome import generation_zero
from ..runtime.life import run_life

I3 = Path(__file__).resolve().parents[1]
PLAN = (I3 / "docs" / "studies" / "stage2-replay-gate-selected-design"
        / "THREE_ARM_EXPLORATORY_DEV_PLAN.json")
SCHEMA = "i3-stage2-1-three-arm-exploratory-development-gr/v1"
PROTOCOL = "I3_STAGE2_THREE_ARM_EXPLORATORY_DEVELOPMENT_20261110"
START = 360000
UNITS = 64
HORIZON = 400
COHORT = "development"
ARMS = ("reference", "p13_replay_gate_v1",
        "p13_replay_gate_random_equal_mean_v1")
CLAIM_BRANCH = "custody/i3-three-arm-development-64-20261110-claimed"
EVIDENCE_BRANCH = "evidence/i3-three-arm-development-64-20261110-originals"


def _hash(value) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()).hexdigest()


def load_plan() -> dict:
    plan = json.loads(PLAN.read_text())
    expected = {
        "schema": "i3-stage2-1-three-arm-exploratory-dev/v1",
        "status": "PROSPECTIVELY_FROZEN_BEFORE_EXPOSURE",
        "protocol_id": PROTOCOL, "index_start": START, "units": UNITS,
        "lives": 3 * UNITS, "horizon": HORIZON, "cohort": COHORT,
        "arms": list(ARMS), "no_retry": True,
        "no_outcome_dependent_stopping": True,
        "no_replacing_failures": True,
        "scientific_registration": False,
        "selection_allowed": False, "validation_allowed": False,
        "reserve_allowed": False, "scientific_go": False,
        "witness_independent_external_attestation": False,
    }
    if any(plan.get(k) != v for k, v in expected.items()):
        raise PermissionError("three-arm prospective developmental scope altered")
    key = SAMPLE._key(plan["witness"])
    if (plan["witness"] == SAMPLE.PREVIEW_WITNESS or
            sha256(key).hexdigest() != plan["witness_sha256"]):
        raise PermissionError("invalid three-arm witness or old synthetic key")
    return plan


def cases() -> list[dict]:
    """Pure allocation; no World, no genome, no individual constructed."""
    plan = load_plan()
    key = SAMPLE._key(plan["witness"])
    units = [
        {"pair_id": f"three-dev-{i:06d}",
         "index": START + i,
         "family": SAMPLE._family(key, i),
         "world_seed": SAMPLE._seed(key, i, "world", SAMPLE.WORLD_BASE),
         "genome_seed": SAMPLE._seed(key, i, "genome", SAMPLE.GENOME_BASE),
         "life_seed": SAMPLE._seed(key, i, "life", SAMPLE.LIFE_BASE)}
        for i in range(UNITS)
    ]
    SAMPLE._check_separation(units)
    if len({r["world_seed"] for r in units}) != UNITS:
        raise ValueError("duplicate assigned World: no replacement")
    # Never mistake distinct sources for proven iid ecology, and never
    # reuse exact original B1 DEVELOPMENT or public technical seeds.
    from . import stage2_b1_development as OLD
    old = OLD.cases()[::2]
    public = SAMPLE.preview(SAMPLE.PREVIEW_WITNESS)["proposed_units"]
    for key_name in ("world_seed", "genome_seed", "life_seed"):
        original_values = {r[key_name] for r in old}
        original_values.update(r[key_name] for r in public)
        if original_values & {r[key_name] for r in units}:
            raise ValueError("colliding historical or PUBLIC synthetic seed; no reroll")
    return [{**r, "cohort": COHORT, "policy": arm}
            for r in units for arm in ARMS]


def match_case(case: dict, fingerprint: str):
    if type(case) is not dict or type(case.get("index")) is not int:
        raise PermissionError("new three-arm developmental case invalid")
    offset = case["index"] - START
    if not 0 <= offset < UNITS or case.get("policy") not in ARMS:
        raise PermissionError("outside three-arm frozen developmental allocation")
    expected = cases()[3 * offset + ARMS.index(case["policy"])]
    if case != expected or case["cohort"] != COHORT:
        raise PermissionError("tampered three-arm developmental case")
    if fingerprint != SOURCE.source_fingerprint():
        raise PermissionError("three-arm developmental source fingerprint mismatch")


def _run_case(scheduled, fingerprint):
    def run(case):
        match_case(case, fingerprint)
        offset = case["index"] - START
        if case != scheduled[3 * offset + ARMS.index(case["policy"])]:
            raise PermissionError("original case not in fixed three-arm order")
        spec = SPECS._construct_f0_spec(case["family"], case["world_seed"])
        ticket = GUARD.admit_three_arm_newworld_development(
            case=case, spec=spec, transport_fingerprint=fingerprint)
        life = run_life(
            generation_zero(case["genome_seed"]), spec, case["life_seed"],
            HORIZON, protocol=PROTOCOL, decision_policy=case["policy"],
            admission=(None if case["policy"] == "reference" else ticket),
        )
        life["admission_receipt"] = ticket.receipt()
        return life
    return run


def _reduce_row(identity, life, fingerprint):
    m = life["manifest"]
    r = life["admission_receipt"]
    c = life["cognitive_accounting"]
    n = life["steps_lived"]
    policy = m.get("experimental_policy", {}).get("name", "reference")
    is_gate = identity["policy"] != "reference"
    checks = {
        "assigned_index": identity["cohort"] == COHORT and
                          START <= identity["index"] < START + UNITS,
        "paid_energy": c["totals"]["energy"]["unpaid"] <= 1e-12,
        "paid_vigilance": c["totals"]["vigilance"]["unpaid"] <= 1e-12,
        "no_shortfall": c["shortfall_steps"] == 0,
        "settled": c["status"] == "SETTLED_FOR_DECLARED_WORK",
        "horizon": type(n) is int and 1 <= n <= HORIZON,
        "terminal": life["terminal"] in ("dead", "censored"),
        "terminal_censoring": life["terminal"] != "censored" or n == HORIZON,
        "policy": policy == identity["policy"],
        "gate_summary": ("replay_gate" in life) == is_gate,
        "ticket_cohort": r["cohort"] == COHORT,
        "ticket_index_family": r["index"] == identity["index"] and
                               r["family"] == identity["family"],
        "ticket_world": r["world_seed"] == identity["world_seed"] and
                        r["world_sha256"] == m["world_sha256"] and
                        r["world_name"] == life["world"],
        "source": r["transport_fingerprint"] == fingerprint,
        "life_seed": m["life_seed"] == identity["life_seed"],
        "valid_replay_count": type(c["replays_executed"]) is int and
                              c["replays_executed"] >= 0,
    }
    schedule = None
    if identity["policy"] == ARMS[2]:
        schedule = life["replay_gate"].get("random_schedule", {})
        draws = schedule.get("draws_funded")
        nominal = schedule.get("nominal_replays_scheduled")
        eligible = schedule.get("eligible_replays_scheduled")
        paid = schedule.get("actual_replays_paid")
        ordinals = schedule.get("lived_sleep_ordinals")
        valid = all(type(v) is int and v >= 0 for v in
                    (draws, nominal, eligible, paid, ordinals))
        checks["random_receipt"] = (
            valid and 6 * draws <= nominal <= 7 * draws and
            0 <= paid <= eligible <= nominal and
            paid == c["replays_executed"] and
            draws <= ordinals <= life["actions"].get("dormir", 0) and
            schedule.get("mean_numerator") == 5532 and
            schedule.get("mean_denominator") == 867)
    if not all(checks.values()):
        raise ValueError("invalid three-arm original: " +
                         ",".join(k for k,v in checks.items() if not v))
    return {
        **identity,
        "terminal": life["terminal"],
        "steps_lived": n,
        "death_causes": life["death_causes"],
        "dead_at_400": life["terminal"] == "dead" and n == HORIZON,
        "paid_energy": c["totals"]["energy"]["paid"],
        "paid_vigilance": c["totals"]["vigilance"]["paid"],
        "replays_paid": c["replays_executed"],
        "sleep_steps": life["actions"].get("dormir", 0),
        "inactive_steps": c["inactive_steps"],
        "random_schedule": (None if schedule is None else {
            k: schedule[k] for k in (
                "draws_funded","nominal_replays_scheduled",
                "eligible_replays_scheduled","actual_replays_paid",
                "lived_sleep_ordinals",
            )}),
        "world_sha256": m["world_sha256"],
        "genome_sha256": _hash(m["genome"]),
        "source_sha256": m["source"]["sha256"],
    }


def analyze(scheduled, rows):
    """Complete finite matched original readout, never confirmatory NI."""
    if len(scheduled) != 3 * UNITS or len(rows) != len(scheduled):
        raise ValueError("missing or duplicate assigned original: NO_VERDICT")
    triples = []
    for i in range(UNITS):
        triple = rows[3*i:3*i+3]
        selected = scheduled[3*i:3*i+3]
        for row, expected in zip(triple, selected):
            if any(row.get(key) != expected[key] for key in (
                    "pair_id","index","cohort","family","policy",
                    "world_seed","genome_seed","life_seed")):
                raise ValueError("three-arm row identity/order mismatch")
        if any(len({row[k] for row in triple}) != 1 for k in (
                "world_sha256","genome_sha256","life_seed","source_sha256")):
            raise ValueError("three-arm source/World/genome not matched")
        triples.append(triple)
    def by_arm(blocks):
        out = {}
        n = len(blocks)
        for j, arm in enumerate(ARMS):
            subset = [trio[j] for trio in blocks]
            random_rows = [row["random_schedule"] for row in subset
                           if row["random_schedule"] is not None]
            totals = {
                "units": n, "horizon_survivors": sum(
                    row["terminal"] == "censored" for row in subset),
                "deaths_at_horizon": sum(row["dead_at_400"] for row in subset),
                "mean_lived_steps": sum(row["steps_lived"] for row in subset) / n,
                "mean_energy_paid_per_assigned_life":
                    sum(row["paid_energy"] for row in subset) / n,
                "mean_vigilance_paid_per_assigned_life":
                    sum(row["paid_vigilance"] for row in subset) / n,
                "mean_replays_paid_per_assigned_life":
                    sum(row["replays_paid"] for row in subset) / n,
                "mean_sleep_steps_per_assigned_life":
                    sum(row["sleep_steps"] for row in subset) / n,
            }
            if random_rows:
                totals["random_schedule_per_assigned_life"] = {
                    k: sum(r[k] for r in random_rows) / n
                    for k in ("draws_funded","nominal_replays_scheduled",
                              "eligible_replays_scheduled","actual_replays_paid",
                              "lived_sleep_ordinals")}
            out[arm] = totals
        return out

    def contrasts(blocks):
        results = {}
        for label, a, b in (("GATE_MINUS_RANDOM",1,2),
                            ("GATE_MINUS_FIXED",1,0),
                            ("RANDOM_MINUS_FIXED",2,0)):
            g = [x[a] for x in blocks]
            f = [x[b] for x in blocks]
            ga = [x["terminal"] == "censored" for x in g]
            fb = [x["terminal"] == "censored" for x in f]
            plus = sum(aa and not bb for aa,bb in zip(ga,fb))
            minus = sum(bb and not aa for aa,bb in zip(ga,fb))
            results[label] = {
                "units": len(blocks), "both_survive": sum(
                    aa and bb for aa,bb in zip(ga,fb)),
                "target_only_survives": plus,
                "comparator_only_survives": minus,
                "neither_survives": sum(
                    not aa and not bb for aa,bb in zip(ga,fb)),
                "paired_risk_difference": (plus-minus)/len(blocks),
                "mean_lived_step_difference":
                    sum(aa["steps_lived"]-bb["steps_lived"]
                        for aa,bb in zip(g,f))/len(blocks),
                "target_shorter_lived": sum(
                    aa["steps_lived"] < bb["steps_lived"] for aa,bb in zip(g,f)),
                "target_longer_lived": sum(
                    aa["steps_lived"] > bb["steps_lived"] for aa,bb in zip(g,f)),
            }
        return results

    family_blocks = {family: [t for t in triples if t[0]["family"]==family]
                     for family in SAMPLE.FAMILIES}
    if any(not blocks for blocks in family_blocks.values()):
        raise ValueError("unexpected empty F0 family; no family exclusion")
    overall = contrasts(triples)
    primary = overall["GATE_MINUS_RANDOM"]
    lower = EXACT.exact_paired_lower_bound(
        pairs=UNITS, gate_only=primary["target_only_survives"],
        fixed_only=primary["comparator_only_survives"],
        alpha=.05)["simultaneous_one_sided_lower_bound"]
    return {
        "schema": SCHEMA,
        "status": "COMPLETE_EXPLORATORY_DEVELOPMENT_ONLY",
        "primary": "GATE_MINUS_RANDOM",
        "overall_contrasts": overall,
        "by_arm": by_arm(triples),
        "by_family": {family:{
            "contrasts":contrasts(blocks), "by_arm":by_arm(blocks)}
            for family,blocks in family_blocks.items()},
        "conditional_iid_primary_lower_bound_unattested": lower,
        "external_iid_or_ecological_sampling_attestation": False,
        "scientific_noninferiority_margin_approved": False,
        "selection_validation_reserve_executed": False,
        "no_transfer_beyond_known_F0": True,
        "scientific_verdict": "NOT_ISSUED",
    }


def _trusted_source_claim():
    """Runs only in one trusted-main Actions push after exclusive remote claim."""
    if (os.getenv("GITHUB_EVENT_NAME") != "push" or
            os.getenv("GITHUB_REF") != "refs/heads/main" or
            os.getenv("GITHUB_RUN_ATTEMPT") != "1" or
            os.getenv("I3_THREE_ARM_CLAIM_BRANCH") != CLAIM_BRANCH):
        raise PermissionError("three-arm DEVELOPMENT opens only after one trusted-main claim")
    source = os.getenv("GITHUB_SHA","")
    if len(source) != 40 or not all(ch in "0123456789abcdef" for ch in source):
        raise PermissionError("missing exact main source lock")
    result = subprocess.run(
        ["git","ls-remote","--heads","origin",CLAIM_BRANCH],
        capture_output=True,text=True,check=True)
    if not result.stdout.strip():
        raise PermissionError("global claim branch missing before first World")
    if EVIDENCE_BRANCH in subprocess.run(
        ["git","ls-remote","--heads","origin",EVIDENCE_BRANCH],
        capture_output=True,text=True,check=True).stdout:
        raise PermissionError("three-arm scientific original evidence already exists")
    if subprocess.run(["git","rev-parse","HEAD"],
                      capture_output=True,text=True,check=True).stdout.strip() != source:
        raise PermissionError("source commit not trusted exact main SHA")
    if subprocess.run(["git","status","--porcelain"],
                      capture_output=True,text=True,check=True).stdout.strip():
        raise PermissionError("source working tree is dirty before G")
    return source


def execute(destination) -> dict:
    source = _trusted_source_claim()
    root = Path(destination).resolve()
    if root.exists() and any(root.iterdir()):
        raise PermissionError("local three-arm original archive already consumed")
    root.mkdir(parents=True, exist_ok=True)
    frozen = cases()
    fingerprint = SOURCE.source_fingerprint()
    claim = {
        "schema": SCHEMA + "/source-claim",
        "status":"CONSUMED_BEFORE_FIRST_BIRTH",
        "source_sha": source,
        "source_fingerprint": fingerprint,
        "plan_sha256": sha256(PLAN.read_bytes()).hexdigest(),
        "claim_branch": CLAIM_BRANCH, "evidence_branch": EVIDENCE_BRANCH,
        "units": UNITS, "lives": len(frozen), "no_retry": True,
        "scientific_inference_authorized": False,
    }
    (root/"SOURCE_LOCK.json").write_text(json.dumps(claim,sort_keys=True,indent=2)+"\n")
    originals = root/"originals"
    g = TP.generate(frozen, _run_case(frozen,fingerprint), originals)
    report = {
        "schema": SCHEMA, "status":"GENERATION_INCOMPLETE_NO_RETRY",
        "phase_G":g["status"],"generated":g["generated"],
        "planned":len(frozen),"phase_R":None,"reduced":0,
        "source_sha":source,"source_fingerprint":fingerprint,
        "plan_sha256":claim["plan_sha256"],
        "no_retry":True,"scientific_verdict":"NOT_ISSUED",
    }
    if g["status"] != "GENERATED":
        report["failure"] = g["failure"]
    else:
        r = TP.reduce(originals,lambda identity,life:
                      _reduce_row(identity,life,fingerprint))
        report["phase_R"] = r["status"]
        if r["status"] != "COMPLETE":
            report["status"] = "REDUCTION_DEFECT_PENDING_REPAIR"
            report["failure"] = r.get("failure")
        else:
            report["reduced"] = len(r["rows"])
            report["analysis"] = analyze(frozen,r["rows"])
            report["status"] = "COMPLETE_EXPLORATORY_DEVELOPMENT_ONLY"
            (root/"REDUCED_ROWS.json").write_text(
                json.dumps(r["rows"],sort_keys=True,indent=2)+"\n")
    (root/"EXECUTION_REPORT.json").write_text(
        json.dumps(report,sort_keys=True,indent=2)+"\n")
    return report


def main(argv=None):
    argv = sys.argv if argv is None else argv
    if len(argv)!=3 or argv[1]!="execute":
        raise SystemExit("usage: python -m i3.lab.stage2_three_arm_development execute FRESH_ARCHIVE_DIR")
    report=execute(argv[2])
    print(json.dumps({k:v for k,v in report.items() if k!="failure"},
                     sort_keys=True,indent=2))
    if report["status"]!="COMPLETE_EXPLORATORY_DEVELOPMENT_ONLY":
        raise SystemExit("three-arm exploratory failure; originals retained; NO RETRY")


if __name__ == "__main__":
    main()
