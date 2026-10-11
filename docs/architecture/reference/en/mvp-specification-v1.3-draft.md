# Individual Zero — MVP v1.3 (DRAFT): engineering-first development and deferred scientific validation

**Status:** PROPOSAL, **NOT YET IN FORCE**. Operator approval and a deliberate repository decision are required before adoption.  
**Version:** v1.3-draft, 11 October 2026.  
**Source of architectural truth:** [MVP v1.2.1](mvp-specification-v1.2.1.md).  
**Change category:** delivery, evidence, and stage-acceptance policy; **not** a redesign of the artificial individual.

> **Decision in one sentence:** develop and qualify all MVP modules using bounded, observable engineering evidence; close each stage only upon explicit operator acceptance; undertake independent scientific evaluation of each module and the integrated individual after the complete software MVP is ready.

## 0. Authority and inheritance

This document is a **versioned delta specification**, not a condensed replacement for the 3,325-line v1.2.1 architecture. All architectural rules, algorithms, schemas, state ownership, temporal semantics, safety constraints, parameters, INV-01 through INV-58, traceability, deterministic replay, and epistemic isolation in v1.2.1 are **inherited unchanged** unless an override is explicitly listed in section 1.

While this draft is unapproved, v1.2.1 remains the sole normative implementation authority. The draft grants no permission to bypass a current gate, relabel a scientific NO-GO, merge a branch, or launch a confidential held-out campaign. On adoption, the two documents jointly define v1.3: this delta takes precedence **only** for the explicitly replaced delivery and evidence requirements. For all other topics, v1.2.1 controls. The corresponding French document is an informative translation; the English text controls if wording diverges.

**Unchanged:** modules, their interfaces and contracts; Stage 1–12 build objectives; 300-step simulated days; hard invariants; safety veto, rollback, and operator controls; frozen equipment/temperament rules; full causal journal and replay; separation of development from oracle/bench-only and independent scientific data.

## 1. Explicit overrides of v1.2.1

| v1.2.1 location | v1.3 change | What remains binding |
| --- | --- | --- |
| §20 opening and §20.1: stages closed with scientific/functional acceptance, exact replay, invariant gates | Separate **technical conformity**, **600-step developmental observation**, and **operator stage decision**. Only an explicit operator decision closes a stage. | Applicable invariants, contracts, deterministic reproducibility and safety are not deferred. |
| §20.3 Stages 5–12: experimental or long-horizon acceptance criteria in individual stage gates | Comparative performance, test-retest reliability, 60-day behavior, and statistical sufficiency become hypotheses and targets for the final scientific phase. A bounded developmental observation is adequate to **propose** functional readiness, not to claim the effect is established. | Implement the original module behavior and retain every stage's technical acceptance requirements and observable target. |
| §19.5: crossed experimental design, 60-day lives, trait battery, reference/ablation conditions, statistical analyses and exit thresholds | Preserve this as the **final scientific protocol baseline**. Its execution is no longer a prerequisite to implementing or operator-accepting the next software stage. | Full evaluation is still required to claim scientific validation; independent custody/preregistration and evidence rules stay intact. |
| §20.3 Stage 13: full MVP campaign | Stage 13 in v1.3 is **software integration and MVP delivery readiness**. The former Stage-13 campaign is moved to **Phase S (post-MVP scientific qualification)**. | Research hypotheses H1–H6, their controls and possible refutations remain unchanged. |
| §20.4 and §21: acceptance and invariant tests | Split the stage decision from scientific claims; enforce all applicable invariants as hard technical gates. | Complete technical verification, including exact replay where relevant; no silent exemptions. |
| §22 parameter preregistration | Engineering diagnostics may use clearly recorded **development configurations**. | Every true scientific campaign must freeze its complete versioned registry and protocol before data exposure, as in v1.2.1. Development runs cannot be promoted retroactively into a held-out test. |

