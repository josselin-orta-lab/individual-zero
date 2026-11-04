"""I2 P2 laboratory-only extraction of personally experienced place outcomes.

This does not change a motor decision and does not create a memory owner.
An association exists only if the single native research owner previously
committed a resource use at a physical site with a measurable current need.
Site reward is never pre-loaded from an experimenter-defined world map.
"""
from __future__ import annotations

from dataclasses import dataclass

from i2.modules.native_body_contract import CHANNELS
from i2.modules.native_birth_temperament import BirthTemperament
from i2.modules.native_owner_support import saved_body
from i2.modules.native_physiological_needs import assess_needs
from i2.modules.native_spatial_world import BORN_SITE, GRAPH, destination, site_after


RESOURCE_NEEDS = {
    "boire": "water",
    "boire_decouverte": "water",
    "manger": "food",
}


@dataclass(frozen=True, slots=True)
class ExperiencedPlaceOutcome:
    site: str
    action: str
    targeted_need: str
    effect: float
    restored: bool
    observation_sequence: int


def lived_place_outcomes(rows, *, traits: BirthTemperament, enabled: bool):
    """Extract site outcomes from the existing physical journal ONLY.

    Rows are the canonical native physical records (seq, capture, action,
    net relief, before JSON, after JSON, found). Current site is reconstructed
    exclusively from *preceding* committed movement events. The action's
    target reserve must have been deficient before its actual physical use.
    No clock forgetting, unexplored-site guesses, I1 imports, or motor calls.
    """
    if type(enabled) is not bool or type(traits) is not BirthTemperament:
        raise ValueError("valid born spatial flag and temperament required")
    site = BORN_SITE
    outcomes = []
    previous_seq = 0
    for row in rows:
        if not isinstance(row, (tuple, list)) or len(row) < 6:
            raise ValueError("complete native physical result required")
        seq, action = row[0], row[2]
        if type(seq) is not int or seq != previous_seq + 1:
            raise ValueError("contiguous physical event sequence required")
        previous_seq = seq
        move = destination(action)
        if move is not None:
            if not enabled:
                raise ValueError("spatial movement in nonspatial birth")
            site = site_after(site, action)
            continue
        target = RESOURCE_NEEDS.get(action)
        if target is None or not enabled:
            continue
        before, after = saved_body(row[4]), saved_body(row[5])
        if assess_needs(before, traits).pressures[target] <= 0:
            continue
        effect = getattr(after, target) - getattr(before, target)
        outcomes.append(ExperiencedPlaceOutcome(
            site, action, target, effect, effect > 0, seq))
    return tuple(outcomes)


def summarized_site_experience(outcomes):
    """Observed target evidence, not a place's inherent/future value."""
    totals = {}
    for item in outcomes:
        if type(item) is not ExperiencedPlaceOutcome or item.site not in GRAPH:
            raise ValueError("untrusted site experience")
        if item.targeted_need not in CHANNELS:
            raise ValueError("untrusted site target")
        key = (item.site, item.targeted_need)
        old = totals.setdefault(key, [0, 0, 0.0])
        old[0 if item.restored else 1] += 1
        old[2] += item.effect
    return {key: (value[0], value[1], round(value[2], 6))
            for key, value in totals.items()}


def current_need_site_relevance(outcomes, *, body, traits):
    """Project observed site consequences onto CURRENT bodily pressures.

    A site has no predicted guaranteed payoff: this is only the signed mean
    of actually personally lived target-reserve changes, weighted by the
    current corresponding need. Missing sites are UNKNOWN, not zero-valued.
    Past success/failure evidence persists unchanged as time passes.
    """
    if type(traits) is not BirthTemperament:
        raise ValueError("exact born temperament required")
    needs = assess_needs(body, traits)
    totals = summarized_site_experience(outcomes)
    relevance = {}
    for (site, target), (successes, failures, total) in totals.items():
        count = successes + failures
        if count <= 0:
            raise ValueError("site experience requires an actual contact")
        relevance[(site, target)] = round(
            (total / count) * needs.pressures[target], 6)
    return relevance


# Source-only observational P2 expansion: never read from hidden world laws.
# Existing target-only outcomes and paid decision ranking are not modified.
LIVED_BODY_ACTIONS = frozenset((
    "manger", "boire", "boire_decouverte", "dormir", "attendre",
))


@dataclass(frozen=True, slots=True)
class LivedWholeBodySiteConsequence:
    """One actually committed action, not a forecast, reward or motor policy."""
    sequence: int
    site: str
    action: str
    before: tuple[float, float, float, float]
    after: tuple[float, float, float, float]
    deltas: tuple[float, float, float, float]
    prior_pressures: tuple[float, float, float, float]

    def channel_effects(self) -> dict[str, float]:
        return dict(zip(CHANNELS, self.deltas))


def lived_whole_body_site_consequences(
    rows, *, traits: BirthTemperament, enabled: bool,
) -> tuple[LivedWholeBodySiteConsequence, ...]:
    """Project ONLY sequential physically committed rows for one birth.

    Canonical rows are (seq, capture, admitted_action, net_relief,
    before_json, after_json, discovery). A pure projection carries no
    independent hash authority: caller must first cold-audit the sole owner.
    Retain even a meal at full food with zero gain and real integrity harm.
    Unknown/unvisited locations have NO record, not fictitious zero injury.
    """
    if type(enabled) is not bool or type(traits) is not BirthTemperament:
        raise ValueError("exact spatial birth and temperament required")
    if type(rows) not in (tuple, list):
        raise ValueError("ordered committed physical rows required")
    site, previous_seq = BORN_SITE, 0
    previous_after = None
    observed = []
    from i2.modules.native_body_contract import COSTS
    allowed = set(COSTS) | {"boire_decouverte", "NO_ACTION"} | set(
        "se_deplacer_vers_" + destination_name for destination_name in GRAPH)
    for entry in rows:
        if not isinstance(entry, (tuple, list)) or len(entry) != 7:
            raise ValueError("complete canonical native physical row required")
        seq, capture, action, net_relief, before_json, after_json, found = entry
        if (type(seq) is not int or seq != previous_seq + 1 or
                type(capture) is not str or not capture or
                type(action) is not str or action not in allowed or
                type(net_relief) not in (int, float) or
                type(found) not in (int, bool) or int(found) not in (0, 1)):
            raise ValueError("invalid ordered committed physical evidence")
        before, after = saved_body(before_json), saved_body(after_json)
        if previous_after is not None and before != previous_after:
            raise ValueError("noncontinuous native bodily consequence")
        previous_seq, previous_after = seq, after
        motion = destination(action)
        if motion is not None:
            if not enabled:
                raise ValueError("movement in nonspatial birth")
            site = site_after(site, action)
            continue
        if action not in LIVED_BODY_ACTIONS or not enabled:
            continue
        prior_need = assess_needs(before, traits)
        before_values = tuple(float(getattr(before, k)) for k in CHANNELS)
        after_values = tuple(float(getattr(after, k)) for k in CHANNELS)
        observed.append(LivedWholeBodySiteConsequence(
            sequence=seq, site=site, action=action,
            before=before_values, after=after_values,
            deltas=tuple(a - b for a, b in zip(after_values, before_values)),
            prior_pressures=tuple(prior_need.pressures[k] for k in CHANNELS),
        ))
    return tuple(observed)
