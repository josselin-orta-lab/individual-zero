# Individual Zero — Normative MVP specification v1.3.1

**Title:** Mortal continuity, exhaustive internal causal journal, independent truth and evaluation, separate consolidated memory  
**Language of authority:** English  
**Date:** 2026-10-11  
**Document state:** **NORMATIVE MIGRATION TARGET; SOFTWARE CONFORMANCE NOT YET CLAIMED**  
**Activation gate:** Stage 10/11 completion confirmed by the operator and integrated into main; each further implementation change requires its own validation and protected PR.  
**Historical baselines:** [MVP v1.2.1](mvp-specification-v1.2.1.md) and [MVP v1.3.0](mvp-specification-v1.3.0.md), both retained unchanged.

## 0. Authority, supersession and non-retroactivity

**The English MVP v1.3.1 is the normative migration target.** The accompanying French translation is informative; English prevails on conflict. Historical specifications v1.2.1 and v1.3.0 remain immutable. This version **explicitly reverses v1.3.0's proposed deletion** of the exhaustive causal journal, its cryptographic chain, journal-backed autobiographical provenance and complete life-audit custody. v1.3.0's irreversible mortality, unmodified world physics, ban on life rollback, 600-step development hypothesis, operator stage sign-off and final independent module-by-module scientific validation remain applicable.

Stages 10 and 11 were integrated into `main` after operator confirmation. The current implementation is a transitional mix: the mortal path exists, but historical rollback code and mandatory benchmark/oracle creation remain in older constructors. **Publishing this specification is not proof of implementation, and does not authorize automatic merging of pending PRs.**

Unless this version explicitly overrides a rule, retain the cognitive architecture, six phases, identity, temperament, memory, Planning, TD and causal learning, metacognition, exploration, sleep, six private consolidation passes, bounded work budgets, physical ownership, deterministic ordering and all world consequences specified by v1.2.1 and v1.3.0. Tests and results of Stage 9, including its scientific NO-GO, must not be rewritten.

**Dependency direction is binding:** I0 → *its own complete technical causal journal and cognitive memories*; Oracle → *authorized external world-truth read interface*; Bench → *authorized observations, optional oracle, exported journal*. Neither Oracle nor Bench is a mandatory prerequisite for building, importing or running a standalone I0.

## 1. Non-negotiable principles

1. **Mortal, irreversible world.** A lethal transition is applied exactly once under the unchanged WorldBody physics, then that individual permanently stops. No replay or rollback of a committed life, retry, lethal mask or revival through snapshots.
2. **Exhaustive journal retained.** I0's complete technical `HashChainedJournal` (or proven lossless equivalent with the same event contract) remains available for its entire lifetime and to offline auditors afterward. No destructive compaction, arbitrary expiration, silent event filtering, automatic deletion or required external storage.
3. **Cryptographic custody retained.** Canonical event serialization, event-ID uniqueness, deterministic causal order, predecessor SHA-256 hash chaining and reproducible export/verification remain mandatory. Audit data must be preserved even when learning ignores an event.
4. **Consolidated journal retained separately.** Durable significant experiences, consolidated knowledge and memories are not replacements for the complete audit journal, and the audit journal is not a cognitively omniscient memory. Keep provenance from autobiographically committed lived events to consolidation without leaking technical/oracle-only facts.
5. **No compulsory Oracle or Bench.** Standalone I0 must be constructible and able to execute, learn, sleep, consolidate, die and retain its complete journal without importing, initializing or invoking those external scientific services. External failures do not alter its cognition, physical effects or journal commits.
6. **Strict truth boundary.** Oracle can only read authorized truth without altering the world; Bench can measure using optional oracle/approved observations/readonly journal export, and keeps its own separate trace. Neither may feed secret truth, labels, danger vetoes or corrections into I0.
7. **Audit independent of evaluation.** A separate operator tool validates exported event integrity, ordering, lineage, command/transition linkage, autobiographical projection restrictions, consolidation commitments and terminal invariants, without importing or booting I0, Oracle or Bench. Without independent physical evidence it makes no claim of real-world truth.
8. **Controlled validation.** At least 600 *actually executed* world steps in development support a working hypothesis only, with genuine deaths ending trajectories. Stage completion requires explicit operator approval; complete scientific validation, per module and integrated, occurs at project end.
9. **No functionality removed to satisfy architecture.** Preserve Stage 10 post-cut updates and atomic consolidation, Stage 11 event provenance and actual memories; keep archive integrity through every incremental PR.

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

## 5. Exhaustive technical journal, consolidated memory and read-only audit

### 5.1 Exhaustive internal causal journal (mandatory)

Every individual owns its **complete append-only, hash-chained technical causal journal** from birth through the physically committed terminal event and the external technical closure of that terminal step. Record causally relevant cognitive events, perception truly accessible to the individual, admitted decisions/commands, actual physical outcomes/body changes, accepted learning updates, memory events and their provenance, Stage 10 sleep/rebase/publication, Stage 11 exploration/causal evidence and terminal causes. Technical event metadata and chronology remain separate from the lived experience interface. This journal is infrastructure of the I0 execution, not an Oracle database or a source of omniscient cognitive perception.

