"""A2-R cold 96-life postflight census: ECO-v1 and paired mechanism witnesses.

Never births individuals, modifies the engine, or issues a scientific GO.
The source checkout and original manifest/lock digests must be supplied from
independent custody; even matching digests do not prove the real Actions run.
Complete per-life M11 and 12-feature Q replay are required before scoring.
"""
from __future__ import annotations

import argparse
import json
from math import isfinite
from pathlib import Path
from statistics import mean

from i1_a2r_archive_guard import (
    HORIZON, MODES, ROLES, SEEDS, load_canonical_json,
    ordered_rows, verify_archive,
)
from i1_eco_metrics import evaluate_life

PARITY_FIELDS = (
    "initial_body", "initial_inventory", "initial_perception",
    "born_temperament", "world_config_sha256", "setpoints", "weights",
    "scales", "born_td", "born_td_evidence_scale",
    "stage8_evaluation", "stage11_intrinsic_weight",
    "stage11_geographic_novelty_weight",
    "stage11_geographic_max_distinct_sites", "initial_exploration",
    "action_control_policy_version", "world_clock",
)




def reconcile_native_evidence(*, stage8, local, replay, require_complete=True):
    """Join full M11 Stage8 quarantine to independently reconstructed local Q.

    Only the exact same (world step, cycle, option) may discharge an already
    quarantined local event. No unknown, intrinsic or other producer is
    promoted to verified by the mere presence of an affordance somewhere.
    Even a complete arithmetic join is NOT a confirmatory L3 verdict.
    """
    if (type(require_complete) is not bool
            or type(stage8) is not dict or type(local) is not dict
            or type(replay) is not dict
            or stage8.get("scope") != "A2R_STAGE8_NATIVE_EVIDENCE_RECONSTRUCTED_NOT_L3"
            or local.get("scope") != "A2R_NATIVE_LOCAL_AFFORDANCE_ARITHMETIC_NOT_L3"
            or replay.get("full_q_replay_verified") is not True
            or stage8.get("preregistered_mechanism_exposed") is not False
            or local.get("preregistered_mechanism_exposed") is not False):
        raise ValueError("native evidence join requires two cold technical auditors")

    pending = stage8.get("unreplayed_evaluations")
    verified = local.get("verified_evaluations")
    if type(pending) is not list or type(verified) is not list:
        raise ValueError("full per-occurrence M11 evidence lists required")

    def key(row):
        if (type(row) is not dict or type(row.get("step")) is not int
                or type(row.get("cycle")) is not int
                or type(row.get("option")) is not str or not row["option"]):
            raise ValueError("malformed evidence occurrence identity")
        return row["step"], row["cycle"], row["option"]

    quarantine = {}
    for row in pending:
        identity = key(row)
        if (identity in quarantine
                or row.get("family") not in (
                    "local_affordance", "intrinsic_or_unknown",
                    "external_adapter")):
            raise ValueError("duplicated/unknown Stage8 evidence quarantine")
        quarantine[identity] = row

    covered = set()
    learned_local = 0
    for row in verified:
        identity = key(row)
        if (identity in covered or identity not in quarantine
                or quarantine[identity]["family"] != "local_affordance"
                or row.get("path") not in ("local", "goal_linked")
                or type(row.get("q_active_used")) is not bool
                or type(row.get("expected_evidence")) not in (int, float)
                or not isfinite(row["expected_evidence"])
                or not -1. <= row["expected_evidence"] <= 1.):
            raise ValueError("unmatched or forged native local Q evidence")
        covered.add(identity)
        learned_local += row["q_active_used"]

    stage8_count = stage8.get("stage8_evaluations_recomputed")
    pending_count = stage8.get("stage8_other_evaluations_unreplayed")
    local_count = local.get("native_local_affordance_recomputed")
    local_q = local.get("local_with_learned_q")
    total = replay.get("stage8_read_count")
    learned_total = replay.get("learned_stage8_reads")
    stage8_q = stage8.get("learned_q_reads_recomputed")
    if (any(type(v) is not int or v < 0 for v in (
            stage8_count, pending_count, local_count, local_q, total,
            learned_total, stage8_q))
            or local_count != len(verified) or local_q != learned_local
            or pending_count != len(pending)
            or stage8_count + pending_count != total
            or stage8_count + len(covered) > total
            or stage8_q + learned_local > learned_total
            or stage8.get("all_native_evidence_recomputed") is not (
                not pending)):
        raise ValueError("native Stage8/Q and local evidence counts disagree")

    unknown = [row for row in pending if key(row) not in covered]
    if not unknown and stage8_q + learned_local != learned_total:
        raise ValueError("learned native Q read not covered by any formula")
    if require_complete and unknown:
        raise ValueError(
            "unreplayed native intrinsic/other evidence remains: %d"
            % len(unknown))
    return {
        "scope": "A2R_COLD_NATIVE_EVIDENCE_JOIN_NOT_L3",
        "ordinary_stage8_equations_recomputed": stage8_count,
        "local_affordance_equations_recomputed": local_count,
        "full_native_stage8_occurrences": total,
        "unreplayed_other_producer_occurrences": len(unknown),
        "unreplayed_examples": unknown[:8],
        "all_native_equations_recomputed": not unknown,
        "preregistered_mechanism_exposed": False,
        "study_admissible": False,
        "general_L3": "NOT_ESTABLISHED",
    }



