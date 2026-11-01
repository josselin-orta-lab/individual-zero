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
5. **ADR-0008 removes mandatory external architecture/science reviewers** as a condition for building or testing the isolated prototype. Registering a successor as the active generation remains a distinct owner release decision after demonstrated capabilities and documented risks; a green check does not authorize promotion.

Proposal and repository boundary scripts (`tools/assess_engine_proposal.py`,
`scripts/check_engine_repository.py`, `tests/test_engine_repository.py`)
route to the **lightweight** `i2-proposal-safety.yml` on a PR. The light
workflow runs its inert I2 tests plus the static registry/archive guard; these
files alone must not launch the living I1 SMOKE + FULL matrix. Changes under
`src/i1/**`, active I1 tests, I1 behavioral tools, engine contracts or the
I1 workflow itself retain the full I1 CI. Workflow edits are reviewed and
tested by exact path assertions, and this routing change is not a G1 or G3 GO.

Generation names are canonical: `I2` through `I9`, then `I10`, `I11`, and later positive decimal identifiers without leading zeros. Preview generation and proposal assessment accept these labels but never register, activate or birth a generation. `I0`, `I1`, `I02`, lowercase names and suffixed labels are refused.

The static `no_parent_runtime_imports` check retains its historical output name but now rejects imports of **any other generation** (including I0 and future generations), selected direct/dynamic imports and symlinked source trees. A dynamic target that cannot be checked statically fails closed. This cannot prove absence of custom loaders, `exec`, third-party transitive dependencies or shared mutable services; technical inspection remains necessary.

The report's `STRUCTURE_PRESENT_REVIEW_REQUIRED` status means only that
static source structure exists. It is not a merge gate, authorization to
execute, scientific GO, or a guarantee of runtime correctness.

## Independent generation ownership (not mandatory third-party reviewers)

Before architecture review, registration or promotion, apply [ADR-0001](../decisions/ADR-0001-strict-generation-autonomy.md). Treat the manifest's `parent` as history, not runtime inheritance. Require an independently owned engine, Lab/WorldBody, Scheduler UC, M11, safety, persistence, tests and cold recovery. Refuse old-mode fallback, direct or indirect imports of obsolete-generation runtime, shared mutable owner, imported identity/memory and silent migrations. Retain previous engines exclusively as isolated research comparators and archives. Respect the existing active I1 and its authentic born state; a structural assessment alone never authorizes birth or scientific GO.
