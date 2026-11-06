"""P2 exit contract: equal initial opportunity is NOT equal realized cognition.

This observer-only laboratory audit decides whether two completed I3 lives
received equivalent experimental opportunities. It does not compare against
oracle/searcher scores and never supplies provenance to the mind.
"""
from __future__ import annotations

from math import isclose

from i3.modules.body import CognitiveWork, cognitive_cost
from i3.runtime.provenance import digest, world_snapshot

TOL = 1e-9
SCHEMA = "i3-p2-equal-opportunity-v1"
WORK_KEYS = ("cycles", "simulated_steps", "memory_items", "replays")


def _settled_life(life: dict, *, require_trace: bool = False) -> None:
    """Refuse invented deaths, unsupported payment, or incomplete trace claims."""
    manifest = life["manifest"]
    if manifest["execution_model"] != "i3-funded-v2":
        raise ValueError("mixed physical execution models")
    if digest(manifest["world"]) != manifest["world_sha256"]:
        raise ValueError("world manifest hash does not match world content")
    if manifest["horizon"] != life["horizon"] or manifest["life_seed"] != life["life_seed"]:
        raise ValueError("mismatched life manifest context")
    horizon, steps = life["horizon"], life["steps_lived"]
    if type(horizon) is not int or horizon < 1 or type(steps) is not int:
        raise ValueError("invalid life horizon/steps")
    if not 1 <= steps <= horizon:
        raise ValueError("life steps out of range")
    terminal = life["terminal"]
    if terminal not in ("dead", "censored") or (terminal == "censored" and steps != horizon):
        raise ValueError("censored survivors must complete the horizon")
    if terminal == "dead" and not life["death_causes"]:
        raise ValueError("death requires a physical cause")
    if terminal == "censored" and life["death_causes"]:
        raise ValueError("censored lives are not dead")
    account = life["cognitive_accounting"]
    if (account["schema"] != "i3-cognitive-funding/v2" or
        account["status"] != "SETTLED_FOR_DECLARED_WORK" or
        account["shortfall_steps"] != 0 or account["pending_replays"] != 0 or
        abs(account["pending_energy"]) > TOL or
        abs(account["pending_vigilance"]) > TOL):
        raise ValueError("individual cognition is not fully settled")
    for channel in ("energy", "vigilance"):
        amounts = account["totals"][channel]
        if (any(amounts[k] < -TOL for k in ("requested", "paid", "unpaid")) or
            abs(amounts["unpaid"]) > TOL or
            not isclose(amounts["requested"], amounts["paid"], abs_tol=TOL)):
            raise ValueError("individual spent unaccounted cognitive work")
    if require_trace or "trace" in life:
        rows = life.get("trace", ())
        if len(rows) != steps:
            raise ValueError("incomplete individual work witness")
        for i, row in enumerate(rows):
            if row["t"] != i + 1:
                raise ValueError("nonsequential witness")
            if row["dead"] and i + 1 != steps:
                raise ValueError("a dead life cannot advance again")
            learning = row["funding_phases"]["learning"]
            if row["dead"] and any(learning["work"][key] for key in WORK_KEYS):
                raise ValueError("postmortem learning bill is not permitted")
            for phase in ("decision", "learning"):
                work = row["funding_phases"][phase]["work"]
                if set(work) != set(WORK_KEYS):
                    raise ValueError("unrecognized work schema")
                for channel in ("energy", "vigilance"):
                    bill = row["funding_phases"][phase]["accounting"][channel]
                    if (bill["unpaid"] > TOL or
                        abs(bill["requested"] - bill["paid"]) > TOL):
                        raise ValueError("unpaid individual work witness")


def compare_equal_opportunity(a: dict, b: dict) -> dict:
    """Two life arms may choose/die/spend differently, not begin differently."""
    _settled_life(a)
    _settled_life(b)
    ma, mb = a["manifest"], b["manifest"]
    # World snapshot includes body at birth, food/water, hidden effects, laws
    # and scheduled world events; these are identical paired opportunities.
    for field in ("world_sha256", "life_seed", "horizon", "execution_model"):
        if ma[field] != mb[field]:
            raise ValueError("unequal initial physical opportunities: " + field)
    if ma["world"] != mb["world"] or ma["source"]["sha256"] != mb["source"]["sha256"]:
        raise ValueError("unequal world contents or engine source")
    delta = {ch: round(a["cognitive_accounting"]["totals"][ch]["paid"] -
                       b["cognitive_accounting"]["totals"][ch]["paid"], 9)
             for ch in ("energy", "vigilance")}
    return {
        "schema": SCHEMA, "equal_initial_opportunity": True,
        "same_nominal_physics": True,
        "world_sha256": ma["world_sha256"],
        "source_sha256": ma["source"]["sha256"],
        "life_seed": ma["life_seed"], "horizon": ma["horizon"],
        "terminal_a": a["terminal"], "terminal_b": b["terminal"],
        "steps_a": a["steps_lived"], "steps_b": b["steps_lived"],
        "paid_cognitive_difference_a_minus_b": delta,
        "equal_realized_cognition": all(abs(d) <= TOL for d in delta.values()),
        "interpretation": "equal_opportunity_not_equal_realized_spending",
        "cost_matched_probe_ceiling": False,
    }


def audit_probe_exact_work(spec, individual: dict, ticks: list, horizon: int) -> dict:
    """A strict falsifier for claims of exact full-horizon probe cost matching.

    This does not prove optimality or equivalent information. The observer
    inspects actual probe receipts, not just an average tariff or advertised
    payment. Full match requires equal starting resources, full individually
    survived horizon, complete probe execution, no skipped/postmortem bills and
    the exact same four-counter decision/learning work vector on every tick.
    """
    _settled_life(individual, require_trace=True)
    if type(horizon) is not int or horizon != individual["horizon"]:
        raise ValueError("different advertised horizons")
    if digest(world_snapshot(spec)) != individual["manifest"]["world_sha256"]:
        raise ValueError("different world or initial reserves")
    if ticks and tuple(ticks[0]["before"]) != tuple(spec.body):
        raise ValueError("probe did not start with identical physical reserves")
    if len(ticks) > horizon:
        raise ValueError("probe fabricated ticks after the horizon")
    paid = matched = 0
    rows = individual["trace"]
    for i, tick in enumerate(ticks):
        if tick["t"] != i + 1:
            raise ValueError("probe ticks must be consecutive")
        if tick.get("dead") and i + 1 != len(ticks):
            raise ValueError("postmortem probe ticks")
        if tick.get("dead") and any(
                getattr(tick["paid_learning"], key) for key in WORK_KEYS):
            raise ValueError("postmortem probe learning")
        if tick["status"] == "MATCHED":
            paid += 1
        if i < len(rows):
            phases = rows[i]["funding_phases"]
            expected = (CognitiveWork(**phases["decision"]["work"]),
                        CognitiveWork(**phases["learning"]["work"]))
            observed = (tick["paid_decision"], tick["paid_learning"])
            if tick["status"] == "MATCHED" and expected == observed:
                matched += 1
    full = (individual["terminal"] == "censored" and
            len(ticks) == horizon == individual["steps_lived"] and
            matched == paid == horizon and
            not (ticks and ticks[-1].get("dead")))
    return {
        "schema": "i3-p2-probe-exact-cost-audit-v1",
        "full_horizon_cost_match": full,
        "matched_ticks": matched, "compared_ticks": len(ticks),
        "horizon": horizon,
        "meaning": ("exact_work_receipts_only_not_information_equivalence" if full
                    else "NOT_COST_MATCHED"),
    }
