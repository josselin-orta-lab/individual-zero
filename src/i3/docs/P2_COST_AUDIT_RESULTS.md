# I3 P2: development charge-panel observation and ecological event correction

**Status:** verified engineering diagnostic; **cost equivalence NOT established**.
No P3 selection, validation, reserve, new architecture selection or scientific GO.

Source (code and tests excluding this write-up):
`9cee1a57788797f8ba4c0376fa26789a413eb248`.
GitHub Actions [run 42178939557](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42178939557):
Python 3.11 and 3.12 each passed **90 I3 tests**, repository boundary check,
and the complete development-only charge panel. Three earlier diagnostic runs remain visible: a passing 120-step
exploratory panel, a failing obsolete test assertion, and a 400-step failure
which exposed the event-order defect. No failure was erased. They have
not been hidden or retrospectively replaced.

## Prior short-horizon preflight (120 steps)

36 development lives, 12 worlds (4 fresh development indices from each of
three ecological families), 3 genotypes (generation-zero seeds 6000–6002).
Observed: 34 censored, 2 dead, 4,290 lived steps, 1,707 inactive steps.
Individual cognitive shortfall 0; pending replay 0; 0 exact-vector matches
to the static mean tariff. The capture-only reference and omniscient probe
could each pay their prescribed fixed tariff over 120 ticks in all 12 worlds.
This early run is a preflight, **not** a substitute for horizon 400.

## Corrected full evolution horizon (400 steps)

The same 36 development cases, with **no candidate selection and no reserved
seed opened**, under P1.3-v2 and the unchanged five-channel body laws:

| Observable | Measured |
| --- | ---: |
| Worlds (4 indices × 3 families) | 12 |
| Individual lives (3 genomes per world) | 36 |
| Censored alive at horizon | **5 / 36** |
| Deaths | **31 / 36** |
| Total actual lived steps | **7,729** |
| Physical inactivity steps | **3,483 / 7,729 (45.06%)** |
| Funding shortfall steps | **0** |
| Pending replay debt | **0** |
| Exact (decision, learning) work-vector matches to static tariff | **0 / 7,729** |
| Capture-only reference fully funded through horizon | **4 / 12 worlds** |
| Full-world greedy oracle fully funded through horizon | **12 / 12 worlds** |

Dead lives by family: `stable` 11/12, `depletion` 9/12,
`pulse` 11/12. The relative difference below is
`(individual actual charged total - static model charge for the SAME
number of lived steps) / static model charge`, averaged over the 12
individual lives in each family. These averages are **not** CPU time,
not a confidence interval and not a measurement of adaptive intelligence.

| Ecology | Mean energy difference | Mean vigilance difference |
| --- | ---: | ---: |
| Stable | -48.07% | -51.86% |
| Depletion | -21.51% | -28.67% |
| Pulse | -63.42% | -64.73% |

The individual's cognitive work is strongly history-dependent, and physical
inactivity contributes many zero-work ticks. A static fixed-work reference can
pay all of its *own* charges and still be much more costly than the individual.
Zero exact-vector matches is a strong falsifier of a **strict per-step
equivalence** claim, not a failure of strict debit accounting.

Python 3.11 and 3.12 report the same counts and cost gaps. The audit hash and
profile hash differ across Python versions because life manifests bind
interpreter/source-execution provenance. Do not misreport those whole-evidence
digests as a cross-Python byte-identical attestation.

## Dynamic-world correction (P2)

During the 400-step probe sweep, a scheduled resource withdrawal could execute
between an individual's last `capture()` and its already-chosen `boire`.
`World.step` then raised `ValueError: no water here` instead of producing a
biological tick. That was a **software/environment boundary failure**, not a
mortality or a valid selection observation.

Corrected ordering:
`capture current world -> fund decision -> commit action/metabolism -> natural
restock -> exogenous scheduled changes -> next capture`.
A changing external source is therefore first visible in the following
observation; an action valid at the current capture cannot be invalidated
retroactively by that same tick's scheduled event. Invalid actions still
rollback atomically; tests cover water depletion/replenishment, changes to
token effects, and invalid action rollback. No rescue, world-fact perception
or alteration to energy/vigilance pricing was introduced. The original G2e
worlds did not use P2's pulse scheduler; historical evidence remains intact.

## Interpretation and honest handoff

1. **P2 software readiness**: three distinct ecological mechanisms, locked
   disjoint cohorts, reproducible generators, original I3 test suite and
   world/event tests pass. The paid-probe cost audit is functioning.
2. **P2 cost-equivalence gate**: **FAIL / UNRESOLVED**. Neither the static
   model tariff nor full-knowledge oracle is a scientifically equal-cost
   comparator. The oracle's successful full run only witnesses that a particular
   full-information policy can run and pay **its own** prescribed work; it
   does not prove optimality or that another policy could pay the same bill.
   The reference searcher is a nonoptimal capture-only heuristic.
3. **P3 selection**: **NOT_RUN**. A concrete draft pilot is in
   [P3_PILOT_DRAFT_PROTOCOL.md](P3_PILOT_DRAFT_PROTOCOL.md) but remains
   not authorized and not preregistered as a launched study. Before P3,
   explicitly decide the scientific comparator standard. A useful design
   might compare multiple *paid* controls with the same energy/vigilance
   allowance envelope and independently record their realized work, rather
   than assert identical work at every tick. That alternative needs its own
   prospective, frozen protocol and test.
4. **Reserved cohorts:** no selection, validation or P4-held-out world was
   instantiated by this diagnostic. Seed family and horizon definitions were
   not altered in response to survival.

No threshold has been tuned to make this result pass. Preserve null and
adverse observations. I1 remains the active generation; I3 is an unregistered
proposal.
