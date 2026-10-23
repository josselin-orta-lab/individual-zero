"""Generated I1 contract: ordered Competition veto, next candidate, fallback.

These are explicitly synthetic software contract fixtures, NOT natural-birth
scientific evidence. No new reward, learned Q, policy, UC exemption, action,
or effect is supplied to an actual M11 life. I0 is never modified.
"""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class RankedActionControlContract(unittest.TestCase):
    def test_generated_I1_control_hook_uses_paid_ranked_veto_and_fallback(self):
        with TemporaryDirectory(prefix="i1-438-ranked-control-") as folder:
            built = Path(folder) / "generated"
            generate(built)
            script = r"""
from dataclasses import replace

from i1.contracts import OptionProposal
from i1.interfaces import PrimitiveCommand
from i1.modules.action_control import StaticSafetyFacts
from i1.modules.competition import Competition
from i1lab.scheduler import CyclePhase
from i1lab.stage4_reference_fixture import build_stage4_reference_runtime
from i1lab.stage4_runtime import Stage4Runtime

# The fixture's immutable known-toxic facts are solely negative-test inputs,
# NEVER knowledge injected into a naturally born individual.
base = build_stage4_reference_runtime()
assert base._config.competition.noise_sigma == 0.0

def exercised_case(*, second, c_max):
    comp_cfg = replace(
        base._config.competition,
        version="438-control-veto-contract",
        c_max=c_max,
        substitution_evidence={
            "manger": 1.0,
            "dormir": 0.75,
            "attendre": 0.0,
        },
    )
    actor = Stage4Runtime(
        world_config=base.world.config,
        layout=base.world._layout,
        safety_config=base.stage3.substrate.safety._config,
        safety_facts=StaticSafetyFacts(
            known_toxic_resources=frozenset({"berry_a", "berry_b"})),
        protected_integrity_threshold=(
            base.stage3.control._config.protected_integrity_threshold),
        config=replace(base._config, competition=comp_cfg),
    )
    capture = actor.stage3.open_step()
    step = capture.t_monde
    assert step == 1
    assert actor.scheduler.active_attempt is not None
    actor.competition.ensure_wait(t_monde=step, st_version="438:fixture")
    wait = actor.competition.fallback()
    assert wait.plan is not None

    def proposal(name, primitive, target=None):
        option_id = "contract:438:" + name
        opt = replace(
            wait.option, id=option_id,
            plan_ref="plan:" + option_id,
            learning_signature="contract:438:" + name,
            provenance="test_only_contract", expires_at_step=step + 3)
        command = PrimitiveCommand(
            primitive, {} if target is None else {"target": target})
        one_step = replace(wait.plan.steps[0], command=command)
        plan = replace(
            wait.plan, id="plan:" + option_id,
            option_ref=option_id, steps=(one_step,))
        made = OptionProposal(opt, plan)
        made.validate()
        assert actor.competition.register(
            made, active_goal_id=None, t_monde=step)
        return made

    first = proposal("top_toxic", "manger", "berry_b")
    contender = None
    if second == "safe":
        contender = proposal("second_sleep", "dormir")
    elif second == "toxic":
        contender = proposal("second_toxic", "manger", "berry_a")
    assert second in {"safe", "toxic", "absent"}

    actor.competition.open_deliberation(
        active_goal_id=None, t_monde=step)
    # This evaluates the genuine generated Competition implementation.
    # Fixture scores are not learned and have no scientific interpretation.
    result = actor.competition.evaluate(cycle=1, t_monde=step)
    ranked = [proposal.option.id for proposal in result.crossed_ranked]
    assert first.option.id in ranked
    if contender is None:
        assert ranked == [first.option.id]
    elif second == "safe":
        assert ranked == [first.option.id, contender.option.id], ranked
    else:
        assert set(ranked) == {first.option.id, contender.option.id}
    assert all(
        next(t for t in result.traces if t.option_ref == ref).crossed
        for ref in ranked)

    before = actor.competition.export_causal_state()
    cold = Competition(comp_cfg)
    cold.restore_causal_state(before)
    assert cold.export_causal_state() == before
    # The owner cannot silently promote a different/stale semantic option.
    wrong = OptionProposal(
        replace(first.option, id="contract:438:foreign"), first.plan)
    snapshot = cold.export_causal_state()
    try:
        cold.close_deliberation(wrong)
    except ValueError:
        pass
    else:
        raise AssertionError("foreign winner gained control")
    assert cold.export_causal_state() == snapshot

    # Pay the real Action Control UC charges. No charge method is patched.
    actor.compute_budget.open_cycle(
        1, occurrence=(step, actor.scheduler.active_attempt.attempt_ref, 1))
    actor._cycle_result = result
    body_before = actor.world.body.as_dict()
    hooks = actor._phase_hooks(
        cycle=1, capture=capture,
        goal_for_planning=None, st_before_cycle=None)
    hooks[CyclePhase.ACCUMULATION_DECISION]["action_control"](None)
    admission = actor._admitted_decision
    assert admission is not None
    assert actor.world.body.as_dict() == body_before
    assert actor.scheduler.t_monde == step
    assert not actor._safety_block_after_cycle

    traced = [
        dict(entry.causal_event)
        for entry in actor.journal.entries
        if entry.causal_event["kind"] in (
            "command_admitted", "command_vetoed", "command_experienced")
    ]
    attempted = [entry for entry in traced
                 if entry["kind"] in ("command_admitted", "command_vetoed")]
    assert traced == attempted, "test setup dispatched an unadmitted action"
    assert actor.journal.verify()
    assert len(attempted) == actor.compute_budget.consumed_module_uc(
        "action_control")
    assert all(entry["data"]["source"] == "decision" for entry in attempted)
    assert attempted[-1]["kind"] == "command_admitted"
    assert all(entry["kind"] == "command_vetoed" for entry in attempted[:-1])
    assert all(entry["data"]["reason"] == "known_toxic_item"
               and entry["data"]["scope"] == "option"
               for entry in attempted[:-1])

    actual, prepared, permit = admission
    assert permit.ok and prepared.option_ref == actual.option.id
    assert permit.command == prepared.command
    assert first.option.id not in {
        p.option.id for p in actor.competition.candidate_proposals}

    if second == "safe":
        assert [entry["data"]["option_ref"] for entry in attempted] == [
            first.option.id, contender.option.id]
        assert actual.option.id == contender.option.id
        assert prepared.command.primitive == "dormir"
        assert not actor._fallback_used_this_cycle
        assert actor.compute_budget.consumed_module_uc("action_control") == 2
        # Only an admitted ranked candidate may become an engaged winner.
        actor.competition.close_deliberation(actual, adjudicated=True)
        assert actor.competition.engaged_option_id == contender.option.id
    else:
        expected_vetoes = 1 if contender is None else 2
        assert len(attempted) == expected_vetoes + 1
        assert actor._fallback_used_this_cycle and c_max == 1
        assert actual.option.id == wait.option.id
        assert prepared.command.primitive == "attendre"
        assert attempted[-1]["data"]["option_ref"] == wait.option.id
        assert actor.compute_budget.consumed_module_uc(
            "action_control") == expected_vetoes + 1
        # A fallback is not a Competition victory and must not erase proof.
        not_engaged = actor.competition.export_causal_state()
        actor.competition.close_deliberation(actual, adjudicated=False)
        assert actor.competition.export_causal_state() == not_engaged
        assert actor.competition.engaged_option_id is None

    # Cold owner snapshot remains identical after veto/invalidation and
    # after the actual (nonphysical) arbitration decision of the fixture.
    verified = actor.competition.export_causal_state()
    restarted = Competition(comp_cfg)
    restarted.restore_causal_state(verified)
    assert restarted.export_causal_state() == verified
    return len(attempted), actual.option.id

two = exercised_case(second="safe", c_max=5)
one = exercised_case(second="absent", c_max=1)
all_vetoed = exercised_case(second="toxic", c_max=1)
assert (two[0], one[0], all_vetoed[0]) == (2, 2, 3)
print("I1_438_RANKED_VETO_ACTUAL_CONTROL_HOOK_OK")
print("I1_438_TEST_ONLY_NOT_NATURAL_MOTOR_LEARNING")
"""
            env = dict(
                os.environ,
                PYTHONPATH=os.pathsep.join((str(built), str(ROOT / "src"))),
                PYTHONDONTWRITEBYTECODE="1",
            )
            outcome = subprocess.run(
                [sys.executable, "-B", "-c", script],
                cwd=ROOT, env=env, text=True,
                capture_output=True, check=False,
            )
            self.assertEqual(
                outcome.returncode, 0, outcome.stdout + outcome.stderr)
            self.assertIn(
                "I1_438_RANKED_VETO_ACTUAL_CONTROL_HOOK_OK", outcome.stdout)


if __name__ == "__main__":
    unittest.main()
