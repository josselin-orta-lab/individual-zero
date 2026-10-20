"""#317 personally experienced place relevance, matched 18-life research cohort.

Identical paid spatial recall in BOTH separate mortal arms; only the
experimental Stage8 evidence interprets an admitted positive personal boire
follow-up at the same site, a current observed thirst need, confidence and
route uncertainty. No type oracle, movement water prediction, forced motor,
changed physiological threshold, changed Q/TD or I0. No M11 cold promotion.
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

PRESETS = ("oasis", "foraging", "memory-corridor")
SEEDS = (15121, 15173, 15313)
HORIZON = 300
ARMS = ("guard_control", "guard_experiential")
MAX_LIVED_ADVISORY = 0.10
MAX_ROUTE_SEARCH_CANDIDATES = 32
CRITICAL_WATER_FOR_ASSOCIATION = 30.0
MAX_ASSOCIATIVE_RELEVANCE = 0.45


def factors(arm):
    if arm not in ARMS:
        raise ValueError("only preregistered first-person place interventions allowed")
    return (True, arm == "guard_experiential")


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


def lived_place_relevance(
    *, experienced_water_gain, current_observed_water, memory_confidence,
    witnessed_hops,
):
    """Past personally observed water relief, discounted for need and doubt.

    An association with a SITE, not a promise that an upcoming movement or
    future drink will change the body. No inferred resource-type effect.
    """
    nums = (experienced_water_gain, current_observed_water, memory_confidence)
    if (any(type(v) not in (int,float) or not isfinite(v) for v in nums)
        or not 0 < experienced_water_gain <= 100
        or not 0 <= current_observed_water <= 100
        or not 0 < memory_confidence <= 1
        or type(witnessed_hops) is not int
        or not 1 <= witnessed_hops <= 8):
        raise ValueError("invalid personal water association")
    if current_observed_water > CRITICAL_WATER_FOR_ASSOCIATION:
        return 0.0
    deficit = 100.0-current_observed_water
    fraction = min(experienced_water_gain, deficit) / deficit
    distance_uncertainty = 1.0/(1.0+0.1*(witnessed_hops-1))
    return min(
        MAX_ASSOCIATIVE_RELEVANCE, fraction*memory_confidence*distance_uncertainty,
    )


class FirstPersonPlaceValueAdapter:
    """Read the current frozen Perception, never world oracle or new Q/TD."""

    def __init__(self, underlying, actor, counters, *, enabled):
        if type(enabled) is not bool:
            raise ValueError("invalid treatment")
        self._underlying=underlying
        self._actor=actor
        self._counters=counters
        self._enabled=enabled

    def __getattr__(self,name):
        if name.startswith("__"):
            raise AttributeError(name)
        return getattr(self._underlying,name)

    def evaluate(self, *, proposal, **kwargs):
        from i1.modules.competition import OptionEvidenceInput
        baseline=self._underlying.evaluate(proposal=proposal, **kwargs)
        option=proposal.option
        if (not self._enabled or option.provenance!="memory"
            or option.motive_ref.type!="place_memory"
            or option.goal_ref is not None
            or baseline.evidence is None
            or baseline.evaluation.status!="evaluated"
            or not _drink_goal_active(self._actor)):
            return baseline
        geo=self._actor.exploration.geographic
        target=None if geo is None else geo.place_for(option)
        if (target is None or target.source_t_monde!=kwargs["t_monde"]
            or not 0 < target.confidence <= 1
            or target.origin==target.observed_position
            or not 2 <= len(target.visited_path) <= 9):
            return baseline
        # Stage11 freezes this single actual bodily Perception BEFORE Phase1.
        seen=getattr(self._actor,"_stage11_prospective_capture",None)
        if (type(seen) is not tuple or len(seen)!=3
            or seen[0]!=kwargs["t_monde"] or seen[1]!=target.origin
            or type(seen[2]) not in (int,float) or not isfinite(seen[2])
            or not 0 <= seen[2] <= 100):
            raise RuntimeError("missing frozen first-person bodily observation")
        site=tuple(target.observed_position)
        actual_gain=positive_sites_from_lived_owner(self._actor).get(site)
        if actual_gain is None:
            return baseline
        relevance=lived_place_relevance(
            experienced_water_gain=actual_gain,
            current_observed_water=seen[2],
            memory_confidence=target.confidence,
            witnessed_hops=len(target.visited_path)-1,
        )
        if relevance==0:
            return baseline
        signal=f"i1:personally-relieved-water:{site[0]}:{site[1]}"
        if signal in baseline.evaluation.signal_ids:
            raise RuntimeError("duplicated first-person evidence")
        scored=OptionEvidenceInput(
            evaluation=replace(
                baseline.evaluation,
                signal_ids=tuple(baseline.evaluation.signal_ids)+(signal,),
                producers=tuple(dict.fromkeys(
                    tuple(baseline.evaluation.producers)
                    +("i1:conditional-lived-site-relevance",))),
            ),
            evidence=max(-1.0,min(1.0,baseline.evidence+relevance)),
        )
        scored.validate()
        self._counters["unattested_relevance_evaluations"]+=1
        return scored


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
    report = {
        "schema": "i1-317-experiential-place-relevance-mortal/v1",
        "status": "NOT_STARTED",
        "source_sha": source_sha, "preset": preset, "seed": seed,
        "horizon": HORIZON, "preset_sha256": preset_sha,
        "preregistered_arms": list(ARMS),
        "both_arms_same_guarded_retrieval": True,
        "goal_conditioned_relevance_treatment_only": True,
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
        with TemporaryDirectory(prefix="i1-317-experiential-relevance-") as temporary:
            generated = Path(temporary)/"generated"
            generate(generated)
            sys.path.insert(0,str(generated))
            from i1lab.i1_birth import birth_i1
            from i1.modules import spatial_memory
            params, _ = _birth_parameters(source)
            report["physics_digest"] = params["world_config"].digest()
            natural_find = spatial_memory.find_spatial_returns
            results = {}
            for arm in ARMS:
                do_rank, do_value = factors(arm)
                directory = out/arm
                directory.mkdir()
                wal = directory/"life-01.wal"
                born = []
                counters = Counter()
                def make_actor(**kwargs):
                    actor = birth_i1(**kwargs)
                    # Same observer on BOTH arms, same ordinary Stage8 charge.
                    actor.stage8_option_evaluator = FirstPersonPlaceValueAdapter(
                        actor.stage8_option_evaluator, actor, counters,
                        enabled=do_value,
                    )
                    born.append(actor)
                    return actor
                def owned_routes(**kwargs):
                    ordinary = natural_find(**kwargs)
                    if not do_rank or not born:
                        raise RuntimeError("matched recall intervention not installed")
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
                            life_id=f"i1:preset:{preset}:{seed}:0",
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
                row["positive_lived_source_sites"] = len(
                    positive_sites_from_lived_owner(actor))
                row["option_ranking_adjusted"] = do_rank
                row["option_value_advisory_adjusted"] = do_value
                row["wal_sha256"] = sha256(wal.read_bytes()).hexdigest()
                row["wal_relative_path"] = str(Path(arm)/wal.name)
                results[arm] = row
            report["arms"] = results
            report["status"] = "COMPLETE_PAIRED_PHYSICAL_DIAGNOSTIC"
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
