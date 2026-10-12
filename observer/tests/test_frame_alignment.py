import hashlib
import json

from observer_app.frame_alignment import compare_frames_to_journal


def make_files(tmp_path, frame_step=1, close=True):
    journal = tmp_path / "journal"
    previous = "00" * 32
    events = [{"kind": "step_opened", "t_monde": 1, "attempt_ref": "a"}]
    if close:
        events.append({"kind": "step_closed", "t_monde": 1, "attempt_ref": "a"})
    rows = []
    for i, event in enumerate(events):
        eid = f"e{i}"
        payload = json.dumps({"event_id": eid, "causal_event": event}, sort_keys=True, separators=(",", ":")).encode()
        digest = hashlib.sha256(bytes.fromhex(previous) + payload).hexdigest()
        rows.append({"index": i, "event_id": eid, "previous_hash": previous,
                     "event_hash": digest, "causal_event": event})
        previous = digest
    journal.write_bytes(b"\n".join(json.dumps(r, sort_keys=True, separators=(",", ":")).encode() for r in rows))
    frames = tmp_path / "frames"
    frames.write_text(json.dumps({
        "schema": "observer-world-frames-v1",
        "identity": {"individual_id": "i0", "life_generation": 0},
        "geometry": {"coordinate_system": "grid-xy-top-left", "width": 4, "height": 4},
        "frames": [{"t_monde": frame_step, "attempt_ref": "a", "step_boundary": "committed",
                    "individual_pose": {"x": 1, "y": 1}, "entities": []}],
        "attestation": {"journal_head_sha256": "a" * 64, "journal_event_count": 2,
                        "verifier": "untrusted", "verified_at": "2026-10-12T00:00:00Z",
                        "source_sha256": "b" * 64}
    }))
    return frames, journal


def test_matching_recorded_step_still_not_authoritative(tmp_path):
    frames, journal = make_files(tmp_path)
    result = compare_frames_to_journal(frames, journal)
    assert result["frame_step_alignment"] is True
    assert result["independently_verified"] is False
    assert result["map_authorized"] is False


def test_frame_at_unclosed_step_rejected(tmp_path):
    frames, journal = make_files(tmp_path, frame_step=2)
    assert compare_frames_to_journal(frames, journal)["error"] == "frame_at_unclosed_step"


def test_open_only_step_rejected(tmp_path):
    frames, journal = make_files(tmp_path, close=False)
    assert compare_frames_to_journal(frames, journal)["error"] == "invalid_recorded_step_boundaries"


def test_frame_attempt_must_match_recorded_closed_step(tmp_path):
    frames, journal = make_files(tmp_path)
    document = json.loads(frames.read_text())
    document["frames"][0]["attempt_ref"] = "different-attempt"
    frames.write_text(json.dumps(document))
    result = compare_frames_to_journal(frames, journal)
    assert result["frame_step_alignment"] is False
    assert result["error"] == "frame_attempt_mismatch"
    assert result["map_authorized"] is False
