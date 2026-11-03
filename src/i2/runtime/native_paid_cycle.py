"""Bounded I2-native first-person -> paid choice -> committed body loop.

Uses the EXISTING v5 CognitiveCycleFixture transaction and SQLite file.
No second cognition, WorldBody, UC or motor owner. Distinct research genesis
does not migrate, run or relabel the earlier energy-only I2 experiment.
Neither this model nor its local cold audit is independent M11 custody.
"""
from __future__ import annotations

from dataclasses import replace
from math import isclose
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
from uuid import uuid4

from i2.modules.cognitive_cycle_fixture import (
    CognitiveCycleFixture, CommitAcknowledgmentLost,
)
from i2.modules.action_control_boundary import SafetyFinding
from i2.modules.chosen_outcome_study import (
    ChosenOutcomeValuationStudy, ObservedChosenResult, observed_chosen_scores,
    MAX_RECORDED_CHOICES,
)
from i2.modules.intention_continuity import FirstPersonCapture
from i2.modules.intention_ingress import ObservationClaim
from i2.modules.native_body_contract import Body, COSTS
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_consequence_bridge import admitted_consequence
from i2.modules.native_owner_support import (
    NativeCaptureReflex, _json, current_evidence, native_scores,
    saved_body, saved_traits,
)
from i2.modules.native_physiological_needs import assess_needs
from i2.modules.native_place_experience import (
    lived_place_outcomes, summarized_site_experience,
    current_need_site_relevance,
)
from i2.modules.native_spatial_world import (
    GRAPH, MOTIONS, offered_moves, destination, site_after,
    replay_site, local_evidence,
)
from i2.runtime.native_physiology_journal import (
    initialize_native_body, native_snapshot, commit_admitted_physics,
    audit_native_body, commit_unadmitted_tick, passive_body_tick, NO_ACTION,
)

PRIORS = {"boire": 1, "manger": 4, "dormir": 2, "attendre": 1, "collecter": 2, "boire_decouverte": 1,
          **{motion: 3 for motion in MOTIONS}}
HORIZON = 8
MAX_BORN_STEPS = 128
# Capture is a bounded projection, not a deletion of an individual's journal.
GENESIS_SCHEMA = "i2-native-paid-local-life-v18-spatial-water-refill-evidence-boundary"
MAX_NATIVE_CAPTURE_REFS = 64


class NativeRefusal(ValueError):
    pass


class _Observation:
    def __init__(self, life):
        self.life = life
        self.expected = None

    def verify(self, *, life_ref, claim, digest):
        return (life_ref == self.life and
                self.expected == digest == claim.digest())


class _Current:
    def __init__(self):
        self.ref = None

    def verify_current(self, *, life_ref, frame, advice):
        return frame.life_ref == life_ref and frame.capture_ref == self.ref


class _Safety:
    def __init__(self):
        self.reflex = None
        self.veto = False

    def check(self, *, life_ref, frame, candidate_ref, control_receipt_ref):
        reflex = self.reflex
        if (reflex is None or life_ref != reflex.claim.life_ref or
                frame.claim_digest != reflex.claim.digest() or
                frame.capture_ref != reflex.claim.capture.ref or
                not any(c.candidate_ref == candidate_ref
                        for c in frame.candidates)):
            raise NativeRefusal("native safety lacks fresh body-bound reflex")
        return SafetyFinding(
            life_ref, frame.frame_ref, frame.capture_ref,
            candidate_ref, control_receipt_ref, self.veto,
            reflex.evidence_ref)


class _Terminal:
    def verify_terminal(self, **kwargs):
        return False


class _NoEvaluation:
    def evaluate_batch(self, **kwargs):
        raise NativeRefusal("cold native audit may not evaluate an action")


class _HistorySource:
    def __init__(self, results):
        self.known = frozenset(results)

    def verify_chosen_result(self, *, result):
        return result in self.known


def innate_adjustment(values, body, traits):
    scores = native_scores(
        values, body, traits, collect="collecter",
        eat="manger", drink="boire")
    needs = assess_needs(body, traits)
    scores["dormir"] += round(8 * needs.pressures["energy"] +
                            4 * needs.pressures["integrity"])
    # An actually discovered and presently accessible water affordance
    # answers the SAME innate thirst as ordinary drinking. This supplies
    # no predicted payoff: the source was observed in a PREVIOUS commit,
    # and whether to use it remains a fully paid Competition decision.
    if "boire_decouverte" in scores:
        scores["boire_decouverte"] += round(8 * needs.pressures["water"])
    for motion in MOTIONS:
        if motion in scores:
            scores[motion] += round(2 * traits.exploration)
    return scores



# Declared evidence sufficiency: do not call one unsuccessful attempt impossible.
NONRESTORING_ATTEMPTS = 2
NONRESTORING_EVIDENCE = ":personal-nonrestoration"
RESOURCE_OUTCOME_EVIDENCE = ":experienced-target-outcome"
TIE_EXPLORATION_EVIDENCE = ":novel-under-lived-failure-tie"
SLEEP_EVIDENCE = ":sleep-consolidated"
PLACE_RETURN_EVIDENCE = ":personally-observed-reachable-place"
PURPOSE_HANDOFF_EVIDENCE = ":paid-purpose-carried-from-arrival"
MOVEMENT_CREDIT_EVIDENCE = ":movement-result-not-generalized-across-sites"

# The target is an ordinary innate action affordance, not a hidden prediction.
# Rest/wait can repair integrity when resources permit, but neither drinks
# calories nor promises a rescue from thirst or hunger.
DIRECT_RESTORATION_RESERVE = {
    "boire": "water", "manger": "food",
    "dormir": "integrity", "attendre": "integrity",
}
# Only actually consumed physical resources have an unambiguous target here.
# Do not treat the fatigue or integrity effects of sleep as a failed drink.
CONSUMED_RESOURCE_NEED = {
    "boire": "water", "boire_decouverte": "water", "manger": "food",
}


def personally_observed_resource_outcomes(*, previous, traits):
    """Count actual target-need successes/failures across this born life.

    This conservative association never infers a world change from time,
    never imputes unchosen outcomes, and cannot be reset by a single later
    success. Recompute from the SAME owner's bounded (<=128 tick) physical
    journal; the unrelated generic G2 chosen-outcome window remains 64.
    An action while its target need was fully satisfied contributes nothing.
    """
    if type(traits) is not BirthTemperament:
        raise NativeRefusal("native birth temperament required")
    counts = {action: [0, 0] for action in CONSUMED_RESOURCE_NEED}
    for row in previous:
        target = CONSUMED_RESOURCE_NEED.get(row[2])
        if target is None:
            continue
        before = saved_body(row[4])
        if assess_needs(before, traits).pressures[target] <= 0:
            continue
        after = saved_body(row[5])
        slot = 0 if getattr(after, target) > getattr(before, target) else 1
        counts[row[2]][slot] += 1
    return {action: tuple(values) for action, values in counts.items()}


