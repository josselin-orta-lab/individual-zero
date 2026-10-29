"""Cold independent A1-P aggregation. No adaptive-learning GO is possible.

Rejects missing/extra/duplicate shards, stale source, invalid pair matching,
M11 tampering, inconsistent physics or unsupported observer provenance.
A1 remains exploratory regardless of sign or size of a paired difference.
"""
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build_i1_fork import generate
from run_i1_eco_a1c import MATRIX, HORIZON, IDENTITIES, SCHEMA, SHA, SEEDS, ROLES

# An already executed single-source cohort: NEVER rerun these eight births.
A1C_ONLY_NEW_SOURCE = True


def aggregate(root, generated, *, source_commit=None, source_run_id=None):
    sys.path.insert(0, str(generated))
    sys.path.insert(0, str(ROOT / "tools"))
    from i1_eco_m11_reader import audited_life_metrics
    from i1_eco_a1_decision_join import (audited_a1_decision_alignment,
        audited_a1_physical_prefix, guard_preintervention_prefix)
    from i1_eco_a1_worlds import a1_world_parameters
    from i1_eco_a1c_mechanism import audited_pair_mechanism
    from i1_eco_a1c_statistics import assess_a1c
    from run_i1_world_preset import load_preset, _birth_parameters

    tool_commit = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
    ).strip()
    if not SHA.fullmatch(tool_commit):
        raise ValueError("invalid exact audit-tool commit")
    if source_commit is not None or source_run_id is not None:
        raise ValueError("A1-C cannot load or alias A1-P archival source")
    commit = tool_commit
    base, preset_digest = load_preset("oasis")
    params, _ = _birth_parameters(base)
    expected_worlds = {
        role: a1_world_parameters(params, role=role)[0]["world_config"]
        for role in ROLES
    }
    rows, issues = [], []
    names = {"a1c-" + role + "-s" + str(seed) + "-" + mode
             for role, seed, mode in MATRIX}
    extras = sorted(p.name for p in root.iterdir()
                    if p.name not in names) if root.is_dir() else []
    if extras:
        issues.append({"scope": "cohort", "problem": "UNREGISTERED_ARTIFACTS",
                       "detail": extras})
    for role, seed, mode in MATRIX:
        name = "a1c-" + role + "-s" + str(seed) + "-" + mode
        identity = IDENTITIES[(role, seed, mode)]
        folder = root / name
        try:
            if not folder.is_dir() or folder.is_symlink():
                raise ValueError("missing or symlinked A1 arm")
            manifest = json.loads((folder / "report.json").read_text())
            if (manifest.get("schema") != SCHEMA
                    or manifest.get("verdict") != "MEASUREMENT_FRAGMENT_READY"
                    or (manifest.get("role"), manifest.get("seed"),
                        manifest.get("mode")) != (role, seed, mode)
                    or manifest.get("identity") != identity
                    or manifest.get("horizon") != HORIZON
                    or manifest.get("adaptive_learning_go") != "NOT_ESTABLISHED"
                    or manifest.get("source_commit") != commit):
                raise ValueError("A1 manifest identity or provenance mismatch")
            life = manifest["life"]
            if (type(life) is not dict
                    or life.get("schema") != SCHEMA
                    or life.get("role") != role
                    or type(life.get("seed")) is not int
                    or life["seed"] != seed
                    or life.get("mode") != mode
                    or life.get("horizon") != HORIZON
                    or life.get("interpretation") !=
                        "CONFIRMATORY_ANALYSIS_PENDING"
                    or life.get("adaptive_learning_go") != "NOT_ESTABLISHED"
                    or life.get("read_provenance") !=
                        "EXTERNAL_OBSERVER_REQUIRES_JOIN_TO_M11"):
                raise ValueError("A1 independent life schema or scope mismatch")
            # Compare only to the effective naturally coupled birth config.
            from i1lab.i1_natural_sleep import enable_natural_sleep_birth
            physical, _ = enable_natural_sleep_birth(
                world_config=expected_worlds[role],
                stage10_config=params["stage10_config"],
            )
            if (life["source_commit"] != commit
                    or life["base_preset_sha256"] != preset_digest
                    or life["identity"] != identity
                    or life["birth_physics_sha256"] != physical.digest()):
                raise ValueError("A1 birth source or physics mismatch")
            # The paired arms must match EACH OTHER *and* their frozen
            # research source. Equality alone could validate two incorrectly
            # born individuals or two identically forged need scales.
            from i1lab.matched_temperament_research import (
                matched_temperament_configuration,
            )
            from i1lab.world import WorldBody
            configured = matched_temperament_configuration(
                params["stage11_config"], life_id=identity,
                world="eco-a1-confirmatory", seed=seed,
            )
            s4 = configured.stage9.stage8.stage7.stage6.stage4
            td = configured.stage9.stage8.td
            expected_td = {
                "version": td.version, "beta": td.beta,
                "eta": td.eta, "lambda_e": td.lambda_e,
            }
            if (life.get("born_temperament") !=
                    configured.temperament_parameters.as_dict()
                    or life.get("born_td") != expected_td
                    or life.get("setpoints") != dict(s4.value_needs.setpoints)
                    or life.get("scales") != dict(
                        s4.value_needs.normalization_scales)):
                raise ValueError(
                    "A1 born temperament, TD, setpoints or scales "
                    "do not match the preregistered research source")
            layout = a1_world_parameters(params, role=role)[0]["layout"]
            pristine = WorldBody(config=physical, layout=layout)
            if (life.get("initial_body") != pristine.body.as_dict()
                    or life.get("initial_inventory") !=
                        dict(pristine.inventory())
                    or life.get("initial_perception") !=
                        pristine.capture_local(t_monde=1).as_dict()):
                raise ValueError(
                    "A1 born physical state or initial perception "
                    "does not match the frozen world")
            database = folder / "life.sqlite"
            if not database.is_file() or database.is_symlink():
                raise ValueError("M11 SQLite missing or symlinked")
            audited = audited_life_metrics(
                path=str(database.resolve()), individual_id=identity,
                horizon=HORIZON, setpoints=life["setpoints"],
                scales=life["scales"],
            )
            if audited != life["audited"]:
                raise ValueError("A1 fragment differs from independent cold M11")
            receipts = life["committed_step_receipts"]
            if (not receipts or len(receipts) != audited["generation"]
                    or receipts[-1]["journal_head"] != audited["journal_head"]
                    or receipts[-1]["journal_count"] != audited["journal_count"]
                    or [x["world_step"] for x in receipts] !=
                       list(range(1, len(receipts) + 1))
                    or [x["generation"] for x in receipts] !=
                       list(range(1, len(receipts) + 1))):
                raise ValueError("A1 step receipt chronology invalid")
            reads = life["read_observations"]
            adapters = life["pending_adapter_observations"]
            if (type(reads) is not list or type(adapters) is not list
                    or any(type(x) is not dict or type(x.get("step")) is not int
                           or x["step"] not in range(1, len(receipts) + 1)
                           or x.get("source") not in (
                               "planning_local", "planning_goal", "stage8_direct")
                           for x in reads)
                    or any(type(x) is not dict or type(x.get("step")) is not int
                           or x["step"] not in range(1, len(receipts) + 1)
                           for x in adapters)):
                raise ValueError("A1 Q observer chronology invalid")
            if (mode == "canonical" and any(x.get("masked") for x in reads)
                    or mode == "td_read_masked" and
                    any(x.get("delivered_status") == "learned"
                        for x in adapters)):
                raise ValueError("A1 masked/unmasked read contract violated")
            alignment = audited_a1_decision_alignment(
                path=str(database.resolve()), identity=identity,
                audited=audited, reads=reads, adapters=adapters,
                mode=mode)
            if life["interpretation"] != "CONFIRMATORY_ANALYSIS_PENDING":
                raise ValueError("A1 overclaimed interpretation")
            rows.append({
                "role": role, "seed": seed, "mode": mode, "identity": identity,
                "source_commit": commit,
                "birth_physics_sha256": life["birth_physics_sha256"],
                "born_temperament": life["born_temperament"],
                "born_td": life["born_td"],
                "initial_perception": life["initial_perception"],
                "initial_body": life["initial_body"],
                "initial_inventory": life["initial_inventory"],
                "setpoints": life["setpoints"], "scales": life["scales"],
                "audited": audited,
                "masked_learned_reads": sum(
                    x["masked"] is True for x in reads),
                "observed_learned_reads": sum(
                    x["original_status"] == "learned" for x in reads),
                "read_provenance": life.get("read_provenance"),
                "decision_alignment": alignment,
                "read_observations": reads,
                "pending_adapter_observations": adapters,
                "database_path": str(database.resolve()),
                "physical_prefix": audited_a1_physical_prefix(
                    path=str(database.resolve()), identity=identity,
                    audited=audited),
            })
        except (OSError, ValueError, KeyError, TypeError, IndexError) as exc:
            issues.append({"scope": name, "problem": "TECHNICAL_AUDIT_FAILURE",
                           "detail": str(exc)[:500]})

    pairs = []
    if not issues and len(rows) == len(MATRIX):
        indexed = {(x["role"], x["seed"], x["mode"]): x for x in rows}
        for role in ROLES:
            for seed in SEEDS:
                a = indexed[(role, seed, "canonical")]
                b = indexed[(role, seed, "td_read_masked")]
                fields = ("birth_physics_sha256", "born_temperament",
                          "born_td", "initial_perception", "initial_body",
                          "initial_inventory", "setpoints", "scales")
                if any(a[f] != b[f] for f in fields):
                    issues.append({"scope": role + ":" + str(seed),
                                   "problem": "UNMATCHED_BIRTH"})
                    continue
                try:
                    prefix_guard = guard_preintervention_prefix(
                        canonical=a["physical_prefix"],
                        masked=b["physical_prefix"],
                        first_masked_step=b["decision_alignment"][
                            "first_masked_read_step"],
                    )
                except ValueError as exc:
                    issues.append({
                        "scope": role + ":" + str(seed),
                        "problem": "INVALID_PREINTERVENTION_PREFIX",
                        "detail": str(exc),
                    })
                    continue
                # A1-C exposure is a conservative, falsifiable M11-anchored
                # mechanism check, not authentication of external Q floats.
                mechanism = audited_pair_mechanism(
                    canonical=a, masked=b, first_masked_step=(
                        b["decision_alignment"]["first_masked_read_step"]))
                ma = a["audited"]["metrics"]
                mb = b["audited"]["metrics"]
                diff = (mb["deficit_area_total"] -
                        ma["deficit_area_total"]) / (4 * HORIZON)
                pairs.append({
                    "role": role, "seed": seed,
                    "preintervention_guard": prefix_guard,
                    "mechanism": mechanism,
                    "mechanism_exposed": mechanism["mechanism_exposed"],
                    "canonical": a["identity"], "masked": b["identity"],
                    "masked_minus_canonical_normalized_deficit": diff,
                    "canonical_dead": ma["mortality"],
                    "masked_dead": mb["mortality"],
                    "observed_masked_learned_reads": b["masked_learned_reads"],
                    "exposure": (
                        "NOT_EXPOSED"
                        if b["masked_learned_reads"] == 0 else
                        "READ_SEEN_CAUSAL_LINK_NOT_ESTABLISHED"
                    ),
                    "verdict": "DESCRIPTIVE_ONLY",
                })
    ready = not issues and len(pairs) == len(ROLES) * len(SEEDS)
    statistics = (assess_a1c([
        {"role": x["role"], "seed": x["seed"],
         "difference": x["masked_minus_canonical_normalized_deficit"],
         "mechanism_exposed": x["mechanism_exposed"]}
        for x in pairs]) if ready else None)
    return {
        "schema": "individual-zero-i1-eco-v1-a1-confirmatory-aggregate/1",
        "verdict": "MEASUREMENT_READY" if ready else "MEASUREMENT_BLOCKED",
        "source_commit": commit,
        "audit_tool_commit": tool_commit,
        "original_run_id": source_run_id,
        "audited_lives": len(rows), "pairs": pairs, "problems": issues,
        "frozen_statistical_analysis": statistics,
        "targeted_status": (statistics["targeted_status"] if ready
                            else "INVALID_EXPERIMENT"),
        "adaptive_learning_go": "NOT_ESTABLISHED",
        "causal_attribution": "NOT_ESTABLISHED",
        "independent_confirmatory_cohort": ready,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifacts", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-commit", default=None,
                        help="Frozen original A1-P SHA for read-only re-audit")
    parser.add_argument("--source-run-id", type=int, default=None,
                        help="Frozen original GitHub Actions run identity")
    args = parser.parse_args()
    generate(args.out.parent / "generated")
    result = aggregate(
        args.artifacts, args.out.parent / "generated",
        source_commit=args.source_commit, source_run_id=args.source_run_id)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    print(json.dumps({"verdict": result["verdict"],
                      "audited_lives": result["audited_lives"],
                      "pairs": len(result["pairs"]),
                      "problems": len(result["problems"])}))
    if result["verdict"] != "MEASUREMENT_READY":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
