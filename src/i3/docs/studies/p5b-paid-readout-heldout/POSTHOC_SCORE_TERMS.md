# P5b exploratory post-hoc decomposition of actually paid candidate scores

**Status: POST-HOC, HYPOTHESIS-GENERATING ONLY.**
This comparison was planned *after seeing* the preregistered P5b
survival and mechanism results. It is NOT a preregistered primary or
confirmatory test, not a new scientific experiment, and it generated
**zero additional lives**.

## Input and exact computation

The only source is the unchanged [P5b original complete evidence](readout-full.json.gz)
from [first prospective run 42220546984](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42220546984),
raw SHA-256
`98d21bc18d88f26743ae9ca07cc0d966605d14de826b73a91b9d24b675c9a8df`,
canonical SHA-256
`211c2586971bace7cc592488c399202f97d07ddb3be0937eb49d4a47dd4f9473`.
The [independent read-only custodian](independent-custody.json)
verifies all 1152 original experimental identities, 24 fresh
worlds, 288 paired genotype/world/seed groups and billed work
before any score decomposition.

Reproduce this report:

`PYTHONPATH=src python -m i3.lab.p5b_posthoc_terms src/i3/docs/studies/p5b-paid-readout-heldout/readout-full.json.gz`

The source examines the first 12 real-paid decision steps of paired
`full` versus each intervention life. It only compares **the same
actually funded candidate option under an identical five-channel
pre-decision body and before the first different physical action**.
It classifies the observed arithmetic relationship

`final_option_score = base_projected_return + curiosity_risk_bonus`

as score differences involving only projected base return, only
curiosity/risk bonus, or both. Changes in both components that
cancel out to an unchanged total score are recorded separately.
A null and an identical behavior hash remain legitimate evidence.

## Findings from full original P5b evidence

| Paired readout vs `full` | Paid option comparisons with score difference from base only | From bonus only | From both terms | Pairs with at least one bonus-only score change /288 |
| --- | ---: | ---: | ---: | ---: |
| Action-agnostic personal prior | **650** | **4,587** | **837** | **273/288** |
| Zero action-specific prediction | **10,729** | **32** | **8,143** | **4/288** |
| Learned sleep forecast masked | **533** | **0** | **0** | **0/288** |

The modes also respectively produced **79/288**, **288/288**
and **44/288** pairs with at least one base-only score change.
The pair-level flags are **not exclusive**: one experimental pair
can have different candidate comparisons of multiple types.
The option comparison counts are repeated observations within
the same 288 genome/world pairs and **must not be interpreted
as thousands of statistically independent experimental units**.

For the action-agnostic prior, a personally learned
**global body-change estimate** is used for every proposed action.
The large number of bonus-only scoring differences is a concrete
reason why the P5b overall score divergence **cannot be described
as merely changing base predicted values**. Readout uncertainty
and the relevant curiosity/risk terms are part of the choice
mechanism. These counts by themselves do not establish that the
bonus causes the subsequent choice or mortality.

Under zero action-specific prediction, base projected returns
frequently change in paid option comparisons, but the uncertainty
bonus may change too; this is also not a clean one-factor test.
Blinding the learned sleep forecast produced comparatively fewer
matched early score differences and no bonus-only changes on this
sample. This does not refute other sleep or replay effects.

## Verification and next falsifier

[Cross-Python post-hoc audit 42222555975](https://github.com/josselin-orta-lab/individual-zero/actions/runs/42222555975)
passed **167 I3 tests on Python 3.11 and 3.12**, original evidence
custody, source generation boundaries, and reproducibly produced
the counts above with **no new world or life**.

The next independently registered study should intervene on
**one additive term at a time**: preserve the same prepaid
simulation and predicted base return while either retaining
or discarding only the curiosity contribution, and
separately test integrity/risk contribution. It must
track initial selection under matched opportunities,
true realized cost, inactivity and survival, without
training on P5b validation results or inventing cognitive
charges. New held-out validation worlds must be different
from P5b 72–95 (indices >=96) and all earlier studies.
If seeking generalization, use genuinely independent
genetic lineages and ecological families rather than
treating old repeated lives as independent populations.

I1 remains the active engine, I3 unregistered, P4 reserve sealed.
No scientific GO, no causal information-only claim and
no evidence of subjective individuality.
