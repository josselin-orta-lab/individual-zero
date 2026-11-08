# Stage 1 Candidate-I: runnable multi-option integration v2

**PROSPECTIVELY FROZEN SUCCESSOR SOFTWARE GATE. NO FRESH DEVELOPMENT WORLD.
NO RUNTIME ADOPTION.**

This protocol succeeds the failed
[Candidate-I runtime integration](STAGE1_CANDIDATE_I_RUNTIME_INTEGRATION.md).
The failed protocol and its
[result](studies/stage1-candidate-i-runtime-integration/RESULTS.md) remain
immutable evidence.

The only semantic change is the directly perceived multi-trial relevance rule.
It is chosen because it is the minimal symmetric extension that reduces exactly
to the already frozen #1170 one-trial rule.

No omega arm, RMS scale, body grid, horizon, fallback rule, post-contact rule or
cost model is changed.

## Frozen distinction

Candidate-I now keeps three explicitly different decision questions.

### A. Imagined first contact

Unchanged from #1170/#1174:

- personal recurrence support is required;
- the water future-opportunity kernel is used;
- relevance is the frozen strict K80 criterion:
  `TRIAL` selected, positive information value and positive trial advantage.

### B. Directly perceived unsupported first contact

This is an **action-trial advantage** question:

> is one unknown resource trial strictly better than not performing that same
> trial and strictly better than every other option actually offered now?

It is not a top-set-change question.

### C. Post-contact information

Unchanged #1163 Candidate-H:

> does the extra information change the final decision top?

Omega and the inherited first-contact prior remain absent post-contact.

These meanings must remain separate in code and receipts.

## Direct multi-trial score matrix

Use the same complete option set, same Candidate-F forecast body, same paid RMS
prior, same per-trial STOP/repeat subjective continuations and same common work
ceiling already frozen in v1.

For each unsupported direct resource trial `t`, retain:

- `trial_no_trial_value[t]`;
- `trial_frozen_value[t]`;
- `trial_informed_value[t]`;
- `information_value[t]`;
- `trial_advantage[t]`;
- shared-prior receipt.

For each nontrial option, retain its Candidate-F score under the same forecast
body and projector.

The full with-information map contains every actual option:

- nontrial option -> Candidate-F ordinary score;
- unsupported trial -> its `trial_informed_value`.

The without-information map may also be reported using
`trial_frozen_value`, but **it is diagnostic only** and has no relevance
authority in v2.

## Frozen direct relevance rule

Let `T` be all simultaneously offered unsupported direct resource trials.
Let `S_with(o)` be the with-information score of every actual offered option.

A direct first-contact decision is RELEVANT iff there exists a trial
`t in T` satisfying **both**:

### V2-R1 — own no-trial advantage

```text
trial_informed_value[t] > trial_no_trial_value[t] + 1e-12
```

### V2-R2 — strict winner among every other offered option

For every actual offered option `o != t`:

```text
trial_informed_value[t] > S_with(o) + 1e-12
```

Because R2 is strict, at most one trial can satisfy it. No token order,
resource type, first-seen order or RNG tie-break can create relevance.

If no trial satisfies R1+R2, the direct first-contact result is FALLBACK.

No explicit positive-information-value condition is added because #1170 did
not contain one. Adding it would itself break the frozen one-trial identity.

## Exact one-trial reduction

With exactly one unsupported trial, V2-R1+R2 becomes exactly #1170:

```text
trial_informed_value > trial_no_trial_value
AND
trial_informed_value > every ordinary offered option
```

The exhaustive 1,128-state P80/F108 identity test is mandatory and must report
**zero mismatches**.

The failed v1 top-set-change classifier must remain available only as a
read-only diagnostic in the comparison report. It must never influence the v2
decision.

## Final authority

Unchanged from v1.

### RELEVANT direct first contact

The complete with-information score map enters the shared P1.3
Competition/ActionControl finalizer.

The strict-winning trial is not forced. If ActionControl rejects it, the
remaining scored options are attempted in the same ranked order and under the
same controller semantics as P1.3.

### FALLBACK

