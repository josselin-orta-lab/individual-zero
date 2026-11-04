"""#986: pure first-person opportunity audit for v23, never a motor policy.

Call only AFTER NativePaidI2.inspect(path).audit() has independently cold-verified
the complete SQLite journal. Does not alter a born identity or infer remote food.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_owner_support import saved_body
from i2.modules.native_spatial_world import BORN_SITE, GRAPH, destination, site_after
from i2.modules.native_physiological_needs import assess_needs
from i2.runtime.native_paid_cycle import (
    NEED_FAILURE_EXPLORATION_EVIDENCE, ORIGIN_NOVELTY_EVIDENCE,
    personally_failed_need_channels,
)

REASONS = frozenset({
    "NO_PAID_FRAME", "NO_FAILED_CURRENT_NEED", "URGENT_REFLEX",
    "ORIGIN_NOVELTY_ALREADY_CREDITED", "NO_UNSEEN_OFFERED_MOVE",
    "MULTIPLE_UNSEEN_OFFERED_MOVES", "NONPOSITIVE_SCORE",
    "SCORE_GAP_GT_FOUR", "ELIGIBLE_BUT_NOT_CREDITED",
    "UNOBSERVABLE_PREBOOST_SCORE",
})


@dataclass(frozen=True, slots=True)
class FailureOpportunity:
    tick: int
    site: str
    chosen: str
    failed_channels: tuple[str, ...]
    visited_before: tuple[str, ...]
    unknown_offered: tuple[str, ...]
    offered: tuple[str, ...]
    reflex: str
    top_score: int | None
    candidate_score: int | None
    score_gap: int | None
    offered_movement_count: int
    origin_novelty: bool
    factor_tagged: bool
    factor_enabled: bool
    reason: str


def _reflex(body, traits):
    if min(body.food, body.water, body.integrity) <= 2:
        return "PREEMPT"
    if assess_needs(body, traits).immediate_danger:
        return "CONSTRAIN"
    return "NO_PREEMPTION"


def audit_need_failure_opportunities(*, events, physical, traits,
                                     factor_enabled):
    """Classify actual paid journal ticks without modifying scores or histories.

    physical: (admitted_action, canonical_before_json, canonical_after_json).
    Cold audit is a REQUIRED caller precondition, not replaced by this observer.
    The v23 signed score is post-boost, so preboost gap is *unknowable* on
    tagged ticks: do not forge or try to subtract a guessed score increment.
    """
    if (type(events) not in (tuple, list) or
            type(physical) not in (tuple, list) or
            len(events) != len(physical) or
            type(traits) is not BirthTemperament or
            type(factor_enabled) is not bool):
        raise ValueError("complete typed native journal required")
    site = BORN_SITE
    visited = {site}
    previous = []
    prior_after = None
    classified = []
    for tick, (event, effect) in enumerate(zip(events, physical), 1):
        if (type(event) is not dict or type(effect) not in (tuple, list)
                or len(effect) != 3):
            raise ValueError("exact committed event and physical outcome required")
        action, before_json, after_json = effect
        before, after = saved_body(before_json), saved_body(after_json)
        if prior_after is not None and before != prior_after:
            raise ValueError("noncontinuous physical history")
        prior_after = after
        if type(action) is not str:
            raise ValueError("exact admitted action required")
        claim = event.get("claim")
        if type(claim) is not dict or type(claim.get("capture")) is not dict:
            raise ValueError("missing first-person claim")
        offered = claim["capture"].get("accessible_semantics")
        if (type(offered) is not list or not offered or
                len(offered) != len(set(offered)) or
                any(type(a) is not str for a in offered)):
            raise ValueError("invalid local offers")
        if action != "NO_ACTION" and action not in offered:
            raise ValueError("motor not offered to current individual")
        for name in offered:
            d = destination(name)
            if d is not None and d not in GRAPH[site]:
                raise ValueError("nonadjacent movement offered")
        failed = personally_failed_need_channels(
            body=before, traits=traits, previous=tuple(previous))
        frame, advice = event.get("frame"), event.get("advice")
        if (frame is None) != (advice is None):
            raise ValueError("unpaired paid frame/advice")
        values = {}
        tagged = []
        old_tags = []
        if frame is not None:
            if (type(frame) is not dict or type(advice) is not dict or
                    type(frame.get("candidates")) is not list or
                    type(advice.get("values")) is not list):
                raise ValueError("malformed paid frame/advice")
            refs = {}
            for candidate in frame["candidates"]:
                if (type(candidate) is not dict or
                        type(candidate.get("candidate_ref")) is not str or
                        type(candidate.get("semantic_ref")) is not str):
                    raise ValueError("invalid candidate")
                ref, semantic = candidate["candidate_ref"], candidate["semantic_ref"]
                if ref in refs:
                    raise ValueError("duplicate candidate reference")
                refs[ref] = semantic
            if len(set(refs.values())) != len(refs) or set(refs.values()) != set(offered):
                raise ValueError("scored frame does not match local offers")
            for item in advice["values"]:
                if (type(item) is not dict or
                        item.get("candidate_ref") not in refs or
                        type(item.get("value")) is not int or
                        type(item.get("evidence_ref")) is not str):
                    raise ValueError("invalid paid score")
                name = refs[item["candidate_ref"]]
                if name in values:
                    raise ValueError("duplicate signed score")
                values[name] = item["value"]
                ev = item["evidence_ref"]
                if NEED_FAILURE_EXPLORATION_EVIDENCE in ev:
                    tagged.append(name)
                if ORIGIN_NOVELTY_EVIDENCE in ev:
                    old_tags.append(name)
            if set(values) != set(offered):
                raise ValueError("missing paid value")
        if not factor_enabled and tagged:
            raise ValueError("factor evidence on disabled birth")
        unseen = tuple(a for a in offered
                       if destination(a) in GRAPH[site]
                       and destination(a) not in visited)
        if (len(old_tags) > 1 or
                any(destination(a) not in GRAPH[site] for a in old_tags)):
            raise ValueError("invalid previous novelty provenance")
        if len(tagged) > 1 or (tagged and
                (not factor_enabled or tagged[0] not in unseen or old_tags)):
            raise ValueError("impossible native exploration provenance")
        reflex = _reflex(before, traits)
        top = max(values.values()) if values else None
        candidate = values[unseen[0]] if len(unseen) == 1 and values else None
        offered_moves = sum(destination(a) in GRAPH[site] for a in offered)
        gap = top - candidate if candidate is not None and not tagged else None
        if frame is None:
            reason = "NO_PAID_FRAME"
            if action != "NO_ACTION":
                raise ValueError("unpaid non-null motor")
        elif not failed or traits.exploration <= 0:
            reason = "NO_FAILED_CURRENT_NEED"
        elif reflex != "NO_PREEMPTION":
            reason = "URGENT_REFLEX"
        elif old_tags:
            reason = "ORIGIN_NOVELTY_ALREADY_CREDITED"
        elif not unseen:
            reason = "NO_UNSEEN_OFFERED_MOVE"
        elif len(unseen) > 1:
            reason = "MULTIPLE_UNSEEN_OFFERED_MOVES"
        elif tagged:
            reason = "UNOBSERVABLE_PREBOOST_SCORE"
        elif not 0 < top < 1024 or candidate <= 0:
            reason = "NONPOSITIVE_SCORE"
        elif gap > 4:
            reason = "SCORE_GAP_GT_FOUR"
        else:
            reason = "ELIGIBLE_BUT_NOT_CREDITED"
        if tagged and reason != "UNOBSERVABLE_PREBOOST_SCORE":
            raise ValueError("factor tag impossible under previous-life gates")
        classified.append(FailureOpportunity(
            tick=tick, site=site, chosen=action,
            failed_channels=tuple(sorted(failed)),
            visited_before=tuple(sorted(visited)), unknown_offered=unseen,
            offered=tuple(offered), reflex=reflex,
            top_score=top, candidate_score=candidate, score_gap=gap,
            offered_movement_count=offered_moves,
            origin_novelty=bool(old_tags), factor_tagged=bool(tagged),
            factor_enabled=factor_enabled, reason=reason))
        previous.append((tick, "", action, 0.0, before_json, after_json, 0))
        d = destination(action)
        if d is not None:
            site = site_after(site, action)
            visited.add(site)
    return tuple(classified)


def summarize_need_failure_opportunities(rows):
    if type(rows) is not tuple or any(type(x) is not FailureOpportunity for x in rows):
        raise ValueError("classified immutable sequence required")
    return {
        "paid_ticks": len(rows),
        "reason_counts": dict(sorted(Counter(x.reason for x in rows).items())),
        "factor_tags": sum(x.factor_tagged for x in rows),
        "current_double_failure_ticks": sum(bool(x.failed_channels) for x in rows),
        "unseen_move_offers": sum(bool(x.unknown_offered) for x in rows),
        "no_movement_offered_ticks": sum(
            x.offered_movement_count == 0 for x in rows),
        "only_visited_moves_offered_ticks": sum(
            x.offered_movement_count > 0 and not x.unknown_offered for x in rows),
        "multiple_unseen_offers_ticks": sum(
            len(x.unknown_offered) > 1 for x in rows),
        "origin_novelty_ticks": sum(x.origin_novelty for x in rows),
        "urgent_reflex_ticks": sum(
            x.reflex != "NO_PREEMPTION" for x in rows),
        "unique_unseen_and_double_failure_ticks": sum(
            len(x.unknown_offered) == 1 and bool(x.failed_channels)
            for x in rows),
        "positive_bounded_score_opportunity_ticks": sum(
            x.reason in ("ELIGIBLE_BUT_NOT_CREDITED",
                         "UNOBSERVABLE_PREBOOST_SCORE")
            for x in rows),
        "eligible_but_not_credited_on_ticks": sum(
            x.reason == "ELIGIBLE_BUT_NOT_CREDITED" and x.factor_enabled
            for x in rows),
        "first_double_failure_tick": next(
            (x.tick for x in rows if x.failed_channels), None),
        "first_unique_unseen_and_double_failure_tick": next(
            (x.tick for x in rows if len(x.unknown_offered) == 1
             and x.failed_channels), None),
        "first_factor_tag_tick": next(
            (x.tick for x in rows if x.factor_tagged), None),
        "offered_but_below_top": sum(
            x.score_gap is not None and x.score_gap > 0 for x in rows),
        "chosen_movements": sum(destination(x.chosen) is not None for x in rows),
        "actual_visits": tuple(sorted({
            d for x in rows if (d := destination(x.chosen)) is not None
        } | {BORN_SITE})),
        "diagnostic_only": True,
        "preboost_score_imputed": False,
    }


def report_need_failure_opportunities(**kwargs):
    rows = audit_need_failure_opportunities(**kwargs)
    return {"summary": summarize_need_failure_opportunities(rows),
            "ticks": [asdict(row) for row in rows]}
