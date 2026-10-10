"""Fail-closed Stage-9 heldout metric assessment, NOT scientific certification.

The laboratory (not the individual) is the only potential reader of oracle
truth and registration data. These functions validate a *claimed* heldout
evidence envelope, derive metrics from its row-level observations, and state
what remains unverified. A digest or self-reported replay is not a physical
witness, prospective Git registration, independent review or Golden.
EN MVP v1.2.1 §§9.6, 13.2, 19.5, 20.3 and INV-25/32/33.
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import isfinite, sqrt
from pathlib import Path
import re
from typing import Mapping

from .determinism import canonical_causal_bytes, sha256_hex
from .stage9_scientific_preregistration import validate_registration


EVIDENCE_VERSION = "stage9-heldout-evidence-v2"
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
TRUTHS = frozenset({"self", "world", "none"})
ATTRIBUTIONS = frozenset({"self_compatible", "world_justified", "uncertain"})
CANDIDATE_STATUSES = frozenset({
    "correlation_observee", "hypothese_causale",
    "testee_par_intervention", "etablie",
})
CASE_FIELDS = frozenset({
    "id", "episode_ref", "observation_ref", "ground_truth", "attribution",
})
CANDIDATE_FIELDS = frozenset({
    "id", "contingency_ref", "episode_ref", "observation_ref",
    "causal_status",
})
RUN_FIELDS = frozenset({
    "world_id", "world_sha256", "seed",
    "journal_sha256", "replay_journal_sha256",
    "causal_state_sha256", "replay_causal_state_sha256",
    "known_cause_cases", "naturally_acquired_false_candidates",
})
EVIDENCE_FIELDS = frozenset({
    "protocol_version", "registration_digest",
    "frozen_implementation_commit", "runs", "evidence_sha256",
})


def _name(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _digest(value: object) -> bool:
    return isinstance(value, str) and bool(SHA256.fullmatch(value))


def _wilson(successes: int, total: int) -> tuple[float, float] | None:
    """Two-sided 95% Wilson score interval; no interval at denominator zero."""
    if total == 0:
        return None
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    midpoint = (p + z * z / (2 * total)) / denominator
    margin = (
        z * sqrt(p * (1 - p) / total + z * z / (4 * total * total))
        / denominator
    )
    return max(0.0, midpoint - margin), min(1.0, midpoint + margin)


def assess_heldout_campaign(
    registration: Mapping[str, object] | None,
    evidence: Mapping[str, object] | None,
) -> dict[str, object]:
    """Calculate provisional metrics only, never an accepted Golden.

    This reader cannot independently establish that report payloads are
    physically authentic, that Git registration predates data, or that INV-25
    holds in unseen runs. External audited witnesses remain mandatory.
    """
    if registration is None:
        if evidence is not None:
            raise ValueError("heldout evidence requires a prior registration")
        return {
            "assessment": "unregistered", "registration_digest": None,
            "scientific_verdict": None, "golden_stage9_frozen": False,
        }

    registration_digest = validate_registration(registration)
    if evidence is None:
        return {
            "assessment": "awaiting_holdout_campaign",
            "registration_digest": registration_digest,
            "scientific_verdict": None, "golden_stage9_frozen": False,
        }
    if not isinstance(evidence, dict) or set(evidence) != EVIDENCE_FIELDS:
        raise ValueError("heldout evidence envelope missing required fields")
    if evidence["protocol_version"] != EVIDENCE_VERSION:
        raise ValueError("heldout evidence version mismatch")
    if (
        evidence["registration_digest"] != registration_digest
        or evidence["frozen_implementation_commit"]
        != registration["frozen_implementation_commit"]
    ):
        raise ValueError("heldout report does not match frozen registration")
    supplied_digest = evidence["evidence_sha256"]
    payload = dict(evidence)
    del payload["evidence_sha256"]
    if not _digest(supplied_digest) or (
        sha256_hex(canonical_causal_bytes(payload)) != supplied_digest
    ):
        raise ValueError("heldout evidence has an invalid full-report digest")

    worlds = set(registration["holdout_world_ids"])
    seeds = set(registration["holdout_seeds"])
    expected = {(world, seed) for world in worlds for seed in seeds}
    rows = evidence["runs"]
    if not isinstance(rows, list) or len(rows) != len(expected):
        raise ValueError("heldout campaign is incomplete or has extra runs")
    encountered = set()
    witnessed_positive_runs = set()
    expected_positive_runs = {
        (world, seed) for world in registration["positive_world_ids"]
        for seed in seeds
    }
    known_cases = correct = uncertain = false_self = 0
    no_effect_controls = no_effect_abstentions = no_effect_false_attributions = 0
    natural_candidates = false_established = 0
    # Pooled metrics are provisional: disclose sample concentration per run.
    count_labels = (
        "known_cause_cases", "correct_links", "uncertain_links",
        "false_self_links", "no_effect_control_cases",
        "no_effect_control_abstentions", "no_effect_control_false_attributions",
        "natural_false_candidate_count", "false_established_count",
    )
    run_metrics = []
    # A memory episode may contain multiple genuine physical transitions.
    # Count observation rows and distinct closed-episode references separately:
    # neither a larger row count nor a distinct episode identifier alone
    # establishes sampling independence across physical contexts.
    repeated_candidate_episode_clusters = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != RUN_FIELDS:
            raise ValueError("invalid heldout run schema")
        world, seed = row["world_id"], row["seed"]
        if (
            not _name(world) or type(seed) is not int
            or (world, seed) not in expected
            or (world, seed) in encountered
        ):
            raise ValueError("unexpected or duplicate heldout world/seed run")
        encountered.add((world, seed))
        counts_before = (
            known_cases, correct, uncertain, false_self, no_effect_controls,
            no_effect_abstentions, no_effect_false_attributions,
            natural_candidates, false_established,
        )
        if row["world_sha256"] != registration["holdout_world_sha256"][world]:
            raise ValueError("heldout physical world digest does not match registration")
        for label in (
            "journal_sha256", "replay_journal_sha256",
            "causal_state_sha256", "replay_causal_state_sha256",
        ):
            if not _digest(row[label]):
                raise ValueError("invalid heldout journal or causal digest")
        if (
            row["journal_sha256"] != row["replay_journal_sha256"]
            or row["causal_state_sha256"] != row["replay_causal_state_sha256"]
        ):
            raise ValueError("heldout replay is not identical")
        cases = row["known_cause_cases"]
        candidates = row["naturally_acquired_false_candidates"]
        if not isinstance(cases, list) or not isinstance(candidates, list):
            raise ValueError("heldout cases and candidates must be lists")
        seen_cases = set()
        seen_candidates = set()
        seen_candidate_contingencies = set()
        known_episode_counts: dict[str, int] = {}
        candidate_episode_counts: dict[str, int] = {}
        # Evidence identity is a physical observation source, not an
        # autobiographical episode. One closed episode may contain distinct
        # transitions (and distinct §13.2 intervention contexts). Independence
        # of heldout sampling still requires external provenance/context audit;
        # this scorer must not claim that a digest proves it.
        used_physical_refs = set()
        positive_known_case_count = 0
        for case in cases:
            if not isinstance(case, dict) or set(case) != CASE_FIELDS:
                raise ValueError("invalid known-cause observation schema")
            if (
                not all(_name(case[k]) for k in CASE_FIELDS)
                or case["ground_truth"] not in TRUTHS
                or case["attribution"] not in ATTRIBUTIONS
                or case["id"] in seen_cases
            ):
                raise ValueError("invalid or duplicate known-cause observation")
            seen_cases.add(case["id"])
            known_episode_counts[case["episode_ref"]] = (
                known_episode_counts.get(case["episode_ref"], 0) + 1
            )
            physical = case["observation_ref"]
            if physical in used_physical_refs:
                raise ValueError("reused physical known-cause evidence")
            used_physical_refs.add(physical)
            # §9.6: "none" is a real negative control, not a known
            # positive cause. Counting it in the accuracy denominator
            # would dilute the benchmark and could hide false attributions.
            if case["ground_truth"] == "none":
                no_effect_controls += 1
                if case["attribution"] == "uncertain":
                    no_effect_abstentions += 1
                else:
                    no_effect_false_attributions += 1
                    if case["attribution"] == "self_compatible":
                        false_self += 1
                continue
            known_cases += 1
            positive_known_case_count += 1
            if case["attribution"] == "uncertain":
                uncertain += 1
            if case["attribution"] == "self_compatible" and case["ground_truth"] != "self":
                false_self += 1
            if (
                (case["ground_truth"] == "self"
                 and case["attribution"] == "self_compatible")
                or (case["ground_truth"] == "world"
                    and case["attribution"] == "world_justified")
            ):
                correct += 1
        # A positive-control world with no observed positive-cause case
        # cannot be treated as an independently evaluated world merely
        # because other worlds contribute enough rows to pass a pooled
        # Wilson bound. Record missing coverage instead of synthesizing
        # a case or excluding the run after seeing outcomes.
        if positive_known_case_count and (world, seed) in expected_positive_runs:
            witnessed_positive_runs.add((world, seed))
        if candidates and world not in registration["negative_world_ids"]:
            raise ValueError("known-false candidates must come from null-control worlds")
        for item in candidates:
            if not isinstance(item, dict) or set(item) != CANDIDATE_FIELDS:
                raise ValueError("invalid natural candidate evidence schema")
            if (
                not all(_name(item[k]) for k in CANDIDATE_FIELDS)
                or item["causal_status"] not in CANDIDATE_STATUSES
                or item["id"] in seen_candidates
            ):
                raise ValueError("invalid or repeated natural candidate")
            # The superstition denominator counts canonical causal rules,
            # never one row for each observation of a single learned rule.
            # Repetition under fresh candidate IDs would otherwise dilute
            # an established false-rule rate with duplicate hypotheses.
            if item["contingency_ref"] in seen_candidate_contingencies:
                raise ValueError("reused canonical false-rule contingency")
            seen_candidates.add(item["id"])
            seen_candidate_contingencies.add(item["contingency_ref"])
            candidate_episode_counts[item["episode_ref"]] = (
                candidate_episode_counts.get(item["episode_ref"], 0) + 1
            )
            physical = item["observation_ref"]
            if physical in used_physical_refs:
                raise ValueError("reused physical natural candidate evidence")
            used_physical_refs.add(physical)
            natural_candidates += 1
            false_established += int(item["causal_status"] == "etablie")
        counts_after = (
            known_cases, correct, uncertain, false_self, no_effect_controls,
            no_effect_abstentions, no_effect_false_attributions,
            natural_candidates, false_established,
        )
        repeated_candidate_episode_clusters.extend(
            {
                "world_id": world, "seed": seed, "episode_ref": episode_ref,
                "candidate_count": n,
            }
            for episode_ref, n in sorted(candidate_episode_counts.items())
            if n > 1
        )
        run_metrics.append({
            "world_id": world, "seed": seed,
            "distinct_known_case_episode_refs": len(known_episode_counts),
            "distinct_natural_candidate_episode_refs": len(candidate_episode_counts),
            "max_natural_candidates_per_episode": max(
                candidate_episode_counts.values(), default=0,
            ),
            **{
                label: after - before
                for label, before, after in zip(
                    count_labels, counts_before, counts_after,
                )
            },
        })
    repeated_candidate_episode_clusters.sort(
        key=lambda group: (
            group["world_id"], group["seed"], group["episode_ref"],
        )
    )
    # Byte-identical archives reused between distinct registered world/seed
    # cells are a concrete provenance warning, even when filenames and inodes
    # differ. This is NOT, by itself, proof of fraud or lack of independence:
    # an unchanged state can legitimately be identical in separate runs.
    # Therefore expose deterministic collision groups for external review,
    # without silently changing the preregistered metric denominator.
    archive_digest_collisions: dict[str, list[dict[str, object]]] = {}
    for field in ("journal_sha256", "causal_state_sha256"):
        by_digest: dict[str, list[dict[str, object]]] = {}
        for row in rows:
            by_digest.setdefault(row[field], []).append({
                "world_id": row["world_id"], "seed": row["seed"],
            })
        archive_digest_collisions[field] = [
            {"sha256": digest, "runs": sorted(
                cells, key=lambda cell: (cell["world_id"], cell["seed"]),
            )}
            for digest, cells in sorted(by_digest.items())
            if len(cells) > 1
        ]
    # Sorting prevents the report from concealing concentration via run order.
    # Run breakdown remains diagnostic, not a proof of sample independence.
    run_metrics.sort(key=lambda item: (item["world_id"], item["seed"]))
    negative_runs_with_candidates = sum(
        item["natural_false_candidate_count"] > 0
        for item in run_metrics
        if item["world_id"] in registration["negative_world_ids"]
    )
    if encountered != expected:
        raise ValueError("heldout world/seed coverage does not match registration")
    missing_positive_runs = sorted(expected_positive_runs - witnessed_positive_runs)
    if registration["confidence_method"] != "wilson_95":
        raise ValueError("unsupported preregistered confidence rule")
    accuracy = correct / known_cases if known_cases else None
    rate = false_established / natural_candidates if natural_candidates else None
    correct_interval = _wilson(correct, known_cases)
    false_interval = _wilson(false_established, natural_candidates)
    if no_effect_false_attributions:
        # A reported causal link without a physical effect violates the
        # basic attribution boundary; do not label metrics review-eligible.
        status = "invalid_no_effect_attribution"
    elif known_cases == 0 or natural_candidates == 0:
        status = "not_evaluable"
    elif missing_positive_runs:
        status = "incomplete_known_cause_world_coverage"
    elif natural_candidates < registration["minimum_naturally_acquired_candidates"]:
        status = "insufficient_natural_candidates"
    elif (
        correct_interval[0] < registration["minimum_known_cause_accuracy"]
        or false_interval[1] > registration["maximum_superstitious_rule_rate"]
    ):
        status = "below_preregistered_confidence_threshold"
    else:
        status = "metrics_eligible_for_independent_review"
    return {
        "assessment": status,
        "registration_digest": registration_digest,
        "evidence_sha256": supplied_digest,
        "runs": len(rows),
        "per_run_metrics": run_metrics,
        "reused_closed_memory_candidate_episodes": repeated_candidate_episode_clusters,
        "total_distinct_natural_candidate_episode_refs_by_run": sum(
            run["distinct_natural_candidate_episode_refs"]
            for run in run_metrics
        ),
        "cross_run_identical_archives": archive_digest_collisions,
        "negative_runs_with_candidates": negative_runs_with_candidates,
        "registered_negative_runs": (
            len(registration["negative_world_ids"]) * len(seeds)
        ),
        "negative_runs_without_natural_candidates": [
            {"world_id": run["world_id"], "seed": run["seed"]}
            for run in run_metrics
            if run["world_id"] in registration["negative_world_ids"]
            and run["natural_false_candidate_count"] == 0
        ],
        "known_cause_cases": known_cases,
        "positive_known_cause_runs": len(witnessed_positive_runs),
        "registered_positive_runs": len(expected_positive_runs),
        "missing_positive_known_cause_runs": [
            {"world_id": world, "seed": seed} for world, seed
            in missing_positive_runs
        ],
        "correct_links": correct,
        "uncertain_links": uncertain,
        "false_self_links": false_self,
        "no_effect_control_cases": no_effect_controls,
        "no_effect_control_abstentions": no_effect_abstentions,
        "no_effect_control_false_attributions": no_effect_false_attributions,
        "known_cause_accuracy": accuracy,
        "known_cause_wilson_95": correct_interval,
        "natural_false_candidate_count": natural_candidates,
        "false_established_count": false_established,
        "superstitious_rule_rate": rate,
        "superstition_wilson_95": false_interval,
        "scientific_verdict": None,
        "golden_stage9_frozen": False,
        "outstanding": [
            "independent proof of prospective registration and heldout-seed custody",
            "raw WorldBody manifests and externally verified oracle truth",
            "independent closed-Memory/physical journal provenance audit",
            "re-execution of heldout runs with frozen manifest and software",
            "safety veto/simulator INV-25 and full Stage-9 acceptance review",
        ],
    }


def _reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    """Never permit an ambiguous heldout record at any JSON nesting level."""
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate heldout evidence JSON key: {key}")
        result[key] = value
    return result


def _reject_nonfinite_constant(value: str) -> None:
    raise ValueError(f"invalid non-finite heldout JSON constant: {value}")


def load_heldout_evidence(path: Path) -> dict[str, object]:
    """Parse an untrusted scientific report without lossy JSON key merging."""
    payload = json.loads(
        path.read_text(encoding="utf-8"),
        object_pairs_hook=_reject_duplicate_keys,
        parse_constant=_reject_nonfinite_constant,
    )
    if not isinstance(payload, dict):
        raise ValueError("heldout evidence root must be a JSON object")
    return payload


def main() -> None:
    import argparse
    from .stage9_scientific_preregistration import load_registration
    parser = argparse.ArgumentParser(
        description="Stage-9 provisional holdout scoring; never a Golden"
    )
    parser.add_argument("--registration", type=Path)
    parser.add_argument("--evidence", type=Path)
    args = parser.parse_args()
    if args.evidence is not None and args.registration is None:
        parser.error("--evidence requires --registration")
    registration = (
        load_registration(args.registration) if args.registration else None
    )
    evidence = load_heldout_evidence(args.evidence) if args.evidence else None
    print(json.dumps(
        assess_heldout_campaign(registration, evidence),
        sort_keys=True, indent=2,
    ))


if __name__ == "__main__":
    main()
