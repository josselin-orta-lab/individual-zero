"""Opt-in LOCAL Stage-1 falsifier, not the adopted reference or a spatial policy.

Actual choices use personal two-step returns, never reference score addends.
The stationary unknown prior and half episodic partition are explicit prototype
assumptions, not learned facts, calibrated uncertainty or a survival guarantee.
"""
from __future__ import annotations

from dataclasses import asdict

from .body import (CognitiveBudget, CognitiveFundingError, CognitiveWork,
                   VITAL, capacities, debit_cognition)
from .information_value import WORK_KEYS, _add_work, paid_information_value
from .mind import DIRS, Mind
from .personal_outcomes import PersonalOutcomes, STORE_WORK

ZERO = (0.0,) * 5


def _work_dict_delta(after, before):
    return {k: getattr(after, k) - getattr(before, k) for k in WORK_KEYS}


def local_options(pos, mapping, inventory):
    """Structural possibilities in the PERSONAL map, not unseen World cells."""
    water, tokens = mapping[pos]
    opts = [("dormir", [("dormir",)], None),
            ("attendre", [("attendre",)], None)]
    if water:
        opts.append(("boire", [("boire",)], None))
    for token in tokens:
        opts.append((f"collecter:{token}", [("collecter", token)], None))
    for token, count in inventory:
        if count > 0:
            opts.append((f"manger:{token}", [("manger", token)], None))
    for name, dx, dy in DIRS:
        q = (pos[0] + dx, pos[1] + dy)
        if mapping.get(q) is not None:
            opts.append((f"move:{name}", [("se_deplacer",)], ("se_deplacer", name)))
    return opts


def effect_key(option):
    key = option[1][0]
    return (key[0], key[1] if len(key) > 1 else None)


def continuation_options(pos, mapping, inventory, probe):
    """Update only deterministic inventory/location, assume no leftover stock.

A consumed item cannot be consumed twice. Collection grants one carried item,
but neither collection nor drinking grants unseen remaining environmental stock.
Future motor affordability is still a prediction, never an execution authority.
"""
    mapping, inv = dict(mapping), dict(inventory)
    action, token = effect_key(probe)
    if action == "se_deplacer":
        _, dx, dy = next(d for d in DIRS if d[0] == probe[2][1])
        pos = (pos[0] + dx, pos[1] + dy)
    elif action == "manger":
        if inv.get(token, 0) < 1:
            raise ValueError("hypothetical consumption requires carried inventory")
        inv[token] -= 1
    elif action == "collecter":
        water, tokens = mapping[pos]
        if token not in tokens:
            raise ValueError("hypothetical collection requires personal presence")
        inv[token] = inv.get(token, 0) + 1
        mapping[pos] = (water, tuple(t for t in tokens if t != token))
    elif action == "boire":
        mapping[pos] = (False, mapping[pos][1])
    return tuple((o[0], effect_key(o)) for o in
                 local_options(pos, mapping, tuple(inv.items())))


class StationaryUnknownOutcomes(PersonalOutcomes):
    """No positive gain invented. Stationarity can still be over-optimistic."""
    def __init__(self, capacity):
        super().__init__(capacity)
        self.unknown_reads = 0

    def _missing_support(self, key):
        self.unknown_reads += 1
        return (ZERO,)  # Not appended to experience, never inherited.


