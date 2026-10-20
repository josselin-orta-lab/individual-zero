"""Research twins share innate traits, never live identity or Q experience."""
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"src"))
from i1.runtime.i1_birth_temperament import temperament_for_life, configure_birth_temperament

class TwinTemperament(unittest.TestCase):
    def test_original_factorial_had_confounded_birth_temperaments(self):
        ids=[f"i1:q-factorial:memory-corridor:23111:{arm}:0" for arm in
             ("local_q_neutral","local_q_rank_only","local_q_evidence_only","local_q_learned")]
        self.assertEqual(len({tuple(temperament_for_life(x).as_dict().values()) for x in ids}),4)
    def test_shared_source_is_stable_and_validated(self):
        source="i1:research-twin:memory-corridor:24103"
        self.assertEqual(temperament_for_life(source),temperament_for_life(source))
        for wrong in ("i1:q-factorial:old","i0",None):
            with self.subTest(wrong=wrong):
                with self.assertRaises((ValueError,TypeError)):
                    configure_birth_temperament(object(),life_id="i1:other",temperament_source_id=wrong)
    def test_research_only_M11_and_no_I0(self):
        natural=(ROOT/"src/i1/runtime/i1_natural_runtime.py").read_text()
        m11=(ROOT/"src/i1/runtime/m11_transactional_mortal.py").read_text()
        self.assertIn('kwargs.pop("i1_research_temperament_source_id", None)',natural)
        self.assertIn('getattr(runtime, "_i1_research_temperament_source_id", None)',m11)
if __name__=="__main__":
    unittest.main()
