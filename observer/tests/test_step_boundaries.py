import hashlib
import json

from observer_app.step_boundaries import check_step_boundaries


def write_journal(path, events):
    previous = "00" * 32
    rows = []
    for i, event in enumerate(events):
        eid = f"e{i}"
        body = json.dumps({"event_id": eid, "causal_event": event}, sort_keys=True, separators=(",", ":")).encode()
        digest = hashlib.sha256(bytes.fromhex(previous) + body).hexdigest()
        rows.append({"index": i, "event_id": eid, "previous_hash": previous,
                     "event_hash": digest, "causal_event": event})
        previous = digest
    path.write_bytes(b"\n".join(json.dumps(x, sort_keys=True, separators=(",", ":")).encode() for x in rows))


def event(kind, step=1, attempt="attempt"):
    return {"kind": kind, "t_monde": step, "attempt_ref": attempt}


def test_closed_step_preflight_is_not_map_authorization(tmp_path):
    path = tmp_path / "journal"
    write_journal(path, [event("step_opened"), event("step_closed")])
    result = check_step_boundaries(path)
    assert result["recorded_boundaries_valid"] is True
    assert result["closed_steps"] == [1]
    assert result["map_authorized"] is False
    assert result["full_causal_audit"] is False


def test_open_step_is_not_closed(tmp_path):
    path = tmp_path / "journal"
    write_journal(path, [event("step_opened")])
    assert check_step_boundaries(path)["recorded_boundaries_valid"] is False


def test_mismatched_attempt_rejected(tmp_path):
    path = tmp_path / "journal"
    write_journal(path, [event("step_opened"), event("step_closed", attempt="other")])
    assert check_step_boundaries(path)["recorded_boundaries_valid"] is False


def test_event_after_death_rejected(tmp_path):
    path = tmp_path / "journal"
    write_journal(path, [event("step_opened"), event("individual_death_confirmed"),
                         event("command_experienced"), event("step_closed")])
    assert check_step_boundaries(path)["recorded_boundaries_valid"] is False


def test_terminal_close_accepted_without_reanimation(tmp_path):
    path = tmp_path / "journal"
    write_journal(path, [event("step_opened"), event("individual_death_confirmed"),
                         event("step_closed")])
    result = check_step_boundaries(path)
    assert result["recorded_boundaries_valid"] is True
    assert result["terminal_death_recorded"] is True
