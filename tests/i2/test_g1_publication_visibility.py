"""Bounded G1 review model, NOT a living I2 runtime or M11 witness.

Target #662 R1/R4/R6: before accepting a single-owner WorldBody design,
show the C5/C7 public-visibility problem across local COMMIT and external CAS.
All owners/witnesses here are VALUE OBJECTS; trusted latest-head/fencing,
append-only retention and independent custody are ASSUMPTIONS, not provided.
This file implements no physics, cognition, motor, birth or recovery rights.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import unittest


class Refusal(ValueError):
    """Stop rather than selecting an uncertain life revision."""


@dataclass(frozen=True)
class Revision:
    number: int
    digest: str
    previous_digest: str | None
    outcome: str | None
    terminal: bool


@dataclass(frozen=True)
class Owner:
    """A proposed ONE-owner revision history, not a mutable WorldBody."""

    revisions: tuple[Revision, ...]
    technical_halt: bool = False


@dataclass(frozen=True)
class Witness:
    """A mock externally governed latest-head claim, NEVER trusted M11."""

    revision: int
    digest: str
    terminal: bool
    writer_epoch: int


def genesis() -> tuple[Owner, Witness]:
    initial = Revision(0, "0" * 64, None, None, False)
    return (Owner((initial,)), Witness(0, initial.digest, False, 1))


def public_revision(owner: Owner, latest: Witness, *, verified_latest: bool) -> Revision:
    """Read ONLY the exact externally attested historical revision.

    A caller's stale receipt or operator HMAC does not satisfy verified_latest.
    A caller with no matching local historical version MUST refuse, not read
    the newest local row and not synthesize an absent old state.
    """
    if verified_latest is not True:
        raise Refusal("no independent fresh witness")
    matches = [v for v in owner.revisions if v.number == latest.revision]
    if len(matches) != 1:
        raise Refusal("attested public revision unavailable")
    found = matches[0]
    if found.digest != latest.digest or found.terminal != latest.terminal:
        raise Refusal("attested revision mismatches owner")
    return found


def commit_private(owner: Owner, latest: Witness, *, outcome: str,
                   terminal: bool = False) -> Owner:
    """Inert hypothetical local COMMIT: append a digest, no public effect."""
    if owner.technical_halt or latest.terminal:
        raise Refusal("halt or terminal forbids another attempt")
    current = public_revision(owner, latest, verified_latest=True)
    if current != owner.revisions[-1]:
        raise Refusal("pending private revision; no second action")
    if outcome not in {"benefit", "harm", "death"} or type(terminal) is not bool:
        raise ValueError("model requires an explicit physical-result token")
    if terminal != (outcome == "death"):
        raise ValueError("model terminal/result inconsistency")
    digest = sha256(
        f"{current.digest}:{current.number + 1}:{outcome}:{int(terminal)}".encode()
    ).hexdigest()
    return replace(owner, revisions=owner.revisions + (
        Revision(current.number + 1, digest, current.digest, outcome, terminal),
    ))


def compare_and_set(latest: Witness, *, expected: Witness, candidate: Revision,
                    writer_epoch: int) -> Witness:
    """Contract of a *hypothetical* independently fenced monotone provider."""
    if type(writer_epoch) is not int or writer_epoch != latest.writer_epoch:
        raise Refusal("stale writer epoch")
    if expected != latest or latest.terminal:
        raise Refusal("old, terminal or equivocated witness head")
    if (candidate.number != latest.revision + 1 or
            candidate.previous_digest != latest.digest):
        raise Refusal("candidate does not extend attested previous state")
    return Witness(candidate.number, candidate.digest, candidate.terminal,
                   latest.writer_epoch)


def halt_after_uncertain_ack(owner: Owner) -> Owner:
    """The model does NOT allow subsequent execution/resumption after loss."""
    return replace(owner, technical_halt=True)


class G1VisibilityBoundaryReview(unittest.TestCase):
    def test_c5_local_commit_is_private_and_latest_local_read_leaks(self):
        owner, witness = genesis()
        owner = commit_private(owner, witness, outcome="benefit")
        self.assertEqual(owner.revisions[-1].number, 1)
        self.assertEqual(public_revision(owner, witness, verified_latest=True).number, 0)
        # Explicit counterexample: naive read of SQLite's latest local row
        # would expose an unanchored bodily result before external CAS.
        self.assertNotEqual(owner.revisions[-1], public_revision(
            owner, witness, verified_latest=True))
        with self.assertRaisesRegex(Refusal, "pending private revision"):
            commit_private(owner, witness, outcome="benefit")

    def test_c5_old_public_version_must_remain_retrievable(self):
        owner, witness = genesis()
        owner = commit_private(owner, witness, outcome="harm")
        # A future owner holding only a current mutable state row, without
        # retained history of the old attested body, cannot publish safely.
        current_only = Owner((owner.revisions[-1],))
        with self.assertRaisesRegex(Refusal, "unavailable"):
            public_revision(current_only, witness, verified_latest=True)
        self.assertEqual(public_revision(owner, witness, verified_latest=True).number, 0)

    def test_c7_external_cas_then_fresh_public_read_not_same_cycle_foresight(self):
        owner, witness = genesis()
        owner = commit_private(owner, witness, outcome="benefit")
        self.assertIsNone(public_revision(owner, witness, verified_latest=True).outcome)
        updated = compare_and_set(witness, expected=witness,
                                  candidate=owner.revisions[-1], writer_epoch=1)
        self.assertEqual(public_revision(owner, updated, verified_latest=True).outcome,
                         "benefit")
        with self.assertRaisesRegex(Refusal, "independent fresh"):
            public_revision(owner, updated, verified_latest=False)

    def test_c8_lost_cas_ack_halts_execution_even_if_public_read_matches(self):
        owner, witness = genesis()
        owner = commit_private(owner, witness, outcome="benefit")
        updated = compare_and_set(witness, expected=witness,
                                  candidate=owner.revisions[-1], writer_epoch=1)
        owner = halt_after_uncertain_ack(owner)
        self.assertEqual(public_revision(owner, updated, verified_latest=True).number, 1)
        with self.assertRaisesRegex(Refusal, "halt"):
            commit_private(owner, updated, outcome="harm")
        with self.assertRaisesRegex(Refusal, "old"):
            compare_and_set(updated, expected=witness,
                            candidate=owner.revisions[-1], writer_epoch=1)

    def test_c9_old_writer_epoch_cannot_publish(self):
        owner, witness = genesis()
        owner = commit_private(owner, witness, outcome="benefit")
        # An independent service has fenced epoch 1 and issued epoch 2.
        fenced = replace(witness, writer_epoch=2)
        with self.assertRaisesRegex(Refusal, "stale writer"):
            compare_and_set(fenced, expected=fenced,
                            candidate=owner.revisions[-1], writer_epoch=1)
        self.assertEqual(public_revision(owner, fenced, verified_latest=True).number, 0)

    def test_c10_terminal_prevents_restore_when_witness_is_independent(self):
        owner, witness = genesis()
        old_owner = owner
        owner = commit_private(owner, witness, outcome="death", terminal=True)
        terminal = compare_and_set(witness, expected=witness,
                                   candidate=owner.revisions[-1], writer_epoch=1)
        self.assertTrue(public_revision(owner, terminal, verified_latest=True).terminal)
        with self.assertRaisesRegex(Refusal, "terminal"):
            commit_private(owner, terminal, outcome="benefit")
        with self.assertRaisesRegex(Refusal, "unavailable"):
            public_revision(old_owner, terminal, verified_latest=True)

    def test_c10_coordinated_owner_and_fake_witness_rollback_is_counterexample(self):
        original_owner, fake_witness = genesis()
        owner = commit_private(original_owner, fake_witness,
                               outcome="death", terminal=True)
        real_terminal = compare_and_set(fake_witness, expected=fake_witness,
                                        candidate=owner.revisions[-1], writer_epoch=1)
        self.assertTrue(real_terminal.terminal)
        # Restore BOTH local files as an attacker can when the 'witness' is
        # merely in the owner's rollback domain. All local checks now PASS.
        self.assertFalse(public_revision(original_owner, fake_witness,
                                         verified_latest=True).terminal)
        # This falsifies ANY claim that local-only test passes establish M11.
        with self.assertRaises(Refusal):
            public_revision(original_owner, real_terminal, verified_latest=True)

    def test_bounded_c5_to_c8_crash_cut_matrix(self):
        cases = 0
        for outcome in ("benefit", "harm", "death"):
            for cut in ("before_commit", "after_commit", "after_cas",
                        "cas_ack_lost"):
                with self.subTest(outcome=outcome, cut=cut):
                    owner, latest = genesis()
                    if cut == "before_commit":
                        self.assertEqual(public_revision(
                            owner, latest, verified_latest=True).number, 0)
                        cases += 1
                        continue
                    owner = commit_private(owner, latest, outcome=outcome,
                                           terminal=outcome == "death")
                    self.assertEqual(public_revision(
                        owner, latest, verified_latest=True).number, 0)
                    if cut == "after_commit":
                        with self.assertRaises(Refusal):
                            commit_private(owner, latest, outcome="benefit")
                        cases += 1
                        continue
                    attested = compare_and_set(latest, expected=latest,
                                               candidate=owner.revisions[-1],
                                               writer_epoch=1)
                    if cut == "cas_ack_lost":
                        owner = halt_after_uncertain_ack(owner)
                        with self.assertRaises(Refusal):
                            commit_private(owner, attested, outcome="benefit")
                    self.assertEqual(public_revision(
                        owner, attested, verified_latest=True).number, 1)
                    cases += 1
        self.assertEqual(cases, 12)


if __name__ == "__main__":
    unittest.main()
