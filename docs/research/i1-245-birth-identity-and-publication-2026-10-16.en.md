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

## Continued correction: eliminate extra phantom mortal birth

Commit `0b7b52054eb4db8a64661a386a5beb5563805316` replaces the call to `build_stage5_reference_runtime(autonomous_mortal=True)` inside canonical I1 temperament construction with the same published Stage5 reference mapping parameters expressed as a pure immutable `TemperamentMappingConfig`. Values continue to use the **actual current I1 Stage4** neutral base weights and inertia. Temperament is projected once from the declared life identity; no auxiliary WorldBody, second mortality authority, Scheduler or journal is created simply to determine coefficients.

This is a source-only correction. No new test, build, physical birth, M11 cold recovery or scientific trial was run. The original I0, source Lab and frozen historical experiments were not edited. Stage10 active-form publication remains deliberately fail-closed without verified owner-specific rebase. PR #245 therefore remains draft / NO-GO.

## Consolidation correction: evidence-source contract and batch size

Code review identified two coupled blockers in the I1-specific consolidation path:

1. The private compiler required a `stage10_plan_applied` autobiographical event, but no ordinary integrated I1 stage produces that event and it is not a Stage7 allowed autobiographical kind. The compiler would therefore produce zero procedures indefinitely.
2. The default sleep selection admitted exactly one episode per cut despite requiring `skill_success_threshold=2` distinct successful episodes. A newly born life could never compile one private procedure from a single cut.

Commits `2e096f5d5696c156841590112c521af8bb8ca6bf` and `9f696bf9496f35ac632e47e59132d5a2e56dd7fd` change only the I1 living policy and I1 cognitive semantic module:

- Batch selection now caps at four independently lived episodes. Each episode scan, replay and semantic pass remains priced under P-42 and can defer if work is unavailable.
- A *private* one-step procedural record is derived solely from an already authorized autobiographical pair of `command_experienced` and `world_transition_experienced` at the same actual world step. Only explicitly recorded positive physical effects qualify as success. Negative effects remain failures. Distinct successful episodes are required. Neither the hidden world, an unverifiable `stage10_plan_applied` event nor replayed duplicates contribute evidence.
- Such a record is limited to `state=compiled_private`. It documents that a primitive action previously succeeded in a local context. It does **not** prove that a distal goal succeeded, that berries are safe, or that the actor caused an ambiguous external change. It is never made executable by this patch and does not alter Stage9 or Action Control.

**Outstanding:** compiler source has not been executed; successful private consolidation, SQLite M11 cold recovery and active-form owner rebase remain unverified. The original I0, Lab, A2.38/A2.39 historical source and data are unchanged. No tests or new physical lives were run under operator instruction. PR remains draft and scientific NO-GO.

## Continued correction: durable private procedural lineage across sleeps

Commit `461671f99fed7690ee2fcea874af46d63558125b` removes a memory-loss regression in the I1-only six-pass semantic private procedure compiler. Previously, each new paid sleep transaction assigned a new `procedural` list to the private candidate and silently forgot all earlier procedures not compiled in the latest batch. The new implementation retains previous private procedures and merges additional evidence for identical procedure/context identities only when source episode IDs and event IDs are disjoint. It recomputes distinct success/trial counts and the empirical success rate, rejects conflicting identity, malformed or overlapping provenance, and leaves all procedures `compiled_private`. It does not authorize new motor primitives, weaken Stage9 or Action Control, or bypass active-form rebase.

Remaining limitation: evidence aggregated in separate nonoverlapping batches is summarized as observed local action success, never independently verified causal responsibility or food safety. Active-form M11 owner replay and end-to-end technical validation remain unimplemented/unexecuted. No tests or simulated lives were run. The stacked PR remains draft/NO-GO.

## Additional source correction: private evidence must not masquerade as a plan or safety proof

