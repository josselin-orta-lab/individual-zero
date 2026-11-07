# Stage 1 frontier-water fresh development diagnostic: engineering failure

**ENGINEERING FAILURE. INCOMPLETE PANEL. SCIENTIFIC RESULT NOT EVALUATED. NO RERUN.**

Prospective protocol: [PROTOCOL.md](PROTOCOL.md), issue #1061, PRs #1083/#1084.

The 48/49 panel was opened once on 7 November 2026 UTC. Execution stopped
during the first three-arm block exactly as preregistered after an engineering
exception. The remaining planned cases were not run.

## Exact custody

- Runtime baseline frozen by the protocol:
  `1236d040279aff847adeefb6d6792e67dd72b2f1` (PR #1082).
- Prospective protocol merge:
  `90bb5a6d4d2f39b6813c11c2b48baea6542c0831` (PR #1083).
- Exact execution source:
  `a1e53daee016e801289a85c9cd7855798b048051`.
- Protocol SHA-256:
  `cc225b0eb6c0b402f4736d8c97a5106d7d28310fe8870072d0a8d4ea74744fa4`.
- Source snapshot SHA-256:
  `3373b578366a1ef25a64a74fbd82c5a104d50da8dfb278b500837ac89782f205`.
- Actions run: `42364436764`.
- One-shot job: `128379511200`.
- Artifact: `13570888057`.
- Artifact ZIP digest:
  `sha256:cd836ffbc5bb35cd1db414c1bfb3161f673af994fdc4acca25f48febc392d10d`.
- Evidence commit:
  `89a36a9186bb9ff89769598baba021f7c79af62a`.
- Evidence tree:
  `e10f33fd85b807f1f53a60216ce0acfa9ff47df2`.

The evidence branch/archive contains exactly six newly archived study files:

- `registration.json`;
- `source.json`;
- `cases.json`;
- `failure.json`;
- `life-00.json.gz`;
- `life-01.json.gz`.

There is deliberately **no `results.json`** because the complete panel was
never produced.

## What physically completed

Only the first two lives of block `stable-48-g901` completed and were reduced.

| Arm | Terminal | Steps | Death | Water uptake | Paid energy | Paid vigilance |
| --- | --- | ---: | --- | ---: | ---: | ---: |
| P1.3 reference | dead | 128 | zero_water | 0 | 82.5968 | 102.6040 |
| storage-only `reference_branch_memory_v1` | dead | 128 | zero_water | 0 | 12.4338 | 19.0780 |

Reference executed 73 movement commands, 51 sleeps, one collection and one
meal; all 128 decisions were funded. It mapped 95 new personal cells.

The storage-only control executed 33 movement commands followed by 95 physical
inactivity steps. Its first `NO_PROCESSING_BUDGET` occurred at step 34 and the
remaining 95 steps stayed unfunded. It recorded 32 branch-memory effects,
retaining the fixed capacity of 18. It mapped 38 new personal cells.

Both lives died from dehydration at step 128 and had no positive water uptake.
Both Stage-0 revision receipts are `NO_EXPOSURE` because neither had a prior
positive water uptake.

These two dependent lives are preserved evidence, but they do **not** answer
the three-arm question and must not be promoted into a candidate comparison.

## Where execution stopped

The third planned case was:

`stable-48-g901:reference_frontier_information_v1`.

No complete candidate life was returned and no candidate original life file was
created. During the candidate's decision path, the external full-Competition
observer rejected a paid frontier score with:

`RuntimeError: P5e: forged or inconsistent paid option`.

The runner recorded:

- status `ENGINEERING_FAILURE_NOT_A_DEATH`;
- completed lives: 2;
- no retry: true.

The exception arose inside
`runtime/competition_observer.py::capture_competition`, before the runner
could archive a complete candidate life. It is therefore **not a physical
candidate death** and not evidence that the frontier mechanism failed to
bootstrap.

## Root cause

The historical P5e observer authenticates P1.3 score witnesses using the
identity:

`total_score = base_return + curiosity_bonus_applied + risk_penalty_applied`.

That identity is correct for the historical P1.3 witness schema.

The new frontier-water witness intentionally records:

- `base_return = uninformed_value`;
- `information_value = informed_value - uninformed_value`;
- old curiosity/risk addends = 0;
- `total_score = informed_value`.

Thus a legitimate frontier score obeys:

`total_score = base_return + information_value`.

The observer had not yet been taught this explicit new score schema and rejected
the first such witness. This is an observer compatibility defect, not a license
to weaken its anti-forgery checks.

## Prospective verdict

The preregistered 36-life panel is **INCOMPLETE_ENGINEERING_FAILURE**.

- Candidate mechanistic endpoint: **NOT_EVALUATED**.
- Engineering continuation rule: **NOT_EVALUATED**.
- Survival comparison: **NOT_EVALUATED**.
- Revision comparison: **NOT_EVALUATED**.
- Stage-1 scientific gate: **NOT_EVALUATED**.

The frozen `STOP_AND_ARCHIVE_NO_RETRY_NO_REPLACEMENT` rule is binding. Do not
rerun the failed candidate, resume at case 3, replace its seed, or continue the
remaining cases of this panel.

Although most planned worlds were never physically reached, the **48/49
preregistered panel is closed for this question**. A later development
diagnostic requires a new prospectively allocated panel and a new protocol
after the observer compatibility fix.

## Next engineering action

Fix only the external Competition witness so that it authenticates the
frontier-water score schema without changing cognition or relaxing historical
P1.3/local checks.

The compatibility fix must be software-tested with:

- a valid frontier witness;
- tampered frontier information value;
- nonzero old addends on a frontier score;
- historical P1.3 witness parity;
- local-information witness parity.

No scientific life is required for that fix, and this 48/49 panel must not be
used to test it.

P1.3 remains the reference. I3 remains unregistered. No selection, validation
or reserve condition was opened.
