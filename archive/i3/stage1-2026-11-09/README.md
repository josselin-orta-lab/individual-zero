# I3 Stage 1 archive — closed 9 November 2026

Stage 1 is **closed negative** under ADR-0018. The final Candidate-J software
falsifier returned `CANDIDATE_J_DEFECT`; P1.3 remains the reference and Stage 2
is unblocked on P1.3. ADR-0017's world-opening moratorium is unchanged.

This archive removes closed Stage-1 scientific runners and their direct tests
from the active I3 research surface without deleting their Git blobs. Files
under `legacy/` keep the exact blob identity they had at their original paths.

## What remains active

The archive is deliberately conservative. It does **not** move:

- Stage-1 result directories and original evidence, because they are part of
  the scientific custody chain and are heavily linked by reports;
- Candidate F-I runtime modules that are still imported by
  `src/i3/runtime/life.py` for historical-policy compatibility;
- module/runtime regression tests covering those compatibility paths;
- ADR-0017 engineering repairs and lifecycle-custody stress tools still useful
  to the two-phase G/R, engineering-cohort and sealed-rehearsal work;
- `stage1_candidate_g_reference_recurrence_falsifier.py`, because the retained
  lifecycle-custody stress imports it.

## Final Candidate-J evidence

The final result remains at:

- `src/i3/docs/studies/stage1-candidate-j-software-falsifier/RESULTS.md`
- `src/i3/docs/studies/stage1-candidate-j-software-falsifier/results.json`
- `src/i3/docs/studies/stage1-candidate-j-software-falsifier/IMPLEMENTATION_NOTES.md`

The owner-supplied deployment package was verified against its
`SHA256SUMS` before integration. Its original pre-execution and closure commit
identities are recorded in `deployment/MANIFEST.json`:

- `15e8d3d485b913057b3d6a794ec19ca95ba251c9`: implementation and notes,
  committed before execution;
- `0c41b4a1f988d7b9721f134e613dc0a49e05eb54`: results and closure entries.

Those two commit objects were supplied in a prerequisite Git bundle but were
not already present on GitHub. The integration therefore preserves their
identity in the deployment manifest while merging the verified content through
the repository branch. The scientific result is not re-executed.

## Operational rule

Do not restore an archived Stage-1 runner to continue Stage 1. Any later reuse
must be a new, explicitly justified experiment under the then-current research
stage and governance. Historical evidence is evidence, not a hidden queue of
unfinished candidates.