class InformationMind(Mind):
    def __init__(self, genome, life_seed, **kwargs):
        if (kwargs.get("effect_readout", "full") != "full" or
                kwargs.get("score_addend_mode", "normal") != "normal"):
            raise ValueError("local information candidate rejects old readout/addend modes")
        super().__init__(genome, life_seed, **kwargs)
        total = self.m_max
        self.personal = StationaryUnknownOutcomes(total // 2)
        self.m_max = total - total // 2
        self.personal_records = 0
        self._pending_personal = None
        self._decision_work = CognitiveWork()
        self._observer_cost_profile = None

    def _finish(self, budget, opts, scored, witnesses, outcome, funding,
                action=None, param=None, oid=None, rejected=0, comp=None):
        info = {"option": oid, "funding": funding,
                "experimental_policy": "local_information_v1"}
        if self.observer_decision_diagnostics:
            diag = {
                "offered_options": len(opts), "scored_options": len(scored),
                "rejected_controls": rejected, "decision_outcome": outcome,
                "offered_families": self._observer_option_families(o[0] for o in opts),
                "scored_families": self._observer_option_families(o for o, _ in scored),
                "pre_body": budget.body, "score_witness": witnesses}
            if comp is not None:
                diag["competition_witness"] = comp
            if self._observer_cost_profile is not None:
                self._observer_cost_profile["status"] = outcome
                self._observer_cost_profile["actual_total_work"] = asdict(budget.work)
                diag["cost_profile"] = self._observer_cost_profile
            info["observer"] = diag
        self._decision_work = budget.work
        return action, param, budget.work, info

    def decide(self, cap, budget):
        if tuple(cap["body"]) != budget.body or budget.work != CognitiveWork():
            raise ValueError("fresh allowance must match the perceived body")
        if any(budget.body[k] <= 0 for k in VITAL):
            raise ValueError("no decision after physical death")
        self.last = None
        self._pending_personal = None
        self._observer_cost_profile = None
        if self.observer_decision_diagnostics:
            zero = {k: 0 for k in WORK_KEYS}
            self._observer_cost_profile = {
                "schema": "i3-local-decision-cost-profile/v1",
                "status": "STARTED",
                "phase": "base_processing",
                "base_processing": dict(zero),
                "options": [],
                "batch_setup": dict(zero),
                "competition": dict(zero),
                "actual_total_work": dict(zero),
            }
        slots = (len(self.buffer) + 2 * len(self.map) + len(self.effects.stats)
                 + len(self.tokens) + len(self.external) + len(self.acc)
                 + sum(len(v) for v in self.values) + 12
                 + 7 * len(self.personal._samples) + len(cap["inventory"])
                 + sum(len(c[1]) for c in (cap["here"], *cap["neighbors"])
                       if c is not None))
        before = budget.work
        if not budget.try_spend(CognitiveWork(cycles=3, memory_items=slots)):
            if self._observer_cost_profile is not None:
                self._observer_cost_profile["phase"] = "base_processing_unfunded"
            return self._finish(budget, [], [], [], "no_processing_budget", "NO_PROCESSING_BUDGET")
        if self._observer_cost_profile is not None:
            self._observer_cost_profile["base_processing"] = _work_dict_delta(budget.work, before)
            self._observer_cost_profile["phase"] = "option_preparation"
        cycles, _, miss = capacities(budget.body, self.n_base, self.h_max)
        inv = self.perceive(cap, miss)
        opts = local_options(self.pos, self.map, inv)
        prepared = []
        compatibility_scan_savings = CognitiveWork()
        decision_index_savings = CognitiveWork()
        support_index = self.personal.begin_support_index()
        self.personal.unknown_reads = 0
        try:
            for opt in opts:
                entry = None
                construction_receipt = None
                if self._observer_cost_profile is not None:
                    entry = {
                        "option": opt[0],
                        "phase": "hypothetical_setup",
                        "hypothetical_setup": {k: 0 for k in WORK_KEYS},
                        "personal_construction": {},
                        "kernel": {},
                    }
                    self._observer_cost_profile["options"].append(entry)
                # Fund the detached hypothetical local map/inventory operation.
                before = budget.work
                budget.spend(CognitiveWork(cycles=1, memory_items=2 * len(self.map) + len(inv) + 8))
                if entry is not None:
                    entry["hypothetical_setup"] = _work_dict_delta(budget.work, before)
                    entry["phase"] = "personal_construction"
                    construction_receipt = {}
                continuations = continuation_options(self.pos, self.map, inv, opt)
                support_keys = tuple(dict.fromkeys(
                    (effect_key(opt), *(key for _, key in continuations))))
                removed_scans = max(0, len(support_keys) - 1)
                scan_savings = CognitiveWork(
                    cycles=removed_scans,
                    memory_items=7 * len(self.personal._samples) * removed_scans)
                compatibility_scan_savings = _add_work(
                    compatibility_scan_savings, scan_savings)
                # After the first paid scan, later option constructions still
                # pay one lookup cycle and per-key bookkeeping, but do not
                # traverse the same immutable personal history again.
                index_savings = CognitiveWork(
                    memory_items=7 * len(self.personal._samples)
                    if support_index.built else 0)
                decision_index_savings = _add_work(
                    decision_index_savings, index_savings)
                if entry is not None:
                    entry["forecast_exhaustive_scan_savings"] = asdict(scan_savings)
                    entry["forecast_decision_index_savings"] = asdict(index_savings)
                unknown_before = self.personal.unknown_reads
                outcomes = self.personal.construct(
                    effect_key(opt), continuations, budget,
                    work_receipt=construction_receipt,
                    support_index=support_index)
                if entry is not None:
                    entry["personal_construction"] = construction_receipt
                    entry["phase"] = "prepared"
                prepared.append((opt, outcomes, self.personal.unknown_reads - unknown_before))
            before = budget.work
            budget.spend(CognitiveWork(cycles=1, memory_items=5 * len(prepared)))
            if self._observer_cost_profile is not None:
                self._observer_cost_profile["batch_setup"] = _work_dict_delta(budget.work, before)
                self._observer_cost_profile["forecast_exhaustive_scan_savings"] = asdict(
                    compatibility_scan_savings)
                self._observer_cost_profile["forecast_decision_index_savings"] = asdict(
                    decision_index_savings)
                self._observer_cost_profile["phase"] = "kernel_evaluation"
            evaluation_end = budget.work
            for _, outcomes, _ in prepared:
                cells = len(outcomes) * len(outcomes[0].continuations)
                evaluation_end = _add_work(evaluation_end, CognitiveWork(
                    cycles=cells + 2, simulated_steps=cells * (2 + len(self.proj_chunks)),
                    memory_items=len(outcomes) * 7 + cells * 5))
            forecast_evaluation_end = _add_work(
                evaluation_end, compatibility_scan_savings)
            forecast_evaluation_end = _add_work(
                forecast_evaluation_end, decision_index_savings)
            ceiling = _add_work(forecast_evaluation_end, CognitiveWork(cycles=cycles))
            debit_cognition(budget.body, budget.laws, ceiling)  # Quote, NOT spend.
            scored, witnesses = [], []
            cell_cache = {}
            for index, (opt, outcomes, unknown) in enumerate(prepared):
                if self._observer_cost_profile is not None:
                    self._observer_cost_profile["phase"] = "kernel:" + opt[0]
                value = paid_information_value(
                    self, outcomes, budget, forecast_work=ceiling, cell_cache=cell_cache)
                if self._observer_cost_profile is not None:
                    entry = self._observer_cost_profile["options"][index]
                    entry["kernel"] = value["work_breakdown"]
                    entry["cell_reuse"] = value["cell_reuse"]
                    entry["phase"] = "scored"
                score = value["informed_value"]
                scored.append((opt[0], score))
                if self.observer_decision_diagnostics:
                    witnesses.append({
                        "option": opt[0], "base_return": score, "total_score": score,
                        "curiosity_bonus_computed": 0.0, "curiosity_bonus_applied": 0.0,
                        "risk_penalty_computed": 0.0, "risk_penalty_applied": 0.0,
                        "curiosity_risk_bonus": 0.0, "uncertainty": None,
                        "first_forecast": None, "score_kind": "local_expected_distress",
                        "information_value": value["information_value"],
                        "unknown_support_queries": unknown,
                        "forecast_start_body": value["forecast_start_body"],
                        "kernel_work": value["work"],
                        "kernel_cell_reuse": value["cell_reuse"],
                        "forecast_work_ceiling": asdict(ceiling)})
            if any(getattr(budget.work, k) > getattr(evaluation_end, k) for k in WORK_KEYS):
                raise RuntimeError("reused local evaluation exceeded exhaustive work ceiling")
        except CognitiveFundingError:
            # No complete comparison, no command and no refund. The ordinary
            # runtime settles all consumed work and advances passive physiology.
            return self._finish(budget, opts, [], [], "no_funded_score", "NO_FUNDED_SCORE")
        before_competition = budget.work
        if self._observer_cost_profile is not None:
            self._observer_cost_profile["phase"] = "competition"
        winner, _ = self._compete(scored, cycles, budget)
        if self._observer_cost_profile is not None:
            self._observer_cost_profile["competition"] = _work_dict_delta(
                budget.work, before_competition)
            self._observer_cost_profile["phase"] = "motor_control"
        ranked = [winner] + [o for o, _ in sorted(scored, key=lambda x: -x[1]) if o != winner]
        by_id = {o[0]: o for o in opts}
        comp = self._observer_competition if self.observer_full_competition else None
        if comp is not None:
            comp["control_order"], comp["control_attempts"] = list(ranked), []
        rejected = 0
        for oid in ranked:
            action, param = self._admit(by_id[oid], inv, budget.remaining)
            if comp is not None:
                comp["control_attempts"].append({"option": oid, "admitted": action is not None})
            if action is not None:
                break
            rejected += 1
        else:
            if comp is not None:
                comp.update(status="ALL_CONTROLS_REJECTED", final_admitted_option=None)
            return self._finish(budget, opts, scored, witnesses, "control_rejected",
                                "NO_FUNDED_MOTOR", rejected=rejected, comp=comp)
        self.intention = None  # All local plans have one physical step.
        self.last = (cap["body"], by_id[oid][1][0], action, param)
        if comp is not None:
            comp.update(status="ACTION_ADMITTED", final_admitted_option=oid,
                        final_admitted_action=action, intention_after=self.intention)
        return self._finish(budget, opts, scored, witnesses, "action_admitted",
                            "FUNDED", action, param, oid, rejected, comp)

    def prepare_learning(self, result, budget):
        self._pending_personal = None
        replay_limit = super().prepare_learning(result, budget)
        if replay_limit is not None and budget.try_spend(STORE_WORK):
            before, key, action, _ = self.last
            key = (action, key[1] if action in ("manger", "collecter") else None)
            self._pending_personal = (key, before, self._decision_work,
                                      tuple(result["body"]), budget.laws)
        return replay_limit

    def learn_from_outcome(self, result, *, replay_limit=0, replay_retention=True):
        if result["dead"]:
            self._pending_personal = None
            return 0
        count = super().learn_from_outcome(result, replay_limit=replay_limit,
                                          replay_retention=replay_retention)
        pending, self._pending_personal = self._pending_personal, None
        if pending is not None:
            key, before, decision, physical_body, laws = pending
            # A checked suballowance for the STORE_WORK already prepaid and
            # settled in the ordinary learning bill, NOT a second World debit.
            sub = CognitiveBudget(physical_body, laws)
            self.personal.observe(key, before, decision, sub)
            if sub.work != STORE_WORK:
                raise RuntimeError("personal recording exceeded its prepaid block")
            self.personal_records += 1
        return count
