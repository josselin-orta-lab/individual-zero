# Individual Zero — Normative MVP specification v1.3.0

**Title:** Mortal continuity, irreversible world effects, minimal persistence, proportionate stage evidence  
**Language of authority:** English  
**Date:** 2026-10-11  
**Document state:** **APPROVED TARGET, NOT YET ACTIVATED IN THE LIVE DEVELOPMENT BASELINE**  
**Activation gate:** explicit operator acceptance of completed Stages 10 and 11, then a recorded migration decision. No automatic activation or merging.  
**Historical baseline:** [MVP v1.2.1](mvp-specification-v1.2.1.md), retained unchanged.

## 0. Authority and migration boundary

This document specifies the **next MVP contract**, not a report claiming that the currently running software conforms to it. While Stages 10 and 11 are being developed, their existing branches, tests, experiments, and PRs continue under their declared v1.2.1 baseline. They must not be rewritten, rebased, or merged merely because this target is published.

After the activation gate, v1.3.0 is the implementation authority. It **replaces the contradictory v1.2.1 clauses** about lethal rollback, checkpoints, exhaustive journals, complete historical replay, and scientific sign-off for each development stage. All other cognitive, behavioral, and physical requirements of v1.2.1 remain binding unless explicitly overridden below. In particular, keep the six cognitive phases, deterministic scheduling, the single physical capture per step, cognition/oracle isolation, temperament, S_t, competition, reflexes, informed vetoes, Value and Needs, Planning, causal reasoning, online learning, five memories, sleep, consolidation, and the ordinary world's physics.

There is no implicit license to delete functionality simply because its existing implementation depends on a journal or snapshot. Such a dependency **must receive an equivalent source of the same authorized information** before the old infrastructure is removed.

If the English and French files conflict, this English version prevails. Scientific validity is never inferred from software test success or operator approval alone.

## 1. Non-negotiable principles

1. **Mortality is real.** A lethal physical transition is applied to the world and body and terminates this individual irreversibly. Death is neither undone nor reclassified as a safety block.
2. **World consequences are unchanged.** Movement, obstacles, damage, food and water, toxic berries, hazards, creatures, resource consumption, schedules and terminal predicates remain exactly those of the applicable world-physics version in v1.2.1. No hidden immunity, damage cap, rescue, alternative outcome or lethal filter is added.
3. **No life rollback, in any mode.** Never restore, rewind, retry or replay a committed living state to escape any outcome, including death. No command masking or resumed deliberation after a lethal result.
4. **No exhaustive event archive.** Neither the individual nor the laboratory persistently stores every contribution, S_t version, internal cycle event or world-step event for the full life. Store only necessary current causal state, meaningful learned/episodic information, bounded in-flight data and purpose-limited evidence.
5. **Cognitive non-interference.** The technical death detector, evaluation bench, oracle and persistence machinery may not contribute new danger facts, reward, beliefs, memories, policy changes or decisions to I0. Ordinary perception and previously established safety rules are unchanged.
6. **Atomic publication, not retrospective repair.** Prevalidate/stage updates before publishing them. A discarded *unpublished candidate* is not a rollback of life. An already committed physical transition may never be compensated by changing history.
7. **Evidence is staged.** A reproducible development test of 600 genuine world steps supports a **working hypothesis**, not definitive scientific acceptance. Stage completion requires an operator decision. Full per-module scientific validation belongs at the end of the complete project.

## 2. Lifecycle and terminal semantics

The runtime has distinct externally observable statuses:

| Status | Meaning | May execute another world step? |
| --- | --- | --- |
| `active` | Individual and world are running | Yes |
| `dead` | World physics reached an existing terminal condition and the fatal transition was committed | **Never** |
| `safety_block` | No existing safety-policy-admissible command can be sent; **no** lethal transition was executed | Only under a separately authorized nonhistorical unblock protocol |
| `technical_halt` | State integrity, external input atomicity or publication cannot be guaranteed | No, pending operator investigation |
| `experiment_stopped` | Operator/protocol ended a test or disposable copy | No for that test instance; **not death** |

Only the world and body determine lethality, using their already versioned rules (e.g. zero integrity or a defined lethal zone). A person, an operator, or a laboratory stopping a campaign cannot turn a nonlethal stop into a physical death.

