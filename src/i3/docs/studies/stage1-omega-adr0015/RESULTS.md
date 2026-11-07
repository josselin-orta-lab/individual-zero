# Stage 1 omega ADR-0015 gate: final result

Issue #1061. Frozen design:
[STAGE1_OMEGA_ADR0015_GATE.md](../../STAGE1_OMEGA_ADR0015_GATE.md).

**COMPLETE FROZEN CAMPAIGN. SCIENTIFIC VERDICT: FAIL.**

## Immutable execution and custody

The first two execution carriers (#1133, #1134) failed before scientific
exposure. They created no prerelease, selection/validation World or I3 life.

The third carrier #1135 completed the full frozen campaign.

- source baseline before execution-only registration:
  `034349844ced2f3d6ba00efe7a0fdc42e74fbbaa`;
- exact execution source:
  `ca506554e67eddde08e71ba6872df3b50f3ea4be`;
- GitHub Actions run: `42416437088`;
- design SHA-256:
  `e4934b4994bc97043deee9b9760df9fe31481aeb8ed4d0a75715eebc5f5e5d48`;
- runner protocol SHA-256:
  `125d708706bce266abb41446ef577dbe0096ba96d0e7be60169165e327d11944`;
- durable prerelease:
  `i3-stage1-omega-adr0015-ca506554e67e`;
- prerelease target: exact execution source above;
- final prerelease assets: **85**;
- workflow jobs: **47**, zero failed;
- selection shards: **16/16 complete**;
- validation shards: **24/24 complete**;
- no retry, seed replacement, partial reranking, early stopping or horizon
  extension.

Durable release digests:

- protocol manifest:
  `sha256:0ddfafed30bd0655808de1dededa269eb40657a092bd1352b16aab522405e360`;
- selection aggregate:
  `sha256:cf77b669ae8a819b71fcebee176bc1b7db36469bd2eaaa3420bc94f1d68c0b83`;
- validation aggregate:
  `sha256:320a6ba468965a3cd160c614d83a243bc5b1d209db2a9412ab4891505b217ecb`;
- campaign status:
  `sha256:c3fb70db6f9c74b1ffc9284d3a863c6854c153ccca1be066587bc91d876ae10d`;
- campaign asset index:
  `sha256:2f6af15b5bf2939160c1bb82acd8a7ab06afa56d49189dc0729ec110c9a59812`.

The final validation aggregate has internal SHA-256
`3a8559036d05d0770d632f7821b41a2e4ccdd99fff932a474da5037c263d618a`.

Campaign status is `COMPLETE` with scientific verdict
`FAIL_FROZEN_STAGE1_OMEGA_GATE`.

## Frozen gate verdict

| Rule | Frozen requirement | Observed | Verdict |
| --- | --- | --- | --- |
| G1 | candidate family survival no more than 2 below reference | candidate 0 in every family; reference stable 25, depletion 41, pulse 16 | **FAIL** |
| G2 | better complete revision rank in >=7/8 populations, better pooled mean, >=1 reacquisition | candidate worse in 8/8, pooled rank 401.0, 0 reacquisitions | **FAIL** |
| G3 | candidate-selected omega shifts upward in >=7/8 populations, pooled selected > pool and >0 | upward 6/8; pooled shift +0.078089 | **FAIL** |
| G4 | actual omega beats same-genome omega=0 survival in >=7/8 populations and pooled | 8/8 ties, both arms zero survival | **FAIL** |
| G5 | actual omega survival benefit in >=2/3 F0 families | stable/depletion/pulse all difference 0 | **FAIL** |
| G6 | all custody floors | all source/world/observer/cost/replay floors pass | **PASS** |

All six were required. The frozen Stage-1 omega architecture is therefore
rejected.

## Survival

Validation contains 240 main lives per arm.

| F0 family | P1.3 reference | candidate omega | same candidate genomes, omega=0 |
| --- | ---: | ---: | ---: |
| stable | 25 | **0** | 0 |
| depletion | 41 | **0** | 0 |
| pulse | 16 | **0** | 0 |
| **total** | **82** | **0** | **0** |

Candidate survival by population is zero in all 8 populations. Omega-zero
survival is also zero in all 8.

For candidate minus reference on matched validation worlds:

- wins: 0;
- losses: 36;
- ties: 12;
- effective non-tied n: 36;
- descriptive exact two-sided sign-test:
  `2.9103830456733704e-11`.

By family, candidate has zero wins:

- depletion: 15 losses, 1 tie;
- pulse: 11 losses, 5 ties;
- stable: 10 losses, 6 ties.

These sign tests are descriptive. G1 was the prospectively frozen family
non-inferiority rule and fails directly.

## Revision

The complete-rank endpoint assigns horizon+1 = 401 to any life without
successful reacquisition.

Candidate:

- pooled mean complete rank: **401.0**;
- actual `REACQUIRED`: **0**.

Reference:

- pooled mean complete rank: **282.5875**;
- actual `REACQUIRED`: **35**.

Candidate does not beat reference in any population. The
reference-minus-candidate mean-rank differences are negative in **8/8**
populations. The descriptive exact two-sided sign-test is
`0.0078125`, in the direction opposite the candidate gate.

Omega-zero is also 401.0 pooled with zero reacquisition.

Thus the candidate architecture does not merely miss a latency improvement; it
fails to demonstrate reacquisition at all under this validation panel.

## Selection pressure on omega

Across the 8 candidate G0 pools:

- realized pooled pool mean omega: **0.076728253125**;
- pooled selected candidate mean omega: **0.1548177**;
- pooled selection shift: **+0.078089446875**.

Population shifts are positive in six and negative in two:

| Population | Pool mean | Selected mean | Shift |
| ---: | ---: | ---: | ---: |
| 0 | 0.093194 | 0.377469 | +0.284275 |
| 1 | 0.075184 | 0.262146 | +0.186962 |
| 2 | 0.094993 | -0.168652 | **-0.263644** |
| 3 | -0.053767 | 0.277128 | +0.330895 |
| 4 | 0.094399 | 0.548241 | +0.453841 |
| 5 | 0.063364 | -0.414027 | **-0.477391** |
| 6 | 0.043191 | 0.048675 | +0.005485 |
| 7 | 0.203269 | 0.307562 | +0.104293 |

The descriptive sign test is 6 wins / 2 losses,
two-sided `p=0.2890625`.

The pooled shift is upward, but the frozen directional requirement was >=7/8.
G3 therefore fails without reinterpretation.

## Equal-genome omega ablation

The actual-omega candidate and the same selected candidate genomes with
`omega := 0` both produce zero survivors:

- population survival difference: 0 in every population;
- family survival difference: 0 in stable, depletion and pulse;
- population comparison: 8 ties, effective n=0.

This does **not** prove omega has no effect on internal decisions. Earlier
software falsifiers already established that it can change pre-contact values
and actions.

It shows something narrower and more important for this gate: under the selected
live Candidate-F architecture, any omega effect is unable to produce a survival
advantage because both the actual-omega and omega-zero architectures collapse
before the endpoint.

Therefore G4 and G5 fail and the live architecture-level effect of omega is not
supported.

## Cognitive expenditure

Realized validation trajectories:

| Arm | Lived steps | Paid energy / step | Paid vigilance / step | Inactive fraction |
| --- | ---: | ---: | ---: | ---: |
| P1.3 reference | 64,327 | 0.584751 | 0.717250 | 15.80% |
| candidate omega | 30,565 | **2.234941** | **3.139114** | 18.24% |
| candidate omega=0 | 30,610 | **2.226593** | **3.125671** | 18.33% |

The candidate architectures pay roughly four times the reference cognitive
energy/vigilance per lived step on their realized trajectories.

This is **descriptive, not causal mediation**. Different choices and bodily
histories mean these numbers do not establish that computation cost alone
caused the survival collapse.

The omega and omega-zero costs are nearly identical, which is consistent with
omega being only a first-contact expectation rather than the main cost driver.

## Custody

G6 passes completely:

- exact execution source lock: PASS;
- validation world lock: PASS;
- full Competition observer coverage: PASS;
- zero cognitive-shortfall receipts: PASS;
- rank-0 exact replay identity: PASS.

The negative result is therefore not explained by missing receipts, partial
worlds, insufficient cognitive funding or replay nondeterminism.

## Interpretation

**The genomic-omega Candidate-F architecture is rejected under the frozen F0
Stage-1 ADR-0015 gate.**

This result is stronger than the earlier software falsifiers:

- software showed that omega had representational capacity;
- selection showed a modest pooled upward omega shift;
- the full architecture nevertheless lost survival catastrophically;
- omega-zero collapses identically on survival;
- revision collapses completely;
- custody is valid.

The result does **not** justify tuning omega's range, changing the frozen gate,
choosing only the six favorable populations, or adjusting Candidate F against
these exposed validation worlds.

It also does not establish that value of information as a general principle is
wrong. Earlier bounded tests showed genuine paid information value. What fails
here is the **current integrated Candidate-F architecture at the scale and cost
required by the frozen gate**.

## Next scientific question

**DRIFT DETECTED:** do not add another omega transform, local score patch or
Stage-2 budget heuristic to rescue this exposed architecture.

The next bounded question should isolate the catastrophic architecture-level
difference already revealed:

> If P1.3 keeps its ordinary decisions while physically paying the Candidate-F
> information-computation burden, does survival collapse similarly?

The existing `omega=0` ablation does not answer this. It removes the inherited
omega expectation but retains Candidate-F's information scoring, projection and
changed choices.

A future **cost-only reference-choice control** could distinguish:

1. physical cost dominates: P1.3 choices plus matched Candidate-F cognition
   also collapse;
2. policy/change dominates: the cost-only arm remains materially closer to
   reference while Candidate-F collapses;
3. both contribute.

That control must be implemented and falsified in software first, then tested
only on a fresh prospectively allocated development panel. It must never waive
real cognition charges or reuse exposed selection/validation worlds 72..167.

Until such a mechanism-level diagnosis exists:

- P1.3 remains the reference;
- I3 remains unregistered;
- Stage 2 stays blocked;
- no general I3 GO;
- P4 reserve remains sealed.
