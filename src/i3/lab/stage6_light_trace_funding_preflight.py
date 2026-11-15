"""Read-only Stage-6-light trace/funding-chain preflight, without running I3.

A native life with ``keep_trace=False`` cannot establish per-step funding from
its end-of-life totals. This optional strict audit requires an entire trace and
recomputes its two native hash chains and every recorded cognitive debit.
For actions without resource gains, the verifier also independently replays
the deterministic five-channel BodyLaws transition and basic position motion.
This is NOT a World/resource/inventory replay, proof that Mind chose an action,
independent source attestation, or permission to open a World.
"""
from __future__ import annotations

from collections import Counter
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path

from i3.lab import stage6_light_native_custody_preflight as custody

BASE_FIELDS = ("t", "action", "param", "option", "body", "pos", "dead")
TRACE_FIELDS = set(BASE_FIELDS) | {"cognitive_work", "cognitive_accounting",
                                   "funding_phases", "info"}
WORK_FIELDS = ("cycles", "simulated_steps", "memory_items", "replays")
CURRENCIES = ("energy", "vigilance")
PHASES = ("decision", "learning")
RATES = {
    "energy": ("energy_per_cycle", "energy_per_simulated_step",
               "energy_per_memory_item", "energy_per_replay"),
    "vigilance": ("vigilance_per_cycle", "vigilance_per_simulated_step",
                  None, "vigilance_per_replay"),
}

# Mirror exactly the BodyLaws v2 asdict snapshot, not a partial bill-only
# declaration. Reference parity is exercised against i3.modules.body in TESTS,
# never imported by the auditor. All five channels are native [0, 100].
LAW_FIELDS = frozenset({
    "food_decay", "water_decay", "sleep_energy_gain",
    "sleep_food_cost_per_energy", "rest_integrity_gain",
    "rest_food_cost_per_integrity", "min_water_for_metabolism",
    "energy_per_cycle", "energy_per_simulated_step",
    "energy_per_memory_item", "energy_per_replay",
    "vigilance_per_cycle", "vigilance_per_simulated_step",
    "vigilance_per_replay", "sleep_vigilance_gain", "version",
})
ACTION_COSTS = {
    "se_deplacer": 2.0, "collecter": 1.0, "manger": 0.5,
    "boire": 0.5, "dormir": 0.25, "attendre": 0.35,
}
MOVES = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
EFFECT_FREE_ACTIONS = frozenset((None, "attendre", "dormir",
                                 "se_deplacer", "collecter"))


def _validate_laws(laws: object) -> dict:
    if (type(laws) is not dict or set(laws) != LAW_FIELDS or
            laws.get("version") != "i3-body-laws-v2" or
            any(not _number(v) for k, v in laws.items() if k != "version") or
            laws["sleep_food_cost_per_energy"] <= 0 or
            laws["rest_food_cost_per_integrity"] <= 0):
        raise ValueError("incomplete or invalid native v2 physical law snapshot")
    return laws


def _clamp(value: float) -> float:
    return 0.0 if value < 0.0 else 100.0 if value > 100.0 else value


def _effect_free_transition(before: list, decision: dict, laws: dict,
                            action: str | None) -> tuple[list, list[str]]:
    """Independent native body.transition parity when no resource gain occurs.

    Token consumption and water acquisition require World state unavailable to
    this reader, so manger/boire MUST NOT enter this function.
    """
    if action not in EFFECT_FREE_ACTIONS:
        raise ValueError("resource action requires unavailable original World replay")
    funded = before[:]
    funded[0] -= _charge(laws, decision, "energy")
    funded[4] -= _charge(laws, decision, "vigilance")
    if funded[0] < 0 or funded[4] < 0:
        raise ValueError("native cognition not physically payable")
    energy, food, water, integrity, vigilance = funded
    if action not in (None, "dormir") and energy < ACTION_COSTS[action]:
        raise ValueError("native motor action not physically payable")
    food = _clamp(food - laws["food_decay"])
    water = _clamp(water - laws["water_decay"])
    hydrated = water >= laws["min_water_for_metabolism"]
    if action == "dormir":
        possible = min(laws["sleep_energy_gain"], max(0.0, 100.0 - energy))
        gained = (min(possible, food / laws["sleep_food_cost_per_energy"])
                  if hydrated else 0.0)
        energy += gained
        food -= gained * laws["sleep_food_cost_per_energy"]
        vigilance += laws["sleep_vigilance_gain"]
    elif action is not None:
        energy -= ACTION_COSTS[action]
    if action in ("attendre", "dormir") and hydrated:
        repair = min(laws["rest_integrity_gain"], max(0.0, 100.0 - integrity),
                     food / laws["rest_food_cost_per_integrity"])
        integrity += repair
        food -= repair * laws["rest_food_cost_per_integrity"]
    after = [_clamp(x) for x in (energy, food, water, integrity, vigilance)]
    reasons = [name for name, idx in (("zero_food", 1), ("zero_water", 2),
                                      ("zero_integrity", 3)) if after[idx] <= 0.0]
    return after, reasons


