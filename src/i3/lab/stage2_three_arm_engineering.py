"""Stage-2.1 new-world FIXED/GATE/paid-RANDOM engineering transport.

Fixed units 96..119 of the PUBLIC synthetic B1 allocation are distinct from
the previously used engineering first 96 and from the spent scientific B1.
These are 72 real, temporary, NON-EVIDENTIARY technical lives. The G/R
rehearsal returns structure only, including physical random-schedule
accounting invariants, never individual survival or behavior outcomes.
"""
from __future__ import annotations

from hashlib import sha256
import json
import sys

from . import stage2_survival_b1_sampling as SAMPLE
from . import stage2_survival_b1_worldspec_audit as SPECS
from . import stage2_survival_b1_engineering as SOURCE
from . import stage2_admission as GUARD
from . import two_phase_panel as TP
from ..modules.genome import generation_zero
from ..runtime.life import run_life

SCHEMA = "i3-stage2-1-three-arm-newworld-engineering-gr/v1"
PROTOCOL = "STAGE2_THREE_ARM_UNUSED_PUBLIC_B1_ENGINEERING_ONLY"
START = 96
PAIRS = 24
HORIZON = 400
ARMS = ("reference", "p13_replay_gate_v1",
        "p13_replay_gate_random_equal_mean_v1")
COHORT = "engineering"


def cases() -> list[dict]:
    """Exactly 24 unused fixed synthetic allocation rows, 3 arms per pair."""
    proposal = SAMPLE.preview(SAMPLE.PREVIEW_WITNESS)
    SAMPLE.verify_preview(proposal, SAMPLE.PREVIEW_WITNESS)
    picked = proposal["proposed_units"][START:START + PAIRS]
    if len(picked) != PAIRS:
        raise ValueError("incomplete 3-arm technical allocation")
    result = [
        {
            "pair_id": unit["pair_id"],
            "index": unit["ordinal"],
            "cohort": COHORT,
            "family": unit["family"],
            "world_seed": unit["world_seed"],
            "genome_seed": unit["genome_seed"],
            "life_seed": unit["life_seed"],
            "policy": arm,
        }
        for unit in picked for arm in ARMS
    ]
    if len(result) != 3 * PAIRS:
        raise ValueError("incomplete engineering triplet allocation")
    return result


def _match_case(case: dict, scheduled: list, fingerprint: str):
    # All checks occur before constructing the World or newborn genome.
    if type(case) is not dict or type(case.get("index")) is not int:
        raise PermissionError("invalid three-arm engineering case")
    offset = case["index"] - START
    if not 0 <= offset < PAIRS or case.get("policy") not in ARMS:
        raise PermissionError("unallocated three-arm engineering case")
    expected = scheduled[3 * offset + ARMS.index(case["policy"])]
    if case != expected or case["cohort"] != COHORT:
        raise PermissionError("three-arm case identity or policy mismatch")
    if fingerprint != SOURCE.source_fingerprint():
        raise PermissionError("three-arm source fingerprint mismatch")


def _run_case(scheduled: list, fingerprint: str):
    def run(case: dict) -> dict:
        _match_case(case, scheduled, fingerprint)
        spec = SPECS._construct_f0_spec(case["family"], case["world_seed"])
        ticket = GUARD.admit_three_arm_newworld_engineering(
            case=case, spec=spec, transport_fingerprint=fingerprint)
        life = run_life(
            generation_zero(case["genome_seed"]), spec, case["life_seed"],
            HORIZON, protocol=PROTOCOL, decision_policy=case["policy"],
            admission=(None if case["policy"] == "reference" else ticket),
        )
        life["admission_receipt"] = ticket.receipt()
        return life
    return run


def _reduce_structural(identity, life):
    """R phase computes only transient provenance, never a biological verdict."""
    m = life["manifest"]
    return {
        "pair_id": identity["pair_id"],
        "policy": identity["policy"],
        "source_sha256": m["source"]["sha256"],
        "world_sha256": m["world_sha256"],
        "genome_sha256": sha256(json.dumps(
            m["genome"], sort_keys=True,
            separators=(",", ":")).encode()).hexdigest(),
        "life_seed": m["life_seed"],
    }


