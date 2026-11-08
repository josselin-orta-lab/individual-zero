"""Identity guard for the Mind finalization extraction."""
from copy import deepcopy
from pathlib import Path
from types import MethodType
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules.body import BodyLaws, CognitiveBudget
from i3.modules.genome import midpoint
from i3.modules.mind import Mind


def _legacy_finalize(
        self, *, body, inv, opts, scored, score_witness,
        cycles, budget, horizon, urgency,
        observer_offered, observer_families):
    """Exact pre-extraction P1.3 finalization block, test oracle only."""
    if not scored:
        info = {"option": None, "funding": "NO_FUNDED_SCORE"}
        if self.observer_decision_diagnostics:
            info["observer"] = {
                "offered_options": observer_offered, "scored_options": 0,
                "rejected_controls": 0, "decision_outcome": "no_funded_score",
                "offered_families": observer_families,
                "scored_families": self._observer_option_families(()),
                "pre_body": tuple(body), "score_witness": score_witness}
        return None, None, budget.work, info
    winner, used = self._compete(scored, cycles, budget)
    ranked = [winner] + [
        o for o, _ in sorted(scored, key=lambda x: -x[1])
        if o != winner]
    by_id = {o[0]: o for o in opts}
    competition = (
        self._observer_competition
        if self.observer_full_competition else None)
    if competition is not None:
        competition["control_order"] = list(ranked)
        competition["control_attempts"] = []
    rejected_controls = 0
    for oid in ranked:
        action, param = self._admit(
            by_id[oid], inv, budget.remaining)
        if competition is not None:
            competition["control_attempts"].append({
                "option": oid, "admitted": action is not None})
        if action is not None:
            break
        rejected_controls += 1
    else:
        info = {"option": None, "funding": "NO_FUNDED_MOTOR"}
        if self.observer_decision_diagnostics:
            info["observer"] = {
                "offered_options": observer_offered,
                "scored_options": len(scored),
                "rejected_controls": rejected_controls,
                "decision_outcome": "control_rejected",
                "offered_families": observer_families,
                "scored_families":
                    self._observer_option_families(
                        o for o, _ in scored),
                "pre_body": tuple(body),
                "score_witness": score_witness}
            if competition is not None:
                competition["status"] = "ALL_CONTROLS_REJECTED"
                competition["final_admitted_option"] = None
                info["observer"]["competition_witness"] = competition
        return None, None, budget.work, info
    self.intention = oid if len(by_id[oid][1]) > 1 else None
    work = budget.work
    key = by_id[oid][1][0]
    self.last = (body, key, action, param)
    info = {
        "option": oid, "cycles": used, "horizon": horizon,
        "simulated": work.simulated_steps,
        "urgency": round(urgency, 6),
        "funding": "FUNDED", "scored_options": len(scored),
        "top": sorted(
            ((round(s, 6), o) for o, s in scored),
            reverse=True)[:3]}
    if self.observer_decision_diagnostics:
        info["observer"] = {
            "offered_options": observer_offered,
            "scored_options": len(scored),
            "rejected_controls": rejected_controls,
            "decision_outcome": "action_admitted",
            "admitted_action": action,
            "offered_families": observer_families,
            "scored_families":
                self._observer_option_families(
                    o for o, _ in scored),
            "pre_body": tuple(body),
            "score_witness": score_witness}
        if competition is not None:
            competition["status"] = "ACTION_ADMITTED"
            competition["final_admitted_option"] = oid
            competition["final_admitted_action"] = action
            competition["intention_after"] = self.intention
            info["observer"]["competition_witness"] = competition
    return action, param, work, info


def _cap(body, *, water=False, here_food=(), inventory=()):
    return {
        "body": tuple(body),
        "here": (water, tuple(here_food)),
        "neighbors": (
            (False, ()),
            (False, ()),
            None,
            None),
        "inventory": tuple(inventory),
    }


def _snapshot(mind, budget):
    return {
        "budget_work": budget.work,
        "budget_remaining": budget.remaining,
        "map": deepcopy(mind.map),
        "hist": deepcopy(mind.hist),
        "tokens": deepcopy(mind.tokens),
        "external": deepcopy(mind.external),
        "acc": deepcopy(mind.acc),
        "intention": mind.intention,
        "last": deepcopy(mind.last),
        "rng": mind.rng.getstate(),
        "budget_rng": mind._budget_rng.getstate(),
    }


class MindFinalizerIdentityTests(unittest.TestCase):
    def test_extracted_finalizer_is_exact_old_block_on_frozen_panel(self):
        caps = (
            _cap((80., 80., 80., 80., 80.)),
            _cap((60., 40., 30., 70., 60.), water=True),
            _cap(
                (65., 20., 75., 55., 70.),
                here_food=("fruit-ext",),
                inventory=(("fruit-ext", 1),)),
            _cap(
                (45., 35., 35., 40., 55.),
                water=True,
                here_food=("food-a", "food-b"),
                inventory=(("food-a", 1), ("food-b", 1))),
        )
        for index, cap in enumerate(caps):
            with self.subTest(index=index):
                new = Mind(
                    midpoint(), 800 + index,
                    observer_decision_diagnostics=True,
                    observer_full_competition=True)
                old = Mind(
                    midpoint(), 800 + index,
                    observer_decision_diagnostics=True,
                    observer_full_competition=True)
                old._finalize_scored_decision = MethodType(
                    _legacy_finalize, old)

                new_budget = CognitiveBudget(
                    cap["body"], BodyLaws())
                old_budget = CognitiveBudget(
                    cap["body"], BodyLaws())
                new_result = new.decide(deepcopy(cap), new_budget)
                old_result = old.decide(deepcopy(cap), old_budget)

                self.assertEqual(new_result, old_result)
                self.assertEqual(
                    _snapshot(new, new_budget),
                    _snapshot(old, old_budget))


if __name__ == "__main__":
    unittest.main()
