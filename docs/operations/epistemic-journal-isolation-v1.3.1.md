# MVP v1.3.1: epistemic custody of the exhaustive I0 journal

## Threat boundary

The complete `HashChainedJournal` belongs to the technical Lab runtime, not to
the cognitive `Memory`, `S_t`, Perception, Exploration, or the Oracle. The
scientific `EvaluationTrace` belongs to the independent evaluation process.
The full technical journal **must retain** even future-scenario and hidden
hazard input events; their occurrence is never itself first-person knowledge.

Only versioned `AutoSegmentCommit` sources may become autobiographical
projections. The projection code drops unknown nested fields for known
Stage-7 cognitive event types. Explicit Oracle/Bench evidence is rejected
even if buried inside an otherwise accepted source value. This prevents the
technical journal from silently becoming a semantic memory as schemas grow.

The independent journal auditor rejects external Oracle/Bench provenance,
including nested fields, and checks that candidate Stage-7 projection data
conforms to the same accepted semantic shape. It does **not** treat legitimate
hidden-world scenario operations as leaks when they are merely retained in the
technical record and excluded from first-person projections.

## Access boundary and limitations

The `runtime.journal`, `JournalViews.technical()`, and
`runtime.world.ground_truth()` methods remain operator/runtime-level Python
interfaces for compatibility and complete audit custody. They are **not**
capabilities granted to cognitive components. Every `i0.modules` component
must be constructed with narrow typed views, never with the Lab runtime,
journal, WorldBody, Oracle or Bench as an argument.

This is module-level data-flow isolation in an in-process Python runtime,
**not** a hardened process sandbox against arbitrary Python code executing
inside the interpreter. Fully adversarial plugins or runtime introspection
need separate address spaces, restricted process permissions and a future
migration decision; they cannot be made safe merely by renaming properties.

No modification here deletes the technical journal, alters world physics,
changes the Stage-10 post-cut owner receipt stream, makes an Oracle mandatory,
or confers scientific acceptance on 600-step runs.

## Validation and review

Run `python -m unittest tests.test_epistemic_journal_isolation tests.test_journal_views tests.test_independent_journal_audit -v`
and the normal unit suite on both Python 3.11 and 3.12.

The tests show that an external secret world-coordinate input remains in
the full technical chain while unexpected nested data does not pass into
`Memory` projections; they reject embedded Oracle labels, technical keys,
cross-attempt autobiographical references and false external provenance.

An additional operator-owned end-to-end trial is still required to establish
that real scenario perturbations do not affect inaccessible cognitive
state, and code review must verify that no new cognitive service receives
the technical runtime or unrestricted WorldBody.

This change is software hardening only. Stage sign-off and final scientific
validation remain distinct requirements.