Commit `592d1bec3f11dc39282a8799a49c3e1bd73c4f23` tightens the I1-only semantic private compiler. The same autobiographical world step now requires the single physically experienced command to precede the single physically experienced transition in the journal-approved projection. Without a pre-action position in that projection, *movement* is not compiled as a context-stable private procedure: the arrival position alone cannot establish a repeatable departure-site affordance. Observed local outcomes for other commands are stored with their exact primitive, parameters and result field, and explicitly carry `goal_success_inferred=False` and `safety_certified=False`. These descriptors are pinned as immutable across later private-evidence merges.

This correction deliberately does not turn private procedures into action authority. Active ownership of causal, metacognitive and value forms remains unchanged; an owner-specific verified post-cut rebaser is still required before publishing active learning. Neither cold M11 restoration nor the resulting cognitive behavior has been executed or independently verified, as no tests or new lives were run. I0, shared Lab and historical runs remain untouched.

## Isolation and epistemic correctness continuation

- `72a4e469`: natural I1 now installs the versioned living metabolism, sleep motivation, and consolidation profile in its **canonical `I1Runtime` constructor** before birth. This remains default-on for ordinary I1 and retains I0 isolation.
- `2a0a7b9e` and `8a51fcfb`: removed the global generated Stage11Sleep constructor patch and its obsolete helper. Previously all generated Stage12 descendants, including historical A2.38/A2.39 ablation runtimes, had their sleep and world parameters silently modified. Those explicit experimental configurations are once again untouched by the natural policy.
- `eda732ca`: physical `ate=berry_*` is no longer deemed procedural success by itself. An ingestion event is a witnessed act, not evidence of safe or beneficial nutrition. Toxic-food confidence cannot be manufactured by private consolidation.

No tests, generator runs, newborn physical lives or M11 cold-recovery have been executed. Active owner semantic rebase stays fail-closed. These source changes are a code candidate, not a scientific GO. I0 and original Lab are unchanged.

## Isolation correction: deprivation is opt-in for historical ablation types, default-on for canonical natural I1

The isolated I1 builder previously added `starvation_integrity_damage_per_step=0.5` and `dehydration_integrity_damage_per_step=1.0` as unconditional dataclass defaults for *all* I1-generated worlds. Although natural sleep was recently moved to the canonical constructor, these shared world physics defaults still silently modified historic A2.38/A2.39 arm configurations. Commit `4d4ab22c` now extends the generated WorldPhysicsConfig schema with zero deprivation defaults, leaving controlled old I1 ablation configs unchanged when not explicitly overridden.

Commit `d6d02fb1` restores gradual starvation (0.5) and dehydration (1.0) as **mandatory birth-time defaults in the canonical living I1 natural physiology installer**, along with the previously versioned food/water per-step decay and energetic costs. Explicitly nonzero environmental damage values remain untouched. I0 and common source Lab physics are never modified.

The existing world transition still applies real post-action deprivation before death determination; no new hidden sensory data enters cognition. This is a code-only scope correction. No tests, build, lives, cold M11 recovery, or scientific calibration were performed. PR #245 remains draft / NO-GO.

## Latest correction: refractory accounting is one physical observation, not one cognitive cycle

Commit `6e5c08776de487c845b1829db15a849da4170b1c` prevents a physically unchanged I1 capture from being counted repeatedly as multiple unplannability failures merely because Competition runs several cognitive cycles in the same world step. The natural actor now records at most one UC-paid `note_non_plannable` event per actual captured world step and active goal. The durable goal/refractory state stays owned by GoalManager; the new per-step runtime marker is a non-causal optimization, with no impact on past physical state or M11 cold replay. Refractory transitions still require genuinely distinct lived observations, not simulated extra episodes.

Further technical evidence is still necessary before any GO, including generator execution, new births, M11 cold restore and active-forms owner rebasing. No tests or physical lives were run.

## Natural planning ownership corrected

