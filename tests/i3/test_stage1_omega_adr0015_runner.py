"""Stage-1 omega ADR-0015 sharded runner: software arithmetic only."""
from copy import deepcopy
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.lab import stage0_design as S
from i3.lab import stage1_omega_adr0015_design as D
from i3.lab import stage1_omega_adr0015_runner as R
from i3.modules.genome import digest

EXECUTION = "a" * 40
SOURCE = "b" * 64


def _probe(population, phase):
    return [{
        "population": population,
        "family": row["family"],
        "world_index": row["index"],
        "world_seed": row["world_seed"],
        "steps_survived": 200,
        "censored": False,
        "interpretation":
            "DESCRIPTIVE_SYSTEMATIC_SEARCH_NOT_COST_MATCHED",
    } for row in S.world_rows(phase)
       if row["population"] == population]


def _top_omega(population):
    return tuple(sorted(
        D.founder_seeds(population),
        key=lambda seed: (
            -D.genome_for_arm("candidate", seed)["genes"]["omega"],
            seed))[:D.KEEP])


def selection_shards():
    shards = []
    protocol = R.protocol_manifest()["sha256"]
    for p in range(D.POPULATIONS):
        top = set(_top_omega(p))
        ref_top = set(D.founder_seeds(p)[:D.KEEP])
        worlds = [
            row for row in S.world_rows("selection")
            if row["population"] == p]
        for arm in ("reference", "candidate"):
            receipts = []
            chosen = ref_top if arm == "reference" else top
            for seed in D.founder_seeds(p):
                for world in worlds:
                    survive = seed in chosen
                    receipts.append({
                        "gate": {
                            "candidate_seed": seed,
                            "world_index": world["index"],
                            "terminal":
                                "censored" if survive else "dead",
                            "steps_lived": 400 if survive else 100,
                            "genome_digest":
                                digest(D.genome_for_arm(arm, seed)),
                        },
                        "family": world["family"],
                        "world_seed": world["world_seed"],
                        "life_seed": world["life_seed"],
                        "world_sha256":
                            f"world-selection-p{p}-i{world['index']}",
                        "source_sha256": SOURCE,
                        "competition_steps": 400 if survive else 100,
                        "cognitive_shortfall_steps": 0,
                        "paid": {"energy": 1.0, "vigilance": 2.0},
                        "inactive_steps": 0,
                        "frontier_information": None,
                        "original": {"file": "synthetic"},
                    })
            shards.append({
                "schema": R.SELECTION_SHARD,
                "status": "COMPLETE",
                "protocol": R.PROTOCOL,
                "protocol_sha256": protocol,
                "execution_sha": EXECUTION,
                "source_sha256": SOURCE,
                "population": p,
                "arm": arm,
                "expected_lives": len(receipts),
                "completed_lives": len(receipts),
                "receipts": receipts,
                "systematic_reference_probe":
                    _probe(p, "selection") if arm == "reference" else None,
            })
    return shards


def validation_shards(selection):
    shards = []
    protocol = R.protocol_manifest()["sha256"]
    for p in range(D.POPULATIONS):
        worlds = [
            row for row in S.world_rows("validation")
            if row["population"] == p]
        for arm in D.ARMS:
            selected_key = "reference" if arm == "reference" else "candidate"
            selected = tuple(selection["selected"][selected_key][str(p)])
            receipts = []
            for seed in selected:
                for world in worlds:
                    terminal, steps = "censored", D.HORIZON
                    if arm == "omega_zero" and seed == selected[0]:
                        target = "stable" if p < 4 else "pulse"
                        if (world["family"] == target
                                and world["repeat"] == 0):
                            terminal, steps = "dead", D.HORIZON - 1
                    if world["family"] == "depletion":
                        revision_status = "REACQUIRED"
                        revision_latency = (
                            20 if arm == "reference" else 10)
                    else:
                        revision_status = revision_latency = None
                    receipts.append({
                        "gate": {
                            "arm": arm,
                            "population": p,
                            "family": world["family"],
                            "world_index": world["index"],
                            "founder_seed": seed,
                            "genome_digest":
                                digest(D.genome_for_arm(arm, seed)),
                            "terminal": terminal,
                            "steps_lived": steps,
                            "revision_status": revision_status,
                            "revision_latency": revision_latency,
                        },
                        "world_seed": world["world_seed"],
                        "life_seed": world["life_seed"],
                        "world_sha256":
                            f"world-validation-p{p}-i{world['index']}",
                        "source_sha256": SOURCE,
                        "competition_steps": steps,
                        "cognitive_shortfall_steps": 0,
                        "paid": {"energy": 1.0, "vigilance": 2.0},
                        "inactive_steps": 0,
                        "frontier_information": None,
                        "revision": None,
                        "original": {"file": "synthetic"},
                    })
            replay = [{
                "world_index": world["index"],
                "founder_seed": selected[0],
                "identical": True,
                "original": {"file": "synthetic-replay"},
            } for world in worlds]
            shards.append({
                "schema": R.VALIDATION_SHARD,
                "status": "COMPLETE",
                "protocol": R.PROTOCOL,
                "protocol_sha256": protocol,
                "execution_sha": EXECUTION,
                "source_sha256": SOURCE,
                "selection_sha256": selection["sha256"],
                "population": p,
                "arm": arm,
                "selected_seeds": list(selected),
                "expected_main_lives": len(receipts),
                "completed_main_lives": len(receipts),
                "expected_replays": len(replay),
                "completed_replays": len(replay),
                "receipts": receipts,
                "rank0_replays": replay,
                "systematic_reference_probe":
                    _probe(p, "validation") if arm == "reference" else None,
            })
    return shards


