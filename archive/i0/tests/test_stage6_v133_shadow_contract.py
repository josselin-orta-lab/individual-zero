"""v1.3.3 static and API safety regressions; no WorldBody or live I0."""
from __future__ import annotations
import unittest
from pathlib import Path
from i0.equipment import (
    EquipmentCorpus, EquipmentCorpusExample, SimulationNeighbor, SimulationState,
)
from i0.interfaces import PrimitiveCommand
from i0.experimental.stage6_visible_delta_shadow import (
    fit_external_lab_shadow, FIELDS, ShadowVisibleDeltaModel, MODEL_VERSION,
)


def state(x=4, energy=50.0, food=40.0, water=40.0, berries=0,
          resource=True, passable=True):
    adj = (SimulationNeighbor("east", x+1, 3, passable, False, (), False),)
    return SimulationState(
        schema_version="simulation-state-v1", x=x, y=3,
        body={"energy": energy, "food": food, "water": water, "integrity": 100.0},
        inventory={"berry_b": berries}, current_water_source=False,
        current_resources=("berry_b",) if resource else (),
        adjacent=adj, known_shelter_here=False, is_night=False,
    )


MOVE = PrimitiveCommand("se_deplacer", {"direction":"east"})
COLLECT = PrimitiveCommand("collecter", {"target":"berry_b"})


def corpus(unstable=False):
    rows = []
    for n in range(8):
        s = state(x=4+n, food=40.0+n)
        rows.append(EquipmentCorpusExample(
            "MOVE", s, MOVE,
            state(x=5+n, energy=49.0, food=39.5+n, water=39.8),
            False,
        ))
        s = state(x=4+n, food=40.0+n)
        rows.append(EquipmentCorpusExample(
            "COLLECT", s, COLLECT,
            state(x=4+n, energy=49.25, food=39.5+n, water=39.8,
                  berries=2 if n != 7 or not unstable else 1), False,
        ))
    return EquipmentCorpus(version="v133-external-test", examples=tuple(rows))


class ShadowContractTests(unittest.TestCase):
    def test_all_unresolved_fields_remain_null(self):
        model = fit_external_lab_shadow(corpus=corpus())
        result = model.forecast_for_review(state=state(), command=MOVE).as_dict()
        self.assertEqual(result["status"], "empirical_partial_not_certified")
        self.assertEqual(set(result["estimated"]), set(FIELDS))
        for k in ("integrity", "terminal", "next_adjacency", "safe",
                  "causal_responsibility"):
            self.assertIsNone(result[k])
        self.assertEqual(result["source_scope"], "external_lab")
        self.assertEqual(model.activation, "shadow_only")

    def test_abstain_on_body_clamp_and_obstacle(self):
        model = fit_external_lab_shadow(corpus=corpus())
        self.assertEqual(model.forecast_for_review(
            state=state(energy=0.2), command=MOVE).status, "abstain_boundary")
        self.assertEqual(model.forecast_for_review(
            state=state(passable=False), command=MOVE).status, "abstain_ineligible")

    def test_abstain_on_unsupported_and_unstable_transition(self):
        model = fit_external_lab_shadow(corpus=corpus(unstable=True))
        self.assertEqual(model.forecast_for_review(
            state=state(), command=COLLECT).status, "abstain_unstable_training")
        self.assertEqual(model.forecast_for_review(
            state=state(), command=PrimitiveCommand("manger", {"target":"berry_b"}))
            .status, "abstain_unsupported_action")

    def test_reject_terminal_ingestion_and_cognitive_source(self):
        raw = corpus()
        bad = EquipmentCorpus(raw.version, raw.examples[:-1] + (
            EquipmentCorpusExample("EAT", state(), PrimitiveCommand("manger",
                {"target":"berry_b"}), state(), False),))
        with self.assertRaises(ValueError):
            fit_external_lab_shadow(corpus=bad)
        with self.assertRaises(ValueError):
            fit_external_lab_shadow(corpus=raw, source_scope="lived_I0")
        with self.assertRaises(ValueError):
            fit_external_lab_shadow(corpus=raw, version="unsafe-upgrade")
        bad_terminal = EquipmentCorpus(raw.version, raw.examples[:-1] + (
            EquipmentCorpusExample("COLLECT",state(),COLLECT,state(),True),))
        with self.assertRaises(ValueError):
            fit_external_lab_shadow(corpus=bad_terminal)

    def test_not_a_planner_and_no_second_dispatch_path(self):
        self.assertFalse(hasattr(ShadowVisibleDeltaModel, "predict"))
        self.assertFalse(hasattr(ShadowVisibleDeltaModel, "dispatch"))
        root = Path(__file__).resolve().parents[1] / "src/i0"
        for file in (
            root/"modules/stage6_planning.py", root/"modules/action_control.py",
            root/"equipment.py",
        ):
            self.assertNotIn("stage6_visible_delta_shadow", file.read_text())

    def test_version_and_evidence_identity_are_stable(self):
        a = fit_external_lab_shadow(corpus=corpus())
        b = fit_external_lab_shadow(corpus=corpus())
        self.assertEqual(a, b)
        self.assertEqual(a.version, MODEL_VERSION)
        self.assertEqual(len(a.corpus_sha256), 64)


if __name__ == "__main__":
    unittest.main()
