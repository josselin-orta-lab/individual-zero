"""Minimal normative Stage-4 Gatekeeper.

Stage 4 uses fixed weights and f=1. Novelty is an exact-symbolic stub:
a subject is novel only when absent from the currently retained/queued pool
and the recent subject history. Stage 11 replaces this stub with the full
exploration/novelty mechanism without changing this interface.

Spec: 6.3-6.6, DC-04, 20.3 Stage 4.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from i0.contracts import Contribution, Goal, STElement
from i0.serde import decode_contribution, encode_contribution


@dataclass(frozen=True, slots=True)
class GatekeeperConfig:
    version: str
    k_slots: int
    recency_window_steps: int
    replacement_hysteresis: float
    safety_threshold: float
    queue_capacity: int
    emission_quota: int
    slot_quota: int
    quota_window_steps: int
    weights: Mapping[str, float]

    def validate(self) -> None:
        if not self.version:
            raise ValueError("Gatekeeper config version must not be empty")
        if self.k_slots < 1:
            raise ValueError("K must be >= 1")
        if self.recency_window_steps < 1:
            raise ValueError("W must be >= 1")
        if self.replacement_hysteresis < 0:
            raise ValueError("Delta_hyst must be non-negative")
        if not 0.0 < self.safety_threshold <= 1.0:
            raise ValueError("s_sec must lie in ]0,1]")
        for name in ("b", "n", "urg", "risk", "value"):
            if name not in self.weights or self.weights[name] < 0:
                raise ValueError(f"missing/non-negative weight required: {name}")
        if self.queue_capacity < 1:
            raise ValueError("queue capacity must be >= 1")
        if self.emission_quota < 1:
            raise ValueError("emission quota must be >= 1")
        if self.slot_quota < 1:
            raise ValueError("slot quota must be >= 1")
        if self.quota_window_steps < 1:
            raise ValueError("quota window must be >= 1")


@dataclass(frozen=True, slots=True)
class GatekeeperFeedback:
    contribution_ref: str
    status: str
    score: float | None
    reason: str | None = None


@dataclass(frozen=True, slots=True)
class GatekeeperSelection:
    elements: tuple[STElement, ...]
    feedback: tuple[GatekeeperFeedback, ...]


@dataclass(slots=True)
class _Scored:
    contribution: Contribution
    score: float
    decomposition: dict[str, float]
    novelty: float
    occupant: bool


class Gatekeeper:
    owner_id = "gatekeeper"

    def __init__(self, config: GatekeeperConfig) -> None:
        config.validate()
        self._config = config
        self._queue: dict[str, Contribution] = {}
        self._retained: dict[str, Contribution] = {}
        self._emissions: dict[str, list[int]] = {}
        self._recent_subjects: dict[str, int] = {}
        self._reliability: Callable[[Contribution], float] | None = None

    def attach_reliability(self, resolver: Callable[[Contribution], float]) -> None:
        if self._reliability is not None:
            raise ValueError('reliability resolver already attached')
        self._reliability = resolver

    @property
    def config(self) -> GatekeeperConfig:
        return self._config

    @staticmethod
    def _canonical(contribution: Contribution) -> tuple[str, str, str]:
        return (
            contribution.subject_ref,
            contribution.emitter_module,
            contribution.id,
        )

    def _trim_histories(self, *, t_monde: int) -> None:
        cutoff = t_monde - self._config.quota_window_steps + 1
        for module in list(self._emissions):
            self._emissions[module] = [
                step for step in self._emissions[module] if step >= cutoff
            ]
            if not self._emissions[module]:
                self._emissions.pop(module, None)

        subject_cutoff = t_monde - self._config.recency_window_steps + 1
        self._recent_subjects = {
            subject: step
            for subject, step in self._recent_subjects.items()
            if step >= subject_cutoff
        }

    def _admit_new(
        self,
        contributions: Sequence[Contribution],
        *,
        t_monde: int,
    ) -> tuple[list[Contribution], list[GatekeeperFeedback]]:
        admitted: list[Contribution] = []
        feedback: list[GatekeeperFeedback] = []

        for contribution in sorted(contributions, key=self._canonical):
            try:
                contribution.validate()
            except ValueError as exc:
                feedback.append(
                    GatekeeperFeedback(
                        contribution_ref=contribution.id,
                        status="rejected",
                        score=None,
                        reason=f"schema:{exc}",
                    )
                )
                continue

            if contribution.expires_at_step <= t_monde:
                feedback.append(
                    GatekeeperFeedback(
                        contribution_ref=contribution.id,
                        status="rejected",
                        score=None,
                        reason="expired",
                    )
                )
                continue

            history = self._emissions.setdefault(contribution.emitter_module, [])
            if len(history) >= self._config.emission_quota:
                feedback.append(
                    GatekeeperFeedback(
                        contribution_ref=contribution.id,
                        status="rejected",
                        score=None,
                        reason="quota_emission",
                    )
                )
                continue

            history.append(t_monde)
            admitted.append(contribution)

        return admitted, feedback

    def _effective_risk(self, contribution: Contribution) -> float:
        if self._reliability is None:
            return contribution.risk
        return contribution.risk * self._reliability(contribution)

    def _score(
        self,
        contribution: Contribution,
        *,
        active_goal: Goal | None,
        occupant: bool,
        subjects_present_before_new: set[str],
    ) -> _Scored:
        relevance = (
            1.0
            if active_goal is not None and contribution.goal_ref == active_goal.id
            else 0.0
        )
        novelty = (
            0.0
            if (
                contribution.subject_ref in subjects_present_before_new
                or contribution.subject_ref in self._recent_subjects
            )
            else 1.0
        )
        decomposition = {
            "b": relevance,
            "n": novelty,
            "urg": contribution.urgency,
            "risk": contribution.risk,
            "value": contribution.value,
        }
        score = sum(
            self._config.weights[name] * decomposition[name]
            for name in decomposition
        )
        if self._reliability is not None:
            score *= self._reliability(contribution)
        return _Scored(
            contribution=contribution,
            score=score,
            decomposition=decomposition,
            novelty=novelty,
            occupant=occupant,
        )

    def select(
        self,
        new_contributions: Sequence[Contribution],
        *,
        active_goal: Goal | None,
        t_monde: int,
    ) -> GatekeeperSelection:
        self._trim_histories(t_monde=t_monde)

        feedback: list[GatekeeperFeedback] = []
        existing: list[Contribution] = []
        for contribution in list(self._retained.values()) + list(self._queue.values()):
            if contribution.expires_at_step <= t_monde:
                feedback.append(
                    GatekeeperFeedback(
                        contribution_ref=contribution.id,
                        status="expired",
                        score=None,
                        reason="recency_or_validity",
                    )
                )
                continue
            existing.append(contribution)

        admitted, admission_feedback = self._admit_new(
            new_contributions,
            t_monde=t_monde,
        )
        feedback.extend(admission_feedback)

        # Exact-subject grouping: retain one contribution per exact subject.
        # Newer causal reobservations are allowed, but only the best scored version
        # of an exact subject occupies the current pool.
        subjects_before = {c.subject_ref for c in existing}
        scored: list[_Scored] = []
        for contribution in existing:
            scored.append(
                self._score(
                    contribution,
                    active_goal=active_goal,
                    occupant=contribution.id in self._retained,
                    subjects_present_before_new=subjects_before,
                )
            )
        for contribution in admitted:
            scored.append(
                self._score(
                    contribution,
                    active_goal=active_goal,
                    occupant=False,
                    subjects_present_before_new=subjects_before,
                )
            )

        by_subject: dict[str, _Scored] = {}
        for item in scored:
            current = by_subject.get(item.contribution.subject_ref)
            if current is None:
                by_subject[item.contribution.subject_ref] = item
                continue
            current_key = (
                current.score
                + (self._config.replacement_hysteresis if current.occupant else 0.0),
                current.contribution.production_t,
                tuple(reversed(self._canonical(current.contribution))),
            )
            item_key = (
                item.score
                + (self._config.replacement_hysteresis if item.occupant else 0.0),
                item.contribution.production_t,
                tuple(reversed(self._canonical(item.contribution))),
            )
            if item_key > current_key:
                by_subject[item.contribution.subject_ref] = item

        pool = list(by_subject.values())

        security = [
            item
            for item in pool
            if self._effective_risk(item.contribution) >= self._config.safety_threshold
        ]
        security.sort(
            key=lambda item: (
                -self._effective_risk(item.contribution),
                self._canonical(item.contribution),
            )
        )
        selected: list[_Scored] = security[:1]
        selected_ids = {item.contribution.id for item in selected}

        ordered = sorted(
            (item for item in pool if item.contribution.id not in selected_ids),
            key=lambda item: (
                -(item.score + (
                    self._config.replacement_hysteresis if item.occupant else 0.0
                )),
                0 if not item.occupant else 1,
                self._canonical(item.contribution),
            ),
        )

        module_counts: dict[str, int] = {}
        for item in selected:
            module_counts[item.contribution.emitter_module] = (
                module_counts.get(item.contribution.emitter_module, 0) + 1
            )

        for item in ordered:
            if len(selected) >= self._config.k_slots:
                break
            module = item.contribution.emitter_module
            if module_counts.get(module, 0) >= self._config.slot_quota:
                continue
            selected.append(item)
            selected_ids.add(item.contribution.id)
            module_counts[module] = module_counts.get(module, 0) + 1

        # Second pass fills otherwise-empty slots beyond diversity quota.
        for item in ordered:
            if len(selected) >= self._config.k_slots:
                break
            if item.contribution.id in selected_ids:
                continue
            selected.append(item)
            selected_ids.add(item.contribution.id)

        selected_map = {item.contribution.id: item for item in selected}
        queue_items = [
            item
            for item in pool
            if item.contribution.id not in selected_map
        ]
        queue_items.sort(
            key=lambda item: (
                -item.score,
                -item.contribution.production_t,
                self._canonical(item.contribution),
            )
        )
        kept_queue = queue_items[: self._config.queue_capacity]
        evicted_queue = queue_items[self._config.queue_capacity :]

        self._retained = {
            item.contribution.id: item.contribution
            for item in selected
        }
        self._queue = {
            item.contribution.id: item.contribution
            for item in kept_queue
        }

        for item in selected:
            self._recent_subjects[item.contribution.subject_ref] = t_monde
            feedback.append(
                GatekeeperFeedback(
                    contribution_ref=item.contribution.id,
                    status="retained",
                    score=item.score,
                )
            )
        for item in kept_queue:
            self._recent_subjects[item.contribution.subject_ref] = t_monde
            feedback.append(
                GatekeeperFeedback(
                    contribution_ref=item.contribution.id,
                    status="queued",
                    score=item.score,
                )
            )
        for item in evicted_queue:
            feedback.append(
                GatekeeperFeedback(
                    contribution_ref=item.contribution.id,
                    status="evicted",
                    score=item.score,
                    reason="queue_capacity",
                )
            )

        elements = tuple(
            STElement(
                contribution_ref=item.contribution.id,
                summary=item.contribution.summary,
                score=item.score,
                decomposition=dict(item.decomposition),
                reliability=(1.0 if self._reliability is None else self._reliability(item.contribution)),
                production_t=item.contribution.production_t,
                expires_at_step=item.contribution.expires_at_step,
                preempted=(
                    bool(selected)
                    and item.contribution.id == selected[0].contribution.id
                    and self._effective_risk(item.contribution) >= self._config.safety_threshold
                ),
            )
            for item in selected
        )
        return GatekeeperSelection(
            elements=elements,
            feedback=tuple(feedback),
        )

    def export_causal_state(self) -> object:
        return {
            "config_version": self._config.version,
            "retained": [
                encode_contribution(self._retained[key])
                for key in sorted(self._retained)
            ],
            "queue": [
                encode_contribution(self._queue[key])
                for key in sorted(self._queue)
            ],
            "emissions": {
                key: list(value)
                for key, value in sorted(self._emissions.items())
            },
            "recent_subjects": dict(sorted(self._recent_subjects.items())),
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("Gatekeeper state must be a mapping")
        if state.get("config_version") != self._config.version:
            raise ValueError("Gatekeeper config version mismatch")
        retained = state.get("retained")
        queue = state.get("queue")
        emissions = state.get("emissions")
        recent = state.get("recent_subjects")
        if not isinstance(retained, list) or not isinstance(queue, list):
            raise ValueError("invalid Gatekeeper retained/queue state")
        if not isinstance(emissions, Mapping) or not isinstance(recent, Mapping):
            raise ValueError("invalid Gatekeeper history state")
        self._retained = {}
        for raw in retained:
            if not isinstance(raw, Mapping):
                raise ValueError("invalid retained contribution")
            c = decode_contribution(raw)
            self._retained[c.id] = c
        self._queue = {}
        for raw in queue:
            if not isinstance(raw, Mapping):
                raise ValueError("invalid queued contribution")
            c = decode_contribution(raw)
            self._queue[c.id] = c
        self._emissions = {
            str(module): [int(step) for step in steps]
            for module, steps in emissions.items()
        }
        self._recent_subjects = {
            str(subject): int(step)
            for subject, step in recent.items()
        }