Commit `dc76685e8e7eb68ba762f9516823f69f48f9bdbc` prevents the inherited experimental unknown-affordance proposer from silently overriding an already produced Stage6 plan in the canonical living I1. The natural runtime now considers an uncertain command only when the existing causal Stage6 proposal is absent. The experiment-specific behavior remains unchanged on historical subclasses. Unknown consequences remain unknown, and every candidate still requires ordinary Competition, Stage9 and Action Control admission. No tests, model lives, or M11 recovery executed; PR remains draft/NO-GO.

## New I1-only paid read-only private procedural recall

Commit `81a412242ae443597a9f493f98b86522d9f3ec3b` introduces a bounded P-43-paid advisory read from already committed private SlowHistory, without promoting private procedures into active CausalModel/ValueNeeds/Metacognition/Perception forms. It is available by default only to ordinary canonical I1 births. An existing Stage6 plan still takes priority. For an otherwise genuinely offered unknown local action, exactly one matching witnessed primitive/parameters/outcome-field family from the committed history may raise its *prior consideration evidence* by at most 0.12. The match requires a locally witnessed contextual radius, at least two distinct successful episodes, a bounded success rate, provenance references and explicit no-goal-success/no-safety assertions. No private skill creates commands, grants motor authority, supplies predicted consequences, or certifies berry safety. A dedicated planning UC operation is reserved in the versioned natural constructor and charged before reading private history. This read-only path avoids the unsafe owner-specific post-cut active-form rebase.

**Important outstanding validation:** this code was not built or executed. Whether the memory traces are produced in actual sleep, exactly how natural affordance evidence composes under Competition, M11 cold recovery and the six-pass publication sequence are unverified. Prior instruction to avoid tests has been respected. The PR remains draft/NO-GO, and the dependent PR stack remains unmerged.

## Current correction: optional private recall and real per-action energetic pricing

- Commit `a25cad767c77b0598c2b7ef6d46c551918ffe947` gates the optional private-memory recall by a **pure Scheduler UC capacity quote**. When there is not enough ordinary planning budget, the recall declines without charging, degrading the cycle, overwriting the pending valid exploratory option or bypassing Stage9. If it is affordable, a genuine P-43 `_charge` still precedes inspection of committed SlowHistory.
- Commit `d7a69ca4996c761f6c620c9de0c53dbcb5059433` fills inert zero-valued per-primitive energy costs in the canonical I1 birth profile even when some other actions were already explicitly priced. Existing nonzero prices remain intact. Every value is frozen prebirth in the WorldPhysicsConfig/M11 digest. Original I0 and separate experiment runtime constructor behavior remain unchanged.

No tests, compiled source build, physical births, private replay, active rebase or M11 cold recovery were executed. PR #245 remains draft/scientific NO-GO.

## Finalization audit continuation: immutable reward sensitivity in Stage8

Commit `aa3575571d7681ff64811c86f015b8e1b0efcba4` connects an already projected, birth-frozen temperament's `extrinsic_value_gain` to the real Stage8 `Stage8EvaluationConfig.extrinsic_gain` in the nested Stage9 constructor config, prior to any real mortal birth. This was previously descriptive-only for this evaluation owner even though Gatekeeper, ValueNeeds and Competition had received the other projected components. The value is preserved through the common Stage10/Stage11 Stage9 substrate and M11 birth fingerprint. No live owner mutation, implicit external reward prior, I0 edit or historical research-arm constructor modification.

The PR remains a **source-only candidate**, not proof of successful execution. Compiler/build and M11 cold restore could not be demonstrated. No new tests or physical cohorts were run, honoring the current operator restriction. The source-only audit cannot establish scientific or operational GO, so the dependent draft PRs are not merged.


## Finalization continuation: preserve unsuccessful-trial provenance

