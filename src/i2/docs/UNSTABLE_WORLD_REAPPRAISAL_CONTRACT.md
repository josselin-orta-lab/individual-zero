# I2 unstable-world reappraisal contract v1

**Status:** I2-only research contract proposal, not integrated into the running
I2 toy world and not a natural-learning, reflex, M11 or motor implementation.

## Why this is a distinct contract

The exact-head #827 blind-restoration falsifier shows identical subjective
histories when a previously harmful food becomes beneficial **without a new
observable cue or chosen re-exposure**. The observational policy cannot
identify the regime, even while the fixed-prior comparator can accidentally
discover recovery by eating again. Under ADR-0006 this is an information
boundary, *not* a standalone learning failure. A fixed stale-time +9
revisit bonus also worsened survival in other experimental worlds and must
not be promoted as natural curiosity.

This contract separates (1) *reason to reconsider* from (2) *evidence that the
world changed* and (3) *permission to act*. Its minimal typed coordinator is
`src/i2/modules/unstable_world_reappraisal_contract.py`. It exposes one
non-motor `review_reappraisal` and no new SQLite owner.

## Dependencies and responsibilities

| Contract | Input | Authority and limitation |
| --- | --- | --- |
| I2 current first-person observation | current life/capture, accessible actions, subjective evidence refs | source port must verify current claim; no hidden payoff/phase allowed |
| H2 chosen-outcome memory | previous personally chosen outcome records | ordered, unique, earlier than current capture; never an unchosen counterfactual |
| **Survival reflex (required dependency)** | fresh, same-life, same-capture `PREEMPT/CONSTRAIN/NO_PREEMPTION/UNKNOWN` | source MUST verify; preemption and constraints dominate any need or context cue; **not implemented** as real I2 reflex yet |
| Physiological need / interoception (optional dependency) | verified `CRITICAL/ELEVATED/NONE/UNKNOWN` bound to current capture | only a motive to consider risk, cannot override reflex, cannot invent reward |
| Context/sensory change (optional dependency) | references in the current subjective capture | new information permits a reappraisal hypothesis, **not proof** of safety |
| UC Scheduler + Competition | full paid candidate evaluation | not invoked by this pure classification function; actual integration must charge UC first and use existing I2 Competition |
| Action Control + WorldBody | fresh safety/veto, internal admission then committed physical consequence | always retains sole action authority; reappraisal advice **never selects or sends** an action |
| M11 / identity | real life provenance and irreversible causal order | unavailable in this prototype; a mock verification is not an attestation |

The first executable contract deliberately **fails closed without a survival
reflex snapshot and its verified source**, rather than substituting a fake
survival reflex. Future I2-owned reflex work must specify what it senses,
preemption/priority, terminal limits, costs and how its authority interacts
with Competition and Action Control. The policy must not infer world
instability simply because time passed.

## Output semantics

- `LATENT_CHANGE_UNIDENTIFIABLE_DEFER`: no new context, no contradictory
  personally observed outcome, no verified critical need. Invisible recovery
  cannot be diagnosed.
- `EVIDENCE_BASED_RECONSIDERATION_HYPOTHESIS`: source-bound changed context
  or personally observed contradictory outcome; **not** confirmation.
- `NEED_BASED_RISK_RECONSIDERATION_HYPOTHESIS`: critical first-person need
  motivates considering a risk, not knowledge of a safer environment.
- `REFLEX_PREEMPTED`, `REFLEX_CONSTRAINED`, `REFLEX_UNKNOWN_DEFER`: survival
  reflex has priority; no risk-taking permission.
- `REFLEX_UNAVAILABLE`, `TARGET_NOT_AVAILABLE` and
  `NO_PERSONALLY_LEARNED_AVERSION`: cannot generate a spurious re-exposure.

Every readout has `motor_authority=NONE`, `m11_authenticated=False`,
`hidden_regime_identified=False`, and requires ordinary paid Competition and
fresh Action Control. No free UC or external motor effect is granted.

## Scientific falsifiers before any integration

Test matched harmful vs hidden-recovered worlds with no cue, new reliable
and misleading cues, critical versus noncritical need, survival reflex
preemption/constraint, and delayed positive/negative personally chosen
re-exposure. Report harmful retry, unnecessary deferral, UC, death and
right-censoring. The exact v1 no-cue null must remain. No adjustment of
the existing +5 score, +9 exploratory comparator or frozen G1-LAB v1-r1
protocol is justified by this interface.

