#!/usr/bin/env python3
"""#317 operator-only factorial test: recovered fatigue and natural awakening.

Compare unchanged I1 to recovery-aware wake evaluation, a higher NATURAL-END
wake threshold, and their combination, in separately born mortal lives. The
candidate reuses the original previous waking memory-consolidation pressure
and day/night phase: only measured fatigue recovery changes within a sleep
bout. Nothing commands sleep or waking: DC-13 still decides precedence, and
Competition/Action Control always decide waking actions. Physics, death,
learned Q/TD, memory consolidation, vital alerts and I0 remain unchanged.

The dynamic session evaluator is research-only: it is attached to an
independently born actor before the first physical step and is NOT the
canonical engine nor a persistent cold-restoration implementation. No
claim of human-equivalence or scientific GO is made from short horizons.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from math import isfinite, isclose
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

PRESETS = ("oasis", "foraging", "dry-valley", "memory-corridor")
# Entire design locked before running; neither previous 9761/9791 nor
# diagnostics 1141/1142, 8411..8497, 9601/9631 may be reused.
SEEDS = (11117, 11239)
HORIZON = 300
ARMS = ("canonical", "recovered_fatigue", "natural_threshold",
        "recovered_and_threshold")
EXPERIMENTAL_NATURAL_WAKE_THRESHOLD = 0.35
STANDARD_NATURAL_WAKE_THRESHOLD = 0.10


def _factor(arm):
    if arm not in ARMS:
        raise ValueError("unregistered factorial arm")
    return (
        arm in ("recovered_fatigue", "recovered_and_threshold"),
        arm in ("natural_threshold", "recovered_and_threshold"),
    )


def calibrate_native_birth(stage10_config, arm):
    """Allow precisely a versioned natural-wake threshold, nothing else."""
    recovered, altered_threshold = _factor(arm)
    if not altered_threshold:
        raise ValueError("only threshold profiles change the birth configuration")
    original = stage10_config
    changed = replace(original.sleep,
        version=original.sleep.version+"+i1-317-wake-factorial-"+arm,
        natural_wake_threshold=EXPERIMENTAL_NATURAL_WAKE_THRESHOLD)
    cfg = replace(original, sleep=changed,
        version=original.version+"+i1-317-wake-factorial-"+arm)
    cfg.validate()
    if (replace(cfg, version=original.version, sleep=original.sleep) != original
        or replace(changed, version=original.sleep.version,
                   natural_wake_threshold=original.sleep.natural_wake_threshold)
                   != original.sleep):
        raise RuntimeError("threshold treatment modified non-wake birth state")
    return cfg


def recovered_fatigue_pressure(*, frozen, entry_fatigue, current_fatigue,
                               sleep_config, frozen_night):
    """Recovery-only counterfactual from first-person owned F_cog.

    Uses the most recent *already frozen waking* consolidation pressure
    and time-of-day observation. It neither reads new Memory episodes nor
    changes pressure at the first sleeping step. Later physical recovery
    decreases F_cog, never invents consolidation or motor permission.
    """
    if (type(frozen_night) is not bool
        or any(type(v) not in (int, float) or not isfinite(v) or not 0 <= v <= 1
               for v in (frozen.fatigue, frozen.consolidation_pressure,
                         frozen.sleep_pressure, entry_fatigue, current_fatigue))
        or current_fatigue > entry_fatigue + 1e-10):
        raise ValueError("wake recovery must be bounded, physical and monotone")
    cfg = sleep_config
    base = (cfg.fatigue_weight * frozen.fatigue
            + cfg.consolidation_weight * frozen.consolidation_pressure
            + (cfg.night_weight if frozen_night else 0.0))
    if not isclose(min(1.0, base), frozen.sleep_pressure,
                   rel_tol=0.0, abs_tol=1e-12):
        raise RuntimeError("source frozen pressure no longer matches DC-13")
    candidate = base + cfg.fatigue_weight * (current_fatigue - entry_fatigue)
    return min(1.0, max(0.0, candidate))


def install_recovery_only_observer(actor):
    """Research-only intervention at birth, before any physical transition.

    The wrapped owner still delegates to the genuine Stage10 session
    with identical reflex, alert, intention, consolidation-active and
    maximum-duration flags. Only the scalar natural-end pressure differs.
    No command or extra world capture occurs in this wrapper.
    """
    session = actor.sleep_session
    native = session.evaluate_sleep_step
    state = {"entry_step": None, "entry_fatigue": None,
             "evaluations": 0, "adjusted": 0}
    def evaluate(*, signals, frozen_sleep_pressure, wake_rule):
        if session.mode != "sleeping" or session.entry_step is None:
            raise RuntimeError("research wake evaluation outside true sleep")
        frozen = actor.sleep_health.frozen
        ref_step = actor.sleep_health.frozen_world_step
        if (frozen is None or type(ref_step) is not int
            or ref_step >= actor.scheduler.t_monde
            or wake_rule is not actor.sleep_health.rules):
            raise RuntimeError("recomputed wake lacks authentic frozen ownership")
        current = actor.sleep_health.fatigue
        if session.entry_step != state["entry_step"]:
            state["entry_step"] = session.entry_step
            state["entry_fatigue"] = current
        computed = recovered_fatigue_pressure(
            frozen=frozen, entry_fatigue=state["entry_fatigue"],
            current_fatigue=current,
            sleep_config=actor._stage10_config.sleep,
            frozen_night=actor.world.is_night(ref_step),
        )
        if session.sleep_duration == 1 and not isclose(
            computed, frozen_sleep_pressure, rel_tol=0.0, abs_tol=1e-12
        ):
            raise RuntimeError("first sleep step cannot change frozen wake evidence")
        state["evaluations"] += 1
        if not isclose(computed, frozen_sleep_pressure, abs_tol=1e-12):
            state["adjusted"] += 1
        return native(signals=signals, frozen_sleep_pressure=computed,
                      wake_rule=wake_rule)
    session.evaluate_sleep_step = evaluate
    return state


def _run_lengths(values):
    runs, length = [], 0
    for value in values:
        if value:
            length += 1
        elif length:
            runs.append(length)
            length = 0
    if length:
        runs.append(length)
    return runs


def summarize_life(life, events, actor):
    trajectory = life["steps"]
    if not trajectory:
        raise ValueError("empty mortal physical life")
    asleep = [row["action_primitive"] == "dormir"
              for row in trajectory]
    night = [actor.world.is_night(row["world_step"])
             for row in trajectory]
    night_count = sum(night)
    sleep_night = sum(a and n for a, n in zip(asleep, night))
    day_count = len(trajectory)-night_count
    sleep_day = sum(a and not n for a, n in zip(asleep, night))
    wake_alerts = {
        e["t_monde"] for e in events
        if e.get("kind") == "stage10_sleep_woke"
        and isinstance(e.get("data"), dict)
        and e["data"].get("reason") == "alert"
    }
    committed = [
        e for e in events if e.get("kind")=="stage10_consolidation_committed"]
    objects = set()
    publications = [
        e for e in events
        if e.get("kind")=="stage10_consolidation_version_activated"
    ]
    if len(committed) != len(publications):
        raise RuntimeError("unmatched atomic publication")
    for publication in publications:
        batch = publication["data"]["batch"]
        if (not isinstance(batch, list) or not batch
            or any(not isinstance(ref,str) or ref in objects
                   for ref in batch)):
            raise RuntimeError("consolidated invented/duplicate reference")
        objects.update(batch)
    episode_refs = [
        e["data"]["id"] for e in events
        if e.get("kind") == "episode_closed"
        and isinstance(e.get("data"), dict)
    ]
    if len(set(episode_refs)) != len(episode_refs):
        raise RuntimeError("duplicate physical episode identity")
    if not objects.issubset(episode_refs):
        raise RuntimeError("consolidated episode never physically lived")
    uc = sum(
        e["data"]["requested_uc"] for e in events
        if e.get("kind") == "compute_charge"
        and isinstance(e.get("data"), dict)
        and e["data"].get("accepted") is True
    )
    if type(uc) is not int or uc < 0:
        raise ValueError("non-canonical logical UC")
    batches = _run_lengths(asleep)
    return {
        "lifecycle":life["lifecycle"],
        "lived_steps":len(trajectory),
        "action_counts":dict(Counter(x["action_primitive"] for x in trajectory)),
        "sleep_fraction":sum(asleep)/len(trajectory),
        "night_sleep_fraction":(
            sleep_night/night_count if night_count else None),
        "day_sleep_fraction":sleep_day/day_count if day_count else None,
        "night_observed_steps":night_count, "day_observed_steps":day_count,
        "physical_sleep_bouts":len(batches),
        "mean_sleep_bout_steps":(
            sum(batches)/len(batches) if batches else 0.0),
        "maximum_sleep_bout_steps":max(batches,default=0),
        "alert_wakes":len(wake_alerts),
        "alert_wakes_followed_by_sleep":sum(
            x["world_step"] in wake_alerts and x["action_primitive"] == "dormir"
            for x in trajectory),
        "consolidation_commits":len(committed),
        "objects_consolidated":len(objects),
        "episode_objects_closed":len(episode_refs),
        "pending_episode_objects":len(episode_refs)-len(objects),
        "accepted_cognitive_uc":uc,
        "final_body":trajectory[-1]["body"],
        "final_position":trajectory[-1]["position"],
        "journal_head":life["journal_head"],
        "verified_journal_entries":life["durable_entries"],
        "physical_wake_thresholds":dict(
            actor._stage10_config.critical_body_thresholds),
        "Stage10_sleep_pressure":{
            "fatigue_gain":actor._stage10_config.sleep.fatigue_gain,
            "sleep_fatigue_recovery":
                actor._stage10_config.sleep.sleep_fatigue_recovery,
            "fatigue_weight":actor._stage10_config.sleep.fatigue_weight,
            "consolidation_weight":
                actor._stage10_config.sleep.consolidation_weight,
            "night_weight":actor._stage10_config.sleep.night_weight,
            "intrinsic_weight":actor._stage10_config.intrinsic_weight,
        },
    }


def run(preset, seed, output):
    if (preset not in PRESETS or type(seed) is not int or seed not in SEEDS):
        raise ValueError("not an independently preregistered birth")
    output = output.resolve()
    if output.exists():
        raise FileExistsError("never replay into an old physical WAL directory")
    from run_i1_world_preset import (_birth_parameters, _wal_life, load_preset)
    source_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
        check=True, capture_output=True).stdout.strip()
    source, preset_digest = load_preset(preset)
    report = {
        "schema":"i1-317-wake-recovery-factorial-mortal/v1",
        "source_sha":source_sha, "preset":preset, "seed":seed,
        "preset_sha256":preset_digest, "horizon":HORIZON,
        "preregistered_arms":list(ARMS),
        "no_sleep_or_motor_forcing":True,
        "same_world_needs_rewards_td_competition_action_control":True,
        "ordinary_wake_thresholds_unchanged":True,
        "all_born_independently_and_irreversibly":True,
        "no_coma_implemented":True,
        "pre_registered_factorial":True,
        "only_natural_wake_pressure_and_threshold_intervened":True,
        "learned_entity_causality_proven":False,
        "human_equivalence_proven":False,
        "scientific_verdict":"NO-GO",
        "status":"NOT_STARTED",
        "factorial_dimensions":{
            "recovery_update": [False, True],
            "natural_wake_threshold": [
                STANDARD_NATURAL_WAKE_THRESHOLD,
                EXPERIMENTAL_NATURAL_WAKE_THRESHOLD,
            ],
        },
    }
    output.mkdir(parents=True, exist_ok=False)
    try:
        with TemporaryDirectory(prefix="i1-317-wake-factorial-") as tmp:
            from build_i1_fork import generate
            generated = Path(tmp)/"generated"
            generate(generated)
            sys.path.insert(0,str(generated))
            from i1lab.i1_birth import birth_i1
            from i1lab import i1_natural_runtime
            from audit_i1_spatial_navigation_314 import audit as audit_wal
            parameters, _ = _birth_parameters(source)
            report["physics_digest"] = parameters["world_config"].digest()
            original_enable = i1_natural_runtime.enable_natural_sleep_birth
            arms = {}
            for label in ARMS:
                directory=output/label
                directory.mkdir()
                wal=directory/"life-01.wal"
                born=[]
                recovered, altered_threshold = _factor(label)
                research_observer = None

                def birth(**kwargs):
                    nonlocal research_observer
                    if not altered_threshold:
                        actor=birth_i1(**kwargs)
                    else:
                        def isolated(*, world_config, stage10_config):
                            world, native = original_enable(
                                world_config=world_config,
                                stage10_config=stage10_config)
                            return world, calibrate_native_birth(native,label)
                        # Only fresh birth construction gets the threshold
                        # override. Restore the I1 module before the life.
                        with patch.object(
                            i1_natural_runtime,"enable_natural_sleep_birth",
                            isolated
                        ):
                            actor=birth_i1(**kwargs)
                    if recovered:
                        research_observer=install_recovery_only_observer(actor)
                    born.append(actor)
                    return actor

                try:
                    life=_wal_life(
                        birth=birth, params=parameters,
                        life_id=f"i1:preset:{preset}:{seed}:0",
                        path=wal, steps=HORIZON)
                except Exception as exc:
                    # Preserve provenance of a genuinely stopped mortal life.
                    # Never rewind or retry a step that may have dispatched.
                    actor = born[0] if len(born) == 1 else None
                    last = (None if actor is None else
                            getattr(actor, "_last_applied_decision", None))
                    session = (None if actor is None else
                               actor.sleep_session.export_causal_state())
                    report.setdefault("stopped_births", []).append({
                        "arm": label,
                        "error": type(exc).__name__ + ": " + str(exc),
                        "mortal_status": (
                            None if actor is None else
                            str(actor.stage3.substrate.mortal_status)),
                        "sleep_session": session,
                        "last_applied_decision": (
                            None if last is None else {
                                "motive_type":last[2].option.motive_ref.type,
                                "option_ref":last[2].option.id,
                                "prepared_source":last[1].source,
                                "prepared_primitive":last[1].command.primitive,
                                "admission_ok":last[0].ok,
                                "admitted_primitive":last[0].command.primitive,
                            }),
                        "wal_relative_path":str(Path(label)/wal.name),
                        "wal_sha256":(
                            sha256(wal.read_bytes()).hexdigest()
                            if wal.is_file() else None),
                        "no_retry_or_rollback":True,
                    })
                    raise
                if len(born)!=1:
                    raise RuntimeError("non-unique lab mortal actor")
                actor=born[0]
                native_wake=(
                    {"water":15.0,"food":10.0,"integrity":25.0,"energy":10.0})
                actual=dict(actor._stage10_config.critical_body_thresholds)
                if any(actual.get(k,0)<v for k,v in native_wake.items()):
                    raise RuntimeError("weakened first-person vital wake")
                original_cfg = actor._stage10_config
                expected_threshold = (
                    EXPERIMENTAL_NATURAL_WAKE_THRESHOLD
                    if altered_threshold else STANDARD_NATURAL_WAKE_THRESHOLD)
                if (original_cfg.sleep.natural_wake_threshold != expected_threshold
                    or original_cfg.sleep.fatigue_gain != 0.7
                    or original_cfg.sleep.sleep_fatigue_recovery != 0.3
                    or original_cfg.sleep.fatigue_weight != 0.65
                    or original_cfg.sleep.consolidation_weight != 0.25
                    or original_cfg.sleep.night_weight != 0.20
                    or original_cfg.intrinsic_weight != 0.9
                    or original_cfg.sleep.max_consecutive_sleep_steps != 6
                    or original_cfg.sleep.unconsolidated_episode_reference != 8.0
                    or original_cfg.sleep.memory_saturation_reference != 2.0):
                    raise RuntimeError("one of three sleep processes was changed by birth")
                if recovered != (research_observer is not None):
                    raise RuntimeError("unregistered recovery observer state")
                proof=audit_wal(wal)
                if (proof["independent_hash_chain_verified"] is not True
                    or proof["journal_head"] != life["journal_head"]
                    or proof["journal_entries"] != life["durable_entries"]):
                    raise RuntimeError("individual original WAL custody failed")
                events=[json.loads(line)["causal_event"]
                        for line in wal.read_bytes().splitlines()]
                details=summarize_life(life,events,actor)
                details["wake_reasons"]=dict(Counter(
                    e["data"].get("reason") for e in events
                    if e.get("kind")=="stage10_sleep_woke"
                    and isinstance(e.get("data"),dict)))
                details["recomputed_wake_evaluations"]=(
                    research_observer["evaluations"] if recovered else 0)
                details["pressure_adjusted_evaluations"]=(
                    research_observer["adjusted"] if recovered else 0)
                details["natural_wake_threshold"]=expected_threshold
                details["experimental_recovery_adjustment"]=recovered
                details["wal_sha256"]=sha256(wal.read_bytes()).hexdigest()
                details["wal_relative_path"]=str(Path(label)/wal.name)
                arms[label]=details
        if (len(set(r["physical_wake_thresholds"].__repr__()
                    for r in arms.values())) != 1):
            raise RuntimeError("thresholds differ across matched births")
        report["arms"]=arms
        report["status"]="COMPLETE_PAIRED_PHYSICAL_DIAGNOSTIC"
    except Exception as e:
        report["status"]="TECHNICAL_FAILURE"
        report["error"]=type(e).__name__+": "+str(e)
        raise
    finally:
        (output/"report.json").write_text(
            json.dumps(report,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({
        "status":report["status"],
        "preset":preset,"seed":seed,
        "arms":{k:{x:r[x] for x in (
            "lifecycle","lived_steps","sleep_fraction",
            "night_sleep_fraction","day_sleep_fraction",
            "pending_episode_objects","objects_consolidated",
            "consolidation_commits","accepted_cognitive_uc",
            "wake_reasons","recomputed_wake_evaluations",
            "pressure_adjusted_evaluations")}
            for k,r in report["arms"].items()},
        "scientific_verdict":report["scientific_verdict"],
    },indent=2,sort_keys=True))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset",required=True)
    parser.add_argument("--seed",type=int,required=True)
    parser.add_argument("--output-dir",type=Path,required=True)
    args=parser.parse_args()
    run(args.preset,args.seed,args.output_dir)


if __name__=="__main__":
    main()
