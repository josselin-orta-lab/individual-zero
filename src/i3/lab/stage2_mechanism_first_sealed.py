"""Read-only sealed-original adapter for the *alternative* Stage-2.1 G0 v3.

This adapter does NOT open a World or dispatch a Mind. It accepts only the
proposed 720 paired G0 lives and a distinct v3 source lock, then invokes
the descriptive mechanism-first calculator after all originals are verified.
The external source and World authority remain unverified.
"""
from __future__ import annotations

from collections.abc import Mapping
from math import fsum

from . import stage0_design as F0
from . import stage2_mechanism_first_design as M
from . import stage2_sealed_selection_bridge as SEALED

SCHEMA = "i3-stage2-1-mechanism-first-sealed-original-readout/v1"
LOCK_SCHEMA = "i3-stage2-1-mechanism-first-sealed-lock/v1"
STATUS = "MATCHES_CALLER_PINS_ONLY_NO_SCIENTIFIC_VERDICT"
IDENTITY_KEYS = frozenset((
    "cohort", "population", "family", "world_index", "world_seed",
    "genome_seed", "life_seed", "arm",
))
POLICIES = {
    "FIXED_G0": "reference",
    "GATE_G0": "p13_replay_gate_v1",
    "RANDOM_G0": "p13_replay_gate_random_equal_mean_v1",
}


def _random_funding(life: Mapping, sleep: int, replay_count: int) -> None:
    gate = life.get("replay_gate")
    schedule = gate.get("random_schedule") if isinstance(gate, Mapping) else None
    if not isinstance(schedule, Mapping):
        raise ValueError("RANDOM original missing paid replay schedule")
    fields = ("draws_funded", "lived_sleep_ordinals",
              "nominal_replays_scheduled", "eligible_replays_scheduled",
              "actual_replays_paid", "mean_numerator", "mean_denominator")
    if any(type(schedule.get(f)) is not int for f in fields):
        raise ValueError("RANDOM original has malformed integer schedule")
    draws = schedule["draws_funded"]
    lived_ordinals = schedule["lived_sleep_ordinals"]
    nominal = schedule["nominal_replays_scheduled"]
    eligible = schedule["eligible_replays_scheduled"]
    paid = schedule["actual_replays_paid"]
    if (schedule.get("policy") != "i3-stage2-1-random-equal-mean-v1" or
            schedule["mean_numerator"] != 5532 or
            schedule["mean_denominator"] != 867 or
            not 0 <= draws <= lived_ordinals <= sleep or
            not 6 * draws <= nominal <= 7 * draws or
            not 0 <= paid <= eligible <= nominal or
            paid != replay_count):
        raise ValueError("RANDOM funded, nominal, eligible and paid replay mismatch")


def _exposure_row(arm, life, sleep, ca):
    """Diagnostics of physical exposure, not a causal parity guarantee."""
    replays = ca["replays_executed"]
    if type(replays) is not int or replays < 0:
        raise ValueError("invalid physically executed replay count")
    if arm == "FIXED_G0":
        return {
            "sleep_actions": sleep, "funded_gate_sleep_steps": 0,
            "decisions_scored": 0, "decisions_audited": 0,
            "audited_relevant": 0, "replays_paid": replays,
            "random_funded_draws": 0, "random_nominal": 0,
            "random_eligible": 0, "actual_lived_steps": life["steps_lived"],
        }
    gate = life.get("replay_gate")
    if not isinstance(gate, Mapping):
        raise ValueError("gate mechanism receipt missing")
    keys = ("sleep_steps_seen_by_gate", "decisions_total",
            "audited_decisions", "relevant_decisions")
    if any(type(gate.get(k)) is not int for k in keys):
        raise ValueError("invalid gate exposure counters")
    gate_sleep = gate["sleep_steps_seen_by_gate"]
    decisions = gate["decisions_total"]
    audited = gate["audited_decisions"]
    relevant = gate["relevant_decisions"]
    if (not 0 <= gate_sleep <= sleep or
            not 0 <= relevant <= audited <= decisions <= life["steps_lived"]):
        raise ValueError("impossible funded gate or decision exposure")
    if arm == "RANDOM_G0":
        schedule = gate["random_schedule"]
        if schedule["draws_funded"] > gate_sleep:
            raise ValueError("random draws exceed funded gate sleep steps")
        draws = schedule["draws_funded"]
        nominal = schedule["nominal_replays_scheduled"]
        eligible = schedule["eligible_replays_scheduled"]
    else:
        draws = nominal = eligible = 0
    return {
        "sleep_actions": sleep, "funded_gate_sleep_steps": gate_sleep,
        "decisions_scored": decisions, "decisions_audited": audited,
        "audited_relevant": relevant, "replays_paid": replays,
        "random_funded_draws": draws, "random_nominal": nominal,
        "random_eligible": eligible, "actual_lived_steps": life["steps_lived"],
    }