class OmegaAdr0015RunnerTests(unittest.TestCase):
    def test_import_is_detached_from_world_and_runtime(self):
        root = str(Path(__file__).resolve().parents[2] / "src")
        subprocess.run([
            sys.executable, "-c",
            "import sys; sys.path.insert(0, " + repr(root) + "); "
            "import i3.lab.stage1_omega_adr0015_runner; "
            "assert 'i3.modules.world' not in sys.modules; "
            "assert 'i3.runtime.life' not in sys.modules"
        ], check=True)

    def test_protocol_manifest_freezes_shard_barriers_and_counts(self):
        p = R.protocol_manifest()
        self.assertEqual(len(p["selection_shards"]), 16)
        self.assertEqual(len(p["validation_shards"]), 24)
        self.assertEqual(p["selection_lives_per_shard"], 240)
        self.assertEqual(p["validation_main_lives_per_shard"], 30)
        self.assertEqual(p["validation_rank0_replays_per_shard"], 6)
        self.assertEqual(
            p["selection_barrier"], "ALL_16_COMPLETE_BEFORE_ANY_RANKING")
        self.assertEqual(
            p["validation_barrier"], "ALL_24_COMPLETE_BEFORE_GATE")
        self.assertEqual(p["retry_policy"], "NO_RETRY_NO_REPLACEMENT")

    def test_case_metadata_uses_only_frozen_allocations_and_equal_genes(self):
        cases = R.selection_cases(0, "candidate")
        self.assertEqual(len(cases), 240)
        self.assertEqual(
            {row["world_index"] for row in cases}, set(range(72, 78)))
        self.assertEqual(
            {row["world_seed"] for row in cases}, set(range(10072, 10078)))
        self.assertEqual(len({row["founder_seed"] for row in cases}), 40)

        selection = R.aggregate_selection(selection_shards())
        candidate = R.validation_cases(0, "candidate", selection)
        zero = R.validation_cases(0, "omega_zero", selection)
        self.assertEqual(len(candidate), 30)
        self.assertEqual(len(zero), 30)
        for a, b in zip(candidate, zero):
            self.assertEqual(a["founder_seed"], b["founder_seed"])
            ga = D.genome_for_arm("candidate", a["founder_seed"])
            gz = D.genome_for_arm("omega_zero", b["founder_seed"])
            for name in ga["genes"]:
                if name != "omega":
                    self.assertEqual(ga["genes"][name], gz["genes"][name])
            self.assertEqual(gz["genes"]["omega"], 0.0)

    def test_launch_guard_checks_exact_source_protocol_and_p2_blobs(self):
        protocol = R.protocol_manifest()["sha256"]
        with patch.object(
                R, "_git",
                side_effect=[
                    EXECUTION, "",
                    S.ECOLOGY_BLOB, R.WORLDGEN_BLOB]):
            R.validate_launch(EXECUTION, protocol)
        with self.assertRaises(ValueError):
            R.validate_launch("bad", protocol)
        with patch.object(
                R, "_git",
                side_effect=[EXECUTION, " M src/i3/modules/mind.py"]):
            with self.assertRaisesRegex(ValueError, "dirty"):
                R.validate_launch(EXECUTION, protocol)

    def test_original_gzip_archive_is_deterministic(self):
        value = {"z": [3, 2, 1], "a": {"x": 1}}
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            ra = R._archive_original(a, "life", value)
            rb = R._archive_original(b, "life", value)
            self.assertEqual(ra["gzip_sha256"], rb["gzip_sha256"])
            self.assertEqual(
                ra["canonical_json_sha256"],
                rb["canonical_json_sha256"])
            self.assertEqual(
                Path(a, "life.json.gz").read_bytes(),
                Path(b, "life.json.gz").read_bytes())

    def test_replay_identity_includes_final_body_and_full_accounting(self):
        summary = {
            "trace_head": "t", "evidence_head": "e",
            "terminal": "censored", "steps_lived": 400,
            "world_sha256": "w", "final_body": [1, 2, 3, 4, 5],
            "actions": {"attendre": 1},
            "cognitive_accounting": {"status": "SETTLED"},
        }
        a = {"summary": deepcopy(summary)}
        b = {"summary": deepcopy(summary)}
        self.assertTrue(R._replay_equal(a, b))
        b["summary"]["final_body"][0] = 9
        self.assertFalse(R._replay_equal(a, b))
        b = {"summary": deepcopy(summary)}
        b["summary"]["cognitive_accounting"]["status"] = "changed"
        self.assertFalse(R._replay_equal(a, b))

    def test_selection_barrier_requires_all_sixteen_complete_shards(self):
        shards = selection_shards()
        selection = R.aggregate_selection(shards)
        self.assertEqual(
            selection["status"], "COMPLETE_SELECTION_READY_FOR_VALIDATION")
        self.assertEqual(
            set(selection["selected"]), {"reference", "candidate"})
        self.assertEqual(
            len(selection["selected"]["candidate"]), D.POPULATIONS)
        self.assertEqual(
            selection["systematic_reference_probe"]["0"]["interpretation"],
            "DESCRIPTIVE_SYSTEMATIC_SEARCH_NOT_COST_MATCHED")
        self.assertEqual(
            selection["random_g0_descriptive"]["0"]["candidate"]
            ["interpretation"],
            "DESCRIPTIVE_G0_EVOLVABILITY_NOT_GATE")
        with self.assertRaises(ValueError):
            R.aggregate_selection(shards[:-1])

    def test_selection_world_hash_or_custody_failure_blocks_ranking(self):
        shards = selection_shards()
        bad = deepcopy(shards)
        row = bad[1]["receipts"][0]
        row["world_sha256"] = "different"
        with self.assertRaisesRegex(ValueError, "world differs"):
            R.aggregate_selection(bad)

        bad = deepcopy(shards)
        bad[0]["receipts"][0]["cognitive_shortfall_steps"] = 1
        with self.assertRaisesRegex(ValueError, "custody"):
            R.aggregate_selection(bad)

    def test_selection_aggregate_sha_is_required_before_validation_cases(self):
        selection = R.aggregate_selection(selection_shards())
        bad = deepcopy(selection)
        bad["selected"]["candidate"]["0"].reverse()
        with self.assertRaises(ValueError):
            R.validation_cases(0, "candidate", bad)

    def test_complete_validation_aggregate_reaches_frozen_gate_only_after_all_shards(self):
        selection = R.aggregate_selection(selection_shards())
        shards = validation_shards(selection)
        report = R.aggregate_validation(selection, shards)
        self.assertEqual(report["status"], "COMPLETE_GATE_ARITHMETIC")
        self.assertEqual(
            report["scientific_verdict"],
            "PASS_FROZEN_STAGE1_OMEGA_GATE")
        self.assertTrue(
            report["gate"]["would_pass_if_receipts_are_authentic"])
        self.assertTrue(all(report["gate"]["rules"].values()))
        self.assertEqual(
            report["systematic_reference_probe"]["0"]["interpretation"],
            "DESCRIPTIVE_SYSTEMATIC_SEARCH_NOT_COST_MATCHED")
        self.assertEqual(report["validation_cost_descriptive"]
                         ["candidate"]["lives"], 240)
        with self.assertRaises(ValueError):
            R.aggregate_validation(selection, shards[:-1])

    def test_validation_world_lock_and_selection_hash_fail_closed(self):
        selection = R.aggregate_selection(selection_shards())
        shards = validation_shards(selection)

        bad = deepcopy(shards)
        bad[1]["receipts"][0]["world_sha256"] = "wrong-world"
        report = R.aggregate_validation(selection, bad)
        self.assertFalse(report["custody"]["world_lock"])
        self.assertFalse(report["gate"]["rules"]["G6_custody_floors"])
        self.assertEqual(
            report["scientific_verdict"],
            "FAIL_FROZEN_STAGE1_OMEGA_GATE")

        bad = deepcopy(shards)
        bad[0]["selection_sha256"] = "wrong-selection"
        with self.assertRaises(ValueError):
            R.aggregate_validation(selection, bad)

    def test_replay_failure_is_gate_failure_not_mortality(self):
        selection = R.aggregate_selection(selection_shards())
        shards = validation_shards(selection)
        bad = deepcopy(shards)
        bad[0]["rank0_replays"][0]["identical"] = False
        report = R.aggregate_validation(selection, bad)
        self.assertFalse(report["custody"]["rank0_replay_identical"])
        self.assertFalse(report["gate"]["rules"]["G6_custody_floors"])
        # Main physical lives remain complete; no death was fabricated.
        self.assertEqual(
            report["gate"]["family_survival"]["reference"]["stable"], 80)

    def test_systematic_probe_cannot_silently_enter_candidate_shard(self):
        shards = selection_shards()
        candidate = next(
            x for x in shards if x["arm"] == "candidate")
        candidate["systematic_reference_probe"] = _probe(
            candidate["population"], "selection")
        with self.assertRaisesRegex(ValueError, "probe"):
            R.aggregate_selection(shards)


if __name__ == "__main__":
    unittest.main()
