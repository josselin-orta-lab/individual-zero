"""I1-only first-person, observable water-effect owner (D1 research prototype).

No world, lab, journal, Oracle, Bench, motor or map dependencies. An admitted
physical result alone is NOT training; a later accessible capture is required.
Evidence expresses association, never causal/safety/terminal certainty.
"""
from __future__ import annotations

from copy import deepcopy
from math import isfinite

SCHEMA = "i1-lived-water-evidence-owner-v1"


class I1LivedWaterOwner:
    owner_id = "i1_lived_water_model"

    def __init__(self, *, life_id: str, enabled: bool) -> None:
        if not isinstance(life_id, str) or not life_id.startswith("i1:"):
            raise ValueError("water learning requires a separate I1 life identity")
        if type(enabled) is not bool:
            raise ValueError("water learning mode must be a boolean")
        self.life_id = life_id
        self.enabled = enabled
        self._pending: dict[str, object] | None = None
        self._examples: list[dict[str, object]] = []

    @property
    def pending(self) -> dict[str, object] | None:
        return deepcopy(self._pending)

    @property
    def examples(self) -> tuple[dict[str, object], ...]:
        return tuple(deepcopy(self._examples))

    @property
    def observed_water_gain(self) -> float | None:
        if not self.enabled or not self._examples:
            return None
        # Limited observed before/after association; not a simulator state,
        # safety guarantee, source map or distal causal responsibility.
        value = sum(float(row["delta_water"]) for row in self._examples)
        return round(value / len(self._examples), 8)

    def record_applied(
        self, *, sent_world_step: int, before_water: float,
        x: int, y: int, command_hash: str, option_ref: str,
        first_capture_hash: str,
    ) -> None:
        if (not self.enabled or self._pending is not None
                or type(sent_world_step) is not int or sent_world_step < 1
                or type(x) is not int or type(y) is not int
                or type(before_water) not in (float, int)
                or not isfinite(before_water) or not 0 <= before_water <= 100
                or any(type(v) is not str or not v
                       for v in (command_hash, option_ref, first_capture_hash))):
            raise ValueError("invalid or overlapping lived water application")
        self._pending = {
            "life_id": self.life_id,
            "sent_world_step": sent_world_step,
            "before_water": float(before_water),
            "x": x, "y": y,
            "primitive": "boire",
            "command_hash": command_hash,
            "option_ref": option_ref,
            "first_capture_hash": first_capture_hash,
        }

    def needs_followup(self, world_step: int) -> bool:
        return (self.enabled and self._pending is not None
                and type(world_step) is int
                and world_step > self._pending["sent_world_step"])

    def observe_followup(
        self, *, observed_world_step: int, x: int, y: int,
        observed_water: float, current_water_source: bool,
        followup_capture_hash: str, paid_uc: bool,
    ) -> dict[str, object] | None:
        if not self.needs_followup(observed_world_step):
            return None
        p = self._pending
        assert p is not None
        self._pending = None
        reason = None
        if (type(x) is not int or type(y) is not int
                or type(observed_water) not in (float, int)
                or not isfinite(observed_water)
                or not 0 <= observed_water <= 100
                or type(current_water_source) is not bool
                or not isinstance(followup_capture_hash, str)
                or not followup_capture_hash
                or type(paid_uc) is not bool):
            reason = "invalid_authorized_capture"
        elif observed_world_step != p["sent_world_step"] + 1:
            reason = "missing_next_capture"
        elif (x, y) != (p["x"], p["y"]):
            reason = "position_changed_confounded"
        elif not current_water_source:
            reason = "water_source_absent_confounded"
        elif not paid_uc:
            reason = "learning_uc_refused"
        delta = (round(float(observed_water) - float(p["before_water"]), 8)
                 if reason is None else None)
        if reason is None and (delta is None or delta <= 0.0):
            reason = "no_observed_positive_water_effect"
        payload: dict[str, object] = {
            "owner_version": SCHEMA, "life_id": self.life_id,
            "sent_world_step": p["sent_world_step"],
            "observed_world_step": observed_world_step,
            "before_water": p["before_water"],
            "observed_water": (float(observed_water) if delta is not None else None),
            "delta_water": delta,
            "source_position": [p["x"], p["y"]],
            "command_hash": p["command_hash"],
            "option_ref": p["option_ref"],
            "first_capture_hash": p["first_capture_hash"],
            "followup_capture_hash": followup_capture_hash,
            "admitted": reason is None,
            "reason": reason,
            "physical_safety_certified": False,
            "distal_agency_certified": False,
            "epistemic_scope": "first_person_observed_association_only",
        }
        if reason is None:
            self._examples.append({
                "sent_world_step": p["sent_world_step"],
                "observed_world_step": observed_world_step,
                "source_position": [p["x"], p["y"]],
                "delta_water": delta,
                "command_hash": p["command_hash"],
                "option_ref": p["option_ref"],
                "first_capture_hash": p["first_capture_hash"],
                "followup_capture_hash": followup_capture_hash,
            })
        return payload

    def export_causal_state(self) -> dict[str, object]:
        return {
            "schema": SCHEMA, "life_id": self.life_id,
            "enabled": self.enabled,
            "pending": deepcopy(self._pending),
            "examples": deepcopy(self._examples),
        }

    def _load_trusted_current_on_fresh(self, state: object) -> None:
        """Called exclusively by authenticated I1 M11 cold installer."""
        if (type(state) is not dict or set(state) != {
                "schema", "life_id", "enabled", "pending", "examples"}
                or state["schema"] != SCHEMA
                or state["life_id"] != self.life_id
                or state["enabled"] is not self.enabled
                or self._pending is not None or self._examples):
            raise ValueError("incompatible/used I1 water cold owner")
        records = state["examples"]
        if type(records) is not list or len(records) > 10000:
            raise ValueError("invalid I1 water cold evidence list")
        previous_step = 0
        for e in records:
            if (type(e) is not dict or set(e) != {
                    "sent_world_step", "observed_world_step",
                    "source_position", "delta_water", "command_hash",
                    "option_ref", "first_capture_hash", "followup_capture_hash"}
                    or type(e["sent_world_step"]) is not int
                    or e["sent_world_step"] < 1
                    or type(e["observed_world_step"]) is not int
                    or e["observed_world_step"] != e["sent_world_step"] + 1
                    or e["sent_world_step"] <= previous_step
                    or type(e["source_position"]) is not list
                    or len(e["source_position"]) != 2
                    or any(type(x) is not int for x in e["source_position"])
                    or type(e["delta_water"]) not in (float, int)
                    or not isfinite(e["delta_water"]) or e["delta_water"] <= 0
                    or any(type(e[key]) is not str or not e[key] for key in (
                        "command_hash", "option_ref", "first_capture_hash",
                        "followup_capture_hash"))):
                raise ValueError("untrusted I1 water model evidence")
            previous_step = e["sent_world_step"]
        pending = state["pending"]
        if pending is not None:
            if (type(pending) is not dict or set(pending) != {
                    "life_id", "sent_world_step", "before_water", "x", "y",
                    "primitive", "command_hash", "option_ref", "first_capture_hash"}
                    or pending["life_id"] != self.life_id or not self.enabled
                    or pending["primitive"] != "boire"
                    or type(pending["sent_world_step"]) is not int
                    or pending["sent_world_step"] < 1
                    or pending["sent_world_step"] <= previous_step
                    or any(type(pending[key]) is not int for key in ("x", "y"))
                    or type(pending["before_water"]) not in (int, float)
                    or not isfinite(pending["before_water"])
                    or not 0 <= pending["before_water"] <= 100
                    or any(type(pending[key]) is not str or not pending[key]
                           for key in ("command_hash", "option_ref", "first_capture_hash"))):
                raise ValueError("invalid pending first-person water proof")
        if not self.enabled and (records or pending):
            raise ValueError("disabled water model cannot carry learning")
        self._examples = deepcopy(records)
        self._pending = deepcopy(pending)
        if self.export_causal_state() != state:
            raise ValueError("cold state failed strict equality check")

    def restore_causal_state(self, state: object) -> None:
        # No historic rollback of knowledge on an already living individual.
        if state != self.export_causal_state():
            raise ValueError("mortal water memory refuses historical state restore")