A death occurs **at the committed physical transition**. Its final position, inventory, resources, body values, external effects and true lethal reasons are retained as terminal world state. No additional cognitive cycle, learning, TD update, consolidation, rest, recovery, exploration visit, or autobiographical memory write is performed *after* death. The external bench may record the final result and its reason; that record is not seen by the individual.

After `dead`, both direct command calls and opening a new step must fail. No runtime mode, copy facility, recovery interface or operator control may resurrect the same instance. A fresh birth or independent copy has a distinct individual identity and lineage.

## 3. Exact command-to-world contract

The existing Action Control remains the sole sender. The existing informed vetoes, reflexes, command validation, risk and uncertainty assessment, known-danger rules and fallback remain in force. **Remove only the extra protocol mask created by lethal rollback.** Do not make the decision system omniscient by consulting hidden world hazards at admission time.

For each admitted primitive command:

1. Confirm that the individual is `active` and that the world step is open.
2. Publish or validate the minimal command context necessary to associate its result; do **not** create a lethal checkpoint.
3. Execute the existing `WorldBody.apply(command, t_monde)` **once**. Preserve its physical effects and pseudorandom consumption.
4. Receive the returned result, including the world's lethal predicate and physical consequences.
5. If nonlethal, close the step once as `applied`; publish only the authorized lived facts to the transient autobiographical pipeline and carry out ordinary learning at the specified time.
6. If lethal, close the step once as `dead`, persist its final state and external terminal metric, and prevent all further individual execution. Do not create an autobiographical commit or learn from a postmortem outcome.

No `rolled_back`, `masked`, `lethal_retry`, `resume_after_death`, `lethal_checkpoint`, `R_letal_consecutif` or `R_letal_max` control branch is permitted in the active-life path. A reflex that causes death is terminal immediately; a cognitive decision that causes death does not reopen Competition.

**Physical parity rule:** For the same pre-state, command, world-physics version, scenario and deterministic random states, the full physical outcome (including a lethal outcome) must match the original unrolled world transition. Only the external lifecycle/protocol changes.

## 4. No backward correction: transactions and technical failures

Rollback is prohibited at the **committed life/world** boundary, not only at death. Do not retain a hidden restoration path for rejected scenario inputs, a failed journal receipt, a crashed evaluator or a delayed callback.

- **External scenario inputs:** validate the entire due input batch, ownership, types, bounds and canonical form *before* applying. Stage input effects privately and publish atomically. A rejection makes no new world transition. If the engine cannot guarantee that a partially applied operation was never published, enter `technical_halt`; never rewind a publicly committed world effect.
- **Cognitive publication:** owners prepare changes privately and publish complete coherent versions at phase boundaries. An unpublished invalid candidate may be dropped. Do not roll back a prior published S_t, body, command or learning state.
- **Sleep consolidation:** keep private six-pass work and the ability to suspend or discard **unpublished** pass work. Rebase on the necessary post-cutpoint **owner-local, bounded causal deltas**. Atomically publish h and corresponding active Q/κ/precision/causal forms; either everything becomes visible or nothing does. A published new h version is not reversed.
- **Persistence failure:** stop at the failure boundary rather than guessing a valid prior state or performing partial reconstruction. A crash may reopen only the **last atomically committed current state**, never an earlier selectable life snapshot; pending uncommitted operations must have no externally visible effects and must be idempotently resolved.
- **Test resets:** an isolated fixture may start a *new* simulation from an initial seed for a controlled comparison. This is not resumption or resurrection of the original individual.

A protective checkpoint before every primitive command, periodic restoration of previous lives, undo of external committed events, or retries after an applied lethal command are all prohibited.

## 5. Minimal persistence and memory without a comprehensive journal

Replace the technical append-only full-life journal, exhaustive `JournalEvent` history, hash chain over all events, historic `AutoSegmentCommit` projection, mandatory exact full-life replay and periodic historical snapshots **as runtime requirements**.

### 5.1 Current causal state

