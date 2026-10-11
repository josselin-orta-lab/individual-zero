"""DC-16 consolidation hypotheses belong to one canonical Stage-10 Causal Model."""
import unittest
from copy import deepcopy

from lab.determinism import canonical_causal_bytes,sha256_hex
from lab.stage9_reference_fixture import build_stage9_reference_runtime
from lab.stage10_reference_fixture import build_stage10_reference_runtime
from i0.modules.stage10_causal_model import Stage10CausalModel


def one_rule():
    predicate={
        "primitive":"boire","parameters":{},
        "observed_field":"drank","observed_value":"true",
    }
    return {
        "id":"hyp:"+sha256_hex(canonical_causal_bytes(predicate))[:28],
        "predicate":predicate,"status":"hypothese_causale",
        "source_episode_refs":["ep:1"],
        "source_event_refs":["cmd:1","transition:1"],
        "expires_at_step":100,"validated_for_safety":False,
    }


class Stage10CanonicalHypothesesTests(unittest.TestCase):
    def test_stage9_does_not_gain_consolidation_behavior(self):
        original=build_stage9_reference_runtime()
        enhanced=build_stage10_reference_runtime()
        self.assertNotIsInstance(original.causal_model,Stage10CausalModel)
        self.assertIsInstance(enhanced.causal_model,Stage10CausalModel)
        self.assertIs(enhanced._canonical_safety._model,enhanced.causal_model)
        self.assertEqual(
            [owner.owner_id for owner in enhanced.causal_owners].count("causal_model"),1)

    def test_private_hypothesis_is_invisible_until_owner_restore(self):
        r=build_stage10_reference_runtime()
        model=r.causal_model
        record=one_rule()
        baseline=deepcopy(model.export_causal_state())
        prepared=model.prepare_consolidated_rules(
            rules=[record],
            physical_by_episode={"ep:1":{"cmd:1","transition:1"}},
        )
        self.assertEqual(model.export_causal_state(),baseline)
        self.assertIsNone(model.get(record["id"]))
        model.restore_causal_state(prepared)
        visible=model.get(record["id"])
        self.assertIsNotNone(visible)
        self.assertEqual(visible.causal_status,"hypothese_causale")
        self.assertEqual(visible.safety_status,"aucun")
        self.assertEqual(visible.evidence_refs,("cmd:1","transition:1"))
        self.assertEqual(model.contingencies(status="etabli_pour_securite"),())
        self.assertEqual(model.export_causal_state(),prepared)

    def test_repeated_episode_does_not_duplicate_causal_evidence(self):
        model=build_stage10_reference_runtime().causal_model
        record=one_rule()
        initial=model.prepare_consolidated_rules(
            rules=[record],physical_by_episode={"ep:1":{"cmd:1","transition:1"}},
        )
        model.restore_causal_state(initial)
        repeated=model.prepare_consolidated_rules(
            rules=[record,record],
            physical_by_episode={"ep:1":{"cmd:1","transition:1"}},
        )
        self.assertEqual(len(repeated["consolidated_hypotheses"]),1)
        self.assertEqual(repeated["consolidated_hypotheses"][0]["source_episode_refs"],["ep:1"])
        self.assertEqual(repeated["consolidated_hypotheses"][0]["source_event_refs"],[
            "cmd:1","transition:1",
        ])

    def test_unwitnessed_or_safety_promoted_rule_fails_closed(self):
        model=build_stage10_reference_runtime().causal_model
        r=one_rule()
        with self.assertRaises(ValueError):
            model.prepare_consolidated_rules(
                rules=[r],physical_by_episode={"ep:1":{"cmd:1"}},
            )
        altered=deepcopy(r);altered["status"]="etablie"
        with self.assertRaises(ValueError):
            model.prepare_consolidated_rules(
                rules=[altered],
                physical_by_episode={"ep:1":{"cmd:1","transition:1"}},
            )
        altered=deepcopy(r);altered["validated_for_safety"]=True
        with self.assertRaises(ValueError):
            model.prepare_consolidated_rules(
                rules=[altered],
                physical_by_episode={"ep:1":{"cmd:1","transition:1"}},
            )

if __name__=="__main__":
    unittest.main()
