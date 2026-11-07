# Stage 1 — ω software falsifier: results

**Verdict under the frozen rules: `CAPACITY_SHOWN`, with a measurement caveat
that limits its reach.** ω moves the water-frontier values in the predicted
direction at identical paid computation. But a plan-length bias in the P1.3
self-projection, found while decomposing the result, makes the absolute sign of
those values uninterpretable. Fixing that bias is the next blocker.

Protocol: [STAGE1_OMEGA_SOFTWARE_FALSIFIER.md](../../STAGE1_OMEGA_SOFTWARE_FALSIFIER.md),
frozen at `e37a6c8`; implementation `6919822`; executed once. Software only:
**no World, no life, no study index**. Data: [falsifier.json](falsifier.json).

## Frozen rules

| Rule | Result |
| --- | --- |
| R0 ω = 0 reproduces #1101 (0/80 epistemic, 28 declined, max information 0.000592902270, best advantage 0.0695239461) | **Pass** |
| R1 paid work identical across ω, state by state | **Pass** |
| R2 trials and positive revelations never fall as ω rises | **Pass** |
| R3 some ω > 0 adds positive water revelation where ω = 0 has none | **Pass**: 0 states at ω = 0.25, 4 at 0.5, 4 at 1 |

| ω | Trial among best | Epistemic trials | Declined | Positive water revelation | Max revelation advantage |
| --- | --- | --- | --- | --- | --- |
| −1 | 48 | 4 | 32 | 48 | 0.0156 |
| −0.5 | 52 | 8 | 28 | 52 | 0.0165 |
| 0 | 52 | 0 | 28 | 52 | 0.0174 |
| 0.25 | 52 | 0 | 28 | 52 | 0.0178 |
| 0.5 | 56 | 4 | 24 | 56 | 0.0183 |
| 1 | 56 | 0 | 24 | 56 | 0.0192 |

Epistemic trials (chosen *and* informative) vary non-monotonically and stay
rare. ω acts on expectation, not on information.

## Post-hoc finding: plan-length bias in the P1.3 projection (not frozen)

At ω = 0 the water revelation advantage is already positive in 52/80 states,
with zero trial information. In the first such state (food 20), even the
negative-effect branch prefers to drink again. Decomposing it showed the
simulator values a plan more just because it is longer:

| Body (E, F, W, I, V) | prefix | + wait | + 3 waits | + move | + sleep |
| --- | --- | --- | --- | --- | --- |
| 80, 20, 80, 80, 80 | −1.4263 | −1.4151 | −1.3938 | −1.4157 | −1.4181 |
| 80, 80, 20, 80, 80 | −1.9801 | −1.9537 | −1.9045 | −1.9548 | −1.9537 |
| 80, 80, 80, 20, 80 | −0.8229 | −0.8197 | −0.8132 | −0.8231 | −0.8231 |
| 80, 80, 80, 80, 80 | −0.4742 | −0.4697 | −0.4610 | −0.4697 | −0.4698 |

Waiting changes nothing useful in the body, yet each extra wait raises the
value. Probable cause, from the P1 design: the innate self-projection charges
each geometric chunk (1, 2, 4 … 128 steps) with the distress at the chunk's
**end**. Under worsening drift that overstates future distress, so a plan that
starts the projection later looks better. The bootstrap is inconsistent: an
explicit step that matches the projection's own drift should leave the value
unchanged.

### Consequences

- **What survives.** The ω effect: every ω arm compares the same plans, so the
  bias cancels in the differences (R1, R2, direction of R3).
- **What does not.** Absolute signs. "Positive revelation in 52/80 at ω = 0",
  #1101's "best trial advantage +0.0695" and the R3 crossing count all compare
  plans of different lengths (stop vs trial vs reuse).
- **Wider reach.** Every P1.3 decision comparing options of different lengths
  is exposed, including the reference cognition and past Stage-1 kernels. This
  is not shown to change survival; it is a measured evaluation defect.

## Next intervention (not implemented)

**Bootstrap consistency in the P1.3 projection.** Proposed invariant: appending
one explicit step whose predicted effect equals the projection's drift must not
change a plan's value (to numerical precision).

- **Candidate fix.** Charge each chunk with its exact discounted distress along
  the linear drift, or at least with a start/end average, instead of the end
  value alone. Pay any extra evaluations.
- **Falsifier.** The table above must flatten. Then rerun this ω falsifier
  unchanged on the corrected projection, prospectively.
- **Why it needs a gate.** It changes the reference cognition, so any adoption
  goes through an ADR-0015 gate, and the result is consigned before it.

Only then can ω's genome slice and live integration be judged on unbiased values.

**Follow-up:** the bias was confirmed and characterized; under an unbiased
projection ω acts strongly and monotonically. See
[projection-consistency results](../projection-consistency/RESULTS.md).

