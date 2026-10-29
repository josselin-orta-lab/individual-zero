#!/usr/bin/env python3
"""Cold 48-life A1-C M11 custody and full TD replay, never a new birth.

Input: 48 ORIGINAL ZIPs and I1_ECO_A1C_EVIDENCE_MANIFEST.json.
Checks ZIP SHA-256, M11 canonical occurrence hashes, 12-feature TD replay,
published native Q, masked Stage8 and Competition, physical motor entries.
"""
import argparse
from concurrent.futures import ProcessPoolExecutor
from hashlib import sha256
import json
from pathlib import Path
from statistics import mean
import sqlite3
import tempfile
import zipfile

from i1_a1c_td_full import FROZEN_RUN_ID, FROZEN_SOURCE_SHA, replay_life

ROLES = ("native", "reversed")
SEEDS = tuple(range(101, 113))
ARMS = ("canonical", "td_read_masked")


def canonical(obj):
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def one(item):
    root, name, record, role, seed, mode = item
    path = root / (name + ".zip")
    if path.is_symlink() or not path.is_file():
        raise ValueError("missing or symlinked original ZIP: " + name)
    data = path.read_bytes()
    if (len(data) != record["bytes"]
            or sha256(data).hexdigest() != record["sha256"]):
        raise ValueError("original A1-C ZIP SHA-256 mismatch: " + name)
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if (not {"life.sqlite", "report.json"}.issubset(names)
                or len(names) != len(set(names))
                or any("/" in n or "\\" in n or ".." in n for n in names)):
            raise ValueError("incomplete or unsafe original A1-C archive")
        report = json.loads(archive.read("report.json"))
        life = report["life"]
        if (report.get("source_commit") != FROZEN_SOURCE_SHA
                or life.get("source_commit") != FROZEN_SOURCE_SHA
                or report.get("verdict") != "MEASUREMENT_FRAGMENT_READY"
                or life.get("audited", {}).get("generation") != 48
                or life.get("identity") != report.get("identity")
                or (report.get("role"), report.get("seed"),
                    report.get("mode")) != (role, seed, mode)):
            raise ValueError("wrong original M11 identity or provenance")
        with tempfile.TemporaryDirectory(prefix="i1-a1c-full-td-") as temp:
            base = Path(temp)
            for filename in ("life.sqlite", "life.sqlite-wal", "life.sqlite-shm"):
                if filename in names:
                    (base / filename).write_bytes(archive.read(filename))
            with sqlite3.connect("file:" + str(base / "life.sqlite") + "?mode=ro",
                                 uri=True) as connection:
                connection.execute("PRAGMA query_only=ON")
                connection.execute("BEGIN")
                state = connection.execute(
                    "SELECT generation,journal_count,journal_head FROM life_current "
                    "WHERE slot=1").fetchone()
                rows = connection.execute(
                    "SELECT idx,event_id,previous_hash,event_hash,canonical_bytes "
                    "FROM causal_occurrence ORDER BY idx").fetchall()
    if (state != (48, life["audited"]["journal_count"],
                  life["audited"]["journal_head"])
            or len(rows) != state[1]):
        raise ValueError("M11 head/count does not match original receipt")
    previous = "00" * 32
    events = []
    for index, eid, parent, digest, raw in rows:
        occurrence = json.loads(raw)
        if (index != len(events) or parent != previous
                or occurrence.get("index") != index
                or occurrence.get("event_id") != eid
                or occurrence.get("previous_hash") != previous
                or occurrence.get("event_hash") != digest
                or canonical(occurrence) != raw):
            raise ValueError("noncanonical or out-of-order M11 occurrence")
        calculated = sha256(bytes.fromhex(previous) + canonical({
            "event_id": eid, "causal_event": occurrence["causal_event"],
        })).hexdigest()
        if calculated != digest:
            raise ValueError("tampered native M11 chain")
        previous = digest
        events.append(occurrence["causal_event"])
    if previous != state[2]:
        raise ValueError("M11 final chain hash mismatch")
    calculated = replay_life(events, born_td=life["born_td"], mode=mode)
    return {"name": name, "role": role, "seed": seed, "mode": mode,
            "original_zip_sha256": record["sha256"], "m11_head": previous,
            **calculated}