def personally_nonrestoring_action(*, body, previous, action):
    """Past evidence of failure, independent of *current* availability.

    Current unavailability is not proof of permanent impossibility. But if a
    resource ran out AFTER two personally observed failures, those failures
    are not erased merely because that affordance disappeared. Only the
    owner-committed before/after states are accepted by the caller.
    """
    if type(body) is not Body or type(action) is not str or not action:
        raise NativeRefusal("native body and prior action required")
    # Physically meaningful affordance-to-reserve mapping. A drink is not a
    # failed meal just because hunger continues to grow during drinking.
    targeted_reserve = DIRECT_RESTORATION_RESERVE.get(action)
    if targeted_reserve is None or getattr(body, targeted_reserve) > 10:
        return False
    attempts = [r for r in previous if r[2] == action]
    if len(attempts) < NONRESTORING_ATTEMPTS:
        return False
    return all(
        getattr(saved_body(row[5]), targeted_reserve) <=
        getattr(saved_body(row[4]), targeted_reserve)
        for row in attempts[-NONRESTORING_ATTEMPTS:]
    )


def personally_nonrestoring_scores(
    scores, *, claim, body, traits, previous, learning,
):
    """Use persistent target-specific evidence before any critical reflex.

    Each lived restoration (+1) or nonrestoration (-1) changes the
    associative contribution. Past contradictions remain in the SAME
    SQLite journal: one success does not erase many failures, and time
    alone never gives a stale resource a bonus. These unit weights are
    exploratory score units, not a claim of calibrated natural learning.

    The distinct critical last-resort gate may still cap a repeatedly
    failing action at zero and does not authorize a motor act.
    """
    if type(learning) is not bool:
        raise NativeRefusal("native learning arm must be exact boolean")
    adjusted = dict(scores)
    if not learning:
        return adjusted, frozenset(), frozenset()
    baseline = innate_adjustment(PRIORS, body, traits)
    outcomes = personally_observed_resource_outcomes(
        previous=previous, traits=traits)
    associated = set()
    for action in claim.capture.accessible_semantics:
        if action not in adjusted or action not in outcomes:
            continue
        successes, failures = outcomes[action]
        if successes + failures:
            # Resource effectiveness is NOT the previous global-relief +5.
            # Evidence accumulates without any clock-driven forgiveness.
            adjusted[action] = baseline[action] + successes - failures
            associated.add(action)
    reflex = NativeCaptureReflex(claim, body, traits)
    discouraged = set()
    if reflex.state != "NO_PREEMPTION":
        for action in claim.capture.accessible_semantics:
            if action in adjusted and personally_nonrestoring_action(
                body=body, previous=previous, action=action
            ):
                adjusted[action] = min(0, adjusted[action])
                discouraged.add(action)
    return adjusted, frozenset(discouraged), frozenset(associated)


def native_evidence_tie_exploration(
    scores, *, claim, body, traits, previous, learning, enabled,
):
    """A born-locked, nonmotor experiment at a tied POSITIVE maximum.

    Use only committed personal failures, current bodily need, the birth
    exploration trait and whether each offered action was ever chosen.
    The *sole* untried candidate gains +1 against one previously sampled
    and predominantly ineffective consumption action at equal top rank.
    No clock freshness, hidden payoff, global novel-action reward or
    knowledge that the other resource will work. Regular paid Competition
    and fresh Action Control still decide and admit any physical action.
    """
    if type(enabled) is not bool or type(learning) is not bool:
        raise NativeRefusal("exact born tie experiment and learning flags required")
    adjusted = dict(scores)
    if not enabled or not learning or traits.exploration <= 0:
        return adjusted, frozenset()
    if NativeCaptureReflex(claim, body, traits).state != "NO_PREEMPTION":
        return adjusted, frozenset()
    offered = claim.capture.accessible_semantics
    if not offered:
        return adjusted, frozenset()
    top = max((adjusted[a] for a in offered if a in adjusted), default=0)
    if not 0 < top < 1024:
        return adjusted, frozenset()
    tied = [a for a in offered if adjusted.get(a) == top]
    if len(tied) < 2:
        return adjusted, frozenset()
    chosen_before = {r[2] for r in previous if r[2] != NO_ACTION}
    unseen = [a for a in tied if a not in chosen_before]
    if len(unseen) != 1:
        return adjusted, frozenset()
    outcomes = personally_observed_resource_outcomes(
        previous=previous, traits=traits)
    failed_tied = [
        a for a in tied if a != unseen[0] and a in outcomes
        and outcomes[a][1] >= NONRESTORING_ATTEMPTS
        and outcomes[a][1] > outcomes[a][0]
        and assess_needs(body, traits).pressures[
            CONSUMED_RESOURCE_NEED[a]] > 0
    ]
    # No multi-source invented ranking: when several personally failing
    # alternatives are tied, this tiny experiment declines to arbitrate.
    if len(failed_tied) != 1:
        return adjusted, frozenset()
    adjusted[unseen[0]] += 1
    return adjusted, frozenset(unseen)


def personally_observed_place_tie(
    scores, *, claim, body, traits, previous, learning, enabled,
):
    """One bounded point to ONE evidenced, adjacent, tied-top move.

    A human-designed tie-only research hypothesis, NOT place planning or
    guaranteed future restoration. A previously visited site may be
    depleted. Only an actual prior paid resource contact under need
    provides a place-specific bodily association. Present need is read
    independently of historical efficacy; time does not erase evidence.
    """
    if type(enabled) is not bool or type(learning) is not bool:
        raise NativeRefusal("exact place tie and learning flags required")
    updated = dict(scores)
    if not enabled or not learning:
        return updated, frozenset()
    if not any(destination(a) is not None for a in claim.capture.accessible_semantics):
        return updated, frozenset()
    offered = claim.capture.accessible_semantics
    top = max((updated[a] for a in offered if a in updated), default=0)
    if not 0 < top < 1024:
        return updated, frozenset()
    tied = [a for a in offered if updated.get(a) == top]
    if len(tied) < 2:
        return updated, frozenset()
    # The native journal uses sqlite3.Row; the read-only site extractor
    # intentionally accepts only plain immutable physical-event tuples.
    # Normalize the same owner's already committed rows without altering
    # their order, values, or evidence boundary.
    evidence = lived_place_outcomes(
        tuple(tuple(row) for row in previous), traits=traits, enabled=True)
    relevance = current_need_site_relevance(
        evidence, body=body, traits=traits)
    possibilities = []
    for action in tied:
        site = destination(action)
        if site is None:
            continue
        total = sum(value for (visited, target), value in relevance.items()
                    if visited == site)
        if total > 0:
            possibilities.append((action, total))
    if not possibilities:
        return updated, frozenset()
    high = max(value for _, value in possibilities)
    favored = [action for action, value in possibilities if value == high]
    if len(favored) != 1:
        return updated, frozenset()
    updated[favored[0]] += 1
    return updated, frozenset(favored)