**Precedence example:** a Stage-9 development run with plausible causal behavior may justify asking the operator to accept software progress. It **cannot** overturn an existing Stage-9 independent-science NO-GO or certify INV-25 without the invariant's own technical test.

## 2. Two independent project axes

### 2.1 Software stage status

1. **IN_PROGRESS:** implementation or hard checks outstanding.
2. **ENGINEERING_READY:** code, applicable invariants, 600-step observation and evidence packet satisfy section 3; awaiting human decision.
3. **OPERATOR_TEST_REQUIRED:** operator requests a test in the actual integrated runtime or additional evidence; stage remains open.
4. **OPERATOR_REJECTED:** the operator identifies a defect, unsafe condition, or insufficient evidence; stage remains open.
5. **OPERATOR_ACCEPTED:** operator explicitly approves a named commit and recorded limitations. **Only this state means “Stage N completed (engineering)”.**

Agents, CI, pull requests and dashboards **MUST NOT** manufacture, infer, or self-issue an operator signature. Silence, a passing CI badge, a stage summary, or a merged PR is not operator approval. Subsequent changes to the accepted stage's relevant code trigger a regression review; the previous approval does not silently transfer to a different commit.

### 2.2 Scientific status (recorded separately)

**NOT_RUN**, **NO_GO**, **INCONCLUSIVE**, **SUPPORTED_WITH_LIMITS**, or **NOT_SUPPORTED**. Scientific status never automatically follows an operator software decision. “Supported” means supported in the preregistered tested conditions, **not absolute proof**. A scientific failure does not erase an honestly accepted engineering delivery, but it can require corrective software work and reevaluation.

Example: **Stage 9 engineering = OPERATOR_ACCEPTED** and **Stage 9 science = NO_GO** is representable without contradiction. The existing scientific NO-GO must remain visible until changed by an independent approved scientific procedure.

## 3. Lightweight 600-world-step developmental protocol

### 3.1 Purpose and minimum

One **reproducible 600 committed-world-step observation** per stage is the default bounded **behavioral smoke test**. A simulated day is 300 world steps under v1.2.1, so this covers two simulated days, **not** a 60-day life. These are world steps, never 600 cognitive cycles or rollback attempts.

It is evidence for a **plausible functional hypothesis**, not statistical confirmation, an independence claim, or a substitute for an invariant check. When a behavior depends on longer aging, rare events, cross-world generalization, or population variance, 600 steps cannot establish that property. The stage report MUST label that question as **DEFERRED_TO_SCIENCE** or **NOT_OBSERVED**, without presenting absence of events as success.

### 3.2 Before execution

The developer MUST record a stage/commit SHA, environment and dependency versions, equipment/configuration hashes, scenario identity, public development seed, full starting state or snapshot hash, target behavior, trigger conditions, at least one falsifying observation, and the metrics/event counters to be captured. Select and record the scenario **before** inspecting its output. Scenarios MUST be development fixtures, never reserved held-out material. Keep failures, alternative attempts, and revisions in the record; do not selectively publish only favorable traces.

For each stage, construct an attainable scenario exercising its **principal target** within the window. If no relevant stimulus occurs, the observed result is **INCONCLUSIVE / NOT_OBSERVED**, not “passed”. A short targeted unit/contract test MAY complement the 600-step run for rare safety paths; it does not change the 600-step report into scientific proof.

### 3.3 During and after execution

- Run the real integrated runtime with v1.2.1 causal timing and access boundaries; 600 **committed** steps must be accounted for. Record unexpected deaths, lethal transitions, rollbacks, safety blocks, stop events and missing observations honestly, including external bench counters.
- Retain a complete hash-chained journal, run manifest, versioned parameters, snapshot/replay references, raw metrics, test results, and machine-readable failure reasons. On unsafe or terminal interruption, stop safely, retain evidence, and mark the 600-step criterion **not met** rather than silently stitching runs together.
- Reexecute the same configuration to verify exact deterministic replay and relevant snapshot continuation; applicable security and isolation tests still run independently. A journal mismatch, violated hard invariant, or unhandled unsafe transition blocks engineering readiness even if the behavior looks encouraging.
- Write an explicit **observation → limited hypothesis → known counterexamples → deferred scientific questions** conclusion. Use “observed in this scenario”, not “proven”, “reliable in general”, or “scientifically validated”.
- If the targeted behavior did not occur, the stage remains open unless the operator explicitly accepts a **software integration-only** scope with its missing behavioral demonstration identified as a blocker for any later functional claim. No scope adjustment can waive hard technical or safety invariants.

