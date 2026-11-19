"""Pure Stage8-E2 science admission tests, NO World or native births.

Synthetic technical receipts used here are structural fixtures only. They do
not replace the actual previously published hashes and original gzip audit.
"""
from copy import deepcopy
from hashlib import sha256 as _real_sha256
from unittest import TestCase
from unittest.mock import patch

from tools import stage8e2_prospective_science as S

SCIENCE_ROOT = "1234567890abcdef" * 4
WRAPPER_HEAD = "abcdef1234567890abcdef1234567890abcdef12"
WRAPPER_SHA = "f" * 64
ABS_ROOT = "/tmp/future-independent-stage8e2-science-originals"


def _technical_plan(version):
    return {
        "root_hex": ("1" if version == "3.11" else "2") * 64,
        "archive_root": "/tmp/source-technical-" + version,
        "source_git_head": S.ENGINE_HEAD,
        "source_files_sha256": S.ENGINE_SHA,
        "allocation_sha256": S.TECHNICAL_PLAN_ALLOCATIONS[version],
        "scientific_admission": False,
        "g2_heldout_worlds_sha256": ("3" if version == "3.11" else "4") * 64,
    }


def _evidence():
    plans = {v: _technical_plan(v) for v in ("3.11", "3.12")}
    audits = {}
    for version in plans:
        audits[version] = {
            "schema": S.C.SCHEMA, "status": S.COLD_PASS,
            "original_lives_rehashed": 64512, "scientific_admission": False,
            "source_git_head": S.ENGINE_HEAD,
            "source_files_sha256": S.ENGINE_SHA,
            "allocation_sha256": plans[version]["allocation_sha256"],
            "g0_g1_g2_manifest_sha256": (["b"*64, "c"*64, "d"*64]
                                              if version == "3.11"
                                              else ["1"*64, "2"*64, "3"*64]),
            "parentage_audit_sha256": ["e"*64, "f"*64],
            "phase_chain_sha256": ("7" if version == "3.11" else "8") * 64,
        }
    return {
        "schema": S.EVIDENCE_SCHEMA, "technical_run_id": S.TECHNICAL_RUN_ID,
        "technical_gate_artifact_id": S.TECHNICAL_GATE_ARTIFACT_ID,
        "technical_gate_file_sha256": S.TECHNICAL_GATE_FILE_SHA256,
        "technical_cold_file_sha256": S.TECHNICAL_COLD_FILE_SHA256,
        "technical_plan_artifact_ids": S.TECHNICAL_PLAN_ARTIFACT_IDS,
        "technical_cold_artifact_ids": S.TECHNICAL_COLD_ARTIFACT_IDS,
        "technical_plan_file_sha256": S.TECHNICAL_PLAN_SHAS,
        "technical_plans": plans, "cold_audits": audits,
        "technical_gate": {
            "schema": S.R.SCHEMA, "status": S.TECH_PASS,
            "source_git_head": S.ENGINE_HEAD,
            "source_files_sha256": S.ENGINE_SHA,
            "total_original_lives_claimed": 129024,
            "total_mutations_claimed": 12288,
            "scientific_admission": False,
            "science_verdict": "NOT_ISSUED", "science_lives_generated": 0,
            "python_versions": ["3.11", "3.12"],
        },
    }


def _native_plan():
    return {
        "planned_lives": 64512, "planned_mutations": 6144,
        "scientific_admission": False, "frozen_method": S.T.METHOD,
        "g2_heldout_worlds_sha256": "5"*64,
        "allocation_sha256": "6"*64,
        "root_hex": SCIENCE_ROOT,
        "archive_root": ABS_ROOT + "/native-originals",
    }


