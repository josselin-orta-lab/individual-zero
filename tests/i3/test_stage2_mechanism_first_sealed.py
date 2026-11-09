"""Mechanism-first sealed adapter regression: SYNTHETIC only; NO World."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from i3.lab import stage2_mechanism_first_design as M
from i3.lab import stage2_mechanism_first_sealed as V3
from i3.lab import stage2_sealed_selection_bridge as SEALED
from i3.lab import two_phase_panel as TP

# Reuse the already validated *synthetic* runtime-shaped dictionary fixture,
# not the real engine and never a source-registered scientific World.
from test_stage2_sealed_selection_bridge import synthetic_life, PINS


COND = {
    "FIXED_G0": "FIXED_on_GATE_selected",
    "GATE_G0": "GATE_on_GATE_selected",
    "RANDOM_G0": "RANDOM_on_GATE_selected",
}


def originals():
    out = []
    for (p, index, seed, arm), world in M.expected_cells().items():
        identity = {
            "cohort": "validation", "population": p,
            "family": world["family"], "world_index": index,
            "world_seed": world["world_seed"], "genome_seed": seed,
            "life_seed": world["life_seed"], "arm": arm,
        }
        stub = dict(identity)
        stub["condition"] = COND[arm]
        life = synthetic_life(stub)
        if arm != "FIXED_G0":
            life["replay_gate"].update({
                "sleep_steps_seen_by_gate": 4,
                "decisions_total": 10,
                "audited_decisions": 8,
                "relevant_decisions": 2,
            })
        if arm == "RANDOM_G0":
            life["replay_gate"]["random_schedule"]["policy"] = (
                "i3-stage2-1-random-equal-mean-v1")
        out.append((identity, life))
    return out


class MechanismFirstOriginals(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = originals()

    def _reduce(self, records):
        with patch.object(SEALED, "_sealed", return_value=records):
            return V3.from_sealed_originals("never-open", "never-open", PINS)

    def test_complete_720_exact_matched_originals(self):
        report = self._reduce(self.data)
        self.assertEqual(report["originals_checked"], 720)
        self.assertEqual(report["paired_blocks"], 240)
        self.assertEqual(report["readout"]["record_count"], 720)
        self.assertEqual(report["readout"]["by_family"]["stable"]
                         ["GATE_minus_FIXED"]["survival_at_400"], 0)
        self.assertFalse(report["worlds_opened_by_adapter"])
        self.assertEqual(report["scientific_verdict"], "NOT_ISSUED")
        self.assertEqual(report["owner_approval"], "NOT_INFERRED")
        self.assertEqual(report["population_independence"], "NOT_ESTABLISHED")
        self.assertEqual(report["survival_noninferiority"], "NOT_TESTED")
        exposure = report["mechanism_exposure"]
        self.assertEqual(exposure["assigned_lives"], 720)
        self.assertFalse(exposure["realized_replay_parity_proven"])
        self.assertEqual(exposure["by_arm"]["FIXED_G0"]["assigned_lives"], 240)
        self.assertEqual(exposure["by_arm"]["GATE_G0"]["totals"]["decisions_audited"], 1920)
        self.assertEqual(exposure["by_arm"]["RANDOM_G0"]["totals"]["random_funded_draws"], 960)
        self.assertEqual(exposure["by_arm"]["RANDOM_G0"]["totals"]["replays_paid"], 5760)
        self.assertEqual(exposure["gate_minus_random_paid_replays_per_assigned_life"], -8)
        for family in ("stable", "depletion", "pulse"):
            self.assertEqual(exposure["by_family"][family]["GATE_G0"]["assigned_lives"], 80)
        for p in range(8):
            self.assertEqual(exposure["by_population"][p]["RANDOM_G0"]["assigned_lives"], 30)

    def test_missing_duplicate_or_foreign_originals_fail_closed(self):
        for mutation in ("missing", "duplicate", "foreign_seed", "changed_arm",
                         "wrong_world", "invalid_policy", "wrong_ticket"):
            data = list(self.data)
            original_id, original_life = data[0]
            identity, life = dict(original_id), deepcopy(original_life)
            data[0] = (identity, life)
            if mutation == "missing":
                data.pop()
            elif mutation == "duplicate":
                data[1] = data[0]
            elif mutation == "foreign_seed":
                identity["genome_seed"] = 99999
            elif mutation == "changed_arm":
                identity["arm"] = "FIXED_on_FIXED_selected"
            elif mutation == "wrong_world":
                identity["world_seed"] = 99999
            elif mutation == "invalid_policy":
                life["manifest"]["experimental_policy"] = {"name": "foreign"}
                life["manifest_id"] = SEALED._json_digest(life["manifest"])
            elif mutation == "wrong_ticket":
                idx = next(i for i, (j, _) in enumerate(data)
                           if j["arm"] == "GATE_G0")
                gi, gl = data[idx]
                gi, gl = dict(gi), deepcopy(gl)
                gl["admission"]["index"] += 1
                data[idx] = (gi, gl)
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self._reduce(data)

    def test_random_funding_nominal_eligible_paid_must_agree(self):
        index = next(i for i, (identity, _) in enumerate(self.data)
                     if identity["arm"] == "RANDOM_G0")
        for name, field, value in (
            ("missing_policy", "policy", "unknown"),
            ("wrong_mean", "mean_numerator", 999),
            ("unfunded_draws", "draws_funded", 5),
            ("unphysical_nominal", "nominal_replays_scheduled", 20),
            ("paid_gt_eligible", "eligible_replays_scheduled", 22),
            ("paid_mismatch", "actual_replays_paid", 23),
            ("bad_boolean", "draws_funded", True),
        ):
            data = list(self.data)
            ident, life = data[index]
            altered = deepcopy(life)
            altered["replay_gate"]["random_schedule"][field] = value
            data[index] = (ident, altered)
            with self.subTest(name=name), self.assertRaises(ValueError):
                self._reduce(data)

    def test_exposure_drift_is_reported_not_promoted(self):
        data = list(self.data)
        idx = next(i for i, (ident, _) in enumerate(data) if ident["arm"] == "GATE_G0")
        ident, life = data[idx]
        changed = deepcopy(life)
        changed["cognitive_accounting"]["replays_executed"] = 0
        data[idx] = (ident, changed)
        exposure = self._reduce(data)["mechanism_exposure"]
        self.assertLess(exposure["gate_minus_random_paid_replays_per_assigned_life"], -8)
        self.assertFalse(exposure["realized_replay_parity_proven"])
        self.assertEqual(exposure["causal_mechanism_advantage"], "NOT_ESTABLISHED")

    def test_funded_gate_counters_fail_closed(self):
        for arm, field, value in (
            ("GATE_G0", "sleep_steps_seen_by_gate", 5),
            ("GATE_G0", "decisions_total", -1),
            ("GATE_G0", "audited_decisions", 11),
            ("GATE_G0", "relevant_decisions", 9),
            ("RANDOM_G0", "sleep_steps_seen_by_gate", 3),
            ("RANDOM_G0", "decisions_total", True),
        ):
            data = list(self.data)
            idx = next(i for i, (ident, _) in enumerate(data) if ident["arm"] == arm)
            ident, life = data[idx]
            changed = deepcopy(life)
            changed["replay_gate"][field] = value
            data[idx] = (ident, changed)
            with self.subTest(arm=arm, field=field), self.assertRaises(ValueError):
                self._reduce(data)

    def test_nonrandom_schedule_not_accepted(self):
        data = list(self.data)
        ident, life = data[0]
        altered = deepcopy(life)
        altered["replay_gate"] = {"random_schedule": {"policy": "fake"}}
        data[0] = (ident, altered)
        with self.assertRaises(ValueError):
            self._reduce(data)

    def test_separate_v3_lock_is_required_not_selected_pipeline_lock(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "plan.json"
            path.write_text('{"study":"synthetic-v3"}')
            archive = root / "sealed"
            TP.generate([{"synthetic": True}],
                        lambda _: {"only_a_test": True}, archive)
            pins = dict(PINS)
            pins["plan_sha256"] = sha256(path.read_bytes()).hexdigest()
            pins["manifest_sha256"] = sha256(
                (archive / "MANIFEST.json").read_bytes()).hexdigest()
            def lock(schema):
                (archive / "SOURCE_LOCK.json").write_text(json.dumps({
                    "schema": schema, "cohort": "validation", "planned": 1,
                    "generated": 1, "no_retry": True, **pins,
                }))
            lock(SEALED.LOCK_SCHEMA)
            with self.assertRaises(ValueError):
                SEALED._sealed(archive, path, pins, "validation", 1,
                               lock_schema=V3.LOCK_SCHEMA)
            lock(V3.LOCK_SCHEMA)
            self.assertEqual(
                len(SEALED._sealed(archive, path, pins, "validation", 1,
                                  lock_schema=V3.LOCK_SCHEMA)), 1)
            self.assertEqual(V3.STATUS, "MATCHES_CALLER_PINS_ONLY_NO_SCIENTIFIC_VERDICT")


if __name__ == "__main__":
    unittest.main()
