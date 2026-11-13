"""Engineering check: the P1.3 reference never reads three genome genes.

`omega`, `temperament.affiliation` and `temperament.reward_sensitivity` are
drawn and mutated in genome v4 but are not read by the reference `Mind`.
A lineage protocol may therefore use them as neutral markers only if a
reference life is step-for-step identical when nothing else changes.

Engineering-cohort worlds only: never evidence, no scientific World or index.
"""
from copy import deepcopy
import unittest

from i3.lab.engineering_cohort import engineering_world, is_engineering_seed
from i3.lab import engineering_cohort
from i3.modules.genome import BOUNDS, generation_zero, validate
from i3.runtime.life import run_life

NEUTRAL_MARKERS = ("omega", "temperament.affiliation",
                   "temperament.reward_sensitivity")
FIXTURES = (("stable", 0), ("depletion", 1), ("pulse", 2))
FOUNDER_SEED = 424_242
LIFE_SEED = 777
HORIZON = 80
IDENTITY_FIELDS = ("manifest", "manifest_id", "evidence_head", "genome",
                   "trace_head")
TIMING_FIELDS = ("mean_step_ms", "run_elapsed_ms")


def _variant(base: dict, changes: dict) -> dict:
    genome = deepcopy(base)
    genome["genes"].update(changes)
    validate(genome)
    return genome


def _life(genome: dict, family: str, index: int) -> dict:
    spec = engineering_world(family, index)
    return run_life(genome, spec, LIFE_SEED, HORIZON, keep_trace=True)


def _lived(outcome: dict) -> dict:
    """Everything the individual did and paid, without identity or timing."""
    return {key: value for key, value in outcome.items()
            if key not in IDENTITY_FIELDS + TIMING_FIELDS}


class ReferenceNeutralMarkerGeneTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = generation_zero(FOUNDER_SEED)
        cls.lives = {fixture: _life(cls.base, *fixture) for fixture in FIXTURES}

    def test_fixtures_are_engineering_worlds_only(self):
        for _, index in FIXTURES:
            self.assertTrue(is_engineering_seed(engineering_cohort.ENGINEERING[index]))
        for outcome in self.lives.values():
            self.assertEqual(outcome["manifest"]["protocol"],
                             "UNREGISTERED_ENGINEERING")
            self.assertEqual(len(outcome["trace"]), outcome["steps_lived"])

    def test_marker_genes_at_both_bounds_leave_every_step_identical(self):
        checked = 0
        for name in NEUTRAL_MARKERS:
            for bound in BOUNDS[name]:
                if bound == self.base["genes"][name]:
                    continue
                genome = _variant(self.base, {name: bound})
                for fixture in FIXTURES:
                    reference = self.lives[fixture]
                    outcome = _life(genome, *fixture)
                    self.assertEqual(outcome["trace"], reference["trace"],
                                     (name, bound, fixture))
                    self.assertEqual(_lived(outcome), _lived(reference),
                                     (name, bound, fixture))
                    # The genome itself did change: identities must differ.
                    self.assertNotEqual(outcome["genome"], reference["genome"])
                    self.assertNotEqual(outcome["manifest_id"],
                                        reference["manifest_id"])
                    checked += 1
        self.assertEqual(checked, len(NEUTRAL_MARKERS) * 2 * len(FIXTURES))

    def test_all_three_markers_changed_together_leave_every_step_identical(self):
        genome = _variant(self.base, {name: BOUNDS[name][0]
                                      for name in NEUTRAL_MARKERS})
        for fixture in FIXTURES:
            self.assertEqual(_life(genome, *fixture)["trace"],
                             self.lives[fixture]["trace"], fixture)

    def test_positive_control_an_expressed_gene_changes_the_life(self):
        genome = _variant(self.base, {"beta_u": BOUNDS["beta_u"][0]})
        changed = [fixture for fixture in FIXTURES
                   if _life(genome, *fixture)["trace"] != self.lives[fixture]["trace"]]
        self.assertEqual(changed, list(FIXTURES))


if __name__ == "__main__":
    unittest.main()
