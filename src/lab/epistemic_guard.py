"""Pure, versioned epistemic guard for the Lab -> I0 autobiographical boundary.

No world, journal owner, Oracle, Bench or cognitive-module imports. A technical
occurrence is not permission to learn its payload. Known Stage-7 nested data
objects are projected field-by-field, never copied as opaque dictionaries.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Mapping


_LEAF = object()

_GOAL = {
    key: _LEAF for key in (
        "id", "goal_type", "target", "satisfaction_condition",
        "principal_measure", "current_pressure", "state",
        "activation_t", "activation_cycle", "justification_ref",
    )
}
_BODY = {key: _LEAF for key in ("energy", "food", "water", "integrity")}
_COMPARISON_EFFECT = {
    key: _LEAF for key in (
        "variable", "predicted", "observed", "precision", "status",
        "comparator_version", "deadline_t_monde",
    )
}

# Current lived Stage-7 event shapes, NOT technical journal schemas. New
# nested cognitive fields require explicit review here; unknown fields are
# still retained without loss in the full technical journal.
_LIVED_DATA_SCHEMAS = {
    "active_goal_changed": {"before": _GOAL, "after": _GOAL},
    "s_t_published": {
        "version": _LEAF, "competitive_refs": (_LEAF,),
    },
    "agency_comparison": {
        "option_ref": _LEAF, "sent_t_monde": _LEAF,
        "observed_t_monde": _LEAF, "status": _LEAF,
        "attribution": _LEAF, "effects": (_COMPARISON_EFFECT,),
    },
    "episode_closed": {
        "id": _LEAF, "start_t_monde": _LEAF,
        "end_t_monde": _LEAF, "event_refs": (_LEAF,),
        "boundary_type": _LEAF, "active_goal_ref": _LEAF,
        "body_start": _BODY, "body_end": _BODY,
        "cumulative_reward": _LEAF, "surprise": _LEAF,
        "linked_previous_ref": _LEAF,
    },
    "memory_recall_proposed": {
        "episode_ref": _LEAF, "subject_ref": _LEAF,
        "contribution_ref": _LEAF,
    },
    "intention_created": {
        "intention_ref": _LEAF, "goal_type": _LEAF,
        "target": _LEAF, "trigger_type": _LEAF,
        "deadline_step": _LEAF, "base_pressure": _LEAF,
        "wake_authorized": _LEAF,
    },
    "intention_triggered": {
        "intention_ref": _LEAF, "contribution_ref": _LEAF,
        "goal_proposal_ref": _LEAF, "current_pressure": _LEAF,
    },
}

# Forbidden even nested under neutral-looking fields. Do not reject danger
# zones or scenario payloads in general: valid hidden-hazard operations MUST
# remain in the full technical journal for independent audit.
_EXTERNAL_TRUTH_KEYS = frozenset({
    "oracle_canary", "oracle_ground_truth", "oracle_token",
    "oracle_capability", "ground_truth", "evaluation_trace",
    "bench_metrics", "benchmark_truth", "benchmark_label",
})
_EXTERNAL_TRUTH_KINDS = frozenset({
    "oracle_read", "oracle_annotation", "oracle_ground_truth",
    "benchmark_truth_injected",
})
_EXTERNAL_PROVENANCE = frozenset({
    "oracle", "evaluation_bench", "evaluation_trace",
})

# Audit indices and hidden map truth may exist in technical custody, but
# have no role as first-person memories.
_FORBIDDEN_LIVED_KEYS = _EXTERNAL_TRUTH_KEYS | frozenset({
    "attempt_ref", "previous_hash", "event_hash", "journal_index",
    "technical_counter", "future_scenario_schedule", "scenario_schedule",
    "lethal_zones", "danger_zones",
})


def has_external_truth(value: object) -> bool:
    """Detect explicit Oracle/Bench evidence anywhere inside an I0 record."""
    if isinstance(value, Mapping):
        for key, item in value.items():
            if not isinstance(key, str):
                continue
            name = key.casefold()
            if name in _EXTERNAL_TRUTH_KEYS:
                return True
            if name in {"oracle_derived", "hidden_world_oracle_used"} and item is True:
                return True
            if name == "kind" and isinstance(item, str) and item in _EXTERNAL_TRUTH_KINDS:
                return True
            if name in {"source", "emitter", "provenance_source"} and (
                isinstance(item, str) and item.casefold() in _EXTERNAL_PROVENANCE
            ):
                return True
            if has_external_truth(item):
                return True
    elif isinstance(value, (list, tuple)):
        return any(has_external_truth(item) for item in value)
    return False


def _has_forbidden_lived_key(value: object) -> bool:
    if isinstance(value, Mapping):
        return any(
            (isinstance(key, str) and key.casefold() in _FORBIDDEN_LIVED_KEYS)
            or _has_forbidden_lived_key(item)
            for key, item in value.items()
        )
    if isinstance(value, (list, tuple)):
        return any(_has_forbidden_lived_key(item) for item in value)
    return False


def _project_selected(value: object, schema: object) -> object:
    if schema is _LEAF:
        if value is None or type(value) in (str, int, float, bool):
            return deepcopy(value)
        raise ValueError("autobiographical scalar cannot contain hidden nested data")
    if value is None:
        return None
    if isinstance(schema, dict):
        if not isinstance(value, Mapping):
            raise ValueError("autobiographical structured field must be a mapping")
        return {
            key: _project_selected(value[key], child)
            for key, child in schema.items() if key in value
        }
    if isinstance(schema, tuple) and len(schema) == 1:
        if not isinstance(value, (list, tuple)):
            raise ValueError("autobiographical sequence field must be a sequence")
        return [_project_selected(item, schema[0]) for item in value]
    raise ValueError("invalid internal autobiographical projection schema")


def project_lived_field(*, kind: str, field: str, value: object) -> object:
    """Return detached cognitive data, stripping unapproved nested fields."""
    if field == "data":
        schema = _LIVED_DATA_SCHEMAS.get(kind)
        if schema is None or not isinstance(value, Mapping):
            raise ValueError("unregistered nested autobiographical event data")
        result = _project_selected(value, schema)
    else:
        result = deepcopy(value)
    if has_external_truth(result) or _has_forbidden_lived_key(result):
        raise ValueError("hidden technical/oracle facts cannot enter autobiography")
    return result


def validate_lived_field_name(field: str) -> None:
    if (
        not isinstance(field, str) or not field
        or field.casefold() in _FORBIDDEN_LIVED_KEYS
    ):
        raise ValueError("technical/oracle field is not autobiographically visible")
