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
