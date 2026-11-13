"""Source-only Stage-6-light methodological preauthorization, never a World runner.

The owner has not authorized a Stage-6-light life, engineering rehearsal or
scientific index. This test must not import i3 modules or call a laboratory
entrypoint. It checks an inert protocol contract, not biological validity.
"""
from __future__ import annotations

import copy
import json
from math import comb
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
STUDY = ROOT / "src/i3/docs/studies/stage6-light-preparation"
MANIFEST = STUDY / "STAGE6_LIGHT_PROTOCOL_METHOD_V1.json"
DOCUMENT = STUDY / "STAGE6_LIGHT_PROTOCOL_METHOD_V1_2026-11-13.md"
ORIGINAL_DRAFT = STUDY / "STAGE6_LIGHT_PROTOCOL_DRAFT_2026-11-13.md"

DENIED = (
    "worlds_allowed",
    "cohorts_allowed",
    "engineering_rehearsal_allowed",
    "science_admission_allowed",
    "auto_start_allowed",
    "adr0017_lineage_exception_accepted",
)
UNASSIGNED = (
    "owner_decision_sha",
    "owner_authorized_world_indices",
    "assigned_world_seeds",
    "assigned_founder_seeds",
    "execution_source_sha",
    "execution_transport_fingerprint",
    "independent_allocation_manifest_sha256",
    "full_scale_python311_rehearsal_sha",
    "full_scale_python312_rehearsal_sha",
)


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _assert_non_admission(d: dict) -> None:
    if d.get("schema") != "i3-stage6-light-method-preauth/v1":
        raise AssertionError("unexpected contract schema")
    if d.get("status") != "METHOD_FIXED_PREAUTH_NOT_EXECUTABLE":
        raise AssertionError("only an inert method contract is supported")
    if d.get("phase") != "design_only":
        raise AssertionError("execution phase not admitted")
    a = d["authorization"]
    if set(a) != set(DENIED) | set(UNASSIGNED):
        raise AssertionError("unknown or missing authorization field")
    if any(a[k] is not False for k in DENIED):
        raise AssertionError("cohort or World permission must remain false")
    if any(a[k] is not None for k in UNASSIGNED):
        raise AssertionError("owner or source/index binding must remain absent")
    custody = d["custody"]
    if custody["rehearsal_worlds_and_lives_now_allowed"] is not False:
        raise AssertionError("no engineering rehearsal has been approved")
    if custody["scientific_worlds_and_lives_now_allowed"] is not False:
        raise AssertionError("no science has been approved")
    if custody["per_generation_selection_requires_separate_adr0017_acceptance"] is not True:
        raise AssertionError("cannot bypass the lineage-specific ADR-0017 decision")
    if custody["generation_retry_allowed"] is not False:
        raise AssertionError("cannot retry consumed births")
    if custody["postmortem_resume_allowed"] is not False:
        raise AssertionError("cannot revive a dead individual")


