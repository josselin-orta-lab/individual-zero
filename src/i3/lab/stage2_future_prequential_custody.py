"""Future-source, no-World, all-assigned prequential forecast receipt guard.

This is a methods-only in-memory observer. It cannot authenticate when a
caller actually learned an outcome, nor does it finance an organism's work.
No inference about cognition, action, physiology, survival or generalization.
"""
from __future__ import annotations

from hashlib import sha256
import json
from math import fsum, isfinite
import re

SCHEMA = "i3-stage2-future-prequential-forecast-custody/v1"
STOP_REASONS = frozenset({
    "COMPLETE", "NO_PERSONAL_SUPPORT", "DENIED_FUNDING",
    "DEAD_BEFORE_OPPORTUNITY", "RIGHT_CENSORED",
})
UNSCORED_PENDING_REASONS = frozenset({
    "DEAD_BEFORE_OPPORTUNITY", "RIGHT_CENSORED",
})
MAX_EVENTS_PER_UNIT = 400
_HEX = re.compile(r"[0-9a-f]{64}\Z")
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:/-]{0,127}\Z")


def _digest(value):
    return sha256(json.dumps(
        value, sort_keys=True, separators=(",", ":"),
        allow_nan=False, ensure_ascii=False,
    ).encode("utf-8")).hexdigest()


def _delta(value):
    if (type(value) not in (tuple, list) or len(value) != 5 or
            any(type(v) not in (float, int) or not isfinite(v)
                or not -100. <= v <= 100. for v in value)):
        raise ValueError("five finite first-person delta channels required")
    return tuple(float(v) for v in value)


def _mean_loss(forecast, observed):
    # Squared-error is proper for a conditional MEAN. Not a risk calibration
    # metric or the body's nonlinear distress/survival outcome.
    return fsum((f - x)**2 for f, x in zip(forecast, observed)) / 5.