All Stage-A work stays physically paid. Restore detached probe/perception state,
then execute exactly one real final perception/decision from the post-probe
body using:

`score_addend_mode="discard_both_bonus_terms"`.

### PROBE_UNFUNDED

No final decision. Emit the repaired
`NO_FUNDED_RELEVANCE_PROBE` composite receipt with one of the two frozen
nested incomplete funding statuses.

## Successor software rules

All v1 S0-S11 boundaries remain, except the v1 perceived relevance definition
is replaced by V2-R1+R2 above.

### S0 — source custody

Required immutable predecessors:

- #1170 shared prior PASS;
- #1174 Candidate-I I0-I9 PASS;
- #1172 composite reducer R0-R6 PASS;
- failed v1 runtime result present and unchanged;
- #1163 post-contact PASS;
- #1164 unified Candidate-H PASS.

### S1 — exact one-trial reduction

Across every P80/F108 state and omega arm:

- relevance mismatch count = **0 / 1,128**;
- trial values, ordinary scores, prior receipt, work ceiling, actual work and
  body settlement remain exactly #1170;
- report the v1 top-set-change disagreement count separately as historical
  diagnostic, expected 700 on the first failed source but not an acceptance
  target for future numerical drift.

### S2 — complete option-set panel

Same v1 cases:

1. no trial;
2. water only;
3. one unknown carried food;
4. water + one unknown food;
5. two unknown foods;
6. water + two unknown foods;
7. one supported + one unsupported resource;
8. all resource actions supported.

For multi-trial fixtures, report which trial, if any, satisfies R1+R2 and why
all other trials fail.

### S3 — permutation / renaming

Unchanged and strict:

- inventory permutation;
- external token renaming;
- consistent internal-token renaming;
- unsupported-trial enumeration permutation.

After semantic renaming, trial values, strict winner identity, relevance,
scores, work, Competition/ActionControl result and body must match.

### S4 — common geometry/accounting

Unchanged:

- one complete quoted ceiling;
- one forecast body;
- Candidate-F geometry for every Stage-A score;
- no mixed reference/Candidate-F Competition;
- no early-stop scoring.

### S5 — shared finalizer identity

Unchanged. Any extracted finalizer must remain exact legacy P1.3 in result,
RNG, accumulators, control attempts, intention, work and persistent state.

### S6 — fallback custody

Unchanged #1174 addend-free fallback identity, plus:

- detached Stage-A perception state is restored before fallback;
- exactly one real perception is retained by the final decision;
- full Stage-A work, including base processing and recurrence read, is reported
  explicitly and reconciles with the cumulative decision work.

### S7 — post-contact parity

Unchanged #1163/#1164, omega-free.

### S8 — omega boundary / same-genome ablation

Unchanged. Native genome omega only first contact; software `omega := 0`
ablation changes no other state.

### S9 — reducer custody

Unchanged repaired composite funding semantics.

### S10 — learning/state authority

Unchanged. Counterfactual scoring cannot create learning authority. On
FALLBACK/UNFUNDED, detached perception/probe state is restored. On RELEVANT,
the retained perception is the one real first-person perception for that
decision.

### S11 — already-exposed runtime smoke

Unchanged: P2 DEVELOPMENT index 0 only, short horizon, not scientific evidence.

The smoke assertion must use the actual schemas of `energy_receipt` and
`revision_receipt`; no field may be invented merely for the test.

## Frozen verdict

All S0-S11 PASS:

`CANDIDATE_I_RUNTIME_INTEGRATION_V2_PASS`

Any failure:

`CANDIDATE_I_RUNTIME_INTEGRATION_V2_DEFECT`

Repair implementation defects only. Any further semantic change requires
another frozen successor protocol.

## After PASS only

Only after a v2 PASS may a fresh DEVELOPMENT 60/61 protocol be proposed.

This document still does not allocate or open 60/61.

A later live protocol should retain at least:

- P1.3 reference;
- Candidate-H control;
- Candidate-I native omega;
- same-genome Candidate-I omega=0 ablation.

P1.3 remains the scientific reference. I3 remains unregistered. Selection,
validation, reserve and Stage 2 remain blocked.
