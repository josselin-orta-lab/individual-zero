"""I3 passive action forecast: model-funded readout and two-phase target custody.

SOFTWARE-ONLY Stage 2.1; no World or run_life opened. Every observation
here is an explicitly synthetic fixture. Native CognitiveBudget approval
is not a physically paid World receipt. No policy or innate change.
"""
from __future__ import annotations

from dataclasses import asdict
from math import isfinite
import json

from ..modules.body import (ACTION_COSTS, BodyLaws, CognitiveBudget,
                            CognitiveWork, cognitive_cost, debit_cognition,
                            validate_body)
from ..modules.mind import Mind
from .stage2_action_conditional_existing_effects import (
    _fixture, _innate_self_reward, _sha, passive_readouts)

SCHEMA = "i3-stage2.1-action-phase-model-funded-synthetic/v1"
PRIMARY_TARGET = "POST_PAID_LEARNING"
SECONDARY_TARGET = "IMMEDIATE_POST_WORLD"
LEARNING_STATUSES = ("PAID_LEARNING", "NO_FUNDED_LEARNING",
                     "TERMINAL_NO_LEARNING")
MAX_MEMORIES = 512


def proposed_readout_work(n: int) -> CognitiveWork:
    """Conservative operator categories, NOT CPU/bytes/joules calibration.

    Covers 3 scalar self-body projections, learned effect lookups, and the
    original O(n) native memory-tuple arity check. Laboratory SHA is separate.
    """
    if type(n) is not int or not 0 <= n <= MAX_MEMORIES:
        raise ValueError("bounded personal memory size required")
    return CognitiveWork(cycles=6, memory_items=48+n)


def _matching_account(laws, work, account):
    if type(account) is not dict:
        raise ValueError("two-currency model-accounting receipt required")
    energy, vigilance = cognitive_cost(laws, work)
    for c, amount in (("energy", energy), ("vigilance", vigilance)):
        entry = account.get(c)
        if (type(entry) is not dict or
                any(type(entry.get(k)) not in (int, float)
                    or not isfinite(entry[k])
                    for k in ("requested", "paid", "unpaid")) or
                abs(entry["requested"]-amount) > 1e-10 or
                abs(entry["paid"]-amount) > 1e-10 or
                entry["unpaid"] != 0):
            raise ValueError("native two-currency bill missing/partially funded")
    return energy, vigilance


