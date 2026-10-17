"""I1-only canonical Value/Needs active form for consolidated lived affordances.

This remains the ONE Value/Needs causal owner. The extra form is a strictly
non-authoritative, versioned, read-only advisory index, not learned TD weights,
a safety rule, an inferred cause, an active plan or a second motor authority.
The I0 source snapshot and legacy experimental owner exports stay untouched.
"""
from __future__ import annotations

from copy import deepcopy
from math import isfinite

from i1.modules.value_needs import ValueAndNeeds
from .determinism import canonical_causal_bytes, sha256_hex

ACTIVE_FORM_KEY = "i1_active_observed_procedures"
ACTIVE_FORM_SCHEMA_KEY = "i1_active_observed_procedures_schema"
SCHEMA = "i1-observed-procedural-advisory-v1"
# The coordinator publishes all four forms as ONE validated candidate.
# Value/Needs owns only its own form, never the other owners' state.
EXPECTED_ACTIVE_OWNERS = frozenset({
    "value_needs", "causal_model", "perception", "metacognition_health",
})
_SOURCE_FIELDS = frozenset({
    "id", "plan_signature", "primitive", "parameters", "observed_field",
    "evidence_scope", "goal_success_inferred", "safety_certified",
    "near_context", "preconditions", "source_episode_refs",
    "source_event_refs", "trial_episode_refs", "trial_event_refs",
    "distinct_success_count", "distinct_trial_count", "success_rate", "state",
})
_ALLOWED_FIELDS = {
    "boire": "drank",
    "collecter": "collected",
    "fabriquer_outil": "tool_crafted",
    "poser_une_pierre": "stone_placed",
}


def validate_advisory_rows(rows):
    """Reject unsupported active semantics and untraceable numerical credits."""
    if type(rows) is not list:
        raise ValueError("I1 active observations must be a list")
    seen = set()
    for row in rows:
        if type(row) is not dict or set(row) != _SOURCE_FIELDS:
            # Unknown fields can carry unreviewed authority/effect claims.
            # Active cognition accepts exactly the witnessed private schema.
            raise ValueError("unrecognized active cognitive evidence fields")
        primitive = row.get("primitive")
        if (type(row.get("id")) is not str or not row["id"].startswith("skill:")
                or row["id"] in seen or primitive not in _ALLOWED_FIELDS
                or row.get("observed_field") != _ALLOWED_FIELDS[primitive]
                or type(row.get("parameters")) is not dict
                or row.get("state") != "compiled_private"
                or row.get("evidence_scope")
                    != "experienced_local_physical_result"
                or row.get("safety_certified") is not False
                or row.get("goal_success_inferred") is not False
                or row.get("preconditions") != []):
            raise ValueError("I1 advisory cannot claim causality or safety")
        context = row.get("near_context")
        if (type(context) is not dict or set(context) != {"x", "y", "radius"}
                or any(type(value) is not int for value in context.values())
                or context["radius"] < 0):
            raise ValueError("unverified active observation spatial context")
        successful = row.get("source_episode_refs")
        attempts = row.get("trial_episode_refs")
        success_events = row.get("source_event_refs")
        attempt_events = row.get("trial_event_refs")
        for items in (successful, attempts, success_events, attempt_events):
            if (type(items) is not list or not items
                    or any(type(ref) is not str or not ref for ref in items)
                    or len(set(items)) != len(items)):
                raise ValueError("invalid independent active evidence references")
        if (not set(successful).issubset(attempts)
                or not set(success_events).issubset(attempt_events)
                or len(successful) != row.get("distinct_success_count")
                or len(attempts) != row.get("distinct_trial_count")
                or len(successful) < 2):
            raise ValueError("active evidence threshold or provenance not met")
        confidence = row.get("success_rate")
        if (type(confidence) not in (float, int)
                or not isfinite(confidence)
                or confidence != len(successful) / len(attempts)):
            raise ValueError("unreconciled active empirical rate")
        signature = sha256_hex(canonical_causal_bytes({
            "primitive": primitive, "parameters": row["parameters"],
            "observed_field": row["observed_field"],
        }))
        context_signature = row.get("plan_signature")
        if context_signature != "observed_primitive:" + signature:
            raise ValueError("active procedure is not bound to its physical primitive")
        expected_ref = "skill:" + sha256_hex(canonical_causal_bytes({
            "signature": signature, "anchor": [context["x"], context["y"]],
        }))[:28]
        if row["id"] != expected_ref:
            raise ValueError("active procedure identifier is not provenance-derived")
        canonical_causal_bytes(row)
        seen.add(row["id"])
    if [row["id"] for row in rows] != sorted(seen):
        raise ValueError("active observation order must be deterministic")


