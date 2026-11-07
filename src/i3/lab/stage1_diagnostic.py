"""One frozen development panel; no cognitive intervention or held-out gate.

Importing this module never imports Mind/World or generates a life. Launch only
on the prospectively pinned source and protocol. Failed lives are not deaths.
"""
from __future__ import annotations

import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path
import subprocess

BASELINE = "046505c34682ef249ec5f6523ec72874442f386d"
PROTOCOL = "i3-stage1-local-development-v1"
FAMILIES = ("stable", "depletion", "pulse")
INDICES = (44, 45)
GENOME_SEEDS = (901, 902)
POLICIES = ("reference", "local_information_v1")
HORIZON = 400


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def digest(value):
    return sha256(canonical(value).encode()).hexdigest()


def plan():
    cases = []
    for f, family in enumerate(FAMILIES):
        for w, index in enumerate(INDICES):
            for g, genome_seed in enumerate(GENOME_SEEDS):
                pair = f"{family}-{index}-g{genome_seed}"
                for policy in POLICIES:
                    cases.append({"case": pair + ":" + policy, "pair": pair,
                                  "family": family, "cohort": "development",
                                  "index": index, "genome_seed": genome_seed,
                                  "life_seed": 7400000 + 1000*f + 10*w + g,
                                  "policy": policy})
    return {"protocol": PROTOCOL, "runtime_baseline": BASELINE,
            "horizon": HORIZON, "maximum_steps": HORIZON * len(cases),
            "cases": cases, "scope": "DESCRIPTIVE_DEVELOPMENT_NOT_GATE",
            "failure_rule": "STOP_AND_ARCHIVE_NO_RETRY_NO_REPLACEMENT",
            "observers": ["full_trace", "full_competition", "resource_acquisition"],
            "no_selection_validation_or_reserve": True}


def _git(*args):
    return subprocess.check_output(["git", *args], text=True).strip()


def validate_launch(expected_sha, expected_protocol):
    """Reject all locks before importing runtime or generating any world."""
    if (type(expected_sha) is not str or len(expected_sha) != 40 or
            any(c not in "0123456789abcdef" for c in expected_sha) or
            _git("rev-parse", "HEAD") != expected_sha):
        raise ValueError("exact prospective source SHA required")
    if expected_protocol != digest(plan()):
        raise ValueError("prospective protocol digest mismatch")
    if _git("status", "--porcelain", "--untracked-files=all", "--", "src/i3", "tests/i3"):
        raise ValueError("dirty I3 source")
    if _git("diff", "--name-only", BASELINE, "HEAD", "--",
            "src/i3/modules", "src/i3/runtime", "src/i3/lab/p2_ecologies.py",
            "src/i3/lab/worldgen.py", "src/i3/lab/stage0_energy.py",
            "src/i3/lab/stage0_revision.py", "config/engine-registry.json"):
        raise ValueError("diagnostic must preserve the declared runtime and observers")


def behavioral_summary(life):
    """Reduce ORIGINAL paid witnesses. No replay, new sensor or inferred score."""
    rows = life["trace"]
    events = life["observer_resource_acquisition"]["steps"]
    competition = life["observer_full_competition"]["steps"]
    if len(rows) != life["steps_lived"] or len(events) != len(rows) or len(competition) != len(rows):
        raise ValueError("incomplete original sidecars")
    funding, actions = Counter(), Counter()
    run = longest = info_options = positive_info = supported_options = 0
    first_failure = first_positive_drink = None
    for row, event, comp in zip(rows, events, competition):
        if (event["step"] != row["t"] or event["action"] != row["action"] or
                comp["physical_action"] != row["action"] or
                event["decision_funding"] != row["info"]["funding"] or
                event["decision_outcome"] != comp["decision_outcome"]):
            raise ValueError("original sidecars disagree")
        status = row["info"]["funding"]
        funding[status] += 1
        actions[row["action"] or "physical_inactivity"] += 1
        if status in ("NO_PROCESSING_BUDGET", "NO_FUNDED_SCORE", "NO_FUNDED_MOTOR"):
            run += 1
            longest = max(longest, run)
            if first_failure is None:
                first_failure = {"step": row["t"], "funding": status,
                                 "body_before": row["funding_phases"]["decision"]["body_before"],
                                 "work": row["funding_phases"]["decision"]["work"]}
        else:
            run = 0
        if first_positive_drink is None and event["positive_water_uptake"]:
            first_positive_drink = row["t"]
        for score in comp["paid_option_scores"]:
            if score.get("score_kind") == "local_expected_distress":
                info_options += 1
                positive_info += score["information_value"] > 1e-12
                supported_options += score["unknown_support_queries"] == 0
    steps = len(rows)
    resource = life["observer_resource_acquisition"]["summary"]
    return {"funding_counts": dict(sorted(funding.items())),
            "actions": dict(sorted(actions.items())),
            "longest_consecutive_unfunded_steps": longest,
            "first_funding_failure": first_failure,
            "first_positive_water_step": first_positive_drink,
            "positive_water_uptakes": resource["positive_water_uptakes"],
            "positive_food_uptakes": resource["positive_food_uptakes"],
            "collected_inventory": resource["collected_inventory"],
            "consumed_inventory": resource["consumed_inventory"],
            "personally_mapped_cells": resource["new_personally_mapped_cells"],
            "paid_information_options": info_options,
            "positive_information_options": positive_info,
            "fully_empirically_supported_options": supported_options,
            "inactive_fraction": actions["physical_inactivity"] / steps if steps else None}


