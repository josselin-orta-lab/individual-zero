"""Fixed 2x2x2 mechanism factorial across two blind food worlds.

Descriptive paired toy-world endpoints; no forced positive conclusions.
"""
import json
import sys
import tempfile
import unittest
from itertools import product
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i2.runtime.isolated_prototype import (
    IsolatedI2, SCENARIOS, DRINK, EAT, world_endpoint,
)

WORLDS = ("adverse", "restoration")
ENERGIES = (6, 40)
STOCKS = (1, 2)
HORIZON = 20
FLAGS = tuple(product((False, True), repeat=3))


class BlindWaterThreeMechanismFactorial(unittest.TestCase):
    def test_full_factorial_with_censoring_and_first_person_matching(self):
        observations = []
        with tempfile.TemporaryDirectory(prefix="i2-factorial-") as root:
            for world, energy, stock, flags in product(
                    WORLDS, ENERGIES, STOCKS, FLAGS):
                learning, deadline, reflex = flags
                label = f"{world}-{energy}-{stock}-{int(learning)}{int(deadline)}{int(reflex)}"
                life = IsolatedI2.create(
                    Path(root) / (label + ".sqlite"),
                    learning=learning,
                    impulses=SCENARIOS[world] + (SCENARIOS[world][-1],) * 2,
                    extended_postcontact_study=True,
                    initial_energy=energy, initial_uc=60, resources=8,
                    restorative_water_study=True, water_effect_blind=True,
                    finite_water_capacity=stock,
                    deadline_aware=deadline,
                    last_resort_exploration=reflex)
                execution = life.run_world(ticks=HORIZON)
                audit = life.audit()
                decisions = life.decision_evidence()
                endpoint = world_endpoint(execution)
                used = sum(d["chosen"] == DRINK for d in decisions)
                self.assertLessEqual(used, stock)
                self.assertEqual(audit["water_remaining"], stock - used)
                self.assertEqual(endpoint["actual_uc_spent"], audit["actual_uc_spent"])
                self.assertLessEqual(audit["actual_uc_spent"], 60)
                self.assertFalse(audit["m11_authenticated"])
                self.assertEqual(audit["science"], "NOT_ESTABLISHED")
                if used == stock:
                    last = max(i for i, d in enumerate(decisions)
                               if d["chosen"] == DRINK)
                    self.assertTrue(all(DRINK not in d["visible"]
                                        for d in decisions[last + 1:]))
                observations.append(dict(
                    world=world, energy=energy, stock=stock,
                    learning=learning, deadline=deadline, reflex=reflex,
                    chosen=[d["chosen"] for d in decisions],
                    first_person=[dict(
                        energy=d["before_energy"],
                        inventory=d["before_inventory"],
                        resources=d["before_resources"],
                        offered=d["visible"], uc=d["uc_before"],
                        physical_tick=d["physical_ticks_before"],
                        history=d["subjective_outcomes_available"],
                        scores=d["candidate_scores"],
                        chosen=d["chosen"],
                        paid=d["uc_spent"],
                        emergency=d["last_resort_priority_applied"])
                        for d in decisions],
                    water_used=used,
                    emergency_count=sum(d["last_resort_priority_applied"]
                                        for d in decisions),
                    tick=endpoint["ending_physical_tick"],
                    death_tick=endpoint["modeled_death_tick"],
                    censored=endpoint["right_censored"],
                    end_energy=endpoint["ending_energy"],
                    actual_uc=endpoint["actual_uc_spent"]))
        self.assertEqual(len(observations), 64)
        index = {(o["world"], o["energy"], o["stock"],
                  o["learning"], o["deadline"], o["reflex"]): o
                 for o in observations}
        self.assertEqual(len(index), 64)

        # When only the hidden food world changes, matching actual
        # predecision body and subjective history forbid different choices.
        for energy, stock, flags in product(ENERGIES, STOCKS, FLAGS):
            a = index["adverse", energy, stock, *flags]
            b = index["restoration", energy, stock, *flags]
            for da, db in zip(a["first_person"], b["first_person"]):
                public = ("energy", "inventory", "resources", "offered",
                          "uc", "physical_tick", "history")
                if any(da[k] != db[k] for k in public):
                    break
                for key in ("chosen", "scores", "paid", "emergency"):
                    self.assertEqual(da[key], db[key], (energy, stock, flags, key))

        # Interaction contrast = difference in the reflex effect with and
        # without deadlines, conditional on a *fixed* learning toggle.
        contrasts = []
        for world, energy, stock, learn in product(
                WORLDS, ENERGIES, STOCKS, (False, True)):
            group = {(deadline, reflex):
                     index[world, energy, stock, learn, deadline, reflex]
                     for deadline, reflex in product((False, True), repeat=2)}
            score = lambda x: int(x["censored"])
            interaction = (score(group[True, True])-score(group[True, False])
                           -score(group[False, True])+score(group[False, False]))
            contrasts.append(dict(
                world=world, energy=energy, stock=stock, learning=learn,
                reflex_deadline_survival_interaction=interaction,
                endpoints={"%s%s" % (int(d), int(f)): dict(
                    censored=group[d, f]["censored"],
                    death_tick=group[d, f]["death_tick"],
                    actual_uc=group[d, f]["actual_uc"])
                    for d, f in product((False, True), repeat=2)}))
        self.assertEqual(len(contrasts), 16)
        compact = [{k: v for k, v in o.items() if k != "first_person"}
                   for o in observations]
        print("I2_THREE_MECHANISM_FACTORIAL_V1=" + json.dumps(dict(
            cases=compact, interactions=contrasts,
            inference="DESCRIPTIVE_NONINDEPENDENT_TOY_WORLDS",
            generalized_survival="NOT_ESTABLISHED"),
            sort_keys=True, separators=(",", ":")), flush=True)


if __name__ == "__main__":
    unittest.main()
