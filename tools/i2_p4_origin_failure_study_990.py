#!/usr/bin/env python3
"""#990: explicit, prospective P4 cohort runner. NEVER invoked by ordinary CI.

One execution, six independently born native lives, original SQLite custody.
No new I2 policy, action script, reward oracle, engine activation or M11.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import re
import sqlite3
import subprocess
import sys
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_spatial_world import BORN_SITE, destination, site_after
from i2.runtime.native_paid_cycle import (
    NativePaidI2, NEED_FAILURE_EXPLORATION_EVIDENCE,
    ORIGIN_NOVELTY_EVIDENCE,
)
from tools.i2_native_completed_life_archive import archive_completed_life
from tools.i2_native_need_failure_diagnostic import diagnose_existing_life

PROTOCOL = "i2-P4-origin-failure-unknown-alternative-990-v1"
PREREGISTERED_ISSUE = "https://github.com/josselin-orta-lab/individual-zero/issues/990"
MAX_STEPS = 128
WORLD_HARMS = (("alternative-no-injury", 0.0),
               ("alternative-injures", -12.0))
ARMS = (("innate-only", False, False),
        ("learning-control", True, False),
        ("failed-need-exploration", True, True))


def frozen_cells():
    """Six ordered, immutable-to-this-protocol research conditions."""
    return tuple(
        (world, injury, arm, learning, factor)
        for world, injury in WORLD_HARMS
        for arm, learning, factor in ARMS
    )


def frozen_birth_kwargs(cell):
    """Exact prospective laws, with NO behavior inferred from prior runs."""
    world, injury, arm, learning, factor = cell
    if cell not in frozen_cells():
        raise ValueError("undeclared prospective P4 cell")
    return dict(
        body=Body(78, 46, 44, 94),
        temperament=BirthTemperament(0, .5, .3, 0, 0),
        learning=learning, need_failure_exploration=factor,
        spatial_world=True, ordinary_water_site="camp",
        water_stock=2, water_restock_every=10, drink_water_gain=35.0,
        ordinary_food_site="camp", food_stock=1, food_restock_every=8,
        berry_food_gain=0.0, berry_integrity_delta=0.0,
        second_food_site="passage", second_food_stock=1,
        second_food_restock_every=8, second_berry_food_gain=20.0,
        second_berry_integrity_delta=injury,
        max_steps=MAX_STEPS, uc=1000,
        origin_novelty_tie=False, target_food_credit_enabled=False,
        contextual_movement_credit=False, place_return_tie=False,
        evidence_tie_exploration=False, sleep_consolidation=False,
        purpose_followthrough=False, whole_body_place_tie=False,
    )


def _write_json(path, item):
    path.write_text(
        json.dumps(item, sort_keys=True, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _require_exact_clean_checkout(expected_head):
    if not re.fullmatch(r"[0-9a-f]{40}", expected_head):
        raise ValueError("full 40-character pinned Git HEAD required")
    actual = subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    dirty = subprocess.check_output(
        ["git", "status", "--porcelain", "--untracked-files=no"],
        cwd=ROOT, text=True).strip()
    if actual != expected_head or dirty:
        raise ValueError("exact clean source-locked Git HEAD required")


def signed_trace(path):
    """Researcher-only readout AFTER independent completed native cold audit.

    Original event_json is retained verbatim as a parsed event alongside
    the separate original SQLite journal. This does not reveal remote stock
    to the individual or reconstruct counterfactual consequences.
    """
    cold = NativePaidI2.inspect(path).audit()
    if not (cold["terminal"] or cold["revision"] == MAX_STEPS):
        raise ValueError("never classify an incomplete native life")
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as db:
        records = db.execute(
            "SELECT p.seq,p.admitted_action,p.before_json,p.after_json,"
            "p.terminal,p.admission_ref,e.event_json "
            "FROM native_physical_events p JOIN events e ON p.seq=e.seq "
            "ORDER BY p.seq").fetchall()
    if len(records) != cold["revision"]:
        raise ValueError("cold-audit/readout revision mismatch")
    site = BORN_SITE
    trace = []
    for tick, action, before_json, after_json, terminal, admission, event_json in records:
        if tick != len(trace) + 1:
            raise ValueError("nonsequential signed native history")
        before, after = json.loads(before_json), json.loads(after_json)
        event = json.loads(event_json)
        scores = {}
        if event.get("frame") is not None:
            refs = {x["candidate_ref"]: x["semantic_ref"]
                    for x in event["frame"]["candidates"]}
            scores = {refs[x["candidate_ref"]]: {
                "value": x["value"], "evidence_ref": x["evidence_ref"]}
                for x in event["advice"]["values"]}
        site_before = site
        if destination(action) is not None:
            site = site_after(site, action)
        offers = event["claim"]["capture"]["accessible_semantics"]
        if action != "NO_ACTION" and action not in offers:
            raise ValueError("claimed action was not locally offered")
        trace.append({
            "tick": tick, "site_before": site_before, "site_after": site,
            "action": action, "offered": offers, "before": before,
            "after": after, "terminal": bool(terminal),
            "admission_ref": admission,
            "food_meal": action == "manger",
            "need_relevant_food_failure": bool(
                action == "manger" and before["food"] < 70 and
                after["food"] <= before["food"]),
            "factor_tagged": any(
                NEED_FAILURE_EXPLORATION_EVIDENCE in x["evidence_ref"]
                for x in scores.values()),
            "origin_novelty_tagged": any(
                ORIGIN_NOVELTY_EVIDENCE in x["evidence_ref"]
                for x in scores.values()),
            "scores": scores, "recorded_event": event,
        })
    if trace and (trace[-1]["site_after"] != cold["site"] or
                  trace[-1]["after"] != cold["body"]):
        raise ValueError("readout does not match cold-audited final state")
    return trace


def first_matched_factor_divergence(control_trace, factor_trace,
                                    control_diag, factor_diag):
    """Observational primary endpoint: same prior physical lives only."""
    for i, (a, b) in enumerate(zip(control_trace, factor_trace)):
        prior_a, prior_b = control_trace[:i], factor_trace[:i]
        past_matched = all(
            (x["action"], x["before"], x["after"], x["site_after"]) ==
            (y["action"], y["before"], y["after"], y["site_after"])
            for x, y in zip(prior_a, prior_b))
        current_matched = (
            past_matched and a["before"] == b["before"] and
            a["site_before"] == b["site_before"] and
            a["offered"] == b["offered"])
        if a["action"] == b["action"]:
            continue
        if not current_matched:
            verdict = "DIVERGENCE_WITH_UNMATCHED_HISTORY"
        elif (i >= len(control_diag["ticks"]) or
              i >= len(factor_diag["ticks"]) or
              "food" not in control_diag["ticks"][i]["failed_channels"] or
              "food" not in factor_diag["ticks"][i]["failed_channels"]):
            verdict = "DIVERGENCE_BEFORE_PERSONAL_DOUBLE_FAILURE"
        elif b.get("factor_tagged") is True:
            # A logged factor credit + a paid motor divergence is a narrow
            # association; never infer success, safety or general learning.
            verdict = "DIVERGENCE_AFTER_MATCHED_FAILURE_WITH_FACTOR_CREDIT"
        else:
            # Divergence alone cannot be attributed to v23 without its
            # observed provenance on this same paid decision frame.
            verdict = "DIVERGENCE_AFTER_MATCHED_FAILURE_NO_FACTOR_CREDIT"
        return {
            "classification": verdict, "first_motor_divergence_tick": i + 1,
            "control_action": a["action"], "factor_action": b["action"],
            "same_prehistory": current_matched,
            "factor_tagged_at_divergence": b.get("factor_tagged") is True,
        }
    if len(control_trace) != len(factor_trace):
        return {"classification": "DIFFERENT_OBSERVED_LIFE_LENGTHS",
                "first_motor_divergence_tick": None,
                "same_prehistory": False}
    return {"classification": "NO_MOTOR_DIVERGENCE",
            "first_motor_divergence_tick": None,
            "same_prehistory": True}


def summary_of_life(cell, born, final, trace, diagnostic, custody):
    world, injury, arm, learning, factor = cell
    minima = dict(born["body"])
    for item in trace:
        for channel, value in item["after"].items():
            minima[channel] = min(minima[channel], value)
    meals = [{
        "tick": x["tick"], "site": x["site_before"],
        "food_delta": x["after"]["food"] - x["before"]["food"],
        "integrity_delta": (x["after"]["integrity"] -
                            x["before"]["integrity"]),
    } for x in trace if x["food_meal"]]
    return {
        "world": world, "passage_integrity_delta": injury, "arm": arm,
        "learning": learning, "factor_enabled": factor,
        "born_body": born["body"], "final_body": final["body"],
        "minimum_body": minima, "revision": final["revision"],
        "biological_terminal": final["terminal"],
        "right_censored": not final["terminal"],
        "uc_spent": born["remaining_uc"] - final["remaining_uc"],
        "chosen_moves": [x["tick"] for x in trace
                         if destination(x["action"]) is not None],
        "first_passage_entry": next(
            (x["tick"] for x in trace if x["site_after"] == "passage"
             and x["site_before"] != "passage"), None),
        "first_passage_meal": next(
            (x["tick"] for x in trace
             if x["food_meal"] and x["site_before"] == "passage"), None),
        "meals": meals,
        "first_double_failure_tick":
            diagnostic["summary"]["first_double_failure_tick"],
        "factor_tags": diagnostic["summary"]["factor_tags"],
        "diagnostic_reasons": diagnostic["summary"]["reason_counts"],
        "archive_sha256": custody["archive_sha256"],
        "cold_audit": "PASS",
        "general_adaptation": "NOT_ESTABLISHED",
        "m11_authenticated": False,
    }


def run_study(output, *, execute=False, expected_head=None):
    """Off by default; never run as a unit test or automatic CI step."""
    if execute is not True:
        raise ValueError("explicit --execute-protocol-990 required")
    if type(expected_head) is not str:
        raise ValueError("exact source HEAD required")
    _require_exact_clean_checkout(expected_head)
    output = Path(output)
    if (output.exists() or output.is_symlink() or
            not output.parent.is_dir() or
            output.resolve().is_relative_to(ROOT.resolve())):
        raise ValueError("new output directory outside source repository required")
    output.mkdir(mode=0o700)
    _write_json(output / "status.json", {
        "protocol": PROTOCOL, "status": "IN_PROGRESS",
        "issue": PREREGISTERED_ISSUE, "source_commit": expected_head,
        "completed_cells": [],
    })
    begun = monotonic()
    reports, traces, diagnostics, identities = {}, {}, {}, set()
    try:
        for cell in frozen_cells():
            world, injury, arm, learning, factor = cell
            key = world + "__" + arm
            origin = output / (key + "__original.sqlite")
            archive = output / (key + "__archive.sqlite")
            if origin.exists() or archive.exists():
                raise ValueError("duplicate original/archived life path")
            life = NativePaidI2.create(origin, **frozen_birth_kwargs(cell))
            if (life.life_ref, life.genesis_ref) in identities:
                raise ValueError("distinct independent births required")
            identities.add((life.life_ref, life.genesis_ref))
            born = life.audit()
            for _ in range(MAX_STEPS):
                final_step = life.step()
                if final_step["terminal"]:
                    break
            final = NativePaidI2.inspect(origin).audit()
            if (final["revision"] < 1 or final["revision"] > MAX_STEPS or
                    not (final["terminal"] or
                         final["revision"] == MAX_STEPS)):
                raise ValueError("incomplete or unaudited native life")
            custody = archive_completed_life(origin, archive)
            if custody["revision"] != final["revision"]:
                raise ValueError("archival custody differs from completed life")
            diagnostic = diagnose_existing_life(archive)
            if (diagnostic["revision"] != final["revision"] or
                    diagnostic["factor_enabled"] != factor):
                raise ValueError("archived observer/independent birth mismatch")
            trace = signed_trace(archive)
            if len(trace) != final["revision"]:
                raise ValueError("full signed trace required")
            report = summary_of_life(
                cell, born, final, trace, diagnostic, custody)
            _write_json(output / (key + "__trace.json"), trace)
            _write_json(output / (key + "__diagnosis.json"), diagnostic)
            _write_json(output / (key + "__receipt.json"), custody)
            reports[key], traces[key], diagnostics[key] = report, trace, diagnostic
            _write_json(output / "status.json", {
                "protocol": PROTOCOL, "status": "IN_PROGRESS",
                "issue": PREREGISTERED_ISSUE, "source_commit": expected_head,
                "completed_cells": sorted(reports),
            })
        comparisons = {}
        for world, _ in WORLD_HARMS:
            left, right = (world + "__learning-control",
                           world + "__failed-need-exploration")
            comparisons[world] = first_matched_factor_divergence(
                traces[left], traces[right],
                diagnostics[left], diagnostics[right])
        result = {
            "protocol": PROTOCOL, "issue": PREREGISTERED_ISSUE,
            "source_commit": expected_head, "lives": reports,
            "comparisons": comparisons,
            "elapsed_seconds": round(monotonic() - begun, 3),
            "study_verdict": "OBSERVATIONAL_ONLY_NOT_GENERAL_ADAPTATION",
            "independent_m11": False,
        }
        _write_json(output / "results.json", result)
        _write_json(output / "status.json", {
            "protocol": PROTOCOL, "status": "COMPLETED",
            "issue": PREREGISTERED_ISSUE, "source_commit": expected_head,
            "completed_cells": sorted(reports),
        })
        return result
    except BaseException as exc:
        # Preserve original partial files. Never relabel partial lives as
        # completed, never retry or invent a favorable cohort automatically.
        _write_json(output / "status.json", {
            "protocol": PROTOCOL, "status": "ABORTED",
            "issue": PREREGISTERED_ISSUE, "source_commit": expected_head,
            "completed_cells": sorted(reports), "error": type(exc).__name__,
        })
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute-protocol-990", action="store_true")
    parser.add_argument("--expected-head", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = run_study(args.output, execute=args.execute_protocol_990,
                       expected_head=args.expected_head)
    print(json.dumps({
        "protocol": report["protocol"], "source_commit": report["source_commit"],
        "completed_lives": len(report["lives"]),
        "study_verdict": report["study_verdict"]},
        sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
