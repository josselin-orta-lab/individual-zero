"""Offline non-motor I2 candidate reconstruction tests; NO live runtime."""
from dataclasses import fields, replace
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from i2.modules.intention_continuity import (  # noqa: E402
    FirstPersonCapture, IntentionContinuity, IntentionTransition,
    SemanticIntention,
)
from i2.modules.intention_ingress import (  # noqa: E402
    ObservationClaim, IntentionIngress, UCReceipt,
)
from i2.modules.option_reconstruction import (  # noqa: E402
    CandidateFrame, SemanticCandidate, reconstruct_candidates,
)

A = "affordance:collect:berry_a"
B = "affordance:eat:berry_a"
C = "affordance:drink:water"
LIFE = "life:synthetic-fixture"
GOAL = "goal:body-food"


def capture(step, visible=(A, B, C), *, goal=GOAL, ref=None, contradicted=()):
    return ObservationClaim(
        life_ref=LIFE,
        capture=FirstPersonCapture(
            step=step, ref=ref or f"capture:{step}", goal_ref=goal,
            accessible_semantics=tuple(sorted(visible)),
            contradicted_semantics=tuple(sorted(contradicted)),
        ),
        source_event_ref=f"source:{step}",
        subjective_evidence_refs=(f"evidence:{step}",),
    )


def begin(visible=(A, B, C)):
    o = IntentionContinuity()
    c = capture(3, visible)
    t = o.open(capture=c.capture, semantic_ref=A,
               evidence_ref="evidence:3", ttl_steps=12, work_ref="work:3")
    return o, c, t


def later(owner, step, visible=(A, B, C), *, goal=GOAL, contradicted=()):
    c = capture(step, visible, goal=goal, contradicted=contradicted)
    t = owner.observe(capture=c.capture, work_ref=f"work:{step}")
    return c, t, reconstruct_candidates(claim=c, transition=t, current=owner.current)


