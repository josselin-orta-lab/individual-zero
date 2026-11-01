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

## Paid Action Control survival constraint (increment after #829)

The isolated world now supplies the exact current owner-derived
`LocalEnergySurvivalReflex` to its **existing paid Action Control safety
port**, never directly to Competition valuation. For a candidate EAT with
energy reserve <= 4, the safety source emits a positive veto referenced to
the exact observed energy evidence; the already-paid control returns
`VETOED`, and no internal eating admission/effect is created. No substitute
action is picked, no hidden reward predicted, and metabolism continues.

The same owner replay recomputes the required veto from *predecision*
committed energy and rejects a missing/misbound veto. This is a deliberately
conservative, mechanistic restriction: it may prevent a beneficial recovery
meal under critical scarcity. That adverse possibility is a required
scientific falsifier, not something to tune away. PREEMPT/CONSTRAIN on
other actions remains informational in this limited increment. This is not
an authenticated M11 witness, a real physiological reflex, or full
reappraisal/need integration. The historical blind restoration and
seven-case batteries remain unchanged.

Focused software regression:
`PYTHONPATH=src python -m unittest discover -s tests/i2 -p 'test_paid_reflex_veto.py' -v`.
