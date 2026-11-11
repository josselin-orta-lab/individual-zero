# Stage 2.1: first-person next-action archival byte verification versus detached alternative

**11 November 2026. Archived development-original reanalysis only, no new births.**
Technical verdict: **READ-ONLY 48-ORIGINAL SHA-PINNED BRIDGE PASS**.
Scientific verdict: **NOT_ISSUED**.

## Exact, reproducible source custody

- [Prospective fixed protocol](ARCHIVED_NEXT_ACTION_ACTUAL_VS_SHADOW_BRIDGE_PROTOCOL_2026-11-11.md)
  committed FIRST at `e8ab645c975f5ea6935bf91c0a633d434c9bf94e`
  against main baseline
  `0c63972774bde1c9cf8369e02946e4f31e68884e`,
  before implementation or any reading of the raw original records.
- Existing **consumed** source evidence branch:
  `evidence/i3-next-decision-24-development-20261110-originals`,
  **EXACT immutable Git commit**
  `20ca7efbf7797fa7b1f12983ce68906b754b312c`,
  archive directory
  `archive/i3/stage2-next-decision-development-2026-11-10/`.
  Old manifest SHA-256
  `53fdea10f56994a9171d274ecc6388a3301128503b98c1572052ee4b780196b5`,
  old-source code SHA `d86474d4eea47e8066169988c152f24c40f8efb6`.
- Existing [read-only original auditor](../../../lab/stage2_next_decision_24_original_audit.py)
  is executed **first**: verifies **48/48 packed + 48/48
  unpacked SHA-256**, source admission, plan, policy, original-to-reduced
  exact identity, all 24 paired families, cognition funding, old
  public summary and all negative/null records.
- [Merged PR #1307](https://github.com/josselin-orta-lab/individual-zero/pull/1307)
  implements the **new read-only archive bridge** in
  `src/i3/lab/stage2_next_action_original_archive_bridge.py`
  and a branch-scoped job in the **existing registered**
  `.github/workflows/i3-proposal-checks.yml`; final tested
  source `d8afdc7e5058ad514a47cac13176196f824cae09`,
  squash `ff7ce3b320b740fc6b3c301d45cd23403f16a45a`.
  The job fetches the old branch but fails closed unless the fetched
  Git commit is **exactly** the frozen archival SHA; then it
  uses `git archive`, **never** `run_life`, a G/R archive runner
  or World engine entrypoint.
- [Exact-source Actions #43017416135](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43017416135)
  **PASS: 1116/1116 I3 software tests in both Python 3.11 and 3.12**,
  both 7/7 engine/generation guards, Python 3.11 **533
  navigation checks, 0 errors and 0 warnings**. The new
  embedded **READ-ONLY archive job passed on both versions**.
  Its aggregate-only SHA-256 was identical on both:
  `d04e9c226340e9b8a14a2df5242765b7f9b2239b4c0bb66ced4077e5145d9776`.

The old archive's original [#1275](https://github.com/josselin-orta-lab/individual-zero/pull/1275)
audit was previously completed. This new result **re-verifies**
old bytes and draws a narrower provenance distinction; it does
**not** constitute new sample exposure or independent replication.

## Entire frozen 24-pair read-only result

| Original archived source category | Verified number |
| --- | ---: |
| Complete OLD paired assignment units | **24/24** |
| Complete OLD born full-policy original files checked | **48/48** |
| First different actually funded memory subset | **20/24** |
| No different funded subset (retained in denominator) | **4/24** |
| Different subset but no subsequent first-person perception | **0/24** |
| Next random-content choice asserted identical to the living Mind's choice and work by verified source observer | **20/24** |
| Detached priority alternative computed at those same next perceptions | **20/24** |
| Same priority-detached and random-living motor/parameter | **19/24** |
| Different priority-detached and random-living motor/parameter | **1/24** |
| Alternate **priority** motor executed in an additional World | **0** |
| NEW born life / NEW World opened by this read-only audit | **0 / 0** |

The one different hypothetical choice belongs to the old **stable**
family. Source families remain **8 stable, 10 depletion, 6 pulse**
without dropping unfavourable or non-fork cases.
No new genotypes, world seeds, source witness, outcomes,
CognitiveWork or result selection were generated.

**Critical epistemic distinction:** the archived random-content
observer was instrumented in the original `run_life` to compare
its detached random clone **exactly** with the actual living
`Mind.decide` choice and work. The archived priority clone
represented a counterfactual decision on the same captured
first-person perception, but **its motor was never sent to
World**. The integrity of the original source files is now
byte-verified; that does not make the alternative's imagined
World outcome factual or independently demonstrate a beneficial
information-delivery intervention.

These are not two cost-matched **visible-vs-discarded**
readout-policy arms. The old arms differed by replay-content
selection; the new passive three-forecast readout was **never
delivered into the living next-action decision**. The old
`NextDecisionReplayObserver` also provides no independent
hardware/video attestation beyond archived internal
source-checked code. The new
`NextActionPairCustody` software contract #1305
must not be falsely populated using this old study as a
genuinely treated and untreated readout pair.

## Negative CI failures and corrections preserved

- [First Actions #43016629444](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43016629444)
  **FAILED** as the generation-ownership guard correctly rejected
  an **unregistered additional GitHub workflow**. The separate
  original-read-only archive workflow
  [#43016629615](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43016629615)
  did succeed on Python 3.11 and 3.12. The extra workflow was
  removed and its read-only job moved to the already registered
  `i3-proposal-checks.yml`.
- [Intermediate Actions #43016903680](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43016903680)
  **FAILED** two *new negative tests*: missing prerequisite mock
  reduced-row file, and a mutation that did not actually falsify
  the compared motor equality. The test harness was corrected,
  not the original archival content, exposure, expected counts
  or research hypothesis. All final exact-source controls
  passed at #43017416135. The failed runs are not hidden.

## Next actual scientific dependency, still blocked

To observe genuine **information → later decision → native
post-paid-learning first-person consequence**, a new
prospectively sealed and independently sampleable cohort would
need a freshly authorized index/source scope,
a real native-billed readout delivered to the *living*
choice process versus identical work computed-and-discarded,
preoutcome and pre-next-action seals, actual post-learning body
loss, and complete no-funding/death/censor records. An
accurate forecast alone is not an adaptive value mechanism.
The existing cost tariff still is not a measured CPU-to-body
conversion, and the old source cannot estimate this new
treatment's information benefit or survival effect.

Reproducibility (after separately checking out the exact old
archive commit into `EVIDENCE_ROOT`):

```bash
PYTHONPATH=src python -m i3.lab.stage2_next_action_original_archive_bridge EVIDENCE_ROOT
```

`EVIDENCE_ROOT` is the directory containing the old
`SOURCE_LOCK.json`, `EXECUTION_REPORT.json`, `REDUCED_ROWS.json`,
and `originals/`. The command interprets only the *existing
verified* archive and outputs aggregates, not original life data.

**Formal boundary:** `old_originals_byte_verified=48`;
`new_Worlds=0`, `new_born_originals=0`,
`scientific_lives=0`, `scientific_verdict=NOT_ISSUED`;
I3 remains **unregistered Stage 2.1**, no Stage 2.2 GO,
no intervention on an individual and no new scientific authorization.
Issues [#1062](https://github.com/josselin-orta-lab/individual-zero/issues/1062),
[#1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276)
and [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283)
remain OPEN.
