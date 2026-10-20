# PR #318: goal-neutral opportunistic local interactions, 2026-10-20

## Frozen base and provenance
- Base review SHA: `1a0e810047f65c621d37cd3678980dc695372a40` (PR #318, draft).
- Original prospective workflow: https://github.com/josselin-orta-lab/individual-zero/actions/runs/39382123672
- Physical birth SHA: `67a5a51237fe68b13e09e442fa3615ac03ad4c7b`; eight successful paired GitHub jobs, two worlds and seeds 20123, 20233, 20357, 20477. Each arm has independent births and a 300-step horizon.
- Reported job logs, not yet independent 16-WAL audit: baseline seven alive, one dead at 228 physical steps; experimental eight alive. Baseline 2328 lived steps, 655 consolidated objects, 101250 accepted UC; cross-goal 2400 steps, 923 consolidated objects, 75066 accepted UC. These are descriptive aggregates, not an authenticated causal certificate. Research-only route-rank counters are UNATTESTED.
- Exact paired cohort was run **before** the subsequent separation-of-producers patch. Do not attribute these outcomes to the later code.

## Verified architecture defect in the former prototype
- `_consider_uncertain_affordance` originally expanded active-goal filters but returned just one selected candidate to the same `_proposal_this_cycle` slot. Thus an unrelated local exploratory action could replace the active goal's proposal before Competition instead of competing against it.
- The resulting Option and Plan had `goal_ref=goal.id`, and Competition could invalidate them on goal change. This did not fully decouple observation from goal choice.
- Stage6 already exposes local physically available `boire`, `manger`, `collecter`, `poser_une_pierre`, `fabriquer_outil` via the actual perceived SimulationState. The local generator must not infer their consequences.

## Development after the original 16 lives
- `32da539`: remove cross-goal expansion from the ordinary goal-bound generator; broaden physical local interaction set and version its opt-in policy.
- `c3e795d`: add a separate Planning phase-1 candidate and separate Competition phase-3 registration, using the same evaluator/Competition, real Planning/Competition UC, available first-person commands, explicit deduplication, neutral goal references, no motor dispatch and no need-value oracle.
- `8d2908c`, `b2f0066`: adjust tests for added legal primitives and supplied candidates.
- `95fc8b1`: bounded regression workflow.
- All changes remain in I1; I0 is untouched. Opt-in `i1_cross_goal_local_opportunities` remains disabled by default.

## Open scientific obligations / NO-GO
1. The original workflow's SUCCESS proves its jobs completed, not that each opportunity reached Competition or improved learned behavior; independently inspect all 16 original WAL paths and transitions.
2. Run an **entirely new** control/treatment cohort at the new source SHA with source-matched binary and fresh birth identities. Record accessible -> locally proposed -> registered -> evaluated -> crossed -> admitted -> motor-applied -> first-person follow-up -> learned reuse. Same physical commands selected through a goal-bound path must not be mistaken for local-opportunity successes.
3. Determine whether added independent options increase Competition cost, cognition/fatigue and sleep, suppress need decisions, or lead to repetitive failed interactions. Verify cross-goal goal changes and M11 cold recovery.
4. Review `I1 current-model validation` parity failures against the separate generated migration snapshot. Its byte-comparison control is not evidence that a modified runtime is semantically incorrect, but CI must not be declared green.
5. No GO, promotion, merge, I0 edits, forced drinking, coma, rollback, replay of dead lives, or fixed survival enhancement may be claimed.

**Scientific decision:** INCONCLUSIVE for this newly committed producer, NO-GO for canonical promotion. Next step: independently auditable physical cohort on a pinned new source commit, then M11 and population hold-out.


## 2026-10-20 continuation: independent UC custody and prospective validation

- Identified under-reservation: the independent producer can add a second Planning charge plus its own Competition registration and additional per-candidate Competition evaluation, while the old configuration reserved only the maximum charge of two *alternative* goal-linked paths. An unfunded cycle may degrade unrelated cognition, so a comparative survival change cannot be attributed solely to adding opportunities until independent UC is budgeted.
- Commit `ff76a24d` reserves separately charged Planning UC and Competition registration/evaluation UC **only for opted-in local exploration**; canonical disabled births retain their own original cost envelope. This is capacity for actual charged work, not free cognitive work.
- Commit `d8f1944a` re-pins the exact reviewed generated I1 active runtime blob in the migration byte-parity validator. The validator still rejects unrelated unreviewed changes.
- Fresh preselected seeds: `21121, 21227, 21341, 21467`, two worlds (`memory-corridor`, `water-isolated-corridor`), two arms (`baseline`, `cross_goal_local`), 300-step horizon, **new births only**. Scripts `tools/run_i1_318_independent_local_cohort.py` and `tests/i1/test_i1_318_independent_local_cohort.py`. Birth workflow [#39385691970](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39385691970), initially RUNNING. Source SHA `8b5b731aa80eb4803d6dbb9e5c1ef82bc7ded230`.
- This campaign cannot yet establish a causal effect. Its two arms preserve the original common paid memory ranking; no water/food action is ordered by the intervention. Classifying first-person perception, distinct registration, Competition crossings, physical effects and future learning from the **original** WAL remains required. A successful workflow execution does not alone satisfy the scientific GO gate.
- Current-model CI on the same commit [#39385699558](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39385699558): pending at the checkpoint. Canonical goal-calibration [#39385699442](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39385699442) SUCCESS. Do not conflate pipeline statuses.


## Independent original-WAL certification: completed

The [read-only independent audit #39388388663](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39388388663) finished SUCCESS. All 16 original mortal WALs were authenticated without a single life replay. The original source is `8b5b731aa80eb4803d6dbb9e5c1ef82bc7ded230`; the reports' two stale protocol labels are retained and explicitly flagged.

Independent physical totals:

| Original physical measure | Baseline (8 lives) | Independent local (8 lives) |
| --- | ---: | ---: |
| Dead by 300-step horizon | 1 | 0 |
| Physically lived steps | 2389 | 2400 |
| Physically accepted `boire` | 14 | 21 |
| Physically accepted `collecter` | 22 | 56 |
| `manger` | 22 | 26 |
| Physical `se_deplacer` | 26 | 129 |
| Physical `dormir` | 2135 | 1766 |
| Consolidated objects | 859 | 768 |
| Accepted cognitive UC | 91413 | 95916 |
| Positive first-person water follow-ups | 14 | 19 |

For the experimental arm alone, `i1_local_opportunity_perceived` occurred in 2587 paid cognitive cycles; 597 goal-neutral local candidates were proposed, 597 registered and evaluated, 113 crossed Competition and **87 physically acted** after Action Control. Another 26 crossed but were not proven physically admitted. The evaluator marked 529 local candidate evaluations with Q previously learned in its context; this count is **not** 529 independent learned abilities or a proof of TD causality. There were 1420 TD updates involving the broad `i1:affordance:` family, including goal-bound proposals; do not attribute them all to this independent local producer.

**Interpretation:** a local opportunity can now really reach Competition and result in physical action independently of the currently active goal. More drinking, collection and movement occurred in this small matched cohort, while aggregate consolidation decreased and cognitive UC increased. Correlation is not a controlled mediation proof: 8 matched pairs, only one differential death, shared learned-place ranking intervention, no long-run population and no cold M11 parity of the newly active producer. Therefore **NO-GO for canonical promotion**, not an endorsed configuration.

Certified audit code `tools/audit_i1_318_independent_local_cohort.py`, adversarial tests `tests/i1/test_i1_318_independent_local_original_audit.py`; run workflow `.github/workflows/i1-issue318-independent-local-original-audit.yml`. Current priority: determine whether independently added local candidates can perturb a legitimate goal option due to duplicate cognitive demand; add a simultaneous-options integration test and M11 same-generation cold recovery before evaluating generalization.


## 2026-10-20: bounded read-only local motor → TD → later Q chronology

Follow-up investigation is entirely retrospective on the **same original** 16 sealed WALs. This is not a new sample or an independent efficacy trial. A new passive tool `tools/audit_i1_318_local_learning_chain.py` (`5a08dbb1`) requires the original WAL certification to succeed again before reading events. It tracks an independently proposed local option through first-person capture, physically applied command, body-after transition, later TD publication for the exact prior signature, a future learned-Q evaluation, and (separately) an admitted later physical command. Missing observations remain explicitly unproven, never filled by World/Oracle truth.

The first implementation matched TD to the motor world step. This was methodologically wrong: `Stage8Runtime` publishes its earlier segment's TD update during the **next decision**. The revised tool (`87384e76`) joins by prior signature and strictly later decision time. Its negative controls (`0504c342`), added to CI in `d17a0a2b`, reject unsupported benefits, local proposals in the control arm, and unelected candidates. It never writes back to WAL or re-births dead actors.

[New learning-chain CI #39392128417](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39392128417) was running at the latest checkpoint; **do not declare the revised audit successful or use its counts before the job finishes**. The initial earlier version's workflow #39391956981 succeeded, but its same-step TD join was invalidated and is superseded.

Remaining proof obligations: source-level correct attribution between goal-linked and goal-independent identical learning signatures; demonstration of positive versus negative experience changing ranked future decisions; close same-life memory/consolidation/physical decision cycle; M11 current-state cold parity for opt-in births; population hold-out after any supported code correction. No survival efficacy claim or GO from this analysis.

### Attribution safeguard following the first temporal audit
An additional ambiguity was detected before using the first chronology counts: a later TD update with the same generic action signature can belong to an **intervening independent decision**. A distant matching update does not necessarily originate from an earlier physical action. Commit `c9b1e5ee` requires the **first** subsequent eligible TD update to cite the earlier signature; otherwise the evidence is conservatively classified as not demonstrated. A new audit [#39392412693](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39392412693) was queued on this stricter implementation. Any earlier chronology counts are superseded for scientific inference. Neither physical life nor original certified report is modified.


### Strict original-WAL local learning chain: completed

The strict temporal chronology workflow [#39392412693](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39392412693) **SUCCESS** with 16 originally authenticated mortal WALs, no rebirth/replay. Its audit report is generated as a separate artifact and never replaces source journals. Results in experimental arm:

- 87 original independent local physically applied commands, all with a first-person body capture and a single world transition.
- 87 with a first subsequent TD update referencing their action signature; 60 did not have a prior update of that signature, while 27 did. These are signature-level TD attributions, **not 87 causal behavioural changes**.
- 49 of the 87 original actions had a later assessment of the same signature carrying learned Q; 27 had a later physically selected candidate after such an evaluation. Repeated signatures can create overlapping re-use records and should not be interpreted as 27 independent abilities.
- Same-step body changes: water increased in 10 local actions, decreased in 75; food increased in 19, decreased in 68; energy declined in all 87. Because baseline metabolic drift also contributes, these are changes **observed after** a motor command, not action-specific gain estimates or proof of nutritional safety.
- The 16-WAL source SHA is `8b5b731aa80eb4803d6dbb9e5c1ef82bc7ded230`; original scientific status remains NO-GO for canonical promotion. The new chronology is `TEMPORAL_ASSOCIATION_ONLY` / `INCONCLUSIVE` regarding causality.

Next research priority is a fresh, pre-registered contrast that can test whether learned Q alters preference for the same locally accessible interaction. Preserve body dynamics, risk ignorance, no forced command and the same active goal context. Investigate sleep/consolidation opportunity cost and M11 cold recovery separately before considering promotion.


## Prospective local-Q decision ablation (2026-10-20)

**New causal question:** the original 16-WAL audit linked 87 physical independent-local actions to later TD and 27 later learned-Q motor selections, but did not isolate whether exposing learned Q to the independent local producer changes decisions.

Research-only opt-in local-Q exposure `i1_local_q_exposure=learned|neutral` is now configured at I1 birth, strictly allowed to be neutral only when independent local opportunities are enabled (`adbbece0`). The same real `q_active` still learns online in both arms. The independent local producer reads learned values as before, but the neutral ablation masks the values in **both** its candidate ranking and its Stage8/Competition evidence (`db9a37d5`). Goal-bound proposals, TD learning, bodily needs, Stage10 sleep and motor control are not ablated. Its constructor is sealed in M11's exact fingerprint (`73aa7bd5`). Exact native runtime, natural birth and M11 blob pins were updated for byte parity (`bb8cd425`, `a4f01401`) without loosening the pin checks. Synthetic tests `7dbaaafa` and corrected `1ada1166`.

**Fresh matched prospective cohort**: seeds `22111, 22229, 22343, 22453`, worlds memory-corridor and water-isolated-corridor, two new mortal individuals per pair, 300-step horizon, 16 independent lives. Both arms have independent local opportunities ON and identical costly personally grounded recall; only local-Q visibility is neutral versus learned. Runner `tools/run_i1_318_local_q_ablation_cohort.py` (`4671b359`), workflow `.github/workflows/i1-issue318-local-q-ablation.yml` (`ab5cc8d9`). Birth CI: https://github.com/josselin-orta-lab/individual-zero/actions/runs/39396212562 .

The first triggered workflow #39396101263 FAILED before executing a single life because the new test shadowed `Path` with an inner import; it supplies **no physical evidence**. After correction, workflow #39396212562 successfully passed the new test and its eight jobs reached actual mortal execution. No observations are yet accepted pending completion and WAL verification. The parity gate initially rejected unpinned natural and M11 changes as designed and was repaired with exact SHA1 blob locks; latest global CI https://github.com/josselin-orta-lab/individual-zero/actions/runs/39396220764 is not yet concluded.

**Status**: provisional NO-GO, causal effect still INCONCLUSIVE. No I0 change, no main merge, no resurrected or retried life, no command or safety oracle. Compare the first physical motor divergences, Competition crossings and subsequent consolidation/sleep/UC only after audit of original reports and WALs. A significant shift in choices under local-Q neutralization may establish Q's *decision contribution*, not automatically the ecological usefulness of learned knowledge.


## 2026-10-20: final physical Q-ablation cohort and independent original-WAL custody

- The completely fresh [Q-ablation cohort #39396212562](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39396212562) has completed all eight paired jobs SUCCESS; physical source `1ada116666591616a932a8a517e00ec6a0b45452`; 16 independent mortal lives, no life resumption/replay. Two worlds, four new seeds 22111/22229/22343/22453.
- Aggregated **original runner report observations**, NOT YET an independent 16-WAL certificate: neutral local Q: 8/8 active at 300 steps, 2400 physical steps, 271 consolidated objects, 119426 accepted UC, eight lives with a positive personally learned water source; learned local Q: 8/8 active, 2400 steps, 480 consolidated, 126057 UC, eight personally learned water sites. No survival distinction at 300 steps; consolidation increase is heterogeneous by matched pair, so no promotion claim.
- A new independent `tools/audit_i1_318_local_q_ablation_cohort.py` at `c4413191` checks immutable original artifact presence, exact source SHA/preset/selector, 16 hash-chained WAL, physically closed actions, body dynamics, consolidation and UC. It then traces the first physically divergent command in each matched pair, requiring explicit current first-person capture for any local proposal, and distinguishes Q previously learned from later changes in an already divergent history. No action is executed by the auditor.
- Initial audit [#39398931243](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39398931243) failed on an incorrect *audit assumption*, not on a damaged birth: continuous Stage10 sleep can physically advance without a new symbolic waking capture every step. The read-only auditor has been fixed in `2a8c4938` to allow real closed sleep while still requiring actual first-person capture on local proposals. Reaudit [#39399023919](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39399023919) was in progress at this checkpoint, retrieving all original artifacts.
- Additional negative controls in `tests/i1/test_i1_318_q_ablation_audit.py` (`514c2104`), and automated gating in `660c824f`, ensure unobserved sleep is not faked as perception, local proposals cannot lack a real capture, and a mere motor divergence without prior Q exposure is not classified as learned-Q caused.
- Canonical I1 CI and vital-goal calibration [#39396369675](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39396369675), [#39396369514](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39396369514) succeeded before this audit-only development. No I0 changes, no main merge, no forced drinking/food/sleep, no rollback/coma/resurrection.

**Scientific status**: `INCONCLUSIVE` for causal benefit and preference changes until the new audit emits authenticated pairwise divergences. `NO-GO` for canonical promotion and population efficacy. Per-pair Q-aided divergence preceding downstream physical drift would show decision contribution, not necessarily ecological benefit; follow with held-out long population study and real M11 cold consistency.


## 2026-10-20 continuation: verified local-Q fork and pathological neutral-boire regime

Independent original sealed WAL certification [#39399184714](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39399184714) succeeded at exact physical source `1ada116666591616a932a8a517e00ec6a0b45452` for all 16 mortality-isolated lives. It attests physical history alignment before the first motor fork in **8/8 pairs**, local Q exposure at or before the first divergence in **8/8 pairs**, and 8/8 motor divergences. First-person capture equality at the fork and exact candidate-level evidence require the newer drill-down, not merely the high-level counters.

**Certified population observations**: 8/8 survived in each arm for 300 physical steps; local-Q-neutral emitted 1788 `boire` motor commands, 586 `dormir`, 1810 commands owned by the goal-neutral local producer, 2120 local proposals, 271 consolidated objects, and 119426 UC. Local-Q-learned emitted 22 `boire`, 1150 `dormir`, 89 independent local commands, 813 local proposals, 480 consolidated objects, and 126057 UC. All counts derive from independently scanned original mortal WAL, not a simulator projection.

This large **behavioral** contrast indicates that the unlearned/neutral exposure permits a repetitive drinking policy to dominate action arbitration, whereas learned Q exposure changes that competition. It does **not** establish that drinking is physiologically beneficial or harmful, nor long-term survival advantage. In both arms, the local producer proposes at most one option per cycle, but high repetitions remain possible across physical world steps; do not add resource-specific hard suppression or a fabricated danger model.

Commit `cd910f50` extends the *read-only* independent original-WAL auditor to expose for each matched pair its exact first motor and bodily fork, first-person capture concordance, candidate Q status/values, longest consecutive drinking run and same-step before/after water deltas. This is a measurement-only step, not an I1 motor change. CI [#39402437669](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39402437669) was in progress at the last checkpoint. Until it finishes, its new breakdown is unverified. `I0` and `main` remain untouched. Scientific decision: **local-Q decision contribution supported, ecological value and held-out survival INCONCLUSIVE; canonical promotion NO-GO**.


## 2026-10-20: first-fork Competition lineage and net-water controls

Full independent Q-ablation drill-down [#39402437669](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39402437669) succeeded, reauthenticating exactly the same 16 original WALs. All eight matched pairs had identical first-person captures and aligned physical histories before their first motor fork (steps 3–5); the neutral arm physically chose `boire` at every first fork, while the learned-Q arm chose waiting, sleep or movement. Learned Q on a local proposal was present at these forks in every learned arm. This is strong evidence of exposure-dependent **decision divergence**, not of a survival or well-being improvement.

Physically observed before/after water within the step: neutral `boire` had 115 positive net water steps and 1673 without positive net gain (1788 total); learned-Q had 19 positive and 3 non-positive (22 total). Max consecutive physical `boire`: 175 vs 3. This same-step net metric includes metabolic drift and must not be presented as the individual causal effect of drinking.

A further independent *read-only* audit extension (`85d39ffb`) extracts the first-fork chain: locally proposed signature, registration receipt, Stage8 evidence, Competition crossing, whether the local option actually owns the motor, and divergence pathway (different selected local signatures vs equal signature with different Q evidence). This does not prove that the learned option must win, nor does it infer unknown physical risk. Negative tests (`46ab0f28`) and CI gate (`76966672`) reject unregistered, absent, or synthetic claims. Original WALs remain immutable. Workflow [#39403917678](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39403917678) was executing at this checkpoint, so **the new lineage counts must not be claimed until its exit status is SUCCESS**.

Investigation priority after the first-fork chain: explain why neutral exposure allows recurrent drinking attempts and how learned negative Q evidence is balanced against vital pressure, without imposing a rule specifically against drinking. Assess sleep and consolidation and repeat over longer held-out newborn lives before canonical promotion. No I0 edits, no merge, no rollback, no forced drink and no resurrection. Scientific classification remains INCONCLUSIVE for ecological utility, NO-GO for promotion.


## 2026-10-20 : 2x2 factorial intervention to separate Q pathways

The original 16-WAL first-fork Competition audit [#39404028900](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39404028900) completed SUCCESS. Its descriptive classification at the eight physical forks: **three** pairs showed a changed independent local candidate signature; **five** offered the same independent local signature but changed learned-Q evidence. These classifications are NOT a factorial estimate because both pathways were changed together in the prior treatment.

Implemented a dedicated **research-only** 2x2 local-Q exposure map in I1:
- `neutral` = neither candidate ranking nor Competition evidence reads learned Q
- `rank_only` = learned-Q ranking, neutral candidate evidence
- `evidence_only` = neutral ranking, learned-Q evidence
- `learned` = both learned-Q ranking and Competition evidence

The same `q_active` owner continues to learn with TD in every arm. No survival heuristic, forced action, resuscitation, primitive-specific penalty, modified physiology, or new authority is introduced. Canonical births remain independent-local-off. The explicit choice is included in the existing M11 I1 birth fingerprint. Commit `cc9c16e0` changes only the research local producer; `40fa5411` registers the two additional opt-in modes; `c1765240` updates exact byte parity pins; `092a33db` adds selector unit tests; `078e39be` introduces CI; `14edcc0a` updates an older assertion.

The implementation itself is **not** proof of efficacy. The next scientific experiment should use fully fresh seeds and physically separate mortal births for all four arms with locked first-person traces, then authenticate original WAL and first motor differences. Existing original births MUST NOT be replayed, reclassified as newly born, or compared as if prior Q-neutral/Q-learned data constituted the missing factorial arms.

**Scientific status:** first-fork Q exposure dependence is supported in original 8 pairs; independent effect of candidate ranking versus evidence is **INCONCLUSIVE** pending new controlled experiment; canonical promotion **NO-GO**. I0 and main unchanged.


## 2026-10-20: preregistered 2x2 full prospective birth campaign (#318)

A four-arm, mutually orthogonal I1-local-Q design is now implemented and committed; no canonical I1 birth opts in, and I0 remains untouched. The contrasts isolate ranking and Competition evidence, not reward truth or postmortem oracle knowledge. Exact policies: neutral (0,0), rank_only (1,0), evidence_only (0,1), learned (1,1), with identical TD learner and physiology.

**New physical run**: [GitHub Actions #39405862547](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39405862547), source SHA `0b727273ff748c7919cebb8420dc99a39f2580f6`; two world presets, four unspent seed identities `23111/23239/23357/23473`, four mortal newborn actors per preset/seed, 300-step maximum each. The source uses unique life identities including arm name, rejects any existing output folder, no replay/rollback, and authenticates its own original WAL hash chain. Runner commit `988898c4`, tests `be64958f`, workflow `0b727273`. All eight matrix jobs had passed their preflight and started the physical four-life run at the latest checkpoint, but **no final physical values or certified efficacy are claimed** until they complete.

**Independent scientific certificate** is a separate read-only audit of the original 32 WAL with exact source SHA, birth selectors, hash chains, physical transitions, UC and consolidation. Script `tools/audit_i1_318_local_q_factorial_cohort.py`, commit `fee25955`. The first audit CI `#39406020879` was triggered by publication before the original 32 artifacts existed, and failed; this is a scheduling error, not evidence of invalid mortal births. CI was changed to gate on completion of the exact source run (`d661c082`) and allow explicit manual certification (`52e2d79`). A manually triggered certification is available if GitHub does not see a workflow_run definition from the default branch. **Do not mark the 32-WAL audit PASS before execution and independent report production.**

Canonical I1 goal calibration [#39405237327](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39405237327) and entire current-model validation [#39405237325](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39405237325) were SUCCESS at the pre-factorial `f92803e0` checkpoint. The newer global CI for changed source and tools is separate and must be verified. Scientific gate remains `INCONCLUSIVE/NO-GO` for four-arm outcomes and promotion. No source-based water reflex, erased fatigue, coma, second motor authority, dead-life retry, resurrection, or merge into main.


## 2026-10-20: CRITICAL factorial confounding and corrected twin-birth control

**Established source-level confound**: `configure_birth_temperament` maps the actor's `birth_life_id` through five deterministic SHA256 channels. The original 2-arm Q comparison and original 32-life 2x2 cohort generated different `birth_life_id` strings **per arm**. Therefore they also generated *different innate temperament vectors*, resulting in different gatekeeper/body need weights, inertia, reward gain, uncertainty and exploration. Their original physical WAL, counts, and first-person divergence observations remain genuine. However, **the causal interpretation "only Q changed" is REFUTED for these historical cohorts**; first-fork motor differences CANNOT be solely attributed to learned Q. Do not count the old 8/8 fork equality as sufficient controls when hidden innate temperament differs. The 32 original unpaired lives from [run #39405862547](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39405862547) must be explicitly classified `CONFOUNDED` for isolated Q-effect estimates, even if physically completed and independently authenticated.

**Minimal architectural correction**, research I1 only:
- `75d9f435`: `configure_birth_temperament` accepts a restricted optional `i1:research-twin:` source used *only to derive raw innate tau*, leaving `TemperamentProjection.individual_id`, individual first-person memory, Q/TD, WAL and mortal identity distinct.
- `73f7566c`: opt-in `i1_research_temperament_source_id` is removed from the I1 constructor kwargs before Stage12 birth. Default behavior still derives tau from actual life ID. Restrict pairing to independent-local research births.
- `14c9140d` / `b765dbd4`: M11 fingerprint pins the experimental twin source **only when provided**. Non-twin I1 births retain the prior exact fingerprint.
- Source-byte parity pins `aa8792aa`, `1d0e6b3a`. Dedicated tests `454d60f3`, corrected source import `94e72bf8`; CI `a84f426c`, factorial test PASS [#39407416762](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39407416762). Full regression with the initial test failed on nonexistent Python import `i1.runtime`, fixed subsequently. Do not claim final complete CI PASS without checking the new head.

**New independent, genuinely twin-temperament factorial born cohort**:
- New runner `tools/run_i1_318_matched_temperament_q_factorial.py`, commits `383fb04e`, tests `b1a6e518`, GitHub workflow `64e9deb6`; source SHA exactly `64e9deb6a544e2266d6ab43b49306a0acf1bacd8`.
- Four new seeds `24103, 24223, 24359, 24481` x two world presets x four factorial Q modes = 32 *new* mortal identities. Each four-way matched block uses the **same** `i1:research-twin:{preset}:{seed}` for temperament projection and a **distinct** `i1:q-factorial-twin:{preset}:{seed}:{arm}:0` journal identity.
- [Run #39407509122](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39407509122) entered actual physical births on all eight matrix jobs after passing preflight. No results certified in this document as of the last checkpoint; original 32-WAL audit for this newer SHA remains to be independently performed. Neither earlier actors nor their original journals are replayed.

**Scientific conclusion revision:** The original inference about a causal local-Q *behavioral* effect is downgraded to `INCONCLUSIVE (TEMPERAMENT-CONFOUNDED)`. No GO for Q efficiency or canonical I1 promotion. First priority on new WALs: authenticate same born tau/derived parameter vector across each four-arm block, separately verify distinct life IDs/memory/WAL, then certify the motor fork under common subjective/perceptual history, survival, needs, UC, sleep and consolidation. I0 and main unchanged.


## 2026-10-20: matched four-arm birth closure and independent WAL audit

- All eight matrix jobs of the [matched-temperament 32 mortal birth run #39407509122](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39407509122) succeeded. All eight original artifact ZIPs are available. Exact source SHA `64e9deb6a544e2266d6ab43b49306a0acf1bacd8`; the remaining commits in this PR do **not** replace original birth source. No new birth or retry occurred during independent analysis.
- Reviewed the [I1 current-model CI #39408436034](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39408436034) on `16139beb`: SUCCESS; canonical vital calibration [#39408436044](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39408436044) SUCCESS. The former blocked on exact generated-byte parity of `i1_birth_temperament.py`; the reviewed source blob `e88bedd1f89eb1409e8d6f6524e906718a1e8654` is now pinned, without broadening the parity exception. This is a CI control repair, not scientific Q proof.
- Because no GitHub workflow-dispatch action was available, `b5eb84e3` added a narrowly scoped push trigger to the **read-only** post-birth certification workflow. It then launched [audit #39409595177](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39409595177), consuming the eight original archived ZIPs. It was still RUNNING at the checkpoint and therefore **no certificate or 32-life biological outcome totals are declared** here.
- The audit verifies original report/WAL SHA, immutable hash-chain and physiological transition counters; it checks the registered four-arm selector, common declared `temperament_source` for each world/seed, distinct original WAL for each actor and first divergent physical motors. A **reported** common source is not on its own a cryptographic proof of identical born temperament values; direct born-parameter comparison remains a next scientific obligation. Crucially, no replay, forced command, recollection override, M11 resurrection, or hidden-body oracle is permitted.
- Canonical model remains default-local-off, I0 unchanged, PR #318 draft and not merged. Until the independent audit has exited SUCCESS and its limitations are addressed, effect of ranking versus Competition evidence is **INCONCLUSIVE** and promotion **NO-GO**.
