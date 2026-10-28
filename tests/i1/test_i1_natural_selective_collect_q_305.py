"""Preregistered one-signature step-18 Stage8 Q-read contrast (#305).

Research-only paired mortal M11 lives, no canonical motor changes. See
src/i1/docs/EXPERIMENT_305_SELECTIVE_COLLECT_Q_2026-10-28.md.
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


class NaturalSelectiveCollectQ305(unittest.TestCase):
    def test_step18_collect_read_contrast(self):
        with TemporaryDirectory(prefix="i1-304-heldout-qread-") as home:
            generated = Path(home) / "generated"
            generate(generated)
            script = r"""
from contextlib import nullcontext
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from i1.modules.stage11_evaluator import Stage11OptionEvaluator
from i1.modules.td_values import LearnedValue, LinearTDValues
from i1lab.i1_birth import birth_i1_m11
from i1lab.sqlite_life_store import SQLiteLifeLedger
from run_i1_world_preset import load_preset, _birth_parameters

# All intervention and analysis decisions were specified in the checked-in
# preregistration BEFORE this experiment can be run in CI.
preset_name = __import__("os").environ["I1_HELDOUT_PRESET"]
identity_suffix = __import__("os").environ["I1_HELDOUT_IDENTITY"]
preset, digest = load_preset(preset_name)
raw, initial_local = _birth_parameters(preset)
params = dict(raw, diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1)
IDENTITY = "i1:304:heldout:" + preset_name + ":" + identity_suffix
LIMIT = 18
original_stage8 = Stage11OptionEvaluator.evaluate
original_read = LinearTDValues.learned_value


