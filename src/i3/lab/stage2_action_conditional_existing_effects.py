"""Read-only action-conditioned first-person distress from already learned effects.

Stage 2.1 SOFTWARE-ONLY provenance gate. No new learner is trained here:
the reference Mind.effects already stores personally observed action-indexed
body deltas, funded by normal I3 outcome learning when a native World runs.
This module neither opens a World nor changes Mind, effects, policy or actions.

New scalar readout and SHA sealing are laboratory CPU, NOT bodily paid.
Never present a synthetic outcome as a first-person lived scientific result.
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import isfinite

from ..modules.body import ACTION_COSTS, validate_body
from ..modules.genome import midpoint
from ..modules.mind import Mind

SCHEMA = "i3-stage2.1-action-conditioned-native-effects-synthetic/v1"
SYNTHETIC_BODY = (30., 30., 30., 35., 30.)


def _sha(value):
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"), allow_nan=False,
        default=str).encode("utf-8")).hexdigest()


def _innate_self_reward(theta, p, w, body):
    """Use the reference innate Mind readout with frozen inherited channels."""
    class Readout:
        pass

    readout = Readout()
    readout.theta, readout.p, readout.w = theta, p, w
    phi = Mind.feats(readout, validate_body(body))
    target = -Mind.distress(readout, phi)
    if not isfinite(target):
        raise ValueError("nonfinite inherited intrinsic readout")
    return target


def _delta_from_native_effects(mind, key):
    """Reference EffectsModel.predict semantics; never a custom World oracle."""
    delta, uncertainty = mind.effects.predict(key)
    if (len(delta) != 5 or any(type(v) not in (int, float) or
        not isfinite(v) for v in delta)
            or not isfinite(uncertainty) or uncertainty < 0):
        raise ValueError("invalid native personally learned effect readout")
    return tuple(float(d) for d in delta)


def _known_action_key(mind, action):
    if action is None:
        return None
    # An actual I3 action-level mean can be stored under either the
    # two-element (action, None) fallback of a token-keyed effect or
    # the single-element (action,) key for non-token actions. Never
    # infer a token, and never use hidden resources or future outcomes.
    for key in ((action, None), (action,)):
        entry = mind.effects.stats.get(key)
        if (entry is not None and type(entry) is list and
                len(entry) == 3 and type(entry[0]) in (int, float)
                and isfinite(entry[0]) and entry[0] > 0):
            return key
    return None


def _project(body, delta):
    return tuple(max(0.0, min(100.0, b + d))
                 for b, d in zip(body, delta))


def passive_readouts(mind: Mind, before_body, action):
    """Three frozen *unpaid lab* readouts of one already chosen action.

    This helper's action argument is only an observed label, never an
    action selector. Callers of the actual prequential ticket validate
    that the action was emitted by Mind.decide before accessing it.
    """
    if type(mind) is not Mind:
        raise TypeError("reference I3 Mind required")
    body = validate_body(before_body)
    if action is not None and (type(action) is not str or
                               action not in ACTION_COSTS):
        raise ValueError("only a valid selected I3 motor action label")
    if any(type(m) not in (tuple, list) or len(m) != 4
           for m in mind.buffer):
        raise PermissionError("native personal replay memories have NO action labels")
    theta, p, w = tuple(mind.theta), tuple(mind.p), tuple(mind.w)
    global_entry = mind.effects.stats.get(("*",))
    has_global = bool(global_entry and global_entry[0] > 0)
    global_delta = _delta_from_native_effects(mind, ("*",))
    key = _known_action_key(mind, action)
    action_delta = (_delta_from_native_effects(mind, key)
                    if key is not None else global_delta)
    forecast = {
        "action": _innate_self_reward(theta, p, w,
                                      _project(body, action_delta)),
        "global": _innate_self_reward(theta, p, w,
                                      _project(body, global_delta)),
        "persistence": _innate_self_reward(theta, p, w, body),
    }
    if any(not isfinite(x) for x in forecast.values()):
        raise ValueError("nonfinite personal action-conditioned forecast")
    return {
        "before_body": body, "chosen_action": action,
        "native_action_effect_key": key,
        "action_specific_history": key is not None,
        "global_effect_history": has_global,
        "action_effect_delta": action_delta,
        "global_effect_delta": global_delta,
        "scalar_forecasts": forecast,
        "innate_parameter_sha256": _sha((theta, p, w, mind.d_max)),
        "native_selected_effect_sha256": _sha((
            key, action_delta, global_delta,
            repr(mind.effects.stats.get(key)) if key is not None else None,
            repr(global_entry))),
        "readout_is_external_unpaid_laboratory_cpu": True,
    }


class SyntheticActionPrequentialTicket:
    """Freeze once before a SYNTHETIC outcome, settle once, fail closed."""

    def __init__(self, *, mind: Mind, capture_body, action, param, identity):
        if type(mind) is not Mind:
            raise TypeError("reference Mind required for chosen action custody")
        if not isinstance(identity, str) or not identity or len(identity) > 128:
            raise ValueError("fixed source identity required")
        if param is not None and type(param) is not str:
            raise ValueError("only actually selected text parameter or None")
        before = validate_body(capture_body)
        if (action is None and (param is not None or mind.last is not None)):
            raise PermissionError("inactive decision cannot have a chosen motor")
        if action is not None:
            last = mind.last
            if (type(last) is not tuple or len(last) != 4 or
                    tuple(last[0]) != before or last[2] != action or
                    last[3] != param):
                raise PermissionError("action not matched to already chosen Mind.last")
        candidate = passive_readouts(mind, before, action)
        self._theta = tuple(mind.theta)
        self._p = tuple(mind.p)
        self._w = tuple(mind.w)
        self._d_max = mind.d_max
        self._selected_action = action
        self._selected_param = param
        self.payload = {
            "schema": SCHEMA,
            "identity": identity,
            "selected_action_before_outcome": action,
            "selected_param_before_outcome": param,
            "frozen_readouts": candidate,
            "no_actual_future_body_available": True,
        }
        self.sha256 = _sha(self.payload)
        self._settled = False

    def settle_synthetic(self, *, sha256, action, param, after_body, dead):
        if self._settled:
            raise RuntimeError("synthetic outcome already scored")
        if (sha256 != self.sha256 or _sha(self.payload) != self.sha256
                or action != self._selected_action
                or param != self._selected_param):
            raise RuntimeError("forged outcome or modified preoutcome seal")
        if type(dead) not in (tuple, list):
            raise TypeError("synthetic terminal evidence must be a death-cause list")
        after = validate_body(after_body)
        target = (-self._d_max if dead else
                  _innate_self_reward(self._theta, self._p, self._w, after))
        predictions = self.payload["frozen_readouts"]["scalar_forecasts"]
        losses = {mode: (value - target)**2
                  for mode, value in predictions.items()}
        if not isfinite(target) or any(not isfinite(v) for v in losses.values()):
            raise RuntimeError("nonfinite synthetic proper loss")
        self._settled = True
        return {
            "status": "SYNTHETIC_ONLY_SCORED",
            "source_identity": self.payload["identity"],
            "forecast_sha256": self.sha256,
            "observed_terminal": bool(dead),
            "observed_synthetic_target": target,
            "squared_loss": losses,
            "worlds_opened": 0,
            "scientific_lives": 0,
            "scientific_verdict": "NOT_ISSUED",
        }


def _fixture():
    mind = Mind(midpoint(), 100042)
    # Synthetic observations through ONLY the actual reference EffectsModel
    # interface: not born, not paid, not personal real-world experiences.
    mind.effects.observe(("attendre",), (-3., -1., -1., 0., -1.))
    mind.effects.observe(("dormir",), (6., -2., -1., 0., 7.))
    return mind


def audit():
    source = _fixture()
    body = SYNTHETIC_BODY
    a = passive_readouts(source, body, "attendre")
    b = passive_readouts(source, body, "dormir")
    missing = passive_readouts(source, body, "boire")
    inactive = passive_readouts(source, body, None)
    if (not a["action_specific_history"] or
            not b["action_specific_history"] or
            missing["action_specific_history"] or
            inactive["action_specific_history"] or
            a["scalar_forecasts"]["action"] == b["scalar_forecasts"]["action"] or
            a["scalar_forecasts"]["global"] != b["scalar_forecasts"]["global"] or
            a["scalar_forecasts"]["persistence"] !=
            b["scalar_forecasts"]["persistence"] or
            missing["scalar_forecasts"]["action"] !=
            missing["scalar_forecasts"]["global"]):
        raise RuntimeError("native personally learned action provenance gate failed")

    source.last = (body, ("attendre",), "attendre", None)
    ticket = SyntheticActionPrequentialTicket(
        mind=source, capture_body=body, action="attendre",
        param=None, identity="synthetic-action-label-probe")
    sealed = ticket.sha256
    outcome = ticket.settle_synthetic(
        sha256=sealed, action="attendre", param=None,
        after_body=(27., 29., 29., 35., 29.), dead=())
    if outcome["status"] != "SYNTHETIC_ONLY_SCORED":
        raise RuntimeError("unsettled synthetic future target")
    return {
        "schema": SCHEMA,
        "status": "SOFTWARE_ACTION_LABEL_PROVENANCE_ONLY",
        "synthetic_fixture_count": 1,
        "frozen_same_body_action_forecasts_differ": (
            a["scalar_forecasts"]["action"] !=
            b["scalar_forecasts"]["action"]),
        "same_body_global_forecasts_identical": (
            a["scalar_forecasts"]["global"] ==
            b["scalar_forecasts"]["global"]),
        "unknown_action_exact_global_fallback": (
            missing["scalar_forecasts"]["action"] ==
            missing["scalar_forecasts"]["global"]),
        "no_action_specific_evidence_for_inactivity": (
            not inactive["action_specific_history"]),
        "existing_reference_effects_not_retrained": True,
        "synthetic_prospectively_frozen_sha256": sealed,
        "synthetic_proper_scores": outcome["squared_loss"],
        "lived_outcomes_scored": 0,
        "fresh_world_opening_permitted": False,
        "external_readout_physically_paid": False,
        "native_effects_previously_lived_payment_attested": False,
        "worlds_opened": 0, "scientific_lives": 0,
        "scientific_verdict": "NOT_ISSUED",
        "stage2_2_go": False,
    }


if __name__ == "__main__":
    print("I3_ACTION_CONDITIONAL_PROVENANCE_RESULT="+json.dumps(
        audit(), sort_keys=True))
