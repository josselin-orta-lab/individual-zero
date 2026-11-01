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
