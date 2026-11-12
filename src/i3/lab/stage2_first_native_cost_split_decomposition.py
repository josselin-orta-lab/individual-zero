"""Read-only retrospective arithmetic audit of #1353's FIRST native cost splits.

This reducer runs NO World or Mind. Original accepted CI output is preserved
as a derivative, NOT independent evidence. The 4-unit denominator includes
the negative/no-cost-split unit. See source-frozen preflight.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha1, sha256
import json
from math import isclose, isfinite
from pathlib import Path

from ..modules.body import BodyLaws, CognitiveWork, cognitive_cost

SCHEMA = "i3-stage2.1-first-native-cost-split-decomposition/v1"
SOURCE = (Path(__file__).resolve().parents[1] / "docs" / "studies"
          / "stage2-replay-gate-selected-design"
          / "STAGE2_FIRST_NATIVE_COST_SPLIT_SOURCE_2026-11-12.json")
SOURCE_BLOB_SHA1 = "2095495827d8764034c7e93c7b1f0679536d1e55"
SOURCE_RECEIPT_SHA256 = (
    "b0020b6c784b2a5d0306ba4cc5031a3fe4bbe86b998dce6efb17e5ebb17b22fa")
GRID = (("dev-open-field", 840061),
        ("dev-open-field", 840062),
        ("dev-failing-well", 840061),
        ("dev-failing-well", 840062))
# Original full-life totals can diverge AFTER the first physical cost split.
# Pin all four original accepted totals without claiming full-life parity.
ORIGINAL_FULL_LIFE_READ_TOTALS = ((120, 120), (105, 105),
                                  (119, 115), (141, 141))
TOL = 1e-10


def _hash(x):
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("utf-8")).hexdigest()


def _body(values):
    if type(values) is not list or len(values) != 5:
        raise ValueError("original five-channel body missing")
    if any(type(x) not in (int, float) or not isfinite(x)
           or not 0 <= x <= 100 for x in values):
        raise ValueError("invalid original body channel")
    return values


def _work(values):
    if type(values) is not dict or set(values) != {
            "cycles", "memory_items", "simulated_steps", "replays"}:
        raise ValueError("original native work shape changed")
    return CognitiveWork(**values)


def reduce_source(source):
    if type(source) is not dict or source.get("schema") != (
            "i3-stage2.1-first-native-cost-split-source-derivative/v1"):
        raise ValueError("unrecognized archived exact-head receipt")
    s = source.get("source")
    if (type(s) is not dict or
            s.get("kind") != "EXTRACT_FROM_ACCEPTED_CI_NOT_INDEPENDENT" or
            s.get("run") != 43292431577 or
            s.get("python311_job") != 131442053760 or
            s.get("python312_job") != 131442053556 or
            s.get("source_head") !=
            "f424be6b0c90d0bdd784776411a1764d2cdd193e" or
            s.get("source_aggregate_sha256") != SOURCE_RECEIPT_SHA256):
        raise ValueError("wrong upstream exact-source CI")
    summary = source.get("original_summary")
    if (type(summary) is not dict or
            summary.get("status") !=
            "PAID_RESIDUAL_READOUT_STOP_NATIVE_COST_CONFOUND" or
            summary.get("engineering_worlds") != 8 or
            summary.get("engineering_world_steps") != 96 or
            summary.get("private_readout_funded_total") != 966 or
            summary.get("private_error_stores_funded_total") != 96 or
            summary.get("first_differences") != 0 or
            summary.get("early_native_cost_confounds") != 3 or
            summary.get("scientific_lives") != 0 or
            summary.get("scientific_verdict") != "NOT_ISSUED"):
        raise ValueError("source cohort summary altered")
    original = source.get("pairs")
    if type(original) is not list or len(original) != 4:
        raise ValueError("must retain exactly four fixed technical pairs")
    laws = BodyLaws()  # unchanged, original native model rates
    rows = []
    for x, (name, seed) in zip(original, GRID):
        if (type(x) is not dict or x.get("world") != name or
                type(x.get("seed")) is not int or x["seed"] != seed or
                x.get("visible_steps") != 12 or x.get("discard_steps") != 12 or
                x.get("visible_error_records") != 12 or
                x.get("discard_error_records") != 12 or
                x.get("first_motor_difference") is not None):
            raise ValueError("modified original fixed-unit denominator")
        vr, dr = x.get("visible_funded_reads"), x.get("discard_funded_reads")
        expected_vr, expected_dr = ORIGINAL_FULL_LIFE_READ_TOTALS[len(rows)]
        if (type(vr) is not int or type(dr) is not int
                or (vr, dr) != (expected_vr, expected_dr)):
            raise ValueError("original full-life read totals changed")
        _body(x.get("visible_end_body"))
        _body(x.get("discard_end_body"))
        f = x.get("first_cost_confound")
        if f is None:
            rows.append({
                "world": name, "seed": seed,
                "classification": "NO_OBSERVED_FIRST_COST_SPLIT",
                "original_end_bodies_equal":
                    x["visible_end_body"] == x["discard_end_body"],
                "first_split_step": None, "native_motor": None,
                "full_life_optional_read_totals": [vr, dr],
                "additional_competition_cycles": None,
                "extra_native_energy_bill": None,
                "extra_native_vigilance_bill": None,
                "max_body_bill_residual": None,
            })
            if x["visible_end_body"] != x["discard_end_body"]:
                raise ValueError("claimed no split but original end bodies differ")
            continue
        if (type(f) is not dict or type(f.get("step")) is not int or
                not 1 <= f["step"] <= 12 or
                f.get("read_work_matched") is not True or
                type(f.get("native_motor")) is not list or
                len(f["native_motor"]) != 2 or
                f["native_motor"][0] not in (
                    "se_deplacer","collecter","manger","boire","dormir","attendre")):
            raise ValueError("forged first same-motor cost split")
        v, d = _work(f.get("visible_decision_work")), _work(
            f.get("discard_decision_work"))
        for c in ("memory_items", "simulated_steps", "replays"):
            if getattr(v, c) != getattr(d, c):
                raise ValueError("not a native cycle-only cost split")
        diff = v.cycles - d.cycles
        if diff <= 0:
            raise ValueError("not a positive previously observed native cycle split")
        ev, vv = cognitive_cost(laws, v)
        ed, vd = cognitive_cost(laws, d)
        extra_e, extra_v = ev-ed, vv-vd
        if (not isclose(extra_e, laws.energy_per_cycle * diff,
                        rel_tol=0, abs_tol=TOL) or
                not isclose(extra_v, laws.vigilance_per_cycle * diff,
                            rel_tol=0, abs_tol=TOL)):
            raise ValueError("native currency rate does not reconcile")
        body_v = _body(f.get("visible_after_storage_body"))
        body_d = _body(f.get("discard_after_storage_body"))
        actual = [a-b for a,b in zip(body_v,body_d)]
        predicted = [-extra_e, 0., 0., 0., -extra_v]
        residual = max(abs(a-b) for a,b in zip(actual,predicted))
        if not isfinite(residual) or residual > TOL:
            raise ValueError("first split body has unexplained non-cost effect")
        rows.append({
            "world": name, "seed": seed,
            "classification": "FIRST_NATIVE_CYCLE_COST_SPLIT_RECONCILED",
            "original_end_bodies_equal":
                x["visible_end_body"] == x["discard_end_body"],
            "first_split_step": f["step"], "native_motor": f["native_motor"],
            "full_life_optional_read_totals": [vr, dr],
            "original_visible_decision_work": asdict(v),
            "original_discard_decision_work": asdict(d),
            "additional_competition_cycles": diff,
            "extra_native_energy_bill": extra_e,
            "extra_native_vigilance_bill": extra_v,
            "actual_five_channel_body_difference": actual,
            "expected_five_channel_body_difference": predicted,
            "max_body_bill_residual": residual,
        })
    n = sum(x["classification"] ==
            "FIRST_NATIVE_CYCLE_COST_SPLIT_RECONCILED" for x in rows)
    if n != 3 or len(rows) != 4:
        raise ValueError("original exact-source count changed")
    return {
        "schema": SCHEMA,
        "status": "FIRST_NATIVE_COST_SPLIT_ACCOUNTING_PASS",
        "analysis_timing": "POSTHOC_AFTER_COST_CONFOUND_KNOWN",
        "original_ci": 43292431577,
        "original_aggregate_sha256": SOURCE_RECEIPT_SHA256,
        "source_derivative_git_blob_sha1": SOURCE_BLOB_SHA1,
        "technical_paired_units": len(rows),
        "original_engineering_world_steps_rerun": 0,
        "new_worlds": 0, "new_scientific_lives": 0,
        "first_reconciled_cost_splits": n,
        "no_first_split_units": len(rows)-n,
        "clean_first_motor_mediations": 0,
        "native_model_energy_per_cycle": laws.energy_per_cycle,
        "native_model_vigilance_per_cycle": laws.vigilance_per_cycle,
        "physical_CPU_joules_calibrated": False,
        "adaptive_information_value_demonstrated": False,
        "scientific_verdict": "NOT_ISSUED",
        "structural_sha256": _hash(rows), "rows": rows,
    }


def audit():
    raw = SOURCE.read_bytes()
    blob = sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if blob != SOURCE_BLOB_SHA1:
        raise ValueError("archived derivative bytes changed")
    return reduce_source(json.loads(raw.decode("utf-8")))


if __name__ == "__main__":
    r = audit()
    print("I3_FIRST_NATIVE_COST_SPLIT="+json.dumps(
        r, sort_keys=True, separators=(",", ":")))
