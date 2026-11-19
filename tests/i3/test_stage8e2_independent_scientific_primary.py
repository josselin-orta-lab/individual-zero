"""Prospective Stage8-E2 second t-test cross-check; no real or simulated World."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest

from i3.lab import stage8e_causal_gamma_population_test as DESIGN
from tools import stage8e2_independent_primary_verification as SECOND
from tools import stage8e2_prospective_science as SCIENCE


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8")


def _fixture(positive: bool = True):
    plan = {
        "schema": SECOND.SCIENCE_SCHEMA,
        "scientific_admission": True,
        "preexposure_scientific_verdict": "NOT_ISSUED",
        "source_engine_head": SECOND.ENGINE_HEAD,
        "source_engine_sha256": SECOND.ENGINE_SHA,
        "source_protocol_head": "b"*40,
        "population_units": 64,
        "planned_original_lives": 64512,
        "planned_g2_original_lives": 36864,
        "native_generator_plan": {"allocation_sha256": "2"*64},
        "technical_evidence_sha256": "a"*64,
        "no_retry": True,
        "primary": SCIENCE.PRIMARY,
        "primary_sha256": sha256(_canonical(SCIENCE.PRIMARY)).hexdigest(),
    }
    plan["allocation_sha256"] = sha256(_canonical(plan)).hexdigest()
    rows = []
    for p in range(64):
        if positive:
            d = 10.0 + (p % 7) * 0.25
        else:
            d = float(p % 5 - 2)
        rows.append({
            "population": p,
            "mean_G2_steps": {
                "S_sham": 110.0 + d, "M_sham": 100.0,
                "S_swap": 110.0, "M_swap": 100.0,
            },
            "original_lives_by_arm": {arm: 144 for arm in SECOND.ARMS},
        })
    primary = DESIGN.analyze_design_only(rows)
    cold = {
        "status": "ALL_64512_NATIVE_ORIGINAL_GZIP_REAUDITED_NO_SCIENCE",
        "original_lives_rehashed": 64512,
        "source_git_head": SECOND.ENGINE_HEAD,
        "source_files_sha256": SECOND.ENGINE_SHA,
        "allocation_sha256": "2"*64,
    }
    outcome = {
        "schema": SECOND.SCIENCE_SCHEMA + "/from-cold-originals",
        "status": SECOND.PASS if primary["nominal_design_only_nonzero_compatible"]
                else SECOND.NO,
        "scientific_admission": True,
        "science_plan_file_sha256": sha256(_canonical(plan)).hexdigest(),
        "science_allocation_sha256": plan["allocation_sha256"],
        "source_engine_head": SECOND.ENGINE_HEAD,
        "source_protocol_head": plan["source_protocol_head"],
        "frozen_primary_sha256": plan["primary_sha256"],
        "technical_evidence_sha256": plan["technical_evidence_sha256"],
        "original_native_lives_rehashed": 64512,
        "G2_original_lives_scored": 36864,
        "native_mutations_reconstructed": 6144,
        "population_units": 64,
        "F0_only": True, "joint_block_not_gamma3_alone": True,
        "external_attestation": False, "previous_technical_lives_excluded": True,
        "cold_audit": cold,
        "cold_originals_sha256": sha256(_canonical(cold)).hexdigest(),
        "original_population_means": rows,
        "primary": primary,
        "positive_population_DID": sum(x>0 for x in primary["all_64_population_did"]),
        "negative_population_DID": sum(x<0 for x in primary["all_64_population_did"]),
        "zero_population_DID": sum(x==0 for x in primary["all_64_population_did"]),
    }
    return plan, outcome


class Stage8E2IndependentPrimaryTests(unittest.TestCase):
    def _check(self, p, result):
        with tempfile.TemporaryDirectory() as temp:
            parent = Path(temp)
            (parent / "plan.json").write_bytes(_canonical(p))
            (parent / "pin").write_text(sha256(_canonical(p)).hexdigest())
            (parent / "result.json").write_bytes(_canonical(result))
            return SECOND.verify(str(parent/"plan.json"),
                                 str(parent/"pin"), str(parent/"result.json"))

    def test_true_positive_frozen_two_sided_student(self):
        plan, result = _fixture(True)
        check = self._check(plan, result)
        self.assertEqual(check["scientific_status"], SECOND.PASS)
        self.assertEqual(check["primary_population_units"], 64)
        self.assertGreater(check["two_sided_97_5_percent_interval_steps"][0],0)
        self.assertFalse(check["gamma3_alone_not_identified"] is False)

    def test_valid_null_result_is_not_promoted(self):
        p, result = _fixture(False)
        check = self._check(p, result)
        self.assertEqual(check["scientific_status"], SECOND.NO)
        lo, hi = check["two_sided_97_5_percent_interval_steps"]
        self.assertLessEqual(lo, 0)
        self.assertGreaterEqual(hi, 0)

    def test_altered_population_mean_or_t_is_rejected(self):
        p, result = _fixture(True)
        for problem in ("mean", "t", "status", "sha", "count", "cold"):
            x = deepcopy(result)
            if problem=="mean":
                x["original_population_means"][0]["mean_G2_steps"]["S_sham"] += 1.
            elif problem=="t":
                x["primary"]["primary_gamma_block_did_t_statistic"] += 1.
            elif problem=="status":
                x["status"] = SECOND.NO
            elif problem=="sha":
                x["science_plan_file_sha256"] = "f"*64
            elif problem=="count":
                x["original_population_means"][0]["original_lives_by_arm"]["S_swap"] = 143
            else:
                x["cold_audit"]["original_lives_rehashed"] = 64511
            with self.subTest(problem=problem), self.assertRaises(ValueError):
                self._check(p, x)

    def test_missing_population_and_changed_alpha_are_rejected(self):
        p, result = _fixture(True)
        result["original_population_means"].pop()
        with self.assertRaises(ValueError):
            self._check(p, result)
        p, result = _fixture(True)
        p["primary"]["two_sided_alpha"] = 0.05
        p["primary_sha256"] = sha256(_canonical(p["primary"])).hexdigest()
        p["allocation_sha256"] = sha256(_canonical({
            k: v for k, v in p.items() if k != "allocation_sha256"
        })).hexdigest()
        with self.assertRaises(ValueError):
            self._check(p, result)


if __name__ == "__main__":
    unittest.main()
