"""Extended Stage-9 software reference, NOT preregistered science or Golden.

EN MVP v1.2.1 section 20.1: each stage needs exact replay and retained
reference evidence. Reexecute the same real Stage-9 runtime independently;
compare complete journal bytes and every canonical causal owner state.
This is a diagnostic only, not held-out causal acceptance under section 20.3.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path

from .determinism import canonical_causal_bytes, sha256_hex
from .stage9_reference_fixture import build_stage9_reference_runtime


PROTOCOL_VERSION = "stage9-extended-reference-diagnostic-v3"


@dataclass(frozen=True, slots=True)
class Stage9ReferenceDiagnostic:
    protocol_version: str
    steps: int
    journal_bytes: int
    journal_sha256: str
    journal_head: str
    causal_owners: int
    causal_state_sha256: str
    identical_independent_reexecution: bool
    classification: str = "diagnostic_only"
    scientific_verdict: None = None
    golden_stage9_frozen: bool = False

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, indent=2) + "\n"


def generate_stage9_reference_diagnostic(
    *, steps: int = 300, journal_path: Path | None = None,
    causal_state_path: Path | None = None,
) -> Stage9ReferenceDiagnostic:
    """Independently rerun the unchanged Stage-9 fixture for a fixed duration.

    Do not use a copied snapshot, injected causal hypothesis or bench oracle
    to obtain equality. A non-applied world step fails this diagnostic rather
    than shortening the advertised reference window.
    """
    if type(steps) is not int or steps < 1:
        raise ValueError("reference requires a positive integer number of steps")

    def execute() -> tuple[bytes, dict[str, object], str]:
        runtime = build_stage9_reference_runtime()
        for index in range(steps):
            outcome = runtime.run_step()
            if outcome.execution_status != "applied":
                raise AssertionError(
                    "Stage-9 reference step was not applied: "
                    f"{index + 1}/{steps} ({outcome.execution_status})"
                )
        if not runtime.journal.verify():
            raise AssertionError("Stage-9 reference journal integrity failed")
        owners = {
            owner.owner_id: owner.export_causal_state()
            for owner in runtime.causal_owners
        }
        if len(owners) != len(runtime.causal_owners):
            raise AssertionError("Stage-9 replay has duplicate causal owner IDs")
        return runtime.journal.canonical_bytes(), owners, runtime.journal.head_hash

    first_journal, first_owners, first_head = execute()
    second_journal, second_owners, second_head = execute()
    if (
        first_journal != second_journal
        or first_owners != second_owners
        or first_head != second_head
    ):
        raise AssertionError("Stage-9 independent reference execution diverged")
    # Export *exactly* the normalized bytes used for the diagnostic digest.
    # The owner map is a software reference, never a held-out causal witness.
    first_state_bytes = canonical_causal_bytes(first_owners)
    if journal_path is not None:
        # Archive the *exact* bytes named by journal_sha256, without an
        # extra line terminator that would break independent raw-file audit.
        journal_path.write_bytes(first_journal)
    if causal_state_path is not None:
        causal_state_path.write_bytes(first_state_bytes)
    return Stage9ReferenceDiagnostic(
        protocol_version=PROTOCOL_VERSION,
        steps=steps,
        journal_bytes=len(first_journal),
        journal_sha256=sha256_hex(first_journal),
        journal_head=first_head,
        causal_owners=len(first_owners),
        causal_state_sha256=sha256_hex(first_state_bytes),
        identical_independent_reexecution=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Stage-9 exact replay diagnostic; never a Golden",
    )
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--journal", type=Path)
    parser.add_argument("--causal-state", type=Path)
    args = parser.parse_args()
    print(generate_stage9_reference_diagnostic(
        steps=args.steps, journal_path=args.journal,
        causal_state_path=args.causal_state,
    ).to_json(), end="")


if __name__ == "__main__":
    main()
