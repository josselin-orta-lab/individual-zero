# I3 funded cognition: physical model v2

Scope: issue #1004, within the owner-approved [development plan](DEVELOPMENT_PLAN.md).
Baseline: `57d07cfbcb55ab31969422977acc4ffba1de7f6e`.
I3 remains unregistered; I1 stays active. This is an engineering correction,
not a scientific adoption of P1.3 or a new lineage experiment.

## Causal payment order

`capture -> bounded decision -> debit decision -> physical action/metabolism ->
prepay outcome learning/replay -> execute learned updates -> record final body`.

`CognitiveBudget` is an advance allowance limited to the current energy and
vigilance. A block must fit before it executes; a failed allocation changes
neither the allowance nor a learned product. `World` debits the cumulative bill
from the same initial body before motor effects. A current decision cannot use
energy or vigilance that its future sleep might restore. Motor admission uses
what remains after cognition. Invalid requests raise engineering errors; they
never become a biological death or a selection score.

The modeled units are deliberately explicit and coarse:

- Three decision-cycle allocations cover perception/memory service, option and
  model preparation, and motor-control/outcome bookkeeping. Memory service
  charges declared working slots, including local capture provision and existing
  map/history, effects, tokens, values, accumulators and transition memories.
- Each simulated travel integration chunk costs one simulated-step unit. Each
  innate projection costs eight such units, including the bootstrap projection.
  A partially computed candidate stays paid but supplies no usable score.
- Competition consumes cycles before each iteration. The already-funded control
  block can select the best completed score when no further accumulation fits.
- The base learned update allocates two cycles, sixteen projection units and
  memory service. Each sleep replay additionally allocates sixteen projection
  units and one replay unit. Replay count is bounded before updates by memory,
  the existing maximum of sixteen, and BOTH resource reserves.

The existing tariff values are not tuned for survival. Cycles now include
bookkeeping, not just Competition; this is a change of charged scope as well
as debit ordering. These counters are model allocations, not a claim to meter
every Python instruction. Provisioned blocks are paid even if some internal
branches do less work. Host timing and observer-only hashing are separate.

Candidate evaluation order uses a dedicated deterministic random stream. This
prevents the list's first option (sleep) becoming a privileged default under
truncation, without changing the score formula or consuming the behavioral
random stream. No funding-aware rescue score or optimal budget policy is added.

## Exhaustion is not a rescue policy

If no processing block, complete score or motor command can be funded, no motor
command is emitted (`action: null`, summary `physical_inactivity`). Time and
food/water decay still advance. This is NOT chosen waiting, sleep, rest repair,
free movement, resurrection, or a new terminal cause. A funded complete choice
still goes through ordinary Competition and Action Control; ties alone never
cause inactivity. Sleep remains the existing physiology: no separate sleep
activation energy fee was debited in v1, and none is invented in v2.

At an inactive tick, memory is inaccessible and not serviced. Its stored state
is not reset or used for decisions. This prototype does not model a separate
standby storage-maintenance cost or irreversible physical destruction of stored
memories. In the existing body/world, passive inactivity cannot replenish energy
or vigilance. Do not describe this as a full biological theory of memory decay.

Outcome position tracking is paid by the control allocation and remains separate
from optional learned updates. An unaffordable learned update is skipped, not
executed for free. No outcome learning or replay executes after death. A newborn
with an already-zero vital channel is terminal before any motor action.

## Same-step replay and evidence

After a live action, the runtime reserves the affordable learned-update block
and replay count, immediately debits the post-action body, and only then executes
those updates. The final observed step follows the SAME sequence; its observation
horizon is never used as a signal to skip a bill. A terminal step does not learn.
There is no pending replay queue and no final unpaid replay bill.

Manifest schema is `i3-life-manifest/v2`, execution model `i3-funded-v2`, body
laws `i3-body-laws-v2`, and accounting schema `i3-cognitive-funding/v2`. Historical
v1 body-law payloads are not silently interpreted with v2 ordering.
Each sampled trace records decision and learning phase workloads, reserve states
and exact bills. `evidence_head` binds both phases and the final settlement;
`trace_head` still describes behavior, now under versioned v2 physics.
No audit or full-world manifest is supplied as a perception to the mind.

## Transaction and interpretation boundaries

World transitions are staged. A bad command, invalid bill or failed admission
cannot advance the clock, consume stock or publish scheduled changes. Previously
paid cognition is not rolled back if a later invalid motor request aborts an
engineering run. Such an exception does not produce a valid completed life.

Pure mathematical helpers are not independent runtime/payment authorities. The
funded execution path is `run_life`; arbitrary monkey-patching is not attested.
Old G2/G2b/G2c scripts and laboratory reference probes have NOT been revalidated
as scientific comparators under v2; P2 must review their budgets before use.
Keep original results and preregistration SHAs untouched. A future P1.3 comparison
must use the SAME funded substrate on both arms, not confound belief revision
with this economics change.

## Development-only observations

See [the full paired observations](engineering/funding-v2/observations.json).
Two existing development worlds, life seed 4, no held-out worlds or selection:

| Panel | v1 survivors | v2 survivors |
| --- | --- | --- |
| Four original short fixtures, 100 steps (genome seeds 2, 9) | 4/4 | 4/4 |
| Sixteen longer fixtures, 400 steps (genome seeds 0-7) | 14/16 | 8/16 |

All four short trajectory hashes change; historical parity is no longer an
appropriate v2 requirement. In the long panel, open-field survival changes from
6/8 to 1/8 and corridor survival from 8/8 to 7/8. Four baseline long lives already
had cognitive shortfalls. Across all twenty baseline lives, nine ended with
pending replay. Every v2 life has zero shortfall and zero pending replay.
The adverse survival difference is retained, not tuned away. It cannot be
attributed solely to removal of old deficits: ordering, charged scope and
budget-limited evaluation also change.

Local Python 3.13.5 mean loop time weighted by actual steps, long panel: about
0.573 ms in v1 and 0.957 ms in v2. These are single-machine development timings,
not a portable 1 ms guarantee, hardware-matched scientific superiority test,
or evidence of adaptive learning. Full per-life times and outcomes are included.

Verification: `python -m unittest discover -s tests/i3 -p 'test_*.py' -v`.
The candidate has 62 focused tests, including exact-boundary debit, failed
allocation, transactional failure, passive exhaustion, no postmortem learning,
same-step replay, deterministic evidence and phase-by-phase cost conservation.
The PR records exact tested commits and any full-repository CI results.
