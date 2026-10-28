"""Preregistered #438 research-only Stage8 Q-read contrast on two mortal M11 lives.

No policy/engine mutation, operator truth injection, scripted command, or
positive scientific GO assertion. See docs/EXPERIMENT_438_STAGE8_READ_2026-10-28.md.
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


class NaturalStage8ReadContrast438(unittest.TestCase):
    def test_matched_birth_first_q_read_and_applied_motor_difference(self):
        with TemporaryDirectory(prefix="i1-438-qread-") as home:
            generated = Path(home) / "generated"
            generate(generated)
            script = r"""
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

# All intervention and analysis decisions were specified in the checked-in
# preregistration BEFORE this experiment can be run in CI.
preset, digest = load_preset("dry-valley")
raw, initial_local = _birth_parameters(preset)
params = dict(raw, diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1)
IDENTITY = "i1:438:stage8-qread-paired-dry-valley"
LIMIT = 12
original_stage8 = Stage8OptionEvaluator.evaluate
original_read = LinearTDValues.learned_value


def life(mode, path):
    assert mode in ("canonical", "stage8_q_read_masked")
    masked_reads = []
    cursor = {}
    read_calls = [0]

    def blind_read(owner, state, signature):
        read_calls[0] += 1
        actual = original_read(owner, state, signature)
        if actual.status == "learned":
            assert actual.value is not None
            masked_reads.append({
                "step": cursor["step"], "cycle": cursor["cycle"],
                "option_ref": cursor["option_ref"],
                "signature": signature, "q": float(actual.value),
                "update_count": actual.update_count,
            })
        # Only the Stage8 readback is hidden, not the TD owner/write or
        # Planning's normal independently paid Q read.
        return LearnedValue(signature=signature, status="unlearned",
                            value=None, evidence=None, update_count=0)

    def blind_stage8(owner, **kw):
        cursor.update(step=kw["t_monde"], cycle=kw["cycle"],
                      option_ref=kw["proposal"].option.id)
        before_calls = read_calls[0]
        with patch.object(LinearTDValues, "learned_value", blind_read):
            result = original_stage8(owner, **kw)
        assert read_calls[0] == before_calls + 1, (
            "Stage8 must make exactly its single normal Q read")
        return result

    scope = (patch.object(Stage8OptionEvaluator, "evaluate", blind_stage8)
             if mode == "stage8_q_read_masked" else nullcontext())
    snapshots, receipts = [], []
    with scope:
        with birth_i1_m11(db_path=str(path), life_id=IDENTITY, **params) as actor:
            rt = actor._runtime
            local_at_birth = rt.world.capture_local(t_monde=1).as_dict()
            physics_digest = rt.world.config.digest()
            physics_version = rt.world.config.version
            assert "i1-living-physical-defaults-v4-metabolic-coupling" in (
                physics_version), physics_version
            born_noise = rt.competition._config.noise_sigma
            td_config = rt.q_active.config
            for _ in range(LIMIT):
                rt = actor._runtime
                before = {
                    "body": dict(rt.world.body.as_dict()),
                    "position": dict(rt.world.position.as_dict()),
                    "inventory": dict(rt.world.inventory()),
                    "q": rt.q_active.export_causal_state(),
                    "competition": rt.competition.export_causal_state(),
                    "goal": rt.goal_manager.export_causal_state(),
                }
                receipt = actor.run_step()  # Sole physical action authority.
                assert receipt.status in ("active", "dead"), receipt
                rt = actor._runtime
                assert receipt.journal_head == rt.journal.head_hash
                snapshots.append({
                    "step": receipt.world_step, "before": before,
                    "after": {
                        "body": dict(rt.world.body.as_dict()),
                        "position": dict(rt.world.position.as_dict()),
                        "inventory": dict(rt.world.inventory()),
                    },
                    "status": receipt.status,
                })
                receipts.append({
                    "generation": receipt.generation,
                    "head": receipt.journal_head,
                    "status": receipt.status,
                })
                if receipt.status == "dead":
                    break
            assert snapshots and rt.journal.verify()
            events = [dict(e.causal_event) for e in rt.journal.entries_since(0)]
            head = rt.journal.head_hash
    audit = SQLiteLifeLedger.audit_read_only(
        path=str(path), expected_individual_id=IDENTITY)
    assert audit.generation == len(receipts)
    assert audit.journal_head == head == receipts[-1]["head"]
    assert audit.status == receipts[-1]["status"] and not audit.pending_intent

    applied, admitted, stage8, competition, p40, td, charges = {}, {}, {}, {}, {}, [], {}
    for event in events:
        kind, step = event.get("kind"), event["t_monde"]
        data = event.get("data", {})
        if kind == "command_experienced":
            assert step not in applied
            applied[step] = {
                "primitive": event["primitive"],
                "parameters": dict(event["parameters"]),
            }
        elif kind == "command_admitted":
            assert step not in admitted
            admitted[step] = {
                "primitive": data["primitive"],
                "option_ref": data.get("option_ref"),
                "source": data.get("source"),
            }
        elif kind == "stage8_option_evaluation":
            key = (step, event["cycle"], data["option_ref"])
            assert key not in stage8
            stage8[key] = {
                "learned": data["learned_value_status"],
                "q": data["learned_value"],
                "status": data["status"],
                "evidence": data["evidence"],
                "signature": data["learning_signature"],
            }
        elif kind == "competition_cycle":
            for trace in data["traces"]:
                key = (step, event["cycle"], trace["option_ref"])
                assert key not in competition
                competition[key] = {
                    "evidence": trace["evidence"],
                    "ratio": trace["accumulator_after"] / trace["threshold"],
                    "crossed": bool(trace["crossed"]),
                }
        elif kind == "stage10_sleep_pressure_frozen":
            assert step not in p40
            p40[step] = float(data["sleep_pressure"])
        elif kind == "td_update_published":
            td.append((step, data["previous_signature"],
                       tuple(data["updated_signatures"])))
        elif kind == "compute_charge":
            charges.setdefault(step, []).append(
                (data.get("module"), data.get("operation"),
                 data.get("requested_uc"), data.get("accepted")))
    assert len(applied) == len(admitted) == len(snapshots)
    assert set(applied) == set(admitted) == {s["step"] for s in snapshots}
    assert all(applied[k]["primitive"] == admitted[k]["primitive"]
               for k in applied)
    assert all(x["generation"] == n + 1 for n, x in enumerate(receipts))
    return {
        "mode": mode, "initial_local": local_at_birth,
        "preset_digest": digest, "physics_digest": physics_digest,
        "physics_version": physics_version, "born_noise": born_noise,
        "td_config": (td_config.version, td_config.beta, td_config.eta,
                      td_config.lambda_e),
        "snapshots": snapshots, "applied": applied, "admitted": admitted,
        "stage8": stage8, "competition": competition, "p40": p40, "td": td,
        "charges": charges, "masked_reads": masked_reads,
        "m11_generation": audit.generation, "m11_status": audit.status,
        "head_verified": True,
    }