class I1ActiveValueNeeds(ValueAndNeeds):
    """Single Value/Needs owner with an extra non-executable observed form."""

    def __init__(self, config):
        super().__init__(config)
        self._i1_active_observed_procedures = []

    def active_observed_procedures(self):
        """Read a detached committed owner view for UC-paid option evaluation."""
        return deepcopy(self._i1_active_observed_procedures)

    def matching_active_observed_procedures(
        self, *, primitive, parameters, observed_field,
    ):
        """Detach only already-active evidence matching the proposed action.

        The source is owner-validated at publication and restore. Planning
        never receives aliases to the active owner's internal rows.
        """
        return [
            deepcopy(row)
            for row in self._i1_active_observed_procedures
            if (type(row) is dict
                and row.get("primitive") == primitive
                and row.get("parameters") == parameters
                and row.get("observed_field") == observed_field)
        ]

    def export_causal_state(self):
        state = super().export_causal_state()
        # This versioned marker is part of the natural owner's M11 state,
        # including before the first successful cognitive publication. It
        # prevents cold-recovering under an incompatible active form schema.
        state[ACTIVE_FORM_SCHEMA_KEY] = SCHEMA
        if self._i1_active_observed_procedures:
            state[ACTIVE_FORM_KEY] = deepcopy(self._i1_active_observed_procedures)
        return state

    def restore_causal_state(self, state):
        if (type(state) is not dict
                or state.get(ACTIVE_FORM_SCHEMA_KEY) != SCHEMA):
            raise ValueError("incompatible I1 active cognitive owner schema")
        proposed = deepcopy(state.get(ACTIVE_FORM_KEY, []))
        validate_advisory_rows(proposed)
        bare = dict(state)
        bare.pop(ACTIVE_FORM_KEY, None)
        bare.pop(ACTIVE_FORM_SCHEMA_KEY)
        before = super().export_causal_state()
        try:
            super().restore_causal_state(bare)
            self._i1_active_observed_procedures = proposed
        except Exception:
            # Recovery of an invalid technical state must not leave a partially
            # updated live TD owner or a partially published advisory form.
            super().restore_causal_state(before)
            raise

    def prepare_stage10_advisory_rebase(self, candidate, baseline, updates):
        """Pure owner-specific rebase: preserve *actual current* online Q state.

        Stage10's coordinator already freezes the authentic post-cut journal
        and prevents intervening updates. Its current baseline owns all
        already applied online TD. Only the orthogonal observed-advisory field
        is modified here; no TD replay or TD reset can occur.
        """
        if (type(candidate) is not dict or type(baseline) is not dict
                or type(candidate.get("forms")) is not dict
                or set(candidate["forms"]) != EXPECTED_ACTIVE_OWNERS
                or type(candidate.get("procedural")) is not list
                or baseline.get(ACTIVE_FORM_SCHEMA_KEY) != SCHEMA):
            raise ValueError("I1 active form requires one versioned canonical owner")
        proposed = candidate["forms"]["value_needs"]
        expected = sorted(
            [deepcopy(row) for row in candidate["procedural"]
             if type(row) is dict and row.get("state") == "compiled_private"],
            key=lambda row: row["id"],
        )
        if proposed != expected:
            raise ValueError("active advisory lacks a verified private source form")
        validate_advisory_rows(proposed)
        if any(
            update.owner_id != "value_needs"
            or update.kind != "td_update_published"
            for update in updates
        ):
            raise ValueError("unreplayable non-TD online update")
        previous = baseline.get(ACTIVE_FORM_KEY, [])
        validate_advisory_rows(previous)
        old = {row["id"]: row for row in previous}
        fresh = {row["id"]: row for row in proposed}
        if not set(old).issubset(fresh):
            raise ValueError("active memory must never forget verified earlier forms")
        for identifier, prior in old.items():
            newer = fresh[identifier]
            if any(prior.get(field) != newer.get(field) for field in (
                "plan_signature", "primitive", "parameters", "observed_field",
                "near_context", "preconditions", "evidence_scope",
                "goal_success_inferred", "safety_certified",
            )):
                raise ValueError("active procedure changed its immutable identity")
            for field in (
                "source_episode_refs", "trial_episode_refs",
                "source_event_refs", "trial_event_refs",
            ):
                if not set(prior[field]).issubset(newer[field]):
                    raise ValueError("active procedure dropped its lived witnesses")
        # The coordinator gives this rebaser an already-detached owner
        # snapshot and makes its own validated copy of the result. Mutate only
        # the orthogonal advisory field, never its online TD state.
        unchanged = canonical_causal_bytes({
            k: v for k, v in baseline.items() if k != ACTIVE_FORM_KEY
        })
        if proposed:
            baseline[ACTIVE_FORM_KEY] = deepcopy(proposed)
        else:
            baseline.pop(ACTIVE_FORM_KEY, None)
        if canonical_causal_bytes({
            k: v for k, v in baseline.items() if k != ACTIVE_FORM_KEY
        }) != unchanged:
            raise ValueError("active advisory attempted to overwrite online learning")
        return baseline
