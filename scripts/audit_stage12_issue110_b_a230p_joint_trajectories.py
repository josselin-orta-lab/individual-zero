"""A2.30-P: an EXTERNAL laboratory model of observed joint trajectories.

Not an EquipmentModel, no predict() method, no next SimulationState, no
commands chosen, no claims of safety or probabilities. Accepts only initial
first-person SimulationState and a fixed command prefix. Observed branches are
never asserted exhaustive; unobserved hidden worlds remain possible.

Physical outcome is *never* read by predict/forecast. It is consumed only by
the offline training constructor and independently held-out evaluation.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Mapping, Sequence

from i0.equipment import SimulationState
from i0.interfaces import PrimitiveCommand
from lab.determinism import canonical_causal_bytes, sha256_hex
from audit_stage12_issue110_b_a230n_uncertain_predictor import (
    DELTA_FIELDS, observable_context,
)

_TERMINAL_STEPS = (1, 2, 3)
_VALID_LABELS = frozenset({
    "observed_terminal_possible", "observed_harm_possible",
    "unknown_hidden_risk", "unavailable",
})


def prefix_key(initial: SimulationState,
               commands: tuple[PrimitiveCommand, ...]) -> str:
    if len(commands) != 3:
        raise ValueError("this P experiment commits to exactly three commands")
    return sha256_hex(canonical_causal_bytes({
        "initial_observable_context": observable_context(
            initial, commands[0]
        ),
        "exact_committed_prefix": [c.as_dict() for c in commands],
    }))


def cumulative_observable_deltas(initial: SimulationState,
                                 observed: SimulationState) -> dict[str, float]:
    """11 visible DELTAS from one baseline, not a fabricated next state."""
    delta = {
        "dx": float(observed.x - initial.x),
        "dy": float(observed.y - initial.y),
    }
    for field in ("energy", "food", "water", "integrity"):
        delta["body." + field] = (
            float(observed.body[field]) - float(initial.body[field])
        )
    for field in ("berry_a", "berry_b", "wood", "stone", "tool"):
        delta["inventory." + field] = float(
            observed.inventory.get(field, 0) -
            initial.inventory.get(field, 0)
        )
    if set(delta) != set(DELTA_FIELDS):
        raise AssertionError("observable delta schema mismatch")
    return delta


@dataclass(frozen=True, slots=True)
class JointStep:
    """True measured joint delta and terminal flag, never a guess."""
    cumulative_delta: Mapping[str, float]
    terminal: bool

    def validate(self) -> None:
        if set(self.cumulative_delta) != set(DELTA_FIELDS):
            raise ValueError("missing a bodily or spatial dimension")
        if not all(
            isinstance(v, (int, float)) and abs(float(v)) < 100000
            for v in self.cumulative_delta.values()
        ):
            raise ValueError("nonfinite/sentinel physical delta")

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "cumulative_delta": {
                k: float(self.cumulative_delta[k]) for k in DELTA_FIELDS
            },
            "terminal": self.terminal,
        }


@dataclass(frozen=True, slots=True)
class PhysicalPrefixWitness:
    world_id: str
    initial: SimulationState
    commands: tuple[PrimitiveCommand, ...]
    steps: tuple[JointStep, ...]

    def validate(self) -> None:
        if not self.world_id or len(self.commands) != 3:
            raise ValueError("physical trajectory needs ID and 3-command prefix")
        self.initial.validate()
        if not (1 <= len(self.steps) <= 3):
            raise ValueError("physical trajectory length outside prefix")
        for step in self.steps:
            step.validate()
        terminals = [i+1 for i,s in enumerate(self.steps) if s.terminal]
        if terminals and (len(terminals)!=1 or terminals[0]!=len(self.steps)):
            raise ValueError("no physically continued postterminal trajectory")
        if not terminals and len(self.steps)!=3:
            raise ValueError("nonterminal trajectory was truncated")

    @property
    def first_terminal_step(self) -> int | None:
        for i,step in enumerate(self.steps, 1):
            if step.terminal:
                return i
        return None

    @property
    def had_observed_harm(self) -> bool:
        return self.first_terminal_step is not None or any(
            float(step.cumulative_delta["body.integrity"]) < -1e-8
            for step in self.steps
        )

    def as_dict(self) -> dict[str, object]:
        self.validate()
        return {
            "world_id": self.world_id,
            "initial": self.initial.as_dict(),
            "commands": [c.as_dict() for c in self.commands],
            "steps": [s.as_dict() for s in self.steps],
            "first_terminal_step": self.first_terminal_step,
            "had_observed_harm": self.had_observed_harm,
            "group_key": prefix_key(self.initial, self.commands),
        }


def _step_fingerprint(step: JointStep) -> dict[str, object]:
    """Precision fixed at 1e-8 solely to suppress float roundoff."""
    return {
        "terminal": step.terminal,
        "cumulative_delta": {
            k: round(float(step.cumulative_delta[k]), 8)
            for k in DELTA_FIELDS
        },
    }


def joint_signature(steps: tuple[JointStep, ...]) -> str:
    return sha256_hex(canonical_causal_bytes([
        _step_fingerprint(step) for step in steps
    ]))


@dataclass(frozen=True, slots=True)
class BranchRecord:
    fingerprint: str
    first_terminal_step: int | None
    physical_training_worlds: int
    observed_steps: tuple[dict[str, object], ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "fingerprint": self.fingerprint,
            "first_terminal_step": self.first_terminal_step,
            "physical_training_worlds": self.physical_training_worlds,
            "observed_steps": list(self.observed_steps),
        }


@dataclass(frozen=True, slots=True)
class JointForecast:
    status: str
    context_key: str
    evidence_worlds: int
    branches: tuple[BranchRecord, ...]
    risk_label: str
    observed_terminal_steps: tuple[int, ...]
    first_step_terminal_in_training: bool
    could_have_unobserved_hidden_hazard: bool = True
    certifies_safe: bool = False

    def validate(self) -> None:
        if self.status not in ("observed_joint_branches", "abstain_unknown_context"):
            raise AssertionError("invented forecast status")
        if self.risk_label not in _VALID_LABELS or self.certifies_safe:
            raise AssertionError("invented causal safety certificate")
        if not self.could_have_unobserved_hidden_hazard:
            raise AssertionError("physical outcomes treated as exhaustive")
        if self.status == "observed_joint_branches":
            if not self.branches or self.evidence_worlds <= 0:
                raise AssertionError("no physically observed branches")
            if sum(x.physical_training_worlds for x in self.branches) != self.evidence_worlds:
                raise AssertionError("branch support missing physical worlds")
            expected = tuple(sorted({
                b.first_terminal_step for b in self.branches
                if b.first_terminal_step is not None
            }))
            if expected != self.observed_terminal_steps:
                raise AssertionError("terminal times collapsed or invented")
        elif (self.branches or self.evidence_worlds or self.observed_terminal_steps
              or self.first_step_terminal_in_training
              or self.risk_label != "unavailable"):
            raise AssertionError("unknown context must abstain")


class LaboratoryJointPrefixModel:
    """Frozen witness catalogue: uses NO oracle or world for forecasting."""

    def __init__(self, witnesses: Sequence[PhysicalPrefixWitness]):
        if not witnesses:
            raise ValueError("physical witnessed prefixes required")
        distinct = set()
        grouped = defaultdict(list)
        for item in witnesses:
            item.validate()
            if item.world_id in distinct:
                raise ValueError("repeated training world")
            distinct.add(item.world_id)
            grouped[prefix_key(item.initial,item.commands)].append(item)
        self._groups: dict[str, JointForecast] = {}
        for key, witnessed in grouped.items():
            groups_by_trace = defaultdict(list)
            for item in witnessed:
                groups_by_trace[joint_signature(item.steps)].append(item)
            branches = []
            for fingerprint, examples in sorted(groups_by_trace.items()):
                first = examples[0]
                branches.append(BranchRecord(
                    fingerprint=fingerprint,
                    first_terminal_step=first.first_terminal_step,
                    physical_training_worlds=len(examples),
                    observed_steps=tuple(
                        _step_fingerprint(step) for step in first.steps
                    ),
                ))
            terminal_set=tuple(sorted({
                w.first_terminal_step for w in witnessed
                if w.first_terminal_step is not None
            }))
            label = (
                "observed_terminal_possible" if terminal_set else
                "observed_harm_possible" if any(
                    w.had_observed_harm for w in witnessed
                ) else "unknown_hidden_risk"
            )
            model = JointForecast(
                status="observed_joint_branches", context_key=key,
                evidence_worlds=len(witnessed), branches=tuple(branches),
                risk_label=label, observed_terminal_steps=terminal_set,
                first_step_terminal_in_training=any(
                    w.first_terminal_step==1 for w in witnessed
                ),
            )
            model.validate()
            self._groups[key] = model
        self.version="lab-a230p-joint-prefix-v1"
        self.training_worlds=len(distinct)
        self.contexts=len(self._groups)

    def forecast(self, *, initial: SimulationState,
                 commands: tuple[PrimitiveCommand,...]) -> JointForecast:
        key = prefix_key(initial,commands)
        known=self._groups.get(key)
        if known is not None:
            return known
        empty=JointForecast(
            status="abstain_unknown_context", context_key=key,
            evidence_worlds=0, branches=(), risk_label="unavailable",
            observed_terminal_steps=(),
            first_step_terminal_in_training=False,
        )
        empty.validate()
        return empty


def score_heldout(pred: JointForecast, actual: PhysicalPrefixWitness) -> dict[str,object]:
    pred.validate()
    actual.validate()
    if prefix_key(actual.initial,actual.commands)!=pred.context_key:
        raise ValueError("forecast and physical root differ")
    if pred.status=="abstain_unknown_context":
        return {
            "covered":False, "joint_branch_witnessed":None,
            "first_terminal_step":actual.first_terminal_step,
            "terminal_step_in_empirical_set":None,
            "novel_joint_branch":None, "observed_possible_late_terminal":False,
        }
    matched=joint_signature(actual.steps) in {
        br.fingerprint for br in pred.branches
    }
    return {
        "covered":True, "joint_branch_witnessed":matched,
        "first_terminal_step":actual.first_terminal_step,
        "terminal_step_in_empirical_set":(
            actual.first_terminal_step in pred.observed_terminal_steps
            if actual.first_terminal_step is not None else
            any(b.first_terminal_step is None for b in pred.branches)
        ),
        "novel_joint_branch":not matched,
        "observed_possible_late_terminal":any(
            t > 1 for t in pred.observed_terminal_steps
        ),
    }
