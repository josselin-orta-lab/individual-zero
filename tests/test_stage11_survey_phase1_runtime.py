"""Phase-1 ownership of optional physically accessible routing surveys."""
from dataclasses import replace
from unittest import TestCase

from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage11_runtime import Stage11Runtime


def instance(*, surveys: bool, exploration_uc=4):
    base = build_stage11_reference_runtime(enable_geography=True)
    geo = replace(
        base._stage11_config.geographic,
        version="p48-observed-survey-phase1-test-v1",
        observe_routes=surveys,
    )
    config = replace(
        base._stage11_config,
        version="stage11-survey-phase1-test-v1",
        geographic=geo,
        exploration_envelope_uc=exploration_uc,
    )
    return Stage11Runtime(
        world_config=base.world.config,
        layout=base.world._layout,
        safety_config=base.stage3.substrate.safety._config,
        safety_facts=base._canonical_safety._innate,
        protected_integrity_threshold=(
            base.stage3.control._config.protected_integrity_threshold
        ),
        config=config, equipment=base.equipment,
    )


class ObservedSurveyRuntimeTests(TestCase):
    def test_only_paid_exploration_may_record_current_physical_survey(self):
        rt = instance(surveys=True)
        rt.run_step()
        events = [e.causal_event for e in rt.journal.entries]
        recorded = [
            (i, e) for i, e in enumerate(events)
            if e.get("kind") == "stage11_route_survey_recorded"
        ]
        self.assertTrue(recorded)
        for index, row in recorded:
            prior = [
                e for e in events[:index]
                if e.get("kind") == "compute_charge"
                and e.get("t_monde") == row["t_monde"]
                and e.get("data", {}).get("module") == "exploration"
                and e.get("data", {}).get("operation") == "exploration_observe"
                and e["data"].get("accepted") is True
            ]
            self.assertTrue(prior)
            self.assertFalse(row["data"]["hidden_safety_claim"])
        self.assertTrue(rt.journal.verify())
        self.assertTrue(rt.exploration.geographic.surveys)

    def test_zero_exploration_uc_does_not_create_surveys(self):
        rt = instance(surveys=True, exploration_uc=0)
        rt.run_step()
        self.assertEqual(rt.exploration.geographic.surveys, ())
        self.assertFalse(any(
            e.causal_event.get("kind") == "stage11_route_survey_recorded"
            for e in rt.journal.entries
        ))
        self.assertTrue(rt.journal.verify())

    def test_disabled_surveys_do_not_modify_legacy_geo_schema(self):
        rt = instance(surveys=False)
        rt.run_step()
        self.assertEqual(
            rt.exploration.geographic.export_causal_state()["schema"],
            "geographic-exploration-v1",
        )
        self.assertFalse(any(
            e.causal_event.get("kind") == "stage11_route_survey_recorded"
            for e in rt.journal.entries
        ))