def _invariants(fingerprint: str):
    def check(identity: dict, life: dict) -> dict[str, bool]:
        receipt = life["admission_receipt"]
        ca = life["cognitive_accounting"]
        manifest = life["manifest"]
        gate = identity["policy"] != "reference"
        random_arm = identity["policy"] == ARMS[2]
        observed = manifest.get("experimental_policy", {}).get("name", "reference")
        replays = ca["replays_executed"]
        checks = {
            "paid_energy": ca["totals"]["energy"]["unpaid"] <= 1e-12,
            "paid_vigilance": ca["totals"]["vigilance"]["unpaid"] <= 1e-12,
            "no_shortfall": ca["shortfall_steps"] == 0,
            "settled": ca["status"] == "SETTLED_FOR_DECLARED_WORK",
            "within_horizon": type(life["steps_lived"]) is int
                              and 1 <= life["steps_lived"] <= HORIZON,
            "terminal_label": life["terminal"] in ("dead", "censored"),
            "censored_at_horizon": life["terminal"] != "censored"
                                   or life["steps_lived"] == HORIZON,
            "manifest_policy": observed == identity["policy"],
            "gate_presence": ("replay_gate" in life) == gate,
            "cohort": receipt["cohort"] == COHORT,
            "family_index": receipt["family"] == identity["family"]
                            and receipt["index"] == identity["index"],
            "world_binding": receipt["world_seed"] == identity["world_seed"]
                             and receipt["world_sha256"] == manifest["world_sha256"]
                             and receipt["world_name"] == life["world"],
            "source_binding": receipt["transport_fingerprint"] == fingerprint,
            "life_seed": manifest["life_seed"] == identity["life_seed"],
            "no_unknown_arm": identity["policy"] in ARMS,
        }
        if random_arm:
            schedule = life["replay_gate"].get("random_schedule", {})
            nominal = schedule.get("nominal_replays_scheduled")
            eligible = schedule.get("eligible_replays_scheduled")
            draws = schedule.get("draws_funded")
            sleep_ordinals = schedule.get("lived_sleep_ordinals")
            paid = schedule.get("actual_replays_paid")
            valid = all(type(v) is int and v >= 0 for v in (
                nominal, eligible, draws, sleep_ordinals, paid))
            checks.update({
                "random_receipt_present": valid,
                "random_count_bounds": valid and
                    6 * draws <= nominal <= 7 * draws,
                "random_nominal_eligible_paid": valid and
                    0 <= paid <= eligible <= nominal,
                "random_paid_equals_physical_replays": valid and
                    paid == replays,
                "random_draw_not_reached_unfunded_sleep": valid and
                    draws <= sleep_ordinals <= life["actions"].get("dormir", 0),
                "random_declared_original_mean": valid and
                    schedule.get("mean_numerator") == 5532 and
                    schedule.get("mean_denominator") == 867,
            })
        else:
            checks["random_receipt_absent"] = (
                not gate or "random_schedule" not in life["replay_gate"])
        return checks
    return check


def rehearse() -> dict:
    """Actual technical lives and sealed G/R, structural-only public receipt."""
    scheduled = cases()
    fingerprint = SOURCE.source_fingerprint()
    report = TP.sealed_rehearsal(
        scheduled, _run_case(scheduled, fingerprint),
        _reduce_structural, _invariants(fingerprint),
    )
    report.update({
        "runner": SCHEMA,
        "protocol_id": PROTOCOL,
        "cohort": COHORT,
        "source_fingerprint": fingerprint,
        "pair_count": PAIRS,
        "arms_per_pair": len(ARMS),
        "expected_worlds": PAIRS,
        "public_synthetic_source": True,
        "scientific_lives": 0,
        "survival_outcomes_disclosed": False,
        "scientific_admission": "CLOSED",
        "scientific_verdict": "NOT_ISSUED",
    })
    return report


def execute(*args, **kwargs):
    raise PermissionError("three-arm prospective scientific cohort is NOT admitted")


def main(argv=None):
    argv = sys.argv if argv is None else argv
    if len(argv) != 2 or argv[1] != "rehearse":
        raise SystemExit("usage: python -m i3.lab.stage2_three_arm_engineering rehearse")
    print(json.dumps(rehearse(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