class Stage6LightPreauthProtocolTests(unittest.TestCase):
    def test_non_executable_contract_cannot_act_as_owner_lift(self):
        d = _manifest()
        _assert_non_admission(d)
        self.assertEqual(d["protocol_id"], "I3_STAGE6_LIGHT_METHOD_V1")
        self.assertEqual(d["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(d["stage2_disposition"], "HOLD_NO_VERDICT")
        self.assertEqual(d["reference_policy"], "P1.3 funded-v2")
        self.assertEqual(d["active_generation"], "I1")
        self.assertEqual(d["reference_generation"], "I3")
        self.assertEqual(d["data_origin"]["stage6_light_exposure_count_at_design"], 0)
        self.assertEqual(d["data_origin"]["historical_first_execution_time"],
                         "INDEPENDENT_PRE_EXECUTION_TIME_NOT_ATTESTED")

    def test_mutated_permission_or_fake_scientific_pin_must_fail_closed(self):
        baseline = _manifest()
        for field in DENIED:
            with self.subTest(permission=field):
                fake = copy.deepcopy(baseline)
                fake["authorization"][field] = True
                with self.assertRaises(AssertionError):
                    _assert_non_admission(fake)
        for field in UNASSIGNED:
            with self.subTest(forged_binding=field):
                fake = copy.deepcopy(baseline)
                fake["authorization"][field] = ["fake"] if field.endswith("seeds") else "fake"
                with self.assertRaises(AssertionError):
                    _assert_non_admission(fake)
        for field, changed in (
            ("status", "AUTHORIZED"),
            ("phase", "science"),
            ("schema", "i3-stage6-light-executable/v1"),
        ):
            fake = copy.deepcopy(baseline)
            fake[field] = changed
            with self.assertRaises(AssertionError):
                _assert_non_admission(fake)
        for field in ("rehearsal_worlds_and_lives_now_allowed",
                      "scientific_worlds_and_lives_now_allowed",
                      "generation_retry_allowed", "postmortem_resume_allowed"):
            fake = copy.deepcopy(baseline)
            fake["custody"][field] = True
            with self.assertRaises(AssertionError):
                _assert_non_admission(fake)

    def test_frozen_design_costs_and_unique_logical_coordinates(self):
        d = _manifest()
        p, q = d["design"], d["plan"]
        self.assertEqual(p["populations"], 16)
        self.assertEqual(p["founders_per_population"], 24)
        self.assertEqual(p["generations"], [0, 1, 2])
        self.assertEqual(p["arms"], ["selected", "random_parent"])
        self.assertEqual(p["families"], ["stable", "depletion", "pulse"])
        self.assertEqual(p["repeats_per_family"], 2)
        self.assertEqual(p["horizon_steps"], 400)
        self.assertEqual(p["mutation_scale"], 0.1)
        self.assertEqual(p["reference_genome_version"], 4)
        self.assertTrue(p["g0_shared_one_original"])
        self.assertEqual(p["parent_selection_weights"], list(range(24, 0, -1)))
        self.assertEqual(
            p["fitness_sort"],
            ["censored_lives_desc", "total_lived_steps_desc", "slot_asc"],
        )
        self.assertEqual(p["random_parent"], "uniform_24_slots_no_fitness_tuning")
        self.assertEqual(p["heritable_material"], "generic_genome_only_no_memory_no_world_fact")
        self.assertEqual(p["primary_gene"],
                         "beta_u_eff = beta_u * (1 + 0.5 * temperament.exploration)")

        pos = [((population*3+generation)*3+family_index)*2+repeat
               for population in range(16)
               for generation in range(3)
               for family_index in range(3)
               for repeat in range(2)]
        self.assertEqual(pos, list(range(288)))
        self.assertEqual(q["world_coordinate_formula"],
                         "((population*3+generation)*3+family_index)*2+repeat")
        self.assertEqual(q["logical_world_coordinates"], len(pos))
        self.assertEqual(q["genotype_founders"], 16 * 24)
        self.assertEqual(q["lives_by_generation"],
                         {"G0": 16*24*6, "G1": 16*2*24*6, "G2": 16*2*24*6})
        self.assertEqual(q["total_lives_if_later_authorized"], 11520)
        self.assertEqual(q["max_physical_steps_if_later_authorized"], 11520*400)
        self.assertFalse(q["actual_world_indices_assigned"])
        self.assertFalse(q["historic_cohort_reuse_allowed"])
        self.assertFalse(q["reserve_seed_reuse_allowed"])
        self.assertTrue(q["distinct_worlds_between_populations_required"])
        self.assertTrue(q["paired_worlds_and_life_seeds_within_population"])

    def test_conservative_exact_two_sided_sign_rule_and_sentinels(self):
        d = _manifest()["analysis"]
        n, k = d["n_units"], d["threshold_concordant_signs"]
        self.assertEqual((n, k), (16, 13))
        numerator = 2 * sum(comb(n, j) for j in range(k, n+1))
        denominator = 2 ** n
        self.assertEqual((numerator, denominator), (1394, 65536))
        self.assertEqual(d["two_sided_binomial_null"]["numerator"], numerator)
        self.assertEqual(d["two_sided_binomial_null"]["denominator"], denominator)
        self.assertEqual(d["two_sided_binomial_null"]["requires"],
                         "independent_symmetrically_distributed_nonzero_signs")
        self.assertEqual(d["signs_zero_policy"],
                         "zero_neither_positive_nor_negative_keep_n_16")
        self.assertEqual(d["neutral_markers"],
                         ["omega", "temperament.affiliation", "temperament.reward_sensitivity"])
        self.assertEqual(d["neutral_alert_if_markers_reach_threshold"], 1)
        self.assertEqual(d["invalid_if_markers_reach_threshold_at_least"], 2)
        self.assertEqual(d["positive_status"], "STAGE6_LIGHT_SIGN_CONCORDANCE_PASS")
        self.assertEqual(d["negative_status"], "STAGE6_LIGHT_NO_SIGN_CONCORDANCE")
        self.assertEqual(d["not_run_status"], "STAGE6_LIGHT_NOT_RUN_NO_AUTHORIZATION")
        self.assertFalse(d["modeled_power_is_guarantee"])
        self.assertFalse(d["forced_actions_allowed"])
        self.assertFalse(d["reclassification_after_exposure_allowed"])

    def test_live_registry_manifest_and_historical_draft_stay_separate(self):
        registry = json.loads((ROOT / "config/engine-registry.json").read_text(encoding="utf-8"))
        active = json.loads((ROOT / "src/i3/ACTIVE_SURFACE.json").read_text(encoding="utf-8"))
        engine = json.loads((ROOT / "src/i3/engine.json").read_text(encoding="utf-8"))
        self.assertEqual(registry["active_generation"], "I1")
        self.assertEqual(registry["reference_generation"], "I3")
        self.assertEqual(engine["status"], "proposal")
        self.assertEqual(engine["activation"], "NOT_REGISTERED_NOT_EXECUTABLE")
        self.assertFalse(active["governance"]["fresh_lived_worlds_allowed"])
        self.assertFalse(active["governance"]["scientific_gate_authorized"])
        self.assertFalse(active["governance"]["other_world_indices_authorized"])
        self.assertFalse(active["governance"]["next_scientific_cohort_authorized"])
        self.assertFalse(active["governance"]["all_new_worlds_currently_authorized"])
        self.assertTrue(ORIGINAL_DRAFT.is_file())
        self.assertIn("BROUILLON, NON GELÉ, NON AUTORISÉ",
                      ORIGINAL_DRAFT.read_text(encoding="utf-8")[:280])
        doc = DOCUMENT.read_text(encoding="utf-8")
        self.assertIn("METHOD_FIXED_PREAUTH_NOT_EXECUTABLE", doc)
        self.assertIn("11 520", doc)
        self.assertIn("13/16", doc)
        self.assertIn("aucun nouveau World", doc)
        self.assertIn("STAGE6_LIGHT_NOT_RUN_NO_AUTHORIZATION", doc)


if __name__ == "__main__":
    unittest.main()