The 600-step window is a **default ceiling for routine development evidence**, not a ban on small unit tests or operator-requested diagnostics. Extra long runs and statistical comparisons are not mandatory for ordinary stage closure. They are mandatory later when required for a scientific claim.

### 3.4 Hard gates that 600 steps never replace

At the implemented scope, all applicable INV-01…INV-58 checks, deterministic journal/replay, snapshot integrity, version freezing, no oracle leakage, command provenance, action control and safety veto, rollback, compute budget and stop/control mechanisms remain mandatory. A newly implemented invariant becomes applicable when its owner/trigger exists. A failed applicable hard gate is **BLOCKED**, not deferred scientific evidence. If an invariant cannot yet be exercised because its component is genuinely absent, record **NOT_APPLICABLE_YET** with the stage of planned verification; do not report “green”.

Scientific **effectiveness** is deferred; technical **correctness, integrity and safety** are not.

## 4. Operator gate and in-situ testing

After technical checks and the 600-step packet, the agent MUST present the operator with a concise request containing:

1. Stage and exact implementation commit; completed features, unit/contract/invariant and replay results, including failures.
2. A 600-step scenario, exposed target behavior and measured counts, reproducibility instructions and evidence location.
3. Unobserved behaviors, scientific limitations, risks, remaining tasks and the scientific status unchanged.
4. A clear **operator decision request**: ACCEPT / REQUEST_REAL_RUNTIME_TEST / REJECT.

The operator MAY request a supervised test **in the actual conditions of operation of the integrated MVP** at the end of a stage or after Stage 13: use the real simulator/runtime, relevant hardware/environment when applicable, and observe the individual rather than an isolated mock. The agent provides exact reproduction steps, expected observations, stop instructions, and a place to save the result. The agent MUST NOT assert that a human test occurred unless its actual result was supplied.

An operator may accept a stage with **non-critical** scientific questions deferred; acceptance must include the scoped limitations. The operator cannot waive an unresolved hard safety or integrity failure. The acceptance record MUST identify an actual decision maker, date/time, stage, code commit, evidence identifiers, decision, conditions and acknowledgment of unresolved limits. An empty or generated template is **not** approval.

No stage, including Stage 13, changes to OPERATOR_ACCEPTED without that explicit record.

## 5. Revised stage roadmap (same software architecture)

The build content of §20.3 is retained except for the explicitly revised Stage 13. The **developmental observation** in this table is a targeted example, not a scientific success threshold.

