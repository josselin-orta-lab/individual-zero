#!/usr/bin/env python3
"""External population calibration: frozen prenatal parameters, natural I1 birth.

No learning reward edits, motor commands, sleep overrides, body changes, or
post-birth control. Optimizer scores *outcomes*, not TD reward.
"""
from __future__ import annotations
import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import random
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "tools"), str(ROOT / "scripts"), str(ROOT / "src")]
from run_i1_world_preset import load_preset, _birth_parameters
from build_i1_fork import generate

# First stage intentionally tiny: only numerical owner configs, no new rules.
BOUNDS = {
    "competition_threshold": (0.30, 0.65),
    "competition_gain": (0.75, 1.25),
}
BASELINE = dict(competition_threshold=0.50, competition_gain=1.00)
WORLDS = ("oasis", "foraging")


def candidates(count=6):
    """Reproducible bounded sampling with a true untouched native control."""
    if type(count) is not int or not 2 <= count <= 24:
        raise ValueError("candidate count out of range")
    rnd = random.Random(20261018)
    result = [dict(BASELINE)]
    for _ in range(count-1):
        result.append({k: round(rnd.uniform(*bounds), 5)
                       for k, bounds in BOUNDS.items()})
    return result


def prenatal_stage4(params, values, label):
    """Only research candidates change immutable configurations before birth."""
    if label == 0:
        if values != BASELINE:
            raise AssertionError("native control must be untouched")
        return params
    if set(values) != set(BOUNDS) or any(
        type(values[k]) not in (float, int) or not BOUNDS[k][0] <= values[k] <= BOUNDS[k][1]
        for k in BOUNDS
    ):
        raise ValueError("illegal prenatal numerical parameter")
    config = params["stage11_config"]
    s9 = config.stage9
    s8 = s9.stage8
    s7 = s8.stage7
    s6 = s7.stage6
    s4 = s6.stage4
    tag = "+population-prenatal-v1:" + str(label)
    stage4 = replace(s4,
        version=s4.version+tag,
        competition=replace(s4.competition, version=s4.competition.version+tag,
                            base_threshold=values["competition_threshold"],
                            gain=values["competition_gain"]))
    stage9 = replace(s9,version=s9.version+tag,
        stage8=replace(s8,version=s8.version+tag,
            stage7=replace(s7,version=s7.version+tag,
                stage6=replace(s6,version=s6.version+tag,stage4=stage4))))
    s11 = replace(config,version=config.version+tag,stage9=stage9)
    s10 = replace(params["stage10_config"],
                  version=params["stage10_config"].version+tag,stage9=stage9)
    s11.validate()
    s10.validate()
    return {**params,"stage11_config":s11,"stage10_config":s10}


