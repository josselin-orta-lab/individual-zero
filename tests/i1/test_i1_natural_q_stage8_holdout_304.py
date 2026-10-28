"""Held-out fixed two-world Stage8 Q-read contrast (#304/#438).

Research-only paired mortal M11 lives, no canonical motor changes. See
src/i1/docs/EXPERIMENT_304_Q_STAGE8_HELDOUT_2026-10-28.md.
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


class NaturalStage8ReadHoldout304(unittest.TestCase):
    def test_fixed_heldout_worlds_without_motor_success_assertions(self):
        with TemporaryDirectory(prefix="i1-304-heldout-qread-") as home:
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
from i1lab.i1_active_runtime import ExperimentalI1Stage12Runtime
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
original_stage8 = Stage8OptionEvaluator.evaluate
original_read = LinearTDValues.learned_value
original_consider = ExperimentalI1Stage12Runtime._consider_uncertain_affordance


def life(mode, path):
    assert mode in ("canonical", "stage8_q_read_masked")
    masked_reads = []
    cursor = {}
    read_calls = [0]
    upstream_reads = []
    def observe_consider(owner, *, capture, goal, st_version, cycle, exact):
        reads = []
        def observer(td_owner, state, signature):
            value = original_read(td_owner, state, signature)
            if td_owner is owner.q_active:
                reads.append({
                    "signature": signature, "status": value.status,
                    "value": value.value, "evidence": value.evidence,
                    "update_count": value.update_count,
                })
            return value
        with patch.object(LinearTDValues, "learned_value", observer):
            result = original_consider(
                owner, capture=capture, goal=goal, st_version=st_version,
                cycle=cycle, exact=exact)
        if reads:
            assert result is not None
            upstream_reads.append({
                "step": capture.t_monde, "cycle": cycle,
                "option_ref": result.option.id, "reads": reads,
            })
        return result

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
    with scope, patch.object(ExperimentalI1Stage12Runtime,
                             "_consider_uncertain_affordance", observe_consider):
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
    proposed = [e for e in events
                if e.get("kind") == "i1_unknown_affordance_proposed"]
    assert len(proposed) == len(upstream_reads)
    upstream_joined = []
    for event, observation in zip(proposed, upstream_reads):
        data = event["data"]
        assert (event["t_monde"], event["cycle"], data["option_ref"]) == (
            observation["step"], observation["cycle"], observation["option_ref"])
        reads = observation["reads"]
        assert len(reads) == data["candidate_count"]
        assert [x["signature"].split(":")[2] for x in reads] == data["candidate_primitives"]
        command = data["command"]
        suffix = ":".join(f"{k}={command['parameters'][k]}"
                          for k in sorted(command["parameters"])) or "here"
        signature = "i1:affordance:" + command["primitive"] + ":" + suffix
        winners = [x for x in reads if x["signature"] == signature]
        assert len(winners) == 1
        assert winners[0]["status"] == data["learned_value_status"]
        assert winners[0]["value"] == data["learned_value"]
        upstream_joined.append({
            "step": observation["step"], "cycle": observation["cycle"],
            "option_ref": observation["option_ref"], "reads": reads,
            "winner_signature": signature, "candidate_count": len(reads),
        })

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
                    "accumulator_before": trace["accumulator_before"],
                    "accumulator_after": trace["accumulator_after"],
                    "threshold": trace["threshold"],
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
        "events": events,
        "upstream_q_actual_reads": upstream_joined,
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

def competition_mediation_438(a, b):
    # No extra TD/Stage8/Competition calls: join validated committed M11 logs.
    assert a["head_verified"] and b["head_verified"]
    reads = sorted(
        (r["step"], r["cycle"], r["option_ref"], r["signature"])
        for r in b["masked_reads"]
    )
    masked_keys = {(t, c, ref) for t, c, ref, _ in reads}
    keys = sorted(set(a["competition"]) | set(b["competition"]))
    first = next(
        (k for k in keys
         if a["competition"].get(k) != b["competition"].get(k)), None)
    first_read = reads[0] if reads else None
    owner_before = next(
        (t for t in sorted(a["applied"])
         if t in b["applied"] and
         a["snapshots"][t-1]["before"]["competition"] !=
         b["snapshots"][t-1]["before"]["competition"]),
        None)
    first_motor = next(
        (t for t in sorted(set(a["applied"]) & set(b["applied"]))
         if a["applied"][t] != b["applied"][t]), None)
    record = None
    verdict = "NO_COMPETITION_DIVERGENCE"
    if first is not None:
        x, y = a["competition"].get(first), b["competition"].get(first)
        s8a, s8b = a["stage8"].get(first), b["stage8"].get(first)
        paired = x is not None and y is not None
        matched_q_read = bool(
            paired and first in masked_keys
            and s8a is not None and s8b is not None
            and s8a["learned"] == "learned"
            and s8b["learned"] == "unlearned"
            and s8a["signature"] == s8b["signature"]
            and s8a["status"] == s8b["status"] == "evaluated"
            and abs(x["evidence"] - s8a["evidence"]) < 1e-10
            and abs(y["evidence"] - s8b["evidence"]) < 1e-10
        )
        record = {
            "step": first[0], "cycle": first[1], "option_ref": first[2],
            "canonical_competition": x, "masked_competition": y,
            "canonical_stage8": s8a, "masked_stage8": s8b,
            "same_option_present_both": paired,
            "genuine_masked_learned_read_on_same_option": matched_q_read,
            "canonical_compute_charges_this_step": a["charges"].get(first[0], []),
            "masked_compute_charges_this_step": b["charges"].get(first[0], []),
        }
        if first_read is None or (first[0], first[1]) < first_read[:2]:
            verdict = "CHRONOLOGY_INCONSISTENT"
        elif not paired:
            verdict = "UNMATCHED_CANDIDATES"
        elif matched_q_read and x["evidence"] != y["evidence"]:
            verdict = "MATCHED_STAGE8_Q_EVIDENCE_MEDIATION_COMPATIBLE"
        else:
            verdict = "MATCHED_TRACE_DIVERGENCE_CAUSE_NOT_ISOLATED"
    return {
        "source": "read_only_join_of_audited_committed_M11_cycles",
        "first_masked_learned_stage8_read": (
            {"step": first_read[0], "cycle": first_read[1],
             "option_ref": first_read[2], "signature": first_read[3]}
            if first_read is not None else None
        ),
        "first_competition_trace_difference": record,
        "first_different_competition_owner_preaction_step": owner_before,
        "first_physically_different_action_step": first_motor,
        "competition_diff_precedes_or_coincides_with_motor": (
            None if first is None or first_motor is None
            else first[0] <= first_motor
        ),
        "paired_chronology_verdict": verdict,
        "direct_motor_effect_at_competition_equal": (
            "NOT_ESTABLISHED" if owner_before is not None
            and first_motor is not None and owner_before <= first_motor
            else "NOT_ASSESSED_BY_THIS_AUDIT"
        ),
        "total_intervention_motor_effect": (
            "ACTION_DIVERGENCE_OBSERVED" if first_motor is not None
            else "NOT_OBSERVED"
        ),
        "adaptive_benefit": "NOT_ESTABLISHED",
        "scientific_generalization": "NOT_ESTABLISHED",
    }


def upstream_exposure_305(arm):
    rows = arm["upstream_q_actual_reads"]
    multi = [r for r in rows if r["candidate_count"] > 1]
    learned = [r for r in multi if any(
        q["status"] == "learned" for q in r["reads"])]
    return {
        "source": "original_Q_reads_joined_to_audited_M11_proposals",
        "proposed_events": len(rows), "multicandidate_events": len(multi),
        "multi_with_learned_Q": len(learned),
        "multicandidate": multi,
        "verdict": (
            "NO_MULTICANDIDATE" if not multi else
            "MULTICANDIDATE_WITH_LEARNED_Q" if learned
            else "MULTICANDIDATE_ALL_UNLEARNED"
        ),
        "upstream_causal_choice": "NOT_ESTABLISHED",
        "instrumental_benefit": "NOT_ESTABLISHED",
    }


summary = {
    "upstream_q_crossworld_305": {
        "canonical": upstream_exposure_305(canonical),
        "stage8_masked": upstream_exposure_305(masked),
    },
    "competition_mediation_chronology_438": competition_mediation_438(canonical, masked),
    "source": "fixed-heldout-two-registered-worlds-prebirth-m11",
    "preset": preset_name,
    "identity_suffix": identity_suffix,
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
print("I1_304_HELDOUT_STAGE8_Q_READ_CONTRAST=" +
      json.dumps(summary, sort_keys=True))
"""
            env = dict(os.environ,
                       PYTHONPATH=os.pathsep.join((
                           str(generated), str(ROOT / "src"),
                           str(ROOT / "tools"))),
                       PYTHONDONTWRITEBYTECODE="1")
            import json
            for preset_name in ("oasis", "foraging"):
                for suffix in ("a", "b"):
                    with self.subTest(preset=preset_name, identity=suffix):
                        scoped_env = dict(env, I1_HELDOUT_PRESET=preset_name,
                                          I1_HELDOUT_IDENTITY=suffix)
                        proc = subprocess.run(
                            [sys.executable, "-B", "-c", script], cwd=ROOT,
                            env=scoped_env, text=True, capture_output=True,
                            timeout=480)
                        self.assertEqual(proc.returncode, 0,
                                         proc.stdout + proc.stderr)
                        prefix = "I1_304_HELDOUT_STAGE8_Q_READ_CONTRAST="
                        self.assertIn(prefix, proc.stdout)
                        line = next(x for x in proc.stdout.splitlines()
                                    if x.startswith(prefix))
                        result = json.loads(line[len(prefix):])
                        self.assertEqual(result["preset"], preset_name)
                        self.assertEqual(result["identity_suffix"], suffix)
                        self.assertTrue(result["canonical_engine_unchanged"])
                        self.assertEqual(result["adaptive_benefit"],
                                         "NOT_ESTABLISHED")
                        print(line, flush=True)


if __name__ == "__main__":
    unittest.main()
