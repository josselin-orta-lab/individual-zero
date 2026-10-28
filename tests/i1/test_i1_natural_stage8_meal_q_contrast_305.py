"""Exploratory selective Stage8 meal-Q ablation on unforced mortal M11 births."""
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate


class MealStage8Read305(unittest.TestCase):
    def test_paired_meal_stage8_read_at_steps_19_and_21(self):
        with TemporaryDirectory(prefix="i1-305-meal-ablation-") as home:
            generated = Path(home) / "generated"
            generate(generated)
            program = r"""
from contextlib import nullcontext
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from i1.modules.stage8_evaluator import Stage8OptionEvaluator
from i1.modules.td_values import LearnedValue, LinearTDValues
from i1lab.i1_birth import birth_i1_m11
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset, _birth_parameters

preset, digest = load_preset("oasis")
raw, initial_local = _birth_parameters(preset)
params = dict(raw, diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1)
IDENTITY = "i1:304:heldout:oasis:b"
SIGNATURE = "i1:affordance:manger:target=berry_a"
original_stage8 = Stage8OptionEvaluator.evaluate
original_read = LinearTDValues.learned_value

def life(mode, path):
    target_step = {"canonical": None, "mask19": 19, "mask21": 21}[mode]
    masked_reads, receipts, snapshots = [], [], []
    def stage8_wrapper(owner, **kw):
        if kw["t_monde"] != target_step or kw["proposal"].option.learning_signature != SIGNATURE:
            return original_stage8(owner, **kw)
        cursor = (kw["t_monde"], kw["cycle"], kw["proposal"].option.id)
        reads = [0]
        def blind_read(qowner, state, signature):
            reads[0] += 1
            actual = original_read(qowner, state, signature)
            assert signature == SIGNATURE
            if actual.status == "learned":
                masked_reads.append({
                    "step": cursor[0], "cycle": cursor[1],
                    "option_ref": cursor[2], "signature": signature,
                    "q": actual.value, "count": actual.update_count,
                })
                return LearnedValue(signature=signature, status="unlearned",
                                    value=None, evidence=None, update_count=0)
            return actual
        with patch.object(LinearTDValues, "learned_value", blind_read):
            result = original_stage8(owner, **kw)
        assert reads[0] == 1
        return result
    scope = (nullcontext() if target_step is None
             else patch.object(Stage8OptionEvaluator, "evaluate", stage8_wrapper))
    with scope:
        with birth_i1_m11(db_path=str(path), life_id=IDENTITY, **params) as actor:
            rt = actor._runtime
            born = {
                "physics": rt.world.config.digest(),
                "version": rt.world.config.version,
                "noise": rt.competition._config.noise_sigma,
                "td": rt.q_active.config.version,
                "needs": rt.value_needs.config.version,
            }
            assert "i1-living-physical-defaults-v4-metabolic-coupling" in born["version"]
            assert born["noise"] == 0
            for _ in range(24):
                before = {
                    "body": dict(rt.world.body.as_dict()),
                    "position": dict(rt.world.position.as_dict()),
                    "inventory": dict(rt.world.inventory()),
                    "q": rt.q_active.export_causal_state(),
                    "competition": rt.competition.export_causal_state(),
                    "goal": rt.goal_manager.export_causal_state(),
                    "fatigue": rt.sleep_health.fatigue,
                    "sleep_mode": rt.sleep_session.mode,
                    "head": rt.journal.head_hash,
                }
                receipt = actor.run_step()
                rt = actor._runtime
                assert receipt.journal_head == rt.journal.head_hash
                snapshots.append({
                    "step": receipt.world_step, "status": receipt.status,
                    "before": before, "after": {
                        "body": dict(rt.world.body.as_dict()),
                        "inventory": dict(rt.world.inventory()),
                    },
                    "head": receipt.journal_head,
                })
                receipts.append(receipt)
                if receipt.status == "dead":
                    break
            assert rt.journal.verify()
            events = [dict(e.causal_event) for e in rt.journal.entries_since(0)]
    audit = SQLiteLifeLedger.audit_read_only(path=str(path), expected_individual_id=IDENTITY)
    assert audit.generation == len(snapshots)
    assert audit.journal_head == snapshots[-1]["head"]
    assert audit.status == snapshots[-1]["status"] and not audit.pending_intent
    applied = {e["t_monde"]: {"primitive": e["primitive"], "parameters": e["parameters"]}
               for e in events if e.get("kind") == "command_experienced"}
    stage8 = {(e["t_monde"], e["cycle"], e["data"]["option_ref"]): {
        "signature": e["data"]["learning_signature"],
        "learned": e["data"]["learned_value_status"],
        "value": e["data"]["learned_value"],
        "evidence": e["data"]["evidence"], "status": e["data"]["status"],
    } for e in events if e.get("kind") == "stage8_option_evaluation"}
    for m in masked_reads:
        key = (m["step"], m["cycle"], m["option_ref"])
        assert key in stage8 and stage8[key]["signature"] == SIGNATURE
        assert stage8[key]["learned"] == "unlearned"
    competition = {(e["t_monde"], e["cycle"], t["option_ref"]): t
                   for e in events if e.get("kind") == "competition_cycle"
                   for t in e["data"]["traces"]}
    return {
        "born": born, "snapshots": snapshots, "applied": applied,
        "stage8": stage8, "competition": competition,
        "masked_reads": masked_reads, "events": events,
        "m11_verified": True, "status": audit.status,
    }

with TemporaryDirectory(prefix="i1-305-three-m11-") as home:
    canonical = life("canonical", Path(home) / "canonical.sqlite")
    arms = {name: life(name, Path(home) / (name + ".sqlite"))
            for name in ("mask19", "mask21")}
assert canonical["m11_verified"] and all(x["m11_verified"] for x in arms.values())

def report(name, arm, target):
    assert arm["born"] == canonical["born"]
    # Every physical/cognitive owner must be identical before intervention.
    for t in range(1, target):
        assert arm["snapshots"][t-1] == canonical["snapshots"][t-1], (
            "preintervention owner or journal mismatch", name, t)
    assert canonical["applied"][11]["primitive"] == "manger"
    assert all(canonical["applied"][t]["primitive"] == "dormir"
               for t in range(12, 18))
    assert canonical["applied"][18] == {
        "primitive": "collecter", "parameters": {"target": "berry_a"}}
    assert canonical["snapshots"][17]["after"]["inventory"]["berry_a"] == 1
    first_motor = next((t for t in range(target, 25)
                        if arm["applied"].get(t) != canonical["applied"].get(t)), None)
    different_stage8 = next((k for k in sorted(set(canonical["stage8"]) | set(arm["stage8"]))
                             if k[0] >= target and
                             canonical["stage8"].get(k) != arm["stage8"].get(k)), None)
    different_competition = next((k for k in sorted(
                                set(canonical["competition"]) | set(arm["competition"]))
                                if k[0] >= target and
                                canonical["competition"].get(k) != arm["competition"].get(k)), None)
    physical = [
        {"step": t, "canonical": canonical["snapshots"][t-1]["after"],
         "masked": arm["snapshots"][t-1]["after"]}
        for t in range(target, min(len(canonical["snapshots"]),
                                   len(arm["snapshots"])) + 1)]
    return {
        "mask_step": target, "masked_reads": arm["masked_reads"],
        "first_motor_difference": first_motor,
        "first_stage8_difference": different_stage8,
        "first_competition_difference": different_competition,
        "canonical_commands": [
            {"step": t, **cmd} for t, cmd in sorted(canonical["applied"].items())
            if t >= target],
        "masked_commands": [
            {"step": t, **cmd} for t, cmd in sorted(arm["applied"].items())
            if t >= target],
        "physical": physical, "canonical_status": canonical["status"],
        "masked_status": arm["status"],
        "verdict": (
            "NOT_EXPOSED" if not arm["masked_reads"] else
            "MATCHED_LOCAL_STAGE8_Q_MOTOR_EFFECT" if first_motor is not None
            else "EXPOSED_NO_APPLIED_DIVERGENCE"),
        "instrumental_credit": "NOT_ESTABLISHED",
        "durable_survival": "NOT_ESTABLISHED",
    }

out = {
    "source": "preregistered_exploratory_Stage8_only_meal_Q_read_M11",
    "same_birth_physics": True, "context_preintervention_matched": True,
    "windows": {name: report(name, arm, target)
                for name, arm, target in
                (("mask19", arms["mask19"], 19),
                 ("mask21", arms["mask21"], 21))},
    "adaptive_generalization": "NOT_ESTABLISHED",
}
print("I1_305_STAGE8_MEAL_Q_CONTRAST=" + json.dumps(out, sort_keys=True))
"""
            env = dict(os.environ,
                       PYTHONPATH=os.pathsep.join((str(generated), str(ROOT / "src"),
                                                   str(ROOT / "tools"))),
                       PYTHONDONTWRITEBYTECODE="1")
            proc = subprocess.run([sys.executable, "-B", "-c", program], cwd=ROOT,
                                  env=env, capture_output=True, text=True, timeout=480)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("I1_305_STAGE8_MEAL_Q_CONTRAST=", proc.stdout)
            print(proc.stdout, flush=True)


if __name__ == "__main__":
    unittest.main()