**Targeted unit command:**
`PYTHONPATH=src python -m unittest discover -s tests/i2 -p 'test_unstable_world_reappraisal_contract.py' -v`.

A PASS validates *interface coherence only*, not that the prototype uses
this contract or that it improves autonomous survival.

## Local energy reflex source (next incremental engineering step)

`src/i2/modules/local_survival_reflex.py` now implements an **owner-local,
nonmotor** survival-reflex snapshot from the exact audited predecision energy
in the existing single SQLite WorldBody. For this bounded world, an energy
reserve of 1–2 is labelled `PREEMPT`, 3–4 `CONSTRAIN` and 5–100
`NO_PREEMPTION`. These transparent thresholds relate to the prototype's
1-unit physical tick and 2-unit chosen action cost; they are researcher-set
engineering bounds, **not** evidence of learned physiological regulation.
The source reuses the current capture's `evidence:i2:energy:<N>` ref and
verifies the entire exact claim/snapshot rather than trusting a free-form
report. Foreign and stale captures, unobserved energy and terminal energy
cannot yield a valid snapshot.

The audited `IsolatedI2.decision_evidence()` now includes
`survival_reflex` at each already-committed decision, derived from the same
predecision state and validated claim. This is a **read-only, researcher-only
composition seam**: it does not inject a reflex into paid valuations, alter
Competition, enable risk re-exposure, preempt an already admitted command,
change the journal, or introduce a second state owner. The typed reappraisal
contract can consume a locally sourced report in a controlled test; the
runtime does **not** yet invoke it as a behavioral policy. Reflex authority
for actual future action selection, need integration, and independently
attested M11 remain **NOT_ESTABLISHED**. Do not interpret a local audit as
independent witness provenance. Old blind-recovery negative cases remain
unchanged and no tuned revisit bonus was added.

Focused regression: `PYTHONPATH=src python -m unittest discover -s tests/i2 -p 'test_local_survival_reflex.py' -v`.

## Correction: survival reflex is last-resort exploration, not a food ban

**Owner clarification, 1 November 2026:** PR #830 incorrectly construed low
energy as a reason to prohibit eating. The intended reflex has the opposite
purpose: when no other viable survival plan is available, it must force
reconsideration of an available berry even if earlier subjective experience
suggests toxicity. This does **not** predict that the food is safe.

The isolated research world's only immediately energy-restoring affordance is
EAT (COLLECT prepares and costs energy; DRINK provides no energy). Under
observed energy <= 4, if EAT is available and all currently offered semantics
are understood by the bounded prototype, the local reflex supplies a
**categorical last-resort priority**. It is passed into the ordinary paid
Competition batch, above the existing learned negative score, with its
separate evidence marker. Normal fresh Action Control may still veto and
UC exhaustion prevents the choice. This is not an external actuator, M11
authentication, free reward or generic plan-understanding engine.

Matched favorable and adverse *hidden* food worlds must both attempt the
same risky action when critically depleted. One may recover; the other may
die. These contrasting physical results only become first-person evidence
after the action and at a later capture if the individual remains alive.
The priority is a researcher-specified survival heuristic, not established
natural adaptation or proof of general survival advantage. The old #831
"protective veto causes death" test describes a mistaken interpretation,
not an accepted reflex requirement.

The stable earlier seven-case and blind-restoration source-locked scenarios
must retain their previous numerical evidence as historical results, not be
silently reinterpreted as results of the new reflex-capable runtime. Any
change to their software test expectations must be reported as a new
behavioral policy version, never historical source equivalence.


## Source-pinned science versus explicitly enabled survival risk (follow-up #832)

The **existing historic seven-case and blind-restoration fixtures run their
original observational/no-learning policies**, with
`last_resort_exploration=False` at fresh genesis. This is a controlled
research ablation, not an old-engine compatibility fallback or migration.
The new I2-only survival policy must be *explicitly enabled* per separate
disposable study; the flag lives in the same canonical SQLite `proto_meta`
record and its exact score/evidence are recomputed by the normal journal
audit. No existing prior results are rewritten. This generation does not
accept an old SQLite schema or revive an old identity.

