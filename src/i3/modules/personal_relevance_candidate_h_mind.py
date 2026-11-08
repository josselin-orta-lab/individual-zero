"""Unified Candidate-H relevance-gated decision software.

This module is intentionally not registered in runtime/life.py.  It composes the
two frozen Candidate-H relevance predicates, pays a detached Stage-A probe, then
recomputes the final decision from the cognition-depleted body.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict

from .body import (
    CognitiveBudget, CognitiveWork, VITAL)
from .mind import Mind
from .personal_recurrence_candidate_g_mind import (
    PersonalRecurrenceCandidateGMind)

POLICY = "personal_relevance_candidate_h_v1"
TOL = 1e-12
WORK_KEYS = ("cycles", "simulated_steps", "memory_items", "replays")
_COMPLETE_PROBE_FUNDING = ("FUNDED", "NO_FUNDED_MOTOR")


def _work_add(left: CognitiveWork, right: CognitiveWork) -> CognitiveWork:
    return CognitiveWork(*(
        getattr(left, key) + getattr(right, key) for key in WORK_KEYS))


def _top(scores: dict[str, float]) -> tuple[str, ...]:
    if not scores:
        return ()
    best = max(scores.values())
    return tuple(sorted(
        name for name, value in scores.items()
        if value >= best - TOL))


def first_contact_relevant_fields(
        target_choices, information_value, trial_advantage) -> bool:
    """Exact #1162 strict first-contact relevance predicate."""
    return (
        target_choices is not None
        and "TRIAL" in tuple(target_choices)
        and type(information_value) in (int, float)
        and information_value > TOL
        and type(trial_advantage) in (int, float)
        and trial_advantage > TOL)


def first_contact_relevant_witnesses(witnesses) -> bool:
    """Apply the frozen first-contact predicate to actually offered explorers."""
    for row in witnesses:
        if not str(row.get("option", "")).startswith("explorer:"):
            continue
        if first_contact_relevant_fields(
                row.get("target_node_best_choices"),
                row.get("trial_information_value"),
                row.get("trial_advantage")):
            return True
    return False


def post_contact_relevant_scores(
        with_information: dict[str, float],
        without_information: dict[str, float],
        positive_frontier_options) -> bool:
    """Exact #1163 top-effect rule on an arbitrary offered option set."""
    positive = tuple(sorted(set(positive_frontier_options)))
    if not positive or set(with_information) != set(without_information):
        return False
    with_top = _top(with_information)
    without_top = _top(without_information)
    return (
        with_top != without_top
        and any(option in with_top for option in positive))


def post_contact_relevant_witnesses(witnesses) -> tuple[bool, dict]:
    """Reconstruct WITH/WITHOUT_INFORMATION sets from Candidate-G receipts."""
    with_information = {}
    without_information = {}
    positive = []
    for row in witnesses:
        option = row.get("option")
        score = row.get("total_score")
        if type(option) is not str or type(score) not in (int, float):
            continue
        with_information[option] = float(score)
        without = float(score)
        if (
                option.startswith("explorer:")
                and row.get("score_kind") == "frontier_water_expected_distress"):
            base = row.get("base_return")
            if type(base) in (int, float):
                without = float(base)
            info = row.get("information_value")
            if type(info) in (int, float) and info > TOL:
                positive.append(option)
        without_information[option] = without

    relevant = post_contact_relevant_scores(
        with_information, without_information, positive)
    return relevant, {
        "with_information_top": _top(with_information),
        "without_information_top": _top(without_information),
        "positive_frontier_options": tuple(sorted(set(positive))),
        "with_information_scores": with_information,
        "without_information_scores": without_information,
    }