| Stage | 600-step developmental observation / target | Scientific question deferred to Phase S |
| --- | --- | --- |
| 1. Execution substrate | deterministic journal, restore, replay and message rejection during a bounded run | independent reproducibility across environments |
| 2. World, body, bench | body/world physics, external counters, lethal restore and bench isolation | realism of world assumptions and cross-world robustness |
| 3. Reflexes | stimulus triggers immediate avoidance; dangerous command vetoed | reliability/coverage over diverse hazards |
| 4. Minimal cognition | traceable need → goal → option → action → feedback | general quality of arbitration and goal alignment |
| 5. Temperament | contrasting recorded tendencies on triggered choice opportunities | differences exceed noise, battery reliability, H1 |
| 6. Equipment and simulator | bounded horizon prediction, planning and incomplete-evaluation handling | independent calibration, horizon error and equivalence |
| 7. Memory | a past event is recalled and changes a subsequent decision | past-dependent gain, false memories, generalization |
| 8. Online learning | recorded state/action updates after consequences; no same-cycle influence | learning curves, calibration and controlled baselines |
| 9. Causal model and agency | observable hypothesis/test/safety-fact path; correct provenance and INV-25 | actual causal identification, intervention efficacy, superstition rate |
| 10. Sleep and consolidation | a sleep/consolidation event, interrupted recovery and coherent commit | long-term retained benefit and H3 |
| 11. Exploration and modulation | exploratory option and profile activation/deactivation | coverage, noisy-TV avoidance across conditions |
| 12. Metacognition and health | triggered detector, bounded UC and safe degraded/stop behavior | endurance and 60-day stability under variable load |
| 13. MVP software integration | end-to-end two-day run with all modules, provenance, snapshots, safety and replay | integrated hypotheses H1–H6 and module attribution |

For modules whose timescale exceeds two simulated days, the 600-step trace tests **wiring, safety, triggers and local state transitions only**. The longer-horizon claim stays explicitly untested. Stage 13 delivery requires that Stages 1–12 have genuine recorded OPERATOR_ACCEPTED decisions, no unresolved critical technical gate, reproducible integration, an evidence inventory and **one final operator software-MVP approval**. Stage 13 MUST NOT be described as a scientific campaign or a scientific success.

## 6. End-of-project Phase S: scientific qualification

Phase S starts **after** the MVP has been delivered and accepted as software, on a separately frozen reference implementation and independently controlled protocol. It is **not Stage 14 and not an automatic test on each development commit**.

### 6.1 Required experimental discipline

- Inventory every implemented module and behavior; associate owner, implementation SHA, interfaces, requirements, hypothesized effect, measurable outcomes, threats to validity and current scientific status.
- Preregister hypotheses, effect sizes or materiality thresholds, positive/negative controls, metrics, exclusions, stop rules, analysis plan, independent seeds/worlds and an appropriately justified sample size/power or precision target **before accessing the results**.
- Use independent held-out worlds/seeds/custody, separate development and evaluation access, retain raw unfavorable as well as favorable results, and publish uncertainty/confidence intervals. Repeated development trials do not become held-out evidence.
- Compare **baseline vs module-enabled vs ablated/disabled**, with controlled differences and identical exposure/budgets, plus integration interaction tests where dependencies matter. A baseline that changes several mechanisms cannot establish a module-specific effect.
- Freeze hashes of code, parameters, scenario generation, equipment, protocol and analysis; ensure replay and provenance. Any material software change requires a new scientific freeze or explicitly preregistered comparison.
- For every module, issue an independent **SUPPORTED_WITH_LIMITS / NOT_SUPPORTED / INCONCLUSIVE / NO_GO** verdict. An inability to identify a module's effect must be reported, not hidden by aggregate MVP performance.
- Conduct the integrated v1.2.1 §19.5 experimental program for H1–H6, including crossed temperament/world/seed conditions, disposable battery copies, ablations, substitution/bifurcation, the 60-day horizon, and statistical analyses, unless a prospectively approved protocol revision explicitly justifies a different design.
- Obtain an independent scientific reviewer/evaluator and a distinct final scientific decision. Operator engineering approval and CI do **not** stand in for scientific independence.

### 6.2 Module-by-module evidence matrix

