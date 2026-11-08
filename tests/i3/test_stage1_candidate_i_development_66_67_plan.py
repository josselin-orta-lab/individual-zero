"""Prospective checks for the fresh Candidate-I 66/67 plan."""
from pathlib import Path
import subprocess
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage0_design
from i3.lab import stage1_candidate_i_development_plan as p60
from i3.lab import stage1_candidate_i_development_62_63_plan as p62
from i3.lab import stage1_candidate_i_development_64_65_plan as p64
from i3.lab import stage1_candidate_i_development_66_67_plan as d


class CandidateIDevelopment6667PlanTests(unittest.TestCase):
    def test_frozen_four_arm_envelope(self):
        value = d.validate_plan()
        self.assertEqual(len(value["cases"]), 48)
        self.assertEqual(value["maximum_steps"], 19200)
        self.assertEqual(
            {row["cohort"] for row in value["cases"]},
            {"development"})
        self.assertEqual(
            {row["index"] for row in value["cases"]}, {66, 67})
        self.assertEqual(
            {row["world_seed"] for row in value["cases"]},
            {2066, 2067})
        self.assertEqual(
            {row["genome_seed"] for row in value["cases"]},
            {907, 908})
        self.assertEqual(
            tuple(dict.fromkeys(
                row["policy"] for row in value["cases"])),
            d.POLICIES)
        self.assertEqual(d.digest(value), d.EXPECTED_PLAN_SHA256)
        self.assertEqual(
            value["required_lifecycle_stress_v2_commit"],
            "fbaecde68d6fbcb5a9ec8c6d5908b4b1880137bd")
        self.assertTrue(value["survival_is_not_a_continuation_rule"])
        self.assertTrue(value["omega_direction_is_not_a_continuation_rule"])
        self.assertTrue(value["no_selection_validation_or_reserve"])

    def test_j1_j7_are_byte_identical_to_all_exposed_predecessors(self):
        current = d.plan()["engineering_continuation_rules"]
        self.assertEqual(
            current, p60.plan()["engineering_continuation_rules"])
        self.assertEqual(
            current, p62.plan()["engineering_continuation_rules"])
        self.assertEqual(
            current, p64.plan()["engineering_continuation_rules"])

    def test_new_allocations_are_disjoint_from_all_predecessors(self):
        new = d.plan()["cases"]
        previous = (
            p60.plan()["cases"]
            + p62.plan()["cases"]
            + p64.plan()["cases"])
        for key in ("index", "world_seed", "genome_seed", "life_seed"):
            self.assertTrue(
                {row[key] for row in new}.isdisjoint(
                    {row[key] for row in previous}),
                msg=key)

    def test_indices_are_inside_p2_development_and_not_stage0_history(self):
        historical = {
            row["index"]
            for row in stage0_design.world_rows("development")}
        self.assertTrue({66, 67}.isdisjoint(historical))
        first, stop = stage0_design.COHORT_BOUNDS["development"]
        self.assertEqual((first, stop), (2000, 2100))
        self.assertEqual(
            {first + index for index in d.INDICES}, {2066, 2067})

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

    def test_plan_import_is_inert_and_does_not_read_exposed_evidence(self):
        root = str(Path(d.__file__).resolve().parents[2])
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "from i3.lab.stage1_candidate_i_development_66_67_plan "
            "import validate_plan; "
            "assert len(validate_plan()['cases']) == 48; "
            "assert 'i3.runtime.life' not in sys.modules; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.modules.mind' not in sys.modules; "
            "assert 'i3.lab.p2_ecologies' not in sys.modules"
        ], check=True)


if __name__ == "__main__":
    unittest.main()
