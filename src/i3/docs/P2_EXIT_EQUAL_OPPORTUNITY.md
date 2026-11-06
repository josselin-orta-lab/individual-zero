# I3 P2 exit decision: equal opportunity, not equal realized work

Status: **methodological contract implemented and software tested**.
Tracking: [#1012](https://github.com/josselin-orta-lab/individual-zero/issues/1012),
[#1002](https://github.com/josselin-orta-lab/individual-zero/issues/1002).

## Decision and falsifiability

The P2 diagnostic found **zero exact work-vector matches in 7,729 individual
ticks** when compared against the development-calibrated fixed-work probe.
Its reference and omniscient oracle are not proven cost-equivalent and are
never adopted as an optimal search ceiling. This negative result is retained
without adjustment.

The P3 controlled experiment compares the lineage selected by survival to an
independent random-parent lineage, **not** an I3 individual to the heuristic
lab reference. Both lineage arms must start each paired life with the same
world snapshot (which includes the same initial body, hidden resources and
physical laws), source bytes, horizon, life seed, genome generation mechanism,
mutation scale, number of reproductive opportunities and fixed simulation
budget. Both pay work via the same `i3-funded-v2` rules.

Different genomes and lived histories can incur different actual cognitive
energy and vigilance costs, which are *phenotypes*, not design-allocated
advantages. **Do not equalize realized work by forcibly charging a weaker mind
for nonexistent computations, or by reimbursing an expensive mind.**
Report real work, dead/censored terminal status, inactivity and survival
alongside fitness. This design supports an equal-*opportunity* lineage
contrast, not proof of equal computation or of causal benefit from learning.

## Software falsifiers

`lab/p2_comparison_contract.py` checks completed individual life manifests
and actual paid energy/vigilance. A declared equal-opportunity pair must:
- have exactly the same initial world identity and snapshot, including
  initial body, physical laws, resources and events;
- have the same physical execution substrate, source content hash,
  life seed and observation horizon;
- be reconciled in both phases, with no unpaid cognitive cost, no pending
  replay and no fictitious censoring or revival.

It deliberately reports the *difference* in realized work rather than
rejecting it. `audit_probe_exact_work` is a separate strict falsifier: it
rejects exact cost-matching claims for incomplete witness prefixes,
different initial world/reserves, unpaid ticks, postmortem learning or
nonidentical actual four-counter decision/learning work.
Even a fully matched receipt does **not** establish identical information
or optimal policy. The existing fixed-tariff reference remains
**descriptive only**.

Tests deliberately inject wrong initial body, different life seed,
unpaid work, truncated traces and postmortem learning. Work receipts now
include actual terminal information for these checks.

## P3 boundary and handoff

`lab/p3_schedule.py` produces only an **unexecuted deterministic schedule**:
four independent populations, three generations, six genotypes per population,
two new lives per genome per ecology, two equal-opportunity arms, 400 steps,
1:1:1 stable/depletion/pulse mix. It publishes 72 distinct selection world
keys, 24 validation world keys and the control/mutation seed scheme without
instantiating selection, validation or reserve worlds. The validated
[protocol draft](P3_PILOT_DRAFT_PROTOCOL.md) explicitly distinguishes
initial parity from realized work. Before P3 runs, freeze the exact
implementation SHA, source and schedule digest; require scientific
preregistration and bounded independent population analysis.

This is a P2 *methodological exit*, not retroactive validation of
the historic oracle or a P3/P4 scientific GO. I3 remains an unregistered
proposal; I1 remains the active generation.
