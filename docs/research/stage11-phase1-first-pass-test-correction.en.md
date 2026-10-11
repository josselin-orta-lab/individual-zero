# Stage11 phase-1 Planning correction: failed first unit pass and test repair

**Recorded on 2026-10-11 before changing the failing assertion and before re-running CI.** This is a public software-development correction, not a held-out scientific result.

- [CI #38114574639](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38114574639), source `65162d884ff07e3e6f01e58a3f06bf98bda42359`: **776 tests executed, 1 failed** (`test_phase1_cap_one_filters_known_lethal_before_offering_east`). It must not be reported as a passing CI.
- The newly added test asserted that no proposal with direction `north` could occur anywhere in four steps. The recorded proposed directions were `east, north, east, east`. A north move *from the new eastern position* can have destination `(3,1)`, which is not the registered lethal zone `(2,1)`. Direction alone is not a canonical safety fact. This assertion was too broad and could incorrectly reject legitimate navigation.
- Repair only the test to require that the **first proposal is east**, that no proposed `destination` equals **the known lethal position `(2,1)`**, and that no physically captured visit equals `(2,1)`. Keep the physical public scenario, `max_targets_per_cycle=1`, versioned Planning preflight, Action Control veto, all UC costs and production code unchanged.
- New Phase-1 charge/lookup ordering unit tests and previous public scenarios did not show another failure in this first run. **They are not sufficient to call the whole change validated** until the repaired suite passes.
- Full Goldens, Python 3.11 reference replay, unseen hazards and independent Stage9 held-out remain unrun. Stage11 remains IN PROGRESS; Stage9 scientific NO-GO and PR draft/unmerged.
