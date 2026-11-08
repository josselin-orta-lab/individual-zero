# Stage 1 Candidate-G: fresh 56/57 development pilot

Issue #1061. Source baseline before protocol:
`117794e56e812c311ab545d1c8a0d26ce71ad0c2` (#1156).

**PROSPECTIVE DEVELOPMENT PILOT ONLY. NOT A STAGE-1 SCIENTIFIC GATE.**

This protocol is frozen before any I3 development world at indices 56/57 is
opened. The protocol commit contains no World execution hook.

## Why

#1156 passed the bounded software integration gate for
`personal_recurrence_candidate_g_v1`:

- personal recurrence can activate the canonical Candidate-F projector without
  reading genomic omega;
- unsupported first contact remains on the P1.3 reference projector;
- supported first contact and post-contact decisions use one commensurate
  Candidate-F projector for every option score in that decision;
- persistent/default mode returns to P1.3 reference after every exit;
- the #1146 kernel reproduces the canonical #1155 set: 24 selected, 0 water,
  24 other, 40 declines, mean 470.05 simulated steps/state.

That is software capacity only. The next question is whether **intermittent,
personally supported activation** is physically cheaper in lived operation than
the rejected Candidate-F architecture whose projector is continuously active.

## Fresh allocation frozen before exposure

P2 development spans indices 0..99 / world seeds 2000..2099.

Known Stage-1 development exposure before this freeze ends at indices 54/55.
Repository collision searches found no I3 study allocation for development
indices **56/57** or P2 world seeds **2056/2057**.

Use exactly:

- F0 ecologies: `stable`, `depletion`, `pulse`;
- development indices: **56, 57**;
- P2 world seeds: **2056, 2057**;
- current v4 G0 genome seeds: **901, 902**;
- horizon: **400**;
- policy arms in exact order:
  1. `reference`;
  2. `personal_recurrence_candidate_g_v1`;
  3. `genomic_omega_frontier_information_v1`.

For zero-based family ordinal `f`, index ordinal `w` and genome ordinal `g`:

`life_seed = 7_460_000 + 1000*f + 10*w + g`.

All three arms in a block share family, world, genome, life seed and horizon.

Total if later executed: **12 matched blocks / 36 lives / at most 14,400
physical steps**.

The G0 genotypes and repeated F0 blocks are engineering fixtures, not independent
populations. No population inference is allowed.

No selection, validation or reserve condition is opened. The P4 reserve remains
sealed.

Canonical plan SHA-256:

`5837c98a9f94b10255e87526a0d4fa4718db09f3a9638cba3f9ff591246ba798`.

Fingerprint note: the initial protocol commit recorded a pre-runner draft
fingerprint. This value is the canonical digest of the machine-readable plan
implemented after that freeze. The correction occurred before any world import
or life exposure and changes no allocation, arm, seed, horizon, criterion or
interpretation rule. Runtime/source locking remains a separate exact-SHA guard.

## Arms

### Reference

Ordinary P1.3, unchanged.

### Candidate-G

`personal_recurrence_candidate_g_v1` from #1156.

The persistent/default projection is P1.3 reference. Candidate-F projection is
used only for a decision with a personally supported information path. First
contact uses paid personal recurrence and `omega=0`; post contact uses paid
personal actionable belief. No inherited recurrence and no genomic omega read.

### Candidate-F cost anchor

`genomic_omega_frontier_information_v1`, unchanged from the rejected frozen
omega architecture.

This arm is included only as a same-opportunity **realized cost/funding anchor**.
It is not retuned and cannot be rescued by this pilot. Differences from
Candidate-G include policy as well as activation frequency, so this is not a
causal mediation estimate.

## Primary engineering question

Does decision-local Candidate-F projection remain genuinely intermittent and
reduce realized cognitive collapse relative to the same-world Candidate-F cost
anchor?

The candidate continuation rule is met only if all are true:

1. at least one Candidate-G decision is `INFORMATION_ACTIVE`;
2. at least one Candidate-G decision remains reference-only;
3. pooled Candidate-G paid **energy per lived step** is strictly below the
   Candidate-F cost anchor;
4. pooled Candidate-G paid **vigilance per lived step** is strictly below the
   Candidate-F cost anchor;
5. pooled Candidate-G `NO_PROCESSING_BUDGET` fraction is strictly below the
   Candidate-F cost anchor.

These are engineering continuation criteria, not scientific acceptance rules.

Survival, death causes, resource acquisition and revision are **reported but do
not determine pass/fail**. No target number of survivors is declared.

## Required Candidate-G observables

For every complete Candidate-G life retain and reconcile:

- total decisions;
- `information_active_decisions`;
- `reference_only_decisions`;
- `recurrence_supported_decisions`;
- first-contact, post-contact and frontier-query counts;
- positive information options;
- opportunity-memory record count and final personal recurrence snapshot;
- branch-memory record count;
- every decision funding status;
- action/inactivity counts;
- actual paid energy/vigilance and per-lived-step rates;
- persistent final mode exactly `reference/chunk_end`;
- absence of `first_contact_omega`.

Trace-level diagnostics must agree with life summaries. Any mismatch is
`ENGINEERING_FAILURE_NOT_A_DEATH`.

## Descriptive secondary observations

For all arms report:

- censor/death and lived steps;
- death causes;
- actual cognitive energy/vigilance;
- `NO_PROCESSING_BUDGET`, `NO_FUNDED_SCORE`, `NO_FUNDED_MOTOR`;
- physical inactivity separately from chosen wait/sleep;
- move/drink/eat/collect counts;
- positive water/food uptake;
- first positive water uptake;
- Stage-0 energy/revision receipts.

Matched survival ordering is descriptive only.

## Source lock and custody

The execution source must preserve the implementation reviewed after this
protocol. Before importing runtime or world generation, the runner must reject:

- wrong exact Git SHA;
- wrong protocol digest;
- dirty I3 source;
- any post-implementation drift in `src/i3/modules`, `src/i3/runtime`,
  P2 ecology/world generation, Stage-0 energy/revision, or engine registry.

The runtime addition is opt-in only. I1 remains the active registry engine.

Every original life must be written as gzip before reduction. A crash, source
mismatch or custody mismatch is an engineering failure, never a death.

A later one-shot execution workflow, if authorized after the implementation PR
merges and exact-head Python 3.11/3.12 checks pass, must:

1. execute only once on fresh 56/57;
2. run the complete I3 software matrix first;
3. archive every available original, including adverse/null lives;
4. preserve exact source/protocol fingerprints;
5. remove the write-capable workflow before final integration.

No retry, replacement seed, horizon extension, favorable stopping, forced
resource, body reset, memory reset, clone or resurrection.

## Interpretation boundary

A continuation PASS means only that conditional activation is exercised and is
physically less destructive than the same-opportunity Candidate-F anchor on this
small development panel.

A FAIL means stop this live integration path and return to architecture/funding
analysis. It does not authorize tuning the activation rule on 56/57.

Even a favorable survival pattern does not authorize selection, validation,
reserve exposure, reference adoption or Stage 2.

P1.3 remains reference. I3 remains unregistered.
