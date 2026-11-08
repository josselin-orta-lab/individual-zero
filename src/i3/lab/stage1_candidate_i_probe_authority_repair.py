"""Frozen Candidate-I probe-restore learning-authority repair gate.

Protocol: docs/STAGE1_CANDIDATE_I_PROBE_AUTHORITY_REPAIR.md.
Software only: no World, life, P2 ecology or 62/63 evidence fixture.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
import json
import sys
from types import MethodType

from ..modules.body import (
    BodyLaws, CognitiveBudget, CognitiveFundingError, CognitiveWork)
from ..modules.genome import midpoint
from ..modules.personal_relevance_candidate_h_mind import (
    PersonalRelevanceCandidateHMind)
from ..modules.personal_shared_prior_candidate_i_mind import (
    PersonalSharedPriorCandidateIMind)

SCHEMA = "i3-candidate-i-probe-authority-repair/v1"
PROTOCOL = "STAGE1_CANDIDATE_I_PROBE_AUTHORITY_REPAIR.md"
BODY = (80.0, 80.0, 40.0, 80.0, 80.0)
STALE_LAST = (
    (80.0, 80.0, 80.0, 80.0, 80.0),
    ("attendre",), "attendre", None)
AUTHORITY_SNAPSHOT_KEYS = frozenset({
    "last",
    "pending_branch",
    "branch_decision_start_body",
    "branch_decision_work",
    "pending_opportunity_presence",
    "pending_opportunity_commit",
})


def _authority(mind):
    return {
        "last": deepcopy(mind.last),
        "pending_branch": deepcopy(mind._pending_branch),
        "branch_decision_start_body":
            deepcopy(mind._branch_decision_start_body),
        "branch_decision_work": mind._branch_decision_work,
        "pending_opportunity_presence":
            deepcopy(mind._pending_opportunity_presence),
        "pending_opportunity_commit":
            deepcopy(mind._pending_opportunity_commit),
    }


def _authority_empty(mind):
    row = _authority(mind)
    return (
        row["last"] is None
        and row["pending_branch"] is None
        and row["branch_decision_start_body"] is None
        and row["branch_decision_work"] == CognitiveWork()
        and row["pending_opportunity_presence"] is None
        and row["pending_opportunity_commit"] is None
    )


def _seed_stale_authority(mind):
    mind.last = deepcopy(STALE_LAST)
    mind._pending_branch = ("stale-branch",)
    mind._set_branch_decision_settlement(
        STALE_LAST[0], CognitiveWork(cycles=1))
    mind._pending_opportunity_presence = ("stale-presence",)
    mind._pending_opportunity_commit = ("stale-commit",)


def _reversible_signature(mind):
    return {
        "map": deepcopy(mind.map),
        "hist": deepcopy(mind.hist),
        "tokens": deepcopy(mind.tokens),
        "external": deepcopy(mind.external),
        "acc": deepcopy(mind.acc),
        "intention": mind.intention,
        "visible": tuple(mind.visible),
        "pos": tuple(mind.pos),
        "unknown": (
            deepcopy(mind._unknown)
            if hasattr(mind, "_unknown") else None),
        "presence": (
            deepcopy(mind._presence)
            if hasattr(mind, "_presence") else None),
        "drift": deepcopy(mind._drift),
        "rng": mind.rng.getstate(),
        "budget_rng": mind._budget_rng.getstate(),
        "observer_competition":
            deepcopy(getattr(mind, "_observer_competition", None)),
        "observer_first_forecast":
            deepcopy(getattr(mind, "_observer_first_forecast", None)),
    }


def _cap(body=BODY, *, water=True, inventory=(), neighbors=None):
    if neighbors is None:
        neighbors = (None, None, None, None)
    return {
        "body": tuple(body),
        "here": (bool(water), ()),
        "neighbors": tuple(neighbors),
        "inventory": tuple(inventory),
    }


def _prime_personal_model(mind):
    for key, delta in (
            (("se_deplacer",), (-2.0, -0.2, -0.4, 0.0, 0.0)),
            (("attendre",), (-0.35, -0.2, -0.4, 0.2, 0.0)),
            (("dormir",), (3.0, -0.35, -0.4, 0.0, 4.0))):
        mind.effects.observe(key, delta)
    mind._drift = mind.drift()


def _legacy_authority_resurrection():
    mind = PersonalSharedPriorCandidateIMind(
        midpoint(), 801, observer_decision_diagnostics=True)
    _seed_stale_authority(mind)

    # Pure reproduction of the pre-repair ownership error: old rollback
    # snapshots carried last, while settlement authority was cleared separately.
    legacy_snapshot = {"last": deepcopy(mind.last)}
    mind._clear_first_contact_learning_authority()
    mind.last = deepcopy(legacy_snapshot["last"])

    rejected = False
    try:
        mind.prepare_learning(
            {"dead": (), "body": BODY},
            CognitiveBudget(BODY, BodyLaws()))
    except RuntimeError as exc:
        rejected = (
            "missing branch decision settlement start body"
            in str(exc))
    return {
        "stale_last_restored": mind.last == STALE_LAST,
        "settlement_absent":
            mind._branch_decision_start_body is None,
        "learning_boundary_rejected": rejected,
    }


def _forced_common_unfunded():
    mind = PersonalSharedPriorCandidateIMind(
        midpoint(), 802,
        observer_decision_diagnostics=True,
        observer_full_competition=True)
    mind.map[(9, 9)] = (False, ())
    mind.hist[(9, 9)] = [2, 0.0, {}]
    mind.acc["old"] = 0.25
    mind.intention = "old-intention"
    baseline = _reversible_signature(mind)
    _seed_stale_authority(mind)

    observed = {}
    original_snapshot = mind._probe_state_snapshot

    def snapshot(self):
        observed["authority"] = _authority(self)
        value = original_snapshot()
        observed["keys"] = tuple(sorted(value))
        return value

    def fail_score(self, **kwargs):
        self.map[(99, 99)] = (True, ())
        self.hist[(99, 99)] = [1, 1.0, {}]
        self.rng.random()
        self._budget_rng.random()
        self._pending_opportunity_presence = ("probe-presence",)
        return {
            "status": "UNFUNDED",
            "probe_funding": "NO_FUNDED_SCORE",
            "work": CognitiveWork(),
            "body_after_computation": kwargs["budget"].remaining,
            "forecast_work_ceiling": kwargs["budget"].work,
            "offered_options": len(kwargs["opts"]),
            "offered_families": (
                self._observer_option_families(
                    row[0] for row in kwargs["opts"])
                if self.observer_decision_diagnostics else None),
        }

    mind._probe_state_snapshot = MethodType(snapshot, mind)
    mind._first_contact_score = MethodType(fail_score, mind)
    budget = CognitiveBudget(BODY, BodyLaws())
    result = mind.decide(_cap(), budget)
    info = result[3]
    return {
        "route": info["candidate_i_route"],
        "reason": info["candidate_i_probe_reason"],
        "authority_at_snapshot_empty": (
            observed.get("authority") is not None
            and observed["authority"]["last"] is None
            and observed["authority"]["pending_branch"] is None
            and observed["authority"]["branch_decision_start_body"] is None
            and observed["authority"]["branch_decision_work"]
            == CognitiveWork()
            and observed["authority"][
                "pending_opportunity_presence"] is None
            and observed["authority"][
                "pending_opportunity_commit"] is None),
        "snapshot_keys": observed.get("keys", ()),
        "authority_after_empty": _authority_empty(mind),
        "reversible_restored":
            _reversible_signature(mind) == baseline,
        "work_matches": result[2] == budget.work,
    }


class _FailRecurrence:
    def estimate(self, *_args, **_kwargs):
        raise CognitiveFundingError(
            "synthetic recurrence read is prospectively unfunded")


def _forced_recurrence_unfunded():
    mind = PersonalSharedPriorCandidateIMind(
        midpoint(), 803,
        observer_decision_diagnostics=True)
    baseline = _reversible_signature(mind)
    _seed_stale_authority(mind)
    mind.opportunity_memory = _FailRecurrence()

    def explorer_options(self, _inv, _body, _horizon):
        self._unknown = {"explorer:1,0": 1}
        self._presence = {}
        return [
            ("dormir", [("dormir",)], None),
            ("attendre", [("attendre",)], None),
            ("explorer:1,0", [("se_deplacer",)],
             ("se_deplacer", "E")),
        ]

    mind.options = MethodType(explorer_options, mind)
    budget = CognitiveBudget(BODY, BodyLaws())
    result = mind.decide(
        _cap(water=False, neighbors=((False, ()), None, None, None)),
        budget)
    info = result[3]
    return {
        "route": info["candidate_i_route"],
        "reason": info["candidate_i_probe_reason"],
        "authority_after_empty": _authority_empty(mind),
        "reversible_restored":
            _reversible_signature(mind) == baseline,
        "work_matches": result[2] == budget.work,
    }


def _fallback_fresh_authority():
    mind = PersonalSharedPriorCandidateIMind(
        midpoint(), 804,
        observer_decision_diagnostics=True,
        observer_full_competition=True)
    _seed_stale_authority(mind)
    budget = CognitiveBudget(BODY, BodyLaws())
    result = mind.decide(_cap(), budget)
    info = result[3]
    work_keys = ("cycles", "simulated_steps", "memory_items", "replays")
    stage_sum = {
        key: (
            info["candidate_i_stage_a_work"][key]
            + info["candidate_i_stage_b_work"][key])
        for key in work_keys
    }
    witness = info.get("observer", {}).get("score_witness", ())
    last_is_fresh = mind.last is None or mind.last != STALE_LAST
    settlement_aligned = (
        mind.last is None
        or (
            mind._branch_decision_start_body == BODY
            and mind._branch_decision_work == result[2] == budget.work))
    current_presence = mind._pending_opportunity_presence
    return {
        "route": info["candidate_i_route"],
        "single_current_cell_observation":
            mind.hist.get((0, 0), [0])[0] == 1,
        "last_is_fresh": last_is_fresh,
        "settlement_aligned": settlement_aligned,
        "current_opportunity_presence":
            current_presence == (True, False),
        "phase_work_exact":
            stage_sum == info["candidate_i_total_work"],
        "addends_zero": bool(witness) and all(
            row["curiosity_bonus_applied"] == 0.0
            and row["risk_penalty_applied"] == 0.0
            for row in witness),
    }


def _find_relevant_fresh_authority():
    # Personal branch scale is software fixture state, not a World oracle.
    from ..lab import stage1_candidate_g_reference_recurrence_falsifier as G

    candidate_bodies = []
    for channel in range(5):
        for level in (20.0, 30.0, 40.0, 50.0):
            body = [80.0] * 5
            body[channel] = level
            candidate_bodies.append(tuple(body))

    for index, body in enumerate(candidate_bodies):
        mind = PersonalSharedPriorCandidateIMind(
            midpoint(), 820 + index,
            observer_decision_diagnostics=True,
            observer_full_competition=True)
        mind.branch_memory = G.effect_memory()
        mind.opportunity_memory = G.recurrence_2_6_10()
        _prime_personal_model(mind)
        _seed_stale_authority(mind)
        budget = CognitiveBudget(body, BodyLaws())
        result = mind.decide(_cap(body), budget)
        info = result[3]
        if info["candidate_i_route"] != "INFORMATION_FINAL":
            continue
        return {
            "found": True,
            "body": body,
            "last_is_fresh":
                mind.last is None or mind.last != STALE_LAST,
            "settlement_aligned": (
                mind._branch_decision_start_body == body
                and mind._branch_decision_work
                == result[2] == budget.work),
            "persistent_reference":
                info["persistent_simulation_mode"] == "reference"
                and info["persistent_projection_accounting"]
                == "chunk_end",
        }
    return {
        "found": False,
        "body": None,
        "last_is_fresh": False,
        "settlement_aligned": False,
        "persistent_reference": False,
    }


def _post_contact_parity():
    left = PersonalSharedPriorCandidateIMind(
        midpoint(), 850,
        observer_decision_diagnostics=True)
    right = PersonalRelevanceCandidateHMind(
        midpoint(), 850,
        observer_decision_diagnostics=True)
    for mind in (left, right):
        _prime_personal_model(mind)
        mind.effects.observe(
            ("boire",), (-0.5, -0.2, 35.0, 0.0, 0.0))

    body = (80.0, 80.0, 40.0, 80.0, 80.0)
    l = left.decide(
        _cap(body, water=False),
        CognitiveBudget(body, BodyLaws()))
    r = right.decide(
        _cap(body, water=False),
        CognitiveBudget(body, BodyLaws()))
    return {
        "motor_work_equal": l[:3] == r[:3],
        "observer_equal":
            l[3].get("observer") == r[3].get("observer"),
        "route":
            l[3].get("candidate_i_route"),
        "omega_unused":
            l[3].get("candidate_i_first_contact_omega_used") is False,
    }


def characterize():
    legacy = _legacy_authority_resurrection()
    common = _forced_common_unfunded()
    recurrence = _forced_recurrence_unfunded()
    fallback = _fallback_fresh_authority()
    relevant = _find_relevant_fresh_authority()
    post = _post_contact_parity()

    forbidden = AUTHORITY_SNAPSHOT_KEYS.intersection(
        set(common["snapshot_keys"]))
    rules = {
        "U0_custody_no_62_63_verdict": True,
        "U1_legacy_authority_resurrection_reproduced": (
            legacy["stale_last_restored"]
            and legacy["settlement_absent"]
            and legacy["learning_boundary_rejected"]),
        "U2_snapshot_has_no_learning_authority":
            not forbidden,
        "U3_authority_cleared_before_snapshot":
            common["authority_at_snapshot_empty"],
        "U4_probe_unfunded_restores_perception_only": (
            common["route"] == "PROBE_UNFUNDED"
            and common["reason"] == "COMMON_MATRIX_UNFUNDED"
            and common["authority_after_empty"]
            and common["reversible_restored"]
            and common["work_matches"]
            and recurrence["route"] == "PROBE_UNFUNDED"
            and recurrence["reason"] == "RECURRENCE_READ_UNFUNDED"
            and recurrence["authority_after_empty"]
            and recurrence["reversible_restored"]
            and recurrence["work_matches"]),
        "U5_fallback_creates_fresh_authority": (
            fallback["route"] == "P1.3_BASE_FINAL"
            and fallback["single_current_cell_observation"]
            and fallback["last_is_fresh"]
            and fallback["settlement_aligned"]
            and fallback["current_opportunity_presence"]
            and fallback["phase_work_exact"]
            and fallback["addends_zero"]),
        "U6_relevant_creates_fresh_authority": (
            relevant["found"]
            and relevant["last_is_fresh"]
            and relevant["settlement_aligned"]
            and relevant["persistent_reference"]),
        "U7_post_contact_candidate_h_parity": (
            post["motor_work_equal"]
            and post["observer_equal"]
            and post["route"] == "POST_CONTACT_CANDIDATE_H"
            and post["omega_unused"]),
        "U8_no_scientific_rule_change": True,
        "U9_authority_boundary": True,
    }
    passed = all(rules.values())
    return {
        "schema": SCHEMA,
        "protocol": PROTOCOL,
        "world_access": False,
        "runtime_life_access": False,
        "p2_ecology_access": False,
        "evidence_branch_acceptance_input": False,
        "lives": 0,
        "legacy": legacy,
        "common_matrix_unfunded": common,
        "recurrence_read_unfunded": recurrence,
        "fallback": fallback,
        "relevant": relevant,
        "post_contact": post,
        "forbidden_snapshot_keys": tuple(sorted(forbidden)),
        "rules": rules,
        "verdict": (
            "CANDIDATE_I_PROBE_AUTHORITY_REPAIR_PASS"
            if passed else
            "CANDIDATE_I_PROBE_AUTHORITY_REPAIR_DEFECT"),
        "60_61_retry_authorized": False,
        "62_63_retry_authorized": False,
        "J1_J7_verdict_authorized": False,
        "new_live_panel_authorized": False,
    }


def run(path):
    report = characterize()
    with open(path, "w") as fh:
        json.dump(report, fh, indent=1, sort_keys=True)
    return report


if __name__ == "__main__":
    report = run(sys.argv[1])
    print("CANDIDATE_I_PROBE_AUTHORITY_REPAIR " + json.dumps({
        "verdict": report["verdict"],
        "rules": report["rules"],
        "relevant_body": report["relevant"]["body"],
    }, sort_keys=True))
