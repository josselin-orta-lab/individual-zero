# I2 physiological needs, native stage 2 (2 November 2026)

After the merged independent pure body/temperament foundation PR #889, the new `src/i2/modules/native_physiological_needs.py` assesses **current four-channel first-person body data** with immutable born `BirthTemperament` (five coordinates). The readout produces four deficit and urgency values, a leading need when any deficit exists, and danger alerts for food/water/integrity reserves at or below 10.0.

**This stage does not integrate into the active I2 toy SQLite prototype yet.** It does not choose actions, update episodic values, supply hidden world truth, pay UC, declare M11 or open a second mutable state owner. Risk and need weights are explicit **I2 study defaults**, not established I1 Stage4 or Stage5 parity. The threat-sensitivity trait modulates current integrity urgency, not real body physics, reflex availability or learned action value.

The working hypothesis is that separate, independently auditable native physical state and innate regulation can later be wired into the existing I2 owner's capture -> paid valuation -> admitted action -> physical effect -> observed consequence loop without copying the I1 cognitive runtime. Strict parity requires a declared I1 world config, a same-action physical tape, all four channels, fatigue/sleep dynamics, matched five raw traits and observed motor affordances. Neither advantage nor equivalence is established by these pure tests.

Focused regression: `python -m unittest discover -s tests/i2 -p 'test_native_physiological_needs.py' -v`. No tuning or new scientific cohort is authorized by this doc. ADR-0009 and development issue #888 remain authoritative.
