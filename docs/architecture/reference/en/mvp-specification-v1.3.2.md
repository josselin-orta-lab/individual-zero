# Individual Zero — Normative MVP specification v1.3.2

**Title:** First-person goal-result agency, independent lived outcomes, and fail-closed attribution diagnostics  
**Language of authority:** English  
**Date:** 2026-10-13  
**Document state:** **NORMATIVE IMPLEMENTATION TARGET, OPERATOR-APPROVED SCOPE; SOFTWARE CONFORMANCE NOT YET CLAIMED**  
**Historical authority:** [v1.3.1](mvp-specification-v1.3.1.md) and its retained [v1.2.1](mvp-specification-v1.2.1.md) rules.  
**Scope of this version:** issue [#110](https://github.com/josselin-orta-lab/individual-zero/issues/110), Stage 12 attribution only.

## 0. Authority, non-retroactivity, and precedence

This is a **new** normative delta to v1.3.1, not an edit or retroactive reinterpretation of historical specifications. v1.3.1 remains binding in full except where this document expressly adds or replaces rules for goal-result agency. The six cognitive phases, WorldBody physics, unique canonical state owners, M-11 current-generation transactional continuity, exhaustive internal journal, independent Oracle and Bench, irreversible mortality, UC limits, Stage 9 scientific **NO-GO**, operator stage approval and separate final scientific validation remain unchanged.

The *unadopted* `docs/architecture/proposals/mvp-v1.3.2-dc05-food-safety-semantics-delta.md` remains **proposal only**: version 1.3.2 does **not** adopt or alter the suggested DC-05 food-safety semantics. That proposal needs a later, separate operator-approved normative revision. No existing Stage 9 causal/safety status, learning rate, veto or κ calibration is changed here.

**Deployment gate:** publication of this specification does not mean that any executable Stage 12 implementation already conforms. Add a separately reviewed and CI-validated code PR, preregistered experiments and explicit operator reception. Keep issue #110 open until its acceptance criteria are met.

## 1. Three distinct propositions (new mandatory contract GA-01)

Every goal-related trace distinguishes:

1. **Goal criterion outcome (`goal_criterion_outcome`)**: `success|failure|unknown`, the result of a pre-action, versioned *observable* one-step criterion (for example strict increase in perceived body water on the immediately following capture). `failure` only means that this bounded criterion was *not met*, not that the whole goal failed and not that I0 caused it. `unknown` for absent, invalid, late, terminal, cancelled or uncharged observations.
2. **Prediction fidelity (`prediction_status`)**: P-47's unchanged `conforming|nonconforming|indeterminable` applied to frozen predicted effects. No inference from this status to goal outcome, agency responsibility or physical causal truth is permitted.
3. **First-person responsibility judgement (`subjective_agency`)**: `self|world|unknown`, a fallible *belief of I0* about its contribution to the consequence relevant to the precommitted goal, formed solely from legally perceived cues and command-effector evidence. This belief is neither an objective physical etiology nor an Oracle/Bench verdict. An explicit `unknown` is a completed and legitimate cognitive judgement; an absent computation is separately `unavailable`.

P-47 labels `self_compatible|world_justified|uncertain` retain their old meanings; they MUST NOT be renamed, mapped or implicitly coerced to `self|world|unknown`. Goal progress and prediction correctness MUST NOT determine a responsibility judgement, nor may a detector or audit fabricate that judgement.

## 2. Existing component ownership (GA-02)

**Action Control**, under the existing canonical `action_control` owner, owns a *bounded subordinate* `GoalAgencyJudgement` service. This is not a new top-level module or independent state owner. It alone computes and publishes the first-person responsibility belief. It receives command efference/admission metadata and the legitimate pre-/post-action Perception capture through declared interfaces. It MUST NOT consult WorldBody raw/hidden state, scenario schedules, Oracle, Bench, laboratory traces, an operator diagnostic, the technical journal as a cognitive input, the detector's output, or an independently computed `success/failure` result.

**Metacognition and Health** remains the sole owner of its canonical `Stage12GoalProgressLedger`, the admitted attribution pair ledger and detector history. Only Metacognition joins separately produced, immutable source references. Causal Model retains ownership of its own established causal statuses and interventions; subjective judgements cannot establish a contingency, change safety-use evidence, update κ, grant motor authority or correct the Simulator. Goal Manager, Perception, Memory and Scheduler keep their previous owners. No mutable duplicate of any of these ledgers is allowed.

## 3. Two independent preregistrations and one later observation (GA-03)

Before a command is physically sent, and only for an active goal-motivated, *admitted* command, record:

**Outcome intent**, using the existing `Stage12GoalProgressLedger` whenever possible: `life_id, intent_ref, goal_ref, option_ref, command_digest, sent_world_step, baseline_measure, baseline_value, comparator, threshold, observe_deadline, version`. The current strict-gain one-step criterion stays supported unchanged. It must be written before the physical transition and linked to the actual uniquely executed command.

**Agency assessment commitment**, produced and owned by Action Control: `life_id, agency_assessment_ref, intent_ref, goal_ref, option_ref, command_digest, sent_world_step, observe_deadline, policy_version, pre_action_cues_ref, candidate_mechanism, allowed_cue_mask`. Its source is efference and perceptible pre-action circumstances, not a post hoc success flag. The commitment is one per intended physical step; unsuccessful admission creates no admissible pair. `candidate_mechanism` describes the agent's hypothesized route of influence; it is not a physical cause label. Pre-registration alone does not count as a finished subjective judgement.

The next authorized single physical-step perception may independently close the outcome intent and supply bounded non-outcome agency cues. Both evaluations must refer to the **same genuinely executed command**, life identity, attempt and observation window but remain computed by their separate canonical owners and algorithms. The external journal records immutable commitments and source references; it must not become a cognitive input.

### 3.1 Semantically grounded judgement policy (GA-04)

Define a deterministic, versioned **responsibility-evidence policy** at birth, frozen for the life. It must use first-person information and offer `self`, `world` and `unknown` as *possible* results without treating policy outputs as physical causal truth.

Permitted classes of evidence:

- **Self-linked mechanism:** an admitted voluntary command with a recorded efference copy, whose *independently accessible, action-specific effect* was witnessed in the authorized next-step perception, with a predeclared physical link (e.g., proprioceptive displacement after a directional movement, or direct manipulation witnessed by an accessible modality). This does **not** imply that the goal criterion succeeded. Command issuance alone or a prediction matching observation is insufficient. The witnessed cue may share the physical consequence but MUST NOT be the same derived `success/failure` Boolean or a copy of the measured criterion.
- **External mechanism:** a specific *perceived* external interruption/change independently identifiable and temporally relevant to the attempted effect (e.g., a perceptible blocking obstacle at the actual attempted destination). Merely observing an adverse outcome, a mismatched P-47 prediction, or generic environmental variability is insufficient.
- **Ambiguity:** insufficient cues, a confound, simultaneous plausible personal and external sources, disputed timing, missing observation, a single sensor repeating itself without fresh consequence, or uncertain relation to the goal ⇒ `unknown`.

`self` means I0 **subjectively credits its own contribution** where direct efference plus a witnessed action-specific cue supports that belief; `world` means I0 **subjectively credits a witnessed external constraint or intervention** as the dominant candidate; `unknown` is mandatory when neither is uniquely supported. The policy must justify the connection to the *goal-relevant consequence*: an unrelated observed movement or unrelated obstacle MUST NOT be used to attribute a separate hydration/health outcome. In particular, observing a fall in integrity after eating a berry with a nearby creature does not identify the creature or berry as the physical cause.

To avoid tautology, computing `subjective_agency` MUST NOT read: goal criterion `success/failure`, the detector's history, `goal_progress_delta`, a truth label, or a P-47 overall/attribution label as a categorical substitute. It MAY use low-level observed cues that are independently available to I0 and that a particular P-47 implementation also receives, only if the agency rule has its **own versioned semantics, evidence references and provenance**. A change in a predicted value while keeping actual command and perception fixed MUST NOT change this subjective judgement unless it legitimately changes a previously declared action-efference cue. Attribution may remain `unknown` for long lives; coverage must be reported, never forced by lowering thresholds.

The final `GoalAgencyJudgement` is immutable, with `judgement_ref, agency_assessment_ref, life_id, intent_ref, command_ref, action_observed_ref, sent_world_step, observed_world_step, judged_cycle, cue_refs, policy_version, subjective_agency, uncertainty_reason`. Exactly one closure (`self|world|unknown|unavailable`) may occur for an assessment; `unavailable` is *not* evidence of the agent choosing `unknown`. Missing or refused UC produces `unavailable`, never a fabricated belief.

## 4. Timing, UC, life and M-11 (GA-05)

- The six cognitive phases and DC-11 ownership order are **unchanged**. The single pre-step physical capture is immutable throughout deliberation. Record pre-action assessment alongside admitted action/goal precommit before WorldBody application. No cognitive judgement can occur after death.
- Action Control may compute its new assessment during the next waking cognitive cycle from the already accessible capture, at an explicitly versioned `goal_agency_assessment` UC cost, and publish the immutable closure via the existing canonical publication boundaries. No free work in Lab, journal hooks or post-transition callbacks. If the UC debit is refused, publish only an incomplete technical receipt with no invented `self/world` judgement.
- Close the goal-progress criterion by its separately charged existing diagnostic contract. Only **after both immutable receipts** exist may Metacognition attempt a join, at a separately versioned `stage12_attribution_join` UC debit (or under a formally increased, demonstrably sufficient versioned diagnostic cost). Keep existing physical-step sampling at most once per truly experienced world step; extra cognitive cycles do not multiply evidence. An accepted join becomes visible in a **later** diagnosis, never retroactively in the prior published diagnosis.
- The exact costs are positive deterministic P-43 parameters registered **before birth**. No ceiling increase is silently made midlife. Refused operations remain unknown/unavailable; they cannot be retried to fabricate extra samples. Fatigue must include all actually charged work.
- Persist Action Control's assessment state inside its existing owner; persist pending/consumed joins and verified references inside the unique Metacognition owner. Export and restore these only through M-11's current authenticated generation and atomic owner roster. Reject older snapshots, duplicate references, mismatched lifetimes, out-of-window samples, noncommitted steps, cancelled attempts and attempts to resurrect dead identities.
- A lethal physical transition has a terminal technical record but no postmortem perception, judgement, pair, metacognitive publication or learning. A period of sleep with no permitted waking cognition yields no imaginary sample. No technical operator report flows back into cognition.

## 5. Independently admitted evidence and detector (GA-06)

The sole admissible detector input is a join of:

`(life_id, goal_intent_ref, command_event_ref, transition_event_ref, perceived_outcome_ref, subjective_judgement_ref, outcome, agency, attribution_ref, policy_versions, UC_receipts)`.

Admission requires a pre-action intent and agency commitment, matching physically **applied** command digest and same life, a later authorized perception within the time window, two **distinct original** computation chains for outcome and judgement, intact event/reference lineage, paid cognitive computation, correct publication order, and exactly one unique pair identity. A physically true consequence independently established by an offline evaluator cannot be silently injected as an agent judgement. A hash-valid journal by itself does not attest physical truth or establish the semantic legitimacy of an invented judgement.

The attribution-bias detector may use only joined `success/failure` and `self/world` pairs. **Unknown outcome, unknown subjective agency, unavailable computation, unlinked records, or repeated physical evidence do not form a pair.** Count unique goal-action-experience events, not duplicate processing of one record; repeated uses of one observation cannot satisfy independent-sample thresholds. The existing four-detector bounded window and preregistered Stage12 thresholds remain versioned. When either outcome class lacks the configured count, output `None`, never `no_detected_pattern`. An available negative pattern needs sufficient real pairs in *both* classes.

The implementation may classify `self_serving_pattern`, `self_blame_pattern` or `no_detected_pattern` only as a **descriptive association between subjective beliefs and bounded observed outcomes**. None establishes objective causes or a general psychological trait. Do not use the pattern to change I0's value learning, goals, safety, TD, world effects or Action Control authority.

## 6. External audit and adversarial acceptance (GA-07)

Provide a standalone independent auditor that uses canonical exported technical receipts, but **never imports or instantiates** I0, WorldBody, Oracle or Bench. It must verify exact schemas and versions, SHA-256 chain, life ID, chronology, command and transition, actual perceptual capture provenance, source semantics, precommitted cues, confidence/unknown, pair uniqueness, source separation, relevant UC charges, snapshot/cold-recovery consistency, absence of cognition after death and the recomputed detector result. It must reject manufactured events even when the complete hash chain has been correctly rebuilt. Semantic verification of receipts and independent physical truth are separate audit levels.

Minimum acceptance tests:

1. Real integrated WorldBody transitions yielding preregistered strict gains, non-gains and unavailable outcomes; changed P-47 predictions under an identical lived consequence do not change those labels or automatically manufacture agency.
2. Separate real first-person `self`, `world` and `unknown` judgements *where lawful cues exist*. Also verify contexts in which one or both categories never occurs.
3. Independently sourced success/failure pairs, at least two distinct physical references per class, then the configured detector counts; synthetic-only positive/negative tests are labeled software fixtures and **not** credited as lived scientific evidence.
4. Positive `self_serving_pattern`, `self_blame_pattern`, `no_detected_pattern`, and correctly unavailable `None`, without manufacturing action selection, truth labels or reducing detector thresholds.
5. Tampered-and-rehashed journals: wrong lifetime, forged Action Control judgement, duplicate references, changed prediction, missing perception, reused outcomes, late receipt, invalid phase, unauthorized provenance, and UC refusal; all must fail closed.
6. Python 3.11/3.12, Stage 9/10/11/12 and Observer non-regression; M-11 hard-crash `os._exit` and authenticated cold recovery with both owners, death and terminal freeze, exact replay where applicable, independent Oracle/Bench isolation and deterministic outputs.
7. Pre-registered exploratory development runs totaling at least 600 **actually applied** physical steps across independent lives when possible, with honest counts for all outcome and attribution classes, abstentions, refusals, UC, deaths and archives. Do not forcibly select favorable actions. Six hundred steps without admissible pairs do not constitute attribution validation.

## 7. Stage gates and supersession map

| Scope | v1.3.2 authority |
| --- | --- |
| v1.2.1 §9.6 P-47 predictor comparator | **UNCHANGED**; new subjective goal agency is a separate Action Control subservice and contract. |
| v1.2.1 §16.1 / §20.3 Stage 12 | **EXTENDED** with GA-01 to GA-07; four detectors still required. |
| v1.2.1 DC-06 | **UNCHANGED**; subjective first-person judgements are not strong κ verification or proof of objective agency. |
| v1.2.1 DC-11 and P-43 UC | **UNCHANGED STRUCTURE**, new declared paid operations integrated into the same cycle and budgets. |
| v1.3.1 §1–§10, M-01 to M-20 | **RETAINED**; atomic continuity, mortality and independent audit apply to new records as well. |
| Unadopted DC-05 v1.3.2 *proposal* (issue #89) | **NOT ADOPTED**; no change to toxic-food inference, safety or Stage 9 NO-GO. |

**Stage 12 remains IN_PROGRESS** until a PR implements and independently audits this contract, sufficiently diverse genuine lived evidence supports at least a development hypothesis, and the operator explicitly accepts the stage. The eventual project-wide module-by-module scientific validation is separate and remains required.

**This specification is a target, not a claim that the current runtime has passed its acceptance criteria.**

## 8. Operator-authorized Option A: directly perceived spatial subgoals (GA-08)

**Amendment authorization:** operator explicitly selected *Option A* on 14 October 2026. This provision extends only the v1.3.2 normative target, not earlier historical standards. No claim of complete implementation or scientific validation follows from approval.

A goal-directed **spatial subcriterion** is distinct from terminal resource or body fulfillment. `spatial_progress_v1` is admissible only when I0 has perceived, **before the admitted action**, a concrete resource/water target at a locally grounded position; an unperceived laboratory target, hidden world coordinates, or an oracle annotation is forbidden. The active goal must independently support the resource kind, and the particular voluntary `se_deplacer` step must be issued with the canonical `active_goal` motive and an established target/direction relationship. Do not declare every exploratory move a goal action.

Metacognition extends the **existing** `Stage12GoalProgressLedger`, not a second ledger, using an immutable pre-action criterion:
`life_id, intent_ref, goal_ref, option_ref, command_digest, physical_step, observable_target_ref, perceived_target_x_y, initial_x_y, authorized_direction, initial_manhattan_distance, criterion=strict_manhattan_distance_decrease, deadline=physical_step+1, contract_version=spatial_progress_v1`.
The target must be traceable to an authorized Perception capture and related to the active goal. The follow-up independently compares the **authorized next Perception position** to the frozen target and baseline. `success` means only distance decreased; `failure` means it did not, **not** that an obstacle physically caused the failure. Missing/late/unpaid/cancelled observations yield `unknown`. Body-goal strict-gain semantics remain unchanged and must never be silently replaced by a spatial criterion for the same command.

Action Control may precommit a distinct, versioned `spatial_obstacle_cue_v1` first-person mechanism **for that same command/goal**, using only the efference copy, direction and the permitted adjacent-cell perception. After an authorized capture:
- `self` may be judged if a position change following the admitted command is *perceptually witnessed*, is in the committed direction, and is relevant to the same target; this remains a belief, not proof of causation.
- `world` may be judged only when a **specific, independently observed non-passable cell** is at the attempted destination in the legitimate capture, the actor remains at the committed position, and the attempted step is related to the precommitted goal target. Perception must support the external constraint, not merely the unchanged position. A known obstruction does **not** grant authority to force a blocked action; admissibility and autonomous plan selection remain authoritative.
- `unknown` is required whenever the destination is not perceptually known, the cue is stale or ambiguous, a target/direction is not goal-relevant, multiple mechanisms compete, the command is unexecuted, or the observation is not authorized. A P-47 prediction mismatch or bodily non-gain is **never** an external-obstacle cue.
- `unavailable` remains distinct from a paid, explicitly uncertain judgement.

The outcome calculator must not read the judgement, and Action Control must not read the goal criterion result. Versions, identities, cue references, temporal windows, accepted UC debits, owner snapshots, M-11 atomic cold recovery, operator audit and postmortem prohibitions remain as GA-01..GA-07. Both spatial assessment and follow-up work must be explicitly included in their owners' **versioned, accepted** UC charge contracts. Diagnostic pairs still require uniqueness, two original independent owner receipts, a separately paid join and a *later waking diagnostic within the existing one-step window*. **No threshold change or artificial sleep bypass** is allowed.

External independent audit MUST reconstruct (1) the original target observation and spatial precommit; (2) the actual Action Control command and WorldBody transition receipt; (3) the admissible next perception position and cell passability; (4) both independent calculations, distinct references and paid UC; (5) the detector's unchanged result; (6) provenance despite a correctly rebuilt technical hash chain. In particular a rehashed claim of a blocked destination, mismatched direction, unrelated target, nonexecuted command, elapsed window, absent perceptual capture, wrong life or refused UC must fail.

**Reception constraint:** a positive `world` fixture validates software semantics only. The issue #110 requires real autonomous physical trials, with authentic `self/world/unknown` only where their cues and sources are legitimate. If the planner never autonomously attempts an obstructed goal-directed command, record `world=0`, keep bias detection unavailable and do not force one or declare Stage 12 complete.
