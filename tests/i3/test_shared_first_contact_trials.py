"""S1 identity guards for the production multi-trial first-contact kernel."""
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage1_candidate_g_projection_dependence as D
from i3.lab import stage1_candidate_g_reference_recurrence_falsifier as G
from i3.lab import stage1_candidate_h_relevance_fallback as H
from i3.lab import stage1_shared_first_contact_prior as S
from i3.modules.body import BodyLaws, CognitiveBudget
from i3.modules.shared_first_contact_trials import (
    paid_shared_perceived_first_contact)


def _opts(action_key):
    rows = [
        (name, tuple(plan), None)
        for name, plan in H.ORDINARY_PLANS.items()]
    rows.append(("perceived_trial", (action_key,), None))
    return tuple(rows)


def _production(body, horizon, action_key, omega):
    model = D.make_mind("candidate_f_projection")
    return paid_shared_perceived_first_contact(
        model, G.effect_memory(), _opts(action_key),
        (("perceived_trial", action_key),),
        horizon, CognitiveBudget(body, BodyLaws()),
        omega=omega, competition_cycles=0)


class SharedFirstContactTrialIdentityTests(unittest.TestCase):
    def _assert_identity(self, body, horizon, action_key, omega):
        frozen = S._perceived_probe(
            body, horizon, action_key, omega)
        current = _production(
            body, horizon, action_key, omega)

        self.assertEqual(frozen["status"], "FUNDED")
        self.assertEqual(
            current["status"],
            "COMPLETE_SHARED_FIRST_CONTACT_MATRIX")
        self.assertEqual(current["relevant"], frozen["relevant"])
        self.assertEqual(
            current["ordinary_scores"],
            frozen["ordinary_scores"])
        self.assertEqual(
            current["forecast_work_ceiling"],
            frozen["forecast_work_ceiling"])
        self.assertEqual(
            current["work"], frozen["work"])
        self.assertEqual(
            tuple(current["body_after_computation"]),
            tuple(frozen["body_after_computation"]))

        trial = current["trials"][0]
        frozen_trial = frozen["trial"]
        for key in (
                "no_trial_value", "trial_frozen_value",
                "trial_informed_value", "information_value",
                "trial_advantage"):
            self.assertEqual(trial[key], frozen_trial[key])
        self.assertEqual(
            trial["prior_record"],
            frozen["shared_effect_prior"])

    def test_exact_p80_reduction_all_frozen_states(self):
        for omega in S.OMEGAS:
            for channel, _name, level, body, horizon in S._grid80():
                with self.subTest(
                        omega=omega, channel=channel,
                        level=level, horizon=horizon):
                    self._assert_identity(
                        body, horizon, ("boire",), omega)

    def test_exact_f108_reduction_all_frozen_states(self):
        action = ("manger", "carried-first-contact")
        for omega in S.OMEGAS:
            for energy, food, integrity, body, horizon in S._grid108():
                with self.subTest(
                        omega=omega, energy=energy, food=food,
                        integrity=integrity, horizon=horizon):
                    self._assert_identity(
                        body, horizon, action, omega)


if __name__ == "__main__":
    unittest.main()
