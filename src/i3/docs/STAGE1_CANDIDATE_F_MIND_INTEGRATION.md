# Stage 1 Candidate F: opt-in Mind integration

Issue #1111. Baseline:
`046d3846f49d1e489d43576968916415001f4d6e`.

**FROZEN BEFORE IMPLEMENTATION. SOFTWARE INTEGRATION ONLY.**

## Scope

#1120 passed Candidate F's laboratory software gate. This slice exposes those
same frozen semantics through `Mind.simulate` without changing the reference
path.

## Modes

Add:

`simulation_mode="reference" | "candidate_f"`

Default:

`reference`.

Candidate F is valid only when:

`projection_accounting == "event_local_quadratic4"`.

Any other pairing fails closed before simulated scoring.

## Reference path

When `simulation_mode="reference"`, `Mind.simulate` follows the existing
ordinary-float implementation unchanged.

No default constructor, runtime life, decision, learning or accounting behavior
is switched to Candidate F.

## Candidate F path

The integrated Candidate F must reproduce #1120:

- one Decimal body, precision 100;
- `Decimal.from_float` for initial body and learned action means;
- existing movement grouping and horizon counter;
- existing one simulated-step CognitiveWork charge per explicit simulated plan
  block;
- existing learned mean/uncertainty readout;
- existing clamp/death/reward/gamma/value semantics;
- body converted to float only for existing feature/distress/value readouts;
- surviving Decimal state passed directly into the existing Candidate-E
  `event_local_quadratic4` sparse projector without a float state round-trip.

No action, world fact or learned product is added.

## Frozen integration gate

1. default/reference path remains reference and rejects unknown modes;
2. integrated Candidate F values match frozen #1120 laboratory Candidate F on
   all 486 cases to <= **1e-12**;
3. integrated projection cost remains Candidate E's cost profile, with maximum
   **112** on the frozen direct grid;
4. invalid mode/projection pairings fail before scoring;
5. no World/life study is opened.

A pass authorizes only the next forecast-cost contract slice.

Omega remains unauthorized until dynamic forecast-cost accounting for the
integrated Candidate F is prospectively frozen and verified.

No ADR-0015 reference adoption follows from this integration.