def _mechanism_exposure_summary(exposures):
    """Finite-panel descriptive provenance counts; never a parity pass."""
    measures = (
        "sleep_actions", "funded_gate_sleep_steps", "decisions_scored",
        "decisions_audited", "audited_relevant", "replays_paid",
        "random_funded_draws", "random_nominal", "random_eligible",
        "actual_lived_steps",
    )
    if not exposures:
        raise ValueError("no mechanism exposures")
    def summarize(records):
        n = len(records)
        totals = {field: sum(r[field] for r in records) for field in measures}
        return {
            "assigned_lives": n,
            "totals": totals,
            "per_assigned_life": {k: totals[k] / n for k in measures},
            "replays_per_lived_step": (
                totals["replays_paid"] / totals["actual_lived_steps"]),
        }
    summaries = {
        arm: summarize([row for a, _, _, row in exposures if a == arm])
        for arm in M.ARMS
    }
    for arm in M.ARMS:
        if summaries[arm]["assigned_lives"] != 240:
            raise ValueError("invalid per-arm exposure denominator")
    families = {
        family: {
            arm: summarize([row for a, f, _, row in exposures
                            if a == arm and f == family])
            for arm in M.ARMS
        }
        for family in F0.FAMILIES
    }
    populations = {
        p: {
            arm: summarize([row for a, _, pop, row in exposures
                            if a == arm and pop == p])
            for arm in M.ARMS
        }
        for p in range(F0.POPULATIONS)
    }
    random_paid = summaries["RANDOM_G0"]["totals"]["replays_paid"]
    gate_paid = summaries["GATE_G0"]["totals"]["replays_paid"]
    random_scheduled = summaries["RANDOM_G0"]["totals"]["random_nominal"]
    random_eligible = summaries["RANDOM_G0"]["totals"]["random_eligible"]
    return {
        "status": "DESCRIPTIVE_ONLY_NO_POLICY_SUPERIORITY_OR_PARITY_CLAIM",
        "assigned_lives": len(exposures),
        "by_arm": summaries,
        "by_family": families,
        "by_population": populations,
        "gate_minus_random_paid_replays_per_assigned_life": (
            (gate_paid - random_paid) / 240),
        "random_scheduled_minus_paid_replays": random_scheduled - random_paid,
        "random_eligible_minus_paid_replays": random_eligible - random_paid,
        "random_nominal_mean_is_not_actual_paid_parity": True,
        "realized_replay_parity_proven": False,
        "scientific_verdict": "NOT_ISSUED",
        "causal_mechanism_advantage": "NOT_ESTABLISHED",
    }


def from_sealed_originals(archive_dir, plan_path, expected_pins,
                          occupied_world_seeds=()) -> dict:
    """Consume no scientific authorization, return NO_VERDICT description only.

    This is a Phase-R *observer*, never an execution plan. Even when all
    720 archives pass, caller pins and its self-seal cannot independently
    attest the source, actual WorldSpec or pre-exposure owner approval.
    """
    expected = M.expected_cells(occupied_world_seeds)
    originals = SEALED._sealed(archive_dir, plan_path, expected_pins,
                               "validation", len(expected),
                               lock_schema=LOCK_SCHEMA)
    worlds = {row["index"]: row for row in F0.world_rows("validation")}
    rows = []
    exposures = []
    seen = set()
    genome_digests = {}
    world_digests = {}

    for identity, life in originals:
        if not isinstance(identity, Mapping) or set(identity) != IDENTITY_KEYS:
            raise ValueError("invalid mechanism-first original identity")
        p, index, seed, arm = (identity[k] for k in (
            "population", "world_index", "genome_seed", "arm"))
        if (any(type(x) is not int for x in (p, index, seed)) or
                type(arm) is not str or arm not in POLICIES):
            raise ValueError("invalid v3 population/world/founder/arm")
        key = (p, index, seed, arm)
        if key not in expected or key in seen:
            raise ValueError("duplicate, foreign or post-selected G0 cell")
        world = worlds[index]
        SEALED._identity(identity, world, IDENTITY_KEYS, "validation")
        sleep, ca = SEALED._actual_life(
            identity, life, POLICIES[arm], expected_pins,
            genome_digests, world_digests)
        gate = life.get("replay_gate")
        if arm == "RANDOM_G0":
            _random_funding(life, sleep, ca["replays_executed"])
        elif isinstance(gate, Mapping) and "random_schedule" in gate:
            raise ValueError("non-RANDOM original claims random schedule")
        exposures.append((arm, identity["family"], p,
                          _exposure_row(arm, life, sleep, ca)))
        seen.add(key)
        rows.append({
            "arm": arm, "population": p,
            "family": identity["family"], "world_index": index,
            "world_seed": identity["world_seed"], "genome_seed": seed,
            "life_seed": identity["life_seed"], "terminal": life["terminal"],
            "steps_lived": life["steps_lived"],
            "energy_paid": ca["totals"]["energy"]["paid"],
            "vigilance_paid": ca["totals"]["vigilance"]["paid"],
            "inactive_steps": ca["inactive_steps"],
        })
    if seen != set(expected):
        raise ValueError("missing mechanism-first original cells")
    readout = M.descriptive_readout(rows, occupied_world_seeds)
    return {
        "schema": SCHEMA, "status": STATUS,
        "originals_checked": len(originals),
        "paired_blocks": readout["paired_blocks"],
        "source_and_world_authority": "CALLER_PINS_ONLY_NOT_INDEPENDENTLY_ATTESTED",
        "owner_approval": "NOT_INFERRED",
        "worlds_opened_by_adapter": False,
        "population_independence": "NOT_ESTABLISHED",
        "survival_noninferiority": "NOT_TESTED",
        "scientific_verdict": "NOT_ISSUED",
        "readout": readout,
        "mechanism_exposure": _mechanism_exposure_summary(exposures),
    }