def _position_after(prev: list, action: str | None, param: object,
                    world: dict) -> list:
    """Simple native World._step position rule; inventory/cell NOT attested."""
    if action == "se_deplacer":
        if type(param) is not str or param not in MOVES:
            raise ValueError("invalid native directional movement")
        dx, dy = MOVES[param]
        expected = [prev[0] + dx, prev[1] + dy]
    else:
        if action in (None, "dormir", "attendre", "boire") and param is not None:
            raise ValueError("native param forbidden for this action")
        expected = prev[:]
    if not (0 <= expected[0] < world["width"] and
            0 <= expected[1] < world["height"]):
        raise ValueError("native movement exits the declared World bounds")
    return expected


def _number(value: object, *, maximum: float = float("inf")) -> bool:
    return (type(value) in (int, float) and isfinite(value) and
            0 <= value <= maximum)


def _same(a: object, b: object) -> bool:
    return (_number(a) and _number(b) and
            abs(a - b) <= 1e-7 + 1e-8 * max(abs(a), abs(b)))


def _body(values: object) -> list:
    if (type(values) is not list or len(values) != 5 or
            not all(_number(x, maximum=100) for x in values)):
        raise ValueError("invalid native five-channel trace body")
    return values


def _work(value: object) -> dict:
    if (type(value) is not dict or set(value) != set(WORK_FIELDS) or
            not all(type(value[k]) is int and 0 <= value[k] <= 10_000_000
                    for k in WORK_FIELDS)):
        raise ValueError("invalid declared native cognitive work")
    return value


def _account(value: object) -> dict:
    if type(value) is not dict or set(value) != set(CURRENCIES):
        raise ValueError("both native currencies are required")
    for entry in value.values():
        if (type(entry) is not dict or
                set(entry) != {"requested", "paid", "unpaid"} or
                not all(_number(x) for x in entry.values()) or
                not _same(entry["requested"], entry["paid"] + entry["unpaid"]) or
                entry["unpaid"] > 1e-12):
            raise ValueError("incomplete/unpaid cognitive work in trace")
    return value


def _charge(laws: dict, work: dict, currency: str) -> float:
    total = 0.0
    for key, amount in zip(RATES[currency], (work[k] for k in WORK_FIELDS)):
        if key is not None:
            rate = laws.get(key)
            if not _number(rate):
                raise ValueError("missing or invalid native cognitive cost rate")
            total += rate * amount
    if not isfinite(total):
        raise ValueError("non-finite native cognitive cost")
    return total


def _phase(value: object, laws: dict) -> tuple[dict, dict, list, list]:
    if type(value) is not dict or set(value) != {
            "work", "accounting", "body_before", "body_after_debit"}:
        raise ValueError("missing native phase-funding receipt")
    work = _work(value["work"])
    accounts = _account(value["accounting"])
    before = _body(value["body_before"])
    after = _body(value["body_after_debit"])
    for idx, currency in ((0, "energy"), (4, "vigilance")):
        expected = _charge(laws, work, currency)
        if (not _same(accounts[currency]["requested"], expected) or
                not _same(accounts[currency]["paid"], expected) or
                not _same(after[idx], before[idx] - expected)):
            raise ValueError("phase work, physical bill or body debit disagree")
    if not all(_same(before[k], after[k]) for k in (1, 2, 3)):
        raise ValueError("cognition debit changed non-cognitive body channels")
    return work, accounts, before, after


