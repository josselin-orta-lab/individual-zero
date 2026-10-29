"""Aggregate exactly the six preregistered ECO-v1 A0 world fragments.

Operator-only technical audit. All six valid M11 files are mandatory.
A0 is measurement readiness, never a causal or adaptive-learning GO.
"""
import argparse
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate
from run_i1_world_preset import _birth_parameters, load_preset

from run_i1_eco_a0 import LABEL, PRESETS

GIT_SHA = re.compile(r"[0-9a-f]{40}\Z")
M11_HEAD = re.compile(r"[0-9a-f]{64}\Z")


def aggregate(root, generated):
    sys.path.insert(0, str(generated))
    sys.path.insert(0, str(ROOT / "tools"))
    from i1_eco_m11_reader import audited_life_metrics
    from i1lab.sqlite_life_store import RecoveryBlocked

    code_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if not GIT_SHA.fullmatch(code_sha):
        raise ValueError("invalid checked-out experiment source revision")
    rows = []
    problems = []
    for name, horizon in PRESETS:
        entries = sorted(root.glob("i1-eco-a0-" + name + "-*"))
        if len(entries) != 1 or not entries[0].is_dir():
            problems.append({"preset": name, "problem": "MISSING_OR_DUPLICATED_ARTIFACT"})
            continue
        directory = entries[0]
        path = directory / "report.json"
        sqlite_path = directory / (name + ".sqlite")
        try:
            fragment = json.loads(path.read_text(encoding="utf-8"))
            if (fragment["schema"] != LABEL
                    or fragment["presets"] != [name]
                    or fragment["horizons"] != {name: horizon}
                    or fragment["verdict"] != "MEASUREMENT_FRAGMENT_READY"
                    or len(fragment["lives"]) != 1):
                raise ValueError("invalid fragment manifest")
            life = fragment["lives"][0]
            expected_identity = "i1:eco:v1:a0:" + name
            if (life["preset"] != name or life["horizon"] != horizon
                    or life["identity"] != expected_identity
                    or life["interpretation"] != "MEASUREMENT_ONLY_NOT_ADAPTIVE_GO"):
                raise ValueError("life identity, horizon or scope mismatch")
            preset, digest = load_preset(name)
            physics, _ = _birth_parameters(preset)
            native_needs = (physics["stage11_config"].stage9.stage8.stage7
                            .stage6.stage4.value_needs)
            if (life["preset_sha256"] != digest
                    or life["physics_sha256"] != physics["world_config"].digest()
                    or life.get("source_commit") != code_sha):
                raise ValueError("source commit, preset or physics digest mismatch")
            if (life.get("setpoints") != dict(native_needs.setpoints)
                    or life.get("scales") != dict(native_needs.normalization_scales)):
                raise ValueError("scoring parameters disagree with native birth configuration")
            if not sqlite_path.is_file() or sqlite_path.is_symlink():
                raise ValueError("missing or symlinked M11 evidence")
            for key in ("journal_head", "journal_count", "generation"):
                if key not in life["audited"]:
                    raise ValueError("missing custody field " + key)
            if not M11_HEAD.fullmatch(life["audited"]["journal_head"]):
                raise ValueError("invalid journal head")
            independently = audited_life_metrics(
                path=str(sqlite_path.resolve()),
                individual_id=expected_identity, horizon=horizon,
                setpoints=life["setpoints"], scales=life["scales"])
            if life["audited"] != independently:
                raise ValueError("reported measurements differ from cold M11")
            metrics = independently["metrics"]
            rows.append({
                "preset": name,
                "identity": expected_identity,
                "horizon": horizon,
                "status": "dead" if metrics["mortality"] else "active",
                "restricted_life_steps": metrics["restricted_life_steps"],
                "deficit_area_by_need": metrics["deficit_area_by_need"],
                "deficit_area_total": metrics["deficit_area_total"],
                "sleep_fraction": metrics["sleep_fraction"],
                "actions": metrics["actions"],
                "journal_head": independently["journal_head"],
                "journal_count": independently["journal_count"],
                "interpretation": "DESCRIPTIVE_ONLY",
            })
        except (OSError, KeyError, TypeError, ValueError, IndexError,
                sqlite3.DatabaseError, RecoveryBlocked) as exc:
            problems.append({"preset": name, "problem": "TECHNICAL_AUDIT_FAILURE",
                             "detail": str(exc)[:500]})
    ready = len(rows) == len(PRESETS) and not problems
    return {
        "schema": "i1-eco-v1-a0-six-world-aggregate/1",
        "verdict": "MEASUREMENT_READY" if ready else "MEASUREMENT_BLOCKED",
        "presets_expected": [n for n, _ in PRESETS],
        "audited_lives": rows,
        "problems": problems,
        "adaptive_learning_go": "NOT_ESTABLISHED",
        "independent_cohort": False,
        "source_commit": code_sha,
        "td_masked_comparator": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    generated = args.out.parent / "i1-eco-a0-aggregate-generated"
    generate(generated)
    result = aggregate(args.artifacts, generated)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n",
                        encoding="utf-8")
    print(json.dumps({"verdict": result["verdict"], "audited": len(result["audited_lives"]),
                      "failures": len(result["problems"])}))
    if result["verdict"] != "MEASUREMENT_READY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
