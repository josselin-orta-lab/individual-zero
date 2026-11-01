# From an engine proposal to an independently reviewed generation

An engine proposal is a source **scaffold**, not a born individual. This
process is designed to prevent accidental registration or reuse of another
engine's Lab, cognitive policy, persistent identity or historical scientific
results.

1. Create an inert source proposal with `tools/new_engine.py` and inspect
   the generated `src/iN/`, `tests/iN/` and `src/iN/docs/` trees.
2. Run `python tools/assess_engine_proposal.py --generation I2 --json`.
   A new scaffold is deliberately **BLOCKED**, because its cognition, Lab,
   runtime and independent tests are placeholders.
3. Implement real independent modules. Do not import the parent's `i1lab`
   runtime, overwrite its evidence, or make any rollback of living states.
4. Prove separately: birth/observations, UC accounting, owner publishing,
   mortal termination, authenticated M11 recovery, fault injection and
   experimental validity. The assessor does **not** run tests or attest
   scientific readiness.
5. **Only after an explicit architecture and science review** can a separate,
   manually approved registration and activation proposal be considered.
   No tool in this campaign registers, activates or imports a future engine.

The static `no_parent_runtime_imports` check retains its historical output name but now rejects imports of **any other generation** (including I0 and future generations), selected direct/dynamic imports and symlinked source trees. A dynamic target that cannot be checked statically fails closed. This cannot prove absence of custom loaders, `exec`, third-party transitive dependencies or shared mutable services; independent review remains mandatory.

The report's `STRUCTURE_PRESENT_REVIEW_REQUIRED` status means only that
static source structure exists. It is not a merge gate, authorization to
execute, scientific GO, or a guarantee of runtime correctness.

## Mandatory independence review

Before architecture review, registration or promotion, apply [ADR-0001](../decisions/ADR-0001-strict-generation-autonomy.md). Treat the manifest's `parent` as history, not runtime inheritance. Require an independently owned engine, Lab/WorldBody, Scheduler UC, M11, safety, persistence, tests and cold recovery. Refuse old-mode fallback, direct or indirect imports of obsolete-generation runtime, shared mutable owner, imported identity/memory and silent migrations. Retain previous engines exclusively as isolated research comparators and archives. Respect the existing active I1 and its authentic born state; a structural assessment alone never authorizes birth or scientific GO.
