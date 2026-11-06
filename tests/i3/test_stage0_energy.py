"""Stage-0 observer arithmetic; synthetic receipts plus bounded development parity.

No validation world or scientific-study entrypoint is used by these tests.
"""
from collections import Counter
from copy import deepcopy
from dataclasses import asdict, replace
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from i3.lab import stage0_energy as energy
from i3.modules.body import BodyLaws, CognitiveWork, debit_cognition, transition

PROTOCOL = "STAGE0_SOFTWARE_FIXTURE_NOT_SCIENCE"


def digest(x):
    return sha256(json.dumps(x, sort_keys=True, separators=(",", ":"),
                             ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def reseal(life):
    """Re-sign synthetic test inputs, never certify a fabricated original."""
    m = life["manifest"]
    m["world_sha256"] = digest(m["world"])
    m["source"]["sha256"] = digest(m["source"]["files"])
    life["manifest_id"] = digest(m)
    life["genome"] = sha256(json.dumps(m["genome"], sort_keys=True,
                                       separators=(",", ":")).encode("ascii")).hexdigest()
    head = sha256(json.dumps([life["genome"], life["world"], life["life_seed"], life["horizon"]],
                             separators=(",", ":")).encode()).hexdigest()
    evidence = life["manifest_id"]
    for row in life["trace"]:
        record = {k: row[k] for k in ("t", "action", "param", "option", "body", "pos", "dead")}
        head = sha256((head + json.dumps(record, sort_keys=True, separators=(",", ":"))).encode()).hexdigest()
        evidence = digest({"previous": evidence, "record": record, "work": row["cognitive_work"],
                           "accounting": row["cognitive_accounting"], "funding_phases": row["funding_phases"]})
    life["trace_head"] = head
    life["evidence_head"] = digest({"previous": evidence, "terminal": life["terminal"],
                                    "accounting": life["cognitive_accounting"]})
    return life


def fixture(population=0, *, candidate=False, birth_water=0.5, actions=None, label="a"):
    laws = BodyLaws()
    body = (80., 80., birth_water, 80., 80.)
    world = {"name": f"synthetic-{population}-{label}", "body": list(body), "laws": asdict(laws)}
    source = {"files": {"synthetic_fixture.py": "a" * 64}}
    m = {"schema": "i3-life-manifest/v2", "execution_model": "i3-funded-v2", "protocol": PROTOCOL,
         "world": world, "source": source, "genome": {"schema": "SYNTHETIC_NOT_ADMISSIBLE", "p": population},
         "life_seed": 100 + population, "horizon": 5}
    totals = {ch: {k: 0.0 for k in ("requested", "paid", "unpaid")} for ch in energy.CHANNELS}
    rows, counts = [], Counter()
    dead = ["zero_water"] if birth_water == 0 else []
    replay_count = updates = 0
    for i in range(1, 6):
        if dead:
            break
        action = actions[i - 1] if actions is not None else ("boire" if candidate else "attendre")
        decision_work = CognitiveWork(cycles=2 if candidate else 1, simulated_steps=3, memory_items=2)
        decision_after, decision_bill = debit_cognition(body, laws, decision_work)
        physical, reasons = transition(body, action, laws, decision_work,
                                       water_gain=2.0 if action == "boire" else 0)
        dead = list(reasons)
        learning_work = CognitiveWork() if dead else CognitiveWork(cycles=1, memory_items=1, replays=1)
        after, learning_bill = debit_cognition(physical, laws, learning_work)
        phases = {
            "decision": {"work": asdict(decision_work), "accounting": decision_bill,
                         "body_before": list(body), "body_after_debit": list(decision_after)},
            "learning": {"work": asdict(learning_work), "accounting": learning_bill,
                         "body_before": list(physical), "body_after_debit": list(after)}}
        bill = {ch: {k: decision_bill[ch][k] + learning_bill[ch][k] for k in totals[ch]}
                for ch in energy.CHANNELS}
        for ch in totals:
            for k in totals[ch]:
                totals[ch][k] += bill[ch][k]
        rows.append({"t": i, "action": action, "param": None, "option": action,
                     "body": list(after), "pos": [0, 0], "dead": dead,
                     "funding_phases": phases, "cognitive_accounting": bill,
                     "cognitive_work": {k: getattr(decision_work, k) + getattr(learning_work, k)
                                        for k in energy.WORK}})
        counts[action if action is not None else "physical_inactivity"] += 1
        replay_count += learning_work.replays
        updates += not dead
        body = after
    life = {"manifest": m, "world": world["name"], "life_seed": m["life_seed"], "horizon": 5,
            "steps_lived": len(rows), "terminal": "dead" if dead else "censored", "death_causes": dead,
            "trace": rows, "actions": dict(sorted(counts.items())), "final_body": [round(x, 6) for x in body],
            "cognitive_accounting": {"schema": "i3-cognitive-funding/v2", "status": "SETTLED_FOR_DECLARED_WORK",
                "shortfall_steps": 0, "pending_replays": 0, "pending_energy": 0.0, "pending_vigilance": 0.0,
                "totals": totals, "inactive_steps": counts["physical_inactivity"],
                "replays_executed": replay_count, "learning_updates": updates}}
    return reseal(life)


def receipt(life):
    return energy.energy_receipt(life, expected_protocol=PROTOCOL,
                                 expected_source_sha256=digest({"synthetic_fixture.py": "a" * 64}))


def panel(**kwargs):
    return [{"population": p, "case_id": "a", "reference": fixture(p, **kwargs),
             "candidate": fixture(p, candidate=True, **kwargs)} for p in range(8)]


def aggregate(pairs, expected=None):
    pin = digest({"synthetic_fixture.py": "a" * 64})
    return energy.population_energy(pairs, expected_cases=expected or {p: ["a"] for p in range(8)},
                                    expected_protocol=PROTOCOL, source_pins={a: pin for a in energy.ARMS})


class Stage0EnergyReceiptTests(unittest.TestCase):
    def test_two_real_tariff_phases_conserve_full_cost(self):
        life = fixture(candidate=True)
        out = receipt(life)
        self.assertEqual(out["steps_lived"], 5)
        for ch in energy.CHANNELS:
            self.assertAlmostEqual(out["paid"][ch], sum(out["phase_paid"][p][ch] for p in energy.PHASES))
        self.assertEqual(out["phase_work"]["learning"]["replays"], 5)

    def test_deliberate_wait_sleep_and_inactivity_are_separate(self):
        out = receipt(fixture(birth_water=80, actions=[None, "attendre", "dormir", None, "attendre"]))
        self.assertEqual((out["inactive_steps"], out["chosen_wait_steps"], out["sleep_steps"]), (2, 2, 1))

    def test_adapter_does_not_mutate_input(self):
        life = fixture()
        before = deepcopy(life)
        receipt(life)
        self.assertEqual(life, before)

    def test_early_death_is_retained_and_has_no_postmortem_learning(self):
        out = receipt(fixture())
        self.assertEqual((out["terminal"], out["steps_lived"]), ("dead", 2))
        self.assertEqual(out["phase_work"]["learning"]["cycles"], 1)

    def test_zero_step_physical_death_is_not_missing_data(self):
        out = receipt(fixture(birth_water=0))
        self.assertEqual((out["terminal"], out["steps_lived"], out["paid"]["energy"]), ("dead", 0, 0))

    def test_missing_or_truncated_trace_rejected(self):
        for remove in (True, False):
            life = fixture()
            if remove:
                life.pop("trace")
            else:
                life["trace"].pop()
            with self.assertRaises(ValueError):
                receipt(life)

    def test_explicit_protocol_and_source_locks(self):
        life = fixture()
        for args in ({"expected_protocol": "other", "expected_source_sha256": life["manifest"]["source"]["sha256"]},
                     {"expected_protocol": PROTOCOL, "expected_source_sha256": ""}):
            with self.assertRaises(ValueError):
                energy.energy_receipt(life, **args)
        life["manifest"]["source"]["files"]["extra.py"] = "b" * 64
        reseal(life)
        with self.assertRaises(ValueError):
            receipt(life)

    def test_nonfinite_negative_and_boolean_costs_fail(self):
        for value in (float("nan"), float("inf"), -0.1, True):
            life = fixture()
            life["trace"][0]["funding_phases"]["decision"]["accounting"]["energy"]["paid"] = value
            with self.assertRaises(ValueError):
                receipt(life)

    def test_invalid_work_counters_fail(self):
        for value in (True, -1, 0.5, float("nan")):
            life = fixture()
            life["trace"][0]["funding_phases"]["decision"]["work"]["cycles"] = value
            with self.assertRaises(ValueError):
                receipt(life)

    def test_resigned_phase_body_tampering_still_fails(self):
        life = fixture()
        life["trace"][0]["funding_phases"]["decision"]["body_after_debit"][0] += 1
        reseal(life)
        with self.assertRaises(ValueError):
            receipt(life)

    def test_resigned_bill_that_does_not_match_work_fails(self):
        life = fixture()
        bill = life["trace"][0]["funding_phases"]["decision"]["accounting"]["energy"]
        bill["requested"] = bill["paid"] = 0.0
        reseal(life)
        with self.assertRaises(ValueError):
            receipt(life)

    def test_resigned_postmortem_learning_fails(self):
        life = fixture()
        last = life["trace"][-1]
        part = last["funding_phases"]["learning"]
        part["work"]["cycles"] = 1
        after, bill = debit_cognition(part["body_before"], BodyLaws(), CognitiveWork(cycles=1))
        part["body_after_debit"], part["accounting"] = list(after), bill
        reseal(life)
        with self.assertRaisesRegex(ValueError, "postmortem learning"):
            receipt(life)

    def test_replay_inactivity_totals_and_chain_mismatches_fail(self):
        for key in ("replays_executed", "inactive_steps"):
            life = fixture()
            life["cognitive_accounting"][key] += 1
            reseal(life)
            with self.assertRaises(ValueError):
                receipt(life)
        for key in ("trace_head", "evidence_head", "manifest_id"):
            life = fixture()
            life[key] = "0" * 64
            with self.assertRaises(ValueError):
                receipt(life)
        life = fixture()
        life["cognitive_accounting"]["totals"]["energy"]["paid"] += 1
        reseal(life)
        with self.assertRaises(ValueError):
            receipt(life)

    def test_false_censoring_crash_and_missing_cause_fail(self):
        for terminal in ("censored", "crash", "incomplete"):
            life = fixture()
            life["terminal"] = terminal
            with self.assertRaises(ValueError):
                receipt(life)
        life = fixture()
        life["death_causes"] = []
        with self.assertRaises(ValueError):
            receipt(life)


class Stage0EnergyPopulationTests(unittest.TestCase):
    def test_complete_panel_retains_unequal_spending_and_lived_time(self):
        out = aggregate(panel())
        self.assertEqual(len(out["populations"]), 8)
        self.assertFalse(out["independence_authenticated"])
        self.assertFalse(out["realized_cost_parity_assumed"])
        for row, contrast in zip(out["populations"], out["paired_differences"]):
            self.assertEqual(row["reference"]["dead"], 1)
            self.assertEqual(row["candidate"]["censored"], 1)
            self.assertEqual(contrast["lived_steps_difference"], 3)
            self.assertGreater(contrast["paid_difference"]["energy"], 0)
            self.assertEqual(contrast["censored_fraction_difference"], 1)
            self.assertAlmostEqual(row["reference"]["paid_per_lived_step"]["energy"],
                                   row["reference"]["paid"]["energy"] / 2)

    def test_rate_uses_all_lived_steps_not_mean_of_life_rates(self):
        pairs = panel()
        pairs.append({"population": 0, "case_id": "b",
                      "reference": fixture(0, birth_water=80, label="b"),
                      "candidate": fixture(0, birth_water=80, label="b", candidate=True)})
        expected = {p: ["a"] for p in range(8)}
        expected[0].append("b")
        out = aggregate(pairs, expected)["populations"][0]["reference"]
        first, second = receipt(pairs[0]["reference"]), receipt(pairs[-1]["reference"])
        self.assertEqual((out["dead"], out["censored"], out["steps_lived"]), (1, 1, 7))
        self.assertAlmostEqual(out["paid_per_lived_step"]["energy"], out["paid"]["energy"] / 7)
        mean_life_rate = (first["paid"]["energy"] / 2 + second["paid"]["energy"] / 5) / 2
        self.assertNotAlmostEqual(out["paid_per_lived_step"]["energy"], mean_life_rate)

    def test_zero_step_lives_have_undefined_rates_not_zero_cost_efficiency(self):
        out = aggregate(panel(birth_water=0))
        for row in out["populations"]:
            self.assertIsNone(row["reference"]["inactive_fraction"])
            self.assertIsNone(row["candidate"]["paid_per_lived_step"]["energy"])
            self.assertEqual(row["reference"]["zero_step_lives"], 1)
        self.assertTrue(all(r["inactive_fraction_difference"] is None for r in out["paired_differences"]))

    def test_complete_case_envelope_and_no_duplicates(self):
        pairs = panel()
        for bad in (pairs[:-1], pairs + [deepcopy(pairs[0])]):
            with self.assertRaises(ValueError):
                aggregate(bad)
        pairs[0]["population"] = False
        with self.assertRaises(ValueError):
            aggregate(pairs)

    def test_no_life_level_or_missing_population_inference(self):
        for expected in ({p: ["a"] for p in range(7)}, {p: ["a"] for p in range(40)}):
            with self.assertRaises(ValueError):
                aggregate(panel(), expected)

    def test_unequal_paired_world_seed_or_horizon_fail(self):
        for field in ("world", "life_seed", "horizon"):
            pairs = panel()
            life = pairs[0]["candidate"]
            if field == "world":
                life["world"] = life["manifest"]["world"]["name"] = "other"
            elif field == "life_seed":
                life["life_seed"] = life["manifest"]["life_seed"] = 999
            else:
                life["horizon"] = life["manifest"]["horizon"] = 6
                life["terminal"] = "dead"  # A false terminal may fail before pair matching.
            reseal(life)
            with self.assertRaises(ValueError):
                aggregate(pairs)

    def test_relabelled_population_and_repeated_same_life_fail(self):
        pairs = panel()
        for arm in energy.ARMS:
            pairs[1][arm] = deepcopy(pairs[0][arm])
        with self.assertRaises(ValueError):
            aggregate(pairs)
        pairs = panel()
        extra = deepcopy(pairs[0])
        extra["case_id"] = "second"
        expected = {p: ["a"] for p in range(8)}
        expected[0].append("second")
        with self.assertRaises(ValueError):
            aggregate(pairs + [extra], expected)

    def test_input_order_does_not_change_aggregates(self):
        pairs = panel()
        self.assertEqual(aggregate(pairs), aggregate(list(reversed(pairs))))

    def test_sources_may_differ_but_pins_must_be_explicit(self):
        pairs = panel()
        pin = pairs[0]["reference"]["manifest"]["source"]["sha256"]
        for pair in pairs:
            pair["candidate"]["manifest"]["source"]["files"]["candidate.py"] = "c" * 64
            reseal(pair["candidate"])
        candidate_pin = pairs[0]["candidate"]["manifest"]["source"]["sha256"]
        out = energy.population_energy(pairs, expected_cases={p: ["a"] for p in range(8)},
                expected_protocol=PROTOCOL, source_pins={"reference": pin, "candidate": candidate_pin})
        self.assertEqual(len(out["populations"]), 8)


class Stage0EnergyRuntimeIntegrationTests(unittest.TestCase):
    def test_actual_development_receipts_and_observer_rng_parity(self):
        from i3.lab.p2_ecologies import world_for
        from i3.modules.genome import generation_zero
        from i3.modules.mind import Mind
        from i3.runtime.life import run_life
        from i3.runtime.provenance import source_snapshot
        source_pin = source_snapshot()["sha256"]
        original_decide = Mind.decide
        states = []

        def monitored_decide(mind, *args, **kwargs):
            result = original_decide(mind, *args, **kwargs)
            states.append(mind.rng.getstate())
            return result

        pairs = []
        # Existing development fixture keys, not Stage-0 selection or validation.
        # Eight software labels here are NOT eight new scientific populations.
        for p in range(8):
            spec = world_for("stable", "development", p)
            genome = generation_zero(901 + p)
            common = dict(keep_trace=True, protocol=PROTOCOL, observer_mind_digest=True,
                          score_addend_mode="normal" if p % 2 == 0 else "discard_curiosity_bonus")
            with patch.object(Mind, "decide", monitored_decide):
                states.clear()
                control = run_life(genome, spec, 910000 + p, 8, **common)
                control_rng = list(states)
                states.clear()
                observed = run_life(genome, spec, 910000 + p, 8, observer_full_competition=True, **common)
                self.assertEqual(control_rng, states)
            a = energy.energy_receipt(control, expected_protocol=PROTOCOL, expected_source_sha256=source_pin)
            b = energy.energy_receipt(observed, expected_protocol=PROTOCOL, expected_source_sha256=source_pin)
            self.assertEqual(a, b)
            for key in ("actions", "final_body", "outcome_model_sha256", "spatial_beliefs_sha256"):
                self.assertEqual(control[key], observed[key])
            for row, original in zip(observed["observer_full_competition"]["steps"], observed["trace"]):
                self.assertEqual(row["paid_decision_work"], original["funding_phases"]["decision"]["work"])
            pairs.append({"population": p, "case_id": "software", "reference": control, "candidate": observed})
        out = energy.population_energy(pairs, expected_cases={p: ["software"] for p in range(8)},
                expected_protocol=PROTOCOL, source_pins={a: source_pin for a in energy.ARMS})
        self.assertTrue(all(r["paid_difference"] == {"energy": 0.0, "vigilance": 0.0}
                            for r in out["paired_differences"]))

    def test_runtime_zero_step_death_is_a_receipt(self):
        from i3.lab.p2_ecologies import world_for
        from i3.modules.genome import generation_zero
        from i3.runtime.life import run_life
        from i3.runtime.provenance import source_snapshot
        source_pin = source_snapshot()["sha256"]
        spec = replace(world_for("stable", "development", 0), body=(80., 80., 0., 80., 80.))
        life = run_life(generation_zero(901), spec, 19, 8, keep_trace=True, protocol=PROTOCOL)
        out = energy.energy_receipt(life, expected_protocol=PROTOCOL, expected_source_sha256=source_pin)
        self.assertEqual((out["terminal"], out["steps_lived"]), ("dead", 0))


if __name__ == "__main__":
    unittest.main()
