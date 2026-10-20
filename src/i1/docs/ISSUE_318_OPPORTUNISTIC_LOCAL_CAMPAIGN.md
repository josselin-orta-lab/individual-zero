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
