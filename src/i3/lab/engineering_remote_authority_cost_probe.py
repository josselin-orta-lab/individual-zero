"""No-World I3 R2.4 authority-v3 cost probe, never a production M11 claim.

Each call makes one isolated engineering-only CAS database and measures actual
host time and SQLite bytes with all existing audit and nonce checks enabled.
No Mind, World, Life, cognition energy, motor or scientific cohort is used.
"""
from __future__ import annotations

import argparse
from contextlib import closing
from hashlib import sha256
import json
import math
from pathlib import Path
import platform
import sqlite3
from statistics import median
import tempfile
from time import perf_counter_ns

from i3.lab.engineering_remote_authority import AuthorityStore, DB_SCHEMA
from i3.runtime.birth_reservation import make_reservation
from i3.runtime.engineering_remote_witness import SCHEMA, claim_data

AUTHORITY_ID = "d" * 64


def _digest(prefix: str, seq: int) -> str:
    return sha256(f"i3-r24-cost:{prefix}:{seq}".encode("ascii")).hexdigest()


def _summary(samples_ns: list[int]) -> dict:
    if not samples_ns:
        raise ValueError("no operation duration samples")
    ordered = sorted(samples_ns)
    n = len(ordered)
    return {
        "samples": n,
        "median_ms": round(median(ordered) / 1_000_000, 6),
        "p95_ms": round(ordered[math.ceil(n * 0.95) - 1] / 1_000_000, 6),
        "max_ms": round(ordered[-1] / 1_000_000, 6),
    }


def probe(steps: int) -> dict:
    """Measure one source-isolated CAS claim, with no externally owned state.

    Timing values are host-specific observations, NOT model energy tariffs.
    The terminal is always censored on the exact final engineering step.
    """
    if type(steps) is not int or not 1 <= steps <= 100:
        raise ValueError("steps must be an integer in [1, 100]")
    with tempfile.TemporaryDirectory(prefix="i3-r24-cost-") as temporary:
        database = Path(temporary) / "authority.sqlite3"
        store = AuthorityStore(database, AUTHORITY_ID)
        claim = claim_data(make_reservation(
            birth_index=9101, life_seed=7719,
            source_sha256="a" * 64, world_sha256="b" * 64,
            genome_sha256="c" * 64))
        nonce_number = 0
        times = {"register": [], "verify": [], "prepare": [], "commit": []}
        step_times = []

        def send(op: str, **fields) -> dict:
            nonlocal nonce_number
            nonce_number += 1
            request = {"schema": SCHEMA, "authority_id": AUTHORITY_ID,
                       "operation": op, "claim": claim, **fields}
            begin = perf_counter_ns()
            response = store.apply(
                request, request_nonce=f"{nonce_number:032x}")
            times[op].append(perf_counter_ns() - begin)
            return response

        head = _digest("genesis", 0)
        registered = send("register", horizon=steps, head_sha256=head)
        if (registered["sequence"] != 0
                or registered["head_sha256"] != head
                or registered["terminal"] != "OPEN"
                or registered["phase"] != "COMMITTED"):
            raise AssertionError("invalid engineering genesis")
        for seq in range(1, steps + 1):
            start_step = perf_counter_ns()
            prior = send("verify")
            if (prior["sequence"] != seq - 1
                    or prior["head_sha256"] != head
                    or prior["phase"] != "COMMITTED"
                    or prior["terminal"] != "OPEN"):
                raise AssertionError("unexpected before-motor CAS state")
            intent = _digest("intent", seq)
            prepared = send("prepare", sequence=seq,
                            previous_head_sha256=head,
                            intent_sha256=intent)
            if (prepared["phase"] != "PREPARED"
                    or prepared["sequence"] != seq - 1
                    or prepared["pending_sequence"] != seq
                    or prepared["pending_intent_sha256"] != intent):
                raise AssertionError("wrong PREPARED acknowledgement")
            new_head = _digest("committed-head", seq)
            terminal = "CENSORED" if seq == steps else "OPEN"
            committed = send("commit", sequence=seq,
                             previous_head_sha256=head,
                             intent_sha256=intent, head_sha256=new_head,
                             terminal=terminal)
            if (committed["phase"] != "COMMITTED"
                    or committed["head_sha256"] != new_head
                    or committed["sequence"] != seq
                    or committed["terminal"] != terminal
                    or committed["pending_sequence"] is not None
                    or committed["pending_intent_sha256"] is not None):
                raise AssertionError("wrong committed/terminal CAS state")
            head = new_head
            step_times.append(perf_counter_ns() - start_step)

        with closing(sqlite3.connect(database)) as connection:
            schema = connection.execute(
                "SELECT schema FROM metadata WHERE id=1").fetchone()[0]
            audit = connection.execute("SELECT COUNT(*) FROM audit").fetchone()[0]
            nonces = connection.execute(
                "SELECT COUNT(*) FROM request_nonces").fetchone()[0]
            final = connection.execute(
                "SELECT sequence,head,phase,terminal FROM histories "
                "WHERE identity=?", (claim["identity_sha256"],)).fetchone()
        if (schema != DB_SCHEMA or audit != 1 + 2 * steps
                or nonces != 1 + 3 * steps
                or final != (steps, head, "COMMITTED", "CENSORED")):
            raise AssertionError("audit/nonce growth or terminal receipt mismatch")
        disk_files = (
            database, Path(str(database) + "-wal"),
            Path(str(database) + "-shm"))
        disk_bytes = sum(p.stat().st_size for p in disk_files if p.is_file())
        quarter = max(1, steps // 4)
        return {
            "schema": DB_SCHEMA,
            "steps": steps,
            "python": platform.python_version(),
            "platform": platform.system(),
            "audit_events": audit,
            "accepted_request_nonces": nonces,
            "expected_audit_events": 1 + 2 * steps,
            "expected_request_nonces": 1 + 3 * steps,
            "terminal": final[3],
            "disk_bytes_db_wal_shm": disk_bytes,
            "register": _summary(times["register"]),
            "verify": _summary(times["verify"]),
            "prepare": _summary(times["prepare"]),
            "commit": _summary(times["commit"]),
            "paid_step_host_only": _summary(step_times),
            "first_quarter_step": _summary(step_times[:quarter]),
            "last_quarter_step": _summary(step_times[-quarter:]),
            "world_steps": 0,
            "scientific_lives": 0,
            "independent_m11_attested": False,
        }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="R2.4 isolated SQLite CAS cost probe, no World or Mind")
    parser.add_argument("--steps", nargs="+", type=int, default=[8, 32, 80])
    args = parser.parse_args()
    for n in args.steps:
        print("R24_AUTHORITY_COST " + json.dumps(probe(n), sort_keys=True))


if __name__ == "__main__":
    main()
