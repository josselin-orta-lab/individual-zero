"""P4 #982: read-only paid exploration opportunity audit.

Never controls an actuator, changes a score, predicts food quality or owns a
life. Caller MUST cold-audit its existing SQLite identity before interpreting
rows as historical evidence. Input is the owner's unchanged committed journal.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from i2.modules.native_body_contract import Body
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_owner_support import saved_body
from i2.modules.native_physiological_needs import assess_needs
from i2.modules.native_spatial_world import BORN_SITE, GRAPH, destination, site_after

NOVELTY_SUFFIX = ":visited-versus-unvisited-adjacent-tie"
REASONS = frozenset({
    "NO_POSITIVE_TOP", "SINGLE_TOP", "NONMOVE_TIED_TOP", "ONLY_ONE_MOVE",
    "NO_UNSEEN", "MULTIPLE_UNSEEN", "URGENT_REFLEX", "ELIGIBLE",
    "EXPLORATION_DISABLED",
})


@dataclass(frozen=True, slots=True)
class ExplorationOpportunity:
    tick: int
    site: str
    visited: tuple[str, ...]
    offered: tuple[str, ...]
    top_value_before_novelty: int | None
    tied_top: tuple[str, ...]
    movement_tied_top: tuple[str, ...]
    nonmovement_tied_top: tuple[str, ...]
    unseen_tied_top: tuple[str, ...]
    reason: str
    reflex_state: str
    pressures: tuple[float, float, float, float]
    chosen_action: str
    original_novelty_tagged: tuple[str, ...]
    destination_offers: tuple[tuple[str, int, bool], ...]


def _reflex_state(body, needs):
    if any(getattr(body, name) <= 2 for name in ("food", "water", "integrity")):
        return "PREEMPT"
    if needs.immediate_danger:
        return "CONSTRAIN"
    return "NO_PREEMPTION"


def classify_opportunity(*, scores, offered, site, visited, exploration,
                         reflex_state, enabled=True):
    """Diagnose exact existing innate novelty eligibility, without applying it.

    Scores are the values immediately BEFORE origin_novelty_tie_scores.
    This function does NOT infer a food payoff at any destination.
    """
    if (type(enabled) is not bool or site not in GRAPH or
            type(visited) not in (set, frozenset) or
            not visited or not visited.issubset(GRAPH) or
            type(exploration) not in (int, float) or
            not isfinite(exploration) or
            reflex_state not in ("PREEMPT", "CONSTRAIN", "NO_PREEMPTION")):
        raise ValueError("invalid native exploration opportunity")
    if (type(scores) is not dict or
            any(type(k) is not str or type(v) is not int
                for k, v in scores.items()) or
            type(offered) not in (tuple, list) or
            any(type(a) is not str or a not in scores for a in offered) or
            len(set(offered)) != len(offered)):
        raise ValueError("invalid paid candidate scores")
    if not offered:
        return ("NO_POSITIVE_TOP", None, (), (), (), ())
    top = max(scores[a] for a in offered)
    tied = tuple(a for a in offered if scores[a] == top)
    move = tuple(a for a in tied if destination(a) in GRAPH[site])
    nonmove = tuple(a for a in tied if a not in move)
    unseen = tuple(a for a in move if destination(a) not in visited)
    if not enabled or exploration <= 0:
        reason = "EXPLORATION_DISABLED"
    elif reflex_state != "NO_PREEMPTION":
        reason = "URGENT_REFLEX"
    elif top <= 0 or top >= 1024:
        reason = "NO_POSITIVE_TOP"
    elif len(tied) < 2:
        reason = "SINGLE_TOP"
    elif nonmove:
        reason = "NONMOVE_TIED_TOP"
    elif len(move) < 2:
        reason = "ONLY_ONE_MOVE"
    elif not unseen:
        reason = "NO_UNSEEN"
    elif len(unseen) > 1:
        reason = "MULTIPLE_UNSEEN"
    elif not any(destination(a) in visited for a in move):
        reason = "NO_UNSEEN"
    else:
        reason = "ELIGIBLE"
    return reason, top, tied, move, nonmove, unseen


def audit_paid_opportunities(*, events, physical, traits, exploration_enabled):
    """Read exact paid events and actually committed physical actions.

    A provenance tag reports the +1 *already* awarded by the existing native
    novelty algorithm. Undo that ONE logged point for eligibility analysis,
    without mutating any event/score or manufacturing a new action. No SQLite
    writes or access to hidden birth food laws.
    """
    if (type(traits) is not BirthTemperament or
            type(exploration_enabled) is not bool or
            type(events) not in (tuple, list) or
            type(physical) not in (tuple, list) or
            len(events) != len(physical)):
        raise ValueError("complete identical native event sequence required")
    site = BORN_SITE
    visited = {site}
    previous_after = None
    outcomes = []
    for tick, (event, phy) in enumerate(zip(events, physical), start=1):
        if type(event) is not dict or type(phy) not in (tuple, list) or len(phy) != 3:
            raise ValueError("canonical committed physical event required")
        action, before_json, after_json = phy
        before, after = saved_body(before_json), saved_body(after_json)
        if previous_after is not None and previous_after != before:
            raise ValueError("noncontinuous owner bodily history")
        previous_after = after
        if type(action) is not str:
            raise ValueError("invalid admitted action")
        claim = event.get("claim")
        if type(claim) is not dict or type(claim.get("capture")) is not dict:
            raise ValueError("missing committed first-person capture")
        cap = claim["capture"]
        offered = cap.get("accessible_semantics")
        if (type(offered) is not list or not offered or
                any(type(a) is not str for a in offered) or
                len(offered) != len(set(offered)) or
                any(destination(a) is not None and
                    destination(a) not in GRAPH[site] for a in offered)):
            raise ValueError("invalid or nonlocal offered actions")
        frame, advice = event.get("frame"), event.get("advice")
        if (frame is None) != (advice is None):
            raise ValueError("unpaired paid frame")
        if frame is None:
            if action != "NO_ACTION":
                raise ValueError("motor without paid frame")
            scores, tagged = {}, ()
            reason, top, tied, move, nonmove, unseen = (
                "NO_POSITIVE_TOP", None, (), (), (), ())
        else:
            if (type(frame) is not dict or type(advice) is not dict or
                    type(frame.get("candidates")) is not list or
                    type(advice.get("values")) is not list):
                raise ValueError("malformed paid candidate frame")
            refs = {c["candidate_ref"]: c["semantic_ref"]
                    for c in frame["candidates"]}
            if (len(refs) != len(frame["candidates"]) or
                    set(refs.values()) != set(offered) or
                    len(advice["values"]) != len(refs)):
                raise ValueError("paid frame does not match local capture")
            scores, tags = {}, []
            for v in advice["values"]:
                if (type(v) is not dict or
                        v.get("candidate_ref") not in refs or
                        type(v.get("value")) is not int or
                        type(v.get("evidence_ref")) is not str):
                    raise ValueError("invalid signed-score projection")
                name = refs[v["candidate_ref"]]
                if name in scores:
                    raise ValueError("duplicate paid candidate")
                has_tag = NOVELTY_SUFFIX in v["evidence_ref"]
                if has_tag:
                    tags.append(name)
                    if destination(name) not in GRAPH[site]:
                        raise ValueError("novelty tag on nonadjacent action")
                scores[name] = v["value"] - int(has_tag)
            tagged = tuple(tags)
        needs = assess_needs(before, traits)
        reflex = _reflex_state(before, needs)
        if frame is not None:
            reason, top, tied, move, nonmove, unseen = classify_opportunity(
                scores=scores, offered=tuple(offered), site=site,
                visited=frozenset(visited), exploration=traits.exploration,
                reflex_state=reflex, enabled=exploration_enabled)
            if (tagged and (reason != "ELIGIBLE" or
                            len(tagged) != 1 or tagged[0] != unseen[0])):
                raise ValueError("signed novelty evidence disagrees with replay")
            if reason == "ELIGIBLE" and not tagged:
                raise ValueError("missing actually paid novelty provenance")
        if action != "NO_ACTION" and action not in offered:
            raise ValueError("motor not locally offered")
        destination_offers = tuple(
            (a, scores.get(a, 0), destination(a) not in visited)
            for a in offered if destination(a) in GRAPH[site])
        outcomes.append(ExplorationOpportunity(
            tick=tick, site=site, visited=tuple(sorted(visited)),
            offered=tuple(offered), top_value_before_novelty=top,
            tied_top=tied, movement_tied_top=move,
            nonmovement_tied_top=nonmove, unseen_tied_top=unseen,
            reason=reason, reflex_state=reflex,
            pressures=tuple(needs.pressures[k] for k in
                            ("energy", "food", "water", "integrity")),
            chosen_action=action, original_novelty_tagged=tagged,
            destination_offers=destination_offers))
        d = destination(action)
        if d is not None:
            site = site_after(site, action)
            visited.add(site)
    return tuple(outcomes)


def summarize_source_opportunities(rows, *, source="source"):
    """Reachable, offered, highest paid, seen, chosen and sampled differ."""
    if not isinstance(rows, tuple):
        raise ValueError("immutable opportunity sequence required")
    at_passage = tuple(r for r in rows if r.site == "passage")
    toward = "se_deplacer_vers_" + source
    return {
        "paid_ticks": len(rows),
        "at_passage": len(at_passage),
        "source_offered": sum(toward in r.offered for r in at_passage),
        "source_highest_pre_novelty": sum(
            toward in r.tied_top for r in at_passage),
        "source_novelty_eligible": sum(
            r.reason == "ELIGIBLE" and toward in r.unseen_tied_top
            for r in at_passage),
        "source_chosen": sum(r.chosen_action == toward for r in rows),
        "source_visited": any(source in r.visited or
                              r.site == source for r in rows),
        "source_food_offered": sum(
            r.site == source and "manger" in r.offered for r in rows),
        "source_food_consumed": sum(
            r.site == source and r.chosen_action == "manger" for r in rows),
        "reasons_at_passage": {
            reason: sum(r.reason == reason for r in at_passage)
            for reason in sorted(REASONS)
        },
    }
