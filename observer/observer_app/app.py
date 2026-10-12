"""Individual Zero Observer API and constrained subprocess runner.

The only bridge to Core is a fixed argv in a separate process. Scientific
artifacts remain owned by their producers and are only opened read-only.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import signal
import stat
import subprocess
import sys
import tempfile
import threading
import time
import uuid
import zipfile
from datetime import datetime, timezone
from typing import Any, Iterator

from fastapi import Body, Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, ConfigDict, StrictInt

WEB = Path(__file__).parent / "web"
RUN_ID = re.compile(r"r-[0-9a-f]{32}\Z")
IMPORT_ID = re.compile(r"import-[a-zA-Z0-9_-]{1,64}\Z")
SAFE_NAME = re.compile(r"[a-zA-Z0-9_][a-zA-Z0-9_.-]{0,127}\Z")
ALLOWED_SOURCES = frozenset({"journal", "oracle", "evaluation_trace", "lab_events"})
LOCAL_FILES = {"lab_events": "events.jsonl", "log": "execution.log", "result": "result.json", "status": "_status.json", "manifest": "_manifest.json"}
SOURCE_CLASSES = {"journal": "causal_journal", "oracle": "oracle_declared_source", "evaluation_trace": "independent_evaluation", "lab_events": "lab_telemetry"}
MAX_PAGE = 200
MAX_RECORD = 2 * 1024 * 1024

CATALOG = (
    {"id": "bootstrap", "title": "Bootstrap deterministic smoke", "description": "LabEvent JSONL; execution infrastructure only, not an Oracle or a cognitive experiment.", "parameters": {"seed": {"min": 0, "max": 2147483647, "default": 0}, "cycles": {"min": 1, "max": 600, "default": 3}}, "timeout_seconds": 120},
    {"id": "mortal_stage11", "title": "Stage 11 autonomous mortal diagnostic", "description": "Runs real physical steps without Oracle/Bench. Produces a report, not an exported journal or scientific verdict. Seed fixed by upstream reference fixture.", "parameters": {"steps": {"min": 1, "max": 600, "default": 20}}, "timeout_seconds": 1200},
    {"id": "journal_unit", "title": "Journal unit checks", "description": "Fixed journal unit-test discovery. No operator-selectable test paths.", "parameters": {}, "timeout_seconds": 180},
)
CATALOG_BY_ID = {item["id"]: item for item in CATALOG}


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_dir(path: Path, *, create: bool = False) -> Path:
    path = path.absolute()
    if create:
        path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink() or not path.is_dir():
        raise ValueError(f"invalid non-directory or symbolic directory: {path}")
    return path


def atomic_json(path: Path, data: dict[str, Any]) -> None:
    raw = (json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()
    name = f".{path.name}.{secrets.token_hex(8)}.tmp"
    fd = os.open(path.parent / name, os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(path.parent / name, path)
        df = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(df)
        finally:
            os.close(df)
    finally:
        try:
            (path.parent / name).unlink()
        except FileNotFoundError:
            pass


def safe_name(value: str) -> str:
    if not isinstance(value, str) or not SAFE_NAME.fullmatch(value) or value in {".", ".."}:
        raise ValueError("invalid artifact basename")
    return value


def open_regular(parent: Path, basename: str):
    """Open direct-child regular file using dir_fd and O_NOFOLLOW.

    No absolute paths, traversals or symlink dereferences are accepted.
    """
    safe_name(basename)
    directory_fd = os.open(parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0))
    try:
        fd = os.open(basename, os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0), dir_fd=directory_fd)
    finally:
        os.close(directory_fd)
    if not stat.S_ISREG(os.fstat(fd).st_mode):
        os.close(fd)
        raise ValueError("artifact must be a regular non-symlink file")
    return os.fdopen(fd, "rb")


def hash_file(parent: Path, name: str) -> dict[str, Any]:
    digest = hashlib.sha256()
    size = 0
    with open_regular(parent, name) as stream:
        for data in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(data)
            size += len(data)
    return {"sha256": digest.hexdigest(), "bytes": size}


def commit_of(root: Path) -> str | None:
    try:
        outcome = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], text=True, capture_output=True, timeout=4, check=True)
        sha = outcome.stdout.strip()
        return sha if re.fullmatch("[0-9a-f]{40}", sha) else None
    except (OSError, subprocess.SubprocessError):
        return None


def worktree_dirty(root: Path) -> bool | None:
    try:
        result = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--untracked-files=no"], capture_output=True, text=True, check=True, timeout=5)
        return bool(result.stdout.strip())
    except (OSError, subprocess.SubprocessError):
        return None


class RunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    test_id: str
    seed: StrictInt | None = None
    steps: StrictInt | None = None
    cycles: StrictInt | None = None


class SessionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    token: str


class Observer:
    def __init__(self, *, core_root: Path, run_root: Path, archive_root: Path | None = None):
        self.core_root = ensure_dir(core_root)
        self.run_root = ensure_dir(run_root, create=True)
        if stat.S_IMODE(self.run_root.stat().st_mode) & 0o077:
            raise ValueError("run directory must be private (chmod 700)")
        self.archive_root = ensure_dir(archive_root) if archive_root else None
        self.commit = commit_of(self.core_root)
        self.dirty = worktree_dirty(self.core_root)
        self._lock = threading.RLock()
        self._active: str | None = None
        self._processes: dict[str, subprocess.Popen] = {}
        self._cancel: set[str] = set()
        self._recover_incomplete()

    def _dir(self, rid: str) -> Path:
        if RUN_ID.fullmatch(rid):
            directory = self.run_root / rid
        elif IMPORT_ID.fullmatch(rid) and self.archive_root:
            directory = self.archive_root / rid.removeprefix("import-")
        else:
            raise HTTPException(404, "unknown run")
        if directory.is_symlink() or not directory.is_dir():
            raise HTTPException(404, "unknown run")
        return directory

    def _local_status(self, rid: str) -> dict[str, Any]:
        directory = self._dir(rid)
        if not RUN_ID.fullmatch(rid):
            raise HTTPException(400, "imported runs have no local execution status")
        try:
            with open_regular(directory, "_status.json") as f:
                row = json.load(f)
            if row.get("id") != rid or row.get("schema") != "observer-run-v1":
                raise ValueError("invalid status schema or identity")
            return row
        except (OSError, ValueError, json.JSONDecodeError):
            raise HTTPException(409, "run metadata missing or corrupt") from None

    def _recover_incomplete(self):
        for path in self.run_root.iterdir():
            if not RUN_ID.fullmatch(path.name) or path.is_symlink() or not path.is_dir():
                continue
            try:
                with open_regular(path, "_status.json") as f:
                    row = json.load(f)
                if row.get("id") == path.name and row.get("status") in ("PENDING", "RUNNING"):
                    row.update(status="INTERRUPTED", ended_at=utcnow(), anomaly="observer_process_restarted_before_terminal_receipt; prior child process may still exist; operator must inspect host process group", technical_success=None, assertions_passed=None, behavior_conformance=None, scientific_validation=None, operator_validation=None)
                    atomic_json(path / "_status.json", row)
            except (OSError, ValueError, json.JSONDecodeError):
                # Missing or corrupted receipts are never interpreted as success.
                pass

    def _imports(self) -> list[dict[str, Any]]:
        if self.archive_root is None:
            return []
        result = []
        for directory in self.archive_root.iterdir():
            if directory.is_symlink() or not directory.is_dir() or not re.fullmatch("[a-zA-Z0-9_-]{1,64}", directory.name):
                continue
            try:
                with open_regular(directory, "observer-source-v1.json") as f:
                    raw = f.read(1024 * 1024 + 1)
                if len(raw) > 1024 * 1024:
                    continue
                data = json.loads(raw)
                files = data["files"]
                if data.get("schema") != "observer-source-v1" or not isinstance(files, dict) or not files:
                    continue
                if not set(files).issubset(ALLOWED_SOURCES) or not all(isinstance(v, str) and safe_name(v) for v in files.values()):
                    continue
                if len(set(files.values())) != len(files):
                    continue
                # Validate all links now and again at every actual read.
                for name in files.values():
                    with open_regular(directory, name):
                        pass
                result.append({"id": "import-" + directory.name, "kind": "imported", "test_id": None, "created_at": data.get("created_at"), "status": "IMPORTED", "files": files, "metadata": data.get("metadata") if isinstance(data.get("metadata"), dict) else {}, "scientific_validation": None, "operator_validation": None, "integrity": "not_verified"})
            except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError):
                continue
        return result

    def list_runs(self, *, query: str = "", status: str = "", limit: int = 100) -> list[dict[str, Any]]:
        found = []
        for directory in self.run_root.iterdir():
            if RUN_ID.fullmatch(directory.name) and not directory.is_symlink() and directory.is_dir():
                try:
                    row = self._local_status(directory.name)
                    found.append(row)
                except HTTPException:
                    found.append({"id": directory.name, "kind": "local", "status": "INTERRUPTED", "anomaly": "invalid_or_missing_run_receipt", "integrity": "not_verified"})
        found.extend(self._imports())
        found = [x for x in found if (not status or x.get("status") == status) and (not query or query.lower() in json.dumps({k: x.get(k) for k in ("id", "test_id", "status", "metadata")}).lower())]
        return sorted(found, key=lambda x: x.get("created_at") or "", reverse=True)[:limit]

    def detail(self, rid: str) -> dict[str, Any]:
        if RUN_ID.fullmatch(rid):
            status = self._local_status(rid)
        else:
            status = next((x for x in self._imports() if x["id"] == rid), None)
            if status is None:
                raise HTTPException(404, "unknown imported run")
        return {**status, "artifacts": self.files(rid)}

    def files(self, rid: str) -> list[dict[str, Any]]:
        directory = self._dir(rid)
        if RUN_ID.fullmatch(rid):
            alias_map = LOCAL_FILES
        else:
            data = next((x for x in self._imports() if x["id"] == rid), None)
            if data is None:
                raise HTTPException(404, "unknown imported run")
            alias_map = data["files"] | {"source_manifest": "observer-source-v1.json"}
        entries = []
        for alias, name in alias_map.items():
            try:
                with open_regular(directory, name) as stream:
                    size = os.fstat(stream.fileno()).st_size
                entries.append({"alias": alias, "name": name, "bytes": size, "category": SOURCE_CLASSES.get(alias, "observer_metadata")})
            except (OSError, ValueError):
                continue
        return entries

    def file(self, rid: str, alias: str) -> tuple[Path, str]:
        directory = self._dir(rid)
        matches = {x["alias"]: x["name"] for x in self.files(rid)}
        if alias not in matches:
            raise HTTPException(404, "artifact alias not available")
        return directory, matches[alias]

    def start(self, params: RunRequest) -> dict[str, Any]:
        catalog = CATALOG_BY_ID.get(params.test_id)
        if not catalog:
            raise HTTPException(422, "unknown test id")
        supplied = {k: v for k, v in params.model_dump(exclude_none=True).items() if k != "test_id"}
        if not set(supplied).issubset(catalog["parameters"]):
            raise HTTPException(422, "unsupported parameter for this catalog test")
        resolved = {}
        for key, rule in catalog["parameters"].items():
            n = supplied.get(key, rule["default"])
            if type(n) is not int or not (rule["min"] <= n <= rule["max"]):
                raise HTTPException(422, f"invalid {key}")
            resolved[key] = n
        with self._lock:
            if self._active is not None:
                raise HTTPException(409, "another test run is active; maximum concurrency is one")
            rid = "r-" + uuid.uuid4().hex
            directory = self.run_root / rid
            directory.mkdir(mode=0o700)
            row = {"schema": "observer-run-v1", "id": rid, "kind": "local", "test_id": params.test_id, "parameters": resolved, "status": "PENDING", "created_at": utcnow(), "started_at": None, "ended_at": None, "source_commit": self.commit, "source_dirty": self.dirty, "technical_success": None, "assertions_passed": None, "behavior_conformance": None, "scientific_validation": None, "operator_validation": None, "integrity": "not_verified", "requested_steps": resolved.get("steps"), "executed_steps": None, "exit_code": None, "anomaly": None}
            atomic_json(directory / "_status.json", row)
            self._active = rid
            threading.Thread(target=self._run, args=(rid, row, catalog), daemon=True, name="observer-" + rid).start()
            return row

    def _argv(self, rid: str, row: dict[str, Any]) -> list[str]:
        test = row["test_id"]
        p = row["parameters"]
        if test == "bootstrap":
            return [sys.executable, "-m", "lab.cli", "--seed", str(p["seed"]), "--cycles", str(p["cycles"]), "--run-id", rid, "--output", str(self.run_root / rid / "events.jsonl")]
        if test == "mortal_stage11":
            return [sys.executable, "-m", "lab.stage11_autonomous_600_step_probe", "--steps", str(p["steps"])]
        if test == "journal_unit":
            return [sys.executable, "-m", "unittest", "discover", "-s", str(self.core_root / "tests"), "-p", "test_causal_journal.py", "-v"]
        raise ValueError("not an explicitly authorized test")

    def _run(self, rid: str, row: dict[str, Any], catalog: dict[str, Any]) -> None:
        directory = self.run_root / rid
        try:
            with self._lock:
                if rid in self._cancel:
                    row.update(status="CANCELLED", ended_at=utcnow(), anomaly="cancelled_before_spawn")
                    atomic_json(directory / "_status.json", row)
                    return
                row.update(status="RUNNING", started_at=utcnow())
                atomic_json(directory / "_status.json", row)
            env = {key: os.environ[key] for key in ("PATH", "SYSTEMROOT", "WINDIR") if key in os.environ}
            env.update(PYTHONPATH=os.pathsep.join((str(self.core_root / "src"), str(self.core_root))), PYTHONDONTWRITEBYTECODE="1", PYTHONUNBUFFERED="1", PYTHONNOUSERSITE="1", PYTHONSAFEPATH="1", HOME=str(directory), TMPDIR=str(directory), LC_ALL="C.UTF-8")
            with open(directory / "execution.log", "xb") as log:
                try:
                    child = subprocess.Popen(self._argv(rid, row), stdin=subprocess.DEVNULL, stdout=log, stderr=subprocess.STDOUT, cwd=directory, env=env, start_new_session=(os.name == "posix"), close_fds=True, preexec_fn=_limits if os.name == "posix" else None)
                except (OSError, ValueError) as exc:
                    log.write(("spawn_error: " + type(exc).__name__ + ": " + str(exc) + "\n").encode())
                    raise
                with self._lock:
                    self._processes[rid] = child
                    if rid in self._cancel:
                        _stop_group(child)
                deadline = time.monotonic() + catalog["timeout_seconds"]
                stopping_since = None
                try:
                    while True:
                        now = time.monotonic()
                        with self._lock:
                            cancelled = rid in self._cancel
                        timed_out = now >= deadline
                        if timed_out:
                            row["anomaly"] = "execution_timeout"
                        if (cancelled or timed_out) and stopping_since is None:
                            stopping_since = now
                            _stop_group(child)
                        if stopping_since is not None and now - stopping_since >= 3:
                            _kill_group(child)
                        try:
                            code = child.wait(timeout=0.2)
                            break
                        except subprocess.TimeoutExpired:
                            continue
                finally:
                    with self._lock:
                        self._processes.pop(rid, None)
            report = self._extract_report(directory / "execution.log", row["test_id"])
            if report is not None:
                atomic_json(directory / "result.json", report)
            with self._lock:
                cancelled = rid in self._cancel
            successful = code == 0 and not cancelled and not row["anomaly"]
            assertion_receipt = successful and (row["test_id"] == "journal_unit" or (row["test_id"] == "mortal_stage11" and isinstance(report, dict) and report.get("protocol_version") == "stage11-autonomous-600-journal-v1" and report.get("classification") == "public_development_diagnostic_not_heldout" and report.get("scientific_verdict") is None and type(report.get("steps_physically_executed")) is int and report["steps_physically_executed"] == row["parameters"]["steps"] and report.get("offline_audit_completed") is True and report.get("external_oracle_loaded") is False and report.get("external_bench_loaded") is False))
            row.update(status="CANCELLED" if cancelled else "FAILED" if not successful else "SUCCESS", exit_code=code, ended_at=utcnow(), technical_success=successful, assertions_passed=(True if assertion_receipt else None), executed_steps=(report.get("steps_physically_executed") if isinstance(report, dict) and type(report.get("steps_physically_executed")) is int else None))
            if row["test_id"] == "bootstrap" and row["status"] == "SUCCESS":
                row["executed_steps"] = None  # CLI cycles are NOT verified physical world steps.
            atomic_json(directory / "_status.json", row)
            self._make_manifest(directory, row)
        except BaseException as exc:
            row.update(status="INTERRUPTED", ended_at=utcnow(), anomaly="runner_error:" + type(exc).__name__, technical_success=None, assertions_passed=None)
            try:
                atomic_json(directory / "_status.json", row)
            except OSError:
                pass
        finally:
            with self._lock:
                self._active = None
                self._cancel.discard(rid)
                self._processes.pop(rid, None)

    def _extract_report(self, log_path: Path, test: str) -> dict[str, Any] | None:
        prefix = {"mortal_stage11": b"stage11_autonomous_600_step="}.get(test)
        if not prefix:
            return None
        with open_regular(log_path.parent, log_path.name) as stream:
            for line in stream:
                if line.startswith(prefix) and len(line) <= MAX_RECORD:
                    try:
                        report = json.loads(line[len(prefix):])
                        return report if isinstance(report, dict) else None
                    except (ValueError, UnicodeDecodeError):
                        return None
        return None

    def _make_manifest(self, directory: Path, row: dict[str, Any]) -> None:
        entries = {}
        for alias, name in LOCAL_FILES.items():
            if alias in {"status", "manifest"}:
                continue
            try:
                entries[alias] = {"name": name, **hash_file(directory, name)}
            except (ValueError, OSError):
                pass
        atomic_json(directory / "_manifest.json", {"schema": "observer-artifacts-v1", "run_id": row["id"], "test_id": row["test_id"], "source_commit": row["source_commit"], "source_dirty": row["source_dirty"], "created_at": utcnow(), "files": entries, "integrity_scope": "observer-produced-file-bytes-only", "physical_truth_verified": False, "scientific_validation": None})

    def cancel(self, rid: str) -> dict[str, Any]:
        with self._lock:
            row = self._local_status(rid)
            if row["status"] not in ("PENDING", "RUNNING") or self._active != rid:
                raise HTTPException(409, "run is not active")
            self._cancel.add(rid)
            child = self._processes.get(rid)
            if child:
                if child.poll() is not None:
                    raise HTTPException(409, "process has already exited")
                _stop_group(child)
            return {"id": rid, "cancellation_requested": True}

    def events(self, rid: str, *, source: str, cursor: int, limit: int, kind: str, component: str, step: int | None, at: str, search: str) -> dict[str, Any]:
        if source not in ALLOWED_SOURCES:
            raise HTTPException(422, "unknown event source")
        directory, name = self.file(rid, source)
        items = []
        line_number = 0
        more = False
        with open_regular(directory, name) as stream:
            while True:
                record = stream.readline(MAX_RECORD + 1)
                if not record:
                    break
                line_number += 1
                if line_number <= cursor:
                    continue
                if len(record) > MAX_RECORD:
                    # Do not silently discard malformed/oversized records.
                    while record and not record.endswith(b"\n"):
                        record = stream.readline(MAX_RECORD + 1)
                    entry = {"line": line_number, "category": SOURCE_CLASSES[source], "integrity_error": "jsonl_record_exceeds_2MiB", "raw": None, "kind": None, "step": None, "component": None}
                else:
                    try:
                        obj = json.loads(record)
                        if not isinstance(obj, dict):
                            raise ValueError("JSONL record must be an object")
                        evt = obj.get("causal_event", obj) if source == "journal" else obj
                        if not isinstance(evt, dict):
                            raise ValueError("causal_event must be an object")
                        data = evt.get("data", {})
                        ekind = evt.get("kind")
                        estep = evt.get("t_monde", evt.get("cycle"))
                        ecomponent = evt.get("component", evt.get("owner_id"))
                        if not ecomponent and isinstance(data, dict):
                            ecomponent = data.get("component", data.get("owner_id"))
                        recorded_time = evt.get("timestamp", evt.get("time_utc"))
                        entry = {"line": line_number, "category": SOURCE_CLASSES[source], "kind": ekind, "step": estep, "timestamp": recorded_time, "component": ecomponent, "raw": obj}
                    except (ValueError, UnicodeDecodeError):
                        entry = {"line": line_number, "category": SOURCE_CLASSES[source], "integrity_error": "invalid_jsonl_record", "raw": None, "kind": None, "step": None, "component": None}
                if (kind and kind != str(entry.get("kind") or "")) or (component and component.lower() not in str(entry.get("component") or "").lower()) or (step is not None and entry.get("step") != step) or (at and str(entry.get("timestamp") or "") != at) or (search and search.lower() not in json.dumps(entry, ensure_ascii=False).lower()):
                    continue
                if len(items) == limit:
                    more = True
                    break
                items.append(entry)
        return {"items": items, "next_cursor": items[-1]["line"] if more and items else None, "source": source, "record_category": SOURCE_CLASSES[source], "physical_truth_verified": False if source != "oracle" else None, "integrity": "not_verified_by_event_browser"}

    def verify_bytes(self, rid: str, alias: str) -> dict[str, Any]:
        directory, name = self.file(rid, alias)
        computed = hash_file(directory, name)
        expected = None
        if RUN_ID.fullmatch(rid):
            try:
                with open_regular(directory, "_manifest.json") as f:
                    expected = json.load(f).get("files", {}).get(alias, {}).get("sha256")
            except (OSError, ValueError, json.JSONDecodeError):
                pass
        else:
            with open_regular(directory, "observer-source-v1.json") as f:
                expected = json.load(f).get("sha256", {}).get(alias)
        return {"alias": alias, **computed, "expected_sha256": expected, "matches_expected": (hmac.compare_digest(expected, computed["sha256"]) if isinstance(expected, str) else None), "scope": "file-bytes-only", "causal_consistency_verified": False, "physical_truth_verified": False}


def _limits():
    import resource
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    resource.setrlimit(resource.RLIMIT_CPU, (1200, 1202))


def _stop_group(child: subprocess.Popen):
    if child.poll() is None:
        try:
            if os.name == "posix":
                os.killpg(child.pid, signal.SIGTERM)
            else:
                child.terminate()
        except ProcessLookupError:
            pass


def _kill_group(child: subprocess.Popen):
    if child.poll() is None:
        try:
            if os.name == "posix":
                os.killpg(child.pid, signal.SIGKILL)
            else:
                child.kill()
        except ProcessLookupError:
            pass


def create_app(*, core_root: Path | None = None, run_root: Path | None = None, archive_root: Path | None = None, token: str | None = None) -> FastAPI:
    core = core_root or Path(os.environ.get("I0_CORE_ROOT", Path(__file__).resolve().parents[2]))
    data = run_root or Path(os.environ.get("I0_OBSERVER_RUN_ROOT", Path.home() / ".local/share/individual-zero-observer/runs"))
    imports = archive_root or (Path(os.environ["I0_OBSERVER_ARCHIVE_ROOT"]) if os.environ.get("I0_OBSERVER_ARCHIVE_ROOT") else None)
    credential = token if token is not None else os.environ.get("I0_OBSERVER_TOKEN", "")
    if len(credential) < 24:
        raise ValueError("I0_OBSERVER_TOKEN must be at least 24 characters")
    observer = Observer(core_root=core, run_root=data, archive_root=imports)
    app = FastAPI(title="Individual Zero Observer", version="0.1.0", description="Local operator-only API, not a cognitive interface")
    app.state.observer = observer
    sessions: set[str] = set()
    session_lock = threading.Lock()

    def authenticated(request: Request):
        bearer = request.headers.get("authorization", "")
        cookie = request.cookies.get("iz_observer")
        verified = bearer.startswith("Bearer ") and hmac.compare_digest(bearer[7:], credential)
        with session_lock:
            verified = verified or (cookie in sessions if cookie else False)
        if not verified:
            raise HTTPException(401, "operator authentication required", headers={"WWW-Authenticate": "Bearer"})
        if request.method not in ("GET", "HEAD", "OPTIONS") and cookie and not bearer:
            origin = request.headers.get("origin")
            if not origin or origin.rstrip("/") != str(request.base_url).rstrip("/"):
                raise HTTPException(403, "invalid request origin")
        return True

    @app.middleware("http")
    async def security_headers(request: Request, call_next):
        result = await call_next(request)
        result.headers["X-Content-Type-Options"] = "nosniff"
        result.headers["Referrer-Policy"] = "no-referrer"
        result.headers["X-Frame-Options"] = "DENY"
        result.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
        result.headers["Cache-Control"] = "no-store"
        return result

    @app.get("/", include_in_schema=False)
    def homepage():
        return FileResponse(WEB / "index.html")

    @app.get("/assets/{asset}", include_in_schema=False)
    def asset(asset: str):
        if asset not in {"app.js", "style.css"}:
            raise HTTPException(404)
        return FileResponse(WEB / asset)

    @app.get("/api/health")
    def health():
        return {"service": "individual-zero-observer", "status": "up", "operator_authenticated": False}

    @app.post("/api/session")
    def login(request: Request, response: Response, credentials: SessionRequest):
        if not hmac.compare_digest(credentials.token, credential):
            raise HTTPException(401, "invalid operator credential")
        session = secrets.token_urlsafe(32)
        with session_lock:
            sessions.add(session)
        response.set_cookie("iz_observer", session, httponly=True, secure=request.url.scheme == "https", samesite="strict", path="/")
        return {"authenticated": True}

    @app.delete("/api/session", dependencies=[Depends(authenticated)])
    def logout(request: Request, response: Response):
        cookie = request.cookies.get("iz_observer")
        with session_lock:
            if cookie:
                sessions.discard(cookie)
        response.delete_cookie("iz_observer", path="/")
        return {"authenticated": False}

    @app.get("/api/settings", dependencies=[Depends(authenticated)])
    def settings():
        return {"bind_default": "127.0.0.1", "core_root": str(observer.core_root), "run_root": str(observer.run_root), "archive_import_enabled": observer.archive_root is not None, "core_commit": observer.commit, "core_worktree_dirty": observer.dirty, "maximum_concurrent_runs": 1, "scientific_acceptance_automatic": False}

    @app.get("/api/tests", dependencies=[Depends(authenticated)])
    def tests():
        return {"tests": CATALOG}

    @app.post("/api/runs", status_code=202, dependencies=[Depends(authenticated)])
    def start(params: RunRequest):
        return observer.start(params)

    @app.get("/api/runs", dependencies=[Depends(authenticated)])
    def runs(q: str = Query(default="", max_length=120), status: str = Query(default="", max_length=32), limit: int = Query(default=100, ge=1, le=200)):
        return {"runs": observer.list_runs(query=q, status=status, limit=limit)}

    @app.get("/api/runs/{rid}", dependencies=[Depends(authenticated)])
    def run(rid: str):
        return observer.detail(rid)

    @app.post("/api/runs/{rid}/cancel", dependencies=[Depends(authenticated)])
    def cancel(rid: str):
        return observer.cancel(rid)

    @app.get("/api/runs/{rid}/logs", dependencies=[Depends(authenticated)])
    def logs(rid: str, offset: int = Query(default=0, ge=0), limit: int = Query(default=65536, ge=1, le=65536)):
        directory, name = observer.file(rid, "log")
        with open_regular(directory, name) as stream:
            stream.seek(0, os.SEEK_END)
            end = stream.tell()
            if offset > end:
                raise HTTPException(416, "log offset beyond end")
            stream.seek(offset)
            buf = stream.read(limit)
        return {"text": buf.decode("utf-8", errors="replace"), "next_offset": offset + len(buf), "has_more": offset + len(buf) < end}

    @app.get("/api/runs/{rid}/events", dependencies=[Depends(authenticated)])
    def events(rid: str, source: str = "lab_events", cursor: int = Query(default=0, ge=0), limit: int = Query(default=50, ge=1, le=MAX_PAGE), kind: str = Query(default="", max_length=128), component: str = Query(default="", max_length=128), step: int | None = Query(default=None, ge=0), at: str = Query(default="", max_length=100), q: str = Query(default="", max_length=100)):
        return observer.events(rid, source=source, cursor=cursor, limit=limit, kind=kind, component=component, step=step, at=at, search=q)

    @app.get("/api/runs/{rid}/integrity/{alias}", dependencies=[Depends(authenticated)])
    def integrity(rid: str, alias: str):
        return observer.verify_bytes(rid, alias)

    @app.get("/api/runs/{rid}/file/{alias}", dependencies=[Depends(authenticated)])
    def download(rid: str, alias: str):
        parent, name = observer.file(rid, alias)
        stream = open_regular(parent, name)
        size = os.fstat(stream.fileno()).st_size
        def chunks() -> Iterator[bytes]:
            with stream:
                while payload := stream.read(65536):
                    yield payload
        return StreamingResponse(chunks(), media_type="application/octet-stream", headers={"Content-Disposition": f'attachment; filename="{name}"', "Content-Length": str(size)})

    @app.get("/api/runs/{rid}/archive.zip", dependencies=[Depends(authenticated)])
    def archive(rid: str):
        files = observer.files(rid)
        if not files:
            raise HTTPException(404, "no files to archive")
        fd, temp_name = tempfile.mkstemp(prefix="iz-observer-", suffix=".zip", dir=observer.run_root)
        os.close(fd)
        try:
            with zipfile.ZipFile(temp_name, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=3, allowZip64=True) as z:
                for entry in files:
                    parent, name = observer.file(rid, entry["alias"])
                    with open_regular(parent, name) as src, z.open(name, "w", force_zip64=True) as dest:
                        shutil.copyfileobj(src, dest, length=1024 * 1024)
            def zipped() -> Iterator[bytes]:
                try:
                    with open(temp_name, "rb") as f:
                        while chunk := f.read(65536):
                            yield chunk
                finally:
                    Path(temp_name).unlink(missing_ok=True)
            return StreamingResponse(zipped(), media_type="application/zip", headers={"Content-Disposition": f'attachment; filename="{rid}.zip"'})
        except BaseException:
            Path(temp_name).unlink(missing_ok=True)
            raise

    return app


def serve():
    import uvicorn
    # Lock BEFORE reading previous run receipts: two servers must never
    # disagree on who owns a live process or mark the other as interrupted.
    root = ensure_dir(Path(os.environ.get("I0_OBSERVER_RUN_ROOT", Path.home() / ".local/share/individual-zero-observer/runs")), create=True)
    if stat.S_IMODE(root.stat().st_mode) & 0o077:
        raise ValueError("run directory must be private (chmod 700)")
    fd = os.open(root / "_instance.lock", os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
    try:
        if os.name == "posix":
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        app = create_app(run_root=root)
        # A remote deployment requires a separately reviewed TLS/auth access layer.
        uvicorn.run(app, host="127.0.0.1", port=int(os.environ.get("I0_OBSERVER_PORT", "8765")), proxy_headers=False, workers=1)
    finally:
        os.close(fd)


if __name__ == "__main__":
    serve()
