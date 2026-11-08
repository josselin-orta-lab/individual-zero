# Candidate-H first-contact relevance-gated fallback: software PASS

Protocol:
[STAGE1_CANDIDATE_H_RELEVANCE_FALLBACK.md](../../STAGE1_CANDIDATE_H_RELEVANCE_FALLBACK.md).

**Software only. No World, no life, no runtime policy.**

Frozen verdict:

`CANDIDATE_H_FIRST_CONTACT_SOFTWARE_GATE_PASS`

Final confirmation: GitHub Actions run `42478647427`, Python 3.11 and 3.12,
full I3 software suite green; Python 3.11 navigation green.

## What Candidate-H tests

Candidate-H separates **support** from **relevance** at first contact:

1. pay the canonical Candidate-F first-contact information probe;
2. call the state RELEVANT only when the epistemic trial is strictly
   advantageous;
3. if relevant, keep the probe result and do no fallback;
4. otherwise, start from the body after the paid probe and pay a complete
   P1.3 four-plan decision basis.

No Candidate-F ordinary score is reused in fallback.

## Frozen gate

| Rule | Result |
| --- | --- |
| H0 canonical 24 relevant / 56 fallback / 40 declines, mean probe work 470.05 | PASS |
| H1 all 56 fallback states fully funded | **PASS, 56/56** |
| H2 fallback scores/top sets exactly equal same-body P1.3 | **PASS, max error 0** |
| H3 all 24 relevant states execute zero fallback work | PASS |
| H4 physical work/body accounting exactly reconciles | PASS |
| H5 no omega / World / life / motor / evidence authority | PASS |

## Policy restoration

#1161 identified 20 support-only states where Candidate-G's mere
support-triggered projector switch changed the ordinary top set.

Candidate-H restores all of them:

- prior #1161 drift states in fallback: **20**;
- returned to pre-probe P1.3 top set: **20/20**;
- still changed after paying the probe: **0**.

Across all 56 fallback states:

- top changes versus pre-probe P1.3: **0/56**;
- same-body fallback/reference score max error: **0.0**;
- unfunded fallback states: **0**.

On this frozen first-contact grid, the physical cost of learning whether
information matters does not itself alter the ordinary top set.

## Paid work

### RELEVANT states, 24

- mean combined simulated steps: **478.6667**;
- max: **545**;
- mean energy bill: **1.35753**;
- max energy bill: **1.49020**;
- mean vigilance bill: **1.85733**;
- max vigilance bill: **1.99000**.

No fallback is executed in these states.

### FALLBACK states, 56

- mean combined simulated steps: **503.3571**;
- max: **603**;
- mean energy bill: **1.40691**;
- max energy bill: **1.60620**;
- mean vigilance bill: **1.90671**;
- max vigilance bill: **2.10600**.

The canonical Candidate-G probe mean is 470.05 simulated steps/state. The
fallback therefore adds about **33.31 simulated steps on average** in the
non-relevant states, roughly 7.1% over the probe mean. That extra work is paid,
not hidden.

## H4 verifier correction after first exposure

The first implementation run, `42478455412`, reported H0/H1/H2/H3/H5 PASS
and H4 FAIL. The candidate mechanism itself already showed 56/56 funded
fallbacks, exact P1.3 score identity and 20/20 restoration.

The H4 verifier contained a bookkeeping defect: after the 80-state construction
loop, its physical-body reconstruction used the outer local variable `level`,
which had ended at 50, rather than the stored `row["level"]`. H4 therefore
recomputed some receipts against the wrong fixture body.

The correction replaced that captured loop variable with the immutable row
identity and added explicit H4 failure receipts. No candidate computation,
fixture, threshold, work receipt, fallback result or H0-H5 rule changed.

Run `42478647427` then passes H4 under both Python versions. This is a
verification repair, not post-result tuning of Candidate-H.

## Interpretation

The software result is strong but deliberately narrow:

- Candidate-G's first-contact defect is not that accurate projection is
  impossible to afford in these fixtures;
- the defect is that Candidate-G switches the whole policy geometry on
  **support**, before knowing whether information is relevant;
- a paid relevance gate can keep the precise projector where information is
  strictly advantageous and restore P1.3 ordinary geometry everywhere else;
- the fallback remains physically paid and fully fundable on all 56 states.

This resolves the specific first-contact support-versus-relevance defect on the
frozen software grid.

It does **not** establish:

- a correct runtime implementation;
- post-contact relevance semantics;
- persistence or survival benefit;
- a reason to reopen 56/57;
- authorization for a fresh live panel.

## Handoff

Do not jump directly to a live Candidate-H. The next missing piece is
**post-contact relevance gating** under the existing personally learned
frontier belief. Freeze and falsify that separately in software.

Only after first-contact and post-contact relevance semantics both have bounded
software evidence would a unified runtime integration question be admissible.

P1.3 remains reference. Candidate-G live remains closed. 56/57 remain exposed.
No fresh World/life panel is authorized.