def reconcile_stage11_intrinsic_provenance(*, stage8, intrinsic):
    """Check every Stage11 diagnostic against the full Stage8 quarantine.

    Direct-frontier magnitude is not evidence of physical novelty or
    accessibility; even recomputed observations remain quarantined and
    cannot become a scientific GO.
    """
    if (type(stage8) is not dict or type(intrinsic) is not dict
            or stage8.get("scope") != "A2R_STAGE8_NATIVE_EVIDENCE_RECONSTRUCTED_NOT_L3"
            or intrinsic.get("scope") !=
                "A2R_STAGE11_PARTIAL_SOURCE_INTRINSIC_ARITHMETIC_NOT_L3"
            or intrinsic.get("study_admissible") is not False
            or intrinsic.get("preregistered_mechanism_exposed") is not False
            or intrinsic.get("all_stage11_intrinsic_state_independently_replayed") is not False
            or intrinsic.get("frontier_admissibility_independently_replayed") is not False
            or intrinsic.get("general_L3") != "NOT_ESTABLISHED"):
        raise ValueError("not an independent non-authorizing Stage11 cold audit")
    pending = stage8.get("unreplayed_evaluations")
    completed = intrinsic.get("intrinsic_magnitude_verified")
    remaining = intrinsic.get("unreconstructed_owner_intrinsic")
    if any(type(x) is not list for x in (pending, completed, remaining)):
        raise ValueError("Stage11 full occurrence lists are required")

    def identity(row):
        if (type(row) is not dict
                or type(row.get("step")) is not int or row["step"] < 1
                or type(row.get("cycle")) is not int or row["cycle"] < 1
                or type(row.get("option")) is not str or not row["option"]):
            raise ValueError("invalid Stage11 original event identity")
        return row["step"], row["cycle"], row["option"]

    all_pending, expected = set(), set()
    for row in pending:
        key = identity(row)
        if key in all_pending:
            raise ValueError("duplicate native Stage8 quarantine event")
        all_pending.add(key)
        if row.get("family") == "intrinsic_or_unknown":
            expected.add(key)

    seen = set()
    for row in completed:
        key = identity(row)
        if (key in seen or key not in expected
                or row.get("producer") not in (
                    "exploration:p48_geographic", "exploration:p48_instrumental")):
            raise ValueError("forged or duplicate intrinsic formula event")
        val, score = row.get("recomputed_intrinsic"), row.get("recomputed_evidence")
        if (type(val) not in (float, int) or not isfinite(val)
                or not 0 < val <= 1
                or type(score) not in (float, int) or not isfinite(score)
                or not -1 <= score <= 1):
            raise ValueError("unbounded intrinsic source calculation")
        seen.add(key)
    for row in remaining:
        key = identity(row)
        if (key in seen or key not in expected
                or type(row.get("reason")) is not str or not row["reason"]):
            raise ValueError("unmatched intrinsic historical gap")
        seen.add(key)

    counts = (
        intrinsic.get("stage11_intrinsic_occurrences"),
        intrinsic.get("direct_frontier_intrinsic_recomputed"),
        intrinsic.get("unreconstructed_owner_intrinsic_occurrences"),
        stage8.get("stage11_post_competition_occurrences"),
    )
    if (any(type(v) is not int or v < 0 for v in counts)
            or counts[0] != counts[3] or counts[1] != len(completed)
            or counts[2] != len(remaining)
            or counts[0] != counts[1] + counts[2] or seen != expected):
        raise ValueError("incomplete native Stage11 occurrence census")
    return {
        "scope":"A2R_STAGE11_SOURCE_FORMULA_JOIN_NOT_L3",
        "stage11_original_events_reconciled":len(seen),
        "direct_frontier_formula_checked_not_novelty":len(completed),
        "owner_history_missing_occurrences":len(remaining),
        "still_quarantined_without_frontier_admissibility":len(seen),
        "all_stage11_intrinsic_causes_proven":False,
        "preregistered_mechanism_exposed":False,
        "study_admissible":False,
        "general_L3":"NOT_ESTABLISHED",
    }

