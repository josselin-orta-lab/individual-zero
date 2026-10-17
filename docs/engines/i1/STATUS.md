# I1 development status

**Date:** 2026-10-17. **Generation:** I1 (active).
**Parent reference:** I0 (frozen).
**This is an engineering ledger, not scientific GO.**

## Authority

- Declarative contract: [engine.json](../../../src/i1/engine.json).
- Registry: [engine-registry.json](../../../config/engine-registry.json).
- Architecture map: [ARCHITECTURE.md](ARCHITECTURE.md).
- Validation obligations: [TEST_PLAN.md](TEST_PLAN.md).
- Native migration evidence: [I1_NATIVE_MIGRATION.md](../../engineering/I1_NATIVE_MIGRATION.md).

## Current implementation at creation of this ledger

- I1 birth: `i1lab.i1_birth.birth_i1`, canonical `I1Runtime`.
- Four published cognitive owner families: values/needs, causal model,
  perception, metacognitive health.
- Per-generation Lab: `src/i1/lab/`; native implementations in
  `src/i1/runtime/`. I0 Lab archived at `archive/i0/lab/`.
- M11 authentic SQLite cold recovery and irreversible death exercised by
  current CI. The disposable `i1lab` build remains a **compatibility
  dependency**, not yet a fully direct importable native runtime.
- Structural migration PRs: #251 (archive I0), #252 (generation tooling),
  #253 (I1 native code and versioned Lab). This campaign is stacked after
  #253; verify real GitHub state before merging.
- A CI pass is not proof of emergent intelligence, long-run learning, or
  independently validated active publications.

## Unresolved engineering and scientific gates

- Prove genuine **nonempty Stage10 publication by all relevant owners**
  from experienced events, followed by consistent cold recovery.
- Maintain M11 refusal gates for corrupt state, ambiguous COMMIT and owner
  mismatch; extend fault-injection when transaction boundaries change.
- Replace transitional namespaced build only with proven output and
  persistence compatibility, not by a path rename.
- New preregistered scientific evaluations must use *current* natural I1;
  previous broken experimental cohorts are not acceptance oracles.
- Every future generation needs its own Lab and its own evidence.

## Working agreement

Update this page with factual PR/commit links and new unresolved issues at
the end of each campaign. Do not mark a scientific property achieved on the
strength of software tests alone. No automated rollback of living states.
