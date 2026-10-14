"""Fail-closed instrumental frontier opt-in contracts."""
from dataclasses import replace
import unittest
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from i0.modules.geographic_exploration import GeographicTarget


class InstrumentalGeographicContracts(unittest.TestCase):
    def test_reference_remains_off(self):
        runtime=build_stage11_reference_runtime(enable_geography=True)
        self.assertFalse(runtime._stage11_config.instrumental_geographic_value)
        self.assertIsNone(runtime.stage8_option_evaluator._instrumental_planning)

    def test_flag_requires_actual_geographic_owner(self):
        runtime=build_stage11_reference_runtime(enable_geography=False)
        with self.assertRaises(ValueError):
            replace(runtime._stage11_config,
                    instrumental_geographic_value=True).validate()

    def test_unoffered_frontier_gives_no_interest(self):
        runtime=build_stage11_reference_runtime(enable_geography=True)
        target=GeographicTarget(
            ref="frontier:3:2:from:2:2",source_t_monde=1,
            origin=(2,2),destination=(3,2),direction="east")
        target.validate()
        result=runtime.exploration.geographic_interest_for_target(target)
        self.assertEqual(result.status,"unavailable")
        self.assertIsNone(result.value)


if __name__=="__main__":
    unittest.main()