with TemporaryDirectory(prefix="i1-438-matched-m11-") as home:
    canonical = life("canonical", Path(home) / "canonical.sqlite")
    masked = life("stage8_q_read_masked", Path(home) / "masked.sqlite")

assert canonical["initial_local"] == masked["initial_local"] == initial_local
assert canonical["preset_digest"] == masked["preset_digest"]
assert canonical["physics_digest"] == masked["physics_digest"]
assert canonical["physics_version"] == masked["physics_version"]
assert canonical["born_noise"] == masked["born_noise"]
assert canonical["td_config"] == masked["td_config"]
assert not canonical["masked_reads"]
assert canonical["head_verified"] and masked["head_verified"]
assert canonical["snapshots"][0]["before"] == masked["snapshots"][0]["before"]
assert canonical["born_noise"] == 0, (
    "random Competition noise requires a different causal protocol")

common = sorted(set(canonical["applied"]) & set(masked["applied"]))
assert common and common == list(range(1, max(common) + 1))
first_physical = next(
    (step for step in common if
     canonical["applied"][step] != masked["applied"][step]), None)
if first_physical is None:
    # A different death/censor without different applied commands cannot be
    # interpreted as a Q-only motor action.
    assert (len(canonical["applied"]) == len(masked["applied"]) and
            canonical["m11_status"] == masked["m11_status"])

changed_q_reads = []
for key in sorted(set(canonical["stage8"]) & set(masked["stage8"])):
    a, b = canonical["stage8"][key], masked["stage8"][key]
    if a["learned"] == "learned" and b["learned"] == "unlearned":
        assert a["q"] is not None and b["q"] is None
        assert a["signature"] == b["signature"]
        changed_q_reads.append(key)
        # A learned Stage8 read must be traceable to genuine Competition
        # evidence, never just a detached operator-side computation.
        if a["status"] == "evaluated":
            assert key in canonical["competition"]
            assert abs(canonical["competition"][key]["evidence"] -
                       a["evidence"]) < 1e-10
