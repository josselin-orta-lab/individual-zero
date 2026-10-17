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

## PR #246 targeted correction: one real active cognitive owner (Value/Needs)

The earlier model allowed privately consolidated `compiled_private` evidence to be read as if it were already cognitively activated. This new I1-only design makes the publication boundary explicit and strictly advisory:

1. `src/i1_overlays/i1_active_value_needs.py` implements the sole canonical Value/Needs owner for new natural I1 births. It carries a versioned, provenance-checked, non-authoritative active observed-procedure index. Existing TD Q weights/traces/counts, embodied needs, safety authority, Stage9 causal inference and metacognition remain unchanged. Invalid owner state fails closed.
2. The *generated I1-only Stage4* birth path selects that exact Value/Needs owner only when the actual runtime class is `I1Runtime`; experimental descendants and original Lab/I0 keep their original owner.
3. The generated Stage10's **paid sixth semantic pass** adds the active advisory candidate inside the actual validated consolidation transaction, never by mutating an already checked digest at publication time. This is the same `candidate` inspected by `Stage10PublicationCoordinator.prepare` and used in its synchronized hash-journaled two-phase `publish`.
4. Only the Value/Needs-specific prepare rebaser may add this advisory field. It starts from the **current owner baseline**, keeps every post-cut online TD update, validates source equality against private consolidated witnesses and forbids erasure of already published evidence. Other three owner rebasers remain identity-preserving. The genuine post-cut journal head must still remain identical through publish.
5. I1's paid recall now reads **only this committed active owner view**, never unpublished SlowHistory. Unknown commands are not authorized, predicted or marked safe. H1/H2 ablation and historical I0 remain outside the code path.

**Scientific and operational status:** This is a source-level implementation and requires real generator/build, Python import, full coordinated six-pass life, counterfactual/poisoned-provenance checks and M11 cold recovery before any scientific GO. No new tests or physical lives were run in this correction pass under the standing constraint. The PR #246 remains draft, not merged. Notably this does **not** claim fully generalized active causal-model, perception or kappa rebasing; they intentionally retain current-online state.

## Additional PR #246 active publication hardening

Commit `246d915e9e35945c9cb078ca81945ef7ce52fbc8` version-pins the canonical active Value/Needs advisory schema in its exported causal state (including empty births) and rejects incompatible cold M11 restoration. Active rows must use an exact approved set of fields; the primitive, parameters, physical effect, context anchor and stable skill identifier must agree with the deterministic firsthand evidence hashes. This prevents unreviewed, authority-like metadata from being smuggled into a published cognitive form and rejects unverifiable identity substitutions. The owner still preserves original TD fields untouched during preparation and only consultatively exposes approved observations.

This is static source hardening. New generator/import executions, sleep consolidation, coordinated commit and M11 cold recovery have not been run or claimed. CI at prior PR head included failures unrelated to this latest commit; PR #246 remains draft and NO-GO.

## M11 publication parity gate (continuation)

Commit `a80eac09e1f327ed246565fb14e67eeba4ab5b44` adds an I1-generated-only M11 custody check: immediately before capturing an owner image and after restoring the owners during a cold recovery, the canonical natural actor must have exactly the same active advisory records in its sole Value/Needs owner and in the committed SlowHistory `forms.value_needs`, which must match the compiled private provenance of the committed SlowHistory version. Historic experimental runtime types are excluded. Unknown forms, invalid active records or divergent active/private owners fail closed as `RecoveryBlocked` rather than being persisted as a consistent mortal life. M11 remains responsible for the actual SQLite generation and journal integrity.

No generated runtime execution or cold M11 recovery was performed. Historical CI at the prior commit still contains failures. This static safeguard does **not** establish scientific GO or authorize a merge.

## Natural I1 generated physics isolation CI contract repair

Commit `3fd196f8af518a137f4a9c0dc66fb061e3f60b9b` fixes the existing generated-isolation gate, which incorrectly required the disposable I1 physical-world module to equal the unchanged Lab source byte-for-byte even though the generated I1 schema intentionally includes birth-specific deprivation fields. The existing assertion now requires the generated world to equal the exact deterministic `i1_physiology_source(rewrite(source_world))` transformation of the unchanged Lab source. This verifies the versioned generated-world transformation without rolling natural I1 physiology back to inert reference behavior. No test suite was added or executed in this pass. Historic datasets are not used as scientific benchmarks. The PR remains draft pending actual technical and first-person scientific verification.

## Development campaign #247/#248/#249: four-owner publication foundation

Commits `28225a87`, `749184b7`, `fa570038`, `a2fe79c8` and `ee535141` introduce generated-I1-only publication views for CausalModel, Perception and Metacognition/Health in addition to the existing Value/Needs owner. The real Stage10 sixth-pass transaction now prepares four owner forms and the coordinator uses four explicit rebasers. Each new form remains a typed, non-authoritative record derived only from pre-cut authenticated autobiography. Causal association remains `hypothese_causale`, `validated_for_safety=False`; perceptual snapshots and agency reports are marked `observed_not_verified`, never reclassified as precision/kappa certificates. Existing online causal safety, kappa, precision, fatigue, health and TD values are not replayed or overwritten.

