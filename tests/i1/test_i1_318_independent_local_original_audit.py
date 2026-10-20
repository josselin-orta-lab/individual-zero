"""Adversarial synthetic evidence for the original-WAL #318 classifier."""
import importlib.util
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
spec = importlib.util.spec_from_file_location(
    "audit318local", ROOT / "tools/audit_i1_318_independent_local_cohort.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def event(kind, data, *, cycle=1, step=1, attempt="test:one", **extra):
    return dict(kind=kind, t_monde=step, cycle=cycle,
                attempt_ref=attempt, data=data, **extra)


def trace():
    ref = "option:i1:local:t1:boire:here"
    command = dict(primitive="boire", parameters={})
    rows = [
        event("i1_local_opportunity_perceived", {
            "policy": module.POLICY, "goal_filter_applied": False,
            "accessible_count": 1, "not_already_proposed": 1}),
        event("i1_local_opportunity_proposed", {
            "policy": module.POLICY, "option_ref": ref,
            "command": command, "goal_ref": None,
            "forced_motor": False, "physical_outcome_known": False,
            "visible_input_sha256": "a" * 64}),
        event("i1_local_opportunity_registration", {
            "option_ref": ref, "registered": True, "goal_neutral": True}),
        event("stage8_option_evaluation", {
            "option_ref": ref, "learned_value_status": "unlearned"}),
        event("competition_cycle", {"traces": [
            {"option_ref": ref, "crossed": True}]}),
        event("command_admitted", {
            "option_ref": ref, "source": "decision", "primitive": "boire",
            "command_hash": "valid-hash"}),
        event("command_experienced", {}, primitive="boire",
              command_hash="valid-hash", emitter="action_control"),
    ]
    return rows


class IndependentLocalOriginalWAL(unittest.TestCase):
    def test_full_synthetic_funnel_not_physical_certificate(self):
        result = module.classify(trace(), treatment=True)
        self.assertEqual(result["funnel"]["physically_applied"], 1)
        self.assertEqual(result["perceived_opportunity_cycles"], 1)

    def test_control_proposals_forbidden(self):
        with self.assertRaises(ValueError):
            module.classify(trace(), treatment=False)

    def test_unregistered_not_selected(self):
        rows = [r for r in trace() if r["kind"] !=
                "i1_local_opportunity_registration"]
        result = module.classify(rows, treatment=True)
        self.assertEqual(result["funnel"]["registered"], 0)
        self.assertEqual(result["funnel"]["proposed_unregistered"], 1)

    def test_false_physical_match_never_certified(self):
        rows = trace()
        rows[-1]["command_hash"] = "unrelated"
        result = module.classify(rows, treatment=True)
        self.assertEqual(result["funnel"]["physically_applied"], 0)
        self.assertEqual(
            result["funnel"]["crossed_without_physically_admitted_command"], 1)

    def test_unknown_utility_is_not_safety_assurance(self):
        rows = trace()
        rows[1]["data"]["physical_outcome_known"] = True
        with self.assertRaises(ValueError):
            module.classify(rows, treatment=True)

    def test_crossing_not_implied_by_registration(self):
        rows = trace()
        rows[4]["data"]["traces"][0]["crossed"] = False
        result = module.classify(rows, treatment=True)
        self.assertEqual(result["funnel"]["crossed"], 0)


if __name__ == "__main__":
    unittest.main()