class SyntheticPhaseTicket:
    """Immutable-on-use prequential custody; not an actual living witness."""

    def __init__(self, *, payload, laws, work, inherited):
        self.payload = payload
        self.sha256 = _sha(payload)
        self.laws = laws
        self.work = work
        self.inherited = inherited
        self._state = "FROZEN_BEFORE_OUTCOME"
        self._world_body = None
        self._dead = None
        self._post_body = None
        self._world_account = None
        self._learning_account = None
        self._learning_work = None
        self._learning_status = None

    def _check(self, seal):
        if seal != self.sha256 or _sha(self.payload) != self.sha256:
            raise RuntimeError("preoutcome choice, source or forecast seal tampered")

    def observe_synthetic_world(self, *, seal, action, param, work,
                                body, dead, accounting):
        self._check(seal)
        if self._state != "FROZEN_BEFORE_OUTCOME":
            raise RuntimeError("immediate World-phase already observed")
        if (action != self.payload["selected_action"]
                or param != self.payload["selected_param"]
                or work != self.work):
            raise PermissionError("factual action or decision work does not match seal")
        if type(dead) not in (tuple, list):
            raise TypeError("original death-cause sequence required")
        _matching_account(self.laws, work, accounting)
        immediate = validate_body(body)
        self._world_body = immediate
        self._dead = tuple(dead)
        self._world_account = accounting
        self._state = "IMMEDIATE_WORLD_OBSERVED"

    def observe_synthetic_learning(self, *, seal, status, work,
                                   body, accounting):
        self._check(seal)
        if self._state != "IMMEDIATE_WORLD_OBSERVED":
            raise RuntimeError("cannot score learning before immediate World-phase")
        if status not in LEARNING_STATUSES or not isinstance(work, CognitiveWork):
            raise ValueError("explicit learning phase and native work required")
        post = validate_body(body)
        if status == "PAID_LEARNING":
            if self._dead or work == CognitiveWork():
                raise ValueError("dead or zero-work cannot execute outcome learning")
            _matching_account(self.laws, work, accounting)
            expected, _ = debit_cognition(self._world_body, self.laws, work)
            if post != expected:
                raise ValueError("post-learning body disagrees with native debit")
        else:
            if (status == "TERMINAL_NO_LEARNING") != bool(self._dead):
                raise ValueError("terminal and unfunded statuses must be distinct")
            if work != CognitiveWork() or post != self._world_body:
                raise ValueError("zero/terminal learning may not change physical body")
            _matching_account(self.laws, work, accounting)
        self._post_body = post
        self._learning_account = accounting
        self._learning_work = work
        self._learning_status = status
        self._state = "POST_LEARNING_OBSERVED"

    def score_synthetic(self, *, seal):
        self._check(seal)
        if self._state != "POST_LEARNING_OBSERVED":
            raise RuntimeError("both phase observations required before scoring")
        theta, powers, weights, d_max = self.inherited
        terminal = bool(self._dead)
        targets = {
            PRIMARY_TARGET: (-d_max if terminal else _innate_self_reward(
                theta, powers, weights, self._post_body)),
            SECONDARY_TARGET: (-d_max if terminal else _innate_self_reward(
                theta, powers, weights, self._world_body)),
        }
        predictions = self.payload["frozen_forecasts"]
        loss = {phase: {
            mode: (predictions[mode] - target)**2
            for mode in ("action", "global", "persistence")}
            for phase, target in targets.items()}
        if any(not isfinite(t) for t in targets.values()) or any(
                not isfinite(v) for errors in loss.values()
                for v in errors.values()):
            raise RuntimeError("nonfinite phase-aware proper score")
        self._state = "SYNTHETIC_SCORED"
        return {
            "schema": SCHEMA, "status": "SYNTHETIC_TWO_PHASE_SCORED",
            "preoutcome_sha256": self.sha256,
            "selected_action": self.payload["selected_action"],
            "primary_phase": PRIMARY_TARGET,
            "secondary_phase": SECONDARY_TARGET,
            "terminal_observed": terminal,
            "learning_status": self._learning_status,
            "phase_bodies": {PRIMARY_TARGET: self._post_body,
                             SECONDARY_TARGET: self._world_body},
            "phase_targets": targets,
            "phase_squared_loss": loss,
            "decision_model_work": asdict(self.work),
            "learning_model_work": asdict(self._learning_work),
            "decision_model_accounting": self._world_account,
            "learning_model_accounting": self._learning_account,
            "native_living_debit_attested": False,
            "external_sha_cpu_billed": False,
            "scientific_lives": 0, "scientific_verdict": "NOT_ISSUED",
        }

    def right_censor_synthetic(self, *, seal):
        self._check(seal)
        if self._state != "FROZEN_BEFORE_OUTCOME":
            raise RuntimeError("observed future cannot be erased as right-censored")
        self._state = "RIGHT_CENSORED_NOT_SCORED"
        return {
            "schema": SCHEMA, "status": "RIGHT_CENSORED_NOT_SCORED",
            "preoutcome_sha256": self.sha256,
            "primary_phase": PRIMARY_TARGET,
            "target": None, "squared_loss": None,
            "scientific_lives": 0, "scientific_verdict": "NOT_ISSUED",
        }