The three added registered owner views preserve the underlying canonical owner and add a committed observational index; they are cold-imported only through M11's authenticated one-time capability. M11 custody now checks parity of all four owner views with the same committed SlowHistory candidate. The I0 source snapshot and shared Lab are not edited.

**Scope / honesty:** This phase delivers an active observational publication *foundation*, NOT yet a demonstration of owner-specific generalized learning of causal rules or recalibration of kappa/precision. No simulator birth, independent scientific experiment, Python build, end-to-end six-pass commit, M11 cold recovery or new tests were executed. The PR stays draft / scientific NO-GO. Further development must prove that each owner can consume these records under its own rules and UC budget without confusing observations with verified causes.

## Current development pass: lived content in active owner forms

Commits `5ad8e9bf` and `91320c16` make the three-owner observational publication foundation more meaningful. P-42-paid interleaved replay now extracts only authorized autobiographical fields: (a) a real post-transition perceived position and finite body quantities, and (b) a lived agency comparison's status and attribution. Perception's active advisory index now publishes witnessed physical transition observations rather than opaque `s_t_published` references. Metacognition's advisory index carries the individual's actual agency judgement rather than only an event digest. Their canonical owner-view validation checks these structures; neither changes active precision or kappa without separate independent verification.

CausalModel continues to receive first-person command/effect hypotheses only, with no established causation or safety transfer. Value/Needs retains its own separate procedure evidence rules. No new tests were created or run, no M11 cold recovery or live birth was executed; this remains code candidate, not GO. Source I0/WorldBody not changed.

## Four-owner commit blocker removed

Commit `1472c97e` fixes an incompatible validation gate in `I1ActiveValueNeeds.prepare_stage10_advisory_rebase`: the existing Value/Needs rebaser required the *entire* candidate forms map to contain only `value_needs`, which made every correctly formed four-owner publication fail. It now requires exactly the four registered keys (`value_needs`, `causal_model`, `perception`, `metacognition_health`) and continues to validate and own only the Value/Needs portion. This preserves the atomic four-owner coordinator contract and prevents publication of a partial unexpected owner roster. The fix is recorded, not executed; no additional tests or model lives were run.

## M11 active owner parity applies before first publication

Commit `f0d87bc5` closes a pre-genesis/cold-recovery inconsistency. Previously the M11 parity function checked the three new owner views only when committed SlowHistory `forms` was nonempty. A previously uncommitted active owner observation could therefore be captured with an empty committed form map. The generated I1 M11 now checks all three owner views in both cases, requiring each to be empty before the first publication and exactly equal to its already committed, validated counterpart thereafter. This check operates before transactional capture and after cold installation. Code is committed; no tests or simulated life were executed, and the whole PR remains draft/NO-GO.

## Transversal I1 natural performance audit and first conservative optimization

GitHub recursive tree inspection of the current PR branch confirms 72 checked-in I1 source files, 13 I1 overlay files and 125 Lab source files. The living I1 runs from an isolated generated copy; the checked-in I0 reference remains untouched.

Identified optimization opportunities, ordered by safety:
1. **Repeated SlowHistory copies during each waking step and during paid sleep candidate selection.** Commits `c66c841d`, `1ca4f1bf`, `34974ea5`, `a3758759` add an O(1), immutable `frozenset` of committed episode identifiers to generated I1 SlowHistory and use it for awake pending counts and the metadata-only sleep selection phases. The cache is derived solely from the owner’s validated birth/restore state and reconstructed on every accepted history commit. It never replaces the full SlowHistory for actual P-42 charged evidence reads.
2. The six-pass semantic compilation and post-cut publication repeatedly validate and deep-copy full owner states. A bulk speed-up requires measured profiles plus proof of immutable detached snapshots and M11 atomicity before changing code. Do not skip any owner/hash guards or reduce P-42/P-43 charges.
3. Cold M11 recovery reads, validates and hashes the current generation and WAL repeatedly. These are safety-critical integrity checks; do not remove or reuse unauthenticated digests.
4. The cognitive phase cycle frequently materializes candidate states and evaluates options. Memoization is admissible only within a versioned, immutable capture and must never treat unobserved physical changes as known.
5. Unchanged I0/I1 source snapshot and Lab input must remain isolated. Any optimization affecting the runtime belongs in generated I1-only code, never the canonical I0 reference.

**Evidence limit:** no benchmark, generator invocation, new unit tests, full-life execution or M11 restore was conducted in this pass per the operator's existing no-new-tests restriction. Therefore no numerical speed-up is claimed. Optimization is committed as a source change only; PR #246 remains draft and scientifically unvalidated.

## Follow-up: constant-time waking backlog count

Commit `a1ac7627` removes another per-waking-step full scan of closed Memory episodes. Under the canonical living I1 append-only episode contract and charged Stage10 selection of existing closed episode IDs, `pending = memory.episode_count - len(slow_history.committed_episode_refs())` computes the same backlog in O(1) time; a negative count fails closed. The number of episodes for memory saturation is reused from the same immutable count. The existing fully charged sleep selection still reads actual evidence; no P-42 costs are reduced and no causal owner is bypassed. Performance improvement remains unbenchmarked and generated code remains unexecuted. A scientific or technical GO is not claimed.

