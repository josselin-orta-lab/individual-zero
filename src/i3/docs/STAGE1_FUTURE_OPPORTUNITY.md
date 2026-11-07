# Stage 1 prerequisite: personal recurrence of future opportunities

Issue #1061. Baseline:
`0ffd4455e4610c674499e2ec1b1b6eca8d04f8f8`.

**SOFTWARE SUBSTRATE ONLY. NOT A LIVE POLICY. NO STUDY AUTHORIZATION.**

## Why this prerequisite exists

The Stage-1 information kernels can already compute genuine epistemic value.
The remaining decision-boundary evidence shows that value becomes useful only
when the individual can represent that a matching action opportunity may occur
again.

This is not permission to assume that the current source persists. #1099 showed
that without a future matching opportunity, immediate bodily observation alone
gave zero information across the tested states. #1101 and #1105 then showed
that water and carried-food information can remain sub-decisive even when the
information arithmetic and physical funding are intact.

The next prerequisite is therefore deliberately smaller than full Stage 3:
retain only personal evidence that a **generic perceived modality has recurred**.

## Representation

`modules/opportunity_recurrence.py::OpportunityRecurrenceMemory` is empty at
birth and recognizes two generic sensor classes:

- `water`;
- `token`.

It stores no token identifier. It also stores no relative/absolute position,
source identity, stock, schedule, world name, ecology family or hidden state.

The caller supplies post-perception booleans only. A future live integration
must derive those booleans from the individual's already perceived state, after
normal sensing/noise, never directly from World.

## Onsets rather than persistence

An opportunity occurrence is a modality **onset**:

```text
present now AND absent on the previous paid observation
```

Therefore a source that remains continuously visible for ten decisions creates
one onset, not ten recurrence observations.

If the modality disappears and later becomes perceived again, the new onset can
close one personal onset-to-onset gap.

This rule does not prove that the two onsets came from different physical
sources. It also does not assume that the current source remains available.
It measures only the individual's lived recurrence of a generic sensory
opportunity.

## Bounded empirical support

For each modality, retain only the latest three completed onset-to-onset gaps,
matching the Stage-1 bounded empirical-support convention.

For planning horizon `H`:

```text
p_future = count(retained gap <= H) / count(retained gaps)
```

There is deliberately:

- no Beta/Laplace smoothing;
- no 0.5 newborn recurrence prior;
- no substitution of zero for missing support.

With no completed personal recurrence gap the status is
`NO_PERSONAL_RECURRENCE_SUPPORT` and the probability is undefined.

The estimate is a bounded personal statistic, not a calibrated environmental
law.

## Costs

Each observed decision snapshot costs:

```text
1 cycle + 8 memory items
```

A recurrence estimate costs:

```text
1 cycle + (2 + retained_gap_count) memory items
```

These are model-work allowances. A future runtime owner would still have to
settle them physically exactly once.

Failed funding does not advance the chronology or create an onset.

## Stage-1 composition boundary

This module does not add stochastic outcome leaves. A later Stage-1 kernel may
use its scalar supported recurrence estimate as an analytically marginalized
availability term, as long as the original two/three simulated outcome-branch
limit is preserved.

It does not:

- score exploration;
- choose an action;
- grant a future resource;
- assume current-source persistence;
- create a favorable unknown-effect prior;
- start Stage-2 compute selection;
- implement Stage-3 change detection, latent causes or attribute factorization.

## Falsifier for the next slice

Before any live policy, combine this recurrence estimate with an existing
Stage-1 information kernel in software only.

A useful result would require all of the following without tuning:

1. unsupported/insufficient recurrence remains unknown and cannot create a
   favorable score;
2. personally observed recurrence can make information more decision-relevant;
3. some states still decline the information-bearing trial;
4. complete cognition remains fundable and paid;
5. no extra stochastic leaves, hidden persistence or World data appear.

If recurrence support merely becomes another generic exploration bonus, or if
it cannot change any decision-boundary comparison, reject this prerequisite
rather than adding another local patch.
