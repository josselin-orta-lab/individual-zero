# R2.4: measured CAS v3 host cost and journal growth, no-World source-exact results

**Date:** 13 November 2026. **Outcome:** `R24_AUTHORITY_COST_PROBE_SOFTWARE_PASS` (instrumentation and exact invariants). **Operational throughput / independently anchored M11:** `NOT_ATTESTED`. **Scientific Stage 2.1:** `NOT_ISSUED`, general `HOLD_NO_VERDICT`. No scientific World, new life, experimental cohort, engine registration, I1 migration or cognition policy change.

## Source custody and boundaries

- Frozen [preflight](R24_AUTHORITY_COST_PROBE_PREFLIGHT_2026-11-13.md) first committed `a26f0cd51f444215b981fe0529277d3df16c5c29` **before** the probe implementation.
- [PR #1367](https://github.com/josselin-orta-lab/individual-zero/pull/1367), exact tested head `80a283dfe790a582508dffac279865da0239fd14`, squash merged to `main` `5c92fb5b8ed29869e7f2f990f772d8ab45992415`. Source is [engineering_remote_authority_cost_probe.py](../../lab/engineering_remote_authority_cost_probe.py); [tests](../../../../tests/i3/test_engineering_remote_authority_cost_probe.py).
- Exact-source [Actions #43418531046](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43418531046): **SUCCESS**, 1,323 / 1,323 I3 software tests on Python 3.11 (job `131862514502`, 130.963 s) and 1,323 / 1,323 on Python 3.12 (job `131862514858`, 201.708 s), generation contracts PASS and navigation guard PASS. The historical 1,320 tests remain green; 3 new probe tests passed in each run. No scientific jobs were executed.
- This report was written *after* the CI-tested code merge; its publication does not retroactively place this document inside the tested source head.

## Technical setup and what was actually measured

Each isolated run creates a new SQLite CAS authority v3, using a synthetic `make_reservation` engineering claim with exactly one `register`, then `verify`, `prepare`, `commit` for each of 8, 32 or 80 **CAS-only** steps. There is **no** Mind, World, motor, body, learning, network round trip or external storage. Every request uses a distinct accepted nonce. The final committed state must be `CENSORED`, with the exact previously prepared intent, sequence and head. The probe leaves the real authority's full-chain checks and nonce writes enabled.

Counters verified on **both** Python versions:

| CAS steps (`n`) | CAS audit events `1+2n` | Successfully accepted nonce rows `1+3n` | SQLite DB + WAL + SHM observed |
| ---: | ---: | ---: | ---: |
| 8 | 17 | 25 | 49,152 bytes (48 KiB) |
| 32 | 65 | 97 | 110,592 bytes (108 KiB) |
| 80 | 161 | 241 | 237,568 bytes (232 KiB) |

The exact sequence, final head, two journals and terminal state passed their assertions. The `verify` remains free of *motor/CAS audit* append but **does write a nonce row**. Sizes are snapshot observations after the in-process run and closure, not byte-per-step universal laws. No accepted nonce history is pruned.

## Python 3.11 CI host timings (Linux, Python 3.11.18)

| Steps | Median CAS-only three-command step | p95 | Median first quarter | Median last quarter |
| ---: | ---: | ---: | ---: | ---: |
| 8 | 5.383 ms | 23.959 ms | 4.899 ms | 14.951 ms |
| 32 | 7.577 ms | 60.032 ms | 5.787 ms | 10.151 ms |
| 80 | 11.606 ms | 23.372 ms | 6.451 ms | 15.417 ms |

## Python 3.12 CI host timings (Linux, Python 3.12.16)

| Steps | Median CAS-only three-command step | p95 | Median first quarter | Median last quarter |
| ---: | ---: | ---: | ---: | ---: |
| 8 | 6.841 ms | 10.339 ms | 5.685 ms | 8.188 ms |
| 32 | 9.664 ms | 14.273 ms | 6.698 ms | 12.071 ms |
| 80 | 14.739 ms | 22.145 ms | 8.055 ms | 21.386 ms |

These numbers come from a *single run per length and interpreter on shared CI hardware*. They are noisy, hardware-specific wall-clock readings. They neither prove a precise time-complexity exponent nor permit a universal latency limit. The source's repeated `_check_audit` full-history scan gives an architectural reason to expect growth of cumulative work, while the actual early/late samples corroborate a risk worth instrumenting. No power/energy/vigilance tariff was measured or inferred, and the label `cas_step_host_only` is deliberately distinct from bodily paid cognition.

## Decision, remaining falsifiers and next engineering gate

**ACCEPT:** the probe's count/identity/terminal invariants and source-specific observability, not a production throughput target. **REMAINING BLOCKERS:** (1) protected, independently administered off-host monotonic authority with attested source/writer identity and key custody, (2) full network, backup, partial/full rollback and crash/partition matrix with explicit irreversible STOP semantics, (3) long-life CPU, nonce growth, disk/WAL and network-latency profiles under actual separate host privilege and storage, (4) a safe checkpoint design.

An O(1)-amortized append / checkpoint fast path is **not authorized merely by these timings**. It must preserve independently anchored high-water, source/identity, terminal, audit and nonce anti-replay evidence, and must survive corrupt/missing/rollbackable checkpoints. No automatic removal of the full-history validator or accepted nonce rows simply for speed. First freeze the checkpoint/anchor trust model and compare to v3 under adversarial exact-source tests; then consider a **separate** runtime release PR.

**Unchanged:** I3 reference / I1 active, `engine.status=proposal`, `activation=NOT_REGISTERED_NOT_EXECUTABLE`, no runtime entrypoints, P1.3 funded-v2 and Stage 2.1 scientific `NOT_ISSUED`. All source/index authorizations and scientific World/cohort flags remain false. The earlier [full rollback negative control](R24_DURABLE_REQUEST_NONCE_RESULTS_2026-11-13.md) still proves `FAIL_INDEPENDENT_M11` for a coherent rollback of authority SQLite plus its nonce history.

**Issues:** [#1339](https://github.com/josselin-orta-lab/individual-zero/issues/1339) and [#1331](https://github.com/josselin-orta-lab/individual-zero/issues/1331) remain OPEN.