## Consolidation optimization: scoped autobiographical materialization

Commit `7d286d93` optimizes the generated I1-only six-pass evidence input. Rather than construct a projected copy of every authorized autobiographical event across the life for each P-42 consolidation pass, `JournalViews.autobiographical(selected_event_refs=...)` constructs only the events belonging to the frozen, charged episode batch. Every AutoSegmentCommit and underlying source reference is still checked against its official policy; `FrozenLivedReplayEvidence` still runs the complete technical hash-chain verification, causal cut validation, no-future-event constraints and prohibition of events appearing in multiple episodes. The frozen episode payload mapping is copied once rather than twice. The general autobiographical API without a selection argument retains its existing full-projection behavior.

Complexity of *projection materialization* becomes proportional to the bounded batch, while the validation scan still depends on total history length. No time improvement is claimed without benchmarking. No tests or I1 physical lives were launched, respecting the standing instruction. I0 is unchanged, PR #246 remains draft.

## Consolidation pass per-unit copy reduction

Commits `6087de34` and `57505926` remove redundant *private* copies in generated natural I1's paid semantic unit path. The pass runner continues to detach the working candidate before invoking the handler and to validate/own the returned state. The general `LivedSixPassAlgorithm.handle` entrypoint retains a defensive copy for arbitrary callers; the canonical generated natural actor alone invokes `handle_detached` on the runner-owned copy. Per-unit evidence projection is additionally scoped to one selected replay event when the charged operation is `episode_replay`. Other pass operations retain their owned episode-identity checks, while `rule_extraction` retains the full per-episode lived pair scan. No uncharged autobiography becomes accessible, and candidate validation/checkpointing, P-42 logical UC, Stage10 publication and M11 custody remain unchanged. No performance ratio, GO or physical execution is claimed; no tests were created or run.

## Stage10 four-owner publication optimization

Commits `7e1de013` and `93b9cffe` reduce CPU and memory work during I1 natural four-owner Stage10 publication. The paid sixth pass continues generating and validating all four forms. At owner rebase time, each of CausalModel, Perception and Metacognition/Health now reconstructs and validates only its own form rather than rebuilding all four every time. The owner-specific source remains the frozen private lived evidence and the original schema/order/provenance/safety checks are retained. After coordinator.prepare detaches the baseline, its per-owner rebaser reuses that detached mapping instead of deep-copying the entire canonical owner a second time; coordinator.prepare continues its final validated ownership copy, and coordinator.publish still verifies live owner baselines before atomic activation. No tests, builds, scientific life executions or benchmarks were run in this pass; this is a structural optimization candidate, not a verified speedup or scientific GO.

## M11 performance review: scoped active publication attestation

Commit `c34ea3a7` removes cross-owner construction during the M11 h/active publication parity check. For the currently authenticated SlowHistory snapshot, the generated I1-only M11 gate reconstructs each of the three active observational views **only for its corresponding owner**, compares the published form and the independently exported live owner view, and continues enforcing the empty-before-first-publication invariant. The Value/Needs procedure provenance check is unchanged. No result is cached across steps or SQLite generations: each captured state remains independently checked against its actual owner and committed SlowHistory.

The complete SQL current-generation checksum, causal journal chain, append order, pending-intent fence, detached candidate and atomic publication are deliberately NOT short-circuited. These checks dominate potential long-life recovery cost, but skipping them without equivalent evidence would violate the unique physical authority of a mortal identity. No numerical performance claims are made, since code generation, execution, benchmarking and tests were not run during this optimization pass. The PR remains draft and scientific acceptance unproven.

## I1 static memory-path optimization, October 17, 2026

Static review found that the previous episodic recall reconstructed the same
current S_t competitive-reference set once per historical episode. The
I1-only generator now constructs it once for the recall call and reuses the
same set for each existing relevance check. Score formulas, threshold
crossings, ordering, UC and source-provenance semantics are unchanged by
construction. The pinned src/i1 source snapshot and I0 remain untouched.

The canonical I1 Value/Needs owner now detaches only *already published*
procedural rows matching a perceived option's primitive, parameters and
observed-effect family. The later provenance, independent-success,
spatial-context, confidence, safety and motor-admission guards are
unchanged, and the original P-43 read charge still precedes the lookup.
The filtered read remains a linear scan; it avoids cloning unrelated
nested evidence rather than introducing a second cache or causal owner.

STATUS: SOURCE-ONLY OPTIMIZATION CANDIDATES, NON VALIDÉ. No tests, code
generation, new lives or performance measurements were executed as part
of this revision. Neither equivalence under all states nor numerical
speedups are claimed before future independent validation.

## I1 private consolidation: anchor and index correction (2026-10-17)

Static source inspection exposed an accidental reassignment in the private
procedural compiler. The local `trials` variable initially referred to
ordered physical observation records, but later became a set of unique
episode identifiers. With more than one distinct successful spatial anchor
the next context's record scan would access string identifiers as records,
instead of scanning experienced events. The compiler now keeps the original
witnessed records in `witnessed_trials` and stores episode identities in
`trial_episode_refs`. This protects all spatial anchors while preserving
the independent-episode success/failure rule, sorted source witnesses,
private learning state and existing output schema.