def run(candidate, world, seed, steps, out, count=6):
    if candidate not in range(count) or world not in WORLDS or type(seed) is not int:
        raise ValueError("unknown candidate, world or seed")
    if type(steps) is not int or not 1 <= steps <= 1000:
        raise ValueError("initial horizon out of range")
    out = Path(out).resolve()
    if out.exists():
        raise FileExistsError("refusing to overwrite any life")
    out.mkdir(parents=True)
    source_sha = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    values = candidates(count)[candidate]
    report = {"status":"TECHNICAL_FAILURE","scientific_verdict":"NOT_EVALUATED",
              "candidate":candidate,"parameters":values,"world":world,"seed":seed,
              "git_sha":source_sha,"steps_requested":steps}
    try:
        with TemporaryDirectory() as tmp:
            build = Path(tmp)/"generated"
            generate(build)
            sys.path.insert(0,str(build))
            from i1lab.i1_birth import birth_i1
            from i1lab.journal import HashChainedJournal
            from audit_i1_birth_capabilities import audit_birth
            preset, digest = load_preset(world)
            params, _ = _birth_parameters(preset)
            original_world_digest = params["world_config"].digest()
            params = prenatal_stage4(params, values, candidate)
            # Same life ID -> same deterministic temperament in every candidate.
            life_id = f"i1:population:{world}:{seed}"
            wal = out/"life.wal"
            life = birth_i1(life_id=life_id,wal_path=str(wal),**params)
            birth_manifest = audit_birth(life, expected_competition={
                'base_threshold': values['competition_threshold'],
                'gain': values['competition_gain'],
            })
            born = life.goal_manager._config
            owner_comp = life.competition._config
            if (born.replacement_hysteresis, born.critical_pressure) != (0.04,0.35):
                raise AssertionError("natural GoalManager invariant violated")
            if (owner_comp.base_threshold != values["competition_threshold"]
                    or owner_comp.gain != values["competition_gain"]):
                raise AssertionError("incorrect effective prenatal Competition")
            init_td = life._stage8_config.td
            initial_physics = life.world.config.digest()
            actual = []
            transitions = []
            previous_goal = None
            cumulative_shortage = 0.0
            lowest_integrity = 100.0
            for _ in range(steps):
                receipt = life.run_step()
                body = dict(life.world.telemetry())
                cumulative_shortage += sum(
                    (100.0 - max(0.0, min(100.0, float(body[key])))) / 100.0
                    for key in ("water", "food", "energy", "integrity")
                ) / 4.0
                lowest_integrity = min(lowest_integrity, float(body["integrity"]))
                goal = life.goal_manager.active_goal
                kind = None if goal is None else goal.goal_type
                if previous_goal is not None and kind is not None and previous_goal != kind:
                    transitions.append([previous_goal,kind,life.scheduler.t_monde])
                previous_goal = kind
                actual.append({
                    "step":life.scheduler.t_monde,
                    "execution":receipt.execution_status,
                    "action":receipt.command_primitive,
                    "body":body,
                    "goal":kind,
                    "journal_head":life.journal.head_hash,
                })
                if (life.goal_manager._config is not born or
                        life.competition._config is not owner_comp
                        or life._stage8_config.td is not init_td
                        or life.world.config.digest() != initial_physics):
                    raise AssertionError("owners or physics changed during one life")
                if receipt.execution_status == "dead":
                    break
            if not life.journal.verify():
                raise AssertionError("live WAL integrity failure")
            audit = HashChainedJournal.audit_durable_wal(str(wal))
            if audit["head_hash"] != life.journal.head_hash:
                raise AssertionError("durable WAL integrity failure")
            actions = Counter(t["action"] for t in actual)
            zero = {k:sum(t["body"][k] <= 0 for t in actual)
                    for k in ("water","food","energy")}
            physical_steps = len(actual)
            survival_fraction = physical_steps / steps
            # Physical deprivation is continuous; a brief critical deficit
            # matters even if the body variable has not reached exactly zero.
            # This objective is external ONLY; I1 TD reward is unchanged.
            mean_shortage = cumulative_shortage / physical_steps
            score = 0.7*survival_fraction + 0.3*(1.0-mean_shortage)
            report.update({
                "status":"COMPLETED_WITHOUT_SCIENTIFIC_VERDICT",
                "life_id":life_id,"world_sha256":digest,
                "world_config_digest_before_birth":original_world_digest,
                "effective_physics_digest":initial_physics,
                "effective_goal":{"hysteresis":born.replacement_hysteresis,
                                  "critical":born.critical_pressure,
                                  "version":born.version},
                "effective_competition":{
                    "threshold":owner_comp.base_threshold,
                    "gain":owner_comp.gain,"version":owner_comp.version},
                "effective_td":{"version":init_td.version,"lambda_e":init_td.lambda_e,
                                "eta":init_td.eta},
                "observed_steps":physical_steps,
                "lifecycle":life.stage3.substrate.mortal_status.value,
                "zero_steps":zero,
                "actions":dict(actions),
                "goal_type_transitions":transitions,
                "score":round(score,9),
                "mean_normalized_shortage":round(mean_shortage,9),
                "lowest_integrity":lowest_integrity,
                "birth_capability_sha256":birth_manifest["birth_profile_sha256"],
                "birth_capability_manifest":birth_manifest,
                "wal_entries":audit["verified_entries"],
                "wal_head":audit["head_hash"],
                "trajectory":actual,
            })
    finally:
        (out/"report.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    return report


def aggregate(paths):
    reports=[json.loads(Path(p).read_text()) for p in paths]
    if not reports or any(r["status"]!="COMPLETED_WITHOUT_SCIENTIFIC_VERDICT" for r in reports):
        raise ValueError("missing or failed life")
    sha={r["git_sha"] for r in reports}
    if len(sha)!=1:
        raise ValueError("mixed code SHAs")
    groups={}
    for r in reports:
        groups.setdefault(r["candidate"],[]).append(r)
    sets=[{(x["world"],x["seed"]) for x in xs} for xs in groups.values()]
    if (not sets or any(set_ != sets[0] for set_ in sets)
            or any(len(set_) != len(xs) for set_,xs in zip(sets,groups.values()))
            or any(w not in WORLDS for w,s in sets[0])):

        raise ValueError("candidate worlds and seeds not paired")
    rows=[]
    for index, xs in sorted(groups.items()):
        scores=sorted(x["score"] for x in xs)
        rows.append({"candidate":index,"parameters":xs[0]["parameters"],
                     "mean_score":round(sum(scores)/len(scores),6),
                     "worst_score":scores[0],
                     "deaths":sum(x["lifecycle"]=="dead" for x in xs),
                     "mean_lifetime":sum(x["observed_steps"] for x in xs)/len(xs)})
    # Distinct held-out seeds and worlds required before scientific promotion.
    rows.sort(key=lambda x:(-x["worst_score"],-x["mean_score"],x["candidate"]))
    return {"source_sha":next(iter(sha)),"status":"TRAINING_RANKING_ONLY",
            "scientific_verdict":"NOT_EVALUATED","ranking":rows}


def main():
    parser=argparse.ArgumentParser()
    sub=parser.add_subparsers(dest="task",required=True)
    e=sub.add_parser("evaluate")
    e.add_argument("--candidate",type=int,required=True)
    e.add_argument("--world",choices=WORLDS,required=True)
    e.add_argument("--seed",type=int,required=True)
    e.add_argument("--steps",type=int,default=120)
    e.add_argument("--output-dir",type=Path,required=True)
    e.add_argument("--count",type=int,default=6)
    a=sub.add_parser("aggregate")
    a.add_argument("reports",nargs="+",type=Path)
    t=parser.parse_args()
    if t.task=="evaluate":
        report=run(t.candidate,t.world,t.seed,t.steps,t.output_dir,t.count)
        print(json.dumps({k:report[k] for k in
          ("status","candidate","world","seed","lifecycle","observed_steps","score")}))
    else:
        print(json.dumps(aggregate(t.reports),indent=2))


if __name__=="__main__":
    main()