def score_cold_original(*, original, reference, cold, replay):
    """Join source-born reference and real cold native receipts, then score.

    Call only after inspect_m11 and cold_replay_m11 on the archived SQLite.
    Unit-test fixture dictionaries do not authenticate M11 on their own.
    """
    if any(type(x) is not dict for x in (original, reference, cold, replay)):
        raise ValueError("missing sealed original, reconstructed birth or M11 proof")
    receipt = cold.get("receipt")
    if type(receipt) is not dict:
        raise ValueError("missing M11 cold signed receipt")
    for field in ("identity", "generation", "status", "journal_head", "state_hash"):
        if receipt.get(field) != original.get(field):
            raise ValueError("M11 signed " + field + " differs from sealed original")
    if (receipt["identity"] != reference.get("identity")
            or original.get("mode") != reference.get("mode")
            or cold.get("analysis_admissible") is not True
            or cold.get("runtime_contract") != reference.get("runtime_contract")
            or reference.get("q_at_birth_empty") is not True
            or replay.get("full_q_replay_verified") is not True
            or replay.get("study_admissible") is not True
            or replay.get("m11_identity") != receipt["identity"]
            or replay.get("m11_journal_head") != receipt["journal_head"]
            or replay.get("m11_state_hash") != receipt["state_hash"]
            or replay.get("generation") != receipt["generation"]
            or replay.get("status") != receipt["status"]
            or replay.get("mode") != original.get("mode")):
        raise ValueError("born source or cold native Q/TD replay disagrees")
    owner = cold.get("owner")
    if (type(owner) is not dict
            or owner.get("owner_config_version") != reference.get("value_needs_config_version")
            or owner.get("td_config_version") != reference["born_td"]["version"]
            or owner.get("td_feature_version") != reference["born_td"]["feature_version"]):
        raise ValueError("signed reward owner not equal to reconstructed birth")
    steps = cold.get("physical_steps")
    if (type(steps) is not list or not steps
            or len(steps) != receipt["generation"]
            or steps[0].get("before") != reference.get("initial_body")):
        raise ValueError("first lived body or physical chain disagrees with source")
    life = evaluate_life(
        initial_body=reference["initial_body"],
        steps=[{"step":item["step"], "body":item["after"],
                "action":item["action"], "status":item["status"]}
               for item in steps],
        horizon=HORIZON, status=receipt["status"],
        setpoints=reference["setpoints"], scales=reference["scales"],
    )
    score = life["deficit_area_total"] / (4 * HORIZON)
    if not isfinite(score) or not 0 <= score <= 1:
        raise ValueError("death-inclusive ECO-v1 score outside preregistered range")
    return {
        "identity": original["identity"], "role": original["role"],
        "seed": original["seed"], "mode": original["mode"],
        "generation": receipt["generation"], "dead": receipt["status"] == "dead",
        "primary_score": score,
        "deficit_area_by_need": life["deficit_area_by_need"],
        "m11_head": receipt["journal_head"],
        "m11_state_hash": receipt["state_hash"],
        "native_q_replay_verified": True,
    }