The charged index-maintenance pass previously re-scanned every hypothesis
and every procedure for each distinct group key. It now groups identifiers
in a single traversal of each private form, then sorts the same keys and
identifiers. P-42 accounting, rule expiry, provenance and deterministic
serialized index structure are unchanged by design.

STATUS: SOURCE INSPECTION ONLY, NON VALIDÉ. Neither tests, benchmarks, CI,
generated-model execution nor simulations were run. Functional equivalence
and quantitative performance gains have not been measured. No I0 source
or normative contract was modified.

## I1 bounded active observational publication (2026-10-17)

Static inspection showed that each of the canonical Perception and
Metacognition/Health publication forms was sorted and deep-copied in full
even though its published projection retains at most 64 latest event
references. The I1-only owner compiler now streams those already witnessed
rows through a bounded min-heap keyed by (event reference, source ordinal).
The ordinal preserves stable sort selection for equal event identities.
Required raw source fields and observed-payload types are checked for
every eligible row, not only the winners; the 64 final nested observations
are detached, sorted and checked with the unchanged owner validator.
The complete private lived history remains preserved in SlowHistory.

The publication bound, provenance fields, six-pass computation, causal
ownership, postcut rebase, and M11 checks were not relaxed. This limits the
temporary selection buffer to 64 rows per observational owner and nested
deepcopies to 64 items per owner per build, instead of the number of
private matching records. No numeric runtime improvement or semantic
equivalence is claimed without execution.

STATUS: SOURCE INSPECTION ONLY, NON VALIDÉ. No tests, simulations,
benchmarks, generation or validation executions were run.

## I1 unknown-action candidate ranking without an intermediate list

The canonical inherited I1 affordance generator retained a complete temporary
list of scored candidates, then recomputed the winning command's signature
suffix. A source-only change streams exactly the same candidates in original
order, scoring each once and retaining only the best rank, command, signature,
lived Q state and suffix. It applies the same `(-evidence, time-rotated-index)`
comparison and retains the first result on exact ties. No decision priority,
physiological reward, tempered exploration coefficient, or UC charge was
altered. The visible candidate count and primitive list in the journal remain
based on the unchanged `choices` tuple.

STATUS: STATIC CODE REVIEW ONLY. No tests, simulations, benchmarks or
runtime build were executed; parity and quantitative gain remain non validated.

## Static long-horizon optimization: priced replay lookup and advisory rebase (2026-10-17)

In the I1-only private six-pass handler, the paid replay agenda already carries
the original in-episode event offset. The handler now accesses that offset
directly, verifies its identity against the agenda event reference, and
detaches only the selected event. An absent offset retains the prior bounded
linear lookup; a supplied invalid offset fails closed. Frozen episode
provenance, per-unit P-42 charging, sequential replay ordering, and canonical
pass checkpointing remain in place. This removes a repeated per-event
full-episode scan in the offset-bearing path without granting unpriced
history access.

During active Value/Needs publication, the Stage10 coordinator already
supplies an isolated baseline and subsequently takes a validated ownership
copy. I1's owner-specific advisory rebaser now updates only that detached
baseline rather than cloning the complete online state again. Pre/post
checksums of all non-advisory fields are retained, along with checked
proposal provenance, postcut owner-update checks, and the coordinator's
atomic publication boundary.

**NON VALIDÉ:** no tests, CI executions, simulations, generated I1 builds,
or benchmarks were run in this pass, per the instruction to continue code
optimization without testing. Runtime speedups, behavior parity and scientific
GO cannot yet be asserted. The original I0 source was not changed.

## I1 consolidation checkpoint digest metadata (2026-10-17)

Static source inspection found that `ConsolidationTransaction.candidate_digest`
rehashed the entire private SlowHistory candidate on every access. The pass
runner checks this property at each charged unit, and the incremental replay
agenda queries it while constructing a paid operation; the cost therefore
grows with the history size even when the candidate is unchanged.

Only the generated I1 `consolidation_transaction.py` now tracks an
**unpublished, derived current-candidate digest**. It is computed from the
owned initial JSON tree and updated upon a validated pass checkpoint, wake
interruption, and authenticated restore. All candidate assignment sites are
explicitly guarded by the generator. The current candidate remains detached
from caller arguments and checkpoints, while export/restore schema, chained
pass hashes, journal identity, M11 independent restoration verification and
UC prices remain unchanged. Birth construction also avoids revalidating
the same initial JSON history a second time before cloning the independent
candidate tree.

The cache is never the independent verifier of incoming state and is not a
serialized causal assertion. This prevents per-unit repetition of a
whole-history SHA-256 serialization; no time gain or functional parity can be
claimed until execution.

**NON VALIDÉ:** This is a static source optimization, not an executed
experiment. No model generation, tests, CI runs, benchmarks or simulations
were performed. I0 and the retained `src/i1` source snapshot are unchanged.

## Static copy-path optimization of canonical I1 (2026-10-17)

The generated Stage10 publication gate now checks `not canonical` before
reading `SlowHistory.read_committed()`, avoiding a full private-history
deepcopy for the current natural I1. The noncanonical branch retains its
original comparison, and canonical form-roster verification remains intact.