The runtime persistently maintains a **single logically current, coherent, versioned causal state**, updated at safe synchronization boundaries. This includes all data needed to continue this very individual without changing behavior: identity and lineage; temperament and fixed equipment/version manifests; world/body and external scenario state; memory representations; intentions and plans; S_t and authorized buffers; learned parameters and forms; cognitive accumulators and clocks; fatigue/sleep and consolidation ownership; uncertainty/calibration maps; stochastic source states; and terminal status.

Use canonical serialization, schema/version checks and an integrity digest. A transient replacement file, private commit buffer or atomic database transaction is permitted for durability; these are **not successive user-selectable historical snapshots**. There is no indefinite archive of previous current states.

An unrecognizable legacy snapshot is rejected or migrated under an explicit offline operator procedure, never silently interpreted as permission to restore a dead individual.

### 5.2 Lived experience and online learning

Give Memory and Consolidation a transient, versioned **lived-event interface** that includes *exactly* the observation, contribution, decision, action and nonlethal physical outcome information those modules were authorized to read under v1.2.1. Preserve causal ordering, phase boundaries, provenance identifiers, ownership, duplicate suppression and the rule that knowledge comes from the individual’s actual experience.

The in-flight buffer is bounded by the active step/episode and released after the responsible consumers acknowledge incorporation. Retain meaningful episodic/semantic/procedural/prospective memories, not a second complete copy of every technical event. Do not provide raw oracle facts or cancelled/unexecuted hypothetical transitions.

**Consolidation rebase:** online updates after its cut point must remain available through bounded per-owner pending deltas or another demonstrably equivalent, lossless mechanism until the atomic rebase/commit. Do not erase deltas before they are consumed. If these guarantees fail, the journal must **not** be removed yet.

### 5.3 Laboratory evidence and diagnostics

The bench may keep bounded aggregate counters, terminal outcomes, normalized test observations, version/seed manifests, hashes and purpose-specific scientific data. Retention and diagnostic sampling must be explicit per protocol. An experiment may persist **selected, justified measurements**, never use that allowance to reinstate a full-event life archive by default.

Streaming causal fingerprints, end-state comparisons and paired runs with agreed input manifests replace the requirement to reconstruct every historical event. Deterministic unit behavior and causal isolation remain required. Do not claim full historical replay after it has been deliberately dropped.

### 5.4 Copies

An explicitly requested copy starts from a coherent **currently available** causal state, obtains a distinct individual identifier and lineage, and then lives independently. There is no implicit backup copy or periodic automatic fork. A dead individual cannot be copied back into life as the same identity. Disposable battery copies stop under their protocol and do not inject their learning into their parent.

## 6. Safety and epistemic isolation

The seven distinct safety mechanisms of v1.2.1 §18.1 continue to serve their original purposes: reflex, existing veto, cognitive preemption, R_a, U_a, safety-use evidence and established causal evidence. Their cognitive rules, thresholds, source permissions and ignorance boundaries are preserved. **The lethal-rollback protocol mask is removed.**

Unknown lethal zones remain unknown until directly accessible evidence legitimately changes what I0 knows. A known lethal zone may be vetoed by the existing policy; an unknown one may cause real death. A nonlethal toxic berry still teaches through ordinary experience; a lethal berry ends the instance and creates no postmortem learning.

Do not synthesize rescue actions, a minimum-viability clamp, ghost learning, retroactive risk penalties, an oracle-informed action veto or operator-driven hidden cognitive updates. The bench/oracle may measure but never direct I0’s learning.

Nonlethal absence of admissible commands remains `safety_block`. A technical inconsistency remains `technical_halt`. Neither is death, and neither rewinds the world.

## 7. Development-stage evidence and scientific acceptance

This MVP deliberately separates **software verification**, **working hypothesis**, **operator acceptance** and **final scientific validation**.

### 7.1 Working hypothesis: 600 genuine world steps

For each stage or new behavioral module, run targeted unit/integration/invariant tests plus a transparent development campaign covering **at least 600 actual executed world steps in total** across declared scenarios and seeds. Prefer more than one independent trajectory and contrasting situations. The exact seed, source SHA, configuration, physics version, intended observations, outputs and known limitations must be retained in a compact report.

