"""#318 verify pure born-tau and effective Stage11 parameters for 2x2 twins.

No new mortal actor is created, no physical world step is executed, and no
historical WAL is replayed. Projection is the EXACT I1 source constructor
used by the sealed 32-life birth SHA (not a shadow numerical formula).
"""
from __future__ import annotations

from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

WORLDS=("memory-corridor","water-isolated-corridor")
SEEDS=(24103,24223,24359,24481)
ARMS=("local_q_neutral","local_q_rank_only","local_q_evidence_only","local_q_learned")


class MatchedProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sandbox=TemporaryDirectory(prefix="i1-318-parameter-only-")
        output=Path(cls.sandbox.name)/"source"
        generate(output)
        sys.path.insert(0,str(output))
        from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
        from i1lab.i1_birth_temperament import (
            configure_birth_temperament, temperament_for_life,
        )
        cls.base=build_stage11_reference_runtime(
            autonomous_mortal=True)._stage11_config
        cls.project=staticmethod(configure_birth_temperament)
        cls.tau=staticmethod(temperament_for_life)

    @classmethod
    def tearDownClass(cls):
        cls.sandbox.cleanup()

    def test_all_eight_four_arm_blocks_have_identical_projected_traits(self):
        different_blocks=set()
        for world in WORLDS:
            for seed in SEEDS:
                source=f"i1:research-twin:{world}:{seed}"
                different_blocks.add(tuple(self.tau(source).as_dict().values()))
                derived=[]
                for arm in ARMS:
                    individual=f"i1:q-factorial-twin:{world}:{seed}:{arm}:0"
                    cfg=self.project(
                        self.base,life_id=individual,
                        temperament_source_id=source,
                    )
                    s4=cfg.stage9.stage8.stage7.stage6.stage4
                    derived.append((
                        cfg.temperament_parameters.as_dict(),
                        dict(s4.gatekeeper.weights),
                        dict(s4.value_needs.weights),
                        s4.competition.inertia,
                        cfg.stage9.stage8.evaluation.extrinsic_gain,
                    ))
                with self.subTest(world=world,seed=seed):
                    self.assertEqual(derived,[derived[0]]*len(ARMS))
        self.assertEqual(len(different_blocks),8)

    def test_default_birth_still_uses_unique_individual_temperament(self):
        a=self.project(self.base,life_id="i1:control:one")
        b=self.project(self.base,life_id="i1:control:two")
        self.assertNotEqual(
            a.temperament_parameters.as_dict(),
            b.temperament_parameters.as_dict(),
        )

    def test_reject_forged_matched_source(self):
        with self.assertRaises(ValueError):
            self.project(
                self.base,life_id="i1:valid:one",
                temperament_source_id="i1:unregistered:not-a-twin",
            )


if __name__=="__main__":
    unittest.main()