def life(mode, path):
    assert mode in ("canonical", "stage8_q_read_masked")
    masked_reads = []
    read_attempts = []
    stage8_calls = []
    cursor = {}
    read_calls = [0]

    def blind_read(owner, state, signature):
        read_calls[0] += 1
        actual = original_read(owner, state, signature)
        if cursor["step"] >= 17:
            read_attempts.append({
                "step": cursor["step"], "cycle": cursor["cycle"],
                "signature": signature, "status": actual.status,
                "option_ref": cursor["option_ref"],
                "value": actual.value,
                "will_mask": (cursor["step"] == 18 and
                              signature == "i1:affordance:collecter:target=berry_a"),
            })
        if (cursor["step"] == 18 and
            signature == "i1:affordance:collecter:target=berry_a" and
            actual.status == "learned"):
            assert actual.value is not None
            masked_reads.append({
                "step": cursor["step"], "cycle": cursor["cycle"],
                "option_ref": cursor["option_ref"],
                "signature": signature, "q": float(actual.value),
                "update_count": actual.update_count,
            })
        if cursor["step"] != 18 or signature != "i1:affordance:collecter:target=berry_a":
            return actual
        # Only the Stage8 readback is hidden, not the TD owner/write or
        # Planning's normal independently paid Q read.
        return LearnedValue(signature=signature, status="unlearned",
                            value=None, evidence=None, update_count=0)

    def blind_stage8(owner, **kw):
        cursor.update(step=kw["t_monde"], cycle=kw["cycle"],
                      option_ref=kw["proposal"].option.id)
        if cursor["step"] >= 17:
            stage8_calls.append(dict(cursor))
        before_calls = read_calls[0]
        with patch.object(LinearTDValues, "learned_value", blind_read):
            result = original_stage8(owner, **kw)
        assert read_calls[0] == before_calls + 1, (
            "Stage8 must make exactly its single normal Q read")
        return result

    scope = (patch.object(Stage11OptionEvaluator, "evaluate", blind_stage8)
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
            born_needs = rt.value_needs.config
            for _ in range(LIMIT):
                rt = actor._runtime
                before = {
                    "body": dict(rt.world.body.as_dict()),
                    "position": dict(rt.world.position.as_dict()),
                    "inventory": dict(rt.world.inventory()),
                    "q": rt.q_active.export_causal_state(),
                    "competition": rt.competition.export_causal_state(),
                    "goal": rt.goal_manager.export_causal_state(),
                    "fatigue": float(rt.sleep_health.fatigue),
                    "sleep_mode": str(rt.sleep_session.mode),
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
                        "fatigue": float(rt.sleep_health.fatigue),
                        "sleep_mode": str(rt.sleep_session.mode),
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
        "born_need_weights": dict(born_needs.weights),
        "born_need_setpoints": dict(born_needs.setpoints),
        "snapshots": snapshots, "applied": applied, "admitted": admitted,
        "stage8": stage8, "competition": competition, "p40": p40, "td": td,
        "charges": charges, "masked_reads": masked_reads,
        "read_attempts": read_attempts, "stage8_calls": stage8_calls,
        "events": events,
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
assert canonical["born_need_weights"] == masked["born_need_weights"]
assert canonical["born_need_setpoints"] == masked["born_need_setpoints"]
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
        "same_fatigue": a["fatigue"] == b["fatigue"],
        "same_sleep_mode": a["sleep_mode"] == b["sleep_mode"],
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


# Pure observer arithmetic over already committed M11 bodily snapshots.
immediate = None
if first_physical is not None:
    ca = canonical["snapshots"][first_physical - 1]
    ab = masked["snapshots"][first_physical - 1]
    assert ca["before"]["body"] == ab["before"]["body"]
    channels = ("energy", "food", "water", "integrity")
    weights = canonical["born_need_weights"]
    setpoints = canonical["born_need_setpoints"]
    def distance(body):
        return sum(weights[k] * abs(float(body[k]) - setpoints[k])
                   for k in channels)
    pre, post_c, post_m = (ca["before"]["body"],
                            ca["after"]["body"], ab["after"]["body"])
    dc, dm = distance(post_c), distance(post_m)
    gap = dm - dc
    immediate = {
        "step": first_physical,
        "born_need_weights": weights, "born_need_setpoints": setpoints,
        "before": pre, "canonical_after": post_c, "masked_after": post_m,
        "canonical_change": {k: post_c[k] - pre[k] for k in channels},
        "masked_change": {k: post_m[k] - pre[k] for k in channels},
        "canonical_minus_masked": {k: post_c[k] - post_m[k] for k in channels},
        "distance_before": distance(pre),
        "distance_canonical_after": dc, "distance_masked_after": dm,
        "improvement_canonical": distance(pre) - dc,
        "improvement_masked": distance(pre) - dm,
        "distance_advantage_canonical": gap,
        "fatigue_before": ca["before"]["fatigue"],
        "fatigue_canonical_after": ca["after"]["fatigue"],
        "fatigue_masked_after": ab["after"]["fatigue"],
        "sleep_mode_before": ca["before"]["sleep_mode"],
        "sleep_mode_canonical_after": ca["after"]["sleep_mode"],
        "sleep_mode_masked_after": ab["after"]["sleep_mode"],
        "verdict": ("IMMEDIATE_HOMEOSTASIS_CANONICAL_BETTER"
                    if gap > 1e-12 else
                    "IMMEDIATE_HOMEOSTASIS_MASKED_BETTER"
                    if gap < -1e-12 else "IMMEDIATE_HOMEOSTASIS_TIED"),
    }
else:
    assert all(canonical["snapshots"][t-1]["after"]["body"] ==
               masked["snapshots"][t-1]["after"]["body"] for t in common)


# Manipulation fidelity is a technical validity gate, not a requirement that
# the intervention change an autonomous decision. A canonical learned read
# at step 18 must be exposed in the paired arm by our prebirth wrapper.
TARGET_Q = "i1:affordance:collecter:target=berry_a"
canonical_target_reads = [
    (k, v) for k, v in canonical["stage8"].items()
    if k[0] == 18 and v["signature"] == TARGET_Q and v["learned"] == "learned"
]
research_target_evals = [
    (k, v) for k, v in masked["stage8"].items()
    if k[0] == 18 and v["signature"] == TARGET_Q
]
if canonical_target_reads:
    assert len(masked["masked_reads"]) == len(research_target_evals) > 0, (
        "targeted Stage11 Q read interception did not occur")
    assert all(row["step"] == 18 and row["signature"] == TARGET_Q
               for row in masked["masked_reads"])
    assert all(v["learned"] == "unlearned" and v["q"] is None
               for _, v in research_target_evals), (
        "targeted manipulation leaked learned Q to Stage11")
    assert all(canonical["applied"][t] == masked["applied"][t]
               for t in range(1, 18)), (
        "targeted research arm diverged before intervention")
    assert (canonical["snapshots"][17]["before"]["body"] ==
            masked["snapshots"][17]["before"]["body"]), (
        "targeted research arms had different pre-step-18 bodies")
else:
    assert not masked["masked_reads"], (
        "unregistered targeted Q read in a non-exposed birth")

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
    "source": "step18-targeted-collect-q-prebirth-m11",
    "preset": preset_name,
    "identity_suffix": identity_suffix,
    "preregistered": True,
    "canonical_engine_unchanged": True,
    "research_variant": "stage8-collect-signature-only-step18-read-masked-before-birth",
    "physical_world_and_physics_identical": True,
    "birth_identity_same_in_separate_ledgers": True,
    "first_q_suppression_step": first_q_suppression_step,
    "masked_genuine_learned_stage8_reads": len(masked["masked_reads"]),
    "selective_intervention_audit": {
        "wrapper_class": "i1.modules.stage11_evaluator.Stage11OptionEvaluator",
        "research_stage8_calls_last_two_steps": masked["stage8_calls"],
        "research_q_read_attempts_last_two_steps": masked["read_attempts"],
        "canonical_food_stage8_last_step": [
            {"cycle": k[1], "option_ref": k[2], **v}
            for k, v in sorted(canonical["stage8"].items())
            if k[0] == 18 and "collecter" in v["signature"]
        ],
        "research_food_stage8_last_step": [
            {"cycle": k[1], "option_ref": k[2], **v}
            for k, v in sorted(masked["stage8"].items())
            if k[0] == 18 and "collecter" in v["signature"]
        ],
    },
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
    "first_divergence_q_and_competition": (
        {
            "step": first_physical,
            "canonical_stage8": [
                {"cycle": k[1], "option_ref": k[2], **v}
                for k, v in sorted(canonical["stage8"].items())
                if k[0] == first_physical
            ],
            "masked_stage8": [
                {"cycle": k[1], "option_ref": k[2], **v}
                for k, v in sorted(masked["stage8"].items())
                if k[0] == first_physical
            ],
            "canonical_competition": [
                {"cycle": k[1], "option_ref": k[2], **v}
                for k, v in sorted(canonical["competition"].items())
                if k[0] == first_physical
            ],
            "masked_competition": [
                {"cycle": k[1], "option_ref": k[2], **v}
                for k, v in sorted(masked["competition"].items())
                if k[0] == first_physical
            ],
            "canonical_td_publications": [
                {"step": event["t_monde"],
                 "previous_signature": event["data"]["previous_signature"],
                 "next_signature": event["data"]["next_signature"],
                 "return_g": event["data"]["return_g"],
                 "delta": event["data"]["delta"],
                 "updated_signatures": event["data"]["updated_signatures"]}
                for event in canonical["events"]
                if event.get("kind") == "td_update_published"
                and event["t_monde"] <= first_physical
            ],
            "canonical_admitted": canonical["admitted"][first_physical],
            "masked_admitted": masked["admitted"][first_physical],
            "masked_genuine_learned_reads": [
                x for x in masked["masked_reads"]
                if x["step"] == first_physical
            ],
        }
        if first_physical is not None
        and preset_name == "oasis" and identity_suffix == "b" else None
    ),
    "post_meal_reuse_audit": (
        {
            "first_meal_step": next(
                (t for t in sorted(canonical["applied"])
                 if canonical["applied"][t]["primitive"] == "manger"),
                None),
            "later_applied": [
                {"step": t, **canonical["applied"][t]}
                for t in sorted(canonical["applied"])
                if t > 11
            ],
            "later_bodies": [
                {"step": row["step"], "before": row["before"]["body"],
                 "after": row["after"]["body"],
                 "before_inventory": row["before"]["inventory"],
                 "after_inventory": row["after"]["inventory"]}
                for row in canonical["snapshots"] if row["step"] > 11
            ],
            "later_td": [
                {"step": e["t_monde"], "cycle": e["cycle"],
                 "previous_signature": e["data"]["previous_signature"],
                 "next_signature": e["data"]["next_signature"],
                 "return_g": e["data"]["return_g"],
                 "delta": e["data"]["delta"],
                 "updated_signatures": e["data"]["updated_signatures"]}
                for e in canonical["events"]
                if e.get("kind") == "td_update_published"
                and e["t_monde"] > 11
            ],
            "later_food_stage8": [
                {"step": k[0], "cycle": k[1], "option_ref": k[2], **v,
                 "competition": canonical["competition"].get(k)}
                for k, v in sorted(canonical["stage8"].items())
                if k[0] > 11 and
                (":manger:" in v["signature"] or
                 ":collecter:" in v["signature"])
            ],
            "later_food_proposals": [
                {"step": e["t_monde"], "cycle": e["cycle"],
                 "signature": e["data"].get("learning_signature"),
                 "command": e["data"].get("command"),
                 "learned_value_status": e["data"].get("learned_value_status")}
                for e in canonical["events"]
                if e.get("kind") == "i1_local_opportunity_proposed"
                and e["t_monde"] > 11 and
                e["data"].get("command", {}).get("primitive")
                in ("collecter", "manger")
            ],
            "later_food_admissions": [
                {"step": t, **v}
                for t, v in sorted(canonical["admitted"].items())
                if t > 11 and v["primitive"] in ("collecter", "manger")
            ],
            "learning_reuse_causal_verdict": "NOT_ESTABLISHED",
            "source": "same-authenticated-natural-M11-life-no-extended-horizon",
        }
        if preset_name == "oasis" and identity_suffix == "b" else None
    ),
    "immediate_first_divergence": immediate,
    "adaptive_benefit": "NOT_ESTABLISHED",
    "durability_and_generalization": "NOT_ESTABLISHED",
    "no_result_forced": True,
}
print("I1_305_SELECTIVE_COLLECT_Q_STEP18=" +
      json.dumps(summary, sort_keys=True))
"""
            env = dict(os.environ,
                       PYTHONPATH=os.pathsep.join((
                           str(generated), str(ROOT / "src"),
                           str(ROOT / "tools"))),
                       PYTHONDONTWRITEBYTECODE="1")
            import json
            scoped_env = dict(env, I1_HELDOUT_PRESET="oasis",
                              I1_HELDOUT_IDENTITY="b")
            proc = subprocess.run(
                [sys.executable, "-B", "-c", script], cwd=ROOT,
                env=scoped_env, text=True, capture_output=True, timeout=480)
            self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
            prefix = "I1_305_SELECTIVE_COLLECT_Q_STEP18="
            line = next((x for x in proc.stdout.splitlines()
                         if x.startswith(prefix)), None)
            self.assertIsNotNone(line, proc.stdout)
            result = json.loads(line[len(prefix):])
            self.assertEqual((result["preset"], result["identity_suffix"]),
                             ("oasis", "b"))
            self.assertTrue(result["canonical_engine_unchanged"])
            self.assertEqual(result["adaptive_benefit"], "NOT_ESTABLISHED")
            self.assertTrue(result["same_commands_before_first_divergence"])
            # Outcome may be negative, but the intervention cannot change any
            # physical action before the preregistered step 18.
            first = result["first_physically_different_command_step"]
            self.assertTrue(first is None or first == 18, result)
            print(line, flush=True)


if __name__ == "__main__":
    unittest.main()