def aggregate(cases):
    """Descriptive sums across all lives, not independent-population inference."""
    groups = {}
    for policy in POLICIES:
        selected = [r for r in cases if r["identity"]["policy"] == policy]
        steps = sum(r["energy"]["steps_lived"] for r in selected)
        paid = {c: sum(r["energy"]["paid"][c] for r in selected)
                for c in ("energy", "vigilance")}
        counts = Counter()
        actions = Counter()
        for r in selected:
            counts.update(r["behavior"]["funding_counts"])
            actions.update(r["behavior"]["actions"])
        groups[policy] = {
            "lives": len(selected),
            "censored": sum(r["energy"]["terminal"] == "censored" for r in selected),
            "dead": sum(r["energy"]["terminal"] == "dead" for r in selected),
            "lived_steps": steps, "paid": paid,
            "paid_per_lived_step": {c: x / steps if steps else None for c, x in paid.items()},
            "funding_counts": dict(sorted(counts.items())),
            "actions": dict(sorted(actions.items())),
            "inactive_fraction": actions["physical_inactivity"] / steps if steps else None,
            "positive_water_uptakes": sum(r["behavior"]["positive_water_uptakes"] for r in selected),
            "positive_food_uptakes": sum(r["behavior"]["positive_food_uptakes"] for r in selected),
            "revision_statuses": dict(Counter(r["revision"]["status"] for r in selected)),
            "scientific_verdict": "NOT_EVALUATED"}
    return groups


def _write_json(path, value):
    path.write_text(canonical(value) + "\n", encoding="utf-8")


def run(output, expected_sha, expected_protocol):
    validate_launch(expected_sha, expected_protocol)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=False)  # Never overwrite previous lives.
    registration = {"plan": plan(), "protocol_sha256": digest(plan()),
                    "execution_sha": expected_sha}
    _write_json(output / "registration.json", registration)
    # Source validation precedes all engine imports and possible births.
    from i3.lab.p2_ecologies import world_for
    from i3.lab.stage0_energy import energy_receipt
    from i3.lab.stage0_revision import revision_receipt
    from i3.modules.genome import generation_zero
    from i3.runtime.life import run_life
    from i3.runtime.provenance import source_snapshot

    source = source_snapshot()
    if source["git_head"] != expected_sha or source["working_tree_dirty"]:
        raise ValueError("source snapshot disagrees with prospective lock")
    _write_json(output / "source.json", source)
    cases = []
    for number, identity in enumerate(plan()["cases"]):
        filename = f"life-{number:02d}.json.gz"
        try:
            spec = world_for(identity["family"], "development", identity["index"])
            genome = generation_zero(identity["genome_seed"])
            life = run_life(genome, spec, identity["life_seed"], HORIZON,
                            protocol=PROTOCOL, decision_policy=identity["policy"],
                            keep_trace=True, observer_mind_digest=True,
                            observer_decision_diagnostics=True,
                            observer_resource_acquisition=True, observer_full_competition=True)
            # Archive full original output BEFORE any reduction can fail.
            raw = (canonical({"identity": identity, "life": life}) + "\n").encode()
            compressed = gzip.compress(raw, mtime=0)
            (output / filename).write_bytes(compressed)
            energy = energy_receipt(life, expected_protocol=PROTOCOL,
                                    expected_source_sha256=source["sha256"])
            revision = revision_receipt(life, expected_protocol=PROTOCOL,
                                        expected_source_sha256=source["sha256"])
            row = {"identity": identity, "original_file": filename,
                   "original_sha256": sha256(compressed).hexdigest(),
                   "original_uncompressed_sha256": sha256(raw).hexdigest(),
                   "energy": energy, "revision": revision,
                   "behavior": behavioral_summary(life)}
            cases.append(row)
            _write_json(output / "cases.json", cases)
            print(canonical({"completed": number + 1, "case": identity["case"],
                             "terminal": energy["terminal"], "steps": energy["steps_lived"]}), flush=True)
        except Exception as exc:
            failure = {"status": "ENGINEERING_FAILURE_NOT_A_DEATH", "case": identity,
                       "completed": len(cases), "error_type": type(exc).__name__,
                       "error": str(exc), "no_retry": True}
            _write_json(output / "failure.json", failure)
            print(canonical(failure), flush=True)
            raise
    # Reconcile matching initial opportunities after all original captures.
    for a, b in zip(cases[::2], cases[1::2]):
        for field in ("world_sha256", "genome_sha256", "life_seed", "horizon"):
            if a["energy"][field] != b["energy"][field]:
                raise ValueError("paired opportunity mismatch: " + field)
    result = {**registration, "source_sha256": source["sha256"],
              "status": "COMPLETE_DESCRIPTIVE_DEVELOPMENT_NOT_GATE",
              "cases": cases, "summary": aggregate(cases)}
    _write_json(output / "results.json", result)
    inventory = {p.name: sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.is_file()}
    _write_json(output / "SHA256.json", inventory)
    print("DIAGNOSTIC_SUMMARY " + canonical(result["summary"]), flush=True)
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--expected-sha")
    parser.add_argument("--expected-protocol")
    args = parser.parse_args()
    if args.plan:
        print(canonical({"plan": plan(), "protocol_sha256": digest(plan())}))
    else:
        if not args.output:
            parser.error("--output required for the frozen single execution")
        run(args.output, args.expected_sha, args.expected_protocol)
