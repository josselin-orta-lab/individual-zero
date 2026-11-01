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
