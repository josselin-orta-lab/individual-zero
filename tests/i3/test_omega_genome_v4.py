"""Genome-v4 contract for the owner-approved heritable omega disposition."""
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from i3.modules import genome as G
from i3.modules.body import BodyLaws, CognitiveBudget
from i3.modules.mind import Mind

COMMON_V3_DIGESTS = {
    0: "8d3258ef778c55edcc6eca4d3f9b8db591600238e41ae77e1bb0512021cc5d20",
    1: "08c4e9c1ff21696076f19fb0a348be027f080c8330443877e156a754fdb607b7",
    39: "c3dcb0188fb37a50d930ca8b702f6f724581c88cfb5f3528a3e60ea49400f624",
    2000000: "528c8940531cbd8bcd0c4d7bcc9004c4089df63e4a01214f54b5303ca2df6b07",
    2000039: "b82641779ab4180b6e26ffa0ff57b5604afa47f8b89862e7488bfffb032c38be",
}


def common_v3_digest(genome):
    genes = {
        key: genome["genes"][key]
        for key in G.GENE_ORDER if key != "omega"
    }
    payload = json.dumps(
        genes, sort_keys=True, separators=(",", ":")).encode("ascii")
    return sha256(payload).hexdigest()


def configured_candidate(genome):
    mind = Mind(genome, 313, simulation_mode="candidate_f")
    mind.projection_accounting = "event_local_quadratic4"
    mind.effects.observe(("attendre",), (-.35, -.2, -.4, .2, 0.))
    mind.effects.observe(("dormir",), (3., -.35, -.4, 0., 4.))
    mind.effects.observe(("boire",), (0., 0., 30., 0., 0.))
    mind._drift = mind.drift()
    return mind


class OmegaGenomeV4Tests(unittest.TestCase):
    def test_schema_has_exactly_one_new_final_gene(self):
        self.assertEqual(G.SCHEMA, "i3-genome-v4")
        self.assertEqual(len(G.GENE_ORDER), 31)
        self.assertEqual(G.GENE_ORDER[-1], "omega")
        self.assertEqual(G.BOUNDS["omega"], (-1.0, 1.0))

    def test_generation_zero_preserves_all_v3_common_gene_draws(self):
        for seed, expected in COMMON_V3_DIGESTS.items():
            with self.subTest(seed=seed):
                genome = G.generation_zero(seed)
                self.assertEqual(common_v3_digest(genome), expected)

    def test_midpoint_is_neutral_and_generation_zero_has_no_positive_default(self):
        self.assertEqual(G.midpoint()["genes"]["omega"], 0.0)
        values = [G.generation_zero(seed)["genes"]["omega"] for seed in range(40)]
        self.assertTrue(all(-1.0 <= value <= 1.0 for value in values))
        self.assertLess(min(values), 0.0)
        self.assertGreater(max(values), 0.0)

    def test_v3_mapping_is_rejected_without_migration(self):
        genome = deepcopy(G.generation_zero(4))
        genome["schema"] = "i3-genome-v3"
        genome["genes"].pop("omega")
        with self.assertRaises(ValueError):
            G.validate(genome)

    def test_mutation_includes_bounded_omega_without_algorithm_exception(self):
        parent = G.generation_zero(9)
        a = G.mutate(parent, 17)
        b = G.mutate(parent, 17)
        self.assertEqual(a, b)
        self.assertIn("omega", a["genes"])
        self.assertGreaterEqual(a["genes"]["omega"], -1.0)
        self.assertLessEqual(a["genes"]["omega"], 1.0)

    def test_current_reference_mind_does_not_use_omega(self):
        neutral = G.midpoint()
        hopeful = deepcopy(neutral)
        fearful = deepcopy(neutral)
        hopeful["genes"]["omega"] = 1.0
        fearful["genes"]["omega"] = -1.0
        G.validate(hopeful)
        G.validate(fearful)

        a = Mind(hopeful, 41)
        b = Mind(fearful, 41)
        for name in (
                "theta", "p", "w", "gammas", "alpha", "beta_u", "lambda_r",
                "kappa0", "inertia", "n_base", "h_max", "m_max",
                "belief_rate", "d_max"):
            self.assertEqual(getattr(a, name), getattr(b, name), name)
        self.assertFalse(hasattr(a, "omega"))
        self.assertFalse(hasattr(b, "omega"))

    def test_candidate_f_values_are_omega_blind_until_explicit_wiring(self):
        neutral = G.midpoint()
        hopeful = deepcopy(neutral)
        fearful = deepcopy(neutral)
        hopeful["genes"]["omega"] = 1.0
        fearful["genes"]["omega"] = -1.0
        body = (80., 40., 30., 80., 80.)
        plan = (("boire",), ("attendre",))

        values = []
        for genome in (hopeful, fearful):
            mind = configured_candidate(genome)
            budget = CognitiveBudget(body, BodyLaws())
            values.append(mind.simulate(body, plan, 4, budget))
        self.assertEqual(values[0], values[1])


if __name__ == "__main__":
    unittest.main()
