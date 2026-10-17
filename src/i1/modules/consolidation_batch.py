"""Stage-10 deterministic *input batch selection* from lived Memory episodes.

MVP 15.6 / P-42: this is a proposed versioned policy for selection before the
private six-pass transaction opens, not semantic replay or consolidated h.
It consumes only Memory's autobiographical Episode.as_dict() projection and
an explicit pending-ID ledger supplied by the slow-history owner. It cannot
consult WorldBody, the Lab oracle, or the technical journal. The caller must
reserve the quoted UC with the budget owner before executing selection.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from heapq import nsmallest
from math import isfinite
from typing import Protocol, Sequence, Mapping

from lab.determinism import canonical_causal_bytes, sha256_hex
from .consolidation_transaction import ConsolidationCut


class EpisodeProjection(Protocol):
    def as_dict(self) -> dict[str, object]: ...


def _finite_positive(value: object) -> bool:
    return type(value) in (int, float) and isfinite(value) and value > 0


def _finite_nonnegative(value: object) -> bool:
    return type(value) in (int, float) and isfinite(value) and value >= 0


@dataclass(frozen=True, slots=True)
class BatchSelectionPolicy:
    """Injected P-42 coefficients. No campaign values are silently chosen."""

    version: str
    maximum_episodes: int
    consequence_reference: float
    surprise_reference: float
    recency_window_steps: int
    repetition_reference: int
    weight_consequence: float
    weight_surprise: float
    weight_recency: float
    weight_repetition: float
    ageing_gain_per_step: float
    scan_uc_per_episode: int

    def validate(self) -> None:
        if not isinstance(self.version, str) or not self.version.strip():
            raise ValueError("versioned P-42 selection policy required")
        for value in (self.maximum_episodes, self.recency_window_steps,
                      self.repetition_reference, self.scan_uc_per_episode):
            if type(value) is not int or value < 1:
                raise ValueError("positive integral batch bounds and scan cost required")
        if not all(_finite_positive(value) for value in (
            self.consequence_reference, self.surprise_reference,
            self.ageing_gain_per_step,
        )):
            raise ValueError("positive finite normalizers and ageing rate required")
        if not all(_finite_nonnegative(value) for value in (
            self.weight_consequence, self.weight_surprise,
            self.weight_recency, self.weight_repetition,
        )):
            raise ValueError("selection weights must be finite nonnegative")


@dataclass(frozen=True, slots=True)
class EpisodePriority:
    episode_ref: str
    score: float
    age_steps: int
    consequence: float
    surprise: float
    recency: float
    repetition: float


class FrozenBatchSelection:
    """Detached deterministic receipt, not a second episodic-memory owner."""

    def __init__(self, *, cut: ConsolidationCut, policy_version: str,
                 priorities: tuple[EpisodePriority, ...],
                 episode_payloads: Mapping[str, object], scan_uc: int):
        if scan_uc < 0:
            raise ValueError("negative quoted UC")
        self.cut = cut
        self.policy_version = policy_version
        self._priorities = priorities
        self._payloads = deepcopy(dict(episode_payloads))
        self.scan_uc = scan_uc
        self.digest = sha256_hex(canonical_causal_bytes({
            "cut": cut.as_dict(), "policy": policy_version,
            "priorities": [
                {"id": item.episode_ref, "score": item.score,
                 "age_steps": item.age_steps} for item in priorities
            ],
            "episodes": self._payloads,
            "quoted_scan_uc": scan_uc,
        }))

    @property
    def episode_refs(self) -> tuple[str, ...]:
        return tuple(item.episode_ref for item in self._priorities)

    @property
    def priorities(self) -> tuple[EpisodePriority, ...]:
        return self._priorities

    def episode_payloads_copy(self) -> dict[str, object]:
        return deepcopy(self._payloads)


class BatchSelectionBudgetError(ValueError):
    """No partial selection is published when the scan UC is unavailable."""


class ConsolidationBatchSelector:
    """P-42 ranked, starvation-resistant selection of pre-cut episodes.

    All non-age terms are bounded to [0,1]. A strictly positive unbounded age
    term ensures that an unselected relevant episode eventually outranks later
    arrivals under a finite older backlog. Exact shared goal identity is only
    *contextual repetition*, not evidence of causal success or compiled skill.
    """

    _fields = frozenset({
        "id", "start_t_monde", "end_t_monde", "event_refs", "boundary_type",
        "active_goal_ref", "body_start", "body_end", "cumulative_reward",
        "surprise", "linked_previous_ref",
    })

    def __init__(self, policy: BatchSelectionPolicy):
        policy.validate()
        self.policy = policy

    def quote_scan_uc(self, *, examined_episode_count: int) -> int:
        if type(examined_episode_count) is not int or examined_episode_count < 0:
            raise ValueError("examined episode count must be nonnegative")
        return examined_episode_count * self.policy.scan_uc_per_episode

    @staticmethod
    def _projection(raw: EpisodeProjection) -> dict[str, object]:
        if not callable(getattr(raw, "as_dict", None)):
            raise ValueError("only an autobiographical Episode.as_dict projection is accepted")
        payload = raw.as_dict()
        if type(payload) is not dict or set(payload) != ConsolidationBatchSelector._fields:
            raise ValueError("unexpected episodic projection schema")
        canonical_causal_bytes(payload)
        return deepcopy(payload)

    def select(self, *, cut: ConsolidationCut,
               episodes: Sequence[EpisodeProjection],
               pending_episode_refs: tuple[str, ...],
               reserved_scan_uc: int) -> FrozenBatchSelection:
        cut.validate()
        if type(pending_episode_refs) is not tuple or any(
            type(ref) is not str or not ref for ref in pending_episode_refs
        ) or len(set(pending_episode_refs)) != len(pending_episode_refs):
            raise ValueError("pending IDs must be unique and explicit")
        required_uc = self.quote_scan_uc(examined_episode_count=len(episodes))
        if type(reserved_scan_uc) is not int or reserved_scan_uc < required_uc:
            raise BatchSelectionBudgetError("P-42 scanning all provided episodes requires prior UC reservation")
        # The caller's reservation is not the ledger debit. The budget owner
        # must actually charge required_uc before invoking this method.
        pending = set(pending_episode_refs)
        candidates: dict[str, dict[str, object]] = {}
        seen_ids: set[str] = set()
        for episode in episodes:
            payload = self._projection(episode)
            ref = payload["id"]
            if type(ref) is not str or not ref or ref in seen_ids:
                raise ValueError("duplicate or invalid episode identity")
            seen_ids.add(ref)
            if ref not in pending:
                continue
            start, end = payload["start_t_monde"], payload["end_t_monde"]
            if (type(start) is not int or type(end) is not int or
                    start < 0 or end < start or end >= cut.world_step):
                raise ValueError("pending episodes must close before the causal cut")
            if (type(payload["event_refs"]) is not list or
                    not payload["event_refs"] or any(
                        type(item) is not str or not item for item in payload["event_refs"]
                    )):
                raise ValueError("pending episode must have lived event references")
            if (not _finite_nonnegative(payload["surprise"]) or
                    type(payload["cumulative_reward"]) not in (int, float) or
                    not isfinite(payload["cumulative_reward"])):
                raise ValueError("invalid lived surprise or reward")
            goal = payload["active_goal_ref"]
            if goal is not None and (type(goal) is not str or not goal):
                raise ValueError("invalid observed goal reference")
            candidates[ref] = payload
        if set(candidates) != pending:
            raise ValueError("missing pending episode data")

        group_counts: dict[str, int] = {}
        for payload in candidates.values():
            goal = payload["active_goal_ref"]
            if goal is not None:
                group_counts[goal] = group_counts.get(goal, 0) + 1
        priorities: list[EpisodePriority] = []
        cfg = self.policy
        for ref, payload in candidates.items():
            age = cut.world_step - payload["end_t_monde"]
            reward = min(1.0, abs(payload["cumulative_reward"]) / cfg.consequence_reference)
            surprise = min(1.0, payload["surprise"] / cfg.surprise_reference)
            recency = max(0.0, 1.0 - age / cfg.recency_window_steps)
            goal = payload["active_goal_ref"]
            repetition = (0.0 if goal is None else min(
                1.0, (group_counts[goal] - 1) / cfg.repetition_reference
            ))
            score = (
                cfg.weight_consequence * reward + cfg.weight_surprise * surprise +
                cfg.weight_recency * recency + cfg.weight_repetition * repetition +
                cfg.ageing_gain_per_step * age
            )
            if not isfinite(score):
                raise ValueError("nonfinite policy score")
            priorities.append(EpisodePriority(
                ref, score, age, reward, surprise, recency, repetition,
            ))
        # Full scores are still paid, computed and validated. Only the
        # policy-bounded best group is sorted at the end.
        selected = tuple(nsmallest(
            cfg.maximum_episodes, priorities,
            key=lambda item: (-item.score, -item.age_steps, item.episode_ref),
        ))
        return FrozenBatchSelection(
            cut=cut, policy_version=cfg.version, priorities=selected,
            episode_payloads={item.episode_ref: candidates[item.episode_ref] for item in selected},
            scan_uc=required_uc,
        )
