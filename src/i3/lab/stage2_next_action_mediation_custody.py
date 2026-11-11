"""Prospective two-arm next-action receipt *preflight*, not a living study.

Pure, read-only reducer for externally supplied future original receipts.
It cannot independently authenticate a source, World, policy intervention,
individual birth, forecast execution or controller information delivery.
No native World, Mind.decide, learning or policy is executed here.
"""
from __future__ import annotations

from dataclasses import asdict
from hashlib import sha256
import json
from math import isfinite

from ..modules.body import (
    ACTION_COSTS, BodyLaws, CognitiveBudget, CognitiveWork,
    debit_cognition, validate_body, validate_laws)
from .stage2_action_phase_readout_budget import (
    _matching_account, proposed_readout_work)

SCHEMA = "i3-stage2.1-next-actual-decision-custody-software/v1"
ARMS = ("visible", "discard")
FORECASTS = ("action", "global", "persistence")
NO_NEXT = ("TERMINAL_BEFORE_NEXT", "RIGHT_CENSORED_NOT_SCORED")
LEARNING = ("PAID_LEARNING", "NO_FUNDED_LEARNING", "TERMINAL_NO_LEARNING")
STATES = ("FROZEN_FIRST", "FIRST_SETTLED", "FROZEN_NEXT",
          "NEXT_SETTLED", "TERMINAL_BEFORE_NEXT", "RIGHT_CENSORED_NOT_SCORED")


def _digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode()).hexdigest()


def _hex_sha(value):
    return (type(value) is str and len(value) == 64
            and all(c in "0123456789abcdef" for c in value))


def _action(action, param, *, allow_inactive):
    if action is None:
        if not allow_inactive or param is not None:
            raise ValueError("only next genuine inactivity may omit action/param")
    elif type(action) is not str or action not in ACTION_COSTS:
        raise ValueError("native physical action label required")
    if param is not None and (type(param) is not str or not param or len(param) > 128):
        raise ValueError("nonempty bounded original action parameter required")


def _receipt(account, work, laws):
    if type(work) is not CognitiveWork:
        raise TypeError("exact native CognitiveWork required")
    _matching_account(laws, work, account)
    return {channel: {part: account[channel][part]
                      for part in ("requested", "paid", "unpaid")}
            for channel in ("energy", "vigilance")}


def _terminal(body, dead):
    if type(dead) not in (tuple, list):
        raise TypeError("actual native terminal causes must be a sequence")
    # Native v2 transition derives these solely from the 3 vital channels.
    expected = tuple(name for name, x in (
        ("zero_food", body[1]), ("zero_water", body[2]),
        ("zero_integrity", body[3])) if x <= 0.)
    if tuple(dead) != expected:
        raise ValueError("native terminal causes contradict observed body")
    return expected


def _learning_phase(*, immediate, dead, status, work, account, post, laws):
    if status not in LEARNING:
        raise ValueError("declared native learning phase required")
    validated_post = validate_body(post)
    learning_receipt = _receipt(account, work, laws)
    if status == "PAID_LEARNING":
        if dead or work == CognitiveWork():
            raise ValueError("terminal/zero-work cannot claim paid learning")
        expected, _ = debit_cognition(immediate, laws, work)
        if validated_post != expected:
            raise ValueError("post-learning phase not equal to native paid body")
    else:
        if (status == "TERMINAL_NO_LEARNING") != bool(dead):
            raise ValueError("terminal and no-funded-learning are distinct")
        if work != CognitiveWork() or validated_post != immediate:
            raise ValueError("absent learning must have zero work and same body")
    return {
        "status": status,
        "work": asdict(work),
        "accounting": learning_receipt,
        "post_paid_learning_body": validated_post,
    }


