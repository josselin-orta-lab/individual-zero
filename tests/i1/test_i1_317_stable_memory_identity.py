"""#317: repeat observations retain only the SAME personally grounded hop.

Generated-I1 software test; it is not a behavioural or scientific campaign.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class StableSpatialMemoryIdentityTests(unittest.TestCase):
    def test_generated_i1_reuses_only_same_grounded_intention(self):
        with TemporaryDirectory(prefix="i1-stable-memory-") as folder:
            generated = Path(folder) / "generated"
            generate(generated)
            script = r"""
from types import SimpleNamespace
from i1.modules.competition import Competition, CompetitionConfig
from i1.modules.geographic_exploration import GeographicExploration, GeographicExplorationConfig
from i1.modules.geographic_planning import propose_spatial_return
from i1.modules.spatial_memory import SpatialReturnTarget

GOAL = "goal:physiological"
def create(t, *, via=(1, 0), entity="unknown_object", at_t=None):
    entity_id = "sighting:" + entity + ":0:0"
    target = SpatialReturnTarget(
        ref=f"place:{entity_id}:at:0:0:from:1:1:via:{via[0]}:{via[1]}",
        source_t_monde=t, origin=(1, 1), destination=via,
        direction="north" if via == (1, 0) else "west",
        entity_id=entity_id, entity_type=entity,
        observed_position=(0, 0), visited_path=((1, 1), via, (0, 0)),
        observed_step=1, confidence=0.65)
    target.validate()
    local = SimpleNamespace(
        x=1, y=1, validate=lambda: None,
        adjacent=(SimpleNamespace(
            direction=target.direction, passable=True, creature=False,
            x=via[0], y=via[1]),))
    simulator = SimpleNamespace(rollout=lambda **kw: SimpleNamespace(
        complete=False, reason="equipment_input_unseen"))
    proposal = propose_spatial_return(
        target=target, initial_state=local, simulator=simulator,
        st_version="perception-context", t_monde=t if at_t is None else at_t,
        ttl_steps=20, goal_ref=GOAL)
    return target, proposal

first_target, first = create(10)
recent_target, recent = create(11)
assert first is not None and recent is not None
assert first.option.id == recent.option.id
assert first.option.plan_ref == recent.option.plan_ref
assert first.option.expires_at_step != recent.option.expires_at_step
assert first.option.goal_ref == GOAL and recent.option.goal_ref == GOAL
assert first.option.id == "option:place-memory:" + first_target.ref
assert first.option.founding_st_version == recent.option.founding_st_version
# A different perceived first hop or personal entity-place is a new option.
assert create(11, via=(0, 1))[1].option.id != first.option.id
assert create(11, entity="other")[1].option.id != first.option.id
# Reusing yesterday's target with today's world clock is not admissible.
assert create(10, at_t=11)[1] is None

geo = GeographicExploration(GeographicExplorationConfig(
    version="unit", novelty_weight=0.15, max_distinct_sites=16,
    max_targets_per_cycle=1, observe_routes=True, remember_entities=True))
# Only the current, frozen Perception-approved target can be resolved.
geo._place_offered = (recent_target,)
assert geo.place_for(first.option) == recent_target
geo._place_offered = ()
assert geo.place_for(recent.option) is None

competition = Competition(CompetitionConfig(
    version="unit", c_max=5, urgency_max=2.0, urgency_scale_cycles=2.0,
    leak=0.0, noise_sigma=0.0, gain=1.0, base_threshold=0.5,
    threshold_floor=0.1, inertia=0.1, residual=0.5, options_max=8,
    substitution_evidence={}))
assert competition.register(first, active_goal_id=GOAL, t_monde=10)
competition._registry[first.option.id].accumulator = 0.23
competition.open_deliberation(active_goal_id=GOAL, t_monde=11)
assert competition.register(recent, active_goal_id=GOAL, t_monde=11)
assert competition.accumulator_for(first.option.id) == 0.23
assert competition.register(create(11, via=(0, 1))[1],
                            active_goal_id=GOAL, t_monde=11)
assert competition.accumulator_for(create(11, via=(0, 1))[1].option.id) == 0.0
# Goal mismatch still invalidates: stable identity is not permanent permission.
competition.open_deliberation(active_goal_id="goal:changed", t_monde=12)
assert competition.proposal_for(first.option.id) is None
print("I1_MEMORY_STABLE_IDENTITY_SOFTWARE_OK")
"""
            r = subprocess.run(
                [sys.executable, "-c", script], cwd=ROOT,
                env={"PYTHONPATH": str(generated) + ":" + str(ROOT / "src")},
                text=True, capture_output=True, check=False)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            self.assertIn("I1_MEMORY_STABLE_IDENTITY_SOFTWARE_OK", r.stdout)


if __name__ == "__main__":
    unittest.main()