Run the new behavior in the same existing world (separate disposable lives):
`PYTHONPATH=src python -m i2.runtime.isolated_prototype --world --scenario restoration --ticks 16 --last-resort`.
Omit `--last-resort` to reproduce the unchanged historical research
control. Passing this option is a *new explicitly declared experimental
policy*, never a hidden default or permission to claim general adaptation.

A local priority is applied only if the current energy is <=4, EAT is
actually offered, all offered affordances have explicit semantics, and
EAT is **not already the uniquely highest evaluated option**. It then
becomes the uniquely highest within the original paid batch. This is
categorical decision precedence rather than predicting a positive payoff.
Explicit Action Control veto, unavailable UC, death and unknown affordances
remain respected. If EAT is already preferred, no synthetic extra score
or fake priority evidence is added. Audit derives the same condition
from the predecision owner state and rejects mismatched value provenance.

The mechanistic counterfactuals must include *both* hidden restoration and
persistently toxic food, matching initial resources, energy, UC and
physical-tick schedule. Report personally observed adverse EAT results,
last-resort attempts, terminal ticks, censoring and costs, even when the
new reflex causes fatal poisoning. These results remain exploratory
engineered-world observations, not real survival or learning evidence.


## Multiple survival plans: a distinct evidence gate (experimental seam)

The next I2-owned pure boundary is
`src/i2/modules/survival_plan_viability.py`. It requires a verified current
first-person capture, exact current reflex, and a complete source-verified
classification of **every other currently offered affordance** as VIABLE,
NOT_VIABLE or UNKNOWN. The priority classification is:

- If a verified accessible alternative is VIABLE, do not claim the berry is
  the only remaining plan.
- If any alternative remains UNKNOWN, say ALTERNATIVE_UNRESOLVED; lack of
  evidence is not proof that the alternative cannot work.
- Only when the reflex is urgent and **all other offered plans** are
  source-verified NOT_VIABLE may the boundary issue a
  LAST_RESORT_RISK_RECONSIDERATION signal.
- At noncritical energy, no emergency priority arises.

The output is deliberately NONMOTOR and still requires ordinary paid
Competition and fresh Action Control. A real source of viability evidence
for new affordances and its in-owner behavioral integration are **not yet
implemented**. Do not infer plan viability from the hidden food impulse,
researcher oracle or imagined future experiences. The presently integrated
opt-in reflex is still a narrow toy-world heuristic for its fixed three
known affordances; it must not be promoted as a generic agentic planner.
The standalone contract provides a falsifiable next integration criterion,
not a new alternate SQLite owner, legacy compatibility path or safety GO.


## First in-owner composition: bounded alternative-plan gate

The opt-in emergency policy now evaluates its complete known alternative
affordance set with `assess_last_resort`, rather than using only an energy
threshold. `_ToyPlanSource` is an exact-capture, local test source for the
existing WorldBody: in this limited physical model COLLECT and DRINK cannot
restore energy *immediately*, while unknown semantics must be classified
UNKNOWN and therefore block the "only plan" conclusion. This says nothing
about unknown multistep strategies, future affordances or unseen nutrition.
The existing paid Competition still determines the action, safety retains
veto, and the same local owner audit recomputes the decision.

This is a minimal integration seam, not a general plan search. Evidence
reference reuse is only an owner-local, source-verified engineering boundary,
not independent M11 provenance. Targeted regression:
`PYTHONPATH=src python -m unittest discover -s tests/i2 -p 'test_owner_plan_assessment.py' -v`.


## Two-step survival planning hypothesis

`src/i2/modules/two_step_survival_plan.py` provides a **pure, bounded,
nonmotor** feasibility analysis for the sequence COLLECT then EAT. It checks
observed energy, resource availability, currently accessible COLLECT, known
action costs and whether the first action would cause terminal energy. It
distinguishes a feasible sequence from an attempt whose food outcome could
still be terminal. The food payoff is ALWAYS UNKNOWN. This is not a
beneficial-food prediction, learned planning, a committed intention, an UC
reservation, an alternative energy source, or authorization to perform either
action. Every physical effect still needs the real paid owner cycle.

This scoped contract cannot yet compete with another executable two-step
plan. The next integration must evaluate alternative *sequences* from the
same current captured evidence and explicitly report costs, uncertain
consequences and deadlines before taking a risk.

## Two-step paid execution falsifier