| Module or layer | Minimum scientific comparisons / measures |
| --- | --- |
| Execution substrate, journal, snapshots | exact reexecution on declared reference environments; seeded perturbation and restore/corruption controls |
| World, simulated body, bench | transition/observation fidelity, oracle isolation and scenario-generator controls |
| Perception, gatekeeper, S_t | oracle-relative relevance precision/recall, crowding and random/unlimited-gatekeeper controls |
| Value, goals, competition, action control | goal progress, alignment, safety interventions, ablation of each decision route |
| Temperament and identity | noise controls, trait-battery reliability, same/different temperament and history, H1/H2/H4/H5 |
| Simulator and planning | horizon-wise errors, calibration, matched budgets, simulator/planner-disabled baselines |
| Memory | memory-enabled vs disabled tasks requiring history; exact recall and false-memory rates |
| Online learning and reliability κ | independent learning curves, Brier/calibration, no-learning and shuffled-outcome controls |
| Causal model and agency | blinded known-cause worlds, real interventions vs correlation-only control, superstition rate, INV-25 comparisons |
| Sleep and consolidation | matched consolidation-enabled/disabled trajectories, interruptions, stability/retention, H3 |
| Exploration and modulation | novelty/coverage, noisy-TV trap, profile switches, exploration-disabled control |
| Metacognition and health | detector accuracy, non-intervention controls, graded UC pressure, 60-day endurance |
| Integrated architecture | H1–H6 together, A1–A4/B0–B2 references, interactions and negative or inconclusive outcomes |

**Final scientific gate:** each module receives a documented verdict and its uncertainty; all required critical invariants remain technically green; the integrated evaluation is reported with its limitations and negative results. “Science complete” means **evaluation complete and conclusions recorded**, not that every hypothesis must be supported. An unsupported hypothesis may lead to a redesigned vNext, but must not be rebranded a success.

## 7. Evidence and reporting contracts

Every engineering stage SHOULD store a small versioned evidence packet, with fields:

- **identity:** stage, run identifier, full code SHA, scenario/config version, seed, environment, timestamps, accountable agent;
- **technical checks:** commands, results, applicable invariant IDs and outcomes, replay/journal/snapshot hashes, failure references;
- **600-step run:** planned and committed steps, target stimulus count, response count, metrics, negative cases, stop/rollback/death counters, complete retained log references;
- **interpretation:** observation, plausible hypothesis, limits, NOT_OBSERVED or DEFERRED_TO_SCIENCE markers;
- **operator review:** decision, actual operator identity, dated evidence reference, scope and outstanding work;
- **science axis:** independent status and its existing source reference, unchanged by the stage packet.

Store machine-readable artifacts under the existing Lab/evidence conventions and link an operator approval record. Do not commit personal secrets, withheld seeds, oracle truth, or private custody material to public GitHub. Templates are provided in the matching research documentation.

## 8. Adoption, parallel agents, and legacy evidence

1. **Proposal stage:** add this file and the French equivalent on a documentation-only branch. v1.2.1, existing CI, and Agents A/B's code branches remain untouched.
2. **Operator adoption:** review and explicitly approve v1.3 as the new *stage-delivery policy*. Only then update repository reference indexes and agent task instructions to point to v1.3, without rewriting the historical v1.2.1 normative artifact.
3. **Forward migration:** reclassify existing technical reports as engineering evidence **only if** they truly satisfy section 3. Historic passes are not invented; historical NO-GO, failures and missing operator sign-offs remain as recorded.
4. **Stage reassessment:** never retroactively mark a stage OPERATOR_ACCEPTED because it was previously called “green”, “done”, “Golden”, or merged. Ask the operator with a concrete evidence packet.
5. **Scientific isolation:** Stage-9 independent held-out prelaunch remains NO-GO until its own independent protocol authorizes and completes it. No relabeling of developer fixtures as scientific samples.
6. **Change management:** after approval, architecture changes still require separate versioned technical/architectural decisions. This policy cannot be used to relax invariants, alter v1.2.1 algorithms or disguise exploratory tuning as preregistered science.

## 9. Approval record for this proposal

- **Proposed scope:** separate bounded engineering stage acceptance from final scientific evaluation.
- **Architectural modifications:** none.
- **Scientific hypothesis changes:** none.
- **Approval to make v1.3 active:** **PENDING OPERATOR DECISION**.
- **Operator, date, repository decision/PR:** **UNSET**.

Until this record is genuinely approved and the project adopts it, this document is **informative draft text only**.
