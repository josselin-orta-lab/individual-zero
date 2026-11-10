"""Software-only source/target leakage gates for native action-effect readouts."""
import json
import unittest
from unittest.mock import patch

from i3.lab import stage2_action_conditional_existing_effects as E
from i3.lab.stage2_compact_paid_first_person_engineering import _source_seal
from i3.modules.genome import midpoint
from i3.modules.mind import Mind
from i3.modules.world import World


class PassiveActionEffectProvenanceTests(unittest.TestCase):
    def test_predeclared_no_world_software_receipt(self):
        with patch.object(World, "__init__",
                          side_effect=AssertionError("no World permitted")):
            r = E.audit()
        print("I3_ACTION_CONDITIONAL_PROVENANCE_RESULT="+json.dumps(
            r, sort_keys=True))
        self.assertEqual(r["status"],"SOFTWARE_ACTION_LABEL_PROVENANCE_ONLY")
        self.assertTrue(r["frozen_same_body_action_forecasts_differ"])
        self.assertTrue(r["same_body_global_forecasts_identical"])
        self.assertTrue(r["unknown_action_exact_global_fallback"])
        self.assertTrue(r["no_action_specific_evidence_for_inactivity"])
        self.assertTrue(r["existing_reference_effects_not_retrained"])
        self.assertTrue(r["synthetic_prospectively_frozen_sha256"])
        self.assertEqual(set(r["synthetic_proper_scores"]),
                         {"action","global","persistence"})
        self.assertEqual(r["lived_outcomes_scored"],0)
        self.assertEqual(r["worlds_opened"],0)
        self.assertEqual(r["scientific_lives"],0)
        self.assertEqual(r["scientific_verdict"],"NOT_ISSUED")
        self.assertFalse(r["stage2_2_go"])
        self.assertFalse(r["fresh_world_opening_permitted"])
        self.assertFalse(r["external_readout_physically_paid"])
        self.assertFalse(r["native_effects_previously_lived_payment_attested"])

    def test_same_frozen_body_and_personal_effects_only_action_label_changes(self):
        source=E._fixture()
        original=_source_seal(source)
        body=E.SYNTHETIC_BODY
        wait=E.passive_readouts(source,body,"attendre")
        sleep=E.passive_readouts(source,body,"dormir")
        self.assertEqual(_source_seal(source),original)
        self.assertTrue(wait["action_specific_history"])
        self.assertTrue(sleep["action_specific_history"])
        self.assertEqual(wait["native_action_effect_key"],("attendre",))
        self.assertEqual(sleep["native_action_effect_key"],("dormir",))
        self.assertNotEqual(wait["scalar_forecasts"]["action"],
                            sleep["scalar_forecasts"]["action"])
        for reference in ("global","persistence"):
            self.assertEqual(wait["scalar_forecasts"][reference],
                             sleep["scalar_forecasts"][reference])
        self.assertNotEqual(wait["action_effect_delta"],
                            sleep["action_effect_delta"])

    def test_action_level_fallback_has_no_hidden_token_identity(self):
        body=E.SYNTHETIC_BODY
        first=Mind(midpoint(), 81111)
        second=Mind(midpoint(), 81111)
        delta=(0.,0.,12.,0.,0.)
        first.effects.observe(("boire","opaque-ABC"),delta)
        second.effects.observe(("boire","different-XYZ"),delta)
        a=E.passive_readouts(first,body,"boire")
        b=E.passive_readouts(second,body,"boire")
        self.assertTrue(a["action_specific_history"])
        self.assertEqual(a["native_action_effect_key"],("boire",None))
        self.assertEqual(a["scalar_forecasts"],b["scalar_forecasts"])
        self.assertEqual(a["native_selected_effect_sha256"],
                         b["native_selected_effect_sha256"])
        self.assertFalse("opaque-ABC" in json.dumps(a))
        self.assertFalse("different-XYZ" in json.dumps(b))

    def test_no_personal_action_history_uses_global_not_invented_rule(self):
        source=E._fixture()
        body=E.SYNTHETIC_BODY
        missing=E.passive_readouts(source,body,"boire")
        inactive=E.passive_readouts(source,body,None)
        self.assertFalse(missing["action_specific_history"])
        self.assertFalse(inactive["action_specific_history"])
        self.assertTrue(missing["global_effect_history"])
        self.assertIsNone(missing["native_action_effect_key"])
        self.assertEqual(missing["scalar_forecasts"]["action"],
                         missing["scalar_forecasts"]["global"])
        self.assertEqual(inactive["scalar_forecasts"]["action"],
                         inactive["scalar_forecasts"]["global"])
        empty=Mind(midpoint(),81112)
        fresh=E.passive_readouts(empty,body,"dormir")
        self.assertFalse(fresh["global_effect_history"])
        self.assertFalse(fresh["action_specific_history"])
        self.assertEqual(fresh["action_effect_delta"],(0.,)*5)
        self.assertEqual(fresh["scalar_forecasts"]["action"],
                         fresh["scalar_forecasts"]["persistence"])

    def test_equal_lived_mean_is_exact_null_even_when_labels_differ(self):
        mind=Mind(midpoint(),81113)
        body=E.SYNTHETIC_BODY
        for key in (("attendre",),("dormir",)):
            mind.effects.observe(key,(0.,-1.,-1.,0.,-1.))
        a=E.passive_readouts(mind,body,"attendre")
        b=E.passive_readouts(mind,body,"dormir")
        self.assertTrue(a["action_specific_history"])
        self.assertTrue(b["action_specific_history"])
        self.assertEqual(a["scalar_forecasts"]["action"],
                         b["scalar_forecasts"]["action"])
        self.assertEqual(a["scalar_forecasts"]["global"],
                         b["scalar_forecasts"]["global"])

    def test_frozen_selected_action_prevents_future_label_and_seal_forgery(self):
        mind=E._fixture()
        body=E.SYNTHETIC_BODY
        source=_source_seal(mind)
        mind.last=(body,("dormir",),"dormir",None)
        with self.assertRaises(PermissionError):
            E.SyntheticActionPrequentialTicket(
                mind=mind,capture_body=body,action="attendre",
                param=None,identity="wrong-action")
        with self.assertRaises(PermissionError):
            E.SyntheticActionPrequentialTicket(
                mind=mind,capture_body=(29.,30.,30.,35.,30.),
                action="dormir",param=None,identity="wrong-body")
        t=E.SyntheticActionPrequentialTicket(
            mind=mind,capture_body=body,action="dormir",param=None,
            identity="fixed-synthetic-outcome")
        self.assertEqual(_source_seal(mind),source if False else _source_seal(mind))
        sha=t.sha256
        with self.assertRaises(RuntimeError):
            t.settle_synthetic(
                sha256=sha,action="attendre",param=None,
                after_body=body,dead=())
        with self.assertRaises(TypeError):
            t.settle_synthetic(
                sha256=sha,action="dormir",param=None,
                after_body=body,dead=True)
        with self.assertRaises(ValueError):
            t.settle_synthetic(
                sha256=sha,action="dormir",param=None,
                after_body=(float("nan"),)*5,dead=())
        t.payload["frozen_readouts"]["scalar_forecasts"]["action"] = 999.
        with self.assertRaises(RuntimeError):
            t.settle_synthetic(
                sha256=sha,action="dormir",param=None,
                after_body=body,dead=())
        t2=E.SyntheticActionPrequentialTicket(
            mind=mind,capture_body=body,action="dormir",param=None,
            identity="terminal-synthetic-outcome")
        receipt=t2.settle_synthetic(
            sha256=t2.sha256,action="dormir",param=None,
            after_body=(30.,0.,0.,30.,30.),dead=("synthetic_terminal",))
        self.assertTrue(receipt["observed_terminal"])
        self.assertEqual(receipt["observed_synthetic_target"],-mind.d_max)
        self.assertGreater(receipt["squared_loss"]["action"],0.)
        with self.assertRaises(RuntimeError):
            t2.settle_synthetic(
                sha256=t2.sha256,action="dormir",param=None,
                after_body=body,dead=())

    def test_rejects_fabricated_buffer_action_labels_or_nonfinite_effects(self):
        mind=E._fixture()
        body=E.SYNTHETIC_BODY
        original=_source_seal(mind)
        with self.assertRaises(ValueError):
            E.passive_readouts(mind,body,"invented_action")
        with self.assertRaises(ValueError):
            E.passive_readouts(mind,(float("nan"),)*5,"attendre")
        self.assertEqual(_source_seal(mind),original)
        mind.buffer.append((1.,body,body,False,"attendre"))
        with self.assertRaises(PermissionError):
            E.passive_readouts(mind,body,"attendre")
        mind.buffer.pop()
        mind.effects.stats[("attendre",)][1][0]=float("nan")
        with self.assertRaises(ValueError):
            E.passive_readouts(mind,body,"attendre")

    def test_null_action_preselected_without_motor_params_only(self):
        mind=E._fixture()
        body=E.SYNTHETIC_BODY
        mind.last=None
        t=E.SyntheticActionPrequentialTicket(
            mind=mind,capture_body=body,action=None,param=None,
            identity="synthetic-inactivity")
        self.assertFalse(t.payload["frozen_readouts"]["action_specific_history"])
        r=t.settle_synthetic(
            sha256=t.sha256,action=None,param=None,
            after_body=body,dead=())
        self.assertEqual(r["status"],"SYNTHETIC_ONLY_SCORED")
        with self.assertRaises(PermissionError):
            E.SyntheticActionPrequentialTicket(
                mind=mind,capture_body=body,action=None,param="N",
                identity="invalid-inactivity")


if __name__=="__main__":
    unittest.main()