A death ends a trajectory. **Never count hypothetical steps after death**. Another independently born test individual may contribute further genuine steps; record births, deaths, denominators and survivorship explicitly. A module not exercised by those steps is **not demonstrated**, regardless of the step count. An operator may authorize a documented exception if 600 steps are technically impossible or inapplicable; an exception must not be disguised as passing evidence.

A 600-step run may justify **“development hypothesis supported / unsupported / inconclusive”**. It may **not** justify definitive scientific proof, validation of every module, a hidden-seed acceptance claim, or promotion of historical Stage-9 NO-GO into GO.

### 7.2 End of each stage

The developer gives the operator a minimal review packet: stage scope, version/SHA, contract delta, results and failures, 600-step accounting, significant behavior, known gaps, and any requested real-condition trial. **The operator alone confirms stage completion.** Until explicit sign-off, the status is `IN_PROGRESS`, even if all software tests pass. When necessary, the operator must be asked to perform or authorize a real-condition test; an agent cannot invent that sign-off.

### 7.3 End of the complete project

**Scientific validation is mandatory at project completion**, distinct from the 600-step hypotheses and operator stage approvals. Design a registered campaign with independent/held-out conditions, module-by-module hypotheses, adequate controls and sample sizes, provenance, measurable behaviors, uncertainty estimates and falsification criteria. Modules are assessed **separately** and then together, with explicit positive, negative and inconclusive outcomes. Retain only the evidence necessary for independent review, not an exhaustive internal event archive.

Scientific verdicts may be `GO`, `NO-GO` or `INCONCLUSIVE`. No test count, PR merge or retrospective rewriting of a negative result substitutes for validation.

## 8. Stage 10 / Stage 11 coexistence and activation gate

Stages 10 and 11 continue untouched until their respective agents finish and **the operator validates their deliverables**. Their active implementation and research baseline stays v1.2.1, even if its rollback and journal requirements will subsequently be replaced.

The migration starts only after:

1. Stage 10 delivers its final reviewed source SHAs and scope, including the separate integration branches/PRs as applicable.
2. Stage 11 delivers its final reviewed source SHAs and scope.
3. The operator records explicit Stage 10 and Stage 11 completion decisions and any outstanding exceptions.
4. A read-only dependency audit is re-run against the final integrated baseline; it produces the code/test/document impacts, collision resolution and risk classification.
5. The operator approves **a separate migration implementation PR**. Do not merge or silently transplant the existing experimental mortality PR.

The initial implementation in PR #31 is **development evidence only**: it is not a validated replacement and its assumptions must be re-audited after the agent branches converge. Changes to historical results, tests or physics are not authorized simply to make that PR pass.

## 9. Required integration and non-regression checks

The post-gate migration must establish all of the following before any runtime change can be accepted:

| ID | Observable criterion |
| --- | --- |
| M-01 | Every admitted command causes exactly one real world transition and one terminal or nonterminal step closure. |
| M-02 | A lethal zone, lethal toxin, starvation/integrity exhaustion, creature damage and combined hazards apply the unmodified physical effects and may kill. |
| M-03 | After `dead`, no new step, command, reflex, decision, learning, TD update, memory closure or consolidation can execute. |
| M-04 | The system does not create lethal checkpoints, masks, retries, old-state restorations or compensating world changes after an applied transition. |
| M-05 | Every nonlethal physical transition is byte-identical in causal state to the baseline for the same commands and random states. |
| M-06 | Ordinary known-danger vetoes, reflexes, competition and unknown-risk behavior are unchanged before the first lethal transition. |
| M-07 | Memory, episode provenance, causal evidence, plans and online learning are unchanged on equivalent nonlethal trajectories after journal replacement. |
| M-08 | The consolidation rebase loses no post-cutpoint owner update; atomic publication is coherent after sleep interruption. |
| M-09 | External input rejection is prepublication and never undoes an already committed world transition. |
| M-10 | Oracle/evaluation facts cannot enter perception, memory, S_t, value, causal models or consolidation. |
| M-11 | Persisted current state reloads coherently after a nonterminal process failure but cannot resurrect a dead identity. |
| M-12 | Causal memory/storage growth is bounded independently of total historical event count, apart from deliberate learned knowledge and scientifically authorized selected evidence. |
| M-13 | Copy creation preserves identity distinction; dead/stopped copies cannot overwrite their parents. |
| M-14 | Tests cover Python 3.11 reference behavior, deterministic seeds, final-state digests, and the operator’s accepted integration smoke run; failures are reported, not relabeled. |
| M-15 | Stage status and scientific status remain independent, with the 600-step working-hypothesis rule and operator sign-off. |

