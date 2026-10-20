"""#318 prospective 32 independent mortal births, four factorial local-Q arms.

For each preset and new seed, produce FOUR independent sealed WALs with the
same physical rules, TD owner, sleep/consolidation, and paid place retrieval.
The only manipulated factor is whether learned Q can inform (a) ranking the
one local candidate and (b) its evidence at Competition. No value oracle,
primitive-specific suppression, forced motor, rollback, replay or I0 edits.
"""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import replace
from hashlib import sha256
import json
from math import isfinite
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from run_i1_317_two_process_sleep import summarize_life

PRESETS = ("memory-corridor", "water-isolated-corridor")
SEEDS = (24103, 24223, 24359, 24481)
HORIZON = 300
ARMS = ("local_q_neutral", "local_q_rank_only", "local_q_evidence_only", "local_q_learned")
MAX_LIVED_ADVISORY = 0.10
MAX_ROUTE_SEARCH_CANDIDATES = 32
CRITICAL_WATER_FOR_ASSOCIATION = 30.0
MAX_ASSOCIATIVE_RELEVANCE = 0.45


def factors(arm):
    if arm not in ARMS:
        raise ValueError("only preregistered four-arm Q-factorial births allowed")
    mode = arm.removeprefix("local_q_")
    # Both arms of each independent 2x2 axis have identical native Q/TD
    # learning, Stage11 lived-place ranking, sleep and motor permissions.
    return True, mode


def positive_sites_from_lived_owner(actor):
    """Only the actor's personally admitted follow-up, never WorldBody truth.

    A personally positive water delta supports a LOCAL ASSOCIATION. It does
    not prove a universal substance, permanent water availability, absence
    of risk or the usefulness of distant entities with the same type.
    """
    learner = actor._water_learner
    if not learner.enabled:
        return {}
    positive = {}
    for item in learner.examples:
        loc = item["source_position"]
        delta = item["delta_water"]
        if (type(loc) is not list or len(loc) != 2
            or any(type(v) is not int for v in loc)
            or type(delta) not in (float, int) or not isfinite(delta)
            or delta <= 0):
            raise RuntimeError("water owner leaked malformed lived evidence")
        key = tuple(loc)
        positive[key] = max(positive.get(key, 0.0), float(delta))
    return positive


def rank_by_lived_sites(candidates, supported_sites, capacity):
    """Stable memory ordering; only an already-lived site earns a tie break."""
    if (type(capacity) is not int or not 1 <= capacity <= 32
        or not isinstance(supported_sites, dict)
        or any(not isinstance(key, tuple) or len(key) != 2
               or any(type(x) is not int for x in key)
               or type(value) not in (int, float) or not isfinite(value)
               or value <= 0 for key, value in supported_sites.items())):
        raise ValueError("invalid experimental positive-site rank inputs")
    values = tuple(candidates)
    return tuple(value for _, value in sorted(enumerate(values), key=lambda item: (
        0 if item[1].observed_position in supported_sites else 1, item[0],
    )))[:capacity]


def expanded_search_may_change_candidates(
    ordinary, learned_sites, origin, cap,
):
    """Proof-obligation gate BEFORE additional paid route search.

    The normal, already-paid Stage11 search is a stable top-cap prefix of
    the exact same complete bounded survey search. If its prefix is not
    saturated, no new candidate exists. If every personally beneficial
    nonlocal place already appears in the prefix AND promoting those
    currently present would not change ordering, another scan cannot
    change the top-cap prefix either. The test learns no hidden route.
    """
    current = tuple(ordinary)
    if (not isinstance(learned_sites, dict) or not isinstance(origin, tuple)
        or len(origin) != 2 or any(type(v) is not int for v in origin)
        or type(cap) is not int or not 1 <= cap <= 32
        or len(current) > cap):
        raise ValueError("invalid already-paid place search context")
    if not learned_sites:
        return False
    # Also strictly validate the evidence itself, even for no-op decisions.
    reordered = rank_by_lived_sites(current, learned_sites, cap)
    if reordered != current:
        return True
    if len(current) < cap:
        return False
    included = {t.observed_position for t in current}
    return any(site != origin and site not in included for site in learned_sites)


def _drink_goal_active(actor):
    goal = actor.goal_manager.active_goal
    return goal is not None and goal.goal_type == "drink"



