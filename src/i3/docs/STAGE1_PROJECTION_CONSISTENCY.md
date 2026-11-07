# P1.3 self-projection: bootstrap consistency (frozen before implementation)

**Software slice only.** No World, no life, no study index. The reference
cognition stays unchanged by default; any adoption needs a separate,
prospectively consigned ADR-0015 gate.

## Observed defect and confirmed cause

Found while decomposing the ω falsifier
([results](studies/stage1-omega-software-falsifier/RESULTS.md)): appending
explicit waits raises a plan's simulated value. With the #1101 fixtures, a 6-step
horizon and the reference projection (geometric chunks 1, 2, 4 … 128, each
charged with the distress at its **end**), the gap is +0.0112 / +0.0325 for
1 / 3 extra waits (food 20), and +0.0264 / +0.0757 (water 20).

Diagnostic check before this protocol: with **per-step** chunks (255 × 1) the
gaps vanish to 1e-4, and absolute values rise (−1.4263 → −1.1357). The cause is
end-of-chunk accounting. It overstates future distress under worsening drift,
so the projection is both inconsistent and too pessimistic.

## Invariant

Appending one explicit step whose predicted effect equals the projection's own
drift must not change a plan's value. With the reference fixtures, `attendre`
is close to, but not exactly, that drift (it also moves energy by −0.35). So
the invariant is tested exactly on a projection-equivalent fixture, and as a
gap measurement on the reference fixtures.

## Candidate accounting schemes

- **A. Per-step (truth).** 255 unit chunks, 255 paid units per projection. This
  is the diagnostic reference, not a candidate for adoption: about 32 times the
  current projection cost.
- **B. Discounted trapezoid.** Same chunks and the same 8 distress evaluations.
  Within a chunk of `n` steps, distress is interpolated linearly between the
  chunk's start (the previous chunk's end) and its end, with exact discount
  weights:

  ```text
  A_n = (1 − γ^n) / (1 − γ)
  B_n = (1 − (n+1) γ^n + n γ^(n+1)) / (1 − γ)^2
  S   = r_start · A_n + (r_end − r_start) · B_n / n
  ```

  `n = 1` reduces exactly to the reference, and the first chunk is size 1, so no
  extra evaluation is ever needed. Paid units stay 8 and all cost ceilings stay
  valid. Death, restoration and clamping keep their reference handling at chunk
  ends.

## Grid (frozen)

- **Genomes.** `midpoint()` and `generation_zero(6000)` to `(6004)`.
- **Fixtures.** The #1101 `make_mind` fixture (wait drift; learned sleep, hence
  restoration in the projection), and the same mind with sleep unlearned.
- **Bodies.** Each channel alone at 10, 20, 30, 40 or 50 (others 80), all at 80,
  and food = water = 30 (others 80).
- **Horizon.** 6.

## Metrics

For each scheme, against A:

- maximum |gap| for +1 and +3 waits;
- maximum |value − A value| for the `prefix` plan;
- maximum |(value(+wait) − value(prefix)) − A's same difference|, the bias that
  matters for decisions;
- paid simulated units per projection.

## Selection rule (prospective)

B becomes the **opt-in candidate** if, on the grid:

1. its maximum decision bias (third metric) is at most 1e-3, about one tenth of
   the score gaps observed in real decisions (P5e median 0.016–0.027);
2. its paid units equal the reference's.

Otherwise no candidate is promoted, and the defect is recorded with B's measured
error and A's cost.

Whatever happens, the default stays `chunk_end`.

## Then, prospectively

- Rerun the frozen ω falsifier unchanged, with the projection mode set to the
  candidate if one passes, and report both runs side by side.
- Draft, but do not execute, the ADR-0015 gate for adopting the candidate into
  the reference cognition.