class Stage8E2SciencePreexposureTests(TestCase):
    def setUp(self):
        self.evidence = _evidence()
        # Mock only the artifact SHA of the synthetic technical plan fixture;
        # production always checks the REAL published immutable plan bytes.
        fake_canonical = {
            v: S.dump(_technical_plan(v)) for v in ("3.11", "3.12")
        }
        class _FakeHash:
            def __init__(self, value):
                self.value = value
            def hexdigest(self):
                return self.value
        def _synthetic_sha(raw):
            for version, data in fake_canonical.items():
                if raw == data:
                    return _FakeHash(S.TECHNICAL_PLAN_SHAS[version])
            return _real_sha256(raw)
        self.patcher_sha = patch.object(S, "sha256", side_effect=_synthetic_sha)
        self.patcher_sha.start()
        self.addCleanup(self.patcher_sha.stop)
        self.patcher_verify = patch.object(S.T, "verify_plan", side_effect=lambda p: p)
        self.patcher_native = patch.object(S.T, "make_plan",
                                          side_effect=lambda *x: _native_plan())
        self.patcher_verify.start()
        self.patcher_native.start()
        self.addCleanup(self.patcher_verify.stop)
        self.addCleanup(self.patcher_native.stop)

    def test_two_source_pinned_technical_cold_audits_required(self):
        self.assertEqual(S.verify_technical_evidence(self.evidence), self.evidence)
        self.assertEqual(S.TECHNICAL_RUN_ID, 44536464441)
        self.assertEqual(S.PRIMARY["population_units"], 64)
        self.assertEqual(S.PRIMARY["G2_lives_per_arm_population"], 144)
        self.assertEqual(S.PRIMARY["two_sided_alpha"], 0.025)
        self.assertEqual(S.PRIMARY["t_critical_df63"], 2.2962367715148795)

    def test_new_science_plan_frozen_without_birth(self):
        p = S.make_science_plan(SCIENCE_ROOT, WRAPPER_HEAD,
                                WRAPPER_SHA, ABS_ROOT, self.evidence)
        self.assertEqual(S.verify_science_plan(p), p)
        self.assertEqual(p["planned_original_lives"], 64512)
        self.assertEqual(p["planned_g2_original_lives"], 36864)
        self.assertEqual(p["science_lives_created_at_preexposure"], 0)
        self.assertTrue(p["scientific_admission"])
        self.assertFalse(p["native_generator_plan"]["scientific_admission"])
        self.assertEqual(p["preexposure_scientific_verdict"], "NOT_ISSUED")
        self.assertNotIn(SCIENCE_ROOT,
                         (v["root_hex"] for v in self.evidence["technical_plans"].values()))
        self.assertEqual(p["source_engine_head"], S.ENGINE_HEAD)

    def test_breaks_if_any_cold_audit_missing_or_forged(self):
        for key,value in (
            ("original_lives_rehashed", 64511),
            ("status", "NOT_PASSED"),
            ("scientific_admission", True),
            ("source_files_sha256", "0"*64),
        ):
            bad = deepcopy(self.evidence)
            bad["cold_audits"]["3.12"][key] = value
            with self.subTest(field=key), self.assertRaises(PermissionError):
                S.verify_technical_evidence(bad)

    def test_reused_original_roots_or_entropies_refused(self):
        with self.assertRaises(PermissionError):
            S.make_science_plan("1"*64, WRAPPER_HEAD, WRAPPER_SHA,
                                ABS_ROOT, self.evidence)
        bad = deepcopy(self.evidence)
        bad["technical_plans"]["3.12"]["root_hex"] = "1"*64
        with self.assertRaises(PermissionError):
            S.verify_technical_evidence(bad)

    def test_after_preexposure_no_method_or_sha_substitution(self):
        good = S.make_science_plan(SCIENCE_ROOT, WRAPPER_HEAD,
                                   WRAPPER_SHA, ABS_ROOT, self.evidence)
        for field, replacement in (
            ("primary_sha256", "0"*64),
            ("planned_original_lives", 64511),
            ("source_protocol_file_sha256", "1"*64),
            ("allocation_sha256", "2"*64),
            ("status", "SCIENCE_ALREADY_EXPOSED"),
            ("preexposure_scientific_verdict", "POSITIVE"),
        ):
            changed = deepcopy(good)
            changed[field] = replacement
            with self.subTest(field=field), self.assertRaises(
                    (PermissionError, ValueError)):
                S.verify_science_plan(changed)

    def test_no_science_result_from_technical_inputs(self):
        p = S.make_science_plan(SCIENCE_ROOT, WRAPPER_HEAD,
                                WRAPPER_SHA, ABS_ROOT, self.evidence)
        with patch.object(S.C, "cold_audit",
                          side_effect=ValueError("missing original gzip")):
            with self.assertRaises((ValueError, FileNotFoundError)):
                S.reduce_after_independent_cold_audit(
                    "/tmp/nonexistent-science-plan.json", "b"*64,
                    "/tmp/nonexistent-native-plan.json", ABS_ROOT)


if __name__ == "__main__":
    import unittest
    unittest.main()
