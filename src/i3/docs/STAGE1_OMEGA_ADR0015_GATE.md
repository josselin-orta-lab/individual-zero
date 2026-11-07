# Stage 1 omega: prospective ADR-0015 gate design

Issue #1061. Design baseline:
`077d6b92fd19eaa6350ec79c370f44820f8dffb5` (#1129).

**DESIGN AND ARITHMETIC ONLY. EXECUTION IS NOT AUTHORIZED BY THIS FILE.**

## Executed result

This prospective design was later executed in full under immutable source
`ca506554e67eddde08e71ba6872df3b50f3ea4be` and run `42416437088`.

Final result: [studies/stage1-omega-adr0015/RESULTS.md](studies/stage1-omega-adr0015/RESULTS.md).

Verdict: **`FAIL_FROZEN_STAGE1_OMEGA_GATE`**. G1-G5 fail; G6 custody passes.
This paragraph records the later result only and does not alter any frozen
design clause below.


No selection, validation or reserve world is opened by this slice.

## Question

Does a lineage-selected generic first-contact expectation `omega` improve the
reference-preserving Stage-1 candidate without becoming a hand-chosen water
parameter?

The gate separates three questions:

1. can the complete Candidate-F + information architecture remain survival
   non-inferior to P1.3?
2. does selection by persistence actually favor upward omega?
3. do the selected genomes perform better with their inherited omega than the
   exact same common genes with `omega := 0`?

Revision in the existing F0 depletion stratum is a co-primary Stage-1 endpoint.

## Frozen sources and policies

Design baseline:
`077d6b92fd19eaa6350ec79c370f44820f8dffb5`.

Reference policy:

`reference`.

Candidate policy:

`genomic_omega_frontier_information_v1`.

Both are in the same source tree and use current genome v4. The reference
validates the full v4 genome but does not read omega.

The candidate uses Candidate-F projection and genome-v4 omega only before
personal drink experience. Personal post-contact history is omega-free.

Any execution protocol must freeze the exact source SHA again before the first
selection life and reject any source drift.

## Populations and candidate pools

Use the already-designed Stage-0 independent-pool contract:

- populations: **8**;
- G0 candidates per population: **K=40**;
- selected per architecture/population: **m=5**;
- horizon: **400**;
- founder seed:
  `2_000_000 + population*40 + candidate_slot`.

These are eight independently generated G0 pools, not the four historical P3
populations and not evolved lineages.

Generation-zero omega is the symmetric uniform v4 draw. Because omega is the
last gene, reference and candidate receive identical values for all 30 common
genes at the same founder seed.

No founder is replaced after seeing an outcome.

## Selection worlds

Reuse the still-unopened Stage-0 P2 `selection` allocation exactly:

- indices **72..119**;
- world seeds **10072..10119**;
- six worlds per population;
- stable, depletion, pulse, two repeats each.

The identical candidate/world/life opportunity is used by both architecture
arms.

Each architecture ranks its own 40 candidates by ADR-0015 only:

1. censored lives descending;
2. total lived steps descending;
3. founder seed ascending.

A physical death with **zero lived steps is a valid persistence outcome** and
remains in the complete ranking with zero steps. Censoring still requires the
full 400-step horizon. A crash, missing receipt or malformed terminal state is
not a death and still blocks selection. This pre-exposure clarification avoids
inheriting the historical Stage-0 helper's older steps>=1 arithmetic boundary.

No omega value, information score, revision status or validation result enters
selection.

Incomplete/crashed selection receipts stop the experiment. They are never
discarded or counted as deaths.

## Validation worlds

Reuse the still-unopened Stage-0 P2 `validation` allocation exactly:

- indices **120..167**;
- world seeds **30120..30167**;
- six worlds per population;
- stable, depletion, pulse, two repeats each.

The original P4 reserve `1200000..1200199` remains sealed.

Three validation arms are evaluated:

1. independently selected P1.3 reference genomes;
2. independently selected candidate genomes with inherited omega;
3. **the same five candidate-selected genomes**, with all 30 common genes
   unchanged and only omega forced to 0 before birth.

The omega-zero arm is never independently selected and never enters reranking.

Its purpose is mechanism attribution, not another architecture search.

## Life pairing

Within a declared validation world, use the same world and life seed across
reference, candidate and omega-zero arms.

Reference and candidate may have different selected founder seeds because
ADR-0015 selects each architecture independently.

Candidate versus omega-zero is stricter: each founder seed and all 30 common
genes are identical.

The genome digest of every receipt must match the declared arm-specific genome.

## Survival non-inferiority

There are:

`8 populations * 2 worlds * 5 selected genomes = 80 lives`

per family and arm.

Historical G2e used a 3% family non-inferiority allowance. To avoid creating a
new outcome-fitted margin, this design reuses that rate prospectively.

The largest integer not exceeding 3% of 80 is **2**.

### G1

For each of stable, depletion and pulse separately:

`candidate survivors >= reference survivors - 2`.

A gain in one family cannot compensate a deficit larger than two in another.

Selected-survivor differences per validation world and exact paired sign tests
are also reported, as required by ADR-0015, but are not mislabelled as a
non-inferiority test.

## Complete revision rank

The revision endpoint is the already-defined **R-depletion-v1** personal
resource-reacquisition clock.

A conditional median among successful revisions is not acceptable as the gate:
architectures can change who survives or ever reaches the exposure.

Every depletion life therefore receives a complete rank:

```text
if status == REACQUIRED:
    rank = latency_from_available_steps
else:
    rank = 401
```

401 is horizon + 1 and cannot be achieved by a successful within-horizon
reacquisition.

Therefore:

- NO_EXPOSURE remains in analysis;
- EXPOSED_NO_REACQUISITION remains in analysis;
- death before reacquisition remains in analysis;
- successful reacquisition on a fatal action retains its observed latency, while
  survival is judged separately by G1.

Conditional successful latencies remain descriptive.

### G2

For each population, compare the mean complete revision rank over its ten
depletion validation lives.

Pass requires:

- candidate rank lower than reference in at least **7/8 populations**;
- candidate pooled mean rank strictly lower than reference pooled mean;
- at least one actual candidate `REACQUIRED` life.

The 7/8 threshold is a directional gate, not a claim of conventional
significance. The exact sign-test result is reported.

## Does selection actually favor omega?

For every population:

```text
shift_p =
    mean(omega of 5 candidate-selected genomes)
    - mean(omega of all 40 candidate-pool genomes)
```

This controls the finite realized G0 omega mean rather than pretending each
40-genome pool is exactly centred at zero.

The omega values of reference-selected genomes are also reported as a negative
control. Reference cognition never reads omega.

### G3

Pass requires:

- positive candidate selection shift in at least **7/8 populations**;
- pooled selected-candidate mean omega > pooled 40-genome-pool mean;
- pooled selected-candidate mean omega > 0.

Thus a merely "less negative" selected set cannot establish the intended
optimistic first-contact disposition.

## Equal-genome omega-zero ablation

For every population, compare total validation survival of the five selected
candidate genomes with their exact omega-zero copies.

### G4

Pass requires:

- actual-omega candidate survival > omega-zero survival in at least
  **7/8 populations**;
- pooled actual-omega survival > pooled omega-zero survival.

Again the exact sign test is reported and the 7/8 directional requirement is
not called significance.

## Ecology-specific calibration guard

A generic innate expectation should not pass solely because one ecology happens
to match it.

For each F0 family, aggregate actual-omega candidate survival minus the
omega-zero copies.

### G5

Positive survival difference is required in at least **2 of 3 families**.

This does not establish whole-family transfer. F0 remains F0. It only rejects a
one-family calibration as the Stage-1 mechanism result.

## Custody floors

### G6

All must pass:

- exact source lock;
- exact P2 world/source lock;
- full Competition observer valid;
- zero cognitive shortfall;
- exact replay of the predeclared rank-0 selected genome on every validation
  world in every arm.

A crash, missing sidecar or inconsistent evidence is an engineering failure and
blocks the gate. It is never converted to mortality.

Depletion validation lives retain the full original trace and resource sidecar
needed by `stage0_revision.revision_receipt`.

## Mandatory descriptive reporting

Regardless of verdict, publish:

- all K=40 selection persistence outcomes;
- selected genomes and all omega values;
- reference-selected omega as a negative control;
- G0 candidate-pool survival/evolvability on selection worlds;
- reference-search probe survival, clearly labelled descriptive and not
  cost-matched;
- selected validation survival per world/family/population;
- omega-zero outcomes at equal common genes;
- all revision statuses and conditional successful latencies;
- actual energy/vigilance/lived time;
- inactive fraction;
- first-contact/post-contact omega counters;
- exact paired-world and population sign tests;
- all crashes/engineering failures.

No failed or inconvenient population may be removed.

## Compute envelope

Main selection:

- 8 * 40 * 6 * 2 architecture arms = **3840 lives**.

Main validation:

- 8 * 5 * 6 * 3 arms = **720 lives**.

Rank-0 exact validation replays:

- 8 * 6 * 3 = **144 lives**.

Maximum:

- **4704 executions**;
- **1,881,600 physical life steps** at horizon 400.

This excludes software-only verification but includes the exact validation
replays.

The eventual execution workflow may partition work by population/arm for
engineering reasons, but may not stop early because a rule appears won or lost.

## Frozen decision

The architecture may pass this gate only if **G1 through G6 all pass**.

A pass would support the narrow claim that:

- selection on persistence favors a positive generic first-contact expectation;
- inherited omega contributes to survival beyond the same selected genomes with
  omega removed;
- the complete candidate remains survival non-inferior in every F0 stratum;
- behavioral reacquisition improves under the complete-rank revision endpoint.

It would still **not** establish:

- a general I3 scientific GO;
- Stage-2 value of computation;
- food information completeness;
- F1-F5 generalization;
- stable acquired individuality;
- a full evolving lineage result;
- registration or activation.

A failure is retained. Do not retune omega bounds, the 3% margin, K/m,
worlds, families or revision scoring after exposure.
