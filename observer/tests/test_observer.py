"""Fast isolated tests; fake Core CLI instead of invoking any scientific campaign."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
import time
import zipfile
from io import BytesIO

import pytest
from fastapi.testclient import TestClient

from observer_app.app import Observer, atomic_json, create_app, open_regular

TOKEN = "a" * 48


@pytest.fixture
def layout(tmp_path):
    core = tmp_path / "core"
    (core / "src/lab").mkdir(parents=True)
    (core / "tests").mkdir()
    (core / "src/lab/cli.py").write_text('''
import argparse,json
p=argparse.ArgumentParser()
p.add_argument('--cycles',type=int);p.add_argument('--seed',type=int)
p.add_argument('--run-id');p.add_argument('--output')
a=p.parse_args()
with open(a.output,'w') as f:
    for cycle in range(a.cycles):
        f.write(json.dumps({'run_id':a.run_id,'kind':'tick','cycle':cycle,'data':{'seed':a.seed}})+'\\n')
print('bootstrap fixture executed')
''')
    (core / "src/lab/stage11_autonomous_600_step_probe.py").write_text('''
import argparse,json,time
p=argparse.ArgumentParser();p.add_argument('--steps',type=int);a=p.parse_args()
time.sleep(1.0)
print('stage11_autonomous_600_step='+json.dumps({'steps_physically_executed':a.steps,'classification':'fixture_only'}))
''')
    (core / "tests/test_causal_journal.py").write_text("import unittest\nclass T(unittest.TestCase):\n def test_ok(self): self.assertTrue(True)\n")
    root = tmp_path / "runs"
    archive = tmp_path / "archives"
    archive.mkdir()
    return core, root, archive


@pytest.fixture
def client(layout):
    core, root, archive = layout
    with TestClient(create_app(core_root=core, run_root=root, archive_root=archive, token=TOKEN)) as c:
        response = c.post("/api/session", json={"token": TOKEN})
        assert response.status_code == 200
        yield c


def wait(c, rid, terminal=("SUCCESS", "FAILED", "INTERRUPTED", "CANCELLED")):
    for _ in range(110):
        data = c.get(f"/api/runs/{rid}").json()
        if data["status"] in terminal:
            return data
        time.sleep(0.04)
    pytest.fail(f"run {rid} did not finish")


def test_authentication_and_csrf(layout):
    core, root, archive = layout
    with TestClient(create_app(core_root=core, run_root=root, archive_root=archive, token=TOKEN)) as c:
        assert c.get("/api/health").status_code == 200
        assert c.get("/api/runs").status_code == 401
        assert c.post("/api/session", json={"token": "wrong"}).status_code == 401
        assert c.post("/api/session", json={"token": TOKEN}).status_code == 200
        assert c.get("/api/runs").status_code == 200
        assert c.post("/api/runs", json={"test_id": "bootstrap"}, headers={"Origin": "http://evil.invalid"}).status_code == 403
        assert c.post("/api/runs", json={"test_id": "bootstrap"}, headers={"Origin": "http://testserver"}).status_code == 202
        assert c.delete("/api/session", headers={"Origin": "http://testserver"}).status_code == 200
        assert c.get("/api/runs").status_code == 401


def test_catalog_strict_validation(client):
    assert client.get("/api/tests").status_code == 200
    for value in [
        {"test_id": "arbitrary", "seed": 0},
        {"test_id": "bootstrap", "seed": -1},
        {"test_id": "bootstrap", "steps": 50},
        {"test_id": "journal_unit", "seed": 4},
        {"test_id": "mortal_stage11", "seed": 4},
        {"test_id": "bootstrap", "seed": "1"},
        {"test_id": "bootstrap", "seed": True},
        {"test_id": "bootstrap", "output": "/etc/passwd"},
    ]:
        assert client.post("/api/runs", json=value, headers={"Origin": "http://testserver"}).status_code == 422


def test_bootstrap_endpoints_archive_and_original_preserved(client, layout):
    core, root, archive = layout
    r = client.post("/api/runs", json={"test_id": "bootstrap", "seed": 12, "cycles": 4}, headers={"Origin": "http://testserver"})
    assert r.status_code == 202
    run = wait(client, r.json()["id"])
    assert run["status"] == "SUCCESS", run
    assert run["technical_success"] is True
    assert run["assertions_passed"] is None  # bootstrap is not an assertion suite
    assert run["scientific_validation"] is None
    assert run["operator_validation"] is None
    assert run["executed_steps"] is None
    rid = run["id"]
    p = root / rid / "events.jsonl"
    before = p.read_bytes()
    browse = client.get(f"/api/runs/{rid}/events", params={"source": "lab_events", "limit": 2}).json()
    assert [x["raw"]["cycle"] for x in browse["items"]] == [0, 1]
    assert browse["next_cursor"] == 2
    second = client.get(f"/api/runs/{rid}/events", params={"source": "lab_events", "limit": 2, "cursor": 2}).json()
    assert [x["raw"]["cycle"] for x in second["items"]] == [2, 3]
    assert second["next_cursor"] is None
    assert client.get(f"/api/runs/{rid}/events", params={"source": "oracle"}).status_code == 404
    filtered = client.get(f"/api/runs/{rid}/events", params={"source": "lab_events", "step": 2}).json()
    assert len(filtered["items"]) == 1
    assert filtered["items"][0]["category"] == "lab_telemetry"
    assert client.get(f"/api/runs/{rid}/events", params={"source": "../passwd"}).status_code == 422
    digest = client.get(f"/api/runs/{rid}/integrity/lab_events").json()
    assert digest["matches_expected"] is True
    assert digest["sha256"] == hashlib.sha256(before).hexdigest()
    assert client.get(f"/api/runs/{rid}/file/lab_events").content == before
    assert client.get(f"/api/runs/{rid}/file/../../etc/passwd").status_code in (404, 422)
    zipped = client.get(f"/api/runs/{rid}/archive.zip")
    assert zipped.status_code == 200
    with zipfile.ZipFile(BytesIO(zipped.content)) as z:
        assert z.read("events.jsonl") == before
    assert p.read_bytes() == before
    assert "events.jsonl" in [x["name"] for x in run["artifacts"]]
    assert client.get(f"/api/runs/{rid}/logs").json()["text"].find("fixture executed") != -1


def test_cancel_and_concurrent_runs(client):
    r = client.post("/api/runs", json={"test_id": "mortal_stage11", "steps": 20}, headers={"Origin": "http://testserver"})
    assert r.status_code == 202
    rid = r.json()["id"]
    assert client.post("/api/runs", json={"test_id": "bootstrap"}, headers={"Origin": "http://testserver"}).status_code == 409
    assert client.post(f"/api/runs/{rid}/cancel", headers={"Origin": "http://testserver"}).status_code == 200
    run = wait(client, rid)
    assert run["status"] == "CANCELLED"
    assert run["scientific_validation"] is None


def test_restart_marks_incomplete_and_does_not_claim_success(layout):
    core, root, archive = layout
    o = Observer(core_root=core, run_root=root, archive_root=archive)
    rid = "r-" + "b" * 32
    d = root / rid
    d.mkdir(mode=0o700)
    atomic_json(d / "_status.json", {"schema": "observer-run-v1", "id": rid, "status": "RUNNING", "test_id": "bootstrap"})
    Observer(core_root=core, run_root=root, archive_root=archive)
    data = o._local_status(rid)
    assert data["status"] == "INTERRUPTED"
    assert data["technical_success"] is None
    assert data["assertions_passed"] is None


def test_imported_oracle_raw_truth_is_separate_and_traversal_rejected(client, layout):
    _, _, archive = layout
    folder = archive / "science-001"
    folder.mkdir()
    rows = [
        {"sequence": 0, "kind": "ground_truth", "data": {"energy": 42}},
        {"sequence": 1, "kind": "ground_truth", "data": {"energy": 43}},
    ]
    content = "".join(json.dumps(r)+"\n" for r in rows).encode()
    (folder / "oracle.jsonl").write_bytes(content)
    (folder / "observer-source-v1.json").write_text(json.dumps({"schema": "observer-source-v1", "files": {"oracle": "oracle.jsonl"}, "sha256": {"oracle": hashlib.sha256(content).hexdigest()}, "metadata": {"case": "fixture_only"}}))
    r = client.get("/api/runs").json()["runs"]
    assert any(x["id"] == "import-science-001" and x["status"] == "IMPORTED" for x in r)
    details = client.get("/api/runs/import-science-001").json()
    assert details["artifacts"][0]["category"] == "oracle_declared_source"
    assert details["scientific_validation"] is None
    assert client.get("/api/runs/import-science-001/events", params={"source": "oracle"}).json()["items"][0]["raw"] == rows[0]
    assert client.get("/api/runs/import-science-001/integrity/oracle").json()["matches_expected"] is True
    (folder / "oracle.jsonl").write_text("modified\n")
    assert client.get("/api/runs/import-science-001/integrity/oracle").json()["matches_expected"] is False
    (folder / "oracle.jsonl").unlink()
    (folder / "oracle.jsonl").symlink_to("/etc/passwd")
    assert client.get("/api/runs/import-science-001").status_code == 404
    bad = archive / "escape"
    bad.mkdir()
    (bad / "observer-source-v1.json").write_text('{"schema":"observer-source-v1","files":{"journal":"../../etc/passwd"}}')
    assert not any(x["id"] == "import-escape" for x in client.get("/api/runs").json()["runs"])


def test_journal_categories_and_corruption_reported(client, layout):
    _, _, archive = layout
    folder = archive / "causal"
    folder.mkdir()
    row = {"index": 0, "event_id": "birth-001", "previous_hash": "0" * 64, "event_hash": "a" * 64, "causal_event": {"kind": "perceptual_capture", "t_monde": 1, "data": {"position": {"x": 1, "y": 2}}}}
    (folder / "journal.jsonl").write_text(json.dumps(row)+"\ninvalid json\n")
    (folder / "observer-source-v1.json").write_text(json.dumps({"schema": "observer-source-v1", "files": {"journal": "journal.jsonl"}}))
    got = client.get("/api/runs/import-causal/events", params={"source": "journal"}).json()
    assert len(got["items"]) == 2
    assert got["items"][0]["kind"] == "perceptual_capture"
    assert got["items"][0]["step"] == 1
    assert got["items"][0]["category"] == "causal_journal"
    assert got["items"][1]["integrity_error"] == "invalid_jsonl_record"
    assert got["integrity"] == "not_verified_by_event_browser"


def test_fixed_unittest_and_stage11_fixture_report(client):
    r = client.post("/api/runs", json={"test_id": "journal_unit"}, headers={"Origin": "http://testserver"})
    assert r.status_code == 202
    data = wait(client, r.json()["id"])
    assert data["status"] == "SUCCESS", data
    assert data["assertions_passed"] is True
    r = client.post("/api/runs", json={"test_id": "mortal_stage11", "steps": 7}, headers={"Origin": "http://testserver"})
    data = wait(client, r.json()["id"])
    assert data["status"] == "SUCCESS", data
    assert data["executed_steps"] == 7
    assert data["assertions_passed"] is True
    assert data["scientific_validation"] is None
    report = client.get(f"/api/runs/{data['id']}/file/result").json()
    assert report["classification"] == "fixture_only"