These checks are **software/integration acceptance**, not a claim that the final scientific campaign has passed.

## 10. Explicit v1.2.1 supersession map

This table is normative: if the referenced older text conflicts with the new rule, the new rule wins **after activation**.

| Previous location | v1.3.0 rule |
| --- | --- |
| Principles P6, P9, P12; architecture Journal/Snapshots roles (§1–2) | Current coherent persistence, minimal diagnostic evidence; full journal/history/replay obligations retired. |
| §3.4 `EXÉCUTER_PAS`, `REPRENDRE_DÉLIBÉRATION`, rollback arrows and §3.5 diagram | Replace with §3 above; fatal command advances once and closes as `dead`; no re-deliberation. |
| §4.6 external-input bookkeeping and §5 journal/snapshot owner table | Keep deterministic inputs and causal ownership, replace full logging with staged atomic input application and current state. |
| §10.2, §10.6 memory-from-journal/read-access logging | Use authorized bounded lived-event interface plus ordinary persistent memories. |
| §15.6–15.8 consolidation, rebase and transaction points | Retain the six semantic passes, private work, lossless local deltas and atomic coherent publication; remove reliance on complete technical journal. |
| §16 detailed technical counters/journal | Preserve logical UC and metacognition but do not archive every counter change. |
| **§17.1–17.8**, DC-08, DC-09, S-01 full-life replay/snapshot requirements | Replace by §§4–5, 9 of this document. No general historical restoration, complete event log, lethal checkpoint or obligatory full-life replay. |
| **§18.2–18.6**, diagram I, V-24/V-25/V-40 lethal rollback and mask | Replace by §§2–3 and 6. Existing physical terminal conditions now really terminate an individual. |
| §19 technical journal/evaluation interfaces | Maintain oracle isolation and selective independent metrics, without total-event collection. |
| **§20, §21**, completion gates and testing matrix | Replace stage evidence/approval rules with §7 and migration checks §9. Unchanged invariants still apply when their test method is compatible. |
| DC-02 protocol mask; DC-14 after-lethal block; DC-15 rollback segments; DC-16 event IDs; glossary | Remove lethal retry/mask, keep ordinary veto/fallback, terminal segments and unique episode/evidence provenance without global event histories. |
| INV-27, INV-28, INV-29, INV-33, INV-39, INV-44, INV-49, INV-52 where these require rollback/journal/checkpoints | Evaluate through M-01 to M-15 and the remaining non-conflicting oracle/control invariants. |
| Parameter P-55 periodic snapshot frequency and R_letal_max | Retired from the living MVP. Legacy parameter parsing must not reactivate a rollback path. |
| All references to re-running a deceased individual or replaying its entire technical life | Forbidden as same-individual continuation. Independent seeded tests and distinct experimental copies remain allowed. |

The prior implementation Stage 9 scientific NO-GO, previously recorded negative results, research provenance and experiment chronology **remain unchanged**. No past stage is automatically certified by adopting this new MVP.

## 11. Change-control and publication

- Preserve v1.2.1 English and French files as immutable historical baseline.
- Publish English and French v1.3.0 documents together, with matching semantic contracts.
- Do **not** change `main`, integrate Stage 10/11 branch code, close PRs, alter experimental outcomes or execute the migration merely to publish this document.
- Record final Stage 10 and 11 source SHAs, operator approvals, baseline differences and the migration’s own reviewed acceptance evidence before declaring v1.3.0 **ACTIVE**.
- The companion [post-Stage-10/11 migration audit](../../../research/audits/post-stage10-11-mortal-mvp-audit.md) defines the read-only audit and release gate. The audit must be refreshed on the actual frozen integration SHA.

**Current status remains: normative target defined; no activation, no migration approval, and no scientific conclusion implied.**
