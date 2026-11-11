# Stage 2.1 readout versus subsequent outcome-learning affordability: source-locked software result

**11 November 2026. Engineering software only, not lived science.**
The preregistered protocol is
[READOUT_LEARNING_AFFORDABILITY_SOFTWARE_2026-11-11.md](READOUT_LEARNING_AFFORDABILITY_SOFTWARE_2026-11-11.md),
committed before the experiment at
`75a85b930d5b5295b53c0e5e7d8788d818554adf` on exact baseline
`a6abe6475d393a71b620efc8ece458ac4fac690c`.
Executable candidate final PR head:
`6a4d54e547e8b61ffdb0721603e7d09e0b8caffc`,
[merged #1298](https://github.com/josselin-orta-lab/individual-zero/pull/1298)
as `3d39761222483e5852243ed3817a1728b7ffbef3`.
[Exact-head Actions #42988497425](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42988497425):
**PASS 1088/1088 i3 software tests on each Python 3.11 and 3.12**, plus
both engine and generation control suites (7/7). Previous
[Actions #42988144413](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42988144413)
failed one newly introduced test's incorrect `unittest.mock.patch(module,...)`
signature; changed to `patch.object(module,...)` without
changing any predeclared bodies, scientific hypothesis or native code.

## Frozen four-case complete result

All four are synthetic native five-body tuples with
`midpoint()`, unchanged `BodyLaws()`, action `attendre`,
the same modeled original decision charge
`CognitiveWork(cycles=3,memory_items=12)`.
Only one branch adds the existing proposed passive readout
`CognitiveWork(cycles=6,memory_items=48)`, adding a modeled
**0.1296 energy / 0.30 vigilance**. Both share the same
unmodified native `transition`. The **actual reference
`Mind.prepare_learning` allocator** then decides whether
the next base update could be funded from each synthetic post-action body.
No `Mind.learn`, `World.step`, `World.pay_cognition` or
`run_life` is invoked.

| Frozen condition | Source before-body | Without optional readout | With optional readout | Result |
| --- | --- | --- | --- | --- |
| `energy_boundary` | E=0.56, V=80 | post-action E=0.14760000000000006, next base learning **fundable** | readout admitted; post-action E=0.01800000000000007, next base learning **not fundable** | Positive energy-limited technical divergence |
| `vigilance_boundary` | E=5, V=0.55 | post-action V=0.4, next base learning **fundable** | readout admitted; post-action V=0.10000000000000003, next base learning **not fundable** | Positive vigilance-limited technical divergence |
| `both_funded` | E=5, V=5 | base learning fundable | readout admitted; base learning still fundable | Expected null contrast |
| `optional_denied` | E=0.49, V=80 | post-action E=0.0776, base learning fundable | readout *rejected* for motor-energy reserve; **zero optional charge**, identical post-action body; learning remains fundable | Negative admission control |

**Primary frozen result:** both 2/2 declared energy/vigilance
learning-lost boundary checks PASS. Both positive/negative controls
PASS, 4/4 cases accounted; no post-hoc fixture changes and no
missing/terminal observations. Same original chosen action in all
cases; no extra World stocks, hidden objects or needs supplied.
Full original reference `Mind` buffers/effects/RNG unchanged.

## Interpretation

The pure model demonstrates that protecting the original motor cost
does **not** guarantee protecting sufficient reserves for the next
native outcome-learning allocation. A readout may therefore be
*admissible now* while making the individual's own subsequent
learning unaffordable in the **same tick**. This is a **resource
competition** and *cost-model dependency*, not evidence that i3
currently anticipates this tradeoff or has learned a general
value-of-computation controller.

The test has **no born organism** and no actual `World.step` debit;
these are synthetic affordability computations from unchanged native
laws, not a living first-person prospective forecast or a physical
CPU-to-energy calibration. The readout was not computed; the test only
reserves its declared work and checks the next genuine reference
learning allowance. It neither compares predictive accuracy nor
assigns any fixed physiological objective to Mind. Future proposed
value-of-computation research should count *both current computation
and its possible forgone next outcome-learning work* when evaluating
long-run personal distress. That is a hypothesis for proper
prospective tests, **not a new hard-coded controller rule**.

**Formal boundaries:** `worlds_opened=0`,
`actually_lived_readout_debits=0`, `scientific_lives=0`,
`scientific_verdict=NOT_ISSUED`, no iid ecological sampling,
no source opening, no selection/validation/reserve,
no changed P1.3 policy, no action control, no Stage 2.2
or i3 activation. Issues
[#1276](https://github.com/josselin-orta-lab/individual-zero/issues/1276)
and [#1283](https://github.com/josselin-orta-lab/individual-zero/issues/1283)
remain OPEN. The actual body phase of an eventual lived forecast
continues to be `POST_PAID_LEARNING` PRIMARY and
`IMMEDIATE_POST_WORLD` SECONDARY, per #1296.