def isolate_context_free_movement_credit(scores, *, learning, spatial_world, enabled):
    """Refuse to transport one move's outcome to all same-named moves.

    The historical G2 result score does not encode origin, need or intended
    physical destination. Do not pretend its immediate physiological relief
    is a general learned payoff for movement to that destination. Retain the
    same innate motion prior and born exploration, and let separately lived
    place/need evidence influence the existing optional tie mechanism.
    """
    if any(type(flag) is not bool for flag in
           (learning, spatial_world, enabled)):
        raise NativeRefusal("exact native movement-credit birth flags required")
    if enabled and (not learning or not spatial_world):
        raise NativeRefusal("isolated movement credit requires spatial learning")
    updated = dict(scores)
    if not enabled:
        return updated, frozenset()
    isolated = frozenset(action for action in MOTIONS if action in updated)
    for action in isolated:
        updated[action] = PRIORS[action]
    return updated, isolated


def personally_paid_arrival_purpose(
    scores, *, claim, body, traits, previous, prior_event, learning, enabled,
):
    """Carry an actually paid return's value into an observed LOCAL use.

    One capture only; no new persistent owner, hidden payoff or motor script.
    The previous *admitted* move must have a signed personal-place provenance
    in its paid candidate valuation. The destination must physically equal
    the currently reached site. The local resource must be offered and have
    restored the corresponding bodily need here in this person's own past.
    Transfer ONLY the already-paid previous score, not a fabricated +N.
    """
    updated = dict(scores)
    if type(enabled) is not bool or type(learning) is not bool:
        raise NativeRefusal("exact born purpose flag required")
    if not enabled or not learning or not previous or prior_event is None:
        return updated, frozenset()
    last = previous[-1]
    arrived = destination(last[2])
    if arrived is None or replay_site(previous, enabled=True) != arrived:
        return updated, frozenset()
    if type(prior_event) is not dict:
        raise NativeRefusal("committed prior cognitive event required")
    frame, advice, control = (
        prior_event.get("frame"), prior_event.get("advice"),
        prior_event.get("control_review"))
    if (not isinstance(frame, dict) or not isinstance(advice, dict)
            or not isinstance(control, dict)
            or control.get("status") != "REVIEWED_NOT_ADMITTED"):
        return updated, frozenset()
    selected = control.get("suggested_candidate_ref")
    picked = [c for c in frame.get("candidates", ())
              if c["candidate_ref"] == selected]
    valued = [v for v in advice.get("values", ())
              if v["candidate_ref"] == selected]
    if (len(picked) != 1 or len(valued) != 1
            or picked[0]["semantic_ref"] != last[2]
            or PLACE_RETURN_EVIDENCE not in valued[0]["evidence_ref"]):
        return updated, frozenset()
    paid_return_value = valued[0]["value"]
    if type(paid_return_value) is not int or paid_return_value <= 0:
        return updated, frozenset()
    # The remembered place must have been physically experienced already.
    effects = lived_place_outcomes(
        tuple(tuple(row) for row in previous[:-1]),
        traits=traits, enabled=True)
    summary = summarized_site_experience(effects)
    pressures = assess_needs(body, traits).pressures
    applicable = []
    for action, target in CONSUMED_RESOURCE_NEED.items():
        if action not in claim.capture.accessible_semantics:
            continue
        success, failures, total = summary.get((arrived, target), (0, 0, 0))
        if (success > 0 and total > 0 and pressures[target] > 0
                and action in updated):
            applicable.append(action)
    if len(applicable) != 1:
        return updated, frozenset()
    action = applicable[0]
    if paid_return_value <= updated[action]:
        return updated, frozenset()
    updated[action] = paid_return_value
    return updated, frozenset((action,))


def sleep_consolidated_scores(scores, *, previous, learning, enabled):
    """Stabilize ONLY repeatedly lived outcomes before a committed sleep.

    A recent non-sleep result overrides old sleep consolidation. No inferred
    rewards, imagined outcomes, extra state owner or free physical effects.
    The normal paid sleep action supplies its own real metabolic cost.
    """
    adjusted = dict(scores)
    if not (learning and enabled):
        return adjusted, frozenset()
    sleeping = [i for i, row in enumerate(previous) if row[2] == "dormir"]
    if not sleeping:
        return adjusted, frozenset()
    boundary = sleeping[-1]
    if boundary == 0:
        return adjusted, frozenset()
    changed = set()
    for action in adjusted:
        prior = [row for row in previous[:boundary] if row[2] == action]
        later = [row for row in previous[boundary + 1:] if row[2] == action]
        if len(prior) < 2 or later:
            continue
        # Net relief is already an observed, birth-replayable consequence.
        mean = round(sum(int(round(20 * row[3])) for row in prior) /
                     len(prior))
        new_value = mean + 5
        if new_value != adjusted[action]:
            adjusted[action] = new_value
            changed.add(action)
    return adjusted, frozenset(changed)


class _Valuation(ChosenOutcomeValuationStudy):
    def __init__(self, *, body, traits, previous=(), learning=False,
                 sleep_consolidation=True, evidence_tie_exploration=False,
                 place_return_tie=False, purpose_followthrough=False,
                 contextual_movement_credit=False, spatial_world=False,
                 prior_event=None, **kwargs):
        super().__init__(**kwargs)
        self.body, self.traits = body, traits
        self.previous, self.learning = tuple(previous), learning
        self.sleep_consolidation = sleep_consolidation
        self.evidence_tie_exploration = evidence_tie_exploration
        self.place_return_tie = place_return_tie
        self.purpose_followthrough = purpose_followthrough
        self.contextual_movement_credit = contextual_movement_credit
        self.spatial_world = spatial_world
        self.prior_event = prior_event

    def evaluate_batch(self, *, frame, receipts):
        evaluated = super().evaluate_batch(frame=frame, receipts=receipts)
        named = {c.candidate_ref: c.semantic_ref for c in frame.candidates}
        original = {named[v.candidate_ref]: v.value for v in evaluated}
        stabilized, consolidated = sleep_consolidated_scores(
            original, previous=self.previous, learning=self.learning,
            enabled=self.sleep_consolidation)
        contextual, isolated = isolate_context_free_movement_credit(
            stabilized, learning=self.learning,
            spatial_world=self.spatial_world,
            enabled=self.contextual_movement_credit)
        initial = innate_adjustment(contextual, self.body, self.traits)
        updated, discouraged, associated = personally_nonrestoring_scores(
            initial, claim=self.claim, body=self.body, traits=self.traits,
            previous=self.previous, learning=self.learning)
        updated, exploratory = native_evidence_tie_exploration(
            updated, claim=self.claim, body=self.body, traits=self.traits,
            previous=self.previous, learning=self.learning,
            enabled=self.evidence_tie_exploration)
        updated, remembered = personally_observed_place_tie(
            updated, claim=self.claim, body=self.body, traits=self.traits,
            previous=self.previous, learning=self.learning,
            enabled=self.place_return_tie)
        updated, carried = personally_paid_arrival_purpose(
            updated, claim=self.claim, body=self.body, traits=self.traits,
            previous=self.previous, prior_event=self.prior_event,
            learning=self.learning, enabled=self.purpose_followthrough)
        return tuple(replace(
            v, value=updated[named[v.candidate_ref]],
            evidence_ref=v.evidence_ref +
            (RESOURCE_OUTCOME_EVIDENCE if
             named[v.candidate_ref] in associated else "") +
            (TIE_EXPLORATION_EVIDENCE if
             named[v.candidate_ref] in exploratory else "") +
            (PLACE_RETURN_EVIDENCE if
             named[v.candidate_ref] in remembered else "") +
            (PURPOSE_HANDOFF_EVIDENCE if
             named[v.candidate_ref] in carried else "") +
            (MOVEMENT_CREDIT_EVIDENCE if
             named[v.candidate_ref] in isolated else "") +
            ":native-body" +
            (SLEEP_EVIDENCE if named[v.candidate_ref] in consolidated
             and named[v.candidate_ref] not in associated else "") +
            (NONRESTORING_EVIDENCE if
             named[v.candidate_ref] in discouraged else ""))
            for v in evaluated)



