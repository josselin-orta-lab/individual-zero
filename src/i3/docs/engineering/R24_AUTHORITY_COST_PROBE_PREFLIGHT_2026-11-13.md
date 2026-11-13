# R2.4: source-frozen authority v3 cost and growth probe, 13 Nov 2026

**Class:** engineering-only, no World/Mind, no scientific cohort, no I3 registration or operating authority. **Parent:** #1339, #1331. **Baseline:** current main v3 request-nonce server from [PR #1365](https://github.com/josselin-orta-lab/individual-zero/pull/1365). Stage 2.1 scientific verdict remains `NOT_ISSUED`.

## Hypothesis, counterexamples and useful endpoints

The loopback-only v3 `AuthorityStore.apply` synchronously commits every accepted request nonce and checks the entire CAS audit chain before each request. Its mutating CAS operations also verify the complete chain after writing. This means host work may grow with the number of historical audit events, even if each CAS is a constant-size update. A green correctness suite alone does not characterize the throughput or WAL footprint needed for long-lived i3.

**H0 (bounded technical):** under source-exact, fresh isolated databases and identical Python workload, increasing a single synthetic engineering claim from 8 through 32 to 80 accepted step pairs should preserve exact sequence/head/terminal and audit/nonce row counts; measured median/p95 step wall time and on-disk size are recorded, not assumed to be constant. **No measured speed regression threshold will serve as a scientific inference or release gate.** We expect an O(total events) audit scan per request from code inspection, but do not infer a universal complexity exponent from three noisy timings.

**Falsifiers:** a step is accepted with the wrong head, a nonterminal final state survives, the CAS audit event count deviates from `1 + 2*n`, the successfully consumed request nonce count deviates from `1 + 3*n`, a reused nonce becomes acceptable while the current DB is retained, a session can advance past its horizon, or any unsafe World/scientific-launch entrypoint is invoked. Existing v3 nonce-replay and full SQLite rollback negative controls must continue to pass.

## Minimal experiment and cost distinctions

- New `i3.lab.engineering_remote_authority_cost_probe` **pure host probe** with local tempfile, one synthetic `make_reservation` claim, one `AuthorityStore` per requested step count, no `Mind`, `World`, physiology, remote network or motor. Commands: `register`, then per step `verify`, `prepare`, `commit` with fresh 128-bit hexadecimal nonces.
- Horizon equals the requested number of steps (allowed 1..100). Intermediate terminal is `OPEN`, last is `CENSORED`; check every signed-CAS shaped response and final `head` vs deterministic digest. The probe does not execute world dynamics or charge cognitive E/V.
- Capture per-step elapsed wall time via `time.perf_counter_ns` with operation-level samples; use median, p95 (nearest-rank), early/late means or medians, plus durable file sizes (SQLite DB/WAL/SHM), count audit and nonce rows, and expected exact counts. Report interpreter, platform and source-readable metadata without claiming deployment attestation.
- Add a focused invariant-oriented unittest including 8/32/80 lengths and no brittle wall-time pass/fail threshold; output JSON rows with a distinctive `R24_AUTHORITY_COST` prefix to the exact-source Python 3.11/3.12 CI logs. A CLI may run 1..100 for further technical profiling. Do not silently disable `_check_audit`, nonce writes or terminal checks for speed.

## Decision criteria

The only `PASS` from this slice can mean **software probe integrity and reproducibility of counts**, not acceptable production latency, independently anchored M11, live genetic value or scientific Stage 2 closure. Use actual measurements to design a future **protected independent monotonic anchor plus bounded-state/checkpoint protocol**; record persistent per-`verify` nonce storage growth and CPU/disk/network/cognition distinction.

**Release blockers unchanged:** no off-host independent administrative principal, protected authority keys, immutable external high-water, backup anti-rollback, full cross-host fault matrix or production throughput evidence. I1 stays active; I3 remains `proposal / NOT_REGISTERED_NOT_EXECUTABLE`; all scientific World/cohort admissions stay false.