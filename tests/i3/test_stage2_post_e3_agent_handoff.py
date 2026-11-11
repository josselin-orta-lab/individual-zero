"""Navigation-only Stage-2 E3 stop: prevent stale handoff reactivation.

No original study is executed, no motor, World or life is constructed.
These checks protect *instructions* from contradicting accepted scientific
evidence. They are not a new scientific hypothesis test or stage verdict.
"""
from __future__ import annotations

import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
I3 = ROOT / "src" / "i3"
MANIFEST = I3 / "ACTIVE_SURFACE.json"
AGENTS = I3 / "AGENTS.md"
ACTIVE = I3 / "docs" / "ACTIVE_SURFACE.md"
STATUS = I3 / "docs" / "STATUS.md"
STOP = (I3 / "docs" / "studies" / "stage2-replay-gate-selected-design"
        / "STAGE2_POST_E3_SCIENTIFIC_STOP_ASSESSMENT_2026-11-11.md")
E3_RESULT = (I3 / "docs" / "studies" / "stage2-replay-gate-selected-design"
             / "E3_NATIVE_PAID_BRANCH_DELIVERY_RESULTS_2026-11-11.md")
E3_SOURCE = I3 / "lab" / "stage2_e3_native_paid_branch_delivery.py"


class PostE3ScientificHandoffContract(unittest.TestCase):
    def test_capacity_status_does_not_lift_scientific_or_world_authority(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertEqual(data["current_stage"], "2.1 replay gate")
        self.assertEqual(data["reference"], "P1.3 funded-v2")
        self.assertEqual(data["canonical_status"], "REPLAY_GATE_CAPACITY_SHOWN")
        governance = data["governance"]
        for key in ("fresh_lived_worlds_allowed", "i3_registered",
                    "scientific_gate_authorized",
                    "next_scientific_cohort_authorized",
                    "all_new_worlds_currently_authorized"):
            self.assertIs(governance[key], False, key)
        self.assertEqual(governance["authorized_fresh_lived_scope"],
                         "EXHAUSTED_80_81_NO_FURTHER_WORLD_AUTHORIZED")
        self.assertEqual(governance["development_80_81"],
                         "CLOSED_COMPLETE_NO_RETRY")

    def test_latest_source_locked_e3_fails_motor_gate_without_erasing_score(self):
        stop = STOP.read_text(encoding="utf-8")
        result = E3_RESULT.read_text(encoding="utf-8")
        self.assertIn("E3_FROZEN_NATIVE_ACTION_MEDIATION_NOT_SHOWN", result)
        self.assertIn("0/2", result)
        self.assertIn("SCORE_ONLY", result)
        self.assertIn("1,148", result)
        self.assertIn("f078899c348944b076bd0038987c434f411571cc0c44aeba5f32bc9f005b4b01", result)
        self.assertIn("E3_EXACT_CANDIDATE_CLOSED_NEGATIVE", stop)
        self.assertIn("STAGE2_SCIENTIFIC_COMPLETION_NOT_ISSUED", stop)
        self.assertIn("zero new scientific lives", stop.lower())
        self.assertTrue(E3_SOURCE.is_file())

    def test_current_agent_and_active_docs_prefer_post_e3_stop(self):
        agents = AGENTS.read_text(encoding="utf-8")
        active = ACTIVE.read_text(encoding="utf-8")
        status = STATUS.read_text(encoding="utf-8")
        for doc in (agents, active):
            self.assertIn(
                "STAGE2_POST_E3_SCIENTIFIC_STOP_ASSESSMENT_2026-11-11.md",
                doc)
            self.assertIn("0/2", doc)
            self.assertIn("NOT_ISSUED", doc)
            self.assertIn("P1.3", doc)
        self.assertIn("Stage 2 post-E3 scientific stop checkpoint", status)
        self.assertIn("E3_FROZEN_NATIVE_ACTION_MEDIATION_NOT_SHOWN", status)
        self.assertLess(agents.index("Current Stage-2.1 E3 research handoff"),
                        agents.index("Historical Stage-2.1 post-B1"))
        self.assertNotIn("the frozen DEVELOPMENT 80/81 pilot may\nuse",
                         agents)
        self.assertNotIn("The cost-only, fixed-action\nsoftware campaigns through",
                         active)

    def test_manifest_instruction_is_not_new_living_experiment_permission(self):
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
        next_step = data["next_scientific_action"]
        self.assertTrue(next_step.startswith("HOLD: No new World"))
        for required in ("CLOSED_NEGATIVE", "0 of 2", "NOT_ISSUED",
                         "P1.3", "paid", "scoped owner authorization",
                         "STAGE2_POST_E3_SCIENTIFIC_STOP_ASSESSMENT"):
            self.assertIn(required, next_step)
        self.assertTrue(any(
            "E3 branch-memory visible-versus-paid-discard" in x
            and "CLOSED_NEGATIVE" in x and "may not be retuned" in x
            for x in data["rules"]))

    def test_recent_handoff_links_exist_and_are_not_old_run_permission(self):
        for path in (AGENTS, ACTIVE):
            text = path.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if (target.startswith("http") or target.startswith("#")
                        or target.startswith("mailto:")):
                    continue
                resolved = (path.parent / target.split("#", 1)[0]).resolve()
                self.assertTrue(resolved.is_file(), (path.name, target))
        self.assertTrue(STOP.is_file())
        self.assertIn("CLOSED_NO_RETRY", AGENTS.read_text(encoding="utf-8"))
        self.assertIn("no new World", ACTIVE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