class NextActionPairCustody:
    """Signed chronology validator for a *claimed* two-arm future source.

    No verification of original Git archive or born life occurs in this
    reducer. Its hard-coded verdict is always NOT_ISSUED.
    """

    def __init__(self, *, source_label, world_spec_sha, genome_sha,
                 initial_living_mind_sha, pair_seed, laws=None):
        for name, value in (("world_spec_sha", world_spec_sha),
                            ("genome_sha", genome_sha),
                            ("initial_living_mind_sha", initial_living_mind_sha)):
            if not _hex_sha(value):
                raise ValueError(f"fixed claimed original {name} SHA-256 required")
        if type(source_label) is not str or not 0 < len(source_label) <= 128:
            raise ValueError("bounded source label required")
        if type(pair_seed) is not int or pair_seed < 0:
            raise ValueError("nonnegative independent pair identity required")
        self.laws = BodyLaws() if laws is None else laws
        validate_laws(self.laws)
        self.source = {
            "source_label": source_label,
            "world_spec_sha": world_spec_sha,
            "genome_sha": genome_sha,
            "initial_living_mind_sha": initial_living_mind_sha,
            "pair_seed": pair_seed,
        }
        self._arms = {}

    def _get(self, arm, phase):
        if arm not in ARMS or type(arm) is not str:
            raise ValueError("source arm must be visible or discard")
        state = self._arms.get(arm)
        if state is None or state["phase"] != phase:
            raise RuntimeError(f"invalid {arm} event chronology for {phase}")
        return state

    def freeze_first(self, arm, *, before_body, action, param,
                     original_work, personal_memory_count, forecasts):
        """External pre-outcome claim: real source must independently attest it."""
        if arm not in ARMS or type(arm) is not str:
            raise ValueError("invalid arm")
        if arm in self._arms:
            raise RuntimeError("first source already frozen")
        _action(action, param, allow_inactive=False)
        if type(original_work) is not CognitiveWork or original_work == CognitiveWork():
            raise ValueError("existing original decision work required")
        if type(forecasts) is not dict or tuple(forecasts) != FORECASTS:
            raise ValueError("all three preoutcome scalar personal forecasts required")
        if any(type(forecasts[x]) not in (int, float) or not isfinite(forecasts[x])
               for x in FORECASTS):
            raise ValueError("finite original forecast values required")
        if type(personal_memory_count) is not int:
            raise ValueError("exact personal memory count required")
        extra = proposed_readout_work(personal_memory_count)
        before = validate_body(before_body)
        allowance = CognitiveBudget(before, self.laws)
        if not allowance.try_spend(original_work):
            raise ValueError("original decision not model-fundable")
        if not allowance.try_spend(extra):
            raise ValueError("no native funds for optional readout")
        if action != "dormir" and allowance.remaining[0] < ACTION_COSTS[action]:
            raise ValueError("optional brain ticket steals already chosen motor")
        # Both arms need literally identical before-exposure learned source,
        # action, claimed forecast and cost; observer visibility is the ONLY
        # intended future intervention.
        shared = {
            "source": self.source, "before_body": before,
            "selected_action": action, "selected_param": param,
            "personal_memory_count": personal_memory_count,
            "original_work": asdict(original_work),
            "optional_work": asdict(extra),
            "total_decision_work": asdict(allowance.work),
            "preoutcome_forecasts": {k: float(forecasts[k]) for k in FORECASTS},
        }
        shared_hash = _digest(shared)
        other = next((s for k, s in self._arms.items() if k != arm), None)
        if other is not None and other["shared_hash"] != shared_hash:
            raise PermissionError("paired sources differ before any intervention")
        # The controller-exposure label is a PLAN, not proof that the
        # future living Mind actually consumes or uses these forecasts.
        frozen = {
            "schema": SCHEMA, "arm": arm, "pair_source": self.source,
            "shared_preexposure_sha256": shared_hash,
            "readout_delivery_claim": (arm == "visible"),
            "receipt": shared,
        }
        seal = _digest(frozen)
        self._arms[arm] = {
            "phase": "FROZEN_FIRST", "seal": seal,
            "shared_hash": shared_hash, "frozen": frozen,
            "first": None, "next_freeze": None, "next": None,
        }
        return seal

    def _settle(self, state, *, before, decision_work, decision_account,
                immediate_body, dead, learning_status, learning_work,
                learning_account, post_paid_learning_body):
        decision = _receipt(decision_account, decision_work, self.laws)
        # The World effect may use first-person resources not represented
        # in this reducer. NEVER invent an alternative native transition.
        immediate = validate_body(immediate_body)
        reasons = _terminal(immediate, dead)
        learning = _learning_phase(
            immediate=immediate, dead=reasons, status=learning_status,
            work=learning_work, account=learning_account,
            post=post_paid_learning_body, laws=self.laws)
        return {
            "captured_predecision_body": validate_body(before),
            "declared_decision_work": asdict(decision_work),
            "decision_native_accounting": decision,
            "immediate_post_world_body": immediate,
            "native_terminal_causes": reasons,
            "learning": learning,
        }

    def settle_first(self, arm, *, seal, action, param, decision_work,
                     decision_account, immediate_body, dead,
                     learning_status, learning_work, learning_account,
                     post_paid_learning_body):
        state = self._get(arm, "FROZEN_FIRST")
        if seal != state["seal"] or _digest(state["frozen"]) != seal:
            raise PermissionError("tampered initial preoutcome SHA")
        frozen = state["frozen"]["receipt"]
        if (action != frozen["selected_action"] or
                param != frozen["selected_param"] or
                asdict(decision_work) != frozen["total_decision_work"]):
            raise PermissionError("actual initial action or work differs from frozen")
        first = self._settle(
            state, before=frozen["before_body"],
            decision_work=decision_work, decision_account=decision_account,
            immediate_body=immediate_body, dead=dead,
            learning_status=learning_status, learning_work=learning_work,
            learning_account=learning_account,
            post_paid_learning_body=post_paid_learning_body)
        state["first"] = first
        state["phase"] = "FIRST_SETTLED"
        return _digest({"first_source_sha": seal, "result": first})

    def freeze_next(self, arm, *, first_seal, source_decision_origin,
                    actual_capture_body, action, param, work,
                    next_capture_sha):
        state = self._get(arm, "FIRST_SETTLED")
        if first_seal != state["seal"] or _digest(state["frozen"]) != first_seal:
            raise PermissionError("first-preoutcome source changed")
        if state["first"]["native_terminal_causes"]:
            raise RuntimeError("terminal cannot make next decision")
        if source_decision_origin != "LIVING_MIND_DECIDE":
            raise PermissionError("detached hypothetical decision is NOT a lived action")
        if not _hex_sha(next_capture_sha):
            raise ValueError("predecision first-person perception SHA required")
        _action(action, param, allow_inactive=True)
        if type(work) is not CognitiveWork:
            raise TypeError("native next decision work required")
        before = validate_body(actual_capture_body)
        if before != state["first"]["learning"]["post_paid_learning_body"]:
            raise ValueError("next first-person body's previous learning phase mismatch")
        budget = CognitiveBudget(before, self.laws)
        if not budget.try_spend(work):
            raise ValueError("next action decision work was unfundable")
        if action not in (None, "dormir") and budget.remaining[0] < ACTION_COSTS[action]:
            raise ValueError("next decision took chosen motor energy")
        freeze = {
            "schema": SCHEMA, "arm": arm,
            "first_preoutcome_seal": first_seal,
            "first_result_sha256": _digest(state["first"]),
            "first_person_capture_sha256": next_capture_sha,
            "captured_body": before, "decision_origin": source_decision_origin,
            "actual_selected_action": action,
            "actual_selected_param": param,
            "actual_next_decision_work": asdict(work),
        }
        seal = _digest(freeze)
        state["next_freeze"] = freeze
        state["phase"] = "FROZEN_NEXT"
        return seal

    def settle_next(self, arm, *, seal, actual_executed_in_world,
                    action, param, decision_work, decision_account,
                    immediate_body, dead, learning_status, learning_work,
                    learning_account, post_paid_learning_body):
        state = self._get(arm, "FROZEN_NEXT")
        frozen = state["next_freeze"]
        if seal != _digest(frozen):
            raise PermissionError("tampered next decision preoutcome SHA")
        if type(actual_executed_in_world) is not bool or not actual_executed_in_world:
            raise PermissionError("unexecuted next decision is a laboratory counterfactual")
        if (action != frozen["actual_selected_action"] or
                param != frozen["actual_selected_param"] or
                asdict(decision_work) != frozen["actual_next_decision_work"]):
            raise PermissionError("claimed actual next result mismatches frozen choice")
        nxt = self._settle(
            state, before=frozen["captured_body"],
            decision_work=decision_work, decision_account=decision_account,
            immediate_body=immediate_body, dead=dead,
            learning_status=learning_status, learning_work=learning_work,
            learning_account=learning_account,
            post_paid_learning_body=post_paid_learning_body)
        state["next"] = nxt
        state["phase"] = "NEXT_SETTLED"
        return _digest({"next_preoutcome_sha": seal, "outcome": nxt})

    def close_without_next(self, arm, *, first_seal, reason):
        state = self._get(arm, "FIRST_SETTLED")
        if first_seal != state["seal"]:
            raise PermissionError("wrong source seal for missing next decision")
        if reason not in NO_NEXT:
            raise ValueError("explicit terminal/censored next choice required")
        terminal = bool(state["first"]["native_terminal_causes"])
        if terminal != (reason == "TERMINAL_BEFORE_NEXT"):
            raise ValueError("terminal cannot be confused with horizon/censor")
        state["phase"] = reason

    def summary(self):
        if set(self._arms) != set(ARMS):
            return self._summary_partial("INCOMPLETE_OR_CENSORED")
        visible, discard = (self._arms[x] for x in ARMS)
        if visible["shared_hash"] != discard["shared_hash"]:
            raise RuntimeError("different underlying source before first exposure")
        if visible["first"] and discard["first"] and (
                visible["first"] != discard["first"]):
            raise RuntimeError("paired same-cost first actual World/learning phase diverged")
        if all(self._arms[a]["phase"] == "NEXT_SETTLED" for a in ARMS):
            a, b = visible["next_freeze"], discard["next_freeze"]
            different = (a["actual_selected_action"], a["actual_selected_param"]) != (
                b["actual_selected_action"], b["actual_selected_param"])
            return self._summary_partial(
                "ACTUAL_NEXT_ACTION_DIFFERENCE" if different
                else "ACTUAL_NEXT_ACTION_SAME",
                action_difference=different)
        return self._summary_partial("INCOMPLETE_OR_CENSORED")

    def _summary_partial(self, status, *, action_difference=None):
        return {
            "schema": SCHEMA, "status": status, "paired_unit_claim": self.source,
            "pair_arms_frozen": sorted(self._arms),
            "arm_phases": {arm: state["phase"]
                           for arm, state in sorted(self._arms.items())},
            "next_actions_differ_claimed": action_difference,
            "source_originals_independently_verified": False,
            "controller_delivery_independently_verified": False,
            "next_decision_independently_verified": False,
            "causal_information_benefit": None,
            "survival_effect": None,
            "worlds_opened": 0, "scientific_lives": 0,
            "scientific_verdict": "NOT_ISSUED", "stage2_2_go": False,
        }
