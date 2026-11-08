# Candidate-G 56/57 DEVELOPMENT pilot: continuation FAIL

Protocol: [PROTOCOL.md](PROTOCOL.md).

**Status: `COMPLETE_DESCRIPTIVE_CANDIDATE_G_DEVELOPMENT_PILOT_NOT_GATE`.**
This was a small DEVELOPMENT engineering pilot, not a Stage-1 scientific gate.
The frozen continuation rule fails unchanged.

## Custody

The panel executed exactly once after Python 3.11/3.12 pre-exposure checks
passed.

- execution source: `6ce6fbc2025f9f6e6b34b779142f90c10c28a1e0`;
- source snapshot SHA-256:
  `0e0ae765cef50342db4f1932cd5141d9de0e577bb2b3f499686e85761b2a0a11`;
- protocol SHA-256:
  `5837c98a9f94b10255e87526a0d4fa4718db09f3a9638cba3f9ff591246ba798`;
- GitHub Actions run: `42477021573`;
- evidence branch:
  `evidence/i3-stage1-candidate-g-56-57-6ce6fbc2025f`;
- workflow artifact: `13616066753`, digest
  `sha256:e6299062f0daffbfa0fbeff355802aaa5348ed02704e7b5532ab5927e729d0b3`;
- 36/36 gzip originals plus `cases.json`, `results.json`,
  `registration.json`, `source.json`, `SHA256.json` and
  `TRANSPORT.json` are preserved.

The earlier transport PR #1158 failed before exposure; its life job was skipped.
56/57 were opened only by the successful one-shot above and are now exposed.
They must never be reused for tuning or replacement.

## Frozen continuation rule

| Rule | Frozen condition | Observed | Verdict |
| --- | --- | --- | --- |
| R1 | Candidate-G has at least one information-active decision | 368 | PASS |
| R2 | Candidate-G also has at least one reference-only decision | 1,213 | PASS |
| R3 | Candidate-G paid energy/lived step < Candidate-F anchor | 0.9161 < 2.1983 | PASS |
| R4 | Candidate-G paid vigilance/lived step < Candidate-F anchor | 1.2723 < 3.1118 | PASS |
| R5 | Candidate-G `NO_PROCESSING_BUDGET` fraction < Candidate-F anchor | **2.8463% > 2.0436%** | **FAIL** |

Frozen verdict:

`CANDIDATE_G_56_57_ENGINEERING_CONTINUATION_FAIL`

R5 is not replaced after exposure. Candidate-G is not authorized to advance to
another live panel, selection, validation, reserve, reference adoption or
Stage 2.

## Pooled descriptive result

| Arm | Lives censored | Lived steps | Energy / step | Vigilance / step | NO_PROCESSING | Inactive | Water uptakes | Food uptakes |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| P1.3 reference | **3/12** | 2,806 | **0.5311** | **0.6596** | 21.7748% | 21.7748% | **196** | **43** |
| no-omega Candidate-G | 0/12 | 1,581 | 0.9161 | 1.2723 | **2.8463%** | **9.1082%** | 16 | 34 |
| rejected Candidate-F cost anchor | 0/12 | 1,468 | 2.1983 | 3.1118 | 2.0436% | 21.4578% | 0 | 0 |

Survival was prospectively excluded from the continuation rule. It remains a
descriptive warning: all 12 Candidate-G lives died, while P1.3 reached the
400-step censoring horizon in 3/12 matched lives.

Candidate-G did achieve the intended conditionality. Its accurate projector was
active on 368/1,581 decisions (23.28%) and the P1.3 projector remained active
on 1,213/1,581 (76.72%). Of all decisions, 227 were supported by personal
recurrence. The candidate produced 28 positive information options.

Relative to Candidate-F, Candidate-G reduces paid energy per lived step by
**58.33%** and vigilance by **59.11%**. This establishes that decision-local
activation materially reduces the physical cost of the accurate projector. It
does not establish useful adaptation.

## Posthoc funding-mode observation, not a revised gate

R5 counts only `NO_PROCESSING_BUDGET`. The complete funding-status composition
shows why its result must not be read as "Candidate-G has more overall cognitive
collapse":

- Candidate-G: 99 `NO_FUNDED_SCORE` + 45 `NO_PROCESSING_BUDGET` =
  **144/1,581 = 9.1082%** non-funded decisions.
- Candidate-F anchor: 285 `NO_FUNDED_SCORE` + 30
  `NO_PROCESSING_BUDGET` = **315/1,468 = 21.4578%** non-funded decisions.

Candidate-G therefore has much less physical inactivity overall, while its
specific processing-budget failure fraction is slightly higher. This is a
posthoc description of failure-mode composition. It **does not** change R5 or
the continuation FAIL.

The distinction is scientifically useful: Candidate-F often fails before a
score can be funded, whereas Candidate-G more often gets through scoring and
later reaches a processing boundary. A future architecture may use this fact
to formulate a new prospective falsifier, but 56/57 cannot be used to tune one.

## Behavioral reading

The cost question and the adaptation question separate cleanly here:

- conditional projection activation is real;
- its physical cost is dramatically below Candidate-F;
- nevertheless Candidate-G is behaviorally weak on this panel: 0/12 censored,
  16 water uptakes and 34 food uptakes, versus P1.3's 3/12 censored, 196 water
  and 43 food uptakes;
- Candidate-F remains rejected and obtains no positive water or food uptakes.

Therefore the immediate Stage-1 problem is no longer simply "make the accurate
projection cheaper." Candidate-G made it much cheaper and still did not approach
reference persistence.

## Handoff

**DRIFT DETECTED if work now tunes recurrence thresholds, activation counts,
world seeds, horizon or R5 on exposed 56/57.**

Close the Candidate-G live path at this point. The next admissible work is
read-only architecture analysis using the preserved evidence, or a new
software-only falsifier on previously established fixtures. It should ask why
information-active accurate projection changes behavior without producing
reference-level persistence, while preserving:

- no genomic omega;
- no imposed drink/eat/explore rule;
- no hidden-world access;
- no free cognition or body reimbursement;
- P1.3 as reference;
- 56/57 as exposed evidence only.

No fresh live panel is authorized by this result.
