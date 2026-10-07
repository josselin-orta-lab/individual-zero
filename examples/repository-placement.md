# Repository placement examples

These examples are fictional and exist only to explain placement.

## Example 1: add a cycle timer

Goal: measure how long each I0 cycle takes.

Placement:

- timing instrumentation: `src/lab/`;
- test for timer output format: `tests/`;
- EXP only if timing instrumentation itself can alter studied behavior.

Reason: timing is observation infrastructure, not cognition.

## Example 2: change memory recall priority

Goal: change which memory item I0 prefers to recall.

Placement:

- mechanism: `src/i0/`;
- scientific comparison: `experiments/EXP-####/`;
- reusable recall benchmark, if shared: `benchmarks/`.

Reason: the change directly affects cognitive behavior.

## Example 3: integrate an external memory package

Goal: use an external package that exposes vector retrieval.

Placement:

- I0 memory role/interface: `src/i0/interfaces/`;
- API translation: `src/adapters/<package>/`;
- integration tests: `tests/`;
- EXP if the package can alter reference recall behavior.

## Example 4: correct a malformed log line

Placement:

- fix: `src/lab/`;
- regression test: `tests/`;
- no EXP unless the malformed logging also changed execution behavior.

## Example 5: redefine a shared cognitive interface

Start with an EXP if the interface change can alter behavior or interpretation.

If evidence supports a shared structural change:

- implementation: `src/i0/`;
- evidence: `experiments/`;
- shared decision: `docs/decisions/ADR-####-...`;
- architecture docs updated after the decision.