def inspect_traced_life(identity: dict, life: dict, *, expected_protocol: str,
                        source_pin: str, source_head: str) -> dict:
    """Verify a *supplied* single life trace and its local paid-work receipts.

    Requires the v2 original envelope to pass custody first. The optional
    ``info`` field is NOT covered by run_life's hash chains and is ignored.
    A self-consistent fabricated trace could also pass: no physical replay,
    independently pinned source, signed timestamp or scientific GO is implied.
    """
    custody._assert_inert()
    generation = identity.get("generation") if type(identity) is dict else None
    custody._case_key(identity, generation)
    custody._check_native_life(identity, life, source_pin, source_head,
                               expected_protocol)
    trace = life.get("trace")
    if (type(trace) is not list or len(trace) != life["steps_lived"] or
            not 1 <= len(trace) <= 400):
        raise ValueError("full keep_trace=True evidence is required")
    world = life["manifest"]["world"]
    laws = _validate_laws(world["laws"])
    expected_start = _body(world["body"])
    initial_position = world["spawn"]
    if (type(initial_position) is not list or len(initial_position) != 2 or
            not all(type(x) is int and x >= 0 for x in initial_position) or
            not 0 <= initial_position[0] < world["width"] or
            not 0 <= initial_position[1] < world["height"]):
        raise ValueError("invalid declared native spawn")
    prev_position = initial_position
    effect_free_checked = 0
    resource_steps_unreplayed = 0
    head = sha256(json.dumps([life["genome"], life["world"],
                              life["life_seed"], life["horizon"]],
                             separators=(",", ":")).encode()).hexdigest()
    evidence_head = life["manifest_id"]
    totals = {c: {k: 0.0 for k in ("requested", "paid", "unpaid")}
              for c in CURRENCIES}
    actions: Counter = Counter()
    first_drink = None
    replayed = 0
    for t, row in enumerate(trace, 1):
        if type(row) is not dict or set(row) != TRACE_FIELDS:
            raise ValueError("missing or unexpected native trace fields")
        if type(row["t"]) is not int or row["t"] != t:
            raise ValueError("trace step sequence is incomplete/reordered")
        current_body = _body(row["body"])
        pos = row["pos"]
        if (type(pos) is not list or len(pos) != 2 or
                not all(type(x) is int and x >= 0 for x in pos)):
            raise ValueError("invalid physical position in trace")
        dead = row["dead"]
        if type(dead) is not list or not all(type(c) is str and c for c in dead):
            raise ValueError("invalid native death receipt")
        if (dead and t != len(trace)) or (
                t == len(trace) and dead != life["death_causes"]):
            raise ValueError("trace death chronology or terminal cause disagrees")
        if row["action"] is not None and (
                type(row["action"]) is not str or
                row["action"] not in {"se_deplacer", "collecter", "manger",
                                      "boire", "dormir", "attendre"}):
            raise ValueError("unexpected motor action in trace")
        expected_position = _position_after(prev_position, row["action"],
                                            row["param"], world)
        if pos != expected_position:
            raise ValueError("native action contradicts physical position")
        prev_position = pos
        if type(row["funding_phases"]) is not dict or set(row["funding_phases"]) != set(PHASES):
            raise ValueError("both real cognitive phases required")
        phases = [_phase(row["funding_phases"][name], laws) for name in PHASES]
        if not all(_same(phases[0][2][k], expected_start[k]) for k in range(5)):
            raise ValueError("funded-body chronology breaks between native steps")
        if row["action"] in EFFECT_FREE_ACTIONS:
            expected_physical, expected_death = _effect_free_transition(
                phases[0][2], phases[0][0], laws, row["action"])
            if (not all(_same(phases[1][2][k], expected_physical[k])
                        for k in range(5)) or dead != expected_death):
                raise ValueError("native effect-free physical transition/death mismatch")
            effect_free_checked += 1
        else:
            # Resource quantities/inventory and scheduled effects need a full
            # World replay, which is deliberately NOT available to this audit.
            resource_steps_unreplayed += 1
        expected_start = current_body
        if not all(_same(phases[-1][3][k], current_body[k]) for k in range(5)):
            raise ValueError("post-learning body must equal traced native body")
        joined = _work(row["cognitive_work"])
        for field in WORK_FIELDS:
            if joined[field] != sum(v[0][field] for v in phases):
                raise ValueError("per-step work differs from funding phases")
        accounts = _account(row["cognitive_accounting"])
        for currency in CURRENCIES:
            for field in totals[currency]:
                amount = sum(v[1][currency][field] for v in phases)
                if not _same(accounts[currency][field], amount):
                    raise ValueError("per-step paid currency differs from phase bills")
                totals[currency][field] += accounts[currency][field]
        base = {k: row[k] for k in BASE_FIELDS}
        head = sha256((head + json.dumps(base, separators=(",", ":"),
                                         sort_keys=True)).encode()).hexdigest()
        evidence_head = custody._digest({
            "previous": evidence_head, "record": base, "work": joined,
            "accounting": accounts, "funding_phases": row["funding_phases"]})
        actions[row["action"] if row["action"] is not None else "physical_inactivity"] += 1
        if row["action"] == "boire" and first_drink is None:
            first_drink = t
        replayed += phases[1][0]["replays"]
    if head != life["trace_head"]:
        raise ValueError("native action/body/step hash chain mismatch")
    terminal_head = custody._digest({
        "previous": evidence_head, "terminal": life["terminal"],
        "accounting": life["cognitive_accounting"]})
    if terminal_head != life["evidence_head"]:
        raise ValueError("native paid-work evidence-chain/terminal mismatch")
    for currency in CURRENCIES:
        for key, observed in totals[currency].items():
            if not _same(life["cognitive_accounting"]["totals"][currency][key], observed):
                raise ValueError("end-of-life cost totals differ from trace")
    if (life["cognitive_accounting"]["inactive_steps"] != actions["physical_inactivity"] or
            life["cognitive_accounting"]["replays_executed"] != replayed):
        raise ValueError("declared inactivity/replay totals differ from trace")
    if (type(life.get("actions")) is not dict or life["actions"] != dict(sorted(actions.items())) or
            life.get("drinks") != actions["boire"] or
            life.get("meals") != actions["manger"] or
            life.get("first_drink_step") != first_drink):
        raise ValueError("native action summary differs from trace")
    body_end = _body(life.get("final_body"))
    if any(not _same(body_end[k], round(expected_start[k], 6)) for k in range(5)):
        raise ValueError("native final body summary differs from trace")
    return {
        "schema": "i3-stage6-native-trace-funding-preflight/v1",
        "status": "SUPPLIED_TRACE_TWO_CURRENCY_CHAIN_MATCH_NOT_ATTESTED",
        "trace_steps_checked": len(trace),
        "effect_free_physical_transitions_checked": effect_free_checked,
        "resource_steps_not_physically_replayed": resource_steps_unreplayed,
        "native_position_continuity_checked": True,
        "complete_world_physics_replayed": False,
        "trace_head_recomputed": True,
        "funding_evidence_head_recomputed": True,
        "two_currency_phase_and_total_bills_checked": True,
        "trace_info_cryptographically_authenticated": False,
        "motor_decision_causality_or_world_physics_replayed": False,
        "independent_original_source_and_time_attested": False,
        "independent_population_sampling_verified": False,
        "owner_authorization": False,
        "new_worlds_opened": 0,
        "new_lives_created": 0,
        "science_verdict": "NOT_ISSUED",
    }


def run_life(*_args, **_kwargs):
    raise PermissionError("trace auditor cannot open a real life")


def open_world(*_args, **_kwargs):
    raise PermissionError("trace auditor cannot open a World")


def authorize_science(*_args, **_kwargs):
    raise PermissionError("trace auditor cannot grant scientific authority")
