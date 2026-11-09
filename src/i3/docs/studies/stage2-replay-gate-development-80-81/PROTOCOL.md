# Stage 2.1 development pilot 80/81: frozen plan (not opened)

**Frozen before the transport code.** Governance: ADR-0017 is **active**. Under
ADR-0019, only the engineering namespace of this plan may run, in a sealed
rehearsal of the exact transport. **No development World 80/81 may open before
an explicit owner lift is recorded in `src/i3/docs/STATUS.md` for the exact
transport fingerprint.**

Machine plan: [PLAN.json](PLAN.json).

## Shape (identical for rehearsal and pilot)

3 families (stable, depletion, pulse) × 2 world indices × 2 genomes × 3 arms =
**36 lives**, 400-step horizon, same-genome blocks. The arms are those of the
frozen protocol [STAGE2_REPLAY_GATE.md](../../STAGE2_REPLAY_GATE.md), lived
path step 1: FIXED (`reference`, P1.3 unchanged), GATE (`p13_replay_gate_v1`)
and ZERO-PERCEIVED-COST (`p13_replay_gate_zero_perceived_cost_v1`).

| Namespace | Cohort | World indices | Genome seeds | Life-seed base |
| --- | --- | --- | --- | --- |
| Scientific (after lift only) | development | 80, 81 | 911, 912 | 7 540 000 |
| Rehearsal | engineering | 2, 3 | 90 011, 90 012 | 9 010 000 |

Life seed = base + 1000 × family position + 10 × index position + genome position.

## Collision search (recorded before freezing)

All development indices declared in plans, protocols and code, or exposed in
archived originals by world name, were collected: 0–5 and 20–69 are used.
Index 70 is excluded for caution: its spec object was generated once in memory,
to read the world-name format; no life ran and no content was read. Indices 80
and 81, genome seeds 911/912 and life-seed base 7 540 000 do not appear
anywhere in the repository.

## Continuation and outputs

The rehearsal passes only if:

- phase G generates all 36 originals;
- phase R reduces them all;
- every structural invariant holds: paid and settled cognition, horizon,
  declared policy, gate summary present iff gate arm, admission ticket bound to
  the exact world and cohort.

The rehearsal reports only pipeline facts (status, counts, digests, invariant
failure counts, time per step), never reduced rows.

The scientific pilot, after a lift, continues on engineering conditions only
and measures GATE's mean replays per sleep step, which sets
RANDOM-EQUAL-MEAN. There are no outcome criteria here: the Stage-2.1 gate
criteria are frozen in the protocol.
