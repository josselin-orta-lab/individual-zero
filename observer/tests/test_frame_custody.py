import hashlib
import json

from observer_app.frame_custody import check_custody


def sources(tmp_path):
    journal = tmp_path / "journal"
    event = {"kind": "step_opened", "t_monde": 1, "attempt_ref": "a"}
    close = {"kind": "step_closed", "t_monde": 1, "attempt_ref": "a"}
    previous = "00" * 32
    rows = []
    for i, e in enumerate([event, close]):
        eid = f"e{i}"
        payload = json.dumps({"event_id": eid, "causal_event": e}, sort_keys=True, separators=(",", ":")).encode()
        digest = hashlib.sha256(bytes.fromhex(previous) + payload).hexdigest()
        rows.append({"index": i, "event_id": eid, "previous_hash": previous,
                     "event_hash": digest, "causal_event": e})
        previous = digest
    journal.write_bytes(b"\n".join(json.dumps(x, sort_keys=True, separators=(",", ":")).encode() for x in rows))
    frames = tmp_path / "frames"
    data = {"schema": "observer-world-frames-v1",
            "identity": {"individual_id": "i0", "life_generation": 0, "attempt_ref": "a"},
            "geometry": {"coordinate_system": "grid-xy-top-left", "width": 4, "height": 4},
            "frames": [{"t_monde": 1, "step_boundary": "committed",
                        "individual_pose": {"x": 1, "y": 1}, "entities": []}],
            "attestation": {"journal_head_sha256": previous, "journal_event_count": 2,
                            "verifier": "untrusted", "verified_at": "2026-10-12T00:00:00Z",
                            "source_sha256": "b" * 64}}
    frames.write_text(json.dumps(data))
    return frames, journal, previous


def test_matching_external_anchors_still_not_physical_truth(tmp_path):
    frames, journal, head = sources(tmp_path)
    result = check_custody(frames, journal, trusted_frame_sha256=hashlib.sha256(frames.read_bytes()).hexdigest(),
                          trusted_journal_head=head, trusted_journal_count=2)
    assert result["operator_anchor_match"] is True
    assert result["anchor_provenance_verified"] is False
    assert result["frame_claims_match"] is True
    assert result["recorded_step_alignment"] is True
    assert result["physical_truth_verified"] is False
    assert result["map_authorized"] is False


def test_wrong_external_frame_digest_rejected(tmp_path):
    frames, journal, head = sources(tmp_path)
    result = check_custody(frames, journal, trusted_frame_sha256="0" * 64,
                          trusted_journal_head=head, trusted_journal_count=2)
    assert result["error"] == "frame_anchor_mismatch"


def test_wrong_external_journal_count_rejected(tmp_path):
    frames, journal, head = sources(tmp_path)
    result = check_custody(frames, journal, trusted_frame_sha256=hashlib.sha256(frames.read_bytes()).hexdigest(),
                          trusted_journal_head=head, trusted_journal_count=3)
    assert result["error"] == "journal_anchor_mismatch"