class FuturePrequentialCustody:
    """Require a frozen before-outcome forecast and retain every assigned unit.

    This checks method-call order within a process. It does NOT prove that a
    caller really froze before physical exposure, or authenticate its source.
    """

    def __init__(self, assigned_unit_ids, *, source_sha256):
        if (type(source_sha256) is not str or
                _HEX.fullmatch(source_sha256) is None):
            raise ValueError("exact lowercase source SHA-256 required")
        if (type(assigned_unit_ids) not in (list, tuple)
                or not assigned_unit_ids):
            raise ValueError("a nonempty fixed assignment set is required")
        for identity in assigned_unit_ids:
            if type(identity) is not str or _ID.fullmatch(identity) is None:
                raise ValueError("invalid assigned unit identity")
        if len(set(assigned_unit_ids)) != len(assigned_unit_ids):
            raise ValueError("duplicate assigned units")
        self._source = source_sha256
        self._order = tuple(assigned_unit_ids)
        self._units = {
            identity: {
                "head": _digest([SCHEMA, source_sha256, identity, "GENESIS"]),
                "events": [], "pending": None, "closed": None,
                "unscored_pending": None,
            } for identity in self._order
        }

    def _unit(self, identity):
        if type(identity) is not str or identity not in self._units:
            raise ValueError("unassigned or invalid unit")
        return self._units[identity]

    def freeze(self, identity, *, step, baseline_forecast, candidate_forecast):
        """Seal both expected five-channel MEANS before the actual delta."""
        row = self._unit(identity)
        if row["closed"] is not None or row["pending"] is not None:
            raise ValueError("cannot freeze closed or pending unit")
        if (type(step) is not int or step != len(row["events"]) + 1 or
                step > MAX_EVENTS_PER_UNIT):
            raise ValueError("nonconsecutive or excessive forecast event step")
        baseline = _delta(baseline_forecast)
        candidate = _delta(candidate_forecast)
        pending = {
            "unit_id": identity, "step": step,
            "source_sha256": self._source,
            "prior_head_sha256": row["head"],
            "baseline": baseline, "candidate": candidate,
        }
        digest = _digest([SCHEMA, "FROZEN", pending])
        row["pending"] = {**pending, "sha256": digest}
        return digest

    def settle(self, identity, *, frozen_sha256, actual_delta):
        """Settle once against an actual outcome supplied *after* freeze.

        External source custody must establish that the submitted outcome is
        genuine and that the freeze happened before real observation.
        """
        row = self._unit(identity)
        if row["closed"] is not None or row["pending"] is None:
            raise ValueError("no open frozen forecast")
        pending = row["pending"]
        if (type(frozen_sha256) is not str or
                frozen_sha256 != pending["sha256"]):
            raise ValueError("wrong pre-outcome forecast digest")
        observed = _delta(actual_delta)
        baseline_loss = _mean_loss(pending["baseline"], observed)
        candidate_loss = _mean_loss(pending["candidate"], observed)
        event = {
            "step": pending["step"],
            "frozen_sha256": frozen_sha256,
            "actual_delta": observed,
            "baseline_mse": baseline_loss,
            "candidate_mse": candidate_loss,
            "candidate_minus_baseline_mse": candidate_loss - baseline_loss,
        }
        next_head = _digest([row["head"], "SETTLED", event])
        row["head"] = next_head
        row["events"].append(event)
        row["pending"] = None
        return next_head

    def close(self, identity, *, reason, frozen_sha256=None):
        """Preserve terminal/no-exposure/censored units without fake outcomes."""
        row = self._unit(identity)
        if row["closed"] is not None or reason not in STOP_REASONS:
            raise ValueError("invalid or repeated closure")
        pending = row["pending"]
        if pending is not None:
            if (reason not in UNSCORED_PENDING_REASONS
                    or frozen_sha256 != pending["sha256"]):
                raise ValueError("pending forecast must be explicitly censored")
            unscored = {
                "step": pending["step"], "frozen_sha256": pending["sha256"],
                "reason": reason, "actual_delta": None, "loss": None,
            }
        else:
            if frozen_sha256 is not None:
                raise ValueError("no pending forecast for supplied digest")
            unscored = None
        if reason == "COMPLETE" and (not row["events"] or pending is not None):
            raise ValueError("COMPLETE requires a settled, nonpending unit")
        row["head"] = _digest([row["head"], "CLOSED", reason, unscored])
        row["closed"] = reason
        row["unscored_pending"] = unscored
        row["pending"] = None
        return row["head"]

    def report(self):
        """Return descriptive per-unit evidence only after ALL are closed."""
        if any(row["closed"] is None for row in self._units.values()):
            raise ValueError("all assigned units including nulls must close first")
        units = []
        for identity in self._order:
            row = self._units[identity]
            events = row["events"]
            n = len(events)
            baseline_mean = fsum(e["baseline_mse"] for e in events)/n if n else None
            candidate_mean = fsum(e["candidate_mse"] for e in events)/n if n else None
            diff = candidate_mean - baseline_mean if n else None
            units.append({
                "unit_id": identity, "closure": row["closed"],
                "scored_events": n,
                "unscored_pending": row["unscored_pending"],
                "mean_baseline_mse": baseline_mean,
                "mean_candidate_mse": candidate_mean,
                "mean_candidate_minus_baseline_mse": diff,
                "worst_baseline_event_mse": max(
                    (e["baseline_mse"] for e in events), default=None),
                "worst_candidate_event_mse": max(
                    (e["candidate_mse"] for e in events), default=None),
                "receipt_head_sha256": row["head"],
            })
        evaluated = [r for r in units if r["scored_events"]]
        diffs = [r["mean_candidate_minus_baseline_mse"] for r in evaluated]
        result = {
            "schema": SCHEMA,
            "status": "SOFTWARE_PREQUENTIAL_CUSTODY_READY_NO_EFFICACY_VERDICT",
            "source_sha256": self._source,
            "assigned_units": len(units),
            "scored_units": len(evaluated),
            "never_scored_units": len(units)-len(evaluated),
            "scored_events": sum(r["scored_events"] for r in units),
            "censored_pending_events": sum(
                r["unscored_pending"] is not None for r in units),
            "closures": {reason: sum(r["closure"] == reason for r in units)
                         for reason in sorted(STOP_REASONS)},
            "descriptive_mean_of_unit_mean_mse_difference":
                fsum(diffs)/len(diffs) if diffs else None,
            "descriptive_candidate_better_units": sum(x < 0 for x in diffs),
            "descriptive_candidate_worse_units": sum(x > 0 for x in diffs),
            "descriptive_tie_units": sum(x == 0 for x in diffs),
            "unit_draw_independence_not_established": True,
            "externally_authenticated_preoutcome_order": False,
            "real_world_paid_forecasts": False,
            "forecast_accuracy_not_organism_viability": True,
            "scientific_worlds": 0,
            "scientific_lives": 0,
            "scientific_verdict": "NOT_ISSUED",
            "units": units,
        }
        result["deterministic_sha256"] = _digest(result)
        return result
