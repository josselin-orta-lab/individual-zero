"""Stage-7 episodic memory and exact recall.

Memory receives only the DC-09 autobiographical projection from its runtime
adapter. It never imports or reads the technical journal or evaluation trace.

Spec: 10.1-10.4, 20.3 Stage 7, P-34, DC-09, INV-02, INV-27.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from i0.contracts import Contribution, GoalProposal, STVersion


@dataclass(frozen=True, slots=True)
class MemoryConfig:
    version: str
    prediction_error_multiplier: float
    max_episode_steps: int
    link_delta_steps: int
    recall_threshold: float
    recall_weight_recency: float
    recall_weight_importance: float
    recall_weight_relevance: float
    recall_recency_scale_steps: int
    contribution_ttl_steps: int

    def validate(self) -> None:
        if not self.version:
            raise ValueError("memory config version must not be empty")
        if self.prediction_error_multiplier < 0:
            raise ValueError("k_episode must be non-negative")
        if self.max_episode_steps < 1:
            raise ValueError("L_episode must be >= 1")
        if self.link_delta_steps < 0:
            raise ValueError("Delta_episode must be non-negative")
        if self.recall_recency_scale_steps < 1:
            raise ValueError("recall recency scale must be >= 1")
        if self.contribution_ttl_steps < 1:
            raise ValueError("memory contribution TTL must be >= 1")
        for name, value in (
            ("recall_threshold", self.recall_threshold),
            ("recall_weight_recency", self.recall_weight_recency),
            ("recall_weight_importance", self.recall_weight_importance),
            ("recall_weight_relevance", self.recall_weight_relevance),
        ):
            if value < 0:
                raise ValueError(f"{name} must be non-negative")


@dataclass(frozen=True, slots=True)
class Episode:
    id: str
    start_t_monde: int
    end_t_monde: int
    event_refs: tuple[str, ...]
    boundary_type: str
    active_goal_ref: str | None
    body_start: Mapping[str, float] | None
    body_end: Mapping[str, float] | None
    cumulative_reward: float
    surprise: float
    linked_previous_ref: str | None

    @property
    def importance(self) -> float:
        return abs(self.cumulative_reward) + self.surprise

    def as_dict(self) -> dict[str, object]:
        return {
            "id": self.id,
            "start_t_monde": self.start_t_monde,
            "end_t_monde": self.end_t_monde,
            "event_refs": list(self.event_refs),
            "boundary_type": self.boundary_type,
            "active_goal_ref": self.active_goal_ref,
            "body_start": None if self.body_start is None else dict(self.body_start),
            "body_end": None if self.body_end is None else dict(self.body_end),
            "cumulative_reward": self.cumulative_reward,
            "surprise": self.surprise,
            "linked_previous_ref": self.linked_previous_ref,
        }


@dataclass(frozen=True, slots=True)
class Intention:
    id: str
    goal_type: str
    target: str
    trigger_type: str
    trigger_value: object
    deadline_step: int | None
    base_pressure: float
    monitoring: str
    cost_uc: int
    wake_authorized: bool
    state: str = "pending"
    candidacy_active: bool = False

    def validate(self) -> None:
        if not self.id or not self.goal_type or not self.target:
            raise ValueError("intention identity and goal fields are required")
        if self.trigger_type not in {"event", "time", "context"}:
            raise ValueError("invalid intention trigger type")
        if not 0.0 <= self.base_pressure <= 1.0:
            raise ValueError("intention base pressure must be in [0,1]")
        if self.monitoring not in {"strategic", "spontaneous"}:
            raise ValueError("invalid intention monitoring mode")
        if self.cost_uc < 0:
            raise ValueError("intention cost must be non-negative")
        if self.state not in {"pending", "triggered", "done", "abandoned"}:
            raise ValueError("invalid intention state")
        if self.deadline_step is not None and self.deadline_step < 0:
            raise ValueError("intention deadline must be non-negative")


@dataclass(frozen=True, slots=True)
class IntentionTriggerResult:
    intention_ref: str
    triggered: bool
    contribution: Contribution | None
    goal_proposal: GoalProposal | None


@dataclass(frozen=True, slots=True)
class RecallResult:
    episode_ref: str
    score: float
    recency: float
    importance: float
    relevance: float


class EpisodicMemory:
    owner_id = "memory"

    def __init__(self, config: MemoryConfig) -> None:
        config.validate()
        self._config = config
        self._episodes: list[Episode] = []
        self._seen_event_refs: set[str] = set()
        self._open_event_refs: list[str] = []
        self._open_start_t: int | None = None
        self._open_goal_ref: str | None = None
        self._open_body_start: Mapping[str, float] | None = None
        self._open_body_end: Mapping[str, float] | None = None
        self._open_reward = 0.0
        self._open_surprise = 0.0
        self._episode_sequence = 0
        self._last_recalled_ref: str | None = None
        self._intentions: dict[str, Intention] = {}

    @property
    def episodes(self) -> tuple[Episode, ...]:
        return tuple(self._episodes)

    @property
    def last_recalled_ref(self) -> str | None:
        return self._last_recalled_ref

    @property
    def intentions(self) -> tuple[Intention, ...]:
        return tuple(self._intentions[key] for key in sorted(self._intentions))

    @property
    def wake_deadline_index(self) -> Mapping[str, int]:
        return {
            item.id: item.deadline_step
            for item in self.intentions
            if (
                item.wake_authorized
                and item.deadline_step is not None
                and item.state == "pending"
            )
        }

    def create_intention(self, intention: Intention) -> None:
        intention.validate()
        if intention.id in self._intentions:
            raise ValueError("intention id already exists")
        self._intentions[intention.id] = intention

    def complete_intention(self, intention_ref: str) -> None:
        current = self._intentions.get(intention_ref)
        if current is None:
            raise KeyError(f"unknown intention: {intention_ref}")
        self._intentions[intention_ref] = Intention(
            id=current.id,
            goal_type=current.goal_type,
            target=current.target,
            trigger_type=current.trigger_type,
            trigger_value=current.trigger_value,
            deadline_step=current.deadline_step,
            base_pressure=current.base_pressure,
            monitoring=current.monitoring,
            cost_uc=current.cost_uc,
            wake_authorized=current.wake_authorized,
            state="done",
            candidacy_active=False,
        )

    @staticmethod
    def _trigger_matches(
        intention: Intention,
        *,
        st: STVersion | None,
        t_monde: int,
    ) -> bool:
        if intention.trigger_type == "time":
            return t_monde >= int(intention.trigger_value)
        if intention.trigger_type == "context":
            if st is None or not isinstance(intention.trigger_value, Mapping):
                return False
            key = intention.trigger_value.get("fixed_key")
            expected = intention.trigger_value.get("equals")
            return isinstance(key, str) and st.fixed.get(key) == expected
        if intention.trigger_type == "event":
            if st is None:
                return False
            return any(
                element.contribution_ref == str(intention.trigger_value)
                for element in st.competitive
            )
        return False

    def check_intentions(
        self,
        *,
        st: STVersion | None,
        t_monde: int,
        cycle: int,
        pressure_fn,
    ) -> tuple[IntentionTriggerResult, ...]:
        results: list[IntentionTriggerResult] = []
        for item in self.intentions:
            if item.state not in {"pending", "triggered"}:
                continue
            matches = self._trigger_matches(item, st=st, t_monde=t_monde)
            if not matches or item.candidacy_active:
                results.append(
                    IntentionTriggerResult(
                        intention_ref=item.id,
                        triggered=False,
                        contribution=None,
                        goal_proposal=None,
                    )
                )
                continue

            remaining = (
                None
                if item.deadline_step is None
                else item.deadline_step - t_monde
            )
            current_pressure = float(
                pressure_fn(
                    base_pressure=item.base_pressure,
                    remaining_steps=remaining,
                )
            )
            contribution_id = f"intention:{item.id}:{t_monde}:{cycle}"
            contribution = Contribution(
                id=contribution_id,
                schema_version="mvp-v1.2.1",
                type="response",
                summary=f"intention triggered: {item.goal_type}",
                subject_ref=f"intention:{item.id}",
                emitter_module="memory",
                signal_family="memory_recall",
                confidence=1.0,
                urgency=current_pressure,
                risk=0.0,
                value=0.0,
                production_t=t_monde,
                production_cycle=cycle,
                expires_at_step=t_monde + self._config.contribution_ttl_steps,
                payload={
                    "intention_ref": item.id,
                    "goal_type": item.goal_type,
                    "target": item.target,
                    "trigger_type": item.trigger_type,
                    "deadline_step": item.deadline_step,
                },
                signal_ids=(f"intention:{item.id}",),
            )
            contribution.validate()
            proposal = GoalProposal(
                id=f"goal-proposal:intention:{item.id}:{t_monde}:{cycle}",
                source="prospective_memory",
                goal_type=item.goal_type,
                target=item.target,
                base_pressure=item.base_pressure,
                current_pressure=current_pressure,
                justification_ref=contribution_id,
                t_monde=t_monde,
                cycle=cycle,
                rule_version=self._config.version,
            )
            proposal.validate()
            self._intentions[item.id] = Intention(
                id=item.id,
                goal_type=item.goal_type,
                target=item.target,
                trigger_type=item.trigger_type,
                trigger_value=item.trigger_value,
                deadline_step=item.deadline_step,
                base_pressure=item.base_pressure,
                monitoring=item.monitoring,
                cost_uc=item.cost_uc,
                wake_authorized=item.wake_authorized,
                state="triggered",
                candidacy_active=True,
            )
            results.append(
                IntentionTriggerResult(
                    intention_ref=item.id,
                    triggered=True,
                    contribution=contribution,
                    goal_proposal=proposal,
                )
            )
        return tuple(results)

    @staticmethod
    def _event_t(event: Mapping[str, object]) -> int | None:
        raw = event.get("t_monde")
        return raw if isinstance(raw, int) else None

    @staticmethod
    def _event_id(event: Mapping[str, object]) -> str | None:
        raw = event.get("event_id")
        return raw if isinstance(raw, str) else None

    @staticmethod
    def _body_from_transition(
        event: Mapping[str, object],
    ) -> Mapping[str, float] | None:
        if event.get("kind") != "world_transition_experienced":
            return None
        raw = event.get("body_after")
        if not isinstance(raw, Mapping):
            return None
        try:
            return {
                key: float(raw[key])
                for key in ("energy", "food", "water", "integrity")
            }
        except (KeyError, TypeError, ValueError):
            return None

    @staticmethod
    def _goal_after(event: Mapping[str, object]) -> str | None | object:
        if event.get("kind") != "active_goal_changed":
            return ...
        data = event.get("data")
        if not isinstance(data, Mapping):
            return ...
        after = data.get("after")
        if after is None:
            return None
        if isinstance(after, Mapping) and isinstance(after.get("id"), str):
            return str(after["id"])
        return ...

    def _prediction_boundary(
        self,
        event: Mapping[str, object],
    ) -> tuple[bool, float]:
        if event.get("kind") == "experienced_prediction_error":
            value_raw = event.get("value")
            precision_raw = event.get("precision")
            if not isinstance(value_raw, (int, float)):
                return False, 0.0
            value = abs(float(value_raw))
            precision = (
                0.0
                if not isinstance(precision_raw, (int, float))
                else abs(float(precision_raw))
            )
            threshold = self._config.prediction_error_multiplier * precision
            return value > threshold, value

        if event.get("kind") != "agency_comparison":
            return False, 0.0
        data = event.get("data")
        if not isinstance(data, Mapping):
            return False, 0.0
        effects = data.get("effects")
        if not isinstance(effects, list):
            return False, 0.0

        largest = 0.0
        crosses = False
        for effect in effects:
            if not isinstance(effect, Mapping):
                continue
            if effect.get("status") not in {
                "nonconforming",
                "expected_effect_missing",
            }:
                continue
            predicted = effect.get("predicted")
            observed = effect.get("observed")
            precision_raw = effect.get("precision")
            if not isinstance(predicted, (int, float)) or not isinstance(
                observed, (int, float)
            ):
                continue
            magnitude = abs(float(observed) - float(predicted))
            precision = (
                0.0
                if not isinstance(precision_raw, (int, float))
                else abs(float(precision_raw))
            )
            largest = max(largest, magnitude)
            if magnitude > self._config.prediction_error_multiplier * precision:
                crosses = True
        return crosses, largest

    def _close(
        self,
        *,
        end_t_monde: int,
        boundary_type: str,
    ) -> Episode | None:
        if self._open_start_t is None or not self._open_event_refs:
            return None

        previous = self._episodes[-1] if self._episodes else None
        linked_previous = None
        if (
            previous is not None
            and self._open_start_t - previous.end_t_monde
            < self._config.link_delta_steps
        ):
            linked_previous = previous.id

        episode = Episode(
            id=f"episode:{self._episode_sequence}",
            start_t_monde=self._open_start_t,
            end_t_monde=end_t_monde,
            event_refs=tuple(self._open_event_refs),
            boundary_type=boundary_type,
            active_goal_ref=self._open_goal_ref,
            body_start=self._open_body_start,
            body_end=self._open_body_end,
            cumulative_reward=self._open_reward,
            surprise=self._open_surprise,
            linked_previous_ref=linked_previous,
        )
        self._episode_sequence += 1
        self._episodes.append(episode)

        self._open_event_refs = []
        self._open_start_t = None
        self._open_goal_ref = None
        self._open_body_start = None
        self._open_body_end = None
        self._open_reward = 0.0
        self._open_surprise = 0.0
        return episode

    def ingest_autobiographical(
        self,
        events: Sequence[Mapping[str, object]],
        *,
        current_t_monde: int,
        current_goal_ref: str | None,
        current_reward: float,
    ) -> tuple[Episode, ...]:
        """Ingest only newly visible autobiographical events."""

        closed: list[Episode] = []
        new_events = []
        for event in events:
            event_id = self._event_id(event)
            if event_id is None or event_id in self._seen_event_refs:
                continue
            self._seen_event_refs.add(event_id)
            new_events.append(event)

        new_events.sort(
            key=lambda event: (
                -1 if self._event_t(event) is None else self._event_t(event),
                str(event.get("event_id", "")),
            )
        )

        for event in new_events:
            t_monde = self._event_t(event)
            if t_monde is None:
                continue

            if self._open_start_t is None:
                self._open_start_t = t_monde
                self._open_goal_ref = current_goal_ref

            event_id = self._event_id(event)
            if event_id is not None:
                self._open_event_refs.append(event_id)

            body = self._body_from_transition(event)
            if body is not None:
                if self._open_body_start is None:
                    self._open_body_start = body
                self._open_body_end = body

            goal_after = self._goal_after(event)
            if goal_after is not ... and goal_after != self._open_goal_ref:
                closed_episode = self._close(
                    end_t_monde=t_monde,
                    boundary_type="goal_change",
                )
                if closed_episode is not None:
                    closed.append(closed_episode)
                self._open_goal_ref = (
                    None if goal_after is None else str(goal_after)
                )
                continue

            prediction_boundary, surprise = self._prediction_boundary(event)
            self._open_surprise += surprise
            if prediction_boundary:
                closed_episode = self._close(
                    end_t_monde=t_monde,
                    boundary_type="prediction_error",
                )
                if closed_episode is not None:
                    closed.append(closed_episode)
                continue

            if (
                self._open_start_t is not None
                and t_monde - self._open_start_t + 1
                >= self._config.max_episode_steps
            ):
                closed_episode = self._close(
                    end_t_monde=t_monde,
                    boundary_type="max_length",
                )
                if closed_episode is not None:
                    closed.append(closed_episode)

        if new_events:
            self._open_reward += float(current_reward)

        # If no boundary event arrived, current goal is context for a fresh open
        # episode only. It does not retroactively rewrite an existing episode.
        if self._open_start_t is not None and self._open_goal_ref is None:
            self._open_goal_ref = current_goal_ref

        return tuple(closed)

    def _relevance(
        self,
        episode: Episode,
        st: STVersion | None,
    ) -> float:
        if st is None:
            return 0.0
        # Stage-7 exact-search stub: relevance is symbolic exact overlap between
        # episode goal/event references and current S_t references.
        current_refs = {
            element.contribution_ref for element in st.competitive
        }
        if episode.active_goal_ref is not None:
            active = st.fixed.get("active_goal")
            if (
                isinstance(active, Mapping)
                and active.get("id") == episode.active_goal_ref
            ):
                return 1.0
        if any(ref in current_refs for ref in episode.event_refs):
            return 1.0
        return 0.0

    def recall(
        self,
        *,
        st: STVersion | None,
        t_monde: int,
        limit: int | None = None,
    ) -> tuple[RecallResult, ...]:
        scored: list[RecallResult] = []
        for episode in self._episodes:
            age = max(0, t_monde - episode.end_t_monde)
            recency = max(
                0.0,
                1.0 - age / self._config.recall_recency_scale_steps,
            )
            importance = episode.importance
            relevance = self._relevance(episode, st)
            score = (
                self._config.recall_weight_recency * recency
                + self._config.recall_weight_importance * importance
                + self._config.recall_weight_relevance * relevance
            )
            if score < self._config.recall_threshold:
                continue
            scored.append(
                RecallResult(
                    episode_ref=episode.id,
                    score=score,
                    recency=recency,
                    importance=importance,
                    relevance=relevance,
                )
            )

        scored.sort(key=lambda item: (-item.score, item.episode_ref))
        if limit is not None:
            if limit < 1:
                raise ValueError("recall limit must be >= 1")
            scored = scored[:limit]
        return tuple(scored)

    def spontaneous_contribution(
        self,
        *,
        st: STVersion | None,
        t_monde: int,
        cycle: int,
    ) -> Contribution | None:
        recalled = self.recall(st=st, t_monde=t_monde, limit=1)
        if not recalled:
            return None
        top = recalled[0]
        episode = next(
            episode for episode in self._episodes
            if episode.id == top.episode_ref
        )
        self._last_recalled_ref = episode.id
        contribution = Contribution(
            id=f"memory-recall:{episode.id}:{t_monde}:{cycle}",
            schema_version="mvp-v1.2.1",
            type="response",
            summary=(
                f"recalled episode {episode.start_t_monde}-{episode.end_t_monde}"
            ),
            subject_ref=f"episode:{episode.id}",
            emitter_module="memory",
            signal_family="memory_recall",
            confidence=1.0,
            urgency=0.0,
            risk=0.0,
            value=0.0,
            production_t=t_monde,
            production_cycle=cycle,
            expires_at_step=t_monde + self._config.contribution_ttl_steps,
            payload={
                "episode_ref": episode.id,
                "start_t_monde": episode.start_t_monde,
                "end_t_monde": episode.end_t_monde,
                "boundary_type": episode.boundary_type,
                "score": top.score,
            },
            provenance_inputs=episode.event_refs,
            signal_ids=(f"memory:{episode.id}",),
        )
        contribution.validate()
        return contribution

    def export_causal_state(self) -> object:
        return {
            "config_version": self._config.version,
            "episodes": [episode.as_dict() for episode in self._episodes],
            "seen_event_refs": sorted(self._seen_event_refs),
            "open_event_refs": list(self._open_event_refs),
            "open_start_t": self._open_start_t,
            "open_goal_ref": self._open_goal_ref,
            "open_body_start": (
                None if self._open_body_start is None
                else dict(self._open_body_start)
            ),
            "open_body_end": (
                None if self._open_body_end is None
                else dict(self._open_body_end)
            ),
            "open_reward": self._open_reward,
            "open_surprise": self._open_surprise,
            "episode_sequence": self._episode_sequence,
            "last_recalled_ref": self._last_recalled_ref,
            "intentions": [
                {
                    "id": item.id,
                    "goal_type": item.goal_type,
                    "target": item.target,
                    "trigger_type": item.trigger_type,
                    "trigger_value": item.trigger_value,
                    "deadline_step": item.deadline_step,
                    "base_pressure": item.base_pressure,
                    "monitoring": item.monitoring,
                    "cost_uc": item.cost_uc,
                    "wake_authorized": item.wake_authorized,
                    "state": item.state,
                    "candidacy_active": item.candidacy_active,
                }
                for item in self.intentions
            ],
        }

    def restore_causal_state(self, state: object) -> None:
        if not isinstance(state, Mapping):
            raise ValueError("Memory state must be a mapping")
        if state.get("config_version") != self._config.version:
            raise ValueError("Memory config version mismatch")

        raw_episodes = state.get("episodes")
        if not isinstance(raw_episodes, list):
            raise ValueError("Memory episodes must be a list")
        restored = []
        for raw in raw_episodes:
            if not isinstance(raw, Mapping):
                raise ValueError("invalid episode state")
            restored.append(
                Episode(
                    id=str(raw["id"]),
                    start_t_monde=int(raw["start_t_monde"]),
                    end_t_monde=int(raw["end_t_monde"]),
                    event_refs=tuple(str(x) for x in raw["event_refs"]),
                    boundary_type=str(raw["boundary_type"]),
                    active_goal_ref=(
                        None
                        if raw.get("active_goal_ref") is None
                        else str(raw["active_goal_ref"])
                    ),
                    body_start=(
                        None
                        if raw.get("body_start") is None
                        else dict(raw["body_start"])
                    ),
                    body_end=(
                        None
                        if raw.get("body_end") is None
                        else dict(raw["body_end"])
                    ),
                    cumulative_reward=float(raw["cumulative_reward"]),
                    surprise=float(raw["surprise"]),
                    linked_previous_ref=(
                        None
                        if raw.get("linked_previous_ref") is None
                        else str(raw["linked_previous_ref"])
                    ),
                )
            )

        self._episodes = restored
        self._seen_event_refs = {
            str(x) for x in state.get("seen_event_refs", [])
        }
        self._open_event_refs = [
            str(x) for x in state.get("open_event_refs", [])
        ]
        raw_start = state.get("open_start_t")
        self._open_start_t = None if raw_start is None else int(raw_start)
        raw_goal = state.get("open_goal_ref")
        self._open_goal_ref = None if raw_goal is None else str(raw_goal)
        raw_body_start = state.get("open_body_start")
        raw_body_end = state.get("open_body_end")
        self._open_body_start = (
            None if raw_body_start is None else dict(raw_body_start)
        )
        self._open_body_end = (
            None if raw_body_end is None else dict(raw_body_end)
        )
        self._open_reward = float(state.get("open_reward", 0.0))
        self._open_surprise = float(state.get("open_surprise", 0.0))
        self._episode_sequence = int(state.get("episode_sequence", 0))
        raw_recalled = state.get("last_recalled_ref")
        self._last_recalled_ref = (
            None if raw_recalled is None else str(raw_recalled)
        )

        raw_intentions = state.get("intentions", [])
        if not isinstance(raw_intentions, list):
            raise ValueError("Memory intentions must be a list")
        self._intentions = {}
        for raw in raw_intentions:
            if not isinstance(raw, Mapping):
                raise ValueError("invalid intention state")
            item = Intention(
                id=str(raw["id"]),
                goal_type=str(raw["goal_type"]),
                target=str(raw["target"]),
                trigger_type=str(raw["trigger_type"]),
                trigger_value=raw.get("trigger_value"),
                deadline_step=(
                    None
                    if raw.get("deadline_step") is None
                    else int(raw["deadline_step"])
                ),
                base_pressure=float(raw["base_pressure"]),
                monitoring=str(raw["monitoring"]),
                cost_uc=int(raw["cost_uc"]),
                wake_authorized=bool(raw["wake_authorized"]),
                state=str(raw["state"]),
                candidacy_active=bool(raw["candidacy_active"]),
            )
            item.validate()
            self._intentions[item.id] = item
