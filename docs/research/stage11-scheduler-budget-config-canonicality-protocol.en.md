# Stage 11: canonical, fail-closed versioned Scheduler UC configuration

**Public software protocol registered 2026-10-11 BEFORE code, tests, or measurements.** Normative source exclusively `docs/architecture/reference/en/mvp-specification-v1.2.1.md`, notably §16.3, S-11/P-43 and INV-21/INV-22, plus deterministic configuration/replay §17.1–17.6. Scientific claims and goldens are **out of scope**. Stage 11 IN PROGRESS; Stage 9 scientific NO-GO.

## Source audit before intervention

Current branch `i0/vnext-stages-10-12`, HEAD `ec5f9145c4347a6b51be21124f438a9a95d5beab`, PR #25 Draft/open/unmerged. `CycleComputeBudget.open_cycle`, `charge` and `restore_causal_state` have already been strengthened in distinct, SHA-pinned work. Latest full CI on source/test `ee9aa8803e4e81045c4a2defd5224036eff92de8`, [#38139987533](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38139987533), shows 908/908 PASS Python 3.11.17 and Python 3.12.15. This is previous evidence only, not validation of the present change.

`ComputeBudgetConfig.validate` still performs `value < 0` without exact-integer type checks, allowing booleans, fractional numbers, NaN and other noncanonical UC values into the Scheduler. Version and module/operation identifiers need exact-string validation, while protected membership needs a stable `frozenset` of declared module IDs. Nonmapping or unhashable inputs currently raise incidental `AttributeError`/`TypeError`. A malformed versioned config could therefore produce fractional, nonfinite or truth-valued `BudgetCharge.requested_uc` even when `count` is canonical. This is an actual API boundary defect, not evidence of learned physical facts.

## Frozen correction scope

1. `ComputeBudgetConfig.validate()` fails closed with **`ValueError`** unless `version` is a non-empty exact `str`; `cycle_ceiling`, `protected_capacity`, every module envelope and operation cost are exact built-in `int >= 0`; and protected capacity is at most `B_cycle`. **Zero costs and zero ceilings remain supported** for legitimate declared diagnostics. No silent coercions/rounding/normalization or invented values.
2. `module_envelopes` and `operation_costs` must each be non-empty **Mapping** objects with exact non-empty `str` keys and valid integer values. Immutable mapping wrappers such as `MappingProxyType` remain legal. `protected_modules` is required to be an exact `frozenset` of non-empty exact `str` entries, all present in `module_envelopes`; including zero, one and multiple protected IDs is legal. No changes to the existing requirement of explicitly configured costs/envelopes.
3. Validation must finish **before** `CycleComputeBudget.__init__` starts an owner, opens a cycle, or charges work. Invalid config calls neither publish nor consume UC. The accepted config and all prior valid snapshots, journal bytes, owner IDs and public Stage-11 budget probes must remain unchanged when the input was already valid.
4. Do **not** modify `CycleComputeBudget.open_cycle`, `charge`, `quote_operations`, `restore_causal_state`, snapshot formats, P-43 cost tables, module algorithms, priority thresholds, protected-capacity semantics, root normative specification, or historical scientific protocols. Do not solve possible *later mutation of caller-owned config dictionaries* in this increment; note it separately if demonstrated, as a distinct ownership boundary needing dedicated tests.
5. Repeat `validate` must be deterministic and must not mutate caller mappings; reject invalid values before creating any owner. No new CI workflow triggers or force-push.

## Synthetic software gates frozen now

- Use the preexisting 10-UC worker/control budget and vary one configuration field at a time with `dataclasses.replace`: invalid version representations, boolean/fractional/NaN/nonfinite/text/categorical UC ceilings, protected capacity, module envelopes, operation costs, missing/extra/invalid module identifiers, non-Mapping values, mutable/untyped protected collections and protected IDs not declared in envelopes.
- Assert every invalid case raises `ValueError` from both `validate()` and `CycleComputeBudget(config=...)`. Repeat both after prior valid config use; no configured value is silently corrected, converted or rounded.
- Positive boundary matrix: unchanged standard config, immutable `MappingProxyType` costs/envelopes, valid zero ceilings/zero-cost operations, multiple protected modules and no protected modules. Verify exact owner-state/snapshot and `BudgetCharge` data in two fully independent runs, with identical snapshot capture schedule and technical journal bytes/hashes. Positive control also runs two cycles with legal integer UC charges.
- Include a fail-closed case with explicitly invalid NaN cost that would otherwise result in NaN consumption, and confirm no owner is constructed; normal charged results remain integer-valued. No tests are to be bypassed or adjusted to match changed behavior.
- Execute targeted suite and adjacent regressions first, at most one `ci-unit` PR CI by label; if green, one distinct Python 3.11/3.12 full CI when proportionate, conserving Actions minutes. Document SHA, command, Python patch, test counts, exact failures/exclusions, artifacts and limitations.

**Scientific gate NOT addressed:** held-out, historical Goldens, hazard learning, autonomous recovery, human-equivalent behavior and Stage-9 NO-GO. **Further independent technical question:** can `open_cycle` legitimately reopen the same active cycle and reset spent UC? Investigate that only after this config gate with a separately registered protocol.

PR #25 must remain Draft, open and unmerged; no edits to `main`, permissions, visibility, protections or normative MVP specification.