The two-step projection alone is not evidence of action. The focused
`test_two_step_owner_execution.py` now checks the same WorldBody running
two consecutive independently paid cognition decisions: COLLECT then
EAT. With the same initial energy=10, stable hidden food leaves energy=12
while harmful food produces modeled terminal energy=0. Both arms pay
the ordinary 4+5 UC, neither has the current EAT consequence available
to the second decision, and no researcher selects the action. The
observed sequence is a programmed toy-world behavior, NOT evidence
that I2 independently invented or maintained a multi-step plan.


## Physical time between steps: necessary survival-plan constraint

An ordered two-action projection must account for elapsed world ticks, not
only the per-action energy costs. The bounded `assess_collect_then_eat`
accepts `ticks_before_second_action` (0 by default for immediate adjacent
decisions). It conservatively subtracts one metabolic energy unit per tick
*after* the collect action and *before* any eating attempt. If energy reaches
zero in between, the plan reports `DEPLETED_BEFORE_SECOND_STEP` rather than
falsely claiming a feasible rescue. If only one or two units remain, the
second action is possible but its outcome remains UNKNOWN and it may cause
terminal energy. No two-step plan executes by itself; motor authority,
per-step UC and the actual world clock are unchanged.

This improvement is a pure planning feasibility boundary, not an inference
that the unknown berry will help. A future plan scheduler must bind the
elapsed time to an authenticated current clock and must refuse to infer
that a proposed delay is guaranteed.


## Actual physical-deadline regression

The focused `test_two_step_physical_deadline.py` compares a prospective
two-tick delay with the actual single-owner physical clock. At initial
energy=4, COLLECT spends 2; two independent metabolic ticks exhaust the
body before EAT can be attempted, even in a favorable-food world. At
energy=5 and no intervening ticks, the ordinary paid COLLECT and EAT
actions remain possible. This is an execution falsifier for a fixed
toy-world deadline, not yet a runtime planner, a food oracle, a
multi-strategy comparison or proof of autonomous survival.


## Audited deadline visibility at actual paid decisions

The prototype's read-only `decision_evidence()` now reports a prospective
COLLECT-then-EAT feasibility assessment from each verified predecision
WorldBody capture. The physical delay used is the existing
`WORLD_COGNITIVE_PERIOD=2` ticks, not a fitted survival threshold. The
readout labels a delayed rescue infeasible when metabolism would exhaust
energy before the second action, even when the hidden food happens to be
nutritious. No hidden food impulse enters the assessment, and this
diagnostic does not enter subjective valuations, change motor choice, or
spend extra UC. It is **not yet a plan-selection policy**.

The next behavioral experiment must explicitly test whether using this
deadline assessment in paid action selection improves survival against
the observational and reflex-only controls, without falsely promising
that food with unknown payoff is safe.


## Opt-in paid deadline policy, source-specific negative control

A new **fresh-genesis only** `deadline_aware=True` experiment suppresses
positive COLLECT valuation when its known action cost plus the fixed two
metabolic ticks make a later EAT attempt physically impossible. It still
pays for every Competition candidate and normal Action Control, and the
single WorldBody owner replay recomputes the suppressed score/evidence.
This policy is **mutually exclusive** with the older optional last-resort
priority until composition can be separately falsified.

The matched toy-world first decision at energy=4 changes from COLLECT to
DRINK, with identical paid UC and identical immediate energy loss. DRINK
does not restore energy. This is **not a survival improvement**: it proves
only that the decision policy can avoid one futile *plan*, while a viable
replacement survival strategy is still absent. At energy=10 the normal
COLLECT action remains. The historic trials leave the new switch off.
An extra experimental policy is not permission to reactivate I2, declare
M11 authentication, predict hidden food, or claim learned planning.


## Opt-in combined emergency/deadline policy (new experimental cohort)

A fresh I2-only genesis may now enable both `last_resort_exploration`
and `deadline_aware`. The same **paid candidate batch** first assigns
zero positive value to COLLECT when its necessary two-tick delay would
exhaust the body before EAT. It then gives an available EAT the
categorical last-resort priority only if it would otherwise lose the
competition and its source-verified emergency conditions hold. When
EAT already wins, no synthetic priority is invented. Action Control can
still veto; no hidden food payoff is consulted. The single-owner audit
recomputes both value transformations and checks distinct evidence
markers. Older control policies remain opt-out at genesis.

