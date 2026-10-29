"""Run the preregistered six-world ECO-v1 A0 measurement pilot.

Requires merged ECO-v1 M11 reader (#608). Operator-only, no learning ablation.
Each database is birth-only and never overwritten. Not a causal comparison.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PRESETS = (
    ("oasis", 24), ("foraging", 32), ("blocked-route", 36),
    ("dry-valley", 36), ("hazard-edge", 30), ("empty-land", 38),
)
LABEL = "i1-eco-v1-a0-measurement-only"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--preset", choices=[name for name, _ in PRESETS],
                        help="run exactly one preregistered world (CI shard)")
    options = parser.parse_args()
    destination = options.out.resolve()
    if destination.exists():
        raise SystemExit("A0 output must be a new directory; never overwrite lives")
    destination.mkdir(parents=True)
    sys.path.insert(0, str(ROOT / "scripts"))
    from build_i1_fork import generate
    generated = destination / "generated"
    generate(generated)
    program = r"""
import json
from pathlib import Path
import sys
from i1lab.i1_birth import birth_i1_m11
from i1_eco_m11_reader import audited_life_metrics
from run_i1_world_preset import load_preset, _birth_parameters

name, horizon, out = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
preset, preset_sha256 = load_preset(name)
if horizon != preset["recommended_steps"]:
    raise ValueError("horizon diverges from frozen world preset")
raw, _ = _birth_parameters(preset)
params = dict(raw, diagnostic_sample_cost_uc=1, module_occupancy_cost_uc=1)
identity = "i1:eco:v1:a0:" + name
db_path = str(out / (name + ".sqlite"))
with birth_i1_m11(db_path=db_path, life_id=identity, **params) as actor:
    runtime = actor._runtime
    setpoints = dict(runtime.value_needs.config.setpoints)
    scales = dict(runtime.value_needs.config.normalization_scales)
    physics_sha256 = runtime.world.config.digest()
    for _ in range(horizon):
        receipt = actor.run_step()
        if receipt.status == "dead":
            break
observed = audited_life_metrics(
    path=db_path, individual_id=identity, horizon=horizon,
    setpoints=setpoints, scales=scales)
result = dict(
    preset=name, horizon=horizon, identity=identity,
    preset_sha256=preset_sha256, physics_sha256=physics_sha256,
    setpoints=setpoints, scales=scales, audited=observed,
    interpretation="MEASUREMENT_ONLY_NOT_ADAPTIVE_GO",
)
print("I1_ECO_A0_LIFE=" + json.dumps(result, sort_keys=True))
"""
    env = dict(os.environ,
               PYTHONPATH=os.pathsep.join((
                   str(generated), str(ROOT / "src"), str(ROOT / "tools"))),
               PYTHONDONTWRITEBYTECODE="1")
    selected = tuple((p, h) for p, h in PRESETS
                     if options.preset is None or p == options.preset)
    manifest = {"schema": LABEL, "presets": [p for p, _ in selected],
                "horizons": {p: h for p, h in selected},
                "lives": [], "verdict": "MEASUREMENT_BLOCKED"}
    for name, horizon in selected:
        p = subprocess.run([sys.executable, "-B", "-c", program,
                            name, str(horizon), str(destination)],
                           cwd=ROOT, env=env, capture_output=True, text=True,
                           timeout=900)
        if p.returncode:
            manifest["lives"].append({
                "preset": name, "status": "TECHNICAL_FAILURE",
                "stderr": p.stderr[-4000:], "stdout": p.stdout[-4000:]})
            continue
        reports = [line[len("I1_ECO_A0_LIFE="):]
                   for line in p.stdout.splitlines()
                   if line.startswith("I1_ECO_A0_LIFE=")]
        if len(reports) != 1:
            manifest["lives"].append({
                "preset": name, "status": "BAD_REPORT",
                "stdout": p.stdout[-4000:]})
            continue
        manifest["lives"].append(json.loads(reports[0]))
    if len(manifest["lives"]) == len(selected) and all(
            "audited" in life for life in manifest["lives"]):
        manifest["verdict"] = ("MEASUREMENT_READY" if len(selected) == len(PRESETS)
                               else "MEASUREMENT_FRAGMENT_READY")
    (destination / "report.json").write_text(
        json.dumps(manifest, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(destination / "report.json"),
                      "verdict": manifest["verdict"]}, sort_keys=True))
    if manifest["verdict"] not in ("MEASUREMENT_READY",
                                   "MEASUREMENT_FRAGMENT_READY"):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
