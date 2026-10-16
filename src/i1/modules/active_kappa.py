"""Stage-8 active reliability, DC-06. Consolidated kappa is Stage 10 only.

Metacognition and Health is the sole writer. Each cycle reads a frozen
published version; verification batches are committed at phase 5.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Mapping

from i0.config.contracts import MVP_SIGNAL_FAMILIES
from lab.determinism import deterministic_id

if TYPE_CHECKING:
    from i0.modules.action_control import AgencyComparison


@dataclass(frozen=True, slots=True)
class KappaConfig:
    version: str
    classes: int
    prior_strength: float
    equipment_priors: Mapping[str, float]

    def validate(self) -> None:
        if not self.version or self.classes < 1 or self.prior_strength <= 0:
            raise ValueError("invalid P-33 kappa configuration")
        for key, value in self.equipment_priors.items():
            if not key or not 0 <= value <= 1:
                raise ValueError("invalid offline equipment calibration prior")


@dataclass(frozen=True, slots=True)
class KappaVerification:
    identifier: str
    equipment_or_module_version: str
    module: str
    contribution_type: str
    signal_family: str
    declared_confidence: float
    emission_step: int
    observation_step: int
    outcome: str
    observation_anchor: str
    independent_family: str | None
    physical_consequence: bool
    provenance_independent: bool
    oracle_derived: bool = False
    rollback_cancelled: bool = False
    observation_ref: str | None = None

    def validate(self) -> None:
        if not self.identifier or not self.module or not self.equipment_or_module_version:
            raise ValueError("missing verification identity")
        if self.signal_family not in MVP_SIGNAL_FAMILIES:
            raise ValueError("unknown DC-06 signal family")
        if self.independent_family is not None and self.independent_family not in MVP_SIGNAL_FAMILIES:
            raise ValueError("unknown independent signal family")
        if not 0 <= self.declared_confidence <= 1:
            raise ValueError("declared confidence outside [0,1]")
        if self.outcome not in {"confirmee", "contredite", "indeterminee", "non_verifiable", "contrefactuelle_non_verifiee", "stabilite_meme_canal"}:
            raise ValueError("unknown verification outcome")
        # INV-03/INV-27: forbidden-origin bytes may not enter pending causal
        # verifications (or later appear in seen IDs / causal snapshots).
        if self.oracle_derived or self.rollback_cancelled:
            raise ValueError("oracle and lethal-rollback verifications are inadmissible")

    @property
    def strong(self) -> bool:
        return (
            self.observation_anchor == "monde"
            and bool(self.observation_ref)
            and self.observation_step > self.emission_step
            and self.provenance_independent
            and not self.oracle_derived
            and not self.rollback_cancelled
            and (
                self.physical_consequence
                or (self.independent_family is not None and self.independent_family != self.signal_family)
            )
        )

    @property
    def key(self) -> tuple[str, str, str, str]:
        return self.equipment_or_module_version, self.module, self.contribution_type, self.signal_family


def physical_verifications_from_comparison(
    *, comparison: "AgencyComparison", equipment_version: str
) -> tuple[KappaVerification, ...]:
    """DC-06: typed independent consequences from Action Control's comparison.

    Shared by the living Stage-8 runtime and Lab's external calibration probe.
    The comparator observes a later Perception capture. This transformer
    never reads the world, bench labels, oracle, or self-confirming signals.
    """
    if not equipment_version:
        raise ValueError("comparison equipment version is mandatory")
    results: list[KappaVerification] = []
    for index, effect in enumerate(comparison.effects):
        status = effect.get("status")
        if status not in {"conforming", "nonconforming"}:
            continue
        if effect.get("observed") is None or effect.get("predicted") is None:
            continue
        variable = str(effect.get("variable"))
        verification = KappaVerification(
            identifier=deterministic_id(
                "kappa-verification-v1",
                equipment_version,
                comparison.option_ref,
                comparison.sent_t_monde,
                comparison.observed_t_monde,
                index,
            ),
            equipment_or_module_version=equipment_version,
            module="simulator",
            contribution_type="prediction",
            signal_family="equipment_predictor",
            declared_confidence=1.0,
            emission_step=comparison.sent_t_monde,
            observation_step=comparison.observed_t_monde,
            outcome="confirmee" if status == "conforming" else "contredite",
            observation_anchor="monde",
            observation_ref=(
                f"physical-capture:{comparison.observed_t_monde}:{variable}"
            ),
            independent_family=(
                "world_symbolic"
                if variable in {"position_x", "position_y"}
                else "body_telemetry"
            ),
            physical_consequence=True,
            provenance_independent=True,
        )
        verification.validate()
        results.append(verification)
    return tuple(results)


class ActiveKappa:
    """Versioned active beta counters; no writes to consolidated kappa."""

    def __init__(self, config: KappaConfig) -> None:
        config.validate()
        self.config = config
        self.owner_id = "metacognition_health"
        self._counters: dict[tuple[str, str, str, str, int], tuple[float, float]] = {}
        self._pending: list[KappaVerification] = []
        self._version = 0
        self._seen: set[str] = set()
        self._credited_observations: set[tuple[str, str, str, str, str]] = set()

    @property
    def version(self) -> int:
        return self._version

    def _bucket(self, confidence: float) -> int:
        if not 0 <= confidence <= 1:
            raise ValueError("confidence outside [0,1]")
        return min(self.config.classes - 1, int(confidence * self.config.classes))

    def _prior(self, key: tuple[str, str, str, str]) -> tuple[float, float]:
        f0 = self.config.equipment_priors.get(key[0], 0.5)
        return self.config.prior_strength * f0, self.config.prior_strength * (1 - f0)

    def reliability(self, *, version: str, module: str, contribution_type: str, family: str, confidence: float) -> float:
        if family not in MVP_SIGNAL_FAMILIES:
            raise ValueError("unknown DC-06 signal family")
        key = (version, module, contribution_type, family)
        a, b = self._counters.get((*key, self._bucket(confidence)), self._prior(key))
        return a / (a + b)

    def integrate(self, verification: KappaVerification) -> None:
        verification.validate()
        if verification.identifier in self._seen or any(v.identifier == verification.identifier for v in self._pending):
            raise ValueError("duplicate verification identifier")
        self._pending.append(verification)

    def publish(self) -> tuple[tuple[KappaVerification, float, float], ...]:
        updates = []
        for v in sorted(self._pending, key=lambda v: (v.module, v.contribution_type, v.signal_family, v.identifier)):
            self._seen.add(v.identifier)
            if not v.strong or v.outcome not in {"confirmee", "contredite"}:
                continue
            observation_key = (*v.key, str(v.observation_ref))
            if observation_key in self._credited_observations:
                continue  # DC-06: one physical consequence cannot train twice
            self._credited_observations.add(observation_key)
            key = (*v.key, self._bucket(v.declared_confidence))
            a, b = self._counters.get(key, self._prior(v.key))
            old = a / (a + b)
            if v.outcome == "confirmee":
                a += 1
            else:
                b += 1
            self._counters[key] = a, b
            updates.append((v, old, a / (a + b)))
        self._pending.clear()
        self._version += 1
        return tuple(updates)

    def export_causal_state(self) -> object:
        return {
            "config_version": self.config.version, "version": self._version,
            "counters": [
                {"key": list(key), "a": a, "b": b}
                for key, (a, b) in sorted(self._counters.items())
            ],
            "pending": [dict(v.__dict__) if hasattr(v, "__dict__") else {
                name: getattr(v, name) for name in v.__dataclass_fields__
            } for v in self._pending],
            "seen": sorted(self._seen),
            "credited_observations": [list(row) for row in sorted(self._credited_observations)],
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping) or state.get("config_version") != self.config.version:
            raise ValueError("kappa snapshot configuration mismatch")
        counters = {}
        for row in state["counters"]:
            key = tuple(row["key"])
            if len(key) != 5 or key[3] not in MVP_SIGNAL_FAMILIES or not 0 <= key[4] < self.config.classes:
                raise ValueError("invalid kappa snapshot key")
            a, b = float(row["a"]), float(row["b"])
            if a < 0 or b < 0 or a + b <= 0:
                raise ValueError("invalid kappa posterior")
            counters[key] = (a, b)
        pending = [KappaVerification(**v) for v in state["pending"]]
        for v in pending:
            v.validate()
        self._counters = counters
        self._pending = pending
        credited = set()
        for row in state.get("credited_observations", ()):
            if len(row) != 5 or row[3] not in MVP_SIGNAL_FAMILIES or not row[4]:
                raise ValueError("invalid physical observation credit")
            credited.add(tuple(row))
        self._credited_observations = credited
        self._seen = set(state["seen"])
        self._version = int(state["version"])

    @property
    def consolidated_birth_form(self) -> Mapping[str, object]:
        return {}