The generated I1-only pass runner passes the explicitly detached, paid
`frozen_episode_subset_copy` directly to the private semantic handler,
rather than cloning the same selected episode subset a second time. The
handler's candidate remains detached, P-42 charging precedes evidence
access, and the transaction owner retains its frozen episode source.
The runner also consumes the budget owner's already freshly constructed
causal-state export without an extra deepcopy. Budget identity checks
remain complete; exported causal-state keys and digests do not change.

STATUS: non validated. No tests, build, CI execution, benchmark, or
simulation was run. These are source-review improvements only; behavior
and performance gains require independent verification.

## I1 private pass-runner copying and recovery (2026-10-17)

Static inspection of `ConsolidationPassRunner` found repeated complete
materializations that had already crossed a checked ownership boundary.
The I1-generated implementation now constructs a sealed pass through
`ConsolidationPassPlan.from_state(plan.export())` without first deep-copying
the detached export. It begins a pass with the transaction's detached,
previously validated `candidate_copy()` instead of creating a second JSON
tree via `_json`. On finalization, it retains the runner-owned result until
the existing executor produces its separate detached copy for the
transaction's validated checkpoint.

During technical recovery, the snapshot digest hashes a new *shallow
top-level mapping* of the supplied state. No nested input is mutated or
retained through this validation, and `ConsolidationPassPlan.from_state`
already validates and owns each unit's JSON data, so a preceding full
deepcopy of `plan_raw` is unnecessary. The recovered working state still
passes through `_json` before being installed. Budget anchors, scheduler
gates, UC charges, candidate hashing, transaction checkpoints and
restore-before-mutation semantics remain as before.

These rewrites apply only to the generated I1, not I0 or the retained
unmodified source snapshot. Source anchors are guarded against drift.
STATUS: NON VALIDÉ, source inspection only, no tests, build,
CI, benchmark or simulated lives executed.

## Static I1 consolidation backlog selection and private indexed projection (2026-10-17)

The P-42 batch selector always computes and validates the priority score of
every admitted, charged episode. It previously sorted the *entire* candidate
list before keeping at most `maximum_episodes`. Generated I1 now uses
`heapq.nsmallest` with the same complete ordering key:
`(-score, -age_steps, episode_ref)`. All candidate inspections, score
validation, quoted work, repetition accounting and unselected episodes remain
unchanged. For N paid candidates and a small policy bound K, the selection
phase is O(N log K) rather than a full O(N log N) sort; the earlier O(N)
projection and scoring passes are intentionally retained.

Inside I1's charged pending-index owner, the private `_IndexedEpisode`
wrapper had copied its already owned payload when `as_dict` was called,
followed immediately by the selector's independently validated deepcopy of
the very same mapping. The wrapper now exposes the internal payload only to
that private selection boundary; `_projection` still checks canonical shape,
serializability and creates the detached snapshot stored by the selector.
The public Memory Episode projection, `_pending`/`_ranked` independence,
charged cursor, serialized snapshot fields, journal provenance and I0 all
remain unchanged.

**NON VALIDÉ**: static-source assessment only. Per request, no test, build,
benchmark, CI or simulation was executed. The ordering equivalence and lower
selection complexity are reasoned from the code, not measured experimentally.

## I1 checkpoint retention and interruption/finalization copies (2026-10-17)

Source inspection distinguishes the **necessary** independent
`_initial`, `_candidate`, and validated `PassCheckpoint.candidate` trees
from extra transient copies. Those persistent versions are deliberately
retained: they are needed for private checkpoint integrity, chained evidence validation and
M11 causal snapshot restoration. No snapshot schema or six-pass checkpoint
was removed.

In the generated I1 transaction only, `interrupt()` now changes the
transaction to suspended without re-copying the last validated checkpoint.
The private current candidate already equals the last checkpoint (or the
independently owned initial state), because all transaction entry points
copy into private state and a unit's unfinished working candidate exists
only inside the separate pass runner. Neither `_candidate` nor checkpoint
data is exposed by reference through public read methods. As the candidate
itself is unchanged, its existing privately cached SHA-256 digest stays
valid, and no extra whole-history digest is needed at wake.

In the generated I1 runner only, `finalize_pass()` hands the runner-owned,
unpublished result directly to the transaction's executor. The transaction
still performs `_owned(result)` before validation and creates a separate
deepcopy for its immutable checkpoint. The runner clears its working
reference only after successful completion; no change occurs to pre-debit
P-42 checks, handler evidence isolation, technical validation or
journal publication.

**NON VALIDÉ**: these are strictly static source deductions, not tested
behavior or measured performance. Per request no tests, builds, CI,
benchmarks or simulations were executed. I0 and the pinned I1 snapshot
remain unchanged.

## Static I1 M11 journal reads and cold-history reconstruction (2026-10-17)

A hot path in the independent SQLite mortal coordinator previously created a
tuple of **every historical journal occurrence** to obtain only its count
(`len(journal.entries)`) and again to enumerate only the newly appended
generation's suffix. Each cold-imported occurrence also recreated the whole
tuple simply to inspect its last entry. The internal journal already maintains
an append-only list and returns the exact committed entry from `append()`.