- Preserve deterministic ordering, normalized canonical bytes, unique NFC event IDs, exact hashes of the retained immutable payloads and complete predecessor-link verification. Neither missing, tampered nor duplicate entries may silently validate.
- Retain **all** technical occurrences, even rejected or uncommitted attempts when needed to audit their actual occurrence. An unexecuted plan never becomes an executed physical result.
- Keep full journal throughout the life and after death under operator-controlled custody. No default limit proportional to time, arbitrary retention window, destructive compression, unacknowledged removal or mandatory hosted storage.
- Permit lossless performance optimization: indices, incremental verification, efficient append, partial read, pagination and read-only canonical export. All exported data remain independently verifiable, with explicit schema and manifest and no import of the live runtime.
- **Never use technical history to restore or replay the *same* living individual into an earlier committed state.** Audit/reproduction of a *separate* experimental instance remains permitted.

### 5.2 Distinct consolidated history and cognitive memories

Keep the permanent consolidated history (`SlowHistory`/active h and the project's actual consolidation records) and the existing episodic, semantic, procedural, prospective and working memories as **different resources** from the exhaustive journal. Consolidation chooses and integrates significant experience, never purges the audit source. Its cognitive input comes only through versioned, explicitly authorized autobiographical `AutoSegmentCommit`/policy projections of events physically or cognitively lived by I0.

The exhaustive journal may prove the existence, ordering and provenance of consolidated source event references, but the presence of an event in the technical journal does not grant I0 access to hidden hazards, Oracle keys, laboratory truth, future scenario schedules or postmortem records. A terminal technical closure is externally readable; **no postdeath autobiographical commit, learning update or cognitive consolidation** is allowed.

### 5.3 Stage 10 and 11 consumers

Preserve Stage 10's frozen cut index/event ID/hash and **all correctly ordered post-cut-point updates** until an atomically committed consolidation rebase has consumed them. Six private semantic passes, UC budgets, waking interruptions, immutable source evidence and coherent active h/Q/κ/precision/causal publication retain their existing contracts. The complete journal can be the authoritative custody source; bounded owner-local delivery caches are permitted optimizations **in addition** to it, never destructive replacements.

Preserve Stage 11's physical attribution, exploration/movement chronology, learned vs unknown danger distinction and provenance. Verify a technical trace may contain a lethal world transition without giving the dead individual new knowledge.

### 5.4 Independent audit interface and epistemic limits

Provide a **standalone, read-only operator verifier** for a canonical journal export. It must run without constructing or importing the I0 runtime, the Oracle or the evaluation Bench. It must check schema/canonical bytes, full SHA-256 chain, event-ID uniqueness, strict occurrence indexing and ordering, provenance references, command/result relationships, autobiographical allowed kinds/attempt boundaries, consolidation source/cut references and closure after terminal death. Any unsupported event semantics must be reported honestly rather than guessed; corruption must cause a nonzero failure exit.

Such verification proves consistency of **records**, not that the external physical world actually had the stated state. Physical truth requires an independent authorized world oracle, sensor witness or scientific protocol. Do not confuse cryptographic self-consistency with observed truth.

### 5.5 Storage evolution is deferred

A future version may consider moving the full technical journal to an external audit storage tier **only after** explicit operator authorization, a new normative decision, measured resource cost, security and incident analysis, a lossless migration plan, independent verification and guarantees against cognitive dependency on Oracle/Bench. **No transfer is authorized by v1.3.1.**

### 5.6 Separate scientific observation and trace

The Oracle is a read-only interface to authorized world truth; Bench observes through clearly scoped read-only interfaces, may optionally consult Oracle, and may validate an exported journal. Bench owns `EvaluationTrace`, its metrics and protocol-specific scientific evidence independently. Oracle reads and Bench results go **only** to that external trace, **never** into I0's exhaustive causal journal as hidden truth, into its consolidated journal or any cognitive owner. A failed/unavailable Oracle or Bench cannot prevent normal I0 logging, cause a rollback or inject a change to the individual.

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

## 8. Baselines, implementation gates and source discipline

Stage 10 and Stage 11 are completed and operator-approved; their software was integrated into protected `main`. Do not restart or rewrite their experiments. Preserve SHA/campaign provenance and the historical Stage 9 NO-GO.

The migration must be split into reviewable PRs: (A) real dependency mapping, (B) these bilingual specifications, (C) standalone I0 without loading Bench/Oracle, (D) independent journal export verifier, (E) Stage 10/11 and consolidated-journal parity, and (F) fixed-seed 600-physical-step software diagnostics. Code PRs may be merged only following their own successful tests and rule-protected review. Outstanding compact-life-stream branches drafted to **replace** the full journal must be re-evaluated and **not merged unchanged**.

No activation claim until both autonomous and externally observed trajectories match before terminal events. No world physics change, involuntary reparenting, historical state resurrection or modification of old scientific records.

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
| M-07 | Full journal and independent consolidated history both persist, with unchanged memory, provenance, causal evidence, planning and online learning on equivalent nonlethal trajectories. |
| M-08 | Stage 10 reads the full journal's verified cut/postcut updates, loses none and publishes coherent consolidated state after sleep interruption. |
| M-09 | External input rejection is prepublication and never undoes an already committed world transition. |
| M-10 | Oracle/evaluation facts cannot enter perception, memory, S_t, value, causal models or consolidation. |
| M-11 | Persisted current state reloads coherently after a nonterminal process failure but cannot resurrect a dead identity. |
| M-12 | Full causal journal storage and export grow losslessly with historical events; every prefix remains hash-verifiable and readable after death. Performance optimization is nondestructive. |
| M-13 | Copy creation preserves identity distinction; dead/stopped copies cannot overwrite their parents. |
| M-14 | Tests cover Python 3.11 reference behavior, deterministic seeds, final-state digests, and the operator’s accepted integration smoke run; failures are reported, not relabeled. |
| M-15 | Stage status and scientific status remain independent, with the 600-step working-hypothesis rule and operator sign-off. |

| M-16 | Standalone I0 creates/imports **neither** Oracle nor EvaluationBench, but produces the same internal causal journal and decisions as its evaluated counterpart. |
| M-17 | An Oracle process can be constructed/read/stopped independently and cannot mutate I0 or its world. |
| M-18 | A Bench process can read approved observations and complete exported journal without being a dependency or backchannel of I0. |
| M-19 | Standalone journal auditor catches altered, reordered, missing and duplicated events, false provenance and illegal post-death cognitive publication without loading I0/Oracle/Bench. |
| M-20 | 600 genuine physical steps produce a complete independently verifiable journal; no silent truncation and no oracle-truth leakage. |

These checks are **software/integration acceptance**, not a claim that the final scientific campaign has passed.

## 10. Explicit v1.3.0 and v1.2.1 supersession map

| Historical rule | v1.3.1 authority |
| --- | --- |
| **v1.3.0 §0, §1.4, §5, §9 M-07/M-12, §10**, and any direction to remove/archive only a fraction of `HashChainedJournal` | **REVERSED**. Keep complete journal, canonical SHA-256 chain, independent full export and journal-grounded memory provenance as in §5 above. |
| v1.3.0 §5.1 single current coherent snapshot | Current state storage may coexist with an unbounded-by-policy append-only **technical event journal**; never confuse durability with historical life restoration. |
| v1.3.0 §5.2 bounded lived-event queue and postcut deltas | Optional read-through/performance caches only; they must not replace or delete complete technical journal records or consolidated memory. |
| v1.3.0 §5.3 selective laboratory evidence and §19 of v1.2.1 | Bench/Oracle scientific traces remain **external and independent**, while internal journal is **complete**; no mirrored secret ground truth. |
| v1.2.1 §17, INV-33, INV-44, INV-49 technical integrity and causal journal | **RETAIN** canonical event order, uniqueness, immutable hash chaining, complete life audit and authorized autobiography, without permitting rollback. |
| v1.2.1 §10/§15 memory and consolidation provenance | **RETAIN** distinct meaningful consolidated history, full source journal and all verified post-cut updates until atomic publication. |
| v1.3.0 §2–4 and §6, v1.2.1 §18 lethal rollback, mask and checkpoint | **RETAIN v1.3 irreversible mortality**. Remove all historical life rollback/second attempts, but record fatal transitions in the journal; no postmortem cognition. |
| v1.3.0 §7/§9 scientific gates | **RETAIN** genuine 600-step development hypothesis, explicit operator stage acceptance and rigorous final independent per-module scientific validation. |
| Future possibility of journal migration outside I0 | **NOT AUTHORIZED**; require new operator-approved specification and security/cost/lossless-migration evidence. |

If a prior document contradicts §1 or §5, this version prevails. No contradictory legacy default behavior is silently reclassified as conforming.

## 11. Publication, audit ownership and validation

- Keep English/French v1.2.1 and v1.3.0 immutable. Publish both complete v1.3.1 files together; English prevails.
- Map and classify coupling points as P0 (mandatory runtime oracle/bench, death rollback, truth leakage, loss of journal), P1 (unverified provenance, consolidation, audit tool completeness), or P2 (index/readme/performance).
- Preserve old Stage 9 negative results and Stages 10/11 completed software proofs without retrospective rewrites.
- Test standalone run with imports/constructors of Oracle and Bench blocked; independent evaluation should leave I0 causal fingerprints and journal event bytes unchanged on matched trajectories.
- Verify journal after death, detect deliberately tampered/reordered/duplicated exports, and check 600 true world steps without claiming physical omniscience.
- Maintain protected `main` and independent, reviewed, CI-validated PRs. Defer offloading the complete journal to future explicit operator approval.

**This document specifies the target. It does not claim that the present codebase already implements every invariant.**