The matched bounded examples intentionally retain the unfavorable case.
At initial energy=4 with no inventory, COLLECT is not a timely rescue:
the composed policy picks DRINK, which **also does not restore energy**.
With initial energy=8 and already collected inventory, physical time
can lower energy to 4; the composed policy attempts EAT, which restores
energy in the stable world but can cause terminal energy in the adverse
world. This is not evidence of generalized survival benefit, a learned
planner or reliable toxic-food detection. It is the smallest practical
behavioral composition and is separately falsifiable.

## Four-policy exploratory ablation after #841

`src/i2/runtime/four_policy_survival_ablation.py` separately initializes
observational, last-resort-only, deadline-only and combined policies for
the same stable, adverse and hidden-restoration world schedules. It
collects their actual audited paid choices, physical ticks, food contacts,
UC cost, death/censoring, and separately marked priority/feasibility
events. All outcomes are **descriptive single-run model evidence**.
Changing actions changes experienced evidence and future state; unequal
exposure must not be summarized as a causal fitness improvement.
Historic source-locked probes are not altered. No hidden world information
is provided to any individual's decisions. This is a bounded science
probe of integration, not proof of natural autonomous learning.


## Four-policy contrast semantics (post-#842)

The exploratory report now nests each environment's four audited arms
under `arms` and reports `contrasts_vs_observational` for last-resort,
deadline and combined policies. A contrast identifies the first observed
action or tick divergence, differing exposure lengths, modeled death ticks
and censoring. It only calculates an end-energy difference when **both
subjects remain nonterminal through the same observed physical tick**.
The first diverging action is a descriptive intervention marker, not proof
of independent causal survival advantage; subsequent experiences can differ
and no independent statistical replication has been conducted. No policy,
world clock, UC, hidden outcome or source-locked historical battery changes.


## Scarcity-specific ablation: 8 and 16 initial energy

The same four-policy, three-environment exploratory comparison now
accepts an explicitly validated `initial_energy` parameter. Separate
fresh-genesis cohorts at 8 and 16 units stress survival decisions near
the known 4-unit danger threshold. These cohorts are declared in the
focused test source before inspecting their CI results, and CI publishes
the full readout for manual scientific review. Neither policy selection,
UC, hidden food payoff, world cadence nor the original default 40-energy
cohort is changed. No result is interpreted as an independent causal
fitness benefit: censoring, death and unequal exposure remain explicit.


## Observed scarcity result, fixed exploratory cohort (2 November 2026)

The GitHub CI result for #844 (Python 3.11, run 41365702859)
contains 24 fresh-life executions: two initial-energy levels (8, 16),
three world regimes and four policies. The readout is source-bound
to the fixed in-process WorldBody, **not** an independent scientific
replication. Its actual negative observations:

| Initial energy | World | Observed outcome across all four policies |
|---|---|---|
| 8 | adverse | terminal at physical tick 4; energy 0 |
| 8 | restoration | terminal at physical tick 4; energy 0 |
| 8 | stable | terminal at physical tick 8; energy 0 |
| 16 | adverse | terminal at physical tick 4; energy 0 |
| 16 | restoration | terminal at physical tick 4; energy 0 |
| 16 | stable | nonterminal through tick 16; energy 8 (right-censored) |

At initial energy 8 in stable food, deadline and combined policies
choose DRINK rather than COLLECT at tick 6; *all* four policies still
die at tick 8. The 16-energy stable policy traces have no action
divergence. **No last-resort valuation increase was exercised** in
any of these 24 traces. Thus the study supplies no evidence that the
combined policy extends survival and insufficient behavioral exposure
to evaluate emergency re-exploration. The restoration world kills
before its hidden recovery can be personally encountered.

The correct next targeted behavioral falsifier is a **reachable**
personally harmful meal followed by a changed hidden regime and
critical energy, comparing the same paid ordinary choice against
survival re-exposure; it must keep pre-choice observations and
motor/UC authority aligned. Do not adjust energy thresholds,
hidden switching times or priors post hoc to manufacture success,
and do not count censoring as survival success. An explicitly
new protocol must be distinguished from the original #844 cohort.


## Separate personally experienced aversion / hidden-restoration experiment

