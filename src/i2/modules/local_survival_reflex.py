"""Owner-local I2 energy survival reflex for the bounded research world.

The sole source of the energy value MUST be the audited I2 SQLite WorldBody
predecision state. This adapter never reads hidden food phases, grants an
action, charges UC, or claims independent M11 authentication. It is a
researcher-defined danger classifier and last-resort *priority signal*,
not learned physiology, action admission or knowledge of food safety.
"""
from __future__ import annotations

from dataclasses import dataclass

from .intention_ingress import ObservationClaim
from .unstable_world_reappraisal_contract import SurvivalReflexSnapshot

# Mechanistic local bounds for a world where an admitted action costs 2
# energy units and metabolism costs 1 per physical tick. These are NOT
# fitted survival thresholds and do not imply any food payoff knowledge.
IMMEDIATE_DANGER_ENERGY = 2
LOW_RESERVE_ENERGY = 4
MAX_WORLD_ENERGY = 100

# Only EAT can possibly increase energy in this bounded world. COLLECT
# consumes energy to acquire food; DRINK has no energy benefit. This is
# transparent toy-world action semantics, NOT a discovered general plan.
COLLECT_SEMANTIC = "affordance:collect:berry_a"
EAT_SEMANTIC = "affordance:eat:berry_a"
DRINK_SEMANTIC = "affordance:drink:water"
KNOWN_SEMANTICS = frozenset({COLLECT_SEMANTIC, EAT_SEMANTIC, DRINK_SEMANTIC})


@dataclass(frozen=True, slots=True)
class LocalEnergySurvivalReflex:
    """Capture-bound source, instantiated ONLY from the audited world owner.

    The current observation already carries the body's energy evidence ref.
    Reuse that ref so the closed historical study's claim bytes, score and
    world events stay unchanged. The verifier checks exact claim identity
    and report equality, not only a plausible string or matching capture.
    """

    claim: ObservationClaim
    committed_energy: int

    def __post_init__(self) -> None:
        if type(self.claim) is not ObservationClaim:
            raise ValueError("exact current I2 observation required")
        self.claim.validate()
        if (type(self.committed_energy) is not int or
                not 1 <= self.committed_energy <= MAX_WORLD_ENERGY):
            raise ValueError("refuse unknown, terminal or invalid energy")
        if self.evidence_ref not in self.claim.subjective_evidence_refs:
            raise ValueError("energy is not bound to the current observation")

    @property
    def evidence_ref(self) -> str:
        return f"evidence:i2:energy:{self.committed_energy}"

    @property
    def state(self) -> str:
        if self.committed_energy <= IMMEDIATE_DANGER_ENERGY:
            return "PREEMPT"
        if self.committed_energy <= LOW_RESERVE_ENERGY:
            return "CONSTRAIN"
        return "NO_PREEMPTION"

    def last_resort_food_priority(self) -> str | None:
        """Nonmotor priority for a risky *available* meal in critical scarcity.

        The existing world models no alternative immediate energy-restoring
        action. Unknown future affordances are NOT assumed inferior. A bad
        personal food memory cannot prove the next meal is harmful, but the
        reflex cannot foresee recovery either. Paid Competition and normal
        fresh Action Control remain mandatory before any internal effect.
        """
        accessible = frozenset(self.claim.capture.accessible_semantics)
        if (self.state not in ("PREEMPT", "CONSTRAIN") or
                not accessible.issubset(KNOWN_SEMANTICS) or
                EAT_SEMANTIC not in accessible):
            return None
        return EAT_SEMANTIC

    def snapshot(self) -> SurvivalReflexSnapshot:
        return SurvivalReflexSnapshot(
            self.claim.life_ref,
            self.claim.capture.ref,
            self.claim.digest(),
            self.evidence_ref,
            self.state,
        )

    def verify_survival_reflex(
        self, *, claim: ObservationClaim, snapshot: SurvivalReflexSnapshot,
    ) -> bool:
        # This is local consistency, NOT an independent tamper-proof source.
        return (
            type(claim) is ObservationClaim
            and type(snapshot) is SurvivalReflexSnapshot
            and claim == self.claim
            and snapshot == self.snapshot()
        )
