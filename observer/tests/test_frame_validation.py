import json

from observer_app.frame_validation import validate_frames


def fixture():
    return {
        "schema": "observer-world-frames-v1",
        "identity": {"individual_id": "i0", "life_generation": 0},
        "geometry": {"coordinate_system": "grid-xy-top-left", "width": 8, "height": 5},
        "frames": [
            {"t_monde": 1, "attempt_ref": "a", "step_boundary": "committed", "individual_pose": {"x": 1, "y": 2},
             "entities": [{"id": "water", "kind": "resource", "position": {"x": 3, "y": 4}}]},
            {"t_monde": 2, "attempt_ref": "b", "step_boundary": "committed", "individual_pose": {"x": 2, "y": 2}, "entities": []}
        ],
        "attestation": {"journal_head_sha256": "a" * 64, "journal_event_count": 2,
                        "verifier": "example-not-trusted", "verified_at": "2026-10-12T00:00:00Z",
                        "source_sha256": "b" * 64}
    }


def check(tmp_path, data):
    path = tmp_path / "frames.json"
    path.write_text(json.dumps(data))
    return validate_frames(path)


def test_valid_frame_structure_is_not_authoritative(tmp_path):
    result = check(tmp_path, fixture())
    assert result["structurally_valid"] is True
    assert result["frame_count"] == 2
    assert result["independently_verified"] is False
    assert result["map_authorized"] is False


def test_duplicate_steps_rejected(tmp_path):
    data = fixture()
    data["frames"][1]["t_monde"] = 1
    assert "unordered_or_uncommitted_step" in check(tmp_path, data)["errors"]


def test_out_of_bounds_position_rejected(tmp_path):
    data = fixture()
    data["frames"][0]["individual_pose"]["x"] = 8
    assert "invalid_individual_position" in check(tmp_path, data)["errors"]


def test_duplicate_entity_identity_rejected(tmp_path):
    data = fixture()
    data["frames"][0]["entities"].append(data["frames"][0]["entities"][0].copy())
    assert "duplicate_or_invalid_entity" in check(tmp_path, data)["errors"]


def test_boolean_step_rejected(tmp_path):
    data = fixture()
    data["frames"][0]["t_monde"] = True
    assert "unordered_or_uncommitted_step" in check(tmp_path, data)["errors"]


def test_oversized_archive_rejected(tmp_path):
    path = tmp_path / "frames.json"
    path.write_bytes(b" " * (16 * 1024 * 1024 + 1))
    assert "archive_too_large" in validate_frames(path)["errors"]


def test_duplicate_json_keys_rejected(tmp_path):
    path = tmp_path / "frames.json"
    document = json.dumps(fixture())
    path.write_text(document.replace('"width": 8', '"width": 8, "width": 8'))
    result = validate_frames(path)
    assert result["structurally_valid"] is False
    assert "unreadable_json" in result["errors"]


def test_nonfinite_json_values_rejected(tmp_path):
    path = tmp_path / "frames.json"
    document = json.dumps(fixture())
    path.write_text(document.replace('"width": 8', '"width": NaN'))
    result = validate_frames(path)
    assert result["structurally_valid"] is False
    assert "unreadable_json" in result["errors"]
