"""Prospective A1-P: run ONE of eight preregistered independent mortal lives.

Only after the preregistration and control instruments are merged and exact
HEAD is green. This file defines a launchable procedure, but its mere presence
does not authorize a pilot verdict. Preserve every technical failure and death.
No forced commands, TD update ablation, state cloning, or cognition changes.
"""
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ROLES = ("native", "reversed")
SEEDS = (1, 2)
MODES = ("canonical", "td_read_masked")
HORIZON = 48
SCHEMA = "individual-zero-i1-eco-v1-a1-pilot-fragment/1"
MATRIX = tuple((role, seed, mode) for role in ROLES
               for seed in SEEDS for mode in MODES)
# Opaque born IDs cannot reveal the hidden nutritional role or research arm.
IDENTITIES = {row: "i1:eco:a1:pilot:n%04d" % (i + 1)
              for i, row in enumerate(MATRIX)}
SHA = re.compile(r"[0-9a-f]{40}\Z")


def _validated_fragment(report, *, role, seed, mode, source_sha):
    if type(report) is not dict or report.get("schema") != SCHEMA:
        raise ValueError("invalid A1 fragment schema")
    if (report.get("role") != role or report.get("seed") != seed
            or report.get("mode") != mode or report.get("horizon") != HORIZON
            or report.get("identity") != IDENTITIES[(role, seed, mode)]
            or report.get("source_commit") != source_sha
            or report.get("adaptive_learning_go") != "NOT_ESTABLISHED"
            or report.get("interpretation") != "EXPLORATORY_NOT_CONFIRMATORY"):
        raise ValueError("A1 identity, birth, source or scope mismatch")
    audited = report.get("audited")
    if (type(audited) is not dict or
            audited.get("custody") != "audited_SQLite_M11_read_only" or
            audited.get("causal_performance") != "NOT_ESTABLISHED" or
            audited.get("individual_id") != report["identity"]):
        raise ValueError("missing independent M11 receipt")
    if (type(report.get("read_observations")) is not list or
            type(report.get("pending_adapter_observations")) is not list or
            type(report.get("committed_step_receipts")) is not list):
        raise ValueError("A1 read or committed-step evidence missing")
    receipts = report["committed_step_receipts"]
    if (not receipts or len(receipts) > HORIZON or
            receipts[-1]["generation"] != audited.get("generation") or
            receipts[-1]["journal_head"] != audited.get("journal_head")):
        raise ValueError("A1 M11 generation custody mismatch")
    if (type(report.get("born_temperament")) is not dict
            or type(report.get("initial_perception")) is not dict
            or type(report.get("setpoints")) is not dict
            or type(report.get("scales")) is not dict):
        raise ValueError("A1 born state evidence missing")
    return report


