"""Old-source verified next-living-action versus DETACHED alternative.

READ ONLY. First verify every original compressed and uncompressed SHA
against the exact historical source via its independent original audit,
then interpret only the already-reduced, integrity-checked witness.
Never instantiate World, run_life, Mind, or a second counterfactual life.

No new delivered/discarded readout comparison is constructed here:
the historical study has a DIFFERENT replay-content treatment.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from pathlib import Path
import json
import sys

from . import stage2_next_decision_24_original_audit as ORIGINAL

SCHEMA = "i3-stage2.1-archived-next-action-actual-vs-detached-original-bridge/v1"
ARCHIVE_COMMIT = "20ca7efbf7797fa7b1f12983ce68906b754b312c"
CHOICE_KEYS = {
    "priority_action", "priority_param", "priority_option",
    "random_action", "random_param", "random_option",
    "same_admitted_action_and_param", "same_decision_option",
    "priority_work", "random_work",
    "random_branch_matches_actual_live_decision_and_work",
    "observer_extra_physical_cost",
}
WORK_KEYS = {"cycles", "simulated_steps", "memory_items", "replays"}


def _require(condition, message):
    if not condition:
        raise ValueError(message)


def _is_action_pair(action, param):
    if action is not None and type(action) is not str:
        return False
    return param is None or type(param) is str


def _classify_verified_rows(rows):
    """Pure *internal* classifier. Call ONLY after ORIGINAL.audit(root) PASS.

    Unit-test fixtures for this helper are never verified originals; only
    audit(root) can create the authenticated archive summary.
    """
    _require(type(rows) is list and len(rows) == 2 * ORIGINAL.PAIRS,
             "24 complete matched source pairs required")
    counts = Counter()
    families = {
        x: {"assigned": 0, "no_different_fork": 0,
            "living_random_next_claim": 0,
            "different_detached_priority_alternative": 0}
        for x in ORIGINAL.FAMILIES
    }
    for i in range(ORIGINAL.PAIRS):
        priority, random = rows[2*i:2*i+2]
        _require(
            type(priority) is dict and type(random) is dict
            and (priority.get("policy"), random.get("policy"))
                == ORIGINAL.POLICIES
            and priority.get("pair_id") == random.get("pair_id")
                == f"next-decision-{i:06d}"
            and priority.get("index") == random.get("index")
                == 560000 + i,
            "archive pairing and policy order changed")
        family = random.get("family")
        _require(
            family == priority.get("family") and family in ORIGINAL.FAMILIES,
            "old family source changed")
        _require(priority.get("next_decision_receipt") is None,
                 "priority old arm cannot gain new observer receipts")
        _require(priority.get("terminal") in ("dead", "censored")
                 and random.get("terminal") in ("dead", "censored"),
                 "both original observed lives must remain assigned")
        families[family]["assigned"] += 1
        witness = random.get("next_decision_receipt")
        _require(type(witness) is dict, "missing old random source observer")
        status = witness.get("status")
        event = witness.get("first_fork")
        if status == "NO_DIFFERENT_FUNDED_REPLAY":
            _require(event is None, "no-fork label has an invented future")
            counts["no_different_fork"] += 1
            families[family]["no_different_fork"] += 1
            continue
        _require(type(event) is dict, "different replay requires source event")
        counts["different_funded_replay"] += 1
        next_choice = event.get("next_decision")
        if status == "FIRST_FORK_WITHOUT_SUBSEQUENT_LIVE_DECISION":
            _require(next_choice is None, "no-next label contains a future")
            counts["different_fork_but_no_next"] += 1
            continue
        _require(status == "FIRST_FORK_AND_NEXT_DECISION_CAPTURED"
                 and type(next_choice) is dict,
                 "unrecognized next actual first-person witness status")
        _require(set(next_choice) == CHOICE_KEYS,
                 "old next decision schema changed or invented execution field")
        _require(next_choice["random_branch_matches_actual_live_decision_and_work"] is True,
                 "original random detached branch does not match living Mind")
        _require(next_choice["observer_extra_physical_cost"] is False,
                 "archived detached observation was not free to living body")
        for label in ("priority", "random"):
            _require(
                _is_action_pair(next_choice[f"{label}_action"],
                                next_choice[f"{label}_param"]),
                "invalid actual/detached action label")
            work = next_choice[f"{label}_work"]
            _require(
                type(work) is dict and set(work) == WORK_KEYS
                and all(type(v) is int and v >= 0 for v in work.values()),
                "forged or missing detached decision work")
        same = (next_choice["priority_action"], next_choice["priority_param"]) == (
            next_choice["random_action"], next_choice["random_param"])
        _require(next_choice["same_admitted_action_and_param"] is same,
                 "detached-to-living comparison boolean forged")
        _require(
            next_choice["same_decision_option"] is (
                next_choice["priority_option"] == next_choice["random_option"]),
            "option parity label forged")
        # Only random's chosen action was matched against the living Mind in
        # the verified original observer. Priority stays detached.
        counts["living_random_next_claim"] += 1
        counts["priority_detached_next_claim"] += 1
        families[family]["living_random_next_claim"] += 1
        if same:
            counts["same_detached_priority_and_living_random_action"] += 1
        else:
            counts["different_detached_priority_alternative"] += 1
            families[family]["different_detached_priority_alternative"] += 1

    summary = {
        "assigned_original_pairs": ORIGINAL.PAIRS,
        "different_funded_replay": counts["different_funded_replay"],
        "no_different_fork": counts["no_different_fork"],
        "different_fork_but_no_next": counts["different_fork_but_no_next"],
        "living_random_next_claim": counts["living_random_next_claim"],
        "priority_detached_next_claim": counts["priority_detached_next_claim"],
        "same_detached_priority_and_living_random_action":
            counts["same_detached_priority_and_living_random_action"],
        "different_detached_priority_alternative":
            counts["different_detached_priority_alternative"],
        "priority_alternative_executed_in_world": 0,
        "by_family": families,
    }
    _require(
        (summary["different_funded_replay"] == 20
         and summary["no_different_fork"] == 4
         and summary["different_fork_but_no_next"] == 0
         and summary["living_random_next_claim"] == 20
         and summary["priority_detached_next_claim"] == 20
         and summary["same_detached_priority_and_living_random_action"] == 19
         and summary["different_detached_priority_alternative"] == 1
         and summary["by_family"]["stable"]["different_detached_priority_alternative"] == 1
         and tuple(summary["by_family"][family]["assigned"]
                   for family in ORIGINAL.FAMILIES) == (8, 10, 6)),
        "historical frozen 24-pair witness counts changed")
    return summary


def audit(root):
    """Archive verification precedes ANY interpretation of reduced records."""
    base = Path(root).resolve()
    # Trust neither an unverified standalone REDUCED_ROWS.json nor a
    # caller's claimed "sha256": the existing archive audit checks all 48
    # compressed/uncompressed actual original bytes and reductions.
    attested = ORIGINAL.audit(base)
    _require(attested["status"] == "READ_ONLY_ALL_ORIGINALS_AND_REDUCTIONS_PASS"
             and attested["packed_sha_verified"] == 48
             and attested["unpacked_sha_verified"] == 48
             and attested["complete_matched_pairs"] == 24
             and attested["manifest_sha256"] == ORIGINAL.MANIFEST_SHA,
             "original source integrity not fully authenticated")
    rows = json.loads((base / "REDUCED_ROWS.json").read_bytes())
    # Re-reading a previously audited reduced file can race a concurrent
    # writer; require a bounded local snapshot and re-verify content by
    # reusing the canonical original summary on the same parsed rows.
    audit_summary = ORIGINAL._summaries(rows)
    _require(audit_summary["mechanism"] == attested["primary"],
             "verified archive reduced rows changed between reads")
    classifications = _classify_verified_rows(rows)
    payload = {
        "schema": SCHEMA,
        "status": "OLD_ORIGINALS_VERIFIED_ACTUAL_RANDOM_VS_DETACHED_PRIORITY",
        "archived_original_commit_expected": ARCHIVE_COMMIT,
        "archived_original_source_sha": ORIGINAL.SOURCE,
        "archive_manifest_sha256": ORIGINAL.MANIFEST_SHA,
        "existing_original_packed_sha_verified": 48,
        "existing_original_unpacked_sha_verified": 48,
        "existing_original_archive_content_verified": True,
        **classifications,
        "historical_observer_random_branch_equals_living_choice": True,
        "priority_branch_is_unexecuted_detached_hypothesis": True,
        "new_readout_delivered_into_living_decision": False,
        "new_paid_discarded_readout_treatment": False,
        "eligible_for_new_visible_discard_causal_comparison": False,
        "new_born_originals": 0,
        "new_worlds_opened": 0,
        "scientific_lives": 0,
        "scientific_verdict": "NOT_ISSUED",
        "causal_information_benefit": None,
        "survival_mediation": None,
        "cpu_to_body_calibrated": False,
        "stage2_2_go": False,
    }
    # Deterministic checksum over aggregate only, no individual data output.
    payload["aggregate_report_sha256"] = sha256(json.dumps(
        payload, sort_keys=True, separators=(",", ":"),
        allow_nan=False).encode("utf-8")).hexdigest()
    return payload


def main(argv=None):
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 1:
        raise SystemExit("usage: python -m i3.lab.stage2_next_action_original_archive_bridge EVIDENCE_ROOT")
    print("I3_ARCHIVED_NEXT_ACTION_BRIDGE_RESULT="+json.dumps(
        audit(args[0]), sort_keys=True))


if __name__ == "__main__":
    main()
