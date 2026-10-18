# I1 minimal learning: 32-life final mechanistic audit

**Physical run:** [Actions #39122746545](https://github.com/josselin-orta-lab/individual-zero/actions/runs/39122746545), engine commit `b5b4c14bd92938ce12d7821ed5bc2c13faedea1f`. All **4/4 jobs PASS**, **32/32 mortal WALs** across seeds 301–308, four treatment groups. All groups are analyzed at the source SHA, not the branch's subsequent documentation commits. I0 and main untouched.

| Food gain | Learned TD readable | Initial lives | Dead before step 300 | Alive, censored at 300 | Actual meals | Mean food (observed steps) |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 0 | Yes | 8 | 8 | 0 | 16 | 12.85 |
| 0 | No | 8 | 8 | 0 | 778 | 12.53 |
| 10 | Yes | 8 | 0 | 8 | 28 | 36.81 |
| 10 | No | 8 | 0 | 8 | 66 | 56.37 |

All 16 paired readable/masked trajectories diverge on **step 4**, after at least one real TD update. Access to TD values therefore **causally alters decisions**. But it does **not** demonstrate that I1 learns to feed itself better or survive longer. In the +10 world the TD-readable agent maintains *lower* food reserves; both arms survive to the 300-step observation cutoff. In the 0 world all die; no survival benefit is established.

## Root-cause hypothesis grounded in WAL

For the 0-food / TD-readable arm, every newborn collects on steps 1 and 2, eats at 3 and 4, then **never collects again**. Food inventory reaches zero; all die by step 237. The baseline unlearned `collecter berry_a` is motivated by the eat goal, but its first observed TD reward is **negative** (about -1.6) because physical food and water decrease at every step while collection provides no immediate bodily gain. The candidate is explicitly *learned* in subsequent proposal logs and has negative Q evidence. In the control, TD reads are masked and the actor keeps collecting and consuming.

This is evidence of **poor instrumental credit assignment**: the collection is a necessary prerequisite for a later useful ingestion, but an immediate homeostatic cost is penalized. The data do not demonstrate that the Q of `manger` is correctly or incorrectly learned in the neutral world: after inventory is empty, there are no further eating opportunities. Treating the drop in eating as learned nutritional avoidance would be scientifically incorrect.

## Subsequent controlled action

[Issue #305](https://github.com/josselin-orta-lab/individual-zero/issues/305) defines a prospective controlled diagnosis of delayed credit, with trace-eligibility sensitivity and fully separate new physical-life SHAs. `lambda_e=0.8` is the default fixture; alternative research weights should be predeclared, never silently change canonical I1. A GO requires benefit on later personally available choices relative to read-masked control, preferably replicated with swapped rewards and eventual survival.

**Verdict for this single-resource study: NO-GO for reliable beneficial learning; YES for demonstrable influence of lived TD on decisions.** Deaths retained, survivors explicitly censored, no rollback and no I0 modification.
