"""Operator-controlled, immutable local export of I0's COMPLETE causal journal.

The retained journal stays INSIDE I0 during execution. This explicit utility
copies a verified, coherent prefix into an append-only audit artifact; it does
not compact, purge, replay or restore the individual, call an Oracle, or
initialize a Bench. Exports can be made after a real terminal death.

This is NOT a crash-proof live WAL. Operators must export at chosen coherent
boundaries and retain a trusted head/count outside the same writable directory.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import os
from pathlib import Path
import tempfile

from .independent_journal_audit import audit_export_bytes
from .journal import HashChainedJournal


@dataclass(frozen=True, slots=True)
class ImmutableJournalExportReceipt:
    """External custody receipt: never a cognitive memory or I0 event."""

    path: str
    occurrence_count: int
    journal_head_hash: str
    exported_bytes: int
    exported_sha256: str
    terminal_deaths: int

    def as_dict(self) -> dict[str, object]:
        return {
            "schema": "individual-zero-immutable-journal-export-v1",
            "path": self.path,
            "occurrence_count": self.occurrence_count,
            "journal_head_hash": self.journal_head_hash,
            "exported_bytes": self.exported_bytes,
            "exported_sha256": self.exported_sha256,
            "terminal_deaths": self.terminal_deaths,
            "physical_truth_verified": False,
        }


def export_immutable_journal(
    journal: HashChainedJournal,
    target: str | Path,
) -> ImmutableJournalExportReceipt:
    """Publish one lossless canonical journal image to a new local pathname.

    Writes and syncs a private same-directory staging file, then hardlinks it
    atomically to the NEVER-OVERWRITTEN destination. The canonical history and
    the individual's state are left untouched on success or error.

    An open physical step or incomplete death is refused by the independent
    auditor. Call from the operator boundary at a coherent scheduler point.
    This is explicit export, NOT guaranteed real-time crash persistence.
    """
    if not isinstance(journal, HashChainedJournal):
        raise TypeError("export requires the actual internal HashChainedJournal")
    destination = Path(target)
    if not destination.name or not destination.parent.is_dir():
        raise ValueError("export destination must have an existing parent directory")
    if destination.exists() or destination.is_symlink():
        raise FileExistsError("immutable journal export destination already exists")

    count_before = len(journal.entries)
    head_before = journal.head_hash
    if count_before == 0 or not journal.verify():
        raise ValueError("cannot export an empty or invalid technical journal")
    image = journal.canonical_bytes()
    if (len(journal.entries) != count_before
            or journal.head_hash != head_before
            or not journal.verify()):
        raise RuntimeError("journal advanced during coherent export preparation")

    # The separate, stdlib-only verifier owns all exported-event consistency
    # checks, including terminal boundaries and complete physical step pairs.
    audited = audit_export_bytes(
        image, expected_head=head_before, expected_count=count_before,
    )
    receipt = ImmutableJournalExportReceipt(
        path=str(destination),
        occurrence_count=count_before,
        journal_head_hash=head_before,
        exported_bytes=len(image),
        exported_sha256=sha256(image).hexdigest(),
        terminal_deaths=audited.terminal_deaths,
    )

    staging: str | None = None
    try:
        fd, staging = tempfile.mkstemp(
            prefix=f".{destination.name}.", suffix=".staged",
            dir=str(destination.parent),
        )
        with os.fdopen(fd, "wb") as stream:
            os.fchmod(stream.fileno(), 0o600)
            stream.write(image)
            stream.flush()
            os.fsync(stream.fileno())
        # link() never replaces an existing export, even in a race.
        os.link(staging, destination)
        # The final path now contains a complete fsynced canonical export.
        dirfd = os.open(
            destination.parent,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
        )
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    finally:
        if staging is not None:
            try:
                os.unlink(staging)
            except FileNotFoundError:
                pass

    return receipt
