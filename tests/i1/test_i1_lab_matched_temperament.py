"""Matched temperament research controls without a single simulated step."""
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"scripts"))
from build_i1_fork import generate

class LabTwinTests(unittest.TestCase):
    def test_pure_research_projection_and_default(self):
        with TemporaryDirectory() as d:
            out=Path(d)/"generated"
            generate(out)
            sys.path.insert(0,str(out))
            from i1lab.stage11_reference_fixture import build_stage11_reference_runtime
            from i1lab.matched_temperament_research import matched_temperament_configuration
            from i1lab.i1_birth_temperament import configure_birth_temperament
            fixture=build_stage11_reference_runtime(autonomous_mortal=True)._stage11_config
            twins=[]
            for arm in ("neutral","rank_only","evidence_only","learned"):
                conf=matched_temperament_configuration(
                    fixture,life_id=f"i1:test:independent:{arm}",
                    world="test-world",seed=24103)
                s4=conf.stage9.stage8.stage7.stage6.stage4
                twins.append((conf.temperament_parameters.temperament,
                    dict(s4.gatekeeper.weights),dict(s4.value_needs.weights),
                    s4.competition.inertia,conf.stage9.stage8.evaluation.extrinsic_gain))
            self.assertEqual(twins,[twins[0]]*4)
            independent=configure_birth_temperament(
                fixture,life_id="i1:test:independent:neutral")
            self.assertNotEqual(independent.temperament_parameters.temperament,
                                twins[0][0])
            with self.assertRaises(ValueError):
                matched_temperament_configuration(fixture,life_id="i1:test",
                                                  world="invalid:world",seed=1)
            with self.assertRaises(ValueError):
                matched_temperament_configuration(fixture,life_id="i1:test",
                                                  world="test",seed=True)

if __name__=="__main__":
    unittest.main()