The generated I1lab HashChainedJournal now exposes a read-only O(1)
`entry_count` and an `entries_since(start)` suffix snapshot with an explicit
nonnegative in-bounds cursor contract. The legacy `entries` property and its
immutable-tuple semantics remain unchanged for all other consumers. The
generated M11 coordinator uses the bounded reads, and during cold restore
compares the returned entry directly with the independently validated durable
row. The generated SQLite registered-owner capture and offline WAL auditor
also read the same authoritative list length without full tuple allocations.

These are structural allocation optimizations, **not** shortcuts around
`journal.verify()`, the cryptographic chain, canonical encoding, durable
SQLite intent fencing, ownership checks or the full causal image. The
existing serialization of authenticated event data remains intact, and the
authoritative journal writer does not change. No I0 source is modified.

**NON VALIDÉ**: source inspection only. No generator, tests, CI, simulation or
benchmarks were executed, and no numerical speedup or complete behavioral
equivalence is claimed.

## I1 Stage10 postcut journal verification and bounded replay (2026-10-17)

Static inspection showed that `Stage10PostCutJournal.validate_no_intervening_updates`
verified the entire append-only journal before calling `freeze()`, which
then verified that entire chain a second time. The generated I1-only
implementation now calls `freeze()` once: it still cryptographically
verifies every journal occurrence, checks the exact causal cut, rebuilds
the complete authorized postcut update digest, and rejects mismatched
end-index, end-hash or digest. There is no cached trust assertion and no
assumption that previously verified entries cannot be tampered with.

The same private I1 journal coordinator now uses the already verified
`HashChainedJournal.get(event_id)`, `entry_count`, `head_hash`, and
`entries_since(cut_index + 1)` to avoid constructing a tuple of every
historical occurrence merely to inspect the point of consolidation or
rebase the postcut suffix. The cut index and identity are checked together
after the complete SHA-256 verification, and the processed update sequence
and serialized digest fields are unchanged. The legacy `entries` API is
preserved for callers requiring whole-journal snapshots.

No skip, no relaxed provenance, no new cognitive prior, and no changes to
the original I0 or lab sources. **NON VALIDÉ:** source-only modification;
tests, generator execution, benchmarks, CI and simulations were not run,
and no runtime gain or behavioral equivalence is claimed.

## I1 M11 verification: avoid defensive copies while rehashing (2026-10-17)

Source review found that the protected journal event mapping deepcopied
nested values on every read, including each read made by the full
hash-chain verifier. Yet the journal already owns a private detached
event dictionary captured during append. Generated I1lab now adds an
internal encoder that hashes that owned dictionary directly, returning
only immutable canonical bytes, not a mutable reference. All entries
are still reserialized and SHA-256-verified on every integrity check.
Public `JournalEntry.as_dict()` and `causal_event` remain detached.

An O(N) seen-identifiers set was redundant: the one-to-one
`_by_id[event_id] is entry` check, equal index cardinalities, and
sequential per-occurrence index check already prove uniqueness.
The generated verifier omits the duplicate set and checks that each
owned event is still the expected private wrapper type.

No journal records, hash algorithms, M11 custody rules, owner schemas,
external observations, causal evidence or I0 source changed.

**NON VALIDÉ:** no tests, generated code execution, benchmarks, CI or
simulations were run. Only static inspection supports the change; no
measured performance gain or proven runtime parity is claimed.

## I1 post-cut owner replay: remove a second deep copy (2026-10-17)

After authenticating the entire journal, Stage10 freezes each published
owner update from `JournalEntry.causal_event`, whose private
`_DetachedCausalEvent` mapping deepcopies nested values when read.
The `data` field, or the selected root precision fields, are therefore
already independent of the hash-chained journal before the post-cut
snapshot is assembled. The I1-generated post-cut adapter now constructs
only a fresh outer dict for that previously detached payload, instead of
deepcopying those newly detached nested values a second time.

The full SHA-256 chain verification, owner-kind validation, cut index,
causal time, `VerifiedOnlineUpdate` fields, digest and M11 publication
boundaries remain unchanged. The patch is guarded by the exact original
source site and applies only to generated I1lab. No I0 code changed.

**NON VALIDÉ:** static inspection only; no generator, tests, CI,
benchmarks or simulations were executed. Gains remain unmeasured.

## I1 selective M11 owner-export detachment (2026-10-17)

The I1-generated SQLite current-state capture now skips one redundant
full-state deepcopy for **exactly** two previously audited owner types:
`SlowHistory` and `ConsolidationSlot`. The former exports independently
deepcopied current-state and lineage trees; the latter exports a new
envelope whose active transaction already returns a completely detached
private JSON tree. No subclass or unrecognized owner is exempted.
All other owners still receive the prior defensive deepcopy, and every
captured export still undergoes canonical causal-tree validation and
the immutable SQLite generation hash. The whole journal is verified,
owner roster checks remain intact, and the physical/clock second reads
continue to detect drift during the quiescent capture.

No I0 or original lab files are modified; only generated I1lab gets this
exact-type guarded change. **NON VALIDÉ:** no generation, tests, CI,
benchmarks or simulations were executed; behavioral parity and numerical
gains are not asserted.

## I1 Stage10: eliminate duplicate full-history candidate copies (2026-10-17)

Static code inspection identified two redundant materializations along the
scheduler-authorized consolidation-publication path:

1. `ConsolidationTransaction.validated_candidate()` already returns a
   privately detached JSON candidate after its validator has completed.
   The generated I1 Stage10 coordinator therefore consumes that candidate
   directly, rather than immediately re-encoding and deep-copying the entire
   history with `_copy_causal()`.
2. `SlowHistory.restore_causal_state()` independently validates the complete
   staged replacement and deep-copies the newly published current state.
   The generated I1 coordinator may attach its already detached prepared
   candidate to the local staged mapping without another full-history copy
   before this owner-owned restoration. A separate tentative `SlowHistory`
   instance still validates the complete version/lineage before any
   publication, and the original `before_history` baseline-consistency
   snapshot remains independent.

**Unchanged**: all four baseline cognitive-owner snapshots, rebase isolation,
canonical validation of the owner-prepared states, journal cut/head checks,
P-42 charges, six-pass receipts, two-phase publication, and fail-closed
termination if a publication installation fails. The transformation is confined to
generated I1lab; neither I0 nor the source lab implementation is touched.

**NON VALIDÉ**: source review only. No generator build, unit test, CI,
benchmark or simulated life was executed. Runtime equivalence and performance
gains remain to be demonstrated independently.

## Generated I1 M11 ledger: eliminate duplicate full-state canonicalization and old-state reparse (2026-10-17)

Static source review of the I1lab SQLite custodian found two entire-state
operations repeated during every physical generation:

* In `SQLiteLifeLedger.audit()`, canonical encoding of the decoded current
  state was used once for an exact raw-byte comparison and again inside
  `_canonical_state()`. Generated I1 now uses the latter's fully checked
  canonical bytes for the same exact comparison. Both the registered-owner
  schema check and byte-identical canonical verification remain mandatory.
* In `commit_generation()`, the old state bytes were reread from SQLite
  and JSON-decoded solely to determine the registered owner roster's SHA.
  The preceding complete `LifeReceipt` already contains
  `registered_roster_hash`. The M11 `verified_intent` path rechecks
  the old SQL state digest and roster under `BEGIN IMMEDIATE` using
  `_checked_current_anchor`; an ordinary non-verified caller performs
  `audit()` in that same locked transaction. The generated I1 code
  compares the receipt's verified roster SHA to the newly validated
  metadata without a second old-state JSON decode.

In particular, these source-only changes do **not** remove full causal
occurrence replay audits, state hash checks, the write-intent fence,
the registered-owner inventory check, atomic WAL commit, the post-COMMIT
audit, or terminal receipt verification. The fallback non-M11 transaction
path retains its complete audit. The original I0/lab source remains pinned.

**NON VALIDÉ**: no model generation, tests, CI runs, benchmarks or
simulated lives were performed. The elimination of repeated O(state-size)
serialization/parsing is established by code inspection, not measured.

## I1 full SQLite audit: one validated owner envelope, bounded digest operations (2026-10-17)

The generated I1lab `SQLiteLifeLedger.audit()` still validates every retained
causal occurrence before permitting any further step, and the existing
post-COMMIT full audit remains mandatory. The optimization is entirely
within that checked traversal; **no historical event is trusted because
it was validated in an earlier call**.

Static inspection found that `_canonical_state()` validated the current
owner-roster metadata, then `audit()` validated that same envelope again
after processing every causal occurrence. A private I1-only helper now
returns both the exact canonical state bytes and the already verified
roster metadata in one pass. The standard `_canonical_state()` still
returns bytes to all other callers. After validating the exact SQLite
state bytes, the auditor releases its large decoded current-state mapping
before beginning the full journal scan. Its verified roster/status/count/head
metadata is retained to check the final independently recomputed journal
head and the external stored owner-roster hash.

The audit SHA-256 chain also keeps the previous digest in its native
32-byte form instead of hex-decoding the previous occurrence's hash for
each next event. Each occurrence still undergoes canonical JSON validation,
exact index/ID/previous-hash checks, recomputed SHA-256, terminal sequence
verification, and the final journal count/head comparison. The value used
for the stored hash comparison remains `.hex()` of the real SHA-256 digest.
No cached trust or shortcut is introduced.

The I1-only generator refuses unexpected source anchors. No I0 or original
lab source or historical experimental result was used as a baseline.

**NON VALIDÉ:** static code review only. No code generation, tests,
CI execution, benchmarks, or simulated lives were run; memory and speed
benefits remain unmeasured and full behavioral parity unproven.

## I1 SQLite metadata reuse on birth/commit and binary suffix hashing (2026-10-17)

Source-only optimization of the generated I1lab SQLite custodian extends
the existing private `_canonical_state_with_metadata` helper. Birth now
receives the fully checked canonical state bytes and the already validated
roster metadata from that one helper call, instead of invoking
`registered_current_metadata` again immediately. During
`commit_generation`, the newly proposed current state is likewise
canonicalized and owner-roster-validated once. The returned metadata
is checked against the **independently audited and transaction-pinned**
previous-generation roster hash exactly as before. Neither the SQL intent
fence nor the old-state digest and roster checks are bypassed.

