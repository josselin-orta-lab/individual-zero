"""Stage-10 P-42 deterministic selection tests; not live sleep acceptance."""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
import unittest

from i0.modules.consolidation_batch import (
    BatchSelectionPolicy, BatchSelectionBudgetError,
    ConsolidationBatchSelector,
)
from i0.modules.consolidation_transaction import ConsolidationCut, ConsolidationTransaction


@dataclass(frozen=True)
class EpisodeView:
    """Independent implementation of the actual Memory Episode.as_dict contract."""
    id: str
    end: int
    reward: float = 0.0
    surprise: float = 0.0
    goal: str | None = None

    def as_dict(self):
        return {
            "id": self.id, "start_t_monde": self.end,
            "end_t_monde": self.end, "event_refs": ["lived:" + self.id],
            "boundary_type": "max_length", "active_goal_ref": self.goal,
            "body_start": None, "body_end": None,
            "cumulative_reward": self.reward, "surprise": self.surprise,
            "linked_previous_ref": None,
        }


class EditableEpisodeView:
    def __init__(self, **payload):
        self.payload = payload

    def as_dict(self):
        return self.payload


def cut(step=10):
    return ConsolidationCut(step, 11, "event:11", "af" * 32, "h:0")


def policy(**kwargs):
    value = BatchSelectionPolicy(
        version="P42:dev:1", maximum_episodes=2,
        consequence_reference=10.0, surprise_reference=4.0,
        recency_window_steps=5, repetition_reference=2,
        weight_consequence=2.0, weight_surprise=1.0,
        weight_recency=0.5, weight_repetition=0.5,
        ageing_gain_per_step=0.02, scan_uc_per_episode=2,
    )
    return replace(value, **kwargs)


def select(episodes, *, cfg=None, clock=None, pending=None, uc=None):
    cfg = cfg or policy()
    clock = clock or cut()
    pending = pending if pending is not None else tuple(ep.id for ep in episodes)
    uc = uc if uc is not None else len(episodes) * cfg.scan_uc_per_episode
    return ConsolidationBatchSelector(cfg).select(
        cut=clock, episodes=episodes, pending_episode_refs=pending, reserved_scan_uc=uc,
    )


