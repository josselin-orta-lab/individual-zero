# Stage7: independent read-only reproduction of lived persistence

**Status: post-run audit tooling, not a new experiment.** This source was
authored **after the 16 November 2026 prospective Stage7 execution started**.
It MUST NOT be used to redefine that study's primary outcome, reseed populations,
change its P1.3 motor, or relaunch any original life. It is an explicitly
separate verification of the original result, to run only when the complete
scientific artifact is available.

## Evidence inputs

Download the three original unmodified artifacts from the same successful
[Stage7 Actions run #43830174125](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43830174125):

1. `stage7-persistence-science-preexposure-RUN_ID` containing `SCIENCE_PLAN.json`.
2. `stage7-persistence-originals-RUN_ID` containing `G0/`, `G1/`,
   `G2/`, `SELECT_G1.json`, `SELECT_G2.json`,
   `PHASES.jsonl`, `CLAIM.json` and `R_FINAL_PERSISTENCE_SCIENCE.json`.
3. `stage7-persistence-result-RUN_ID` containing `SCIENCE_RESULT.json`.

Neither a technical engineering artifact nor a synthetic preflight ZIP is
acceptable in place of scientific originals. Preserve the original ZIP bytes,
their GitHub artifact IDs, publish timestamps, and ZIP SHA256 metadata before
extraction. Use read-only copies for auditing; no extracted JSON may be edited.

## Usage (no worlds, no new lives)

```bash
PYTHONPATH=src python -m i3.lab.stage7_persistence_independent_audit \
  /extracted/science-plan/SCIENCE_PLAN.json \
  /extracted/science-originals \
  /extracted/science-result/SCIENCE_RESULT.json
```

The original runner used a `/tmp` path. The extracted archive may reside
anywhere; this read-only verifier binds it through `CLAIM.json` and the
source/plan SHA rather than requiring the runner filesystem path to still
exist.

The auditor only uses Python's standard library. It independently rehashes
every compressed original and decompressed JSON payload; checks all 11,520
population/arm/individual/family/repeat coordinates, World/life/genome/source
pins, original horizon, deaths/censoring, trace length and cognitive
energy/vigilance payment. It checks both arms share the same ecological
opportunity within each generation. From the original lived steps and
censorship markers it rebuilds the 16 G2 selected-minus-random parental
contrasts with exact integer totals before division, and checks the original
published `SCIENCE_RESULT.json` values and decision against the *unchanged*
13/16 positive threshold. It also cross-checks G0 and G1 population summaries
and all nine SHA-linked phase payloads, including parent-selection files.

A passing result uses:
`READ_ONLY_REPRODUCTION_OK`, with the frozen underlying biological status
unchanged. A failure means **AUDIT_MISMATCH / NO_NEW_VERDICT** requiring a
transparent investigation; it is not a licence to rerun the study or discard
an adverse result.

## Boundaries

This independently validates SHA-bound *records*, not replayed physical
decision semantics. It does not create an independent origin timestamp,
attest random OS entropy, prove environmental independence, authenticate
GitHub off-host signatures, or validate the causal interpretation of raw
cross-generation changes. These are separate questions; the experimental
unit remains each of the 16 populations. A negative finding stays negative
unless a distinct, prospectively pre-registered experiment is undertaken.

**Scientific status on creation:** Stage7 first attempt had its Python
3.11 and 3.12 complete engineering jobs still running; the scientific cohort
had not begun. No success or outcome values are assumed by this document.
I1 active, I3 unregistered reference; Stage2.1
`NOT_ISSUED/HOLD_NO_VERDICT`.
