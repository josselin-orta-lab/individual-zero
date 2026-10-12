import hashlib
import json

from observer_app.journal_preflight import check_chain


def make_chain(path, count=2):
    previous = "00" * 32
    rows = []
    for i in range(count):
        eid = f"event-{i}"
        event = {"kind": "test", "t_monde": i}
        body = json.dumps({"causal_event": event, "event_id": eid}, sort_keys=True, separators=(",", ":")).encode()
        digest = hashlib.sha256(bytes.fromhex(previous) + body).hexdigest()
        rows.append({"index": i, "event_id": eid, "previous_hash": previous,
                     "event_hash": digest, "causal_event": event})
        previous = digest
    path.write_bytes(b"\n".join(json.dumps(row, sort_keys=True, separators=(",", ":")).encode() for row in rows))
    return previous


def test_chain_valid_but_not_full_causal_audit(tmp_path):
    path = tmp_path / "journal"
    head = make_chain(path)
    result = check_chain(path, expected_head=head, expected_count=2)
    assert result["chain_valid"] is True
    assert result["trusted_tail_verified"] is True
    assert result["full_causal_audit"] is False
    assert result["map_authorized"] is False


def test_self_contained_chain_does_not_prove_complete_tail(tmp_path):
    path = tmp_path / "journal"
    make_chain(path, count=1)
    result = check_chain(path)
    assert result["chain_valid"] is True
    assert result["trusted_tail_verified"] is False


def test_truncation_detected_by_independent_expected_count(tmp_path):
    path = tmp_path / "journal"
    head = make_chain(path, count=1)
    result = check_chain(path, expected_head=head, expected_count=2)
    assert result["trusted_tail_verified"] is False
    assert result["error"] == "trusted_count_mismatch"


def test_corrupted_event_detected(tmp_path):
    path = tmp_path / "journal"
    make_chain(path)
    path.write_bytes(path.read_bytes().replace(b'"kind":"test"', b'"kind":"fake"', 1))
    assert check_chain(path)["chain_valid"] is False
