"""Source-bound, original-only Stage-2 causal-eligibility audit.

The only admitted evidence is 96 immutable content original lives and 48
immutable next-decision original lives. Run BOTH existing original auditors
before reading any old-life fields for classification. This does NOT create
a World, run Mind, reproduce a life or approve a prospective study.

Protocol: studies/stage2-replay-gate-selected-design/
OLD_ORIGINALS_CAUSAL_READINESS_PREFLIGHT_2026-11-11.md
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

from . import stage2_content_48_original_audit as CONTENT
from . import stage2_next_decision_24_original_audit as NEXT

SCHEMA = "i3-stage2.1-exact-old-originals-causal-readiness-readonly/v1"
CONTENT_COMMIT = "459d0d9f90ea8edae95881d4e3110b91a24f85f5"
NEXT_COMMIT = "20ca7efbf7797fa7b1f12983ce68906b754b312c"
EXPECTED_ORIGINALS = 2 * (CONTENT.PAIRS + NEXT.PAIRS)
SOURCE_KIND = "IMMUTABLE_OLD_DEV_ORIGINALS_NOT_NEW_TREATMENT"
FORBIDDEN_NEW_SOURCE_FIELDS = frozenset((
    "paid_personal_information_delivery",
    "controller_readout_delivery",
    "source_independent_visible_vs_discard",
    "future_real_action_mediation",
    "causal_information_benefit",
))

def _require(value, reason):
    if not value:
        raise ValueError(reason)


def _scan_verified_originals(root, *, count, identity_prefix, next_receipt):
    """Private shape inventory: caller MUST have run the original auditor.

    Never use this helper as an independent proof of byte authenticity.
    The historical original auditor binds *both* packed and unpacked hashes,
    source lock, genotype, World, outcome, whole denominator and reduced rows.
    """
    root = Path(root).resolve()
    manifest = json.loads((root / "originals" / "MANIFEST.json").read_bytes())
    _require(len(manifest["files"]) == count, "different assigned old source")
    counts = Counter()
    for index, entry in enumerate(manifest["files"]):
        _require(entry["file"] == f"life-{index:03d}.json.gz",
                 "old original filename/order changed")
        original = json.loads(gzip.decompress(
            (root / "originals" / entry["file"]).read_bytes()))
        _require(original["identity"] == entry["identity"],
                 "reopened old identity differs from audited original")
        identity = original["identity"]
        _require(identity["pair_id"].startswith(identity_prefix),
                 "wrong old source label")
        expected_arm = CONTENT.POLICIES[index % 2]
        _require(identity["policy"] == expected_arm, "old arm ordering changed")
        life = original["life"]
        _require(type(life) is dict, "malformed old life")
        _require(not FORBIDDEN_NEW_SOURCE_FIELDS.intersection(life),
                 "new experimental delivery claim inserted in an old source")
        _require(life.get("terminal") in ("dead", "censored"),
                 "invalid observed old terminal status")
        _require(life.get("cognitive_accounting", {}).get("status") ==
                 "SETTLED_FOR_DECLARED_WORK", "unsettled old cognitive bill")
        counts["old_originals"] += 1
        trace = life.get("trace")
        if trace is not None:
            _require(type(trace) is list, "old native trace malformed")
            counts["originals_with_trace_field"] += 1
            counts["stored_trace_steps"] += len(trace)
        observer = life.get("observer_next_decision_replay")
        if next_receipt:
            if index % 2 == 1:
                _require(type(observer) is dict,
                         "missing historical random-arm observer")
                counts["detached_next_observer_originals"] += 1
                status = observer.get("status")
                if status == "FIRST_FORK_AND_NEXT_DECISION_CAPTURED":
                    event = observer.get("first_fork")
                    choice = event.get("next_decision") if type(event) is dict else None
                    _require(type(choice) is dict,
                             "historical next decision witness missing")
                    _require(choice.get(
                        "random_branch_matches_actual_live_decision_and_work"
                    ) is True, "old living random witness was not matched")
                    _require(choice.get("observer_extra_physical_cost") is False,
                             "old shadow observer mischaracterized as paid")
                    counts["historical_next_perception_with_shadow"] += 1
                    if choice["same_admitted_action_and_param"] is False:
                        counts["detached_alternative_motor_differences"] += 1
                elif status == "NO_DIFFERENT_FUNDED_REPLAY":
                    counts["old_no_fork"] += 1
                elif status == "FIRST_FORK_WITHOUT_SUBSEQUENT_LIVE_DECISION":
                    counts["old_fork_no_next"] += 1
                else:
                    raise ValueError("unknown old observer status")
            else:
                _require(observer is None, "historical priority arm gained observer")
        else:
            _require(observer is None,
                     "unexpected next-decision observer in old content-only study")
        counts["old_actual_executed_lives"] += 1

    # In the old original policies, there is no VISIBLE/PAID-DISCARD
    # additional-computation treatment. New fields cannot be fabricated by
    # reconstructing a trace or by labeling shadow motor work as physical.
    counts["new_paid_information_readout_deliveries"] = 0
    counts["new_equal_paid_visible_discard_pairs"] = 0
    counts["new_counterfactual_motors_executed_after_same_capture"] = 0
    counts["new_mediated_post_paid_learning_pair_outcomes"] = 0
    return dict(sorted(counts.items()))


def audit(content_root, next_root):
    """Only the two exact archived old evidence roots are admissible."""
    if Path(content_root).resolve() == Path(next_root).resolve():
        raise ValueError("two independent historical source roots required")
    # The independent old auditors must pass FIRST; no output on partial data.
    a = CONTENT.audit(content_root)
    b = NEXT.audit(next_root)
    for report, auditor, expected in (
        (a, CONTENT, 2 * CONTENT.PAIRS),
        (b, NEXT, 2 * NEXT.PAIRS),
    ):
        _require(
            report["status"] == "READ_ONLY_ALL_ORIGINALS_AND_REDUCTIONS_PASS"
            and report["source"] == auditor.SOURCE
            and report["manifest_sha256"] == auditor.MANIFEST_SHA
            and report["packed_sha_verified"] == expected
            and report["unpacked_sha_verified"] == expected
            and report["complete_matched_pairs"] == expected // 2
            and report["no_new_World_or_life"] is True
            and report["iid_attested"] is False
            and report["scientific_go"] is False,
            "old original auditor did not independently authenticate all lives"
        )
    _require(
        a["primary"]["both_survive"] == 16
        and a["primary"]["priority_only_survives"] == 1
        and a["primary"]["random_content_only_survives"] == 7
        and b["primary"]["assigned_pairs"] == 24
        and b["primary"]["first_different_funded_memory_fork"] == 20
        and b["primary"]["different_next_admitted_action_or_param"] == 1,
        "old historical result has been changed or misinterpreted"
    )
    shape_content = _scan_verified_originals(
        content_root, count=2 * CONTENT.PAIRS,
        identity_prefix="content-dev-", next_receipt=False)
    shape_next = _scan_verified_originals(
        next_root, count=2 * NEXT.PAIRS,
        identity_prefix="next-decision-", next_receipt=True)
    _require(shape_content["old_originals"] == 96
             and shape_next["old_originals"] == 48
             and shape_next["historical_next_perception_with_shadow"] == 20
             and shape_next["detached_alternative_motor_differences"] == 1
             and shape_next["old_no_fork"] == 4
             and shape_next.get("old_fork_no_next", 0) == 0,
             "old detached/living witness failed historical identity reconciliation")

    compact = {
        "schema": SCHEMA,
        "source_kind": SOURCE_KIND,
        "historical_source_commits": {
            "content_48": CONTENT_COMMIT,
            "next_decision_24": NEXT_COMMIT,
        },
        "source_manifest_sha256": {
            "content_48": CONTENT.MANIFEST_SHA,
            "next_decision_24": NEXT.MANIFEST_SHA,
        },
        "packed_and_unpacked_originals_verified": (
            a["packed_sha_verified"] + b["packed_sha_verified"]),
        "historical_born_lives_reverified": EXPECTED_ORIGINALS,
        "historical_complete_pairs": CONTENT.PAIRS + NEXT.PAIRS,
        "by_source": {
            "content_48": shape_content,
            "next_decision_24": shape_next,
        },
        "detached_alternative_action_count": 1,
        "actual_alternative_after_same_capture_executed": 0,
        "new_equal_paid_visible_discard_source": False,
        "new_action_relevant_paid_information_delivered": False,
        "new_post_paid_learning_outcome_caused_by_delivery": False,
        "causal_net_information_gain_identifiable": False,
        "old_original_bytes_changed": False,
        "new_worlds_opened": 0,
        "new_lives_created": 0,
        "iid_ecology_attested": False,
        "scientific_verdict": "NOT_ISSUED",
        "stage2_2_go": False,
        "eligibility": "OLD_ORIGINALS_INSUFFICIENT_FOR_PAID_INFORMATION_CAUSAL_TEST",
    }
    sha = sha256(json.dumps(compact, sort_keys=True, separators=(",", ":"),
                            allow_nan=False).encode("utf-8")).hexdigest()
    return {**compact, "aggregate_sha256": sha}


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 2:
        raise SystemExit(
            "usage: python -m i3.lab.stage2_old_original_causal_readiness "
            "CONTENT_48_EVIDENCE_DIR NEXT_DECISION_24_EVIDENCE_DIR")
    result = audit(args[0], args[1])
    print("I3_STAGE2_OLD_SOURCE_CAUSAL_READINESS=" +
          json.dumps(result, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
