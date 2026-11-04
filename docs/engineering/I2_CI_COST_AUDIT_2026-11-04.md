# I2 proposal CI cost audit (4 November 2026)

## Measured baseline, not an estimate

Source: GitHub Actions run 41740611291 for PR #953. Both source-pinned jobs completed under Python 3.11 and 3.12.

| Baseline job | I2 unittest cases | I2 suite wall time | Separate repository boundary tests |
| --- | ---: | ---: | ---: |
| Python 3.11 | 755 | 998.211 s | 6 PASS |
| Python 3.12 | 755 | 1042.675 s | 6 PASS |

The two I2 suites total 2,040.886 seconds (34.01 cumulative minutes). Checkout, setup, static repository checks, compileall and inert assessment are not significant bottlenecks. The 20-minute timeout remains justified by cancellations documented in issue #946.

The slowest complete test modules in the Python 3.12 log were: recurrent-need re-exposure #906 (190 s), ecological exposure gradient #951 (117 s), harmful-food satiety #952 (78 s), and food restock #944 (78 s). Together they occupy approximately 463 seconds, 44% of the suite; the ten slowest occupy about 699 seconds, 67%. These tests create multiple fresh paid I2 lives, simulate 64 to 96 ticks, and cold-audit committed SQLite histories. Do NOT elide lives, share experimental arms, remove cold replay, weaken falsifiers or shorten horizons to accelerate CI.

## Controlled change

The Python 3.11/3.12 matrix and checkout at the exact PR HEAD are unchanged. The same full unittest discovery is retained through tools/i2_ci_shards.py and split into exactly two concurrent processes per existing runner, not two additional jobs. The original discovery contains some repeated unittest IDs. Every **occurrence**, not just every name, is preserved using its index in full discovery; an exhaustive and disjoint partition by module retains the original order within each module and uses separate in-memory worker processes. A worker must rediscover the same complete, ordered ID sequence.

Historical timings are scheduling hints only, NEVER coverage filters. New modules are included automatically. Discovery errors, altered worker membership, test errors, failures, missing cases and skips fail the job. The parent checks the total executed count against full discovery. Compilation, the six repository-boundary tests, independent proposal assessment, source pinning and the 20-minute job timeout remain unchanged.

An initial automatic run on PR #958 failed fast because the first scheduler rejected repeated unittest IDs. The corrected scheduler preserves each occurrence by position; planner regressions and the full two-version matrix passed on the exact following source. The first failure was a CI-orchestration failure, not a scientific-test failure.

## Observed after-time (not the theoretical 522-second target)

The normal PR #958 run [41804656481](https://github.com/josselin-orta-lab/individual-zero/actions/runs/41804656481) validated exact source `364eb301d0ac0cc0a0f9f4edf98d17a5b3aa7f5c`, with both Python jobs PASS. The old runner used serial full discovery and the new runner used full discovery distributed over two processes. Measured elapsed time is from the test step's "Run python" log marker to "I2_CI_FULL_SUITE=PASS"; it is **not** total CPU time.

| Python | Before I2 suite | After I2 suite | Reduction in elapsed suite time | Cases before / after |
| --- | ---: | ---: | ---: | ---: |
| 3.11 | 998.211 s | 314.578 s | 68.5% | 755 / 761 |
| 3.12 | 1042.675 s | 481.813 s | 53.8% | 755 / 761 |
| Sum of two runner suite windows | 2040.886 s | 796.391 s | 61.0% | 1510 / 1522 |

The 3.11 shards ran 391 tests in 300.541 s and 370 tests in 311.378 s. The 3.12 shards ran 391 tests in 463.419 s and 370 in 480.298 s. Each version independently reported **761 discovered, 761 executed, zero errors, failures or skips**, plus all six generation-boundary tests and the inert activation guard PASS. Counts grew because new tests were added; nothing was suppressed. The reduction is in GitHub runner elapsed time, **not** a demonstrated 61% reduction in executed CPU work.

### Final exact-source integration and rollback

After this first passing run, `main` advanced by merging PR #956, adding `tests/i2/test_native_paid_food_harm_divergence_955.py`. Before merging #958, the PR branch must include that test and pass both Python versions at its **new exact merged head**. This single documentation update is bundled with that source synchronization, not committed independently to create a redundant heavy run. Record the final SHA and the standard CI results in PR #958; do not run additional Actions solely to benchmark.

Never shorten simulated lives, discard cold audits, remove repeat test occurrences, or claim new scientific evidence from a scheduling change. If the new exact-head run exposes process interference, revert the sharding and preserve the complete serial suite.

Primary evidence:
- https://github.com/josselin-orta-lab/individual-zero/actions/runs/41740611291
- https://github.com/josselin-orta-lab/individual-zero/issues/946
