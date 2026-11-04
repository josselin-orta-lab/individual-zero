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

The Python 3.11/3.12 matrix and checkout at the exact PR HEAD are unchanged. The same full unittest discovery is retained through tools/i2_ci_shards.py and split into exactly two concurrent processes per existing runner, not two additional jobs. All discovered test IDs must be unique; the partition is exhaustive and disjoint by module, preserving test order within each module and separate in-memory test state.

Historical timings are scheduling hints only, NEVER coverage filters. New modules are included automatically. Discovery errors, altered worker membership, test errors, failures, missing cases and skips fail the job. The parent checks the total executed count against full discovery. Compilation, the six repository-boundary tests, independent proposal assessment, source pinning and the 20-minute job timeout remain unchanged.

A local synthetic miniature suite verified successful exhaustive execution, stable partitioning and propagation of intentional test failure. It is NOT an I2 scientific-suite benchmark.

## Measurement and rollback

Do not trigger additional scientific campaigns or rerun GitHub Actions to benchmark this change. Observe only the normal PR run carrying this change. Record the exact PR source SHA, discovered/executed test counts, version-specific job durations and any contention or failures. Compare I2 suite wall times for both Python versions and sum of runner wall times, distinct from concurrent elapsed wall time.

Historical module times imply a theoretical 2-way balance of roughly 522 seconds per process on Python 3.12 BEFORE contention and process overhead. This is a hypothesis, NOT a measured after-time or a guaranteed saving. If the ordinary run reveals process-interference, revert the scheduling change; keep the complete serial suite. Do not interpret an engineering speedup as scientific evidence.

Primary evidence:
- https://github.com/josselin-orta-lab/individual-zero/actions/runs/41740611291
- https://github.com/josselin-orta-lab/individual-zero/issues/946