Commit `27c2a36018c55d42cda28890b23fb67d894cdcf3` repairs the private procedural evidence denominator. Previously only successful episode/event refs were persisted, while `distinct_trial_count` included failures. Subsequent merges could silently re-count an earlier failed trial as a fresh trial and change the claimed empirical rate. Private records now carry independent `trial_episode_refs` and `trial_event_refs` including failures; the merge requires both successful and all-trial provenance to be distinct across batches. Mixed success/failure evidence within one episode is conservatively counted as a failed trial, never as an unqualified success. Private forms still make no success-of-goal or safety claim and do not become executable.

The source is committed but not executed: no build, test, mortal birth, M11 cold recovery or active owner publication has been demonstrated. Earlier user direction prohibited additional tests. PR #245 and its prerequisite drafts remain unmerged; the scientific status is still NO-GO and finalization cannot be claimed.

## Scheduler UC occurrence custody correction

Commit `793c21cfe61301530fd0a5003523bf454711a2f3` enables the existing Scheduler cycle-occurrence guard by default for canonical new I1 births. A second opening of the same physical world step, attempt and cognitive cycle cannot reset the UC budget. This is birth-frozen and remains isolated from I0 and historic experimental runtimes. No execution, CI, M11 cold recovery or scientific cohort was run; active-form owner rebase remains an unresolved integration gate. PR is draft/NO-GO.

## Cross-sleep accumulation of incomplete lived procedural evidence

Commits `9e2bfe998501a302660c9a25df3737f889a0c3ad` and `8a876425f8369ec7040034dffc69a980bdeb1a19` address the failure to learn a local physical affordance from independent successful experiences occurring in different sleep cuts. First positive evidence is now retained as `witnessed_private`, which is **not considered a compiled or executable skill** and is ignored by the existing recall reader. Repeated success in a later disjoint, provenance-verified cut can promote it to `compiled_private` only after meeting the versioned `skill_success_threshold`. Event and episode anti-double-count protections remain, and Stage9/ActionControl and all active-form owner rebase guards remain unchanged.

This is a source-level patch, not a validated successful sleep or actual M11 recovery. No new tests were added or run at the user's prior direction, and no scientific lives were executed. The stacked PRs remain draft and are not fused into `main`; scientific GO cannot be claimed.

## Verified GitHub CI failure and source-snapshot repair

Existing I1 isolated-fork CI run `38971433532` failed on both Python 3.11 and 3.12 at `test_i1_source_snapshot`: direct edits to `src/i1/modules/consolidation_semantics.py` had violated the immutable I0/I1 exact source snapshot requirement. This has been corrected without changing the cognitive improvements: `src/i1_overlays/i1_semantics_template.txt` retains the enhanced module, and `scripts/build_i1_fork.py` emits it only into the generated `i1/modules/consolidation_semantics.py` after verifying the source snapshot is unmodified. The checked-in `src/i1` file was reverted exactly to `src/i0`.

Verified through GitHub's actual recursive tree (71 Python I0 files): **zero differing blob SHAs between `src/i0` and `src/i1`**. No new tests, test suites, simulator lives or cold recoveries were executed. CI jobs previously recorded other failures; these remain to be investigated and are not implied fixed by this repair. The active owner replay gate is still fail-closed, and PR integration stays draft/NO-GO pending execution evidence.

## Additional existing-A2.38 CI failure fixed at code level

The existing A2.38 smoke GitHub Actions job `117210488455` failed with `AttributeError: 'I1A238ExperimentalRuntime' object has no attribute 'temperament_parameters'`. The shared I1 unknown-affordance implementation started reading Stage11's projected temperament but only the canonical natural subclass declared this property. Commit `50a71e534d6811cd7dc4c4d6ddee96e8ca57f853` exposes the actual frozen Stage11 parameter projection on the existing I1 experimental Stage12 ancestor as well, restoring historical experimental compatibility without altering experimental birth personality defaults. The canonical actor continues to use its birth-derived projection.

No new tests or simulations were executed. The source repair is supported by archived CI diagnostic evidence but remains unverified by a subsequent passing CI run. PR #245 and the cumulative draft integration PR #246 remain unmerged pending actual review.