During insertion of the new generation's append-only event suffix, the
verifier retains the preceding SHA-256 digest as 32 bytes, converting it
to a lowercase hex string only for the stored row and cross-checks.
The validated head string is decoded once before the loop rather than
once per appended occurrence. Every new event is still independently
encoded, SHA-256-rehashed, terminal-sequence-validated, inserted under
the same SQLite transaction, and compared to its claimed event hash.

**Not optimized away:** the full pre-step and post-commit SQLite journal
audits, per-owner causal capture, post-private-step detection of mutations
to the published individual, and post-commit validation before publication
all remain mandatory. An audit result does not become an across-step
cache of trust. Original I0 and baseline Lab sources remain untouched.

**NON VALIDÉ:** per instruction, no code generation, tests, CI runs,
benchmarks or simulations were executed. Exact performance gains and
runtime equivalence remain unmeasured.

## Static Stage10 staging-state and Value/Needs evidence comparison (2026-10-17)

Further review showed that `Stage10PublicationCoordinator.publish()` first
obtains a fully detached `SlowHistory.export_causal_state()` snapshot for
prepublication consistency checks, then performs an unnecessary `deepcopy` of **that entire history**
just to stage a new `current_version`, replace `current_state`, and append
one provenance row to `lineage`. Generated I1lab now creates a shallow top
level mapping and a new lineage list only, before replacing the new state.
Neither the original `before_history` (needed for baseline consistency comparison) nor any
existing lineage row is mutated. `SlowHistory.restore_causal_state()`
continues full structure validation and creates independent copies of the
new state and lineage before committing them. The separate temporary
SlowHistory validation remains unchanged, as does the journal cut/receipt
boundary.

In the natural I1 Value/Needs rebaser, `expected` is built exclusively
to compare the compiled procedural rows against the proposed already-private
owner form. There is no mutation of these expected rows. Sorting can therefore
operate on row references in its *own new list* rather than deep-copying
each complete row, its source/trial references and nested context. Source
provenance, exact comparison, advisory validation, unchanged online TD
checks and final owner-copy boundaries all remain in place.

**NON VALIDÉ:** no generated model, test, CI, benchmark or simulation was
executed. This is a guarded source-only optimization; runtime parity and
performance gains require future independent validation. I0 is unchanged.

## I1 normative clarification: irreversible life, no published-owner rollback (2026-10-17)

The operator confirmed that I1 must NEVER rewind a lived step or restore a
dead individual from an earlier version. Normative MVP v1.3.3, V133-MDL-07
already prohibits rollback, postmortem cognition and resurrection.

Static inspection found a contradictory exception handler in Stage10:
after attempting to install active-owner states, it restored previous owner
snapshots whenever journal append had not yet succeeded. The generated
canonical I1 Stage10 coordinator now raises a fail-stop error regardless of
whether the journal record was appended, and never re-installs those earlier
live cognitive values. On the same attempted execution, the existing mortal
Stage10.run_step exception guard irreversibly halts technical dispatch, and
the SQLite M11 wrapper poisons any uncertain generation and refuses recovery.
The original Lab/I0 source retains its historical behavior unmodified.

Canonical I1 Value/Needs previously tried to reinstall its preceding TD
state upon a failed owner restore. That historical-state restoration has
also been removed: an invalid installation now propagates failure to the
mortal owner boundary. No physical transition is replayed.

**Distinct mechanics:** discarding unpublished private candidate work, or
SQL ROLLBACK of an *uncommitted SQLite transaction*, does NOT resurrect a
living individual or negate a physically applied command. These storage
operations remain necessary for crash atomicity. M11 cold recovery admits
only the exact, authenticated, fully committed current nonterminal generation.
Technical halt is represented as technical halt, not fabricated physical
death. A genuine lethal WorldBody transition is irreversibly dead, and no
further perception, deliberation or learning is authorized.

**NON VALIDÉ:** source-only correction; no generation, tests, CI runs,
benchmarks or simulated lives were executed. Runtime behavior remains to
be independently verified.

## Canonical I1: remove Meta/Health compensating rewind and O(N) Stage10 journal counts (2026-10-17)

The inherited `_MetacognitionAndSleepCustody.restore_causal_state` previously
exported two complete snapshots of the living Metacognition and SleepHealth
owners solely to *reinstall* them after a partial restore failure. This
contradicts the clarified irreversible-life rule. The generated I1lab
Stage10 implementation no longer creates either rollback-only snapshot or
performs a compensating owner restoration. It still validates the combined
custody envelope and passes independently detached state to each owner.
Any exception propagates to the existing mortal Stage10 fail-stop boundary.
During cold recovery, a failed import aborts an as-yet-unpublished new
runtime; it never selects an earlier generation or revives a terminal life.

In the same generated I1lab Stage10 publication coordinator, the journal
was unnecessarily materialized as a complete tuple **three** times just
to compute its current length, including in the fail-stop error branch.
The generated `HashChainedJournal.entry_count` accessor already returns
the exact length of its append-only private list. The publication
coordinator now uses that O(1) count instead. The deterministic activation
event ID, journal index, full chain verification when required, receipt
identity, owner integrity and irreversible publication contract are
unchanged. I0 and original shared Lab source remain untouched.

**NON VALIDÉ:** static source inspection only. No generated build, tests,
benchmarks, CI runs or simulations were performed. No numerical gains or
runtime-equivalence claims are made.
