# Stage 1 Candidate-H unified software integration: result

**SOFTWARE-INTEGRATION PASS. ZERO LIVES. NO RUNTIME REGISTRATION.**

Protocol:
[STAGE1_CANDIDATE_H_UNIFIED_INTEGRATION.md](../../STAGE1_CANDIDATE_H_UNIFIED_INTEGRATION.md).

Final tested source:
`bf527c92dd445b4f4ffcab4c8a24cbe8ed0c959f`.

GitHub Actions:
`42482799511`, Python 3.11 and Python 3.12 both PASS.

Final verdict:

`CANDIDATE_H_UNIFIED_SOFTWARE_INTEGRATION_PASS`

## Frozen classifier parity

The unified component preserves both previously frozen Candidate-H semantics
state-for-state.

First contact (#1162 fixture):

- states: **80**;
- RELEVANT: **24**;
- FALLBACK: **56**;
- mismatches: **0**.

Post contact (#1163 fixture):

- states: **80**;
- RELEVANT: **68**;
- FALLBACK: **12**;
- mismatches: **0**.

No third relevance definition was introduced.

## Frozen integrated routing panel

The prospectively fixed software panel contains 20 body states x 3 personal
history modes = **60 decisions per omega arm**, with no World and no life.

Final omega=-1 routing:

- complete integrated decisions: **60/60**;
- P1.3 final route: **37**;
- Candidate-F final route: **23**;
- probe-unfunded decisions: **0**;
- integration errors: **0**.

All five required route classes are observed:

1. no support -> P1.3 final;
2. first-contact support but non-relevant -> P1.3 final;
3. first-contact relevant -> Candidate-F final;
4. post-contact actionable but non-relevant -> P1.3 final;
5. post-contact relevant -> Candidate-F final.

Repeating the complete fixed panel with genome omega=-1 and omega=+1 gives
**zero output mismatches**.

The forced low-budget fixture returns
`NO_FUNDED_RELEVANCE_PROBE`, executes no Stage B and restores persistent mode
to `reference/chunk_end`.

## Frozen U0-U9 rules

| Rule | Result |
|---|---|
| U0 authority boundary | PASS |
| U1 first-contact classifier parity | PASS |
| U2 post-contact classifier parity | PASS |
| U3 exact same-body P1.3 fallback identity | PASS |
| U4 relevant Candidate-F final geometry | PASS |
| U5 phase work/body accounting | PASS |
| U6 persistent projector restoration | PASS |
| U7 source separation and omega invariance | PASS |
| U8 all frozen routes observed | PASS |
| U9 output authority boundary | PASS |

For U3, all **37/37** P1.3 final routes match their independently recomputed
same-body P1.3 control on action, parameter, funding, option, paid score
witnesses and Stage-B work. Final control-body reconciliation is within the
already frozen U5 tolerance. Final mismatch list: **empty**.

## Engineering corrections before final verdict

The first implementations exposed three verifier/integration defects. They are
retained as part of the result history rather than hidden.

1. Run #208 used an import test that rejected `i3.modules.world`, although
   existing P1.3 `Mind` transitively imports that module for direction
   constants. The test was corrected to forbid runtime life and World
   generation/ecology imports instead. Candidate computation was unchanged.
2. The integrated mind initially compared two cumulative floating-body
   settlements with exact tuple equality. The protocol had prospectively frozen
   U5 at max absolute gap <= `1e-12`. The implementation was corrected to
   enforce that already-declared tolerance. No fixture or rule changed.
3. Run #210 then showed U3 FAIL only because the U3 verifier added exact
   bit-for-bit final-body equality, a criterion not present in U3 and already
   governed by U5. The verifier was split into explicit identity components and
   the same frozen U5 body tolerance. Final U3 has **zero** component failures.

These corrections did not change the first-contact or post-contact relevance
predicates, synthetic panel identities, seeds, body levels, history modes,
omega arms, U0-U9 rules or authority boundary.

## Interpretation

This PASS establishes that the two Candidate-H relevance rules can be composed
cleanly in software while:

- paying the detached relevance probe;
- recomputing the final decision from the cognition-depleted body;
- returning exactly to P1.3 on fallback;
- using one commensurate Candidate-F geometry on relevant decisions;
- avoiding genomic omega;
- preventing post-contact recurrence reads;
- restoring the persistent P1.3 projector after every path.

The integration intentionally **overpays** by not sharing Stage-A ordinary
scores with Stage B. It proves a clean integration, not optimal efficiency.

This result authorizes only the preparation of a separately frozen,
fresh DEVELOPMENT protocol. It does **not** authorize adding Candidate-H to
`runtime/life.py`, opening a World, selection, validation, reserve use,
reference adoption or Stage 2.

P1.3 remains reference. Candidate-G live remains closed. Development 56/57
remain exposed and closed.
