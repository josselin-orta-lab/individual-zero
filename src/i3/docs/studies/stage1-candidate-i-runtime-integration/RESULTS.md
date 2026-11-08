# Candidate-I runnable multi-option integration: frozen S1 DEFECT

Protocol:
[STAGE1_CANDIDATE_I_RUNTIME_INTEGRATION.md](../../STAGE1_CANDIDATE_I_RUNTIME_INTEGRATION.md).

**SOFTWARE ONLY. NO 60/61 WORLD OPENED. NO RUNTIME ADOPTION.**

Frozen verdict:

`CANDIDATE_I_RUNTIME_INTEGRATION_DEFECT`

First implementation SHA:
`ada6ad054ec1ac68fad5eb031cadd3f63c3e3702`.

GitHub Actions:
`42493965599`.

Python 3.11 and 3.12 fail identically on the prospectively frozen S1
single-trial-reduction rule.

## Fatal S1 result

The protocol proposed the following multi-trial perceived relevance criterion:

1. build a with-information top set;
2. build a without-information top set;
3. require the two top sets to differ;
4. require a positive-information unsupported trial in the with-information
   top set.

The protocol also required that this rule reduce **state-for-state** to the
already exposed #1170 P80/F108 one-trial classifier.

It does not.

Across the **1,128** frozen one-trial states:

- P80: 480 states;
- F108: 648 states;
- disagreements: **700 / 1,128**.

### Disagreements by arm

| Path | omega | Mismatches |
| --- | ---: | ---: |
| P80 | -1.0 | 16 |
| P80 | -0.5 | 36 |
| P80 | 0.0 | 40 |
| P80 | 0.25 | 48 |
| P80 | 0.5 | 56 |
| P80 | 1.0 | 60 |
| F108 | -1.0 | 0 |
| F108 | -0.5 | 56 |
| F108 | 0.0 | 84 |
| F108 | 0.25 | 100 |
| F108 | 0.5 | 96 |
| F108 | 1.0 | 108 |

Direction:

- **696** states: new rule FALSE, frozen #1170 TRUE;
- **4** states: new rule TRUE, frozen #1170 FALSE.

The four false positives are all F108 at:

- omega = 0.25;
- energy = 35;
- food = 40;
- integrity = 20;
- horizons 4, 6, 8 and 12.

## Why the rules differ

#1170's frozen one-trial classifier is:

```text
trial_informed_value > trial_no_trial_value
AND
trial_informed_value > every ordinary offered option
```

within the frozen 1e-12 strict margin.

That asks whether the **unknown trial itself is strictly worth taking** relative
to both not taking it and the available alternatives.

The failed runtime rule asked a different question:

> does information change the top set relative to the frozen trial score?

These are not equivalent.

A trial may already be the best offered option under its frozen expectation,
then gain information value without changing the top set. #1170 can classify
that trial as relevant; the proposed top-change rule rejects it. This explains
the dominant 696 false negatives.

Conversely, a trial may become the best actually offered option while still
failing to beat its own internal no-trial comparator. The proposed top-change
rule can accept it while #1170 rejects it. The four F108 false positives are
examples of that category.

The defect therefore exposes a semantic conflation:

- **direct first contact:** whether performing the unknown trial is strictly
  advantageous;
- **post-contact information:** whether extra information changes the final
  decision top.

The first is the #1170 rule. The second is the #1163 Candidate-H post-contact
rule. They are different questions and must not be silently unified.

## Structural checks that did pass

The failure is not a general runtime/plumbing collapse.

On the same SHA:

- extracted P1.3 Competition/ActionControl finalizer matched the exact legacy
  block on the frozen cap panel;
- two-trial enumeration permutation invariance passed;
- direct first-contact projector restoration passed;
- same-genome omega override plumbing passed;
- personally supported-water post-contact matched Candidate-H motor/work and
  observer output;
- Candidate-I remained opt-in and reference did not construct it.

The existing P2 DEVELOPMENT-0 runtime smoke also successfully reached both
`energy_receipt` and `revision_receipt`. Its test then raised a harness
`KeyError` by incorrectly expecting `energy_receipt` to expose a
`scientific_verdict` field. That is a verifier assertion defect, not evidence
for or against Candidate-I. S11 is not interpreted because S1 already failed.

## Interpretation

This is a **protocol/runtime-generalization defect**, not an organism result and
not a rejection of the #1174 Candidate-I software architecture.

No K80/P80/F108 result changes. Candidate-I I0-I9 remains a PASS.

The failed runtime implementation is not merged. Development 60/61 remains
unallocated and unopened.

The next semantics must be frozen in a new protocol before implementation.