class ConsolidationBatchSelectionTests(unittest.TestCase):
    def test_exact_order_independent_of_memory_input_order(self):
        episodes = (
            EpisodeView("ep:z", 8, 1),
            EpisodeView("ep:b", 6, 0, 3),
            EpisodeView("ep:a", 4, 7),
        )
        a = select(episodes)
        b = select(tuple(reversed(episodes)), pending=tuple(reversed(tuple(x.id for x in episodes))))
        self.assertEqual(a.digest, b.digest)
        self.assertEqual(a.episode_refs, b.episode_refs)
        self.assertEqual(a.scan_uc, 6)
        self.assertEqual(len(a.episode_refs), 2)

    def test_high_consequence_and_surprise_are_not_ignored(self):
        items = (EpisodeView("major", 8, -10), EpisodeView("minor", 8, 0, 0), EpisodeView("surprise", 8, 0, 4))
        result = select(items, cfg=policy(maximum_episodes=3))
        self.assertEqual(result.episode_refs, ("major", "surprise", "minor"))
        self.assertEqual(result.priorities[0].consequence, 1.0)
        self.assertEqual(result.priorities[1].surprise, 1.0)

    def test_ageing_prevents_indefinite_starvation_from_fresh_arrivals(self):
        cfg = policy(maximum_episodes=1, weight_consequence=1.0,
                     weight_surprise=0, weight_recency=0, weight_repetition=0,
                     ageing_gain_per_step=0.1)
        old = EpisodeView("old", 1, 0)
        new = EpisodeView("new", 8, 10)
        # With an age delta of 7, a new high-impact episode initially wins.
        at_ten = select((old, new), cfg=cfg)
        self.assertEqual(at_ten.episode_refs, ("new",))
        # A permanently postponed episode is more aged than any newly arrived
        # entrant of similarly bounded priority at a sufficiently late step.
        arrival = EpisodeView("arrival", 40, 10)
        at_forty_one = select((old, arrival), cfg=cfg, clock=cut(41))
        self.assertEqual(at_forty_one.episode_refs, ("old",))

    def test_contextual_repetition_is_not_a_compiled_success(self):
        episodes = (
            EpisodeView("a", 7, goal="g:water"),
            EpisodeView("b", 7, goal="g:water"),
            EpisodeView("c", 7, goal="g:food"),
        )
        result = select(episodes, cfg=policy(maximum_episodes=3))
        self.assertEqual(result.episode_refs[:2], ("a", "b"))
        self.assertEqual(result.priorities[0].repetition, 0.5)
        self.assertEqual(result.priorities[-1].repetition, 0)

    def test_only_explicit_pending_episodes_can_be_selected(self):
        episodes = (EpisodeView("already:1", 1, 10), EpisodeView("pending:1", 2, 0.5))
        result = select(episodes, pending=("pending:1",))
        self.assertEqual(result.episode_refs, ("pending:1",))
        self.assertEqual(result.scan_uc, 4)  # both records were examined

    def test_empty_pending_selection_produces_no_phantom_batch(self):
        episodes = (EpisodeView("already", 2),)
        result = select(episodes, pending=())
        self.assertEqual(result.episode_refs, ())
        self.assertEqual(result.episode_payloads_copy(), {})
        self.assertEqual(result.scan_uc, 2)

    def test_insufficient_logical_uc_rejected_before_projection(self):
        class Trap:
            def as_dict(self):
                raise AssertionError("scanned without UC")
        with self.assertRaises(BatchSelectionBudgetError):
            select((Trap(),), cfg=policy(), pending=("x",), uc=1)

    def test_frozen_payload_is_detached_from_memory_and_callers(self):
        payload = EpisodeView("a", 5).as_dict()
        source = EditableEpisodeView(**payload)
        result = select((source,), pending=("a",))
        digest = result.digest
        source.payload["event_refs"].append("later")
        obtained = result.episode_payloads_copy()
        obtained["a"]["event_refs"].append("injected")
        self.assertEqual(result.episode_payloads_copy()["a"]["event_refs"], ["lived:a"])
        self.assertEqual(result.digest, digest)

    def test_chosen_batch_opens_real_transaction_with_unchanged_cut(self):
        selected = select((EpisodeView("a", 2), EpisodeView("b", 3)))
        transaction = ConsolidationTransaction(
            consolidation_id="consolidation:1", cut=selected.cut,
            episode_refs=selected.episode_refs,
            episode_payloads=selected.episode_payloads_copy(),
            history_candidate={"version": "h:0"},
        )
        self.assertEqual(transaction.batch, selected.episode_refs)
        self.assertEqual(transaction.cut, cut())
        self.assertNotEqual(transaction.batch_digest, "")
        self.assertEqual(transaction.frozen_episodes_copy(), selected.episode_payloads_copy())

    def test_pending_episode_at_or_after_cut_rejected(self):
        for end in (10, 12):
            with self.subTest(end=end), self.assertRaises(ValueError):
                select((EpisodeView("future", end),))

    def test_missing_duplicate_or_corrupt_lived_data_rejected(self):
        for eps, pending in (
            ((EpisodeView("a", 1),), ("notfound",)),
            ((EpisodeView("a", 1), EpisodeView("a", 2)), ("a",)),
            ((EditableEpisodeView(**dict(EpisodeView("x", 2).as_dict(), event_refs=[])),), ("x",)),
        ):
            with self.subTest(eps=eps), self.assertRaises(ValueError):
                select(eps, pending=pending)

    def test_nonfinite_scores_and_bad_policy_rejected(self):
        with self.assertRaises(ValueError):
            ConsolidationBatchSelector(policy(ageing_gain_per_step=0))
        with self.assertRaises(ValueError):
            ConsolidationBatchSelector(policy(weight_consequence=float("nan")))
        with self.assertRaises(ValueError):
            select((EpisodeView("x", 2, float("nan")),))
        # Very large but finite weights can overflow the computed score:
        with self.assertRaises(ValueError):
            select((EpisodeView("x", 8, 10, 4),), cfg=policy(weight_consequence=1e308,
                    weight_surprise=1e308, weight_recency=1e308))

    def test_tie_break_by_episode_identity(self):
        items = (EpisodeView("z", 5), EpisodeView("a", 5))
        result = select(items)
        self.assertEqual(result.episode_refs, ("a", "z"))


if __name__ == "__main__":
    unittest.main()