class PersonalRelevanceCandidateHMind(PersonalRecurrenceCandidateGMind):
    """Candidate-G memories/projector plus paid support-versus-relevance gating."""

    def __init__(self, genome, life_seed, **kwargs):
        super().__init__(genome, life_seed, **kwargs)
        self.relevance_probes = 0
        self.relevance_probe_unfunded = 0
        self.relevance_candidate_final = 0
        self.relevance_reference_final = 0

    @staticmethod
    def first_contact_relevant(
            target_choices, information_value, trial_advantage) -> bool:
        return first_contact_relevant_fields(
            target_choices, information_value, trial_advantage)

    @staticmethod
    def post_contact_relevant(
            with_information, without_information,
            positive_frontier_options) -> bool:
        return post_contact_relevant_scores(
            with_information, without_information,
            positive_frontier_options)

    def _probe(self, cap, budget: CognitiveBudget) -> dict:
        """Execute a detached, fully paid Candidate-G proposal as Stage A."""
        shadow = deepcopy(self)
        shadow.observer_decision_diagnostics = True
        shadow.observer_full_competition = False

        before = budget.work
        result = PersonalRecurrenceCandidateGMind.decide(
            shadow, cap, budget)
        after = budget.work
        work = CognitiveWork(*(
            getattr(after, key) - getattr(before, key)
            for key in WORK_KEYS))
        info = result[3]
        observer = info.get("observer", {})
        witnesses = observer.get("score_witness", ())
        phase = info.get("frontier_phase", "UNKNOWN")
        complete = info.get("funding") in _COMPLETE_PROBE_FUNDING

        post_details = None
        if not complete:
            relevant = None
            classification = "PROBE_UNFUNDED"
        elif phase == "POST_CONTACT_PERSONAL":
            relevant, post_details = post_contact_relevant_witnesses(
                witnesses)
            classification = "RELEVANT" if relevant else "FALLBACK"
        elif phase == "FIRST_CONTACT_PERSONAL_RECURRENCE":
            relevant = first_contact_relevant_witnesses(witnesses)
            classification = "RELEVANT" if relevant else "FALLBACK"
        else:
            relevant = False
            classification = "FALLBACK"

        return {
            "classification": classification,
            "relevant": relevant,
            "complete": complete,
            "phase": phase,
            "funding": info.get("funding"),
            "work": work,
            "body_after_computation": budget.remaining,
            "shadow_option": info.get("option"),
            "post_contact": post_details,
            "first_contact_strict_options": tuple(sorted(
                row.get("option") for row in witnesses
                if str(row.get("option", "")).startswith("explorer:")
                and first_contact_relevant_fields(
                    row.get("target_node_best_choices"),
                    row.get("trial_information_value"),
                    row.get("trial_advantage")))),
            "score_witnesses": tuple(witnesses),
        }

    @staticmethod
    def _cap_with_body(cap, body):
        out = dict(cap)
        out["body"] = tuple(body)
        return out

    def _decorate(
            self, final, *, stage_a, stage_b_work,
            route, total_work, body_after) -> tuple:
        action, param, _old_work, old_info = final
        info = dict(old_info)
        info["experimental_policy"] = POLICY
        info["candidate_h_route"] = route
        info["candidate_h_relevance"] = stage_a["classification"]
        info["candidate_h_probe_phase"] = stage_a["phase"]
        info["candidate_h_probe_funding"] = stage_a["funding"]
        info["candidate_h_stage_a_work"] = asdict(stage_a["work"])
        info["candidate_h_stage_a_body_after"] = tuple(
            stage_a["body_after_computation"])
        info["candidate_h_stage_b_work"] = asdict(stage_b_work)
        info["candidate_h_total_work"] = asdict(total_work)
        info["candidate_h_body_after_cognition"] = tuple(body_after)
        info["persistent_simulation_mode"] = "reference"
        info["persistent_projection_accounting"] = "chunk_end"
        info["omega_source"] = "NONE_PERSONAL_ONLY"
        if route == "P1.3_FINAL":
            info["decision_projection_mode"] = "reference"
        elif route == "CANDIDATE_F_FINAL":
            info["decision_projection_mode"] = "candidate_f"
        return action, param, total_work, info

    def decide(self, cap, budget: CognitiveBudget):
        if tuple(cap["body"]) != budget.body or budget.work != CognitiveWork():
            raise ValueError("fresh allowance must match the perceived body")
        if any(budget.body[k] <= 0 for k in VITAL):
            raise ValueError("no decision after physical death")
        if (self.simulation_mode, self.projection_accounting) != (
                "reference", "chunk_end"):
            raise RuntimeError(
                "Candidate-H persistent mode must remain P1.3 reference")

        self.relevance_probes += 1
        stage_a = self._probe(cap, budget)

        if not stage_a["complete"]:
            self.relevance_probe_unfunded += 1
            info = {
                "option": None,
                "funding": "NO_FUNDED_RELEVANCE_PROBE",
                "experimental_policy": POLICY,
                "candidate_h_route": "PROBE_UNFUNDED",
                "candidate_h_relevance": "PROBE_UNFUNDED",
                "candidate_h_probe_phase": stage_a["phase"],
                "candidate_h_probe_funding": stage_a["funding"],
                "candidate_h_stage_a_work": asdict(stage_a["work"]),
                "candidate_h_stage_a_body_after": tuple(
                    stage_a["body_after_computation"]),
                "candidate_h_stage_b_work": asdict(CognitiveWork()),
                "candidate_h_total_work": asdict(budget.work),
                "candidate_h_body_after_cognition": tuple(budget.remaining),
                "persistent_simulation_mode": "reference",
                "persistent_projection_accounting": "chunk_end",
                "omega_source": "NONE_PERSONAL_ONLY",
            }
            if (self.simulation_mode, self.projection_accounting) != (
                    "reference", "chunk_end"):
                raise RuntimeError("Candidate-H probe leaked projector mode")
            return None, None, budget.work, info

        post_probe_body = budget.remaining
        final_cap = self._cap_with_body(cap, post_probe_body)
        final_budget = CognitiveBudget(post_probe_body, budget.laws)

        if stage_a["relevant"]:
            self.relevance_candidate_final += 1
            final = PersonalRecurrenceCandidateGMind.decide(
                self, final_cap, final_budget)
            route = "CANDIDATE_F_FINAL"
        else:
            self.relevance_reference_final += 1
            self._pending_branch = None
            self._pending_opportunity_presence = None
            self._pending_opportunity_commit = None
            self.last = None
            final = Mind.decide(self, final_cap, final_budget)
            if final[3].get("funding") != "NO_PROCESSING_BUDGET":
                self._capture_opportunity_presence()
            route = "P1.3_FINAL"

        # Stage B was already block-by-block funded by its own allowance.
        # Mirror that exact work into the cumulative decision receipt.
        budget.spend(final_budget.work)
        total = budget.work
        expected = _work_add(stage_a["work"], final_budget.work)
        if total != expected:
            raise RuntimeError("Candidate-H phase work does not sum exactly")
        settlement_gap = max(
            abs(a - b)
            for a, b in zip(budget.remaining, final_budget.remaining))
        if settlement_gap > 1e-12:
            raise RuntimeError(
                "Candidate-H cumulative body settlement mismatch")

        # Learning storage must own the complete decision cost, not Stage B only.
        self._branch_decision_work = total
        if (self.simulation_mode, self.projection_accounting) != (
                "reference", "chunk_end"):
            raise RuntimeError("Candidate-H final decision leaked projector mode")

        return self._decorate(
            final, stage_a=stage_a, stage_b_work=final_budget.work,
            route=route, total_work=total, body_after=budget.remaining)


__all__ = [
    "POLICY", "PersonalRelevanceCandidateHMind",
    "first_contact_relevant_fields", "first_contact_relevant_witnesses",
    "post_contact_relevant_scores", "post_contact_relevant_witnesses",
]