class TestOptionReconstruction(unittest.TestCase):
    def test_requires_a_paid_owner_transition_by_shape_not_as_proof(self):
        o, c, t = begin()
        f = reconstruct_candidates(claim=c, transition=t, current=o.current)
        self.assertEqual(f.work_correlation_ref, "work:3")
        self.assertEqual(f.physical_step, 3)
        self.assertEqual(f.claim_digest, c.digest())
        self.assertEqual(f.life_ref, LIFE)
        self.assertTrue(f.frame_ref.startswith("frame:i2:"))

    def test_all_accessible_candidates_survive_motivational_tagging(self):
        o, c, t = begin()
        f = reconstruct_candidates(claim=c, transition=t, current=o.current)
        self.assertEqual(tuple(z.semantic_ref for z in f.candidates), tuple(sorted((A, B, C))))
        self.assertEqual({z.semantic_ref:z.intention_ref for z in f.candidates},
                         {A:o.current.ref, B:None, C:None})
        self.assertEqual(len(set(z.candidate_ref for z in f.candidates)), 3)

    def test_no_food_bias_candidate_priorities_or_motor_commands(self):
        o, c, t = begin()
        f = reconstruct_candidates(claim=c, transition=t, current=o.current)
        forbidden = {"priority", "score", "q", "accumulator", "winner", "command",
                     "motor", "admission", "approved", "threshold", "option_ref", "action"}
        self.assertFalse(forbidden & {k.name for k in fields(SemanticCandidate)})
        self.assertFalse(forbidden & {k.name for k in fields(CandidateFrame)})
        self.assertFalse(any(hasattr(f, n) for n in ("run_step", "dispatch", "act", "admit")))

    def test_determinism_without_reusing_next_step_candidate_identity(self):
        o, c, t = begin()
        left = reconstruct_candidates(claim=c, transition=t, current=o.current)
        right = reconstruct_candidates(claim=c, transition=t, current=o.current)
        self.assertEqual(left, right)
        cc, tt, future = later(o, 4)
        self.assertNotEqual(left.frame_ref, future.frame_ref)
        self.assertTrue(set(z.candidate_ref for z in left.candidates).isdisjoint(
            {z.candidate_ref for z in future.candidates}))
        self.assertEqual(future.candidates[0].intention_ref, o.current.ref)
        self.assertEqual(cc.capture.step, 4)

    def test_only_current_perception_can_supply_candidates(self):
        o, c, t = begin()
        for visible in ((A,), (B, C), (), (C,)):
            with self.subTest(visible=visible):
                # Independent fixture; no imputed feeding or remembered resource.
                a = IntentionContinuity()
                v = capture(3, visible)
                tr = a.observe(capture=v.capture, work_ref="work:3")
                frame = reconstruct_candidates(claim=v, transition=tr, current=a.current)
                self.assertEqual(tuple(x.semantic_ref for x in frame.candidates), tuple(sorted(visible)))
                self.assertTrue(all(x.intention_ref is None for x in frame.candidates))

    def test_hidden_goal_suspends_but_other_choices_remain(self):
        o, _, _ = begin()
        c, t, f = later(o, 4, (B, C))
        self.assertEqual(t.kind, "suspended")
        self.assertEqual(tuple(z.semantic_ref for z in f.candidates), tuple(sorted((B, C))))
        self.assertTrue(all(z.intention_ref is None for z in f.candidates))
        self.assertEqual(o.current.status, "suspended")

    def test_resumption_does_not_resurrect_an_old_candidate(self):
        o, c, t = begin()
        original = reconstruct_candidates(claim=c, transition=t, current=o.current)
        later(o, 4, (B,))
        _, tr, fresh = later(o, 5, (A, B))
        self.assertEqual(tr.kind, "resumed")
        self.assertEqual({x.semantic_ref:x.intention_ref for x in fresh.candidates}[A], o.current.ref)
        self.assertTrue({c.candidate_ref for c in original.candidates}.isdisjoint(
            {c.candidate_ref for c in fresh.candidates}))

    def test_goal_change_clears_tag_without_suppressing_options(self):
        o, _, _ = begin()
        _, tr, f = later(o, 4, (A, B), goal="goal:thirst")
        self.assertEqual(tr.kind, "goal_changed")
        self.assertEqual(tuple(x.semantic_ref for x in f.candidates), (A, B))
        self.assertTrue(all(x.intention_ref is None for x in f.candidates))

    def test_contradiction_invalidates_tag_and_keeps_other_choices(self):
        o, _, _ = begin()
        _, tr, f = later(o, 4, (B, C), contradicted=(A,))
        self.assertEqual(tr.kind, "contradicted")
        self.assertEqual(tuple(x.semantic_ref for x in f.candidates), tuple(sorted((B, C))))
        self.assertTrue(all(x.intention_ref is None for x in f.candidates))

    def test_expiry_cannot_resurrect_tag(self):
        o = IntentionContinuity()
        c = capture(3)
        o.open(capture=c.capture, semantic_ref=A, evidence_ref="evidence:3",
               ttl_steps=1, work_ref="work:3")
        _, t, frame = later(o, 4)
        self.assertEqual(t.kind, "expired")
        self.assertIsNone(o.current)
        self.assertTrue(all(x.intention_ref is None for x in frame.candidates))

    def test_different_live_id_changes_candidate_reference(self):
        c = capture(3)
        tr = IntentionTransition("idle", 3, c.capture.ref, None, "work:3")
        other = replace(c, life_ref="life:another")
        f = reconstruct_candidates(claim=c, transition=tr, current=None)
        g = reconstruct_candidates(claim=other, transition=tr, current=None)
        self.assertTrue(set(x.candidate_ref for x in f.candidates).isdisjoint(
            {x.candidate_ref for x in g.candidates}))

    def test_rejects_wrong_transition_capture_or_time(self):
        o, c, t = begin()
        invalid = (replace(t, capture_ref="capture:wrong"), replace(t, step=4),
                   replace(t, work_ref=""), replace(t, kind="motor"))
        for v in invalid:
            with self.subTest(v=v), self.assertRaises(ValueError):
                reconstruct_candidates(claim=c, transition=v, current=o.current)

    def test_rejects_stale_intention_even_if_it_is_still_active(self):
        o, c, t = begin()
        c2 = capture(4)
        tr = IntentionTransition("retained", 4, c2.capture.ref, o.current.ref, "work:4")
        with self.assertRaises(ValueError):
            reconstruct_candidates(claim=c2, transition=tr, current=o.current)

    def test_rejects_forged_current_goal_or_status(self):
        o, c, t = begin()
        bad = (replace(o.current, goal_ref="goal:thirst"),
               replace(o.current, status="suspended"),
               replace(o.current, last_capture_ref="capture:other"),
               replace(o.current, semantic_ref=B))
        for v in bad:
            with self.subTest(v=v), self.assertRaises(ValueError):
                reconstruct_candidates(claim=c, transition=t, current=v)

    def test_rejects_clear_transition_claiming_current_intention(self):
        o, c, t = begin()
        for kind in ("idle", "expired", "goal_changed", "contradicted"):
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                reconstruct_candidates(claim=c, transition=replace(t, kind=kind), current=o.current)

    def test_rejects_open_transition_with_unbacked_origin_evidence(self):
        o, c, t = begin()
        bad = replace(o.current, origin_evidence_ref="evidence:alien")
        # Recompute ID so the owner semantic checksum is otherwise valid.
        from i2.modules.intention_continuity import _intention_ref
        bad = replace(bad, ref=_intention_ref(bad.origin_capture_ref, bad.goal_ref,
                                                bad.semantic_ref, bad.origin_evidence_ref))
        with self.assertRaises(ValueError):
            reconstruct_candidates(claim=c, transition=replace(t, intention_ref=bad.ref), current=bad)

    def test_rejects_transition_on_nonexistent_or_inconsistent_intent(self):
        o, c, t = begin()
        with self.assertRaises(ValueError):
            reconstruct_candidates(claim=c, transition=t, current=None)
        with self.assertRaises(ValueError):
            reconstruct_candidates(claim=c, transition=replace(t, kind="still_suspended"), current=o.current)
        with self.assertRaises(ValueError):
            reconstruct_candidates(claim=c, transition=replace(t, intention_ref="intent:alien"), current=o.current)

    def test_rejects_unexpected_claim_type_and_uncanonical_evidence(self):
        o, c, t = begin()
        with self.assertRaises(ValueError):
            reconstruct_candidates(claim=c.capture, transition=t, current=o.current)
        bad = replace(c, subjective_evidence_refs=("z", "a"))
        with self.assertRaises(ValueError):
            reconstruct_candidates(claim=bad, transition=t, current=o.current)

    def test_rejects_future_and_expired_intention_and_mixed_goal(self):
        o, c, t = begin()
        other = capture(4, goal="goal:thirst")
        t2 = replace(t, step=4, capture_ref=other.capture.ref)
        v = replace(o.current, last_checked_step=4, last_capture_ref=other.capture.ref)
        with self.assertRaises(ValueError):
            reconstruct_candidates(claim=other, transition=t2, current=v)
        expired = replace(o.current, expires_at_step=3)
        with self.assertRaises(ValueError):
            reconstruct_candidates(claim=c, transition=t, current=expired)

    def test_status_is_not_transferred_between_independent_frames(self):
        o, c, t = begin()
        f = reconstruct_candidates(claim=c, transition=t, current=o.current)
        cleared = IntentionTransition("idle", 3, c.capture.ref, None, t.work_ref)
        # Same perceived opportunities preserve candidate IDs, independent of intent tag.
        plain = reconstruct_candidates(claim=c, transition=cleared, current=None)
        self.assertEqual([x.candidate_ref for x in f.candidates],
                         [x.candidate_ref for x in plain.candidates])
        self.assertEqual([x.intention_ref for x in plain.candidates], [None, None, None])
        self.assertNotEqual(f.frame_ref, plain.frame_ref)


    def test_ingress_synthetic_ports_only_can_feed_current_transition(self):
        # End-to-end SOURCE-ONLY wiring, NOT an authenticated birth or Scheduler.
        c = capture(3)
        class Source:
            def verify(self, *, life_ref, claim, digest):
                return life_ref == LIFE and digest == c.digest()
        class SyntheticUC:
            count = 0
            def debit(self, *, life_ref, capture_ref, claim_digest, operation, units):
                self.count += 1
                return UCReceipt(f"mock:charge:{self.count}", life_ref,
                                 capture_ref, claim_digest, operation, units)
        gate = IntentionIngress(life_ref=LIFE, observation_authority=Source(),
                                uc_authority=SyntheticUC())
        t = gate.open(claim=c, semantic_ref=A, evidence_ref="evidence:3", ttl_steps=6)
        frame = reconstruct_candidates(claim=c, transition=t, current=gate.current)
        self.assertEqual(frame.work_correlation_ref, "mock:charge:1")
        self.assertEqual({z.semantic_ref:z.intention_ref for z in frame.candidates}[A],
                         gate.current.ref)
        self.assertEqual(len(frame.candidates), 3)

    def test_ingress_transition_not_reusable_after_new_capture(self):
        c = capture(3)
        class Source:
            def verify(self, *, life_ref, claim, digest):
                return digest == claim.digest()
        class SyntheticUC:
            n = 0
            def debit(self, *, life_ref, capture_ref, claim_digest, operation, units):
                self.n += 1
                return UCReceipt(f"mock:receipt:{self.n}", life_ref,
                                 capture_ref, claim_digest, operation, units)
        gate = IntentionIngress(life_ref=LIFE, observation_authority=Source(),
                                uc_authority=SyntheticUC())
        t = gate.open(claim=c, semantic_ref=A, evidence_ref="evidence:3", ttl_steps=8)
        c4 = capture(4)
        t4 = gate.observe(claim=c4)
        self.assertEqual(t4.kind, "retained")
        with self.assertRaises(ValueError):
            reconstruct_candidates(claim=c4, transition=t, current=gate.current)
        frame = reconstruct_candidates(claim=c4, transition=t4, current=gate.current)
        self.assertTrue(all(z.candidate_ref.startswith("candidate:i2:")
                            for z in frame.candidates))

    def test_frame_rejects_boolean_step_even_if_equal_numerically(self):
        o = IntentionContinuity()
        c = capture(1)
        t = o.observe(capture=c.capture, work_ref="work:1")
        with self.assertRaises(ValueError):
            reconstruct_candidates(claim=c, transition=replace(t, step=True), current=None)

    def test_suspended_status_requires_not_visible_on_current_capture(self):
        o, _, _ = begin()
        c, t, frame = later(o, 4, (B, C))
        changed = replace(c, capture=replace(c.capture,
                                            accessible_semantics=tuple(sorted((A, B, C)))))
        with self.assertRaises(ValueError):
            reconstruct_candidates(claim=changed, transition=t, current=o.current)



if __name__ == "__main__":
    unittest.main()
