# Native I2: recurrence of need after a hidden quality reversal

Issue #906. This is a **new, prospective, exploratory** longitudinal
engineering experiment, declared before the first execution. The previous
32-tick test in merged #910 demonstrated that a resource may change
physically without either individual ever sampling it again. In that run,
both individuals remained well above the critical 10-unit water range.

## Exact locked design before execution

Cross learning OFF/ON with exactly two real physical source worlds:
`stable_useful` (water effect +10 throughout) and `becomes_empty`
(+10 before 12 already committed physical ticks, then 0). This makes
four independently created native SQLite lives, each with a maximum
of **96 paid cycles** in a single born identity. Each has initial
body (energy 85, food 90, water 9, integrity 100), birth temperament
(0, 0.5, 0.3, 0, 0), 1000 UC, no initial food, one water offer at birth,
renewal every 2 committed ticks, zero secondary discovery gain, and sleep
consolidation OFF. The physical access schedule, beginning body and
innate survival reflex are identical in all cells.

Unlike the original 32-tick protocol, this initial water reserve is
deliberately low so that **a physiological need may recur naturally**
within the technical horizon, including after successful early
hydration. Whether it actually does is **an observed endpoint**, not
a mandated choice or guaranteed result. No authored action tape,
forced exploration, intervention at the reversal, future-quality
claim, free UC, new memory owner or hidden reward is permitted.
If a life becomes terminal before the 96-tick limit, stop; never
resurrect, refill the individual, or append a simulated continuation.

## Prospective observables and negative outcomes

Record the complete self-chosen action sequence, paid UC, after/before
body, first capture with critical water (<=10), first actual restorative
drink before the physical change, the first *return* to <=10 after
restoration, the first critical capture after tick 12, first post-change
drink, number of truly nonrestorative post-change drinks, personally
claimed last-resort goal ticks, terminal state, observation length,
and cold replay of the one local owner. These distinctions avoid
mistaking critical thirst at birth for a *recurrence* of thirst.

Primary *identifiability* endpoint: did the changed source have a
physically admitted **post-change drink** so that the individual
could personally observe its new quality? If not, report
`UNOBSERVED_CENSORED`. If observed, compare later actions with
the innate-only control and document whether lived failures
precede any revised intention. The stable-useful world is a control
for physiological decline and repeated offers without a reversal.
Both worlds must be indistinguishable until the first actually
chosen post-reversal drink. Stable-only viability, death, no drink,
unchanged choices, or innate-only matched behavior are valid negative
results. No post hoc threshold tuning to manufacture a success.

This measures **engineered native G2 adaptation**, not independent
scientific evidence of general autonomous learning. It inherits
the same fixed researcher-selected priors, single-site simplified
physical world, no registered living engine and absent independent
M11 attestation. The original #910 outcomes remain unchanged.
Dream/recombination remains deferred in #902.

Verification target: focused
`python -m unittest discover -s tests/i2 -p 'test_native_recurrent_need_reexposure_906.py' -v`
on an exact SHA; then a **single** ordinary I2 PR CI run.
Keep failed or ambiguous outcomes as recorded evidence.

## Feasibility correction before any birth or behavior (3 November 2026)

The first CI on PR #912 (run 41622350498, Python 3.11 and 3.12)
failed **before any individual was created**. Its four subcases were
rejected by `NativePaidI2.create` because the draft had 1200 UC
while the existing native immutable birth contract accepts only
0..1000 UC. Therefore **no quality-reversal or long-life observation
was obtained** from that run. The later KeyError was a downstream
test-harness consequence of the absent births, not another cognition
failure.

Correct the proposed shared UC to 1000 (same as the earlier 32-cycle
longitudinal cohort), *without modifying the native upper bound*,
the physical world, temperament, learning flags or action policy.
Also predeclare separate telemetry for initial critical need versus
a *return* of critical thirst after a restorative drinking event, and
for two personally observed post-change failures. This explicitly
amends the unexecuted design; it is **not** a retroactive scientific
preregistration nor a post-outcome policy tuning. Retain the original
CI failure as provenance rather than silently rewriting history.
