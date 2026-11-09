"""Selected Stage-2.1 custody bridge: only synthetic, never a World."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from i3.modules.genome import generation_zero, digest as genome_digest
from i3.lab import stage0_design as F0
from i3.lab import stage2_finite_panel as PANEL
from i3.lab import stage2_sealed_selection_bridge as BRIDGE
from i3.lab import two_phase_panel as TP


def sha(value):
    return sha256(str(value).encode()).hexdigest()


def synthetic_life(identity):
    """Faithful run_life *shape* only; constructed without any World/Mind."""
    seed = identity["genome_seed"]
    condition = identity.get("condition")
    policy = BRIDGE.POLICIES[condition if condition is not None
                             else identity["policy"]]
    is_random = condition == "RANDOM_on_GATE_selected"
    # One top-ranked G0 seed per policy, still purely synthetic.
    slot = seed % F0.CANDIDATES
    if condition is None:
        terminal = "censored" if (
            (identity["policy"] == "GATE" and slot == 4) or
            (identity["policy"] == "FIXED" and slot == 2)) else "dead"
    else:
        terminal = "censored"
    n = 400 if terminal == "censored" else 50
    spec_name = "synthetic-world-" + str(identity["world_index"])
    world = {"name": spec_name, "synthetic_only": True,
             "cohort": identity["cohort"], "index": identity["world_index"]}
    world_digest = BRIDGE._json_digest(world)
    genome = generation_zero(seed)
    ticket = {
        "cohort": identity["cohort"], "family": identity["family"],
        "index": identity["world_index"], "world_seed": identity["world_seed"],
        "world_name": spec_name, "world_sha256": world_digest,
        "transport_fingerprint": "d" * 64}
    source_files = {"synthetic/test-only.py": "e" * 64}
    manifest = {
        "schema": "i3-life-manifest/v2", "execution_model": "i3-funded-v2",
        "protocol": "SYNTHETIC_TEST_NO_WORLD",
        "source": {"files": source_files,
                   "sha256": BRIDGE._json_digest(source_files),
                   "git_head": PINS["source_sha"], "working_tree_dirty": False},
        "life_seed": identity["life_seed"], "horizon": 400,
        "world": world, "world_sha256": world_digest,
        "genome": genome,
    }
    if policy != "reference":
        mode = {"p13_replay_gate_v1": "gate",
                "p13_replay_gate_random_equal_mean_v1": "random_equal_mean",
                "p13_replay_gate_zero_perceived_cost_v1": "zero_perceived_cost"}[policy]
        manifest["experimental_policy"] = {
            "name": policy, "mode": mode,
            "protocol": "STAGE2_REPLAY_GATE", "admission": ticket}
    result = {
        "manifest": manifest, "manifest_id": BRIDGE._json_digest(manifest),
        "world": spec_name, "genome": genome_digest(genome),
        "steps_lived": n, "terminal": terminal,
        "death_causes": [] if terminal == "censored" else ["synthetic_death"],
        "horizon": 400, "life_seed": identity["life_seed"],
        "actions": {"dormir": 4},
        "cognitive_accounting": {
            "schema": "i3-cognitive-funding/v2",
            "status": "SETTLED_FOR_DECLARED_WORK", "shortfall_steps": 0,
            "totals": {
                "energy": {"requested": 3.0, "paid": 3.0, "unpaid": 0.0},
                "vigilance": {"requested": 4.0, "paid": 4.0, "unpaid": 0.0}},
            "replays_executed": 24 if is_random else 16,
            "inactive_steps": 2},
    }
    if policy != "reference":
        result["admission"] = ticket
        result["experimental_policy"] = manifest["experimental_policy"]
        result["replay_gate"] = {"mode": manifest["experimental_policy"]["mode"]}
    if is_random:
        result["replay_gate"]["random_schedule"] = {
            "draws_funded": 4, "lived_sleep_ordinals": 4,
            "nominal_replays_scheduled": 24,
            "eligible_replays_scheduled": 24, "actual_replays_paid": 24,
            "mean_numerator": 5532, "mean_denominator": 867}
    return result

def selection_originals():
    for w in F0.world_rows("selection"):
        p = w["population"]
        for arm in ("FIXED", "GATE"):
            for j in range(F0.CANDIDATES):
                identity = {
                    "cohort": "selection", "population": p,
                    "family": w["family"], "world_index": w["index"],
                    "world_seed": w["world_seed"], "genome_seed": F0.founder_seed(p, j),
                    "life_seed": w["life_seed"], "policy": arm}
                yield identity, synthetic_life(identity)


def validation_originals(selected):
    for w in F0.world_rows("validation"):
        p = w["population"]
        for condition in PANEL.CONDITIONS:
            arm = "FIXED" if condition == "FIXED_on_FIXED_selected" else "GATE"
            for seed in selected[arm][p]:
                identity = {
                    "cohort": "validation", "population": p,
                    "family": w["family"], "world_index": w["index"],
                    "world_seed": w["world_seed"], "genome_seed": seed,
                    "life_seed": w["life_seed"], "condition": condition}
                yield identity, synthetic_life(identity)


PINS = {"manifest_sha256": "a" * 64, "source_sha": "b" * 40,
        "plan_sha256": "c" * 64, "transport_fingerprint": "d" * 64}


class CompleteOriginalSelectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.originals = list(selection_originals())

    def test_complete_rank_rederived_without_validation_exposure(self):
        with patch.object(BRIDGE, "_sealed", return_value=self.originals):
            selection = BRIDGE.selection_from_originals("not-opened", "not-opened", PINS)
        self.assertEqual(selection["selection_originals"], 3840)
        self.assertEqual(selection["source_custody"],
                         "MATCHES_CALLER_SUPPLIED_DIGEST_PINS_ONLY")
        self.assertFalse(selection["world_opening_authorized"])
        for p in range(8):
            self.assertIn(F0.founder_seed(p, 4), selection["selected"]["GATE"][p])
            self.assertIn(F0.founder_seed(p, 2), selection["selected"]["FIXED"][p])
            self.assertEqual(len(selection["selected"]["GATE"][p]), 5)

    def test_missing_duplicate_wrong_policy_world_genome_and_cognition_fail(self):
        changes = [
            lambda o: o.pop(),
            lambda o: o.__setitem__(1, o[0]),
            lambda o: o[0][0].__setitem__("world_seed", 999),
            lambda o: o[0][1]["manifest"]["experimental_policy"].__setitem__(
                "name", "p13_replay_gate_v1"),
            lambda o: o[0][1].__setitem__("genome", "0" * 64),
            lambda o: o[0][1]["cognitive_accounting"]["totals"]["energy"].__setitem__(
                "paid", -1.0),
        ]
        for i, mutation in enumerate(changes):
            # Keep the pristine fixture clean and allocate only the mutated row.
            originals = list(self.originals)
            original_id, original_life = originals[0]
            originals[0] = (dict(original_id), json.loads(json.dumps(original_life)))
            mutation(originals)
            with self.subTest(i=i), patch.object(BRIDGE, "_sealed", return_value=originals):
                with self.assertRaises(ValueError):
                    BRIDGE.selection_from_originals("not-opened", "not-opened", PINS)

    def test_complete_validation_readout_keeps_genome_and_world_parity(self):
        with patch.object(BRIDGE, "_sealed", return_value=self.originals):
            selected = BRIDGE.selection_from_originals("not-opened", "not-opened", PINS)
        validation = list(validation_originals(selected["selected"]))
        def read_archive(_, __, ___, cohort, ____):
            return self.originals if cohort == "selection" else validation
        with patch.object(BRIDGE, "_sealed", side_effect=read_archive):
            result = BRIDGE.readout_from_originals(
                "never", "never", PINS, "never", "never", PINS)
        self.assertEqual(result["selection_originals_checked"], 3840)
        self.assertEqual(result["validation_originals_checked"], 1200)
        self.assertFalse(result["owner_authorization_inferred"])
        self.assertFalse(result["population_independence_established"])
        self.assertEqual(result["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(result["readout"]["finite_panel_cells"], 1200)

        bad_validation = list(validation)
        identity, life = bad_validation[0]
        bad_validation[0] = (dict(identity), json.loads(json.dumps(life)))
        bad_validation[0][1]["genome"] = "0" * 64
        def bad_archive(_, __, ___, cohort, ____):
            return self.originals if cohort == "selection" else bad_validation
        with patch.object(BRIDGE, "_sealed", side_effect=bad_archive):
            with self.assertRaisesRegex(ValueError, "genome digest"):
                BRIDGE.readout_from_originals("never", "never", PINS,
                                              "never", "never", PINS)


class DigestAndSealedTransportTests(unittest.TestCase):
    def test_two_phase_seal_verified_with_explicit_caller_pins(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive, plan = root / "archive", root / "plan.json"
            plan.write_text('{"software_only":true}')
            identities = [{"dummy": i} for i in range(2)]
            g = TP.generate(identities, lambda c: {"dummy_life": c["dummy"]}, archive)
            body = (archive / "MANIFEST.json").read_bytes()
            pins = dict(PINS)
            pins["manifest_sha256"] = sha256(body).hexdigest()
            pins["plan_sha256"] = sha256(plan.read_bytes()).hexdigest()
            (archive / "SOURCE_LOCK.json").write_text(json.dumps({
                "schema": BRIDGE.LOCK_SCHEMA, "cohort": "selection",
                "planned": 2, "generated": 2, "no_retry": True, **pins}))
            self.assertEqual(
                BRIDGE._sealed(archive, plan, pins, "selection", 2),
                [(x, {"dummy_life": x["dummy"]}) for x in identities])
            changed = dict(pins)
            changed["manifest_sha256"] = "e" * 64
            with self.assertRaises(ValueError):
                BRIDGE._sealed(archive, plan, changed, "selection", 2)
            (archive / "life-001.json.gz").write_bytes(b"tampered")
            with self.assertRaises(ValueError):
                BRIDGE._sealed(archive, plan, pins, "selection", 2)
            self.assertEqual(g["generated"], 2)

    def test_missing_plan_pin_and_forged_lock_fail(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive, plan = root / "archive", root / "plan.json"
            plan.write_text("plan")
            g = TP.generate([{"case": 0}], lambda _: {"life": 1}, archive)
            pins = dict(PINS)
            pins["manifest_sha256"] = sha256((archive / "MANIFEST.json").read_bytes()).hexdigest()
            pins["plan_sha256"] = sha256(plan.read_bytes()).hexdigest()
            with self.assertRaises(ValueError):
                BRIDGE._sealed(archive, plan, pins, "selection", 1)
            (archive / "SOURCE_LOCK.json").write_text(json.dumps({
                "schema": BRIDGE.LOCK_SCHEMA, "cohort": "selection",
                "planned": 1, "generated": 1, "no_retry": True, **pins}))
            (archive / "life-999.json.gz").write_bytes(b"extra")
            with self.assertRaises(ValueError):
                BRIDGE._sealed(archive, plan, pins, "selection", 1)
            (archive / "life-999.json.gz").unlink()
            with self.assertRaises(ValueError):
                BRIDGE._sealed(archive, plan, {**pins, "source_sha": "0"},
                               "selection", 1)
            self.assertEqual(g["planned"], 1)


if __name__ == "__main__":
    unittest.main()
