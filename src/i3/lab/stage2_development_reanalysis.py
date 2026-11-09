"""Reanalyse the *existing* sealed DEVELOPMENT 80/81 lives, read-only.

This is not a prospective cohort, a runner, a new Mind/World, an inference
gate, or a claim of independent source/owner attestation. It requires the
historically published digest pins, reopens the archived FILES for reading
only, and verifies all 36 originals against their frozen reduced rows.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
from math import fsum, isclose, isfinite
from pathlib import Path
import json

from . import two_phase_panel as TP

SCHEMA = "i3-stage2-1-development-80-81-reanalysis/v1"
STATUS = "ARCHIVED_LIVES_DESCRIPTIVE_ONLY_NO_SCIENTIFIC_GATE"
SOURCE_SHA = "5d362e226f8e87df226dae5b239e26cc99072a13"
PLAN_SHA = "a28606678d13bb9af18f590c328a63eb9eb82f7130c90656e4f520260d294c92"
MANIFEST_SHA = "c6893bb1b2457890e3d66680f10bf0c14b451e62c2e5c381951f1119f286b76e"
RESULT_SHA = "a6652f4d8cd1f8ccb87d8bf902ecb2eabf68ec0a548b187db140ea61dfc9401b"
TRANSPORT_SHA = "dcada9e221f79b9450a4f05fecd20e60ac6595bb306aa871f29e45aefea0b6f1"
LOCK_SCHEMA = "i3-stage2-1-development-80-81-original-custody/v1"
FAMILIES = ("stable", "depletion", "pulse")
POLICIES = ("reference", "p13_replay_gate_v1",
            "p13_replay_gate_zero_perceived_cost_v1")
FIXED, GATE, ZERO = POLICIES
HORIZON = 400

STUDY_DIR = (Path(__file__).resolve().parents[1] / "docs" / "studies" /
             "stage2-replay-gate-development-80-81")


def _digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _actual_paid(row, channel: str) -> float:
    field = "energy_per_step" if channel == "energy" else "vigilance_per_step"
    return row[field] * row["steps_lived"]


def _original_reduced_row(identity, life):
    """Recompute the old Phase-R row without importing a World runner."""
    n = life["steps_lived"]
    ca = life["cognitive_accounting"]
    sleep = life["actions"].get("dormir", 0)
    return {
        **identity,
        "steps_lived": n,
        "terminal": life["terminal"],
        "death_causes": life["death_causes"],
        "energy_per_step": ca["totals"]["energy"]["paid"] / n,
        "vigilance_per_step": ca["totals"]["vigilance"]["paid"] / n,
        "replays": ca["replays_executed"],
        "sleep_steps": sleep,
        "sleep_fraction": sleep / n,
        "inactive_fraction": ca["inactive_steps"] / n,
        "drinks": life["drinks"],
        "meals": life["meals"],
        "first_drink_step": life["first_drink_step"],
        "mean_step_ms": life["mean_step_ms"],
        "replay_gate": life.get("replay_gate"),
    }


def _expected_identities(plan):
    ns = plan["scientific"]
    return [
        {
            "cohort": "development", "family": family, "index": index,
            "genome_seed": seed, "life_seed": ns["life_seed_base"] +
            1000 * f + 10 * w + g, "policy": policy,
            "block": f"{family}-{index}-g{seed}",
        }
        for f, family in enumerate(FAMILIES)
        for w, index in enumerate((80, 81))
        for g, seed in enumerate((911, 912))
        for policy in POLICIES
    ]


def _check_reduced_row(row):
    if not isinstance(row, dict) or row.get("cohort") != "development":
        raise ValueError("foreign original or damaged reduced receipt")
    n = row.get("steps_lived")
    if type(n) is not int or not 1 <= n <= HORIZON:
        raise ValueError("invalid original lived duration")
    terminal = row.get("terminal")
    if (terminal not in ("dead", "censored") or
            (terminal == "censored" and n != HORIZON) or
            type(row.get("death_causes")) is not list or
            bool(row["death_causes"]) != (terminal == "dead")):
        raise ValueError("death and censoring inconsistent")
    for k in ("energy_per_step", "vigilance_per_step", "inactive_fraction",
              "sleep_fraction"):
        x = row.get(k)
        if type(x) not in (float, int) or not isfinite(x) or x < 0:
            raise ValueError("invalid paid-cognition or activity denominator")
    for k in ("sleep_steps", "replays"):
        v = row.get(k)
        if type(v) is not int or v < 0:
            raise ValueError("invalid sleep or replay count")
    if row["sleep_steps"] > n or row["replays"] > 16 * row["sleep_steps"]:
        raise ValueError("physically impossible replay custody")
    if row["policy"] == FIXED and row["replay_gate"] is not None:
        raise ValueError("FIXED original has replay gate")
    if row["policy"] != FIXED and not isinstance(row["replay_gate"], dict):
        raise ValueError("gated original lacks gate record")


def _paired_rows(rows):
    by_block = {}
    for row in rows:
        key = row["block"]
        if (row.get("family") not in FAMILIES or
                row.get("index") not in (80, 81) or
                row.get("genome_seed") not in (911, 912) or
                row.get("policy") not in POLICIES or
                row.get("block") !=
                f'{row["family"]}-{row["index"]}-g{row["genome_seed"]}'):
            raise ValueError("foreign historical F0 identity")
        cell = by_block.setdefault(key, {})
        if row["policy"] in cell:
            raise ValueError("duplicated historical policy receipt")
        cell[row["policy"]] = row
    if len(by_block) != 12 or any(set(v) != set(POLICIES)
                                  for v in by_block.values()):
        raise ValueError("incomplete historical paired panel")
    return by_block


def _group_stats(groups: list) -> dict:
    n = len(groups)
    if not n:
        raise ValueError("empty analysis subgroup")
    fg = [(group[FIXED], group[GATE], group[ZERO]) for group in groups]
    diffs = [g["steps_lived"] - f["steps_lived"] for f, g, _ in fg]
    zgaps = [z["steps_lived"] - f["steps_lived"] for f, _, z in fg]
    def paid_mean(policy, channel):
        return fsum(_actual_paid(group[policy], channel) for group in groups) / n
    def replay_ratio(policy):
        sleep = sum(group[policy]["sleep_steps"] for group in groups)
        return (sum(group[policy]["replays"] for group in groups) / sleep
                if sleep else None)
    survival = {p: sum(group[p]["terminal"] == "censored" for group in groups)
                for p in POLICIES}
    f_paid, g_paid = paid_mean(FIXED, "energy"), paid_mean(GATE, "energy")
    f_vig, g_vig = paid_mean(FIXED, "vigilance"), paid_mean(GATE, "vigilance")
    return {
        "matched_blocks": n,
        "gate_minus_fixed_mean_lived_steps": fsum(diffs) / n,
        "zero_minus_fixed_mean_lived_steps": fsum(zgaps) / n,
        "gate_minus_fixed_worst_lived_steps": min(diffs),
        "gate_minus_fixed_best_lived_steps": max(diffs),
        "gate_longer_shorter_equal": {
            "longer": sum(v > 0 for v in diffs),
            "shorter": sum(v < 0 for v in diffs),
            "equal": sum(v == 0 for v in diffs),
        },
        "survival_at_400": survival,
        "fixed_only_survived": sum(f["terminal"] == "censored"
                                   and g["terminal"] != "censored" for f, g, _ in fg),
        "gate_only_survived": sum(g["terminal"] == "censored"
                                  and f["terminal"] != "censored" for f, g, _ in fg),
        "mean_paid_cognitive_energy_per_assigned_life": {
            FIXED: f_paid, GATE: g_paid,
        },
        "mean_paid_cognitive_vigilance_per_assigned_life": {
            FIXED: f_vig, GATE: g_vig,
        },
        "gate_minus_fixed_energy_paid_per_assigned_life": g_paid - f_paid,
        "gate_minus_fixed_vigilance_paid_per_assigned_life": g_vig - f_vig,
        "gate_energy_paid_fractional_change_per_assigned_life": (
            (g_paid / f_paid) - 1),
        "gate_vigilance_paid_fractional_change_per_assigned_life": (
            (g_vig / f_vig) - 1),
        "gate_shorter_and_lower_paid_energy": sum(
            g["steps_lived"] < f["steps_lived"] and
            _actual_paid(g, "energy") < _actual_paid(f, "energy")
            for f, g, _ in fg
        ),
        "replays_per_reached_sleep_step": {
            p: replay_ratio(p) for p in POLICIES
        },
    }


def analyze_reduced_rows(rows) -> dict:
    """Only descriptive finite-panel arithmetic; missing cells fail closed."""
    if type(rows) is not list or len(rows) != 36:
        raise ValueError("all 36 archived records required")
    for row in rows:
        _check_reduced_row(row)
    blocks = _paired_rows(rows)
    grouped = [blocks[k] for k in sorted(blocks)]
    all_diffs = [group[GATE]["steps_lived"] - group[FIXED]["steps_lived"]
                 for group in grouped]
    family_exclusions = {
        family: fsum(group[GATE]["steps_lived"] - group[FIXED]["steps_lived"]
                     for group in grouped if group[FIXED]["family"] != family) / 8
        for family in FAMILIES
    }
    leave_one = [(fsum(all_diffs) - diff) / 11 for diff in all_diffs]
    return {
        "status": STATUS, "scientific_verdict": "NOT_ISSUED",
        "new_scientific_lives": 0, "new_worlds_opened": 0,
        "historical_reduced_lives": len(rows), "paired_blocks": len(grouped),
        "overall": _group_stats(grouped),
        "by_family": {
            family: _group_stats([g for g in grouped
                                  if g[FIXED]["family"] == family])
            for family in FAMILIES
        },
        "by_index": {
            str(i): _group_stats([g for g in grouped if g[FIXED]["index"] == i])
            for i in (80, 81)
        },
        "sensitivity_not_inference": {
            "leave_one_block_out_mean_lived_steps_min": min(leave_one),
            "leave_one_block_out_mean_lived_steps_max": max(leave_one),
            "leave_one_family_out_mean_lived_steps": family_exclusions,
        },
        "independent_replications": "NOT_ESTABLISHED",
        "transfer_to_new_ecologies": "NOT_ESTABLISHED",
        "causal_replay_selection_effect": "NOT_IDENTIFIED",
        "no_survival_noninferiority_gate": True,
    }


def analyze_sealed_archive(study_dir=STUDY_DIR) -> dict:
    """Read pinned JSON and all archived gzip originals; no generation route."""
    root = Path(study_dir)
    archive = root / "evidence"
    plan_path = root / "PLAN.json"
    result_path = archive / "SCIENTIFIC_RESULT.json"
    manifest_path = archive / "MANIFEST.json"
    if (_digest(plan_path) != PLAN_SHA or
            _digest(result_path) != RESULT_SHA or
            _digest(manifest_path) != MANIFEST_SHA):
        raise ValueError("frozen historical plan/manifest/result digest changed")
    plan = json.loads(plan_path.read_bytes())
    result = json.loads(result_path.read_bytes())
    lock = json.loads((archive / "SOURCE_LOCK.json").read_bytes())
    expected = _expected_identities(plan)
    if (plan.get("arms") != list(POLICIES) or
            plan.get("families") != list(FAMILIES) or
            plan.get("horizon") != HORIZON or
            plan.get("scientific") != {
                "cohort": "development", "indices": [80, 81],
                "genome_seeds": [911, 912], "life_seed_base": 7540000} or
            len(expected) != 36):
        raise ValueError("historical plan changed")
    if (result.get("status") != "COMPLETE" or
            result.get("scientific_gate") != "NOT_EXECUTED" or
            result.get("no_retry") is not True or
            any(result.get(key) != 36 for key in
                ("planned", "generated", "reduced", "originals_sha256_verified")) or
            result.get("invariant_failures") is None or
            any(type(v) is not int or v != 0
                for v in result["invariant_failures"].values())):
        raise ValueError("incomplete historical science reduction")
    for field, value in (
            ("source_sha", SOURCE_SHA), ("plan_sha256", PLAN_SHA),
            ("manifest_sha256", MANIFEST_SHA),
            ("transport_fingerprint", TRANSPORT_SHA)):
        if result.get(field) != value or lock.get(field) != value:
            raise ValueError("historical source/custody pin mismatch")
    if (lock.get("schema") != LOCK_SCHEMA or lock.get("no_retry") is not True or
            lock.get("scientific_gate") != "NOT_EXECUTED" or
            lock.get("generated") != 36 or
            lock.get("originals_sha256_verified") != 36):
        raise ValueError("historical source lock invalid")
    manifest = json.loads(manifest_path.read_bytes())
    if (manifest.get("generated") != 36 or manifest.get("planned") != 36 or
            manifest.get("failure") is not None or
            len(manifest.get("files", ())) != 36 or
            len(list(archive.glob("life-*.json.gz"))) != 36):
        raise ValueError("original manifest incomplete or extra originals")
    rows = result.get("rows")
    if type(rows) is not list or len(rows) != 36:
        raise ValueError("historical reduced rows not complete")
    originals = list(TP.load_sealed(archive))
    if len(originals) != 36:
        raise ValueError("historical original count changed")
    for i, ((identity, life), frozen, expected_id) in enumerate(
            zip(originals, rows, expected)):
        if (identity != expected_id or
                manifest["files"][i].get("identity") != expected_id or
                frozen != _original_reduced_row(identity, life)):
            raise ValueError(f"historical original-to-reduction mismatch at {i}")
    analysis = analyze_reduced_rows(rows)
    analysis["schema"] = SCHEMA
    analysis["source_pin_consistency"] = "MATCHES_PUBLISHED_HISTORICAL_PINS"
    analysis["archive_gzip_sha256_verified_this_pass"] = len(originals)
    analysis["originals_vs_frozen_reductions_matched"] = len(originals)
    analysis["external_pre_exposure_authority"] = "NOT_INDEPENDENTLY_REATTESTED"
    return analysis


def main():
    print(json.dumps(analyze_sealed_archive(), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