def actual_old_water_gain(meta, elapsed_ticks):
    """External world quality at this physical time, NOT an observation.

    A birth-locked reversal may change old-source hydration after a fixed
    committed-time boundary, without granting any evidence or water. Only a
    later admitted drink actually reveals the resulting bodily consequence.
    """
    change_at = meta["water_quality_change_at"]
    if change_at and elapsed_ticks >= change_at:
        return meta["water_quality_after_gain"]
    return meta["drink_water_gain"]


def bounded_native_evidence(current, rows, *, water_restock_every, spatial_world=False):
    """Bound current subjective refs without erasing actual lifelong evidence.

    Preserve body/interoception and observed discovery provenance. For other
    factual events keep the latest committed physical-time refs across refills
    and chosen outcomes. They remain intact in the sole SQLite owner, and the
    independently replayed chosen-result window is unchanged (max 64).
    Hidden quality, future events and learning flags never enter this view.
    """
    fixed = list(current)
    fixed.extend("evidence:i2:native:water-found:" + str(row[0])
                 for row in rows if row[6])
    if len(fixed) > MAX_NATIVE_CAPTURE_REFS:
        raise NativeRefusal("mandatory first-person evidence overflow")
    timed = []
    # Spatial owners cannot personally observe historical replenishment
    # at distant sites. Current local stock still controls the affordance.
    # Nonspatial research births retain their global-offer event timeline.
    if water_restock_every and not spatial_world:
        timed.extend(
            (epoch * water_restock_every,
             "evidence:i2:native:water-offer-refilled:" +
             str(epoch * water_restock_every))
            for epoch in range(1, len(rows) // water_restock_every + 1)
        )
    timed.extend(
        (row[0], "evidence:i2:native:outcome:" + str(row[0]))
        for row in rows if row[2] != NO_ACTION
    )
    timed.sort(key=lambda item: (item[0], item[1]))
    slots = MAX_NATIVE_CAPTURE_REFS - len(fixed)
    recent = [ref for _, ref in timed[-slots:]] if slots else []
    result = tuple(sorted(fixed + recent))
    if (len(result) > MAX_NATIVE_CAPTURE_REFS or
            len(result) != len(set(result))):
        raise NativeRefusal("noncanonical bounded native evidence")
    return result


def old_water_available(meta, rows):
    """Present physical offers, never a prediction of water's actual effect.

    An exogenous refill becomes perceivable only after the corresponding
    number of committed physical ticks. No action or learning flag creates
    a refill, and an admitted drink must still cause any physiological gain.
    """
    interval = meta["water_restock_every"]
    born_supply = meta["water_stock"]
    elapsed = len(rows)
    replenished = elapsed // interval if interval else 0
    consumed = sum(row[2] == "boire" for row in rows)
    return born_supply + replenished - consumed


def old_water_accessible(meta, rows):
    """Physical *local* water offer, never a future gain or hidden map clue.

    None retains legacy global offers. A birth-locked site identity requires
    an actually reached location in the same owner's committed move history.
    """
    if old_water_available(meta, rows) <= 0:
        return False
    home = meta["ordinary_water_site"]
    if home is None:
        return True
    return (bool(meta["spatial_world"]) and
            replay_site(rows, enabled=True) == home)


def old_food_available(meta, rows):
    """Actual food units; exogenous clock is physical, never learned payoff."""
    # Pure legacy physical projection fixtures omit an optional refill period.
    # Persisted v17 genesis always includes its born-locked signed value.
    interval = meta.get("food_restock_every", 0)
    elapsed = len(rows)
    replenished = elapsed // interval if interval else 0
    consumed = sum(row[2] == "manger" for row in rows)
    return meta["food_stock"] + replenished - consumed


def old_food_accessible(meta, rows):
    """Physically stocked and locally offered food, never hidden payoff."""
    if old_food_available(meta, rows) <= 0:
        return False
    home = meta["ordinary_food_site"]
    if home is None:
        return True
    return (bool(meta["spatial_world"]) and
            replay_site(rows, enabled=True) == home)


def genesis_digest(meta):
    return sha256(_json([GENESIS_SCHEMA, meta["life_ref"],
        meta["genesis_ref"], meta["body_json"], meta["traits_json"],
        meta["food_stock"], meta["water_stock"], meta["learning"],
        meta["berry_food_gain"], meta["berry_integrity_delta"],
        meta["drink_water_gain"], meta["discovered_water_gain"], meta["sleep_consolidation"],
        meta["max_steps"], meta["water_restock_every"],
        meta["water_quality_change_at"], meta["water_quality_after_gain"],
        meta["evidence_tie_exploration"], meta["spatial_world"],
        meta["ordinary_water_site"], meta["place_return_tie"],
        meta["purpose_followthrough"],
        meta["contextual_movement_credit"],
        meta["ordinary_food_site"],
        meta["food_restock_every"]]).encode("ascii")).hexdigest()


class NativePaidI2:
    """One local SQLite file per research individual, no independent M11."""

    def __init__(self, path, life, genesis, *, inspection_only=False):
        self.path = Path(path)
        self.life_ref, self.genesis_ref = life, genesis
        self.inspection_only = inspection_only
        self.halted = False
        self.observation = _Observation(life)
        self.current = _Current()
        self.safety = _Safety()

    def _connect(self):
        if self.path.is_symlink() or not self.path.is_file():
            raise NativeRefusal("no native research identity file")
        return sqlite3.connect(self.path.resolve().as_uri() + "?mode=rw",
                               uri=True, timeout=5)

    def _fixture(self, evaluator):
        return CognitiveCycleFixture.reopen(
            path=self.path, life_ref=self.life_ref,
            observation_source=self.observation,
            valuation_source=evaluator, current_source=self.current,
            safety_source=self.safety, genesis_ref=self.genesis_ref,
            terminal_source=_Terminal())

    @classmethod
    def create(cls, path, *, body: Body, temperament: BirthTemperament,
               learning=True, sleep_consolidation=True,
               evidence_tie_exploration=False, spatial_world=False,
               ordinary_water_site=None, place_return_tie=False,
               purpose_followthrough=False, contextual_movement_credit=False,
               ordinary_food_site=None, max_steps=HORIZON, food_stock=4, water_stock=4,
               water_restock_every=0, food_restock_every=0,
               water_quality_change_at=0, water_quality_after_gain=0.0,
               uc=80,
               berry_food_gain=20.0, berry_integrity_delta=-8.0,
               drink_water_gain=25.0, discovered_water_gain=0.0):
        if (type(body) is not Body or
                type(temperament) is not BirthTemperament or
                min(body.food, body.water, body.integrity) <= 0 or
                type(learning) is not bool or
                type(sleep_consolidation) is not bool or
                type(evidence_tie_exploration) is not bool or
                type(spatial_world) is not bool or
                type(place_return_tie) is not bool or
                type(purpose_followthrough) is not bool or
                type(contextual_movement_credit) is not bool or
                (contextual_movement_credit and
                 (not spatial_world or not learning)) or
                (purpose_followthrough and (not spatial_world or
                    not place_return_tie or not learning)) or
                (place_return_tie and not spatial_world) or
                (ordinary_water_site is not None and
                 (type(ordinary_water_site) is not str or
                  ordinary_water_site not in GRAPH or not spatial_world)) or
                (ordinary_food_site is not None and
                 (type(ordinary_food_site) is not str or
                  ordinary_food_site not in GRAPH or not spatial_world)) or
                type(max_steps) is not int or not 1 <= max_steps <= MAX_BORN_STEPS or
                type(water_restock_every) is not int or
                not 0 <= water_restock_every <= 32 or
                type(food_restock_every) is not int or
                not 0 <= food_restock_every <= 32 or
                type(water_quality_change_at) is not int or
                not 0 <= water_quality_change_at <= MAX_BORN_STEPS or
                (water_quality_change_at and not water_restock_every) or
                type(water_quality_after_gain) not in (int, float) or
                not 0 <= water_quality_after_gain <= 100 or
                type(food_stock) is not int or not 0 <= food_stock <= 8 or
                type(water_stock) is not int or not 0 <= water_stock <= 8 or
                type(uc) is not int or not 0 <= uc <= 1000 or
                type(discovered_water_gain) not in (int, float) or
                not 0 <= discovered_water_gain <= 100):
            raise NativeRefusal("invalid independent bounded native birth")
        from i2.modules.native_body_contract import transition
        transition(body, "manger", berry_food_gain=berry_food_gain,
                   berry_integrity_delta=berry_integrity_delta)
        transition(body, "boire", drink_water_gain=drink_water_gain)
        # SQLite REAL columns restore integers as floating-point values.
        # Canonicalize physics inputs BEFORE hashing the immutable genesis,
        # so valid 0 and 0.0 are the same born world (but tampering still fails).
        berry_food_gain = float(berry_food_gain)
        berry_integrity_delta = float(berry_integrity_delta)
        drink_water_gain = float(drink_water_gain)
        discovered_water_gain = float(discovered_water_gain)
        water_quality_after_gain = float(water_quality_after_gain)
        key = uuid4().hex
        obj = cls(path, "i2:prototype:native:" + key,
                  "genesis:i2:native:" + key)
        CognitiveCycleFixture.create(
            path=obj.path, life_ref=obj.life_ref, synthetic_uc=uc,
            observation_source=obj.observation,
            valuation_source=_NoEvaluation(), current_source=obj.current,
            safety_source=obj.safety, genesis_ref=obj.genesis_ref,
            terminal_source=_Terminal())
        with obj._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            initialize_native_body(db, body=body, traits=temperament)
            db.execute("""CREATE TABLE native_genesis (
                id INTEGER PRIMARY KEY CHECK(id=1),
                life_ref TEXT NOT NULL, genesis_ref TEXT NOT NULL,
                body_json TEXT NOT NULL, traits_json TEXT NOT NULL,
                food_stock INTEGER NOT NULL, water_stock INTEGER NOT NULL,
                learning INTEGER NOT NULL, berry_food_gain REAL NOT NULL,
                berry_integrity_delta REAL NOT NULL,
                drink_water_gain REAL NOT NULL,
                discovered_water_gain REAL NOT NULL,
                sleep_consolidation INTEGER NOT NULL,
                max_steps INTEGER NOT NULL CHECK(max_steps BETWEEN 1 AND 128),
                water_restock_every INTEGER NOT NULL
                    CHECK(water_restock_every BETWEEN 0 AND 32),
                water_quality_change_at INTEGER NOT NULL
                    CHECK(water_quality_change_at BETWEEN 0 AND 128),
                water_quality_after_gain REAL NOT NULL,
                evidence_tie_exploration INTEGER NOT NULL
                    CHECK(evidence_tie_exploration IN (0,1)),
                spatial_world INTEGER NOT NULL CHECK(spatial_world IN (0,1)),
                ordinary_water_site TEXT,
                place_return_tie INTEGER NOT NULL CHECK(place_return_tie IN (0,1)),
                purpose_followthrough INTEGER NOT NULL
                    CHECK(purpose_followthrough IN (0,1)),
                contextual_movement_credit INTEGER NOT NULL
                    CHECK(contextual_movement_credit IN (0,1)),
                ordinary_food_site TEXT,
                food_restock_every INTEGER NOT NULL
                    CHECK(food_restock_every BETWEEN 0 AND 32),
                digest TEXT NOT NULL)""")
            db.execute("""CREATE TABLE native_discoveries (
                seq INTEGER PRIMARY KEY,
                physical_hash TEXT NOT NULL UNIQUE,
                found INTEGER NOT NULL CHECK(found IN (0,1)))""")
            meta = dict(life_ref=obj.life_ref, genesis_ref=obj.genesis_ref,
                        body_json=_json(body.as_dict()),
                        traits_json=_json(temperament.as_dict()),
                        food_stock=food_stock, water_stock=water_stock,
                        learning=int(learning), berry_food_gain=berry_food_gain,
                        berry_integrity_delta=berry_integrity_delta,
                        drink_water_gain=drink_water_gain,
                        discovered_water_gain=discovered_water_gain,
                        sleep_consolidation=int(sleep_consolidation),
                        max_steps=max_steps,
                        water_restock_every=water_restock_every,
                        water_quality_change_at=water_quality_change_at,
                        water_quality_after_gain=water_quality_after_gain,
                        evidence_tie_exploration=int(evidence_tie_exploration),
                        spatial_world=int(spatial_world),
                        ordinary_water_site=ordinary_water_site,
                        place_return_tie=int(place_return_tie),
                        purpose_followthrough=int(purpose_followthrough),
                        contextual_movement_credit=int(contextual_movement_credit),
                        ordinary_food_site=ordinary_food_site,
                        food_restock_every=food_restock_every)
            db.execute("INSERT INTO native_genesis VALUES(1,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                       (*meta.values(), genesis_digest(meta)))
            db.commit()
        obj.audit()
        return obj

    @classmethod
    def inspect(cls, path):
        """Cold audit only; never reopens native action authority."""
        path = Path(path)
        if path.is_symlink() or not path.is_file():
            raise NativeRefusal("native identity missing or symlinked")
        with sqlite3.connect(path.resolve().as_uri() + "?mode=ro",
                             uri=True) as db:
            row = db.execute(
                "SELECT life_ref,genesis_ref FROM native_genesis "
                "WHERE id=1").fetchone()
        if row is None:
            raise NativeRefusal("incomplete native birth")
        obj = cls(path, row[0], row[1], inspection_only=True)
        obj.audit()
        return obj

    def _meta(self, conn):
        conn.row_factory = sqlite3.Row
        row = conn.execute(
            "SELECT * FROM native_genesis WHERE id=1").fetchone()
        if row is None:
            raise NativeRefusal("missing native genesis")
        meta = dict(row)
        if ((meta["life_ref"], meta["genesis_ref"]) !=
                (self.life_ref, self.genesis_ref) or
                meta["digest"] != genesis_digest(meta)):
            raise NativeRefusal("foreign or mutated native genesis")
        return meta

    def _rows(self, conn):
        return tuple(conn.execute(
            "SELECT e.seq, e.capture_ref, p.admitted_action, "
            "p.net_physiological_relief, p.before_json, p.after_json, "
            "COALESCE(d.found,0) FROM native_physical_events p "
            "JOIN events e ON e.seq=p.seq "
            "LEFT JOIN native_discoveries d ON d.seq=p.seq ORDER BY p.seq"))

    def _claim(self, snapshot, meta, rows):
        seq = len(rows)
        if seq != snapshot["revision"]:
            raise NativeRefusal("native observation crossed revisions")
        chosen = [r[2] for r in rows]
        # Physical access, independent of the learning flag: every born life
        # sees the same local search site until it has actually explored it.
        offered = ["dormir", "attendre"]
        if "collecter" not in chosen:
            offered.append("collecter")
        if old_food_accessible(meta, rows):
            offered.append("manger")
        if old_water_accessible(meta, rows):
            offered.append("boire")
        if sum(r[6] for r in rows) > chosen.count("boire_decouverte"):
            offered.append("boire_decouverte")
        site = replay_site(rows, enabled=bool(meta["spatial_world"]))
        if meta["spatial_world"] and snapshot["body"].energy >= COSTS["se_deplacer"]:
            offered.extend(offered_moves(site))
        current = tuple(snapshot["current_evidence"])
        if meta["spatial_world"]:
            current += local_evidence(site)
        evidence = bounded_native_evidence(
            current, rows, water_restock_every=meta["water_restock_every"],
            spatial_world=bool(meta["spatial_world"]))
        def observed_claim(goal):
            return ObservationClaim(
                self.life_ref, FirstPersonCapture(
                    10 + 8 * seq, "capture:i2:native:" + str(seq),
                    goal, tuple(sorted(offered))),
                "source:i2:native:committed:" + str(seq),
                tuple(sorted(evidence)))
        # The existing intention owner consumes this subjective goal change.
        # A failed affordance remains physically accessible. Only a personally
        # observed, urgent repeated nonrestoration can revise the goal.
        ordinary = observed_claim("goal:physical-needs")
        body, traits = snapshot["body"], snapshot["traits"]
        # A spent resource is absent from affordances, but two personally
        # lived nonrestorations remain evidence for revising the intention.
        # This claims no permanent environmental impossibility.
        if bool(meta["learning"]) and any(
            personally_nonrestoring_action(
                body=body, previous=rows, action=action
            ) for action in DIRECT_RESTORATION_RESERVE
        ):
            # Reappraisal changes the current GOAL and paid priorities,
            # never whether a physical search site exists.
            return ObservationClaim(
                self.life_ref, FirstPersonCapture(
                    10 + 8 * seq, "capture:i2:native:" + str(seq),
                    "goal:physical-last-resort", tuple(sorted(offered))),
                "source:i2:native:committed:" + str(seq),
                tuple(sorted(evidence)))
        return ordinary

    def _history(self, rows):
        # Keep the FULL lifelong physical and cognitive journal for audit;
        # expose only the latest bounded chosen results to G2 Competition.
        # This is an explicit finite working window, never a new memory owner
        # or a deletion of older first-person experiences.
        lived = [row for row in rows if row[2] != NO_ACTION]
        return tuple(ObservedChosenResult(
            self.life_ref, capture, action,
            11 + 8 * (seq - 1),
            "evidence:i2:native:outcome:" + str(seq),
            int(round(20 * relief)))
            for seq, capture, action, relief, *_ in
            lived[-MAX_RECORDED_CHOICES:])

    def _apply(self, *, conn, seq, claim, frame, control_review,
               remaining_uc, event_head):
        """The sole physical action hook within v5's existing COMMIT."""
        meta = self._meta(conn)
        snapshot = native_snapshot(conn)
        rows = self._rows(conn)
        if claim != self._claim(snapshot, meta, rows):
            raise NativeRefusal("stale native body capture")
        if seq != len(rows) + 1:
            raise NativeRefusal("nonsequential native cognition")
        record = conn.execute(
            "SELECT event_json FROM events WHERE seq=?", (seq,)).fetchone()
        if record is None:
            raise NativeRefusal("no paid cognitive event")
        event = json.loads(record[0])
        if (event["frame"] != frame or
                event["control_review"] != control_review or
                event["claim_digest"] != claim.digest()):
            raise NativeRefusal("unbound native candidate or observation")
        review = event["control_review"]
        if review is None or review["status"] != "REVIEWED_NOT_ADMITTED":
            return commit_unadmitted_tick(conn, cognition_hash=event_head)
        selected = [c["semantic_ref"] for c in event["frame"]["candidates"]
                    if c["candidate_ref"] == review["suggested_candidate_ref"]]
        if len(selected) != 1:
            raise NativeRefusal("ambiguous chosen action")
        action = selected[0]
        admission = "internal:i2:native-admission:" + sha256(
            _json([seq, event_head, action]).encode()).hexdigest()
        if (action not in claim.capture.accessible_semantics or
                (action == "boire_decouverte" and
                 sum(r[2] == action for r in rows) >= sum(r[6] for r in rows)) or
                (action == "boire" and
                 not old_water_accessible(meta, rows)) or
                (action == "manger" and
                 not old_food_accessible(meta, rows))):
            raise NativeRefusal("unavailable or depleted native resource")
        if destination(action) is not None:
            if (not meta["spatial_world"] or
                    snapshot["body"].energy < COSTS["se_deplacer"] or
                    destination(action) not in GRAPH[
                        replay_site(rows, enabled=True)]):
                raise NativeRefusal("physical move not adjacent or unaffordable")
        effect = {}
        if action == "boire":
            effect["drink_water_gain"] = actual_old_water_gain(meta, len(rows))
        elif action == "boire_decouverte":
            effect["drink_water_gain"] = meta["discovered_water_gain"]
        elif action == "manger":
            effect["berry_food_gain"] = meta["berry_food_gain"]
            effect["berry_integrity_delta"] = meta["berry_integrity_delta"]
        result = commit_admitted_physics(
            conn, action=action, admission_ref=admission,
            cognition_hash=event_head, **effect)
        if action == "collecter":
            found = int(meta["discovered_water_gain"] > 0 and
                        not any(r[6] for r in rows))
            conn.execute("INSERT INTO native_discoveries VALUES(?,?,?)",
                         (seq, result["physical_hash"], found))
        if conn.execute("SELECT remaining_uc FROM account WHERE id=1").fetchone()[0] != remaining_uc:
            raise NativeRefusal("native physiological step lacks paid UC")
        return result

    def audit(self):
        """Replay every native effect from the immutable local genesis.

        The generic journal audit checks its physical hash chain; this
        additional local audit recalculates the actual body and subjective
        values from birth, with only preceding chosen observations. This is
        NOT an independently witnessed M11 or a proof of general learning.
        """
        with self._connect() as db:
            meta = self._meta(db)
            physical = audit_native_body(db)
            snapshot = native_snapshot(db)
            recorded = tuple(db.execute(
                "SELECT seq,capture_ref,event_json,event_hash "
                "FROM events ORDER BY seq"))
            effects = tuple(db.execute(
                "SELECT seq,admitted_action,admission_ref,cognition_hash,"
                "before_json,after_json,net_physiological_relief,terminal, "
                "event_hash FROM native_physical_events ORDER BY seq"))
            discoveries = tuple(db.execute(
                "SELECT seq,physical_hash,found FROM native_discoveries ORDER BY seq"))
            capacity, remaining = db.execute(
                "SELECT capacity,remaining_uc FROM identity JOIN account ON "
                "identity.id=account.id WHERE identity.id=1").fetchone()
        cognition = self._fixture(_NoEvaluation()).audit()
        if (len(recorded) != len(effects) or
                len(effects) > meta["max_steps"] or
                physical["revision"] != len(effects) or
                cognition["committed"] != len(effects) or
                cognition["motor_authority"] != "NONE" or
                cognition["synthetic_terminal"]):
            raise NativeRefusal("native world and paid cognition diverge")

        body = saved_body(meta["body_json"])
        traits = saved_traits(meta["traits_json"])
        if (snapshot["traits"] != traits or
                physical["traits"] != traits.as_dict() or
                min(body.food, body.water, body.integrity) <= 0):
            raise NativeRefusal("mutated native birth traits or terminal genesis")
        previous = []
        discoveries_by_seq = {r[0]: (r[1], r[2]) for r in discoveries}
        if len(discoveries_by_seq) != len(discoveries):
            raise NativeRefusal("duplicate discovery")
        total_uc, terminal = 0, False
        prior_cognitive_event = None
        for index, (source, effect) in enumerate(zip(recorded, effects)):
            seq, capture, event_json, cognition_hash = source
            (phy_seq, action, admission_ref, linked_head,
             before_json, after_json, saved_relief, saved_terminal,
             physical_hash) = effect
            if (terminal or seq != index + 1 or phy_seq != seq or
                    linked_head != cognition_hash):
                raise NativeRefusal("post-terminal or unbound native transition")
            claim = self._claim(
                {"revision": index, "body": body, "traits": traits,
                 "current_evidence": current_evidence(body, traits)},
                meta, previous)
            event = json.loads(event_json)
            expected_capture = {
                "step": claim.capture.step, "ref": claim.capture.ref,
                "goal_ref": claim.capture.goal_ref,
                "accessible_semantics": list(
                    claim.capture.accessible_semantics),
                "contradicted_semantics": list(
                    claim.capture.contradicted_semantics)}
            expected_claim = {
                "life_ref": claim.life_ref,
                "source_event_ref": claim.source_event_ref,
                "subjective_evidence_refs": list(
                    claim.subjective_evidence_refs),
                "capture": expected_capture}
            if (capture != claim.capture.ref or
                    event["claim_digest"] != claim.digest() or
                    event["claim"] != expected_claim):
                raise NativeRefusal("first-person body or past evidence forged")

            frame, advice = event["frame"], event["advice"]
            if frame is not None:
                if (advice is None or
                        frame["claim_digest"] != claim.digest() or
                        frame["capture_ref"] != claim.capture.ref):
                    raise NativeRefusal("missing bound paid native frame")
                past = self._history(previous) if meta["learning"] else ()
                priors = observed_chosen_scores(
                    claim=claim, results=past,
                    source=_HistorySource(past), priors=PRIORS)
                stabilized, consolidated = sleep_consolidated_scores(
                    priors, previous=previous, learning=bool(meta["learning"]),
                    enabled=bool(meta["sleep_consolidation"]))
                contextual, isolated = isolate_context_free_movement_credit(
                    stabilized, learning=bool(meta["learning"]),
                    spatial_world=bool(meta["spatial_world"]),
                    enabled=bool(meta["contextual_movement_credit"]))
                initial = innate_adjustment(contextual, body, traits)
                scores, discouraged, associated = personally_nonrestoring_scores(
                    initial, claim=claim, body=body, traits=traits,
                    previous=previous, learning=bool(meta["learning"]))
                scores, exploratory = native_evidence_tie_exploration(
                    scores, claim=claim, body=body, traits=traits,
                    previous=previous, learning=bool(meta["learning"]),
                    enabled=bool(meta["evidence_tie_exploration"]))
                scores, remembered = personally_observed_place_tie(
                    scores, claim=claim, body=body, traits=traits,
                    previous=previous, learning=bool(meta["learning"]),
                    enabled=bool(meta["place_return_tie"]))
                scores, carried = personally_paid_arrival_purpose(
                    scores, claim=claim, body=body, traits=traits,
                    previous=previous, prior_event=prior_cognitive_event,
                    learning=bool(meta["learning"]),
                    enabled=bool(meta["purpose_followthrough"]))
                candidates = {item["candidate_ref"]: item["semantic_ref"]
                              for item in frame["candidates"]}
                values = advice["values"]
                if (len(candidates) != len(frame["candidates"]) or
                        len(values) != len(candidates) or
                        any(c not in candidates or
                            candidates[c] not in claim.capture.accessible_semantics or
                            value["value"] != scores[candidates[c]] or
                            not value["evidence_ref"].endswith(
                                (RESOURCE_OUTCOME_EVIDENCE if
                                 candidates[c] in associated else "") +
                                (TIE_EXPLORATION_EVIDENCE if
                                 candidates[c] in exploratory else "") +
                                (PLACE_RETURN_EVIDENCE if
                                 candidates[c] in remembered else "") +
                                (PURPOSE_HANDOFF_EVIDENCE if
                                 candidates[c] in carried else "") +
                                (MOVEMENT_CREDIT_EVIDENCE if
                                 candidates[c] in isolated else "") +
                                ":native-body" +
                                (SLEEP_EVIDENCE if
                                 candidates[c] in consolidated and
                                 candidates[c] not in associated else "") +
                                (NONRESTORING_EVIDENCE if
                                 candidates[c] in discouraged else ""))
                            for value in values
                            for c in (value["candidate_ref"],))):
                    raise NativeRefusal("paid score not grounded in born needs or experience")
            elif advice is not None:
                raise NativeRefusal("unpaid native advice")

            review = event["control_review"]
            if review is not None and review["status"] == "REVIEWED_NOT_ADMITTED":
                if frame is None:
                    raise NativeRefusal("native action lacks paid candidates")
                chosen = [item["semantic_ref"] for item in frame["candidates"]
                          if item["candidate_ref"] ==
                          review["suggested_candidate_ref"]]
                safety = event["safety_finding"]
                control = event["control_receipt"]
                if (len(chosen) != 1 or action != chosen[0] or
                        action not in claim.capture.accessible_semantics or
                        safety is None or safety["veto"] is not False or
                        control is None or
                        control["ref"] != review["control_receipt_ref"]):
                    raise NativeRefusal("native physical action lacks fresh admission")
                expected_ref = ("internal:i2:native-admission:" + sha256(
                    _json([seq, cognition_hash, action]).encode()).hexdigest())
                if destination(action) is not None and (
                        not meta["spatial_world"] or
                        body.energy < COSTS["se_deplacer"] or
                        destination(action) not in GRAPH[
                            replay_site(previous, enabled=True)]):
                    raise NativeRefusal("replayed movement not adjacent or affordable")
                if action == "boire" and not old_water_accessible(meta, previous):
                    raise NativeRefusal("native drank unavailable or remote water")
                if action == "boire_decouverte" and sum(
                        prior[2] == action for prior in previous) >= sum(
                            prior[6] for prior in previous):
                    raise NativeRefusal("drank new source before discovered")
                if action == "manger" and not old_food_accessible(meta, previous):
                    raise NativeRefusal("native ate unavailable or remote food")
                changes = {}
                if action == "boire":
                    changes["drink_water_gain"] = actual_old_water_gain(meta, len(previous))
                elif action == "boire_decouverte":
                    changes["drink_water_gain"] = meta["discovered_water_gain"]
                elif action == "manger":
                    changes["berry_food_gain"] = meta["berry_food_gain"]
                    changes["berry_integrity_delta"] = meta["berry_integrity_delta"]
                outcome = admitted_consequence(
                    before=body, temperament=traits,
                    action=("boire" if action == "boire_decouverte" else
                            "se_deplacer" if destination(action) is not None
                            else action),
                    admitted=True, applied=True, **changes)
                next_body = outcome.after
                terminal = outcome.terminal
            else:
                if (action != NO_ACTION or
                        (review is not None and (
                            review["status"] == "REVIEWED_NOT_ADMITTED" or
                            review["suggested_candidate_ref"] is not None))):
                    raise NativeRefusal("unadmitted physical time became a motor action")
                expected_ref = "no-motor:i2:physical-time:" + sha256(
                    _json([seq, cognition_hash]).encode()).hexdigest()
                next_body = passive_body_tick(body)
                terminal = min(next_body.food, next_body.water,
                               next_body.integrity) <= 0
            if admission_ref != expected_ref:
                raise NativeRefusal("native motor or no-motor receipt forged")
            before_pressure = assess_needs(body, traits)
            after_pressure = assess_needs(next_body, traits)
            relief = (sum(before_pressure.pressures.values()) -
                      sum(after_pressure.pressures.values()))
            if (before_json != _json(body.as_dict()) or
                    after_json != _json(next_body.as_dict()) or
                    not isclose(saved_relief, relief, rel_tol=0, abs_tol=1e-12) or
                    saved_terminal != int(terminal)):
                raise NativeRefusal("native physiology disagrees with birth replay")
            found = int(action == "collecter" and
                        meta["discovered_water_gain"] > 0 and
                        not any(prior[6] for prior in previous))
            if action == "collecter":
                if discoveries_by_seq.get(seq) != (physical_hash, found):
                    raise NativeRefusal("native discovery record forged")
            elif seq in discoveries_by_seq:
                raise NativeRefusal("unearned discovery event")
            total_uc += (event["intake_uc"] + event["competition_uc"] +
                         event["control_uc"])
            previous.append((seq, capture, action, relief,
                             before_json, after_json, found))
            prior_cognitive_event = event
            body = next_body
        if (len(discoveries) != sum(r[2] == "collecter" for r in previous) or
                body != snapshot["body"] or
                body.as_dict() != physical["body"] or
                total_uc != capacity - remaining or
                remaining != cognition["remaining_synthetic_uc"]):
            raise NativeRefusal("native final body or paid UC disagrees with replay")
        return {
            "revision": len(effects), "max_steps": meta["max_steps"],
            "body": body.as_dict(),
            "site": replay_site(previous, enabled=bool(meta["spatial_world"]))
                    if meta["spatial_world"] else None,
            "temperament": traits.as_dict(), "remaining_uc": remaining,
            "terminal": terminal, "m11_authenticated": False,
            "engine_registered": False, "scientific_verdict": "NOT_ESTABLISHED",
            "native_loop": "PAID_SINGLE_SQLITE_INTERNAL_ONLY",
        }

    def step(self, *, veto=False, fault=None):
        if self.inspection_only or self.halted:
            raise NativeRefusal("halted or cold inspection-only life")
        if type(veto) is not bool:
            raise NativeRefusal("native safety veto must be a boolean")
        before = self.audit()
        if before["terminal"] or before["revision"] >= before["max_steps"]:
            raise NativeRefusal("terminal or bounded native life")
        with self._connect() as db:
            meta = self._meta(db)
            snap = native_snapshot(db)
            rows = self._rows(db)
        claim = self._claim(snap, meta, rows)
        with self._connect() as db:
            prior_row = (db.execute("SELECT event_json FROM events WHERE seq=?",
                                    (len(rows),)).fetchone()
                         if rows else None)
        prior_cognitive_event = (json.loads(prior_row[0]) if prior_row else None)
        body, traits = snap["body"], snap["traits"]
        self.observation.expected = claim.digest()
        self.current.ref = claim.capture.ref
        self.safety.veto = veto
        self.safety.reflex = NativeCaptureReflex(claim, body, traits)
        # Only previously committed personal results, never a hidden counterfactual.
        outcomes = self._history(rows) if meta["learning"] else ()
        valuation = _Valuation(
            claim=claim, results=outcomes, source=_HistorySource(outcomes),
            priors=PRIORS, body=body, traits=traits,
            previous=rows, learning=bool(meta["learning"]),
            sleep_consolidation=bool(meta["sleep_consolidation"]),
            evidence_tie_exploration=bool(meta["evidence_tie_exploration"]),
            place_return_tie=bool(meta["place_return_tie"]),
            purpose_followthrough=bool(meta["purpose_followthrough"]),
            contextual_movement_credit=bool(meta["contextual_movement_credit"]),
            spatial_world=bool(meta["spatial_world"]),
            prior_event=prior_cognitive_event)
        fixture = self._fixture(valuation)
        try:
            if not rows:
                choice = next((action for action in ("boire", "manger")
                               if action in claim.capture.accessible_semantics),
                              claim.capture.accessible_semantics[0])
                fixture.open(
                    claim=claim, semantic_ref=choice,
                    evidence_ref=current_evidence(body, traits)[0],
                    ttl_steps=64, _fault_at=fault, _g1_lab_hook=self._apply)
            else:
                fixture.observe(
                    claim=claim, _fault_at=fault, _g1_lab_hook=self._apply)
        except CommitAcknowledgmentLost:
            self.halted = True
            raise
        except sqlite3.Error:
            self.halted = True
            raise
        final = self.audit()
        if final["revision"] != before["revision"] + 1:
            self.halted = True
            raise NativeRefusal("native ambiguous physical COMMIT")
        return final
