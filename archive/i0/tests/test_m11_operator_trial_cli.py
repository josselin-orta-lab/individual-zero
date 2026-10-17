"""End-to-end operator CLI cannot create a second life under one DB."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

from lab.sqlite_life_store import SQLiteLifeLedger


def cli(*args):
    return subprocess.run(
        [sys.executable, "scripts/run_m11_transactional_trial.py", *map(str, args)],
        capture_output=True, text=True, timeout=90,
    )


def test_birth_and_resume_current_generation_from_new_process():
    with TemporaryDirectory() as tmp:
        db = Path(tmp) / "one-life.sqlite"
        born = cli("--db", db, "--steps", "2")
        assert born.returncode == 0, born.stderr
        created = json.loads(born.stdout)
        assert created["schema"] == "m11-operator-sqlite-trial-v1"
        assert created["status"] == "active"
        assert created["generation"] == 2
        assert created["executed_steps"] == 2
        assert created["scientific_validation"] is None
        identity = created["individual_id"]
        blocked_birth = cli("--db", db, "--steps", "1")
        assert blocked_birth.returncode == 2
        assert "already exists" in blocked_birth.stderr
        wrong = cli("--db", db, "--steps", "1",
                    "--resume", "--identity", identity + ":wrong")
        assert wrong.returncode == 2
        recovered = cli("--db", db, "--steps", "2",
                        "--resume", "--identity", identity)
        assert recovered.returncode == 0, recovered.stderr
        after = json.loads(recovered.stdout)
        assert after["generation"] == 4
        assert after["last_world_step"] == 4
        assert after["journal_count"] > created["journal_count"]
        assert after["journal_head"] != created["journal_head"]
        assert SQLiteLifeLedger.audit_read_only(
            path=str(db), expected_individual_id=identity
        ).generation == 4


def test_cli_never_implicitly_recovers_or_reuses_an_identity():
    with TemporaryDirectory() as tmp:
        db = Path(tmp) / "one-life.sqlite"
        no_id = cli("--db", db, "--resume", "--steps", "1")
        assert no_id.returncode != 0
        assert "requires the precise persistent" in no_id.stderr
        user_birth = cli("--db", db, "--steps", "1",
                         "--identity", "chosen-self")
        assert user_birth.returncode != 0
        assert not db.exists()


def test_cli_stage10_current_owner_custody():
    with TemporaryDirectory() as tmp:
        db = Path(tmp) / "sleep.sqlite"
        born = cli("--db", db, "--runtime", "stage10", "--steps", "1")
        assert born.returncode == 0, born.stderr
        data = json.loads(born.stdout)
        resumed = cli("--db", db, "--runtime", "stage10",
                      "--steps", "1", "--resume",
                      "--identity", data["individual_id"])
        assert resumed.returncode == 0, resumed.stderr
        assert json.loads(resumed.stdout)["generation"] == 2
