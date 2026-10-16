# I1 PR #245 continuation: temperament and birth path

Source: development branch `feat/i1-natural-integrated-recovery-20261016`. No source files in original I0 or shared Lab modified.

- Canonical `I1Runtime` now supplies the immutable Stage11 temperament projection used by its own unknown-affordance evaluator, fixing the previous missing-property access.
- `i1_birth_temperament.py` deterministically derives five independent traits from the I1 life identifier and uses the existing Stage5 mapping to freeze the projected parameters in Stage11Config before birth. The full changed config is included by the existing I1 M11 runtime-contract hash; it cannot legitimately change across cold recovery.
- `i1_birth.py` provides one direct public factory `birth_i1` that constructs a mortal I1, without requiring historical H1/H2/D2 research-arm flags or extra opt-ins.
- Stage10 consolidation **still declines active-form publication** requiring unimplemented owner-specific verified post-cut replay. This guard must not be bypassed: the slow history can still retain private provenance but not invent live skills or duplicate TD updates.
- No software tests, executions, or scientific validation have been performed. Factory runtime compatibility remains unverified, and a separate coherent M11 SQLite birth factory requires validation. Keep PR draft and issue open.

## Continuation: completed code-level wiring, not execution proof

- Temperament projection now changes the *real* Stage4 Gatekeeper weights,
  Value/Needs weights and Competition inertia inside the frozen Stage9
  configuration, instead of only setting a descriptive Stage11 projection.
  The Stage10 config receives this exact same Stage9 subtree at birth. This
  corrects contradictory wake/sleep nested contracts and avoids live mutations.
- Only in the generated I1 Stage10 runtime, validated `procedural` records
  with `state=compiled_private` may now be durably included in private
  SlowHistory. Active owner forms must remain identical to the prior state.
  The existing post-cut verified online-update freeze, coordinator, hash-chain,
  two-phase publication, private index accounting and no-double-TD rebase are
  retained. **No active procedural execution is enabled.** Active-form
  changes still defer under `active_form_rebase_not_implemented`.
- `birth_i1_m11` offers an explicit SQLite-only fresh birth path and
  `recover_i1_m11` delegates to the existing strict M11 cold-recovery
  verification. The original WAL-based `birth_i1` remains a separate mode;
  they must not coexist for one life.
- No tests, builds, CI runs, recovery operations or physical lives were
  executed under the previous operator constraint. Source implementation is
  therefore still **untested**; these are proposed code-level safeguards, not
  a demonstration of successful SQLite recovery or consolidation.

Remaining integration gate: this PR stack is not merged into main. The
new code and historical studies cannot be assumed scientifically equivalent.

## Continuation: generator integration correction

The generated-I1-only `i1_private_consolidation_source` builder transformer accidentally used escaped literal backslash-n sequences in its Python source-matching template rather than newline escape sequences. That prevented matching the exact two-line Stage10 active-form publication guard. Commit `9bdbcbbcc2dca327328feaaac44a572ff9515a36` corrects the template so it targets the actual source shape.

The intended semantics remain narrowly scoped:
- Private SlowHistory may retain observed hypotheses and provenance-checked `compiled_private` procedures.
- Changes to *active* forms continue to defer until a verified per-owner post-cut rebase exists.
- Online TD, kappa and precision values are not replayed or overwritten.
- The original shared Lab and I0 stay unmodified.

Audit observations, NOT proof of execution: the Stage4 reference computation budget already declares `goal_arbitrate` under the `goal_manager` module; no new unpriced GoalManager operation was added in this pass. The I1 generated M11 rewrite already replaces the Stage12 exact-type gate in three source occurrences with an `isinstance` gate, so the natural Stage12 descendant can be considered by M11; whether its complete independent owner graph can actually cold-recover remains unverified.

No scripts, tests, builds or new lives were executed under the standing no-additional-tests instruction. All new functionality and cold recovery still require technical verification before an integration or scientific GO.

## Final static safety review (2026-10-16)

The I1-generated M11 type gate was broadened to every Stage12 descendant in an earlier version. That admits experimental subclasses whose owner graphs, cold-state contracts and snapshot responsibilities may differ. This is not defensible for irreversible mortal SQLite custody.

The generator now allows the original exact Stage12 type **or only the exact canonical `I1Runtime`**, while retaining the existing M11 SQLite opt-in and fresh-body requirements. It injects the local canonical-class import into the same local M11 method scopes using their existing indentation. This does not certify cold restoration: it only tightens the code-level acceptance boundary. No caller can infer that all Stage12 subclasses are transaction-safe.

The consolidation active-form rebase remains intentionally fail-closed. Private hypotheses/procedures in SlowHistory are not promoted to active or safety-authoritative skills. The archived A2.38/A2.39 experiments remain immutable.

### Finalization gate that is still missing

No source build, Python 3.11/3.12 execution, M11 real birth/recovery, WAL audit, physical lives, or independent scientific review was performed. The GitHub head has zero status checks and zero workflow runs in the inspected revision. Therefore the requested scientific GO and merge into main are **not authorized by evidence**. The PR remains a technical candidate, not a completed verified integration.

## Continued generator audit: actual M11 import syntax

On this revision, code review detected that the I1-only generator had still emitted a literal backslash-n sequence between local M11 imports. The earlier indentation correction did not eliminate this defect. Commit `aa541207a75e1f1b093c0546e71e7f07549bb235` replaces it with an actual source newline. Commit `4808dd1aae722295994dec4d6648b11ee24fa3dc` adds a deterministic generation-time assertion requiring all three exact canonical actor import scopes. Both are I1-only generator changes; no original I0 or Lab module is edited.

**Remaining gates:** actual source-generation/build and a new mortal I1 birth have still not been executed. There is no executed M11 cold recovery or confirmed active-form reconciliation. All previously documented source-level claims remain provisional. Do not merge #245 or claim scientific GO on static inspection alone.

## Continued restoration: general Stage6 planning and honest unplannability

Commit `cf86f97aade3e99fffba6f5d6f3a888b666ae3f3` enables Stage6 progressive subgoals in the canonical I1 constructor by default, using single-step prefix and fresh-physical-capture revalidation. This changes the **actual frozen Stage6 config nested inside Stage11 and Stage10**, never the historic fixture. Progress can be credited only to a physically predicted change in the active homeostatic measure or food-inventory acquisition as a partial capacity, never as full satiation. The I1 uncertain-affordance option continues to represent unknown consequences explicitly and must still compete under Stage9 and Action Control.

The same commit excludes degraded cognitive cycles from GoalManager non-plannable failure accounting: insufficient UC is not proof that a need cannot be met. Native GoalManager remains in charge of refractory releases, not H1.

These modifications are committed source, not verified behavior. No additional tests, builds, independent cohorts or execution were run. Original I0/shared Lab and A2.38/A2.39 histories are unchanged. M11 active-form rebase remains fail-closed and this PR remains draft.
