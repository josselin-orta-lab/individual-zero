# I3 P2: ecological family, separated cohorts and paid probe witnesses

Status: **engineering contract**, not a scientific GO, not P3 or P4.
Tracking: [#1002](https://github.com/josselin-orta-lab/individual-zero/issues/1002).
Substrate: P1.3-v2, with the same real debit order for individual and probes.

## Causal purpose

The future lineage must encounter **changing resource economies**, not simply
more random seeds from one fixed topology. P2 freezes a prospective mixture
before any P3 selection. It makes different ecological mechanisms observable
without introducing innate target preferences or hidden information into I3.

The new code is isolated in `lab/p2_ecologies.py` and does **not** modify
historical `worldgen.py` or the G2/G2b/G2c/G2e seeds or results.

| Evolution ecology | Mechanism | Ecological question |
| --- | --- | --- |
| `stable` | Spatially randomized persistent water, replenishing food | Can an organism persist in repeatable geography? |
| `depletion` | Limited near well that never refills, distant unlimited well | Can behavior revise after the familiar strategy fails? |
| `pulse` | Finite water stocks with externally scheduled drought/recovery events | Can a disposition tolerate recurring environmental disruption? |

The physiological laws, body channels and mortality remain exactly v2. All
names, locations and effects are per-world; the world alone owns hidden effects
and event schedules. `World.capture()` still offers only the body's own
state, inventory and local five-cell geometry. No world family or cohort is
revealed to the mind. The generators are procedural **structural** checks:
positive resource presence and reachable geometry do not prove physiological
feasibility, and one successful heuristic trajectory is only a witness.

P3 evolution mix: **equal weight 1:1:1** between the three mechanisms; horizon
400 physical steps per life, fixed before selection. This is the input ecology
contract, not an authorization or launch of a P3 lineage.

## Condition boundaries

| Condition | Seed range per family | Allowed use |
| --- | --- | --- |
| Development | 2000–2099 | Debug generators, physical validity, cost tariffs |
| Selection | 10000–10399 | P3 fitness and parent selection, no mechanism tuning |
| Validation | 30000–30199 | Frozen-candidate audit, no repeated selection/tuning |
| Reserve | 1200000–1200199 | Locked for a later, separately preregistered P4 held-out procedure |

These ranges are disjoint from G2e (100–129 selection; 1000200–1000299
evaluation). Numeric ranges alone do not create different ecological families.
The tuple (generator protocol, family, seed, cohort) defines a world; file
source SHA plus complete `world_snapshot` hash establishes provenance. The
P2 API **refuses to instantiate reserve worlds**. P4 must independently
preregister its access before any call or analysis.

Never transfer candidate genomes, score summaries, learned maps or hyperparameter
choices from validation/reserve into the earlier stages. Validate only after
selection is frozen. Repeated validation-driven modifications would convert
validation into development and require new quarantined validation worlds.

## Comparator scope and cost accounting

The historical `PROBE_WORK` is far cheaper than an I3 decision. As a result,
historical reference/oracle survival counts are **not** paid ceilings and are
not used to justify P3 choices.

P2 adds an optional work tariff to the existing probes, without changing their
default historical behavior. On each observed physical tick:

1. The external observer supplies the individual's exact prepaid decision and
   post-action work counts from its complete recorded `run_life` trace.
2. The probe reserves and debits the same decision units **before** its action.
   A zero-work inactive tick never gives a free probe action.
3. Post-action work can only execute and debit while alive and if reserves
   suffice. An unaffordable bill is **not** silently treated as paid.
4. The audit records requested/paid work separately for each phase, per-step
   equality, terminal/censoring, life identifiers, full world fingerprint,
   and the compared prefix's energy/vigilance charges.

A completed cost-matched comparison is recognized only when **both** runs
survive the full horizon (censored), all `horizon` steps are comparable and
the full model-work vectors are actually paid. Otherwise it is only a
**partial diagnostic** and explicitly not a fair survival ceiling. No extra
steps are invented when the individual's recorded life ends. This is strict
and conservative; death during either run is a legitimate outcome, not
evidence of algorithmic infeasibility.

**Important limitation:** the replayed tariff varies with a specific
individual's lived work, so the probe's physical affordability can reflect
that schedule. It is an **engineering diagnostic**, not a fully independent,
blind comparator. Before any P3/P4 causal comparison, a fixed tariff/profile
must be calibrated on *development only*, frozen, and applied identically to
all comparison arms; document whether per-step actual bills match it. A
full-knowledge oracle remains an **existential feasibility witness only if
it succeeds**, not an optimal or matched performance ceiling even if paid.
The capture-only searcher is a heuristic comparator, not an optimal searcher.

## Full-horizon diagnostic (after initial P2 integration)

See [P2_COST_AUDIT_RESULTS.md](P2_COST_AUDIT_RESULTS.md): 36 development
lives at 400 ticks yield 31 deaths, 5 censored, 0/7,729 exact matches
between the actual individual work vectors and the static tariff.
The reference pays its full fixed tariff through horizon in only 4/12
worlds, the omniscient probe in 12/12; this does not prove oracle optimality.
An initial pulse-world exception exposed premature exogenous changes;
scheduled world events now apply after the previously admitted action and
before the next capture. All invalid commands still fail transactionally.
The strict cost-equivalence claim remains **false**. This is an adverse
engineering observation, not a scientific GO.

## P2 gates before P3

- Generator replay and source hashes reproduce the same worlds; ecology
  mechanisms differ and every world obeys the actual v2 contract.
- All four cohorts have non-overlapping, enforced roles; reserve cannot be
  instantiated by P2. No historical evaluation cohort is reopened.
- Each probe has funded decision and post-action receipts, no free choice on
  zero-work ticks, explicit unmatched work and observational-only custody.
- Report development audit success/failures and unmatched cost coverage;
  never force matched-comparison status to green by retuning survival.
- Predeclare P3 population count, life-seed schedule, multiple fresh lives
  per genome, mutation-only reproduction, independent replicates, and
  equal-budget random-parent controls **before** running selection.

P2 does not establish a scientifically fair prospective comparator merely
through software tests. I1 remains active. I3 remains an unregistered proposal.

## Independent static tariff for future comparators

`lab/p2_validation.py::calibrate_fixed_tariff` now derives the phase-by-phase
mean `CognitiveWork` counters from **six development lives only** (one
generation-zero genome, two seeds from each ecology, horizon 120).
It rounds each counter to an integer, records the inputs and manifestation
IDs, and produces a SHA-256-sealed `i3-p2-static-tariff-v1` profile.

`run_fixed_tariff_probe` accepts only an unchanged development profile and
subjects every probe to the same decision and post-action bills on every tick.
There is no per-world or per-individual work schedule supplied to this
comparator. It reports exactly which ticks were actually paid and cannot
present an underfunded comparator as fully funded. Its charge is a **fixed
approximation to mean development work**, not exact parity with each
individual's actual variable work. Full scientific cost comparability still
requires reporting the distribution of actual individual work against that
frozen profile, ideally with a matched charging intervention in P3/P4, not
merely a close average.

The diagnostic trace-replay mode remains useful for falsifying any *claim*
that the existing probes already pay an individual's workload. Neither
cost-fixing mode is permitted to use selection, validation or reserve worlds
to calibrate the tariff. A frozen tariff from one source commit must be
persisted with a study protocol; recalculating after observing validation
outcomes would violate the partition.
