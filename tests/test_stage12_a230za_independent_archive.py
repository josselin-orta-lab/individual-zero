"""A2.30-ZA falsification controls on original sealed Z 3.11/3.12 records."""
from __future__ import annotations

from copy import deepcopy
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from audit_stage12_issue110_b_a230za_independent_archives import (
    read_archives,independently_review,independently_decide,
    independent_candidate_commands,eat_b,move_east,
)


class FrozenZPhysicalArchiveAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows,cls.summary=read_archives(
            Path(os.environ["A230ZA_SOURCE_311"]),
            Path(os.environ["A230ZA_SOURCE_312"]),
        )

    def review(self,rows=None,summary=None):
        return independently_review(
            deepcopy(self.rows if rows is None else rows),
            deepcopy(self.summary if summary is None else summary),
        )

    def test_all_original_worlds_and_real_stage6_roots_independent(self):
        report=self.review()
        self.assertEqual(report["source_original_worlds"],168)
        self.assertEqual(report["source_original_physical_steps"],244)
        self.assertEqual(report["independently_recounted_berry_b_ingestions"],80)
        self.assertEqual(report["independently_recounted_physical_terminalities"],20)
        self.assertEqual(report["independently_recounted_surviving_food_successes"],40)
        self.assertEqual(report["independently_recounted_surviving_insufficient"],20)
        self.assertEqual(report["independently_recounted_abstentions"],88)
        self.assertEqual(report["observable_aliased_initial_groups"],40)
        self.assertEqual(report["observationally_aliased_B_groups_containing_terminal"],20)
        self.assertEqual(report["far_B_invisible_initial_matched_controls"],8)
        self.assertEqual(report["stage6_root_exactly_unavailable_80_of_80"],80)
        self.assertFalse(report["conditional_safe_food_certificate_possible_for_fixed_B_policy"])
        self.assertEqual(report["new_physical_worlds"],0)
        self.assertEqual(report["new_i0_lives"],0)
        self.assertFalse(report["real_worldbody_apply_proved_by_JSON_alone"])
        self.assertEqual(report["cognitive_deployment"],"NO-GO")

    def test_hidden_effect_added_to_first_person_rejected(self):
        altered=deepcopy(self.rows)
        altered[0]["initial_first_person"]["latent_external_only"]="toxin_100"
        with self.assertRaisesRegex(ValueError,"hidden/future/partial"):
            self.review(rows=altered)

    def test_injected_future_berry_safety_certificate_rejected(self):
        altered=deepcopy(self.rows)
        altered[0]["certifies_food_safety"]=True
        with self.assertRaisesRegex(ValueError,"fabricated safety"):
            self.review(rows=altered)

    def test_unknown_uc_cost_as_measured_rejected(self):
        altered=deepcopy(self.rows)
        altered[0]["actual_I0_UC_cost"]=0
        with self.assertRaisesRegex(ValueError,"UC"):
            self.review(rows=altered)

    def test_unauthorized_berry_collection_from_blocked_east_rejected(self):
        altered=deepcopy(self.rows)
        row=next(x for x in altered if x["layout_external_only"]=="B_EAST_BLOCKED")
        row["perceptual_policy_choices"][0]["command"]={
            "primitive":"collecter","parameters":{"target":"berry_b"},
        }
        with self.assertRaisesRegex(ValueError,"decision"):
            self.review(rows=altered)

    def test_resource_appearing_from_future_in_policy_input_rejected(self):
        altered=deepcopy(self.rows)
        row=next(x for x in altered if x["layout_external_only"]=="B_EAST_TWO_STEPS")
        snap=row["perceptual_policy_choices"][0]["input_accessible_state"]
        next(n for n in snap["adjacent"] if n["direction"]=="east")["resources"].append("berry_b")
        from lab.determinism import canonical_causal_bytes,sha256_hex
        row["perceptual_policy_choices"][0]["input_sha256"]=sha256_hex(
            canonical_causal_bytes(snap)
        )
        with self.assertRaisesRegex(ValueError,"decision used a state unavailable"):
            self.review(rows=altered)

    def test_physical_example_sha_tampered_rejected(self):
        altered=deepcopy(self.rows)
        item=next(x for x in altered if x["physical_steps_external"])
        item["physical_steps_external"][0]["physical_example_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"physical receipt"):
            self.review(rows=altered)

    def test_adversarial_consistent_sha_but_broken_continuity_rejected(self):
        altered=deepcopy(self.rows)
        row=next(x for x in altered if x["physical_step_count"]>=3)
        ex=row["physical_steps_external"][0]
        ex["physical_example"]["observed_next_state"]["body"]["food"]+=2.0
        ex["physical_after_external_only"]["body"]["food"]+=2.0
        from lab.determinism import canonical_causal_bytes,sha256_hex
        ex["physical_example_sha256"]=sha256_hex(canonical_causal_bytes(
            ex["physical_example"]
        ))
        with self.assertRaisesRegex(ValueError,"chain|state"):
            self.review(rows=altered)

    def test_physical_death_falsified_rejected(self):
        altered=deepcopy(self.rows)
        dead=next(x for x in altered if x["physical_terminal_step_external_only"])
        dead["physical_terminal_step_external_only"]=None
        with self.assertRaisesRegex(ValueError,"external terminal step"):
            self.review(rows=altered)

    def test_postmortem_technical_capture_as_lived_rejected(self):
        altered=deepcopy(self.rows)
        dead=next(x for x in altered if x["physical_terminal_step_external_only"])
        dead["lived_postterminal_capture"]={"future":"invented"}
        with self.assertRaisesRegex(ValueError,"postmortem"):
            self.review(rows=altered)

    def test_terminal_physics_without_integrity_loss_rejected(self):
        altered=deepcopy(self.rows)
        dead=next(x for x in altered if x["physical_terminal_step_external_only"])
        ex=dead["physical_steps_external"][-1]
        ex["terminal_external_only"]=False
        ex["physical_example"]["terminal"]=False
        from lab.determinism import canonical_causal_bytes,sha256_hex
        ex["physical_example_sha256"]=sha256_hex(
            canonical_causal_bytes(ex["physical_example"])
        )
        with self.assertRaisesRegex(ValueError,"terminal flag conflicts"):
            self.review(rows=altered)

    def test_stage6_future_ingestion_in_own_history_rejected(self):
        altered=deepcopy(self.rows)
        row=next(x for x in altered if x["stage6_shadow"] is not None)
        future=row["physical_steps_external"][-1]["physical_example"]
        row["stage6_shadow"]["own_physical_examples"].append(future)
        with self.assertRaisesRegex(ValueError,"Stage6 history contaminated"):
            self.review(rows=altered)

    def test_stage6_foreign_world_history_rejected(self):
        altered=deepcopy(self.rows)
        row=next(x for x in altered if x["stage6_shadow"] is not None)
        foreign=next(x for x in altered if x is not row and x["physical_steps_external"])
        row["stage6_shadow"]["own_physical_examples"][0]=foreign[
            "physical_steps_external"
        ][0]["physical_example"]
        with self.assertRaisesRegex(ValueError,"Stage6 history contaminated"):
            self.review(rows=altered)

    def test_stage6_forged_predictable_first_edge_rejected(self):
        altered=deepcopy(self.rows)
        row=next(x for x in altered if x["stage6_shadow"] is not None)
        row["stage6_shadow"]["stage6_root_available_edges"]=1
        with self.assertRaisesRegex(ValueError,"root exact-key"):
            self.review(rows=altered)

    def test_stage6_oracle_leak_rejected(self):
        altered=deepcopy(self.rows)
        row=next(x for x in altered if x["stage6_shadow"] is not None)
        row["stage6_shadow"]["oracle_fed_to_shadow"]=True
        with self.assertRaisesRegex(ValueError,"Stage6 shadow"):
            self.review(rows=altered)

    def test_wrong_full_cohort_denominator_rejected(self):
        with self.assertRaisesRegex(ValueError,"wrong original|incomplete"):
            self.review(rows=self.rows[:-1])

    def test_duplicate_physical_world_id_rejected(self):
        altered=deepcopy(self.rows)
        altered[0]["world_id"]=altered[1]["world_id"]
        with self.assertRaisesRegex(ValueError,"identifier invalid|duplicate"):
            self.review(rows=altered)

    def test_summary_falsely_reclassifies_death_as_food_success_rejected(self):
        changed=deepcopy(self.summary)
        changed["surviving_food_gain_at_least_5"]=60
        with self.assertRaisesRegex(ValueError,"original Z summary"):
            self.review(summary=changed)

    def test_visible_alternative_vs_inaccessible_passability_control(self):
        local=next(x for x in self.rows if x["layout_external_only"]=="B_LOCAL")
        blocked=next(x for x in self.rows if x["layout_external_only"]=="B_EAST_BLOCKED")
        remote=next(x for x in self.rows if x["layout_external_only"]=="B_EAST_TWO_STEPS")
        cmd,reason=independently_decide(
            local["initial_first_person"],local["protocol_precommitted"],[],
        )
        self.assertEqual(cmd,{"primitive":"collecter","parameters":{"target":"berry_b"}})
        self.assertEqual(reason,"local_berry_b_visible")
        cmd,reason=independently_decide(
            blocked["initial_first_person"],blocked["protocol_precommitted"],[],
        )
        self.assertIsNone(cmd)
        self.assertEqual(reason,"eastern_berry_b_visible_but_blocked")
        cmd,reason=independently_decide(
            remote["initial_first_person"],"OBSERVED_ONLY",[],
        )
        self.assertIsNone(cmd)
        self.assertNotIn(eat_b(),independent_candidate_commands(remote["initial_first_person"]))

    def test_independent_auditor_never_imports_worldbody_or_planner(self):
        path=(Path(__file__).resolve().parents[1]/
              "scripts/audit_stage12_issue110_b_a230za_independent_archives.py")
        text=path.read_text()
        for forbidden in (
            "from lab.world import","import WorldBody","SimulatorPlanner(",
            "FrozenTableEquipment(", "EquipmentCorpusRecorder(",
            "from run_stage12_issue110_b_a230z_alternative_food import",
            "import Oracle",
        ):
            self.assertNotIn(forbidden,text)


if __name__=="__main__":
    unittest.main()
