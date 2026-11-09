"""Prospective checks for the fresh Candidate-I 62/63 plan."""
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage0_design
from i3.lab import stage1_candidate_i_development_plan as old
from i3.lab import stage1_candidate_i_development_62_63_plan as d


class CandidateIDevelopment6263PlanTests(unittest.TestCase):
    def test_frozen_four_arm_envelope(self):
        plan = d.validate_plan()
        self.assertEqual(len(plan["cases"]), 48)
        self.assertEqual(plan["maximum_steps"], 19200)
        self.assertEqual(
            {row["cohort"] for row in plan["cases"]},
            {"development"})
        self.assertEqual(
            {row["index"] for row in plan["cases"]}, {62, 63})
        self.assertEqual(
            {row["world_seed"] for row in plan["cases"]},
            {2062, 2063})
        self.assertEqual(
            {row["genome_seed"] for row in plan["cases"]},
            {903, 904})
        self.assertEqual(
            tuple(dict.fromkeys(
                row["policy"] for row in plan["cases"])),
            d.POLICIES)
        self.assertEqual(d.digest(plan), d.EXPECTED_PLAN_SHA256)
        self.assertEqual(
            plan["required_settlement_repair_commit"],
            "5ee25b3b0f39050321b0b5c6147bdae0e3e68ec5")
        self.assertTrue(plan["survival_is_not_a_continuation_rule"])
        self.assertTrue(plan["omega_direction_is_not_a_continuation_rule"])
        self.assertTrue(plan["no_selection_validation_or_reserve"])

    def test_j1_j7_are_exactly_the_preexposure_60_61_rules(self):
        self.assertEqual(
            d.plan()["engineering_continuation_rules"],
            old.plan()["engineering_continuation_rules"])

    def test_new_allocations_are_disjoint_from_60_61(self):
        new = d.plan()["cases"]
        previous = old.plan()["cases"]
        for key in (
                "index", "world_seed", "genome_seed", "life_seed"):
            self.assertTrue(
                {row[key] for row in new}.isdisjoint(
                    {row[key] for row in previous}),
                msg=key)

    def test_indices_are_inside_p2_development_and_not_stage0_history(self):
        historical = {
            row["index"]
            for row in stage0_design.world_rows("development")}
        self.assertTrue({62, 63}.isdisjoint(historical))
        first, stop = stage0_design.COHORT_BOUNDS["development"]
        self.assertEqual((first, stop), (2000, 2100))
        self.assertEqual(
            {first + index for index in d.INDICES}, {2062, 2063})

    def test_each_opportunity_is_an_exact_four_policy_block(self):
        cases = d.plan()["cases"]
        self.assertEqual(
            len({row["life_seed"] for row in cases}), 12)
        for start in range(0, len(cases), len(d.POLICIES)):
            block = cases[start:start + len(d.POLICIES)]
            self.assertEqual(
                tuple(row["policy"] for row in block),
                d.POLICIES)
            shared = {
                key: block[0][key]
                for key in (
                    "block", "family", "cohort", "index",
                    "world_seed", "genome_seed", "life_seed")}
            for row in block[1:]:
                self.assertEqual(
                    {key: row[key] for key in shared}, shared)

    def test_native_and_omega0_are_same_genome_matched_arms(self):
        cases = d.plan()["cases"]
        for start in range(0, len(cases), len(d.POLICIES)):
            block = cases[start:start + len(d.POLICIES)]
            native = block[2]
            zero = block[3]
            for key in (
                    "block", "family", "cohort", "index",
                    "world_seed", "genome_seed", "life_seed"):
                self.assertEqual(native[key], zero[key])
            self.assertEqual(native["policy"], d.CANDIDATE_I)
            self.assertEqual(zero["policy"], d.CANDIDATE_I_OMEGA0)

    def test_plan_import_is_inert_and_does_not_read_60_61_evidence(self):
        root = str(Path(d.__file__).resolve().parents[2])
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "from i3.lab.stage1_candidate_i_development_62_63_plan "
            "import validate_plan; "
            "assert len(validate_plan()['cases']) == 48; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.modules.mind' not in sys.modules; "
            "assert 'i3.lab.p2_ecologies' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