def _run_births(preset, seed, out):
    if (preset not in PRESETS or type(seed) is not int or seed not in SEEDS):
        raise ValueError("birth outside pre-registered matched cohort")
    out = out.resolve()
    if out.exists():
        raise FileExistsError("existing mortal WAL directory cannot be replayed")
    from run_i1_world_preset import _birth_parameters, _wal_life, load_preset
    from build_i1_fork import generate
    source_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
        capture_output=True, check=True,
    ).stdout.strip()
    source, preset_sha = load_preset(preset)
    if preset == 'water-isolated-corridor':
        water = {tuple(p) for p in source['layout']['water_sources']}
        berries = {tuple(r['cell']) for r in source['layout']['resources'] if r['kind'] in ('berry_a', 'berry_b')}
        if (water & berries or water != {(8,8)} or berries != {(10,8)}
            or tuple(source['spawn']) != (8,8)):
            raise RuntimeError('held-out water/berry separation failed')

    report = {
        "schema": "i1-318-matched-temperament-Q-factorial-mortal/v1",
        "status": "NOT_STARTED",
        "source_sha": source_sha, "preset": preset, "seed": seed,
        "horizon": HORIZON, "preset_sha256": preset_sha,
        "preregistered_arms": list(ARMS),
        "all_arms_same_guarded_retrieval": True,
        "goal_conditioned_relevance_treatment_only": False,
        "prior_source_algorithm_sha": "43e1fa82e8034c20708d9edf380b41a5bf30502b",
        "heldout_validation_not_promotion": True,
        "native_experiential_stage8_opt_in": False,
        "only_critical_alert_sleep_registration_gate_changed": False,
        "only_local_Q_exposure_changed": True,
        "factorial_design": "rank x competition_evidence, independently blinded",
        "matched_twin_birth_temperament": True,
        "temperament_source": f"i1:research-twin:{preset}:{seed}",
        "all_lives_distinct_and_mortal": True,
        "fixed_local_opportunity_contract": "i1-local-interaction-goal-independent-v2",
        "excluded_prebirth_constructor_failure_seeds": [17123,17257,17383,17491],
        "water_berry_colocation_ablated_in_isolated_corridor": True,
        "relevance_maximum": MAX_ASSOCIATIVE_RELEVANCE,
        "relevance_water_gate": CRITICAL_WATER_FOR_ASSOCIATION,
        "learned_site_requires_personally_applied_boire_and_followup": True,
        "same_world_physics_needs_td_competition_action_control": True,
        "no_type_based_resource_utility": True,
        "no_motor_forcing_or_new_vital_reflex": True,
        "no_cold_recovery_claim": True,
        "all_prior_seeds_excluded": True,
        "no_forced_motor_or_movement_water_forecast": True,
        "no_coma_implemented": True,
        "scientific_verdict": "NO-GO",
    }
    out.mkdir(parents=True, exist_ok=False)
    try:
        with TemporaryDirectory(prefix="i1-318-q-factorial-twin-") as temporary:
            generated = Path(temporary)/"generated"
            generate(generated)
            sys.path.insert(0,str(generated))
            from i1lab.i1_natural_runtime import I1Runtime
            from i1.modules import spatial_memory
            params, _ = _birth_parameters(source)
            report["physics_digest"] = params["world_config"].digest()
            natural_find = spatial_memory.find_spatial_returns
            results = {}
            for arm in ARMS:
                do_rank, q_mode = factors(arm)
                directory = out/arm
                directory.mkdir()
                wal = directory/"life-01.wal"
                born = []
                counters = Counter()
                def make_actor(**kwargs):
                    # Native first-person relevance integrated before birth.
                    # Both arms use the SAME guarded place retrieval research
                    # intervention; only Stage8's native opt-in differs.
                    actor = I1Runtime(
                        birth_life_id=kwargs.pop("life_id"),
                        autonomous_mortal=True,
                        i1_experienced_place_enabled=False,
                        i1_critical_alert_reentry_guard=False,
                        i1_cross_goal_local_opportunities=True,
                        i1_local_q_exposure=q_mode,
                        i1_research_temperament_source_id=f"i1:research-twin:{preset}:{seed}",
                        diagnostic_sample_cost_uc=1,
                        module_occupancy_cost_uc=1,
                        **kwargs,
                    )
                    born.append(actor)
                    return actor
                def owned_routes(**kwargs):
                    ordinary = natural_find(**kwargs)
                    if not do_rank or not born:
                        raise RuntimeError("factorial identical paid recall intervention not installed")
                    actor = born[0]
                    if not _drink_goal_active(actor):
                        return ordinary
                    positive = positive_sites_from_lived_owner(actor)
                    if not positive:
                        return ordinary
                    cap = kwargs.get("max_candidates", MAX_ROUTE_SEARCH_CANDIDATES)
                    if not (1 <= cap <= MAX_ROUTE_SEARCH_CANDIDATES):
                        raise ValueError("invalid route capacity")
                    if not expanded_search_may_change_candidates(
                        ordinary, positive, kwargs["origin"], cap
                    ):
                        counters["avoided_provably_noop_expansions"] += 1
                        return ordinary
                    counters["potentially_useful_expansions"] += 1
                    # Only now is the second route search actually needed.
                    # It still requires its own real Planning UC receipt.
                    if not actor._charge(
                        module="planning", operation="geographic_route_search"
                    ):
                        counters["rank_budget_denied"] += 1
                        return ordinary
                    expanded = natural_find(**{
                        **kwargs, "max_candidates": MAX_ROUTE_SEARCH_CANDIDATES})
                    reranked = rank_by_lived_sites(expanded, positive, cap)
                    if reranked != ordinary:
                        counters["rank_changes"] += 1
                    return reranked
                try:
                    with patch.object(spatial_memory,"find_spatial_returns",
                                      owned_routes):
                        life = _wal_life(
                            birth=make_actor, params=params,
                            life_id=f"i1:q-factorial-twin:{preset}:{seed}:{arm}:0",
                            path=wal, steps=HORIZON)
                except Exception as error:
                    report.setdefault("technically_halted_births",[]).append({
                        "arm": arm,
                        "reason": f"{type(error).__name__}: {error}",
                        "wal_relative_path": str(Path(arm)/wal.name),
                        "wal_sha256": sha256(wal.read_bytes()).hexdigest()
                            if wal.is_file() else None,
                        "no_retry_or_rollback": True,
                    })
                    raise
                if len(born) != 1:
                    raise RuntimeError("nonunique embodied I1 actor")
                actor = born[0]
                # No config changes are permitted even in the research arms.
                from i1lab.i1_natural_sleep import (
                    FATIGUE_GAIN_PER_UC_FRACTION, CONSOLIDATION_WEIGHT,
                    FATIGUE_WEIGHT, NIGHT_WEIGHT,
                )
                sleep = actor._stage10_config.sleep
                if (sleep.fatigue_gain != FATIGUE_GAIN_PER_UC_FRACTION
                    or sleep.fatigue_weight != FATIGUE_WEIGHT
                    or sleep.consolidation_weight != CONSOLIDATION_WEIGHT
                    or sleep.night_weight != NIGHT_WEIGHT
                    or dict(actor._stage10_config.critical_body_thresholds)
                        != {"energy":10.0,"water":15.0,"food":10.0,"integrity":25.0}):
                    raise RuntimeError("research birth changed native sleep/wake config")
                from audit_i1_spatial_navigation_314 import audit as audit_wal
                custody = audit_wal(wal)
                if (custody["independent_hash_chain_verified"] is not True
                    or custody["journal_head"] != life["journal_head"]
                    or custody["journal_entries"] != life["durable_entries"]):
                    raise RuntimeError("original mortal journal authentication failed")
                with wal.open(encoding="utf-8") as stream:
                    events = [json.loads(line)["causal_event"] for line in stream]
                row = summarize_life(life, events, actor)
                row["research_counters_UNATTESTED"] = dict(counters)
                row["native_stage8_opt_in"] = False
                row["critical_alert_sleep_guard_opt_in"] = False
                row["cross_goal_local_opportunities_opt_in"] = True
                row["local_q_exposure"] = q_mode
                row["positive_lived_source_sites"] = len(
                    positive_sites_from_lived_owner(actor))
                row["option_ranking_adjusted"] = do_rank
                row["option_value_advisory_adjusted"] = False
                row["wal_sha256"] = sha256(wal.read_bytes()).hexdigest()
                row["wal_relative_path"] = str(Path(arm)/wal.name)
                results[arm] = row
            report["arms"] = results
            report["status"] = "COMPLETE_FACTORIAL_PHYSICAL_DIAGNOSTIC"
    except Exception as error:
        report["status"] = "TECHNICAL_FAILURE"
        report["error"] = f"{type(error).__name__}: {error}"
        raise
    finally:
        (out/"report.json").write_text(
            json.dumps(report,sort_keys=True,indent=2)+"\n",
            encoding="utf-8",
        )
    print(json.dumps({
        "status": report["status"], "world": preset, "seed": seed,
        "arms": {a:{k:r[k] for k in (
            "lifecycle", "lived_steps", "objects_consolidated",
            "accepted_cognitive_uc", "positive_lived_source_sites",
            "research_counters_UNATTESTED")} for a,r in results.items()},
        "scientific_verdict": "NO-GO",
    }, indent=2, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preset",required=True)
    parser.add_argument("--seed",required=True,type=int)
    parser.add_argument("--output-dir",required=True,type=Path)
    args = parser.parse_args()
    _run_births(args.preset,args.seed,args.output_dir)


if __name__ == "__main__":
    main()