assert all(
    (x["step"], x["cycle"], x["option_ref"]) in masked["stage8"]
    for x in masked["masked_reads"]
)
first_q_suppression_step = min(
    (r["step"] for r in masked["masked_reads"]), default=None)
if first_physical is not None:
    assert first_q_suppression_step is not None
    assert first_q_suppression_step <= first_physical, (
        "physical divergence preceded any genuine learned Stage8 suppression")

precondition = None
if first_physical is not None:
    a = canonical["snapshots"][first_physical - 1]["before"]
    b = masked["snapshots"][first_physical - 1]["before"]
    precondition = {
        "same_body": a["body"] == b["body"],
        "same_position": a["position"] == b["position"],
        "same_inventory": a["inventory"] == b["inventory"],
        "same_td": a["q"] == b["q"],
        "same_competition": a["competition"] == b["competition"],
        "same_active_goal": a["goal"] == b["goal"],
        "same_frozen_p40": (
            canonical["p40"].get(first_physical) ==
            masked["p40"].get(first_physical)),
        "same_charge_chronology_before": all(
            canonical["charges"].get(t) == masked["charges"].get(t)
            for t in range(1, first_q_suppression_step)),
        "learned_stage8_read_before_or_at_first_difference": any(
            k[0] <= first_physical for k in changed_q_reads),
        "real_admission_and_command_both_arms": (
            first_physical in canonical["admitted"]
            and first_physical in masked["admitted"]
            and first_physical in canonical["applied"]
            and first_physical in masked["applied"]),
    }
    assert all(precondition[k] for k in (
        "same_body", "same_position", "same_inventory")), (
        "world trajectories diverged before recorded first physical command")

eligible = bool(first_physical is not None and precondition is not None
                and all(precondition.values()))
if first_q_suppression_step is None:
    verdict = "NOT_EXPOSED"
elif eligible:
    verdict = "L3_SINGLE_MATCHED_STAGE8_READ_MOTOR_EFFECT"
elif first_physical is not None:
    verdict = "SCIENTIFICALLY_INCONCLUSIVE_CONTEXT_NOT_FULLY_MATCHED"
else:
    verdict = "L3_NOT_ESTABLISHED_NO_APPLIED_DIFFERENCE"

summary = {
    "source": "independent-M11-paired-natural-actions-research-ablation",
    "preregistered": True,
    "canonical_engine_unchanged": True,
    "research_variant": "stage8-only-q-read-masked-before-birth",
    "physical_world_and_physics_identical": True,
    "birth_identity_same_in_separate_ledgers": True,
    "first_q_suppression_step": first_q_suppression_step,
    "masked_genuine_learned_stage8_reads": len(masked["masked_reads"]),
    "matched_stage8_option_cycles_with_learned_read_removed": len(changed_q_reads),
    "same_commands_before_first_divergence": all(
        canonical["applied"][t] == masked["applied"][t]
        for t in common if first_physical is None or t < first_physical),
    "first_physically_different_command_step": first_physical,
    "preaction_first_difference_checks": precondition,
    "canonical_first_action": (
        canonical["applied"].get(first_physical)
        if first_physical is not None else None),
    "masked_first_action": (
        masked["applied"].get(first_physical)
        if first_physical is not None else None),
    "canonical_m11": {
        "steps": len(canonical["applied"]),
        "status": canonical["m11_status"],
        "td_updates": len(canonical["td"]),
        "paid_competition_evaluations": len(canonical["competition"]),
    },
    "masked_m11": {
        "steps": len(masked["applied"]),
        "status": masked["m11_status"],
        "td_updates": len(masked["td"]),
        "paid_competition_evaluations": len(masked["competition"]),
    },
    "scientific_motor_verdict": verdict,
    "adaptive_benefit": "NOT_ESTABLISHED",
    "durability_and_generalization": "NOT_ESTABLISHED",
    "no_result_forced": True,
}
print("I1_438_MATCHED_STAGE8_Q_READ_CONTRAST=" +
      json.dumps(summary, sort_keys=True))
"""
            env = dict(os.environ,
                       PYTHONPATH=os.pathsep.join((
                           str(generated), str(ROOT / "src"),
                           str(ROOT / "tools"))),
                       PYTHONDONTWRITEBYTECODE="1")
            proc = subprocess.run(
                [sys.executable, "-B", "-c", script], cwd=ROOT, env=env,
                text=True, capture_output=True, timeout=480)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            self.assertIn("I1_438_MATCHED_STAGE8_Q_READ_CONTRAST=", proc.stdout)
            print(proc.stdout, flush=True)


if __name__ == "__main__":
    unittest.main()
