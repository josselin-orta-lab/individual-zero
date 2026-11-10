"""Observer-only first differing prepaid replay on a REAL learned Mind state.

This is a laboratory counterfactual *learning update* on two detached copies
at the same pre-replay state and count. It neither constructs a second World
nor mutates the live Mind/World or its private randomness. Outputs cannot
enter Action Competition. No survival or causal mediation conclusion.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from math import fsum, isfinite
import json

from i3.modules.stage2_replay_content_selection import random_content_indices

SCHEMA = "i3-stage2.1-realstate-first-content-fork/v1"


def _hash(obj):
    return sha256(json.dumps(obj, sort_keys=True, separators=(",", ":"),
                             allow_nan=False).encode("utf-8")).hexdigest()


def _run_td_copy(source, indices):
    clone = deepcopy(source)
    before = [row[:] for row in clone.values]
    for index in indices:
        _, b0, b1, dead = clone.buffer[index]
        err = clone._td(b0, b1, dead)
        clone.buffer[index] = (abs(err), b0, b1, dead)
    return {
        "post_values_sha256": _hash(clone.values),
        "post_buffer_sha256": _hash(list(clone.buffer)),
        "value_update_l1": fsum(
            abs(clone.values[k][j] - before[k][j])
            for k in range(len(before))
            for j in range(len(before[k]))),
        "values": clone.values,
    }


class RealStateContentForkObserver:
    def __init__(self, mind):
        if mind.replay_gate_mode != "gate_random_content":
            raise PermissionError(
                "first causal-content probe requires genuine random-content arm")
        self.mind = mind
        self.replay_opportunities_seen = 0
        self.differing_replay_opportunities_seen = 0
        self.first_fork = None

    def replay(self, selected, ranked, priorities):
        """Called once BEFORE actual replay TD by the existing observer hook."""
        count = len(selected)
        if count <= 0:
            return None
        self.replay_opportunities_seen += 1
        baseline = tuple(ranked[:count])
        alternative = random_content_indices(
            eligible=len(ranked),
            count=count,
            life_seed=self.mind._random_life_seed,
            sleep_ordinal=self.mind.content_sleep_ordinal)
        if tuple(selected) != alternative:
            raise RuntimeError("live content choice differs from independent HMAC")
        if set(alternative) == set(baseline):
            return None
        self.differing_replay_opportunities_seen += 1
        if self.first_fork is not None:
            return None
        # Snapshot is AFTER the physically paid base update but BEFORE both
        # optional prepaid replay TD updates. The two clones start identically.
        source = deepcopy(self.mind)
        before_digest = _hash({
            "values":source.values,
            "buffer":list(source.buffer),
            "effects":repr(source.effects.stats),
            "personal_history":repr(source.hist),
            "mind_rng":repr(source.rng.getstate()),
            "decision_rng":repr(source._budget_rng.getstate()),
        })
        p = _run_td_copy(source, baseline)
        r = _run_td_copy(source, alternative)
        delta = fsum(
            abs(p["values"][k][j] - r["values"][k][j])
            for k in range(len(p["values"]))
            for j in range(len(p["values"][k])))
        if not isfinite(delta):
            raise RuntimeError("nonfinite realstate fork learning difference")
        self.first_fork = {
            "schema": SCHEMA,
            "lived_sleep_ordinal":self.mind.content_sleep_ordinal,
            "prepaid_replays_in_each_detached_arm":count,
            "identical_pre_replay_learned_state_sha256":before_digest,
            "priority_memory_indices":list(baseline),
            "random_memory_indices":list(alternative),
            "priority_post_values_sha256":p["post_values_sha256"],
            "random_post_values_sha256":r["post_values_sha256"],
            "priority_post_buffer_sha256":p["post_buffer_sha256"],
            "random_post_buffer_sha256":r["post_buffer_sha256"],
            "l1_value_difference_between_detached_updates":delta,
            "priority_l1_update":p["value_update_l1"],
            "random_l1_update":r["value_update_l1"],
            "actual_live_replay_count_unchanged":True,
            "world_or_life_clone_created":False,
            "observer_physical_debit":False,
            "biological_survival_claim":False,
        }
        return None

    def report(self):
        return {
            "schema":SCHEMA,
            "status":"FIRST_DIFFERING_REPLAY_CAPTURED"
                     if self.first_fork is not None
                     else "NO_DIFFERING_FUNDED_REPLAY_OBSERVED",
            "prepaid_replay_opportunities_seen":self.replay_opportunities_seen,
            "differing_replay_opportunities_seen":
                self.differing_replay_opportunities_seen,
            "first_fork":self.first_fork,
            "read_only_detached_learning_only":True,
            "no_world_births_from_observer":True,
            "scientific_verdict":"NOT_ISSUED",
        }
