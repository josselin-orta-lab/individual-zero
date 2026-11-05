"""I3 P1 core contract tests (software validity only, no scientific claim)."""
import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules import genome as G
from i3.modules.body import BodyLaws, CognitiveWork, capacities, transition
from i3.modules.mind import Mind
from i3.modules.world import FoodPatch, WaterSource, World, WorldSpec
from i3.runtime.life import run_life
from i3.lab.dev_worlds import dev_long_corridor, dev_open_field

LAWS = BodyLaws()
IDLE = CognitiveWork()


def small_world(offset=(0, 0), names=("red", "blue")):
    ox, oy = offset
    return WorldSpec(
        name="test-small", width=9 + ox, height=7 + oy, spawn=(2 + ox, 2 + oy),
        body=(70.0, 50.0, 45.0, 90.0, 100.0),
        water={(6 + ox, 2 + oy): WaterSource(gain=30.0, stock=2, max_stock=2, restock_every=9)},
        food={(2 + ox, 5 + oy): FoodPatch(names[0], 2, 2, restock_every=11),
              (7 + ox, 5 + oy): FoodPatch(names[1], 2, 2, restock_every=11)},
        token_effects={names[0]: (12.0, 0.0), names[1]: (5.0, -6.0)},
    )


class GenomeTests(unittest.TestCase):
    def test_generation_zero_and_midpoint_are_admissible(self):
        for seed in range(20):
            G.validate(G.generation_zero(seed))
        G.validate(G.midpoint())

    def test_closed_schema_refuses_world_facts_and_extra_fields(self):
        g = G.generation_zero(1)
        bad = copy.deepcopy(g)
        bad["genes"]["prefer.berry_a"] = 1.0
        with self.assertRaises(ValueError):
            G.validate(bad)
        bad = copy.deepcopy(g)
        bad["memories"] = []
        with self.assertRaises(ValueError):
            G.validate(bad)
        bad = copy.deepcopy(g)
        bad["genes"]["beta_u"] = 99.0
        with self.assertRaises(ValueError):
            G.validate(bad)

    def test_mutation_is_bounded_and_deterministic(self):
        g = G.generation_zero(3)
        a, b = G.mutate(g, 7), G.mutate(g, 7)
        self.assertEqual(G.digest(a), G.digest(b))
        self.assertNotEqual(G.digest(a), G.digest(g))
        for k, (lo, hi) in G.BOUNDS.items():
            self.assertTrue(lo <= a["genes"][k] <= hi)


class BodyTests(unittest.TestCase):
    def test_v4_physics_parity_for_waiting(self):
        nxt, dead = transition((50.0, 60.0, 40.0, 90.0, 100.0), "attendre", LAWS, IDLE)
        self.assertEqual(dead, ())
        for got, want in zip(nxt, (49.65, 59.78, 39.6, 90.2, 100.0)):
            self.assertAlmostEqual(got, want, places=9)

    def test_sleep_is_substrate_limited_and_restores_vigilance(self):
        nxt, _ = transition((50.0, 60.0, 40.0, 100.0, 50.0), "dormir", LAWS, IDLE)
        self.assertAlmostEqual(nxt[0], 53.0)
        self.assertAlmostEqual(nxt[1], 60.0 - 0.2 - 3.0 * 0.05)
        self.assertAlmostEqual(nxt[4], 54.0)

    def test_cognition_is_paid_in_energy_and_vigilance(self):
        work = CognitiveWork(cycles=10, simulated_steps=100, memory_items=500, replays=10)
        free, _ = transition((50.0, 60.0, 40.0, 90.0, 100.0), "attendre", LAWS, IDLE)
        paid, _ = transition((50.0, 60.0, 40.0, 90.0, 100.0), "attendre", LAWS, work)
        self.assertAlmostEqual(free[0] - paid[0], 0.2 + 0.2 + 0.1 + 0.05)
        self.assertAlmostEqual(free[4] - paid[4], 0.5 + 0.2 + 0.1)

    def test_capacities_are_vulnerable(self):
        full = capacities((100.0, 50.0, 50.0, 100.0, 100.0), 8, 20)
        weak = capacities((10.0, 50.0, 50.0, 40.0, 20.0), 8, 20)
        self.assertGreater(full[0], weak[0])
        self.assertGreater(full[1], weak[1])
        self.assertLess(full[2], weak[2])

    def test_vital_channel_at_zero_is_death(self):
        _, dead = transition((50.0, 60.0, 0.3, 90.0, 100.0), "attendre", LAWS, IDLE)
        self.assertEqual(dead, ("zero_water",))


class WorldTests(unittest.TestCase):
    def test_capture_is_local_and_first_person(self):
        w = World(small_world())
        cap = w.capture()
        self.assertEqual(set(cap), {"body", "inventory", "here", "neighbors"})
        self.assertEqual(len(cap["neighbors"]), 4)
        flat = repr(cap)
        for hidden in ("12.0", "-6.0", "token_effects", "spawn"):
            self.assertNotIn(hidden, flat)

    def test_death_is_irreversible(self):
        spec = small_world()
        spec.body = (50.0, 50.0, 0.3, 90.0, 100.0)
        w = World(spec)
        out = w.step("attendre", None, IDLE)
        self.assertEqual(out["dead"], ("zero_water",))
        with self.assertRaises(RuntimeError):
            w.step("attendre", None, IDLE)