def verify_birth_pair(canonical, candidate):
    """Every non-reward birth field must match within the role/seed pair."""
    if (type(canonical) is not dict or type(candidate) is not dict
            or canonical.get("mode") != MODES[0]
            or candidate.get("mode") != MODES[1]
            or canonical.get("seed") != candidate.get("seed")
            or canonical.get("role") != candidate.get("role")
            or canonical.get("identity") == candidate.get("identity")):
        raise ValueError("invalid A2-R paired birth identities")
    for field in PARITY_FIELDS:
        if field not in canonical or canonical[field] != candidate.get(field):
            raise ValueError("pre-reward birth parity differs: " + field)
    if (canonical.get("q_at_birth_empty") is not True
            or candidate.get("q_at_birth_empty") is not True
            or canonical.get("runtime_contract") == candidate.get("runtime_contract")):
        raise ValueError("learned Q imported or reward mode not constructor-pinned")
    return True


def describe_complete_pairs(pairs):
    """Exactly 48 paired scores, no inferential test or GO by design."""
    if type(pairs) is not list or len(pairs) != 48:
        raise ValueError("exactly 48 pairs needed, not 96 pseudoreplicates")
    seen = set()
    deltas = {role: [] for role in ROLES}
    reward_differences = candidate_paths = 0
    for pair in pairs:
        if type(pair) is not dict:
            raise ValueError("malformed original pair")
        role, seed = pair.get("role"), pair.get("seed")
        key = (role, seed)
        if role not in ROLES or type(seed) is not int or seed not in SEEDS or key in seen:
            raise ValueError("missing or duplicate preregistered role/seed block")
        seen.add(key)
        a, b, witness = pair.get("canonical"), pair.get("candidate"), pair.get("witness")
        if type(a) is not dict or type(b) is not dict or type(witness) is not dict:
            raise ValueError("original M11 comparison incomplete")
        if (a.get("role") != role or b.get("role") != role
                or a.get("seed") != seed or b.get("seed") != seed
                or a.get("mode") != MODES[0] or b.get("mode") != MODES[1]
                or a.get("identity") == b.get("identity")):
            raise ValueError("swapped or duplicated original pair arms")
        for arm in (a, b):
            value = arm.get("primary_score")
            if (type(value) not in (int, float) or not isfinite(value)
                    or not 0 <= value <= 1 or type(arm.get("dead")) is not bool):
                raise ValueError("invalid ECO-v1 original score")
        if (witness.get("schema") != "i1-a2r-pair-mechanism-witness/1"
                or witness.get("scope") != "COLD_PAIRED_L1_DIAGNOSTIC_NOT_L3"
                or witness.get("general_L3") != "NOT_ESTABLISHED"
                or witness.get("preregistered_mechanism_exposed") is not False
                or witness.get("canonical_m11_head") != a.get("m11_head")
                or witness.get("candidate_m11_head") != b.get("m11_head")):
            raise ValueError("paired mechanism witness lacks original M11 heads")
        reward_differences += witness.get("first_physical_reward_difference_step") is not None
        candidate_paths += witness.get("descriptive_candidate_path_observed") is True
        deltas[role].append(a["primary_score"] - b["primary_score"])
    if seen != {(role, seed) for role in ROLES for seed in SEEDS}:
        raise ValueError("A2-R original pair roster is incomplete")
    return {
        "schema": "individual-zero-i1-a2r-cold-postflight-descriptive/1",
        "original_lives_replayed": 96,
        "paired_comparisons": 48,
        "independent_temperament_blocks": 24,
        "reward_difference_pairs_descriptive": reward_differences,
        "candidate_mediation_paths_descriptive": candidate_paths,
        "by_role": {
            role: {
                "pair_count": 24,
                "mean_canonical_minus_candidate_descriptive": mean(deltas[role]),
                "positive_pairs_descriptive": sum(x > 0 for x in deltas[role]),
            } for role in ROLES
        },
        "frozen_statistical_gate_called": False,
        "preregistered_mechanism_exposed": False,
        "live_actions_run_provenance_independently_attested": False,
        "immutable_once_only_guaranteed": False,
        "study_admissible": False,
        "status": "MEASUREMENT_BLOCKED_PENDING_EXTERNAL_ATTESTATION",
        "general_L3": "NOT_ESTABLISHED", "historical_A1C": "NO_GO",
    }


