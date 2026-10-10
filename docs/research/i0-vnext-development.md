# I0-vNext development register

**Classification:** development-only; no scientific Stage-9 acceptance.

- Git branch: `i0/vnext-stages-10-12`
- Integrated I0 software starting point: `773cd84557d661977568c318413510096d15fed0` (`main`, 2026-10-10)
- Normative specification: `docs/architecture/reference/en/mvp-specification-v1.2.1.md` (unchanged)
- Stage 9: **SOFTWARE IMPLEMENTED / SCIENTIFIC VALIDATION PENDING / NO-GO**. The independent held-out procedure is not authorized. Historical results are immutable.
- Stage 11: **IN_PROGRESS**, P-48 Exploration and later Global Modulation; no science acceptance claimed.
- Stage 10: NOT_STARTED.
- Stage 12: NOT_STARTED.

Development-only source: [Stage-9 behavior](stage9-development-behavior-2026-10-10.en.md) and [Stage-9 NO-GO](stage9-heldout-prelaunch-decision-record.md). Public seeds 41 and 42 may be used for non-held-out comparisons; no result from I0-vNext retroactively validates the Stage-9 implementation.

The I0-vNext branch must not be merged into `main` automatically. Use targeted local Python tests before commits and draft pull requests without CI labels while the GitHub Actions quota is constrained.
