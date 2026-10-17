# From an engine proposal to an independently reviewed generation

An engine proposal is a source **scaffold**, not a born individual. This
process is designed to prevent accidental registration or reuse of another
engine's Lab, cognitive policy, persistent identity or historical scientific
results.

1. Create an inert source proposal with `tools/new_engine.py` and inspect
   the generated `src/iN/`, `tests/iN/` and `docs/engines/iN/` trees.
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

The report's `STRUCTURE_PRESENT_REVIEW_REQUIRED` status means only that
static source structure exists. It is not a merge gate, authorization to
execute, scientific GO, or a guarantee of runtime correctness.