The new `restoration_reexposure_composition.py` uses the original frozen
40-energy restoration and persistently adverse scripted physics, with
three independently initialized paid policies: observational, last-resort
and combined. It reports food contacts after physical tick 7, the earlier
personally observed food results available at each contact, delayed
availability of the new result, terminal/censor outcomes, UC debits and
the first matched-prechoice policy divergence. The next outcome is never
a subjective prior: the research-only report reads it after the paid
physical action. Neither environment is selected by the individual.

This study is deliberately separate from the 8/16-energy negative
scarcity cohorts and the original locked blind-identifiability study.
One positive restored contact cannot prove a general survival advantage,
especially if it causes different later experiences. A continuously
toxic food exposure remains a mandatory adverse falsifier; no tuned
threshold or injected hidden-world cue is permitted.


## Observed re-exposure is not yet learned recovery (#846 follow-up)

Actual CI readout of the separately specified #846 protocol: with a
personally experienced EAT net of -10, the learned observational policy
does not re-expose and reaches modeled terminal energy at physical tick
16. The reflex-only and reflex+deadline policies each independently
choose EAT at the eighth paid decision, with prechoice observations
matched to observational control. In hidden restoration the net is +4
and the body remains nonterminal with energy 6 at tick 16 (right-
censored); under persistent adversity the net is -2 and the body dies
at tick 16. Each intervention spent 38 UC; combined and reflex-only
have equal contacts and endpoints. No independent added deadline benefit
is observed.

Critically, that food contact occurs in the **last available paid
cognitive window**. The new positive outcome is **not personally
available in a later capture** in this experiment. Consequently, this
supports risky *re-exposure under survival pressure*, not successful
updating from the restored reward or sustained adaptive survival.
Do not silently extend the locked #846 results, raise MAX_STEPS or
reclassify a right-censored individual as having survived indefinitely.
A future **new** source-declared protocol with a longer, bounded,
adequately funded cognition horizon must observe an additional paid
decision *after* a successful recontact, assess the prior -10 and newly
observed +4 together and retain the persistently adverse control.


## Separate ten-window postcontact observation, not a historical edit

An explicitly declared `extended_postcontact_study=True` fresh genesis
permits exactly ten input impulse phases; the original eight-decision
SCENARIOS remain unchanged and a longer sequence without this flag
is refused. The new test duplicates each world's final external food
payoff for two further phases **only in the new experiment**, with the
same hidden regime and no new subjective cue. The ninth paid decision
can now encounter the positive restored-food outcome from the eighth
chosen EAT through the ordinary next capture. The persistently toxic
control must retain modeled terminal status at tick 16 before a ninth
decision can occur. This extends observation and tests memory access,
not the individual's independent ability to learn the recovered payoff,
predict it before contact, or improve life expectancy. The separate
new cohort must not be combined numerically with #846's locked
eight-window study. No real M11 authentication or I2 activation.


## Post-contact paid action and valuation falsifier

The fresh ten-phase study now asserts that the ninth decision consumes the
actual newly observed EAT net +4 as *past-only* evidence, yielding the
existing comparator's EAT score of 9 (net +4 plus fixed offset 5), with
an ordinary paid EAT admission. This differs from the eighth decision's
emergency priority over a personally observed -10. No fabricated
restoration knowledge was available to the eighth decision. An EAT that
already wins at ninth decision receives no extra emergency boost.

This test distinguishes **new evidence availability**, **value updating**,
and **subsequent paid action** within one bounded toy-world life. It
cannot establish generalization, robust planning or statistical
survival advantage from one fixed sequence. The persistently adverse
control stays terminal before ninth capture, and the original 8-phase
protocol remains separate and immutable.


## Ninth-decision memory ablation: value change versus motor choice

A separate extended restoration control compares learning-enabled and
fixed-prior fresh lives with the same hidden food schedule and reflex
policy. The learned ninth-decision food valuation uses personally
experienced net +4 (score 9), whereas the fixed-prior comparator
retains food score 4. Both can still select EAT, so one chosen action
does not itself prove that the new memory changed behavior. Their
earlier food exposures and resulting body states can differ, therefore
the comparison is *not* a matched-prechoice causal estimate. If the
software test confirms both actions are identical, record a **score
update without demonstrated choice dependence**. Do not claim that
relearning is behaviorally necessary on this evidence alone, and do
not adjust existing priors to manufacture a difference.
