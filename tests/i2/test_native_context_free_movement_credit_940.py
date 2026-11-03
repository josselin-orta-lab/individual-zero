"""P2 #940: prospective opt-in isolation of context-free movement outcome credit.

Research-only single-owner native lives. All admitted actions emerge from paid
Competition and fresh Action Control; no scripted motor or post-hoc tuning.
"""
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NativeRefusal, MOVEMENT_CREDIT_EVIDENCE, PRIORS,
    isolate_context_free_movement_credit,
)

TRAITS = BirthTemperament(0, .5, .3, 0, 0)


class ContextFreeMovementCredit940(unittest.TestCase):
    def test_pure_motion_projection_keeps_resource_scores_and_native_priors(self):
        initial = dict(PRIORS)
        first, markers = isolate_context_free_movement_credit(
            initial, learning=True, spatial_world=True, enabled=True)
        self.assertEqual(first, initial)
        self.assertEqual(markers, frozenset(
            action for action in PRIORS if action.startswith("se_deplacer_vers_")))

        values = {**PRIORS, "se_deplacer_vers_camp": 120,
                  "se_deplacer_vers_passage": -25,
                  "boire": 7, "manger": -2}
        projected, markers = isolate_context_free_movement_credit(
            values, learning=True, spatial_world=True, enabled=True)
        self.assertEqual(projected["se_deplacer_vers_camp"],
                         PRIORS["se_deplacer_vers_camp"])
        self.assertEqual(projected["se_deplacer_vers_passage"],
                         PRIORS["se_deplacer_vers_passage"])
        self.assertEqual(projected["boire"], 7)
        self.assertEqual(projected["manger"], -2)
        self.assertIn("se_deplacer_vers_camp", markers)
        disabled, markers = isolate_context_free_movement_credit(
            values, learning=True, spatial_world=True, enabled=False)
        self.assertEqual(disabled, values)
        self.assertFalse(markers)
        for bad in (
            {"learning": False, "spatial_world": True, "enabled": True},
            {"learning": True, "spatial_world": False, "enabled": True},
            {"learning": 1, "spatial_world": True, "enabled": True},
            {"learning": True, "spatial_world": True, "enabled": 1},
        ):
            with self.subTest(bad=bad), self.assertRaises(NativeRefusal):
                isolate_context_free_movement_credit(values, **bad)

    def test_born_flag_gates_and_four_independent_paid_24_tick_lives(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            born = dict(body=Body(85, 90, 35, 100), temperament=TRAITS,
                        uc=300, max_steps=24, spatial_world=True,
                        ordinary_water_site="camp", place_return_tie=True,
                        purpose_followthrough=True, learning=True,
                        evidence_tie_exploration=False, sleep_consolidation=False,
                        food_stock=0, water_stock=2, water_restock_every=0)
            for bad in (
                {"spatial_world": False},
                {"learning": False},
                {"contextual_movement_credit": 1},
            ):
                with self.subTest(illegal=bad), self.assertRaises(NativeRefusal):
                    NativePaidI2.create(
                        root / ("illegal" + str(len(bad)) + ".sqlite"),
                        **{**born, **bad, "contextual_movement_credit": bad.get(
                            "contextual_movement_credit", True)})
            result = {}
            for gain in (0.0, 40.0):
                for contextual in (False, True):
                    key = ("effective" if gain else "ineffective") + (
                        "-contextual" if contextual else "-legacy")
                    path = root / (key + ".sqlite")
                    life = NativePaidI2.create(
                        path, **born, drink_water_gain=gain,
                        contextual_movement_credit=contextual)
                    before = life.audit()
                    for _ in range(24):
                        current = life.step()
                        if current["terminal"]:
                            break
                    final = life.audit()
                    self.assertEqual(NativePaidI2.inspect(path).audit(), final)
                    with sqlite3.connect(path) as db:
                        moves = [a for a, in db.execute(
                            "SELECT admitted_action FROM native_physical_events ORDER BY seq")]
                        physical = [json.loads(a) for a, in db.execute(
                            "SELECT after_json FROM native_physical_events ORDER BY seq")]
                        events = [json.loads(a) for a, in db.execute(
                            "SELECT event_json FROM events ORDER BY seq")]
                    markers = []
                    for tick, event in enumerate(events, 1):
                        if not event["advice"]:
                            continue
                        candidates = {
                            c["candidate_ref"]: c["semantic_ref"]
                            for c in event["frame"]["candidates"]}
                        markers.extend(
                            (tick, candidates[v["candidate_ref"]], v["value"])
                            for v in event["advice"]["values"]
                            if MOVEMENT_CREDIT_EVIDENCE in v["evidence_ref"])
                    self.assertEqual(bool(markers), contextual)
                    self.assertEqual(final["scientific_verdict"], "NOT_ESTABLISHED")
                    self.assertFalse(final["engine_registered"])
                    self.assertFalse(final["m11_authenticated"])
                    result[key] = {
                        "actions": moves,
                        "second_drink_ticks": [
                            tick for tick, action in enumerate(moves, 1)
                            if action == "boire" and tick > 1],
                        "water_final": round(final["body"]["water"], 4),
                        "water_history": [round(p["water"], 4) for p in physical],
                        "uc_spent": before["remaining_uc"] - final["remaining_uc"],
                        "terminal": final["terminal"],
                        "censored": final["revision"] == 24 and not final["terminal"],
                        "movement_isolation_evidence": markers,
                        "cold_audit": "PASS"}
            for gain in ("effective", "ineffective"):
                baseline = result[gain + "-legacy"]
                experimental = result[gain + "-contextual"]
                first_divergence = next(
                    (tick for tick, (old, new) in enumerate(
                        zip(baseline["actions"], experimental["actions"]), 1)
                     if old != new), None)
                baseline["first_divergence_vs_contextual"] = first_divergence
                experimental["first_divergence_vs_legacy"] = first_divergence
            print("I2_CONTEXT_FREE_MOVEMENT_CREDIT_940=" + json.dumps(
                result, sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
