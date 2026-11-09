# Stage 2.1: prospective RANDOM-EQUAL-MEAN parameter custody

**Value frozen from DEVELOPMENT 80/81, prior to any gate/validation opening.**
This is a parameter-estimation result from the already frozen
[Stage-2.1 protocol](../../STAGE2_REPLAY_GATE.md), not a new
scientific hypothesis, not a gate verdict and not a transport-code change.

- Source: [complete original-custody DEVELOPMENT result](RESULTS.md) and
  [machine result](evidence/SCIENTIFIC_RESULT.json).
- Executed source SHA: `5d362e226f8e87df226dae5b239e26cc99072a13`.
- Frozen plan SHA-256:
  `a28606678d13bb9af18f590c328a63eb9eb82f7130c90656e4f520260d294c92`.
- Arm: `p13_replay_gate_v1` (GATE) only.
- Numerator: **5,532** actual paid replays across 12 GATE lives.
- Denominator: **867** actual sleep steps across those same lives.
- Parameter: **6.380622837370242 replays per sleep step**
  (exact rational `5532/867` before floating-point presentation).

Frozen interpretation: RANDOM-EQUAL-MEAN is the existing P1.3
priority-ordered replay policy with a dedicated, life-seeded random
count per sleep step whose **target mean** equals the parameter above.
Its audit cost must match the gate audit, and all physical work remains
paid. The previously frozen mechanism and controls must not be altered
to fit observed deaths or advantage.

**Not yet frozen:** the discrete count distribution and its truncation
rule when fewer than `k` memories are eligible, exact random stream
ownership, independent population/selection schedule, gate uncertainty
method, primary margins and holdout World allocation. Those must be
preregistered before implementing or exposing the next scientific
panel. A natural floor/ceiling mixture is an option, but is **not yet
approved or frozen here**.

**No new World authorization.** Stage-2.1 DEVELOPMENT 80/81 was
consumed once. Selection/validation/reserve remain closed until a new
prospective owner-approved design.
