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
