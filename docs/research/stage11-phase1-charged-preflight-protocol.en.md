# Stage 11: Phase-1 Planning ownership correction after charged-preflight v2

**Registered 2026-10-11 before new Phase-1 changes or CI.** This supersedes the *phase placement* proposal of [the v2 charge-first public protocol](stage11-geographic-charge-before-consult-protocol.en.md), not its observed results or code SHA. No Stage9 held-out or scientific GO is authorized.

## Newly identified normative concern

The English v1.2.1 specification's DC-11 canonical table (near §22.4) assigns Phase 0 to **Scheduler freeze and Global Modulation**, Phase 1 to Exploration and then Planning as independent producers, and Phase 3 to Competition with explicitly declared service calls to Exploration. The v2 software correction charged the early geographical Planning optimization correctly but executed it from a Phase-0 Global Modulation hook. That solves unpaid lookup, but does not cleanly honor the component-phase boundary. The successful v2 CI record remains historical, not normative phase-order sign-off.

## Narrow architectural correction (v3)

- Prepare an immutable read-only *unfiltered* geographical frontier from exactly the current Perception capture and **pre-Phase-1** Exploration physical visits. At most four adjacent directions; do not cap before applying known interdictions. Never consult Action Control in Phase 0.
- In **Phase-1 Planning**, when ordinary upstream cognitive budget and a preceding S_t are available, charge 1 UC to Planning for `geographic_admissibility_preflight` **before** the canonical Action Control read-only query. If refused, report `incomplete_budget` once and do not publish a new geographical option.
- The same Planning producer removes only `INADMISSIBLE` directions, retains `INDETERMINATE`, then applies the configured `max_targets_per_cycle` cap before `planning_build`. No raw Exploration output produced during Phase 1 may be reread by Planning.
- The **Phase-1 Exploration producer** only records genuine Perception/causal observations and leaves physical visit ownership intact. It does not declare a target that Planning has not yet funded/filtered.
- In **Phase-3 Competition**, which normatively permits service calls to Exploration, register the already Phase-1-produced/funded target references with Exploration's owner-local `freeze_targets`, only if no budget degradation occurred. This is not causal evidence, new safety knowledge or a same-phase producer output read. Then perform the already-existing Competition registration and intrinsic evaluation path.
- Demand-driven v4 early check still skips UC only when no raw Perception-grounded new frontier; known-lethal-only candidate must still be queried and barred. Historical Stage9/default geography-OFF, all safety categories, final veto, κ, Equipment and Stage9 evidence are unchanged.

## Tests and reporting

Re-run the unit suite once with targeted assertions proving (a) 0 Planning UC implies no early preflight query, (b) accepted Planning charge precedes an early Action Control query **within Phase-1 Planning**, not Phase 0, (c) bounded one-target known-lethal north still exposes an alternative, (d) no stale offered target survives Planning rejection or a rollback, (e) all 6 public v4 map cases preserve physical custody and known-lethal avoidance, (f) exact reexecution and owner snapshots remain valid, and (g) old v2 CI plus earlier v1/v4 experiment hash receipts are not silently rewritten.

New code/diagnostic identifiers must reflect this phase correction. Avoid full Goldens and Stage9 held-out.

**Status prior to run: NOT VALIDATED. Stage11 IN PROGRESS; Stage9 scientific NO-GO.**
