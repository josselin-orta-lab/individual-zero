"""Reproducible Stage-9 acceptance evidence, NOT a golden or a gate waiver.

Normative source: docs/architecture/reference/en/mvp-specification-v1.2.1.md
Sections 9.6, 13.2-13.4, 19.2-19.5 and Stage 9 (20.3), INV-25.

The runner executes existing physical known-cause probes and random-reward
controls. It separately re-executes the unmodified Stage-9 reference runtime.
Unit-test coverage is reported as coverage, not falsely presented as a physical
experiment. In particular neither an injected false hypothesis nor a single
random-reward canary proves a scientific superstition rate.

Run: python -m lab.stage9_acceptance_report
No file is written or reference hash frozen as part of this diagnostic.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import json

from .determinism import canonical_causal_bytes, sha256_hex
from .replay import verify_reexecution
from .stage9_known_causes_benchmark import run_known_cause_probes
from .stage9_random_reward_benchmark import run_random_reward_negative_control
from .stage9_reference_fixture import build_stage9_reference_runtime
from .stage9_spontaneous_superstition_matrix import (
    run_spontaneous_superstition_matrix,
)


NORMATIVE_SPECIFICATION = (
    "docs/architecture/reference/en/mvp-specification-v1.2.1.md"
)
PROTOCOL_VERSION = "stage9-acceptance-diagnostic-v1"


@dataclass(frozen=True, slots=True)
class Stage9AcceptanceCheck:
    criterion: str
    normative_reference: str
    classification: str
    evidence: dict[str, object]
    outstanding: str | None


@dataclass(frozen=True, slots=True)
class Stage9AcceptanceReport:
    protocol_version: str
    normative_specification: str
    random_reward_seed: int
    random_reward_steps: int
    checks: tuple[Stage9AcceptanceCheck, ...]
    acceptance_status: str
    golden_stage9_frozen: bool

    def as_dict(self) -> dict[str, object]:
        document = {
            "protocol_version": self.protocol_version,
            "normative_specification": self.normative_specification,
            "random_reward_seed": self.random_reward_seed,
            "random_reward_steps": self.random_reward_steps,
            "checks": [asdict(check) for check in self.checks],
            "acceptance_status": self.acceptance_status,
            "golden_stage9_frozen": self.golden_stage9_frozen,
        }
        document["evidence_sha256"] = sha256_hex(
            canonical_causal_bytes(document)
        )
        return document

    def to_json(self) -> str:
        return json.dumps(
            self.as_dict(), ensure_ascii=False, sort_keys=True, indent=2,
        ) + "\n"


def _reference_reexecution(*, steps: int = 11) -> dict[str, object]:
    """Compare independently executed causal owners AND journaled decisions.

    No snapshot is used to manufacture future state. Existing Stage-9 replay
    tests cover the separate snapshot/rollback path. This check is narrower
    than the final comprehensive Stage-9 replay acceptance criterion.
    """
    def execute() -> dict[str, object]:
        runtime = build_stage9_reference_runtime()
        outcomes = []
        for _ in range(steps):
            step = runtime.run_step()
            outcomes.append({
                "source": step.source,
                "execution_status": step.execution_status,
                "command_primitive": step.command_primitive,
                "option_ref": step.option_ref,
            })
        if not runtime.journal.verify():
            raise AssertionError("reference journal integrity failed")
        return {
            "outcomes": outcomes,
            "owners": {
                owner.owner_id: owner.export_causal_state()
                for owner in runtime.causal_owners
            },
            "journal_sha256": sha256_hex(
                runtime.journal.canonical_bytes()
            ),
        }

    comparison = verify_reexecution(
        execute_reference=execute, execute_replay=execute,
    )
    comparison.require_identical()
    return {
        "identical": comparison.identical,
        "reference_sha256": comparison.reference_sha256,
        "replayed_sha256": comparison.replay_sha256,
        "steps_per_execution": steps,
        "scope": "unmodified_stage9_reference_two_independent_runs",
    }


def generate_stage9_acceptance_report(
    *, random_reward_seed: int = 42,
    random_reward_steps: int = 14,
) -> Stage9AcceptanceReport:
    """Collect actual diagnostics without inferring missing acceptance data.

    The supplied seed/steps identify a reproducible software control, not a
    preregistered scientific campaign. No cutoff or acceptance claim can be
    introduced via these arguments.
    """
    if type(random_reward_seed) is not int or random_reward_seed < 0:
        raise ValueError("random reward seed must be a nonnegative integer")
    if type(random_reward_steps) is not int or random_reward_steps < 6:
        raise ValueError("random reward steps must be an integer >= 6")

    known = run_known_cause_probes()
    by_id = {case.identifier: case for case in known.cases}
    required_night = (
        "creature-night-harm",
        "two-visible-creatures-night",
        "hidden-danger-harm",
    )
    if not set(required_night).issubset(by_id):
        raise AssertionError("known-cause diagnostic missing night controls")
    if known.ground_truthed_cases <= 0 or known.accuracy is None:
        raise AssertionError("known-cause diagnostic lacks physical ground truth")

    seeded = run_random_reward_negative_control(
        campaign_seed=random_reward_seed,
        steps=random_reward_steps,
        bench_seed_false_hypothesis=True,
    )
    unseeded = run_random_reward_negative_control(
        campaign_seed=random_reward_seed,
        steps=random_reward_steps,
        bench_seed_false_hypothesis=False,
    )
    if (
        seeded.schedule_sha256 != unseeded.schedule_sha256
        or seeded.physical_reward_steps != unseeded.physical_reward_steps
        or seeded.logged_inputs != random_reward_steps - 1
        or unseeded.logged_inputs != random_reward_steps - 1
    ):
        raise AssertionError("paired negative controls have inconsistent schedule")
    if (
        seeded.scientific_gate is not None
        or unseeded.scientific_gate is not None
        or seeded.scientific_superstition_rate is not None
        or unseeded.scientific_superstition_rate is not None
    ):
        raise AssertionError("diagnostic must not invent scientific success")

    # The existing fixed multi-world negative-control diagnostic measures
    # whether this runtime *ever* produces naturally acquired candidates.
    # A zero denominator is "not_evaluable", never a passing superstition rate.
    spontaneous = run_spontaneous_superstition_matrix(
        seeds=(
            random_reward_seed,
            random_reward_seed + 1,
            random_reward_seed + 2,
        ),
        steps=random_reward_steps,
    )
    if spontaneous.natural_false_rule_rate is None:
        if spontaneous.spontaneously_observed_candidates != 0:
            raise AssertionError("spontaneous false-rule denominator inconsistency")
    elif spontaneous.spontaneously_observed_candidates <= 0:
        raise AssertionError("spontaneous false-rule rate without candidate exposure")
    replay = _reference_reexecution()
    night = tuple({
        "scenario": identifier,
        "external_ground_truth": by_id[identifier].known_cause,
        "agency_attribution": by_id[identifier].attribution,
        "correct_link": by_id[identifier].correct_link,
        "uncertain": by_id[identifier].uncertain,
    } for identifier in required_night)
    checks = (
        Stage9AcceptanceCheck(
            criterion="known_cause_attribution",
            normative_reference="9.6 / 19.5 / Stage 9 acceptance",
            classification="diagnostic_only",
            evidence={
                "physical_probe_count": len(known.cases),
                "positive_ground_truth_cases": known.ground_truthed_cases,
                "correct_links": known.correct_links,
                "uncertain_cases": known.uncertain_cases,
                "false_self_links": known.false_self_links,
                "accuracy": known.accuracy,
            },
            outstanding=(
                "Diagnostic probes do not replace a preregistered "
                "evaluation across multiple independent worlds."
            ),
        ),
        Stage9AcceptanceCheck(
            criterion="nighttime_attribution",
            normative_reference="9.6 / Stage 9 observable behavior",
            classification="diagnostic_only",
            evidence={"scenarios": night},
            outstanding=(
                "Full nighttime running-example evidence and repeated "
                "attribution across worlds remain to be evaluated."
            ),
        ),
        Stage9AcceptanceCheck(
            criterion="superstitious_rules_under_random_reward",
            normative_reference="13.2 / 19.5 / P-35 / Stage 9 acceptance",
            classification="not_evaluable",
            evidence={
                "schedule_sha256": seeded.schedule_sha256,
                "external_inputs_verified_seeded": seeded.logged_inputs,
                "external_inputs_verified_unseeded": unseeded.logged_inputs,
                "applied_drinking_seeded": seeded.drinking_commands,
                "applied_drinking_unseeded": unseeded.drinking_commands,
                "false_established_with_bench_hypothesis": (
                    seeded.established_false_rule
                ),
                "false_established_without_bench_hypothesis": (
                    unseeded.established_false_rule
                ),
                "naturally_learned_false_rule_rate": None,
                "preregistered_maximum_false_rule_rate": None,
                "spontaneous_matrix_protocol": spontaneous.protocol_version,
                "spontaneous_matrix_sha256": spontaneous.digest,
                "spontaneous_matrix_seeds": spontaneous.seeds,
                "spontaneous_matrix_worlds": spontaneous.world_variants,
                "spontaneous_matrix_runs": len(spontaneous.runs),
                "spontaneous_candidate_count": (
                    spontaneous.spontaneously_observed_candidates
                ),
                "spontaneously_established_false_rules": (
                    spontaneous.established_false_rules
                ),
                "spontaneous_diagnostic_rate": (
                    spontaneous.natural_false_rule_rate
                ),
                "independent_lived_hydration_episodes": (
                    spontaneous.total_lived_hydration_observations
                ),
                "observed_drinking_episodes": (
                    spontaneous.lived_drink_observations
                ),
                "observed_wait_control_episodes": (
                    spontaneous.lived_wait_control_observations
                ),
                "runs_with_both_drink_and_wait": (
                    spontaneous.runs_with_observed_drink_and_wait
                ),
                "runs_with_n1_positive_drinks": (
                    spontaneous.runs_with_independent_positive_drinks
                ),
                "runs_with_matched_controls": (
                    spontaneous.runs_with_matched_controls
                ),
                "spontaneous_evaluation_status": (
                    spontaneous.evaluation_status
                ),
                "spontaneous_correlation_readiness": (
                    spontaneous.correlation_readiness
                ),
            },
            outstanding=(
                "The multi-seed diagnostic measures physical opportunities "
                "but no naturally acquired false-rule candidates; its "
                "denominator is zero and no scientific rate can be inferred. "
                "An independent frozen protocol, sufficient naturally formed "
                "candidates, and an author-preregistered superstition "
                "threshold remain required."
                if spontaneous.spontaneously_observed_candidates == 0 else
                "The matrix has natural candidates but is still only a "
                "diagnostic: independent preregistration, a fixed maximum "
                "false-rule rate, and held-out trials remain required."
            ),
        ),
        Stage9AcceptanceCheck(
            criterion="safety_fact_veto_without_new_exposure",
            normative_reference="13.3 / DC-05 / Stage 9 acceptance",
            classification="regression_coverage_only",
            evidence={
                "tests": [
                    "tests/test_stage9_runtime.py",
                    "tests/test_stage9_causal_model.py",
                    "tests/test_stage9_lived_evidence.py",
                ],
            },
            outstanding=(
                "Test coverage is not a bench-measured full-world "
                "acceptance campaign, including unchanged R_a and predictions."
            ),
        ),
        Stage9AcceptanceCheck(
            criterion="simulator_uses_established_only",
            normative_reference="13.3 / INV-25 / Stage 9 acceptance",
            classification="regression_coverage_only",
            evidence={
                "tests": [
                    "tests/test_stage9_canonical_corrections.py",
                    "tests/test_stage9_causal_corrections.py",
                ],
            },
            outstanding=(
                "Exact-context correction tests exist; broader physical "
                "acceptance across established and safety-only facts remains."
            ),
        ),
        Stage9AcceptanceCheck(
            criterion="causal_replay",
            normative_reference="17.1-17.3 / INV-33 / Stage 9 acceptance",
            classification="diagnostic_only",
            evidence=replay,
            outstanding=(
                "Reference re-execution is identical, but the Stage-9 golden "
                "has not been frozen and full experiment replays are outstanding."
            ),
        ),
        Stage9AcceptanceCheck(
            criterion="inv25_separation",
            normative_reference="INV-25 / Stage 9 gate",
            classification="regression_coverage_only",
            evidence={
                "tests": [
                    "tests/test_stage9_runtime.py",
                    "tests/test_stage9_causal_lifecycle.py",
                    "tests/test_stage9_canonical_corrections.py",
                ],
            },
            outstanding=(
                "Software regression coverage does not independently certify "
                "the entire scientific Stage-9 gate."
            ),
        ),
    )
    # Not a stale hardcoded green result: no diagnostic-only or coverage-only
    # check is equivalent to experimental acceptance. All criteria would
    # need external preregistered success evidence to close the gate.
    status = (
        "accepted"
        if checks and all(
            check.classification == "scientifically_accepted"
            and check.outstanding is None
            for check in checks
        )
        else "open"
    )
    return Stage9AcceptanceReport(
        protocol_version=PROTOCOL_VERSION,
        normative_specification=NORMATIVE_SPECIFICATION,
        random_reward_seed=random_reward_seed,
        random_reward_steps=random_reward_steps,
        checks=checks,
        acceptance_status=status,
        golden_stage9_frozen=False,
    )


def main() -> None:
    print(generate_stage9_acceptance_report().to_json(), end="")


if __name__ == "__main__":
    main()
