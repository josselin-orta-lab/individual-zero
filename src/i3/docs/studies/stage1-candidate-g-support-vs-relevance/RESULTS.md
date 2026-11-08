# Candidate-G support versus decision relevance: result

Protocol:
[STAGE1_CANDIDATE_G_SUPPORT_VS_RELEVANCE.md](../../STAGE1_CANDIDATE_G_SUPPORT_VS_RELEVANCE.md).

**Software diagnostic only. No World, no life, no fresh allocation.**

Classification:

`SUPPORT_TRIGGER_ORDINARY_POLICY_DRIFT_PRESENT`

The result was first exposed in CI run `42477702730` before an import-only
assertion failed. The assertion incorrectly required `i3.modules.world` not to
be transitively imported, although `Mind` already imports the shared
`DIRECTIONS` constants from that module. The protocol was then corrected only
at that technical authority boundary: no World instance, generation, capture or
hidden-world read. No fixture, state, plan, projector, tolerance, observable or
classification rule changed. Run `42477882554` reproduced the same result on
Python 3.11 and 3.12 and passed the full I3 software/navigation checks.

## Canonical information kernel

The frozen #1156 kernel is unchanged:

| Observable | Result |
| --- | ---: |
| States | 80 |
| Strict epistemic selected | 24 |
| Support-only nonselected | 56 |
| Declined | 40 |
| Mean simulated work / state | 470.05 |
| Work-ceiling violations | 0 |

Personal recurrence support exists in all 80 states. The classification below
therefore asks whether **support alone**, before strict epistemic relevance is
established, is enough for the projector switch to alter ordinary choice
geometry.

## Ordinary-plan geometry

The fixed ordinary basis is `wait`, `sleep`, `move`, and `move_wait`.

| Class | States | Top-set changes | Unique-winner changes | Reference mean paid simulated steps | Candidate-F mean |
| --- | ---: | ---: | ---: | ---: | ---: |
| All | 80 | **44** | **12** | 37.0 | 371.55 |
| Strict epistemic selected | 24 | **24** | **8** | 37.0 | 378.0 |
| Support-only nonselected | 56 | **20** | **4** | 37.0 | 368.7857 |

The support-only result is the decisive observation. In **20/56 states where the
information trial is not strictly advantageous**, merely using the
Candidate-F projector changes the top ordinary option set.

Those 20 states are structurally concentrated:

- all 16 water-deficit states at water levels 20/30/40/50 and horizons
  4/6/8/12;
- the four integrity=30 states at horizons 4/6/8/12.

For the water states, P1.3's ordinary top is `move_wait`; Candidate-F often
turns this into a broad tie among `move`, `move_wait`, `wait`, and at lower
water also `sleep`. For integrity=30, P1.3's `move_wait` becomes
Candidate-F `wait`.

The maximum pairwise ordinary score-gap shift is
**0.026429932777191745**, at water=20. The Candidate-F four-plan evaluation
costs up to 448 simulated steps versus 37 for the reference basis.

## Interpretation

Candidate-G currently conflates two distinct facts:

1. a personal information path is **supported**;
2. that information is **decision-relevant now**.

The first is sufficient to switch the entire decision to Candidate-F
projection. This diagnostic shows that this switch can alter ordinary policy
even when the epistemic trial itself is not strictly advantageous.

That mechanism is a plausible contributor to the live 56/57 behavior, but this
software diagnostic does **not** causally reinterpret the exposed lives and does
not rescue Candidate-G.

The next admissible architecture question is therefore narrower than another
projection optimization:

> Can the system pay to establish information relevance, but keep ordinary
> policy on P1.3 when the information trial is not strictly advantageous?

Any such candidate must preserve commensurability inside the final actual
decision, pay both computations if a fallback is required, read no omega and
encode no action-specific survival rule.

## Boundaries

This result does not authorize a Candidate-H implementation in this PR, a fresh
World/life panel, reuse of 56/57, selection, validation, reserve exposure,
reference adoption or Stage 2.

P1.3 remains reference. Candidate-G live remains closed.