def admit_and_freeze(*, mind: Mind, capture_body, action, param,
                     budget: CognitiveBudget, identity):
    """Original Mind chooses before this proposed optional readout; no World."""
    if type(mind) is not Mind or type(budget) is not CognitiveBudget:
        raise TypeError("reference Mind and real native-budget type required")
    if type(identity) is not str or not 0 < len(identity) <= 128:
        raise ValueError("fixed provenance identity required")
    before = validate_body(capture_body)
    if before != budget.body:
        raise PermissionError("current allowance must match first-person body")
    if action is None:
        if mind.last is not None or param is not None:
            raise PermissionError("null motor choice cannot impersonate selected action")
        return {"status": "NO_SELECTED_ACTION", "work_added": 0,
                "readouts_executed": 0, "scientific_lives": 0}
    if type(action) is not str or action not in ACTION_COSTS:
        raise ValueError("reference chosen motor action required")
    if param is not None and type(param) is not str:
        raise ValueError("original action parameter must be text or None")
    if (type(mind.last) is not tuple or len(mind.last) != 4
            or tuple(mind.last[0]) != before
            or mind.last[2] != action or mind.last[3] != param):
        raise PermissionError("action was not selected by original Mind.decide")
    if budget.work == CognitiveWork():
        raise PermissionError("original decision cognition must already be funded")
    n = len(mind.buffer)
    if (type(mind.m_max) is not int or
            not 0 <= n <= mind.m_max <= MAX_MEMORIES):
        raise ValueError("personally stored buffer exceeds genomic capacity")
    extra = proposed_readout_work(n)
    energy, vigilance = cognitive_cost(budget.laws, extra)
    initial_work = budget.work
    if (budget.remaining[0] < energy or budget.remaining[4] < vigilance
            or (action != "dormir" and
                budget.remaining[0] - energy < ACTION_COSTS[action])):
        return {
            "status": "NO_FUNDED_READOUT", "work_added": 0,
            "readouts_executed": 0, "energy_requested": energy,
            "vigilance_requested": vigilance,
            "original_decision_work": asdict(initial_work),
            "scientific_lives": 0,
        }
    if not budget.try_spend(extra):
        raise RuntimeError("native budget rejected previously admissible extra work")
    # Every optional readout, scan and provenance hash happens AFTER grant.
    forecast = passive_readouts(mind, before, action)
    expected_work = CognitiveWork(
        cycles=initial_work.cycles+extra.cycles,
        simulated_steps=initial_work.simulated_steps+extra.simulated_steps,
        memory_items=initial_work.memory_items+extra.memory_items,
        replays=initial_work.replays+extra.replays)
    if budget.work != expected_work:
        raise RuntimeError("native cumulative work unexpectedly changed")
    payload = {
        "schema": SCHEMA, "identity": identity,
        "selected_action": action, "selected_param": param,
        "actual_before_body": before,
        "native_personal_memory_count": n,
        "native_effect_source_sha256":
            forecast["native_selected_effect_sha256"],
        "innate_parameter_sha256": forecast["innate_parameter_sha256"],
        "action_specific_history": forecast["action_specific_history"],
        "frozen_forecasts": dict(forecast["scalar_forecasts"]),
        "original_decision_work": asdict(initial_work),
        "cumulative_model_work": asdict(budget.work),
        "incremental_model_work": asdict(extra),
        "primary_target_phase": PRIMARY_TARGET,
        "secondary_target_phase": SECONDARY_TARGET,
        "forecast_before_both_future_phases": True,
    }
    return SyntheticPhaseTicket(
        payload=payload, laws=budget.laws, work=budget.work,
        inherited=(tuple(mind.theta), tuple(mind.p),
                   tuple(mind.w), mind.d_max))


def _synthetic_budget(mind, body, action="attendre"):
    b = CognitiveBudget(body, BodyLaws())
    if not b.try_spend(CognitiveWork(cycles=3, memory_items=12)):
        raise RuntimeError("synthetic original decision allowance failed")
    mind.last = (body, (action,), action, None)
    return b


def _zero_account():
    return debit_cognition((50., 50., 50., 50., 50.),
                           BodyLaws(), CognitiveWork())[1]