class MindTests(unittest.TestCase):
    def test_newborn_depends_only_on_genome_and_seed(self):
        g = G.generation_zero(5)
        a, b = Mind(g, 1), Mind(g, 1)
        self.assertEqual(a.values, b.values)
        self.assertEqual(a.effects.stats, {})
        self.assertEqual(a.map, {})
        self.assertEqual(list(a.buffer), [])

    def test_replay_is_exact(self):
        g = G.generation_zero(9)
        r1 = run_life(g, dev_open_field(), 4, 150)
        r2 = run_life(g, dev_open_field(), 4, 150)
        self.assertEqual(r1["trace_head"], r2["trace_head"])
        self.assertEqual(r1["steps_lived"], r2["steps_lived"])

    def test_renaming_invariance(self):
        # Same geometry, species names permuted against their alphabetical
        # order: no decision may depend on a world name.
        g = G.generation_zero(2)
        base = run_life(g, small_world(), 3, 120, keep_trace=True)
        moved = run_life(g, small_world(names=("zz-q", "aa-p")), 3, 120, keep_trace=True)
        self.assertEqual([r["action"] for r in base["trace"]],
                         [r["action"] for r in moved["trace"]])
        self.assertEqual([r["option"] for r in base["trace"]],
                         [r["option"] for r in moved["trace"]])
        self.assertEqual([r["body"] for r in base["trace"]],
                         [r["body"] for r in moved["trace"]])

    def test_no_abstention_by_default_on_ties(self):
        m = Mind(G.midpoint(), 0)
        m.intention = None
        winner, used = m._compete([("a", 0.0), ("b", 0.0), ("c", 0.0)], 4)
        self.assertIn(winner, ("a", "b", "c"))
        self.assertEqual(used, 4)

    def test_waiting_is_not_privileged(self):
        m = Mind(G.midpoint(), 0)
        winner, _ = m._compete([("attendre", -1.0), ("boire", 0.5), ("dormir", -0.8)], 4)
        self.assertEqual(winner, "boire")

    def test_every_life_acts_and_is_fast(self):
        for spec in (dev_open_field(), dev_long_corridor()):
            r = run_life(G.midpoint(), spec, 1, 100)
            self.assertNotIn("NO_ACTION", r["actions"])
            self.assertLess(r["mean_step_ms"], 5.0)


if __name__ == "__main__":
    unittest.main()


class ProjectionTests(unittest.TestCase):
    def test_known_sleep_restores_energy_in_projection(self):
        m = Mind(G.midpoint(), 0)
        for _ in range(5):
            m.effects.observe(("dormir",), [3.0, -0.35, -0.4, 0.2, 4.0])
            m.effects.observe(("attendre",), [-0.4, -0.22, -0.4, 0.2, -0.1])
        tired = (5.0, 60.0, 60.0, 100.0, 100.0)
        rested = (90.0, 60.0, 60.0, 100.0, 100.0)
        _, end_tired = m.project(tired, m.drift())
        _, end_rested = m.project(rested, m.drift())
        self.assertGreaterEqual(end_tired[0], m.theta[0] - 1e-9)
        self.assertLess(end_tired[1], end_rested[1])  # sleeping costs food

    def test_without_sleep_experience_energy_is_held(self):
        m = Mind(G.midpoint(), 0)
        _, end = m.project((5.0, 60.0, 60.0, 100.0, 100.0), m.drift())
        self.assertAlmostEqual(end[0], 5.0)


class P12Tests(unittest.TestCase):
    def _genome(self, **genes):
        g = G.midpoint()
        g["genes"].update(genes)
        return G.validate(g)

    def test_place_belief_is_revised_at_the_inherited_rate(self):
        for rate, expect_forgotten in ((0.5, True), (0.02, False)):
            m = Mind(self._genome(belief_rate=rate), 0)
            cap_full = {"body": (80.0, 60.0, 60.0, 100.0, 100.0), "inventory": (),
                        "here": (False, ()), "neighbors": ((True, ()), (False, ()), (False, ()), (False, ()))}
            cap_dry = dict(cap_full, neighbors=((False, ()), (False, ()), (False, ()), (False, ())))
            for _ in range(20):
                m.perceive(cap_full, 0.0)
            for _ in range(8):
                m.perceive(cap_dry, 0.0)
            m.visible = ()
            self.assertEqual(m.presence((0, -1)) == 0.0, expect_forgotten)

    def test_exploration_options_are_headings_or_frontiers(self):
        spec = small_world()
        for reach, prefix in ((3, ("explorer:N", "explorer:E", "explorer:S", "explorer:W")),
                              (0, ("explorer:",))):
            m = Mind(self._genome(reach=float(reach)), 0)
            w = World(spec)
            cap = w.capture()
            inv = m.perceive(cap, 0.0)
            ids = [o[0] for o in m.options(inv, cap["body"], 10) if o[0].startswith("explorer:")]
            self.assertTrue(ids)
            for oid in ids:
                self.assertTrue(oid.startswith(prefix))
                if reach:
                    self.assertIn(oid, prefix)
                else:
                    self.assertRegex(oid, r"explorer:-?\d+,-?\d+$")
