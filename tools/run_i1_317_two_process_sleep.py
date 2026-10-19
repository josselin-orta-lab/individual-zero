#!/usr/bin/env python3
"""#317 operator-only two-process sleep calibration, independently mortal I1.

Born under canonical world/physics/Action Control/Competition/TD; the only
changed experimental input is a frozen, versioned Stage10 sleep-pressure
configuration passed at birth, NEVER a scripted motor command, learned reward,
physical resource, direct Q edit or sleep/alert/critical-body override.

Two-process analogue, not a claim of human-equivalent units or circadian time:
awake UC fatigue (homeostatic S) + observed night phase (circadian C).
Consolidation is genuine separately priced Stage10 work, not a perpetual
behaviour command. Each arm is a different, irreversible life with its own
cryptographically audited WAL. Research calibrations are never enabled by the
canonical birth_i1 API and are not scientific GO before matched outcomes.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

PRESETS = ("oasis", "foraging", "dry-valley", "memory-corridor")
SEEDS = (9761, 9791)
HORIZON = 300
ARMS = ("canonical", "homeostatic", "circadian")

# Locked candidate settings before the first cohort. These are deliberately
# non-human units, bounded hypotheses, NOT fitted to old diagnostic deaths.
PROFILES = {
    "homeostatic": dict(
        fatigue_gain=0.20, sleep_fatigue_recovery=0.36,
        fatigue_weight=0.62, consolidation_weight=0.05,
        night_weight=0.27, unconsolidated_episode_reference=32.0,
        memory_saturation_reference=4.0, intrinsic_weight=0.82,
        max_consecutive_sleep_steps=6,
    ),
    "circadian": dict(
        fatigue_gain=0.12, sleep_fatigue_recovery=0.34,
        fatigue_weight=0.58, consolidation_weight=0.03,
        night_weight=0.42, unconsolidated_episode_reference=32.0,
        memory_saturation_reference=4.0, intrinsic_weight=0.85,
        max_consecutive_sleep_steps=6,
    ),
}


def calibrate_native_birth(stage10_config, arm):
    """Only Stage10's original lawful sleep motive, never physiological facts."""
    if arm not in PROFILES:
        raise ValueError("not a preregistered sleep profile")
    selected = PROFILES[arm]
    wake_baseline = dict(stage10_config.critical_body_thresholds)
    sleep = replace(
        stage10_config.sleep,
        version=stage10_config.sleep.version+"+i1-317-two-process-"+arm,
        **{key: value for key, value in selected.items()
           if key != "intrinsic_weight"}
    )
    cfg = replace(
        stage10_config,
        version=stage10_config.version+"+i1-317-two-process-"+arm,
        sleep=sleep,
        intrinsic_weight=selected["intrinsic_weight"],
    )
    cfg.validate()
    if (dict(cfg.critical_body_thresholds) != wake_baseline
        or cfg.p_cons_min != stage10_config.p_cons_min
        or cfg.sleep_work != stage10_config.sleep_work
        or cfg.maximum_passes_per_sleep_step !=
           stage10_config.maximum_passes_per_sleep_step):
        raise RuntimeError("candidate changed wake/semantic work outside P40")
    return cfg


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
        "schema":"i1-317-two-process-sleep-mortal-pairs/v1",
        "source_sha":source_sha, "preset":preset, "seed":seed,
        "preset_sha256":preset_digest, "horizon":HORIZON,
        "preregistered_arms":list(ARMS),
        "no_sleep_or_motor_forcing":True,
        "same_world_needs_rewards_td_competition_action_control":True,
        "ordinary_wake_thresholds_unchanged":True,
        "all_born_independently_and_irreversibly":True,
        "no_coma_implemented":True,
        "learned_entity_causality_proven":False,
        "human_equivalence_proven":False,
        "scientific_verdict":"NO-GO",
        "status":"NOT_STARTED",
    }
    output.mkdir(parents=True, exist_ok=False)
    try:
        with TemporaryDirectory(prefix="i1-317-two-process-") as tmp:
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

                def birth(**kwargs):
                    if label == "canonical":
                        actor=birth_i1(**kwargs)
                    else:
                        def isolated(*, world_config, stage10_config):
                            world, native = original_enable(
                                world_config=world_config,
                                stage10_config=stage10_config)
                            return world, calibrate_native_birth(native,label)
                        # Patch ONLY the generated I1 module symbol during
                        # fresh construction, restore before physical life.
                        with patch.object(
                            i1_natural_runtime,"enable_natural_sleep_birth",
                            isolated
                        ):
                            actor=birth_i1(**kwargs)
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
                if label != "canonical":
                    configured = actor._stage10_config
                    declared = PROFILES[label]
                    observed = {
                        "fatigue_gain": configured.sleep.fatigue_gain,
                        "sleep_fatigue_recovery":
                            configured.sleep.sleep_fatigue_recovery,
                        "fatigue_weight": configured.sleep.fatigue_weight,
                        "consolidation_weight":
                            configured.sleep.consolidation_weight,
                        "night_weight": configured.sleep.night_weight,
                        "unconsolidated_episode_reference":
                            configured.sleep.unconsolidated_episode_reference,
                        "memory_saturation_reference":
                            configured.sleep.memory_saturation_reference,
                        "intrinsic_weight": configured.intrinsic_weight,
                        "max_consecutive_sleep_steps":
                            configured.sleep.max_consecutive_sleep_steps,
                    }
                    if observed != declared:
                        raise RuntimeError(
                            "experimental birth values not frozen: "
                            +json.dumps({"expected":declared,"actual":observed,
                                         "version":configured.version},
                                        sort_keys=True))
                proof=audit_wal(wal)
                if (proof["independent_hash_chain_verified"] is not True
                    or proof["journal_head"] != life["journal_head"]
                    or proof["journal_entries"] != life["durable_entries"]):
                    raise RuntimeError("individual original WAL custody failed")
                events=[json.loads(line)["causal_event"]
                        for line in wal.read_bytes().splitlines()]
                details=summarize_life(life,events,actor)
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
            "consolidation_commits","accepted_cognitive_uc")}
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
