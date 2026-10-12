import hashlib
import json

from observer_app.engine_replay import verify_engine_recording


def recorded_history(tmp_path, *, positions=None, outcome="normal"):
    positions = positions or [(1, 1), (2, 1)]
    journal = tmp_path / "journal.jsonl"
    previous = "00" * 32
    rows = []
    for step, (x, y) in enumerate(positions, 1):
        attempt = "a" + str(step)
        events = [
            {"kind": "step_opened", "t_monde": step, "attempt_ref": attempt},
            {"kind": "world_transition_experienced", "t_monde": step,
             "attempt_ref": attempt, "position_after": {"x": x, "y": y},
             "body_after": {"energy": 1}},
            {"kind": "step_closed", "t_monde": step, "attempt_ref": attempt,
             "data": {"outcome": outcome, "applied_command_count": 1,
                      "world_advance_count": 1}},
        ]
        for event in events:
            event_id = "event-" + str(len(rows))
            message = json.dumps({"event_id": event_id, "causal_event": event},
                                 sort_keys=True, separators=(",", ":")).encode()
            digest = hashlib.sha256(bytes.fromhex(previous) + message).hexdigest()
            rows.append({"index": len(rows), "event_id": event_id,
                         "previous_hash": previous, "event_hash": digest,
                         "causal_event": event})
            previous = digest
    original = b"\n".join(json.dumps(r, sort_keys=True, separators=(",", ":")).encode()
                          for r in rows)
    journal.write_bytes(original)
    frames_path = tmp_path / "world_frames.json"
    doc = {"schema": "observer-world-frames-v1",
           "identity": {"individual_id": "i0-vnext-stage11", "life_generation": 0},
           "geometry": {"coordinate_system": "grid-xy-top-left", "width": 4, "height": 4},
           "frames": [
               {"t_monde": i, "step_boundary": "committed", "attempt_ref": "a"+str(i),
                "individual_pose": {"x": x, "y": y}, "entities": []}
               for i, (x, y) in enumerate(positions, 1)],
           "attestation": {"journal_head_sha256": previous, "journal_event_count": len(rows),
                           "verifier": "lab.independent_journal_audit",
                           "verified_at": "2026-10-12T00:00:00Z",
                           "source_sha256": hashlib.sha256(original).hexdigest()}}
    frames_path.write_text(json.dumps(doc))
    report = {"individual_id": "i0-vnext-stage11",
              "steps_physically_executed": len(positions),
              "journal_event_count": len(rows), "journal_head_sha256": previous,
              "journal_bytes_sha256": hashlib.sha256(original).hexdigest(),
              "offline_audit_completed": True, "external_oracle_loaded": False,
              "external_bench_loaded": False, "terminal_deaths": 0}
    return frames_path, journal, report


def check(frames, journal, report, step=1):
    return verify_engine_recording(frames, journal, report=report,
                                   frame_hash=hashlib.sha256(frames.read_bytes()).hexdigest(),
                                   journal_hash=hashlib.sha256(journal.read_bytes()).hexdigest(),
                                   step=step)


def test_engine_history_map_after_complete_integrity_checks(tmp_path):
    frames, journal, report = recorded_history(tmp_path)
    result = check(frames, journal, report, step=2)
    assert result["available"] is True
    assert result["map_authorized"] is False if "map_authorized" in result else True
    assert result["capture_integrity_verified"] is True
    assert result["engine_pose_journal_match"] is True
    assert result["physical_truth_verified"] is False
    assert result["frame"]["individual_pose"] == {"x": 2, "y": 1}


def test_forged_pose_with_matching_recomputed_file_hash_rejected(tmp_path):
    frames, journal, report = recorded_history(tmp_path)
    data = json.loads(frames.read_text())
    data["frames"][0]["individual_pose"] = {"x": 3, "y": 3}
    frames.write_text(json.dumps(data))
    result = check(frames, journal, report)
    assert result["available"] is False
    assert result["reason"] == "engine_position_journal_mismatch"


def test_missing_producer_audit_rejected(tmp_path):
    frames, journal, report = recorded_history(tmp_path)
    report["offline_audit_completed"] = False
    assert check(frames, journal, report)["available"] is False


def test_different_individual_rejected(tmp_path):
    frames, journal, report = recorded_history(tmp_path)
    report["individual_id"] = "another-life"
    assert check(frames, journal, report)["reason"] == "individual_identity_mismatch"


def test_inconsistent_step_outcome_rejected(tmp_path):
    frames, journal, report = recorded_history(tmp_path, outcome="blocked")
    assert check(frames, journal, report)["reason"] == "uncommitted_or_nonphysical_step"


def test_outside_recorded_history_is_unavailable(tmp_path):
    frames, journal, report = recorded_history(tmp_path)
    result = check(frames, journal, report, step=3)
    assert result["available"] is False
    assert result["reason"] == "step_outside_recorded_life"


def test_world_custody_refuses_hidden_oracle_material(tmp_path):
    frames, journal, report = recorded_history(tmp_path)
    document = json.loads(frames.read_text())
    document["oracle_canary"] = "secret"
    frames.write_text(json.dumps(document))
    assert check(frames, journal, report)["reason"] == "invalid_geometry_archive"