def audit_sealed_originals(*, archive_root, checkout_root, generated_root,
                           source_commit, source_tree, preset_sha256,
                           github_run_id, external_lock_sha256,
                           external_manifest_sha256):
    """Cold census on all 96 M11 original files, no confirmation decision.

    Independently supplied external origin/manifest SHA values are required;
    this tool cannot certify where those SHA values were first published.
    Every failure is a hard blocker; never censor missing lives or replace
    originals. All scientific outcomes remain descriptive pending a separate
    external execution and full mediation attestation.
    """
    from i1_a2r_source_birth_audit import (
        verify_generated_fork, verify_source_checkout, reconstruct_pristine_birth,
    )
    from i1_a2r_m11_cold import inspect_m11
    from i1_a2r_q_replay import cold_replay_m11
    from i1_a2r_pair_witness import compare_pair
    from i1_a2r_stage8_evidence import attest_native_stage8
    from i1_a2r_affordance_cold import audit_native_affordance_evidence
    from i1_a2r_intrinsic_cold import audit_stage11_intrinsic_magnitude
    from i1_a2r_geographic_history_cold import replay_geographic_history
    from i1_a2r_geo_intrinsic_join import reconcile_geographic_intrinsic
    from i1_a2r_control_cold import audit_native_action_control, audit_native_wait_continuity
    from i1_a2r_candidate_provenance import audit_candidate_provenance
    from i1_a2r_q_coexposure import summarize_paid_q_coexposure

    root = Path(archive_root)
    verify_archive(
        root=root, expected_commit=source_commit, expected_tree=source_tree,
        expected_preset=preset_sha256, expected_run_id=github_run_id,
        expected_lock_sha256=external_lock_sha256,
        expected_manifest_sha256=external_manifest_sha256,
    )
    verify_source_checkout(
        root=checkout_root, expected_commit=source_commit,
        expected_tree=source_tree, expected_preset=preset_sha256)
    verify_generated_fork(root=Path(checkout_root), generated=Path(generated_root))
    manifest = load_canonical_json(
        root / "manifest.json", expected_digest=external_manifest_sha256)
    stored = {}
    for row, archived in zip(ordered_rows(), manifest["lives"]):
        role, seed, mode, identity = (
            row["role"], row["seed"], row["mode"], row["identity"])
        ref = reconstruct_pristine_birth(
            role=role, seed=seed, mode=mode, preset_sha256=preset_sha256)
        if ref.get("identity") != identity or ref.get("mode") != mode:
            raise ValueError("reconstructed source birth differs from original identity")
        path = str(root / "lives" / identity / "life.sqlite")
        cold = inspect_m11(path=path, identity=identity, mode=mode)
        replay = cold_replay_m11(
            path=path, identity=identity, mode=mode,
            setpoints=ref["setpoints"], weights=ref["weights"],
            born_td=ref["born_td"], world_clock=ref["world_clock"])
        # Separate native evidence-equation check: cold Q parity alone does
        # not prove that Stage8 actually used the reconstructed Q value.
        stage8 = attest_native_stage8(
            cold["events"], q_replay=replay,
            calibration=ref["stage8_evaluation"],
            td_version=ref["born_td"]["version"])
        local = audit_native_affordance_evidence(
            cold["events"], q_replay=replay, birth=ref)
        intrinsic = audit_stage11_intrinsic_magnitude(
            cold["events"], q_replay=replay, stage8_audit=stage8, birth=ref)
        intrinsic_join = reconcile_stage11_intrinsic_provenance(
            stage8=stage8, intrinsic=intrinsic)
        geography = replay_geographic_history(
            cold["events"], final_exploration=cold["final_exploration"],
            birth=ref, generation=cold["receipt"]["generation"])
        geo_intrinsic = reconcile_geographic_intrinsic(
            geography=geography, intrinsic=intrinsic,
            stage11_join=intrinsic_join)
        controller = audit_native_action_control(
            cold["events"], q_replay=replay, birth=ref)
        q_coexposure = summarize_paid_q_coexposure(
            cold["events"], q_replay=replay, controller=controller,
            stage8=stage8, local=local)
        candidates = audit_candidate_provenance(
            cold["events"], birth=ref, q_replay=replay, control=controller)
        continuity = audit_native_wait_continuity(
            cold["events"], q_replay=replay, birth=ref,
            control=controller, final_competition=cold["final_competition"])
        # Direct-frontier intensity is NOT enough to establish that a
        # physically admissible frontier was novel at that lived step.
        coverage = reconcile_native_evidence(
            stage8=stage8, local=local, replay=replay,
            require_complete=True)
        score = score_cold_original(
            original=archived, reference=ref, cold=cold, replay=replay)
        score["stage8_evidence_recomputed"] = True
        score["stage8_math_read_count"] = stage8["stage8_evaluations_recomputed"]
        score["local_affordance_math_read_count"] = local["native_local_affordance_recomputed"]
        stored[(role, seed, mode)] = {
            "reference": ref, "cold": cold, "replay": replay,
            "stage8": stage8, "local": local,
            "coverage": coverage, "intrinsic": intrinsic,
            "intrinsic_join": intrinsic_join, "geography": geography,
            "geography_intrinsic": geo_intrinsic,
            "action_control": controller, "wait_continuity": continuity,
            "candidate_provenance": candidates,
            "q_coexposure": q_coexposure,
            "score": score,
        }
    pairs = []
    for role in ROLES:
        for seed in SEEDS:
            c = stored[(role, seed, MODES[0])]
            d = stored[(role, seed, MODES[1])]
            verify_birth_pair(c["reference"], d["reference"])
            witness = compare_pair(
                canonical=c["replay"], candidate=d["replay"],
                canonical_events=c["cold"]["events"],
                candidate_events=d["cold"]["events"],
                setpoints=c["reference"]["setpoints"],
                weights=c["reference"]["weights"],
            )
            pairs.append({
                "role": role, "seed": seed,
                "canonical": c["score"], "candidate": d["score"],
                "witness": witness,
            })
    descriptive = describe_complete_pairs(pairs)
    return {
        **descriptive,
        "source_commit": source_commit,
        "source_tree": source_tree,
        "external_lock_digest_checked": external_lock_sha256,
        "external_manifest_digest_checked": external_manifest_sha256,
        "all_96_cold_m11_and_12_feature_q_replayed": True,
        "all_96_native_stage8_equations_recomputed": True,
        "all_96_local_affordance_equations_reconciled": True,
        "all_96_death_inclusive_scores_recomputed": True,
        "pairs": pairs,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--checkout-root", type=Path, required=True)
    parser.add_argument("--generated-root", type=Path, required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--source-tree", required=True)
    parser.add_argument("--preset-sha256", required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--lock-sha256", required=True)
    parser.add_argument("--manifest-sha256", required=True)
    args = parser.parse_args()
    result = audit_sealed_originals(
        archive_root=args.archive_root,
        checkout_root=args.checkout_root,
        generated_root=args.generated_root,
        source_commit=args.source_commit, source_tree=args.source_tree,
        preset_sha256=args.preset_sha256, github_run_id=args.run_id,
        external_lock_sha256=args.lock_sha256,
        external_manifest_sha256=args.manifest_sha256,
    )
    print(json.dumps(result, sort_keys=True, allow_nan=False))


if __name__ == "__main__":
    main()