_PROGRAM = r"""
import json
from pathlib import Path
import subprocess
import sys

from i1lab.i1_birth import birth_i1_m11
from i1_eco_m11_reader import audited_life_metrics
from i1_eco_a1_matched_birth import a1_matched_temperament_birth
from i1_eco_a1_td_mask import a1_decision_read_scope
from i1_eco_a1_worlds import a1_world_parameters
from run_i1_world_preset import load_preset, _birth_parameters
from run_i1_eco_a1 import SCHEMA, HORIZON, IDENTITIES

role, seed, mode, output = sys.argv[1], int(sys.argv[2]), sys.argv[3], Path(sys.argv[4])
source_sha = subprocess.check_output(
    ["git", "rev-parse", "HEAD"], text=True).strip()
base, preset_sha = load_preset("oasis")
parameters, _ = _birth_parameters(base)
parameters, local = a1_world_parameters(parameters, role=role)
parameters = {**parameters, "diagnostic_sample_cost_uc": 1,
              "module_occupancy_cost_uc": 1}
identity = IDENTITIES[(role, seed, mode)]
sqlite_path = str((output / "life.sqlite").resolve())
reads, adapters, receipts = [], [], []
with a1_matched_temperament_birth(life_id=identity, seed=seed):
    actor = birth_i1_m11(db_path=sqlite_path, life_id=identity, **parameters)
with actor:
    born = actor._runtime
    config = born._stage11_config
    td = born.q_active.config
    born_td = {
        "version": td.version, "beta": td.beta,
        "eta": td.eta, "lambda_e": td.lambda_e,
    }
    initial_perception = born.world.capture_local(t_monde=1).as_dict()
    if local != initial_perception:
        raise RuntimeError("A1 born visibility differs from operator preregistration")
    birth_physics = born.world.config.digest()
    birth_berry_effects = {
        k: {"food_gain": v.food_gain, "integrity_delta": v.integrity_delta}
        for k, v in born.world.config.berry_effects.items()
    }
    expected_effects = parameters["world_config"].berry_effects
    if born.world.config.berry_effects != expected_effects:
        raise RuntimeError("A1 birth applied unregistered berry mutation")
    born_temperament = born.temperament_parameters.as_dict()
    setpoints = dict(born.value_needs.config.setpoints)
    scales = dict(born.value_needs.config.normalization_scales)
    initial_body = dict(born.world.body.as_dict())
    initial_inventory = dict(born.world.inventory())
    with a1_decision_read_scope(mode=mode, reads=reads, adapters=adapters):
        for _ in range(HORIZON):
            rc = actor.run_step()
            receipts.append({
                "world_step": rc.world_step, "generation": rc.generation,
                "status": rc.status, "journal_head": rc.journal_head,
                "journal_count": rc.journal_count,
            })
            if rc.status == "dead":
                break

audited = audited_life_metrics(
    path=sqlite_path, individual_id=identity, horizon=HORIZON,
    setpoints=setpoints, scales=scales,
)
if audited["generation"] != len(receipts):
    raise RuntimeError("A1 birth and audited M11 generation differ")
if (audited["journal_head"] != receipts[-1]["journal_head"]
        or audited["metrics"]["observed_steps"] != len(receipts)):
    raise RuntimeError("A1 M11 head or physical trajectory differs")
if any(x["step"] > audited["generation"] for x in reads + adapters):
    raise RuntimeError("A1 read observer contains an uncommitted step")
if any(x["masked"] for x in reads) and mode == "canonical":
    raise RuntimeError("A1 canonical decision reads were masked")
if (mode == "td_read_masked" and
        any(x["delivered_status"] == "learned" for x in adapters)):
    raise RuntimeError("A1 Stage8 pending adapter leaked learned Q")
if (len(receipts) < HORIZON and
        (audited["metrics"]["mortality"] is not True or
         receipts[-1]["status"] != "dead")):
    raise RuntimeError("A1 short unaccounted life")
report = {
    "schema": SCHEMA,
    "role": role, "seed": seed, "mode": mode,
    "horizon": HORIZON, "identity": identity,
    "source_commit": source_sha,
    "base_preset_sha256": preset_sha,
    "birth_physics_sha256": birth_physics,
    "born_temperament": born_temperament,
    "born_td": born_td,
    "setpoints": setpoints, "scales": scales,
    "initial_perception": initial_perception,
    "initial_body": initial_body,
    "initial_inventory": initial_inventory,
    "read_observations": reads,
    "pending_adapter_observations": adapters,
    "read_provenance": "EXTERNAL_OBSERVER_REQUIRES_JOIN_TO_M11",
    "committed_step_receipts": receipts,
    "audited": audited,
    "interpretation": "EXPLORATORY_NOT_CONFIRMATORY",
    "adaptive_learning_go": "NOT_ESTABLISHED",
}
print("I1_ECO_A1_LIFE=" + json.dumps(report, sort_keys=True, allow_nan=False))
"""


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=ROLES, required=True)
    parser.add_argument("--seed", type=int, choices=SEEDS, required=True)
    parser.add_argument("--mode", choices=MODES, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    destination = args.out.resolve()
    if destination.exists():
        raise SystemExit("A1 output exists: never overwrite a mortal life")
    destination.mkdir(parents=True)
    manifest = {
        "schema": SCHEMA, "role": args.role, "seed": args.seed,
        "mode": args.mode, "horizon": HORIZON,
        "identity": IDENTITIES[(args.role, args.seed, args.mode)],
        "verdict": "MEASUREMENT_BLOCKED",
        "adaptive_learning_go": "NOT_ESTABLISHED",
    }
    try:
        code_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        if not SHA.fullmatch(code_sha):
            raise ValueError("invalid exact source commit")
        sys.path.insert(0, str(ROOT / "scripts"))
        from build_i1_fork import generate
        generated = destination / "generated"
        generate(generated)
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                   PYTHONPATH=os.pathsep.join((
                       str(generated), str(ROOT / "src"), str(ROOT / "tools")
                   )))
        job = subprocess.run(
            [sys.executable, "-B", "-c", _PROGRAM,
             args.role, str(args.seed), args.mode, str(destination)],
            cwd=ROOT, env=env, text=True, capture_output=True, timeout=900,
        )
        if job.returncode:
            raise RuntimeError(
                "child_process_failed exit=" + str(job.returncode)
                + " stderr=" + job.stderr[-5000:]
                + " stdout=" + job.stdout[-1500:])
        lines = [line[len("I1_ECO_A1_LIFE="):]
                 for line in job.stdout.splitlines()
                 if line.startswith("I1_ECO_A1_LIFE=")]
        if len(lines) != 1:
            raise ValueError("A1 missing or duplicated physical life receipt")
        life = _validated_fragment(
            json.loads(lines[0]), role=args.role, seed=args.seed,
            mode=args.mode, source_sha=code_sha,
        )
        manifest.update(
            verdict="MEASUREMENT_FRAGMENT_READY", source_commit=code_sha,
            life=life,
        )
    except (OSError, ValueError, RuntimeError,
            subprocess.TimeoutExpired) as exc:
        manifest.update(
            verdict="TECHNICAL_AUDIT_FAILURE",
            detail=str(exc)[-5500:],
        )
    (destination / "report.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "role": args.role, "seed": args.seed, "mode": args.mode,
        "verdict": manifest["verdict"],
    }, sort_keys=True))
    if manifest["verdict"] != "MEASUREMENT_FRAGMENT_READY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
