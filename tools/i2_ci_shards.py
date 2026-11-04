#!/usr/bin/env python3
"""Run the exact discovered I2 unittest suite once, in two module-isolated workers.

Only CI scheduling changes. All source-locked physical lives, cold audits and
falsifiers still run; module-local test ordering is retained. Unknown modules
are always discovered and scheduled, never excluded by a fixed allowlist.
"""
import argparse
from collections import defaultdict
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

ROOT = Path(__file__).resolve().parents[1]
TEST_DIR = ROOT / "tests" / "i2"
# Approximate module wall times observed on Python 3.12 in Actions run
# 41740611291, before any sharding. Hints only; never coverage filters.
BASELINE_SECONDS = {
    "test_native_recurrent_need_reexposure_906": 190,
    "test_native_ecological_exposure_gradient_951": 117,
    "test_native_harmful_food_satiation_952": 78,
    "test_native_food_restock_944": 78,
    "test_three_mechanism_blind_water_factorial": 47,
    "test_three_mechanism_first_divergences": 47,
    "test_native_longitudinal_quality_cohort_906": 39,
    "test_native_site_bound_food_942": 36,
    "test_blind_water_reachability_census": 34,
    "test_h2_frozen_regime_battery": 33,
    "test_seeded_hidden_reversal_panel": 31,
    "test_blind_water_learning_ablation": 27,
    "test_seeded_varying_world_panel": 23,
    "test_finite_water_capacity_contrast": 13,
    "test_four_policy_survival_ablation": 13,
    "test_native_purpose_followthrough_937": 12,
    "test_native_context_free_movement_credit_940": 12,
    "test_native_place_return_longitudinal_p2_924": 12,
    "test_finite_water_extended_panel": 11,
    "test_native_stable_resource_choice_cohort_906": 11,
    "test_water_longitudinal_panel": 10,
    "test_h2_fresh_committed_selector": 9,
    "test_finite_water_panel": 9,
    "test_h2_three_way_committed": 7,
    "test_scarcity_four_policy_ablation": 7,
    "test_restoration_reexposure_composition": 7,
    "test_exhausted_water_last_resort_proof": 6,
    "test_blind_water_integrated_boundary": 6,
    "test_world_viability_probe": 6,
}


def cases_in(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from cases_in(item)
        else:
            yield item


def discover_cases():
    loader = unittest.TestLoader()
    cases = list(cases_in(loader.discover(
        str(TEST_DIR), pattern="test_*.py", top_level_dir=str(TEST_DIR))))
    if loader.errors:
        raise RuntimeError("I2 discovery failed:\n" + "\n".join(loader.errors))
    ids = [case.id() for case in cases]
    if not ids or len(ids) != len(set(ids)):
        raise RuntimeError("I2 discovery empty or has duplicate test IDs")
    return cases


def partition(cases):
    """Disjoint exhaustive module assignment, preserving each module's order."""
    modules = defaultdict(list)
    for case in cases:
        test_id = case.id()
        modules[test_id.split(".", 1)[0]].append(test_id)
    weights = lambda name, ids: BASELINE_SECONDS.get(name, max(0.25, len(ids) * 0.2))
    assignment = [set(), set()]
    cost = [0.0, 0.0]
    for module, ids in sorted(modules.items(),
                              key=lambda row: (-weights(*row), row[0])):
        worker = 0 if cost[0] <= cost[1] else 1
        assignment[worker].update(ids)
        cost[worker] += weights(module, ids)
    # Keep canonical unittest discovery order within each process.
    shards = [[case.id() for case in cases if case.id() in selected]
              for selected in assignment]
    full = set(case.id() for case in cases)
    if (len(full) != len(cases) or not all(shards) or
            set(shards[0]) & set(shards[1]) or
            set(shards[0]) | set(shards[1]) != full or
            sum(map(len, shards)) != len(cases)):
        raise RuntimeError("I2 partition is not exhaustive and disjoint")
    return shards


def run_worker(manifest_path, report_path, index):
    expected = json.loads(Path(manifest_path).read_text(encoding="utf-8"))["shards"][index]
    cases = discover_cases()
    available = {case.id() for case in cases}
    if len(set(expected)) != len(expected) or not set(expected) <= available:
        raise RuntimeError("I2 test IDs changed between planning and worker discovery")
    selected = [case for case in cases if case.id() in set(expected)]
    if len(selected) != len(expected):
        raise RuntimeError("I2 worker's test membership changed")
    result = unittest.TextTestRunner(verbosity=2).run(unittest.TestSuite(selected))
    report = {
        "planned": len(expected), "executed": result.testsRun,
        "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "successful": result.wasSuccessful(),
    }
    Path(report_path).write_text(json.dumps(report), encoding="utf-8")
    print(f"I2_CI_SHARD_{index}=" + json.dumps(report, sort_keys=True), flush=True)
    return 0 if (report["successful"] and report["executed"] == report["planned"]
                 and report["skipped"] == 0) else 1


def relay(process, lock):
    for line in process.stdout:
        with lock:
            sys.stdout.write(line)
            sys.stdout.flush()


def run_parent():
    cases = discover_cases()
    shards = partition(cases)
    print(f"I2_CI_DISCOVERED={len(cases)}; SHARDS={list(map(len, shards))}", flush=True)
    with tempfile.TemporaryDirectory(prefix="i2-ci-") as directory:
        base = Path(directory)
        manifest = base / "manifest.json"
        manifest.write_text(json.dumps({"shards": shards}), encoding="utf-8")
        processes = [subprocess.Popen(
            [sys.executable, "-u", str(Path(__file__).resolve()),
             "--worker", str(index), "--manifest", str(manifest),
             "--report", str(base / f"result-{index}.json")],
            cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, bufsize=1,
        ) for index in range(2)]
        lock = threading.Lock()
        readers = [threading.Thread(target=relay, args=(process, lock), daemon=True)
                   for process in processes]
        for reader in readers:
            reader.start()
        codes = [process.wait() for process in processes]
        for reader in readers:
            reader.join()
        reports = []
        for index in range(2):
            report_path = base / f"result-{index}.json"
            if not report_path.is_file():
                print(f"I2_CI_MISSING_SHARD_REPORT={index}", file=sys.stderr)
                return 1
            reports.append(json.loads(report_path.read_text(encoding="utf-8")))
        total = sum(report["executed"] for report in reports)
        passed = (all(code == 0 for code in codes) and total == len(cases)
                  and all(report["planned"] == len(shards[index])
                          and report["executed"] == report["planned"]
                          and report["skipped"] == 0 and report["successful"]
                          for index, report in enumerate(reports)))
        print(f"I2_CI_FULL_SUITE={'PASS' if passed else 'FAIL'}; "
              f"DISCOVERED={len(cases)}; EXECUTED={total}; SHARDS=2",
              flush=True)
        return 0 if passed else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", type=int, choices=(0, 1))
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    if args.worker is not None:
        if args.manifest is None or args.report is None:
            parser.error("--worker requires --manifest and --report")
        return run_worker(args.manifest, args.report, args.worker)
    if args.manifest is not None or args.report is not None:
        parser.error("--manifest and --report require --worker")
    return run_parent()


if __name__ == "__main__":
    sys.exit(main())