def audit():
    body = (30., 30., 30., 35., 30.)
    source = _fixture()
    budget = _synthetic_budget(source, body)
    ticket = admit_and_freeze(
        mind=source, capture_body=body, action="attendre", param=None,
        budget=budget, identity="synthetic-frozen-two-phase-main")
    if not isinstance(ticket, SyntheticPhaseTicket):
        raise RuntimeError("synthetic action readout not authorized")
    immediate = (27., 29., 29., 35., 29.)
    ticket.observe_synthetic_world(
        seal=ticket.sha256, action="attendre", param=None,
        work=budget.work, body=immediate, dead=(),
        accounting=debit_cognition(body, budget.laws, budget.work)[1])
    learning_work = CognitiveWork(cycles=2, simulated_steps=16, memory_items=1)
    post, learning_receipt = debit_cognition(
        immediate, budget.laws, learning_work)
    ticket.observe_synthetic_learning(
        seal=ticket.sha256, status="PAID_LEARNING", work=learning_work,
        body=post, accounting=learning_receipt)
    paid = ticket.score_synthetic(seal=ticket.sha256)

    null_source = _fixture()
    null_budget = _synthetic_budget(null_source, body)
    null_ticket = admit_and_freeze(
        mind=null_source, capture_body=body, action="attendre", param=None,
        budget=null_budget, identity="synthetic-no-funded-learning")
    null_ticket.observe_synthetic_world(
        seal=null_ticket.sha256, action="attendre", param=None,
        work=null_budget.work, body=immediate, dead=(),
        accounting=debit_cognition(body, null_budget.laws, null_budget.work)[1])
    null_ticket.observe_synthetic_learning(
        seal=null_ticket.sha256, status="NO_FUNDED_LEARNING",
        work=CognitiveWork(), body=immediate, accounting=_zero_account())
    zero = null_ticket.score_synthetic(seal=null_ticket.sha256)

    dead_source = _fixture()
    dead_budget = _synthetic_budget(dead_source, body)
    death = admit_and_freeze(
        mind=dead_source, capture_body=body, action="attendre", param=None,
        budget=dead_budget, identity="synthetic-terminal-no-learning")
    dead_body = (25., 29., 0., 35., 29.)
    death.observe_synthetic_world(
        seal=death.sha256, action="attendre", param=None,
        work=dead_budget.work, body=dead_body, dead=("zero_water",),
        accounting=debit_cognition(body, dead_budget.laws, dead_budget.work)[1])
    death.observe_synthetic_learning(
        seal=death.sha256, status="TERMINAL_NO_LEARNING",
        work=CognitiveWork(), body=dead_body, accounting=_zero_account())
    terminal = death.score_synthetic(seal=death.sha256)

    censor_source = _fixture()
    censor_budget = _synthetic_budget(censor_source, body)
    censor = admit_and_freeze(
        mind=censor_source, capture_body=body, action="attendre", param=None,
        budget=censor_budget, identity="synthetic-right-censor")
    missing = censor.right_censor_synthetic(seal=censor.sha256)

    report = {
        "schema": SCHEMA,
        "status": "SOFTWARE_PHASE_AND_PREAUTHORIZATION_CONTRACT_ONLY",
        "primary_target_phase": PRIMARY_TARGET,
        "secondary_target_phase": SECONDARY_TARGET,
        "modeled_readout_work": asdict(proposed_readout_work(0)),
        "modeled_readout_energy_vigilance": cognitive_cost(
            BodyLaws(), proposed_readout_work(0)),
        "positive_learning_phase_target_diverges": (
            paid["phase_targets"][PRIMARY_TARGET] !=
            paid["phase_targets"][SECONDARY_TARGET]),
        "no_learning_phase_target_identical": (
            zero["phase_targets"][PRIMARY_TARGET] ==
            zero["phase_targets"][SECONDARY_TARGET]),
        "terminal_phase_target_identical": (
            terminal["phase_targets"][PRIMARY_TARGET] ==
            terminal["phase_targets"][SECONDARY_TARGET] ==
            -dead_source.d_max),
        "explicit_unscored_right_censor": (
            missing["status"] == "RIGHT_CENSORED_NOT_SCORED" and
            missing["squared_loss"] is None),
        "synthetic_phase_scores": {
            "paid_learning": paid["phase_squared_loss"],
            "no_learning": zero["phase_squared_loss"],
            "terminal": terminal["phase_squared_loss"]},
        "actual_worlds_created": 0, "actually_lived_readout_debits": 0,
        "native_model_admissions_only": True,
        "cost_tariff_host_cpu_calibrated": False,
        "experimental_utility_established": False,
        "scientific_lives": 0, "scientific_verdict": "NOT_ISSUED",
        "stage2_2_go": False,
    }
    if not (report["positive_learning_phase_target_diverges"]
            and report["no_learning_phase_target_identical"]
            and report["terminal_phase_target_identical"]
            and report["explicit_unscored_right_censor"]):
        raise RuntimeError("synthetic two-phase falsifier did not pass")
    return report


if __name__ == "__main__":
    print("I3_ACTION_PHASE_MODEL_BUDGET_RESULT="+json.dumps(audit(), sort_keys=True))
