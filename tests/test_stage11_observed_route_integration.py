"""Public opt-in Stage11 observed-route integration, not held-out evidence."""
from dataclasses import replace
from unittest import TestCase

from lab.stage11_junction_probe import ALLOWED_OPEN, BASE
from lab.stage11_geographic_probe import START_BODY, _positions
from lab.stage11_reference_fixture import build_stage11_reference_runtime
from lab.stage11_runtime import Stage11Runtime
from lab.world import Position


def run_route(*, planning_uc=None, open_branch=True):
    base = build_stage11_reference_runtime(enable_geography=True)
    cfg = replace(
        base._stage11_config,
        version="stage11-observed-route-integration-dev-v1",
        geographic_route_enabled=True,
        geographic=replace(
            base._stage11_config.geographic,
            version="p48-observed-route-integrated-v1",
            observe_routes=True,
        ),
    )
    if planning_uc is not None:
        stage9 = cfg.stage9
        stage8 = stage9.stage8
        stage7 = stage8.stage7
        stage6 = stage7.stage6
        stage4 = stage6.stage4
        budget = replace(
            stage4.compute_budget,
            version=stage4.compute_budget.version+f"+route-planning-{planning_uc}",
            module_envelopes={
                **stage4.compute_budget.module_envelopes,
                "planning": planning_uc,
            },
        )
        cfg = replace(cfg, stage9=replace(stage9, stage8=replace(
            stage8, stage7=replace(stage7, stage6=replace(
                stage6, stage4=replace(stage4, compute_budget=budget),
            )),
        ))))
    runtime = Stage11Runtime(
        world_config=replace(
            base.world.config, initial_body=START_BODY,
            initial_position=Position(2, 2),
        ),
        layout=replace(
            base.world._layout,
            obstacles=BASE | (
                frozenset() if open_branch
                else frozenset({Position(2, 3)})
            ),
            resources=(), water_sources=frozenset(), creatures=frozenset(),
            danger_zones=frozenset(), lethal_zones=frozenset(),
        ),
        safety_config=base.stage3.substrate.safety._config,
        safety_facts=base._canonical_safety._innate,
        protected_integrity_threshold=(
            base.stage3.control._config.protected_integrity_threshold
        ),
        config=cfg, equipment=base.equipment,
    )
    actions = [runtime.run_step() for _ in range(10)]
    return runtime, actions


class ObservedRouteIntegrationTests(TestCase):
    def test_route_is_optional_and_legacy_unchanged(self):
        base = build_stage11_reference_runtime(enable_geography=True)
        self.assertFalse(base._stage11_config.geographic_route_enabled)
        self.assertFalse(base.exploration.geographic.config.observe_routes)

    def test_open_branch_uses_only_really_observed_sites(self):
        owner, actions = run_route()
        self.assertTrue(owner.journal.verify())
        visited = _positions(owner)
        self.assertTrue(set(visited) <= ALLOWED_OPEN)
        self.assertEqual(
            {tuple(x[:2]) for x in owner.exploration.geographic.export_causal_state()["visits"]},
            set(visited),
        )
        events = [e.causal_event for e in owner.journal.entries]
        searches = [
            (i, e) for i, e in enumerate(events)
            if e.get("kind") == "stage11_route_search"
        ]
        for i, e in searches:
            self.assertFalse(e["data"]["oracle_access"])
            earlier = [
                x for x in events[:i]
                if x.get("kind") == "compute_charge"
                and x.get("t_monde") == e.get("t_monde")
                and x.get("cycle") == e.get("cycle")
                and x.get("data", {}).get("operation") == "geographic_route_search"
                and x["data"]["accepted"] is True
            ]
            self.assertTrue(earlier)
        self.assertTrue(any(e["data"]["route_found"] for _, e in searches))
        print("stage11_public_routed_junction=" + str({
            "positions": visited,
            "commands": [(a.command_primitive, a.option_ref) for a in actions],
            "journal_sha256": owner.journal.head_hash,
            "route_searches": len(searches),
        }))

    def test_budget_zero_never_offers_a_transit(self):
        owner, actions = run_route(planning_uc=0)
        self.assertTrue(owner.journal.verify())
        self.assertFalse(owner.exploration.geographic.transit_offered)
        self.assertFalse(any(
            a.option_ref is not None and "frontier_route" in a.option_ref
            and a.execution_status == "applied"
            for a in actions
        ))

    def test_opt_in_replay_is_exact(self):
        for open_branch in (True, False):
            with self.subTest(open_branch=open_branch):
                a, actions_a = run_route(open_branch=open_branch)
                b, actions_b = run_route(open_branch=open_branch)
                self.assertTrue(a.journal.verify())
                self.assertTrue(b.journal.verify())
                self.assertEqual(a.journal.canonical_bytes(),
                                 b.journal.canonical_bytes())
                self.assertEqual(a.exploration.export_causal_state(),
                                 b.exploration.export_causal_state())
                self.assertEqual(
                    [(x.command_primitive, x.option_ref) for x in actions_a],
                    [(x.command_primitive, x.option_ref) for x in actions_b],
                )