def audit(root, *, workers=1):
    if type(workers) is not int or workers not in (1, 2, 3, 4):
        raise ValueError("1–4 independent cold audit workers only")
    root = Path(root)
    if root.is_symlink():
        raise ValueError("symlinked original evidence root")
    manifest = json.loads(
        (root / "I1_ECO_A1C_EVIDENCE_MANIFEST.json").read_text())
    if (manifest.get("original_run_id") != FROZEN_RUN_ID
            or manifest.get("original_source_sha") != FROZEN_SOURCE_SHA
            or manifest.get("archived_independent_lives") != 48):
        raise ValueError("wrong original frozen source cohort")
    expected = {f"a1c-{role}-s{seed}-{mode}"
                for role in ROLES for seed in SEEDS for mode in ARMS}
    originals = [row for row in manifest["original_zip_archives"]
                 if row["name"].endswith(".zip")
                 and row["name"][:-4] in expected]
    byname = {row["name"][:-4]: row for row in originals}
    if len(originals) != 48 or len(byname) != 48 or set(byname) != expected:
        raise ValueError("missing, extra, or duplicated original cohort ZIP")
    inputs = [(root, f"a1c-{role}-s{seed}-{mode}",
               byname[f"a1c-{role}-s{seed}-{mode}"], role, seed, mode)
              for role in ROLES for seed in SEEDS for mode in ARMS]
    if workers == 1:
        lives = [one(i) for i in inputs]
    else:
        with ProcessPoolExecutor(max_workers=workers) as pool:
            lives = list(pool.map(one, inputs))
    groups = {}
    for role in ROLES:
        for mode in ARMS:
            subset = [l for l in lives if l["role"] == role and l["mode"] == mode]
            updates = [u for life in subset for u in life["postmeal"]]
            delta_q = [u["collect_update_q_at_td_next_state"] for u in updates]
            groups[role + "/" + mode] = {
                "lives": len(subset), "postmeal_td": len(updates),
                "projected_positive": sum(n > 0 for n in delta_q),
                "projected_negative": sum(n < 0 for n in delta_q),
                "mean_update_only_collect_Q_delta_at_next_state":
                    mean(delta_q) if delta_q else None,
            }
    return {
        "schema": "individual-zero-i1-a1c-full-vector-M11-read-only/1",
        "source_commit": FROZEN_SOURCE_SHA, "original_run_id": FROZEN_RUN_ID,
        "audited_original_lives": len(lives),
        "stage8_native_q_checks": sum(x["native_m11_q_checks"] for x in lives),
        "masked_stage8_checks": sum(x["masked_stage8_consistency_checks"]
                                    for x in lives),
        "td_snapshot_fields_checked": sum(x["td_snapshot_q_and_delta_checks"]
                                          for x in lives),
        "td_updates": sum(x["td_updates"] for x in lives),
        "stage8_competition_links": sum(x["stage8_to_competition_links"]
                                        for x in lives),
        "motor_crossed": sum(x["motor_selected_crossed"] for x in lives),
        "motor_wait_fallback": sum(x["motor_wait_fallback"] for x in lives),
        "max_m11_numeric_residual": max(
            x["max_m11_numeric_residual"] for x in lives),
        "by_role_mode": groups, "lives": lives,
        "scope": "POSTHOC_NATIVE_M11_REPLAY_NOT_CAUSAL_BENEFIT",
        "a1c_status": "NO_GO", "general_L3": "NOT_ESTABLISHED",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--workers", type=int, default=1)
    args = parser.parse_args()
    result = audit(args.root, workers=args.workers)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "lives"},
                     sort_keys=True))


if __name__ == "__main__":
    main()
