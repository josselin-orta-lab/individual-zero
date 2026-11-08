# Stage 1 Candidate-G 56/57: read-only first-contact audit

**POST-HOC REDUCTION OF IMMUTABLE ORIGINALS. ZERO NEW LIVES. NO ENGINE REPLAY.
NO COUNTERFACTUAL SCORE.**

Source: the 36 originals preserved on
`evidence/i3-stage1-candidate-g-56-57-6ce6fbc2025f` (commit
`22d60edeeef09248a7f7786a4b5e284e4b94ce1b`), execution source
`6ce6fbc2025f9f6e6b34b779142f90c10c28a1e0`, Actions run `42477021573`.

Reduction: `src/i3/lab/stage1_candidate_g_56_57_posthoc_first_contact.py`,
run as `python -m i3.lab.stage1_candidate_g_56_57_posthoc_first_contact
<evidence-directory>`. Output: [posthoc-first-contact.json](posthoc-first-contact.json).
Before reading any life, the script checks every digest listed in the archive's
`SHA256.json`, each case's compressed and uncompressed digests, every life
identity, both genome digests and the frozen execution SHA. Its inputs are the
archived behavior summaries and the already-paid option scores recorded by the
P5e full-competition witness. It recomputes nothing.

This note changes neither the frozen continuation verdict
(`CANDIDATE_G_56_57_ENGINEERING_CONTINUATION_FAIL`) nor any rule. 56/57 remain
exposed evidence only.

## Question

[RESULTS.md](RESULTS.md) leaves open why information-active accurate projection
changes behavior without producing reference-level persistence. Candidate-G cut
Candidate-F's bill by about 58% and still drank 16 times, against 196 for P1.3.

The first hypothesis tested here is a **pessimistic projection**. The innate
self-projection extends the drift observed while waiting, with no future eating
or drinking, and #1153 found all 400 projections on the #1146 fixtures reaching
predicted death before step 255. An accurate projection of that future might compress the value
difference between drinking and its alternatives, which the coarse P1.3
projection might preserve by accident.

## Test 1: the pessimistic projection is not supported as the primary cause

**Spread of base values within a decision.** Base value excludes addends.

| Arm, projector | Decisions | Median spread | All options equal (< 1e-9) |
| --- | ---: | ---: | ---: |
| P1.3, reference | 2,195 | 0.2884 | 61 (2.8%) |
| Candidate-G, reference | 1,168 | 0.0017 | 59 (5.1%) |
| Candidate-G, candidate_f | 269 | 0.1331 | 2 (0.7%) |
| Candidate-F, candidate_f | 1,153 | 0.1156 | 43 (3.7%) |

Inside Candidate-G, decisions scored by the accurate projector are not flatter.
The near-flat decisions are the reference-scored ones. The two modes occur in
different states, so this is descriptive, not a projector contrast.

**Where Candidate-G drank.** Its 16 drinks come from two lives, both with
information-active decisions (104 and 37). None of the 8 lives that never
activated the accurate projector drank.

**Drinking before and after first contact.** On-water decisions are those where
`boire` was offered.

- Before the life's first drink, drinking is never valued above the best
  alternative: 0/8 decisions for P1.3, 0/28 for Candidate-G, 0/1 for
  Candidate-F. The maximum gap is exactly 0.0, a tie.
- After first contact, no on-water decision lies below the genome's own water
  threshold, so this side is thin. The two decisions nearest that threshold
  carry the two largest gaps (+0.4778 at 1.7 points above it, +0.3682 at 8.9),
  then gaps shrink toward ±0.02 further away. Once its effect is personally
  known, drinking's value follows need.

Classification: **`PESSIMISTIC_PROJECTION_NOT_SUPPORTED_AS_PRIMARY_CAUSE`**.
This is not a falsification: no projector swap was computed at equal states.

## Finding 1: a perceived unsupported action is valued as an ordinary step

In all 28 pre-contact on-water decisions, Candidate-G's forecast for `boire` is
the generic average step: water −0.4 (passive decay), uncertainty 1.0,
information value 0, no personal drink support. Drinking looks like waiting
with a motor cost.

P1.3 faces the same flat valuation and overcomes it with its designer addend. Witness,
`depletion-57-g901`, decision 1: water 46.78, below the genome's threshold
51.79. Base values of `boire` and `attendre` are identical,
−1.5943354840931943. Curiosity adds 0.2567 to `boire` and 0.0067 to `attendre`.
P1.3 drinks.

| Where water was perceived | P1.3 | Candidate-G |
| --- | --- | --- |
| Blocks with a water option | 7 | 4 |
| First drink after first water option | 1 to 2 decisions later, in all 7 | 23 and 47 decisions later in 2; never in 2 |

The two Candidate-G lives that never drank are `depletion-57`, where water is
offered from decision 0 (water options in 118 and 16 decisions). P1.3 drinks
at step 2 in both and reaches the horizon in both.

**Imagined versus perceived asymmetry.** Witness, Candidate-G
`depletion-57-g901`, decision 3: water 45.98, below threshold, on water.

- `boire`: total −1.39846, forecast water −0.40, information 0.
- best imagined frontier trial `explorer:-1,-1`: total −1.39724, information
  +0.00122.

The individual explores away. The same unknown first drink receives the paid
unsupported-effect prior and an information value when imagined at an unseen
cell, and the generic average-step forecast when water is actually present.

## Finding 2: exploration has almost no value without the designer addend

| Median per life | P1.3 | Candidate-G | Candidate-F |
| --- | ---: | ---: | ---: |
| Sleep | 26.9% | 32.1% | 88.1% |
| Movement | 28.0% | 12.4% | 6.7% |
| Waiting | 11.9% | 30.2% | 2.1% |
| Personally mapped cells | 80.5 | 19.5 | 19.0 |
| Lives with a positive water uptake | 7/12 | 2/12 | 0/12 |
| Mean step time | 1.19 ms | 1.51 ms | 28.46 ms |

All 4,322 P1.3 explorer scores carry a positive curiosity addend. With addends
removed, 28/2,868 Candidate-G explorer scores (1.0%) have positive information
value; Candidate-F has 445/2,294 (19.4%).

In three blocks P1.3 found water (decisions 51, 3 and 3) where Candidate-G never
perceived any: `stable-56-g902`, `pulse-56-g901` and `pulse-56-g902`.
Candidate-G mapped 11, 42 and 12 cells there, against 83, 72 and 97.

## Finding 3: once supported, the information path pays Candidate-F-like costs

| Candidate-G lives | Information-active | Sleep + inactivity | Energy / step | Vigilance / step | Drinks |
| --- | ---: | ---: | ---: | ---: | ---: |
| 8 never-active lives | 0% | 28.0–41.7% | 0.28–0.69 | 0.43–0.98 | 0 |
| `depletion-56-g901` | 16.0% | 42.0% | 1.10 | 1.40 | 4 |
| `stable-56-g901` | 66.2% | 53.5% | 1.48 | 1.96 | 12 |
| `depletion-57-g901` | 97.5% | 90.7% | 2.93 | 4.12 | 0 |
| `depletion-57-g902` | 94.9% | 86.4% | 0.51 | 0.74 | 0 |

The low bill of `depletion-57-g902` reflects unfunded decisions with zero work,
not cheap cognition.

## Two failure modes

- **Unsupported (8/12 lives).** Cognition is P1.3-priced, but exploration and
  first contact have no value. The individual waits and does not find or try
  water.
- **Supported (the two `depletion-57` lives).** Water is perceived at birth but
  not tried, because of the asymmetry above. Personal recurrence then keeps the
  accurate projector on almost every decision. Sleep and inactivity reach
  86–91%, as in Candidate-F, and the individual dies of thirst beside known
  water.

The other two lives drank late and died of starvation with zero food uptakes.

The price of cognition matters in the supported mode and in Candidate-F, not
in the unsupported mode.

## What is and is not established

Established, descriptively, for this archive:

- every pre-contact on-water decision valued drinking at most equal to its best
  alternative, in every arm;
- Candidate-G applies the unsupported-effect prior to an imagined first drink
  and not to a perceived one;
- without addends, exploration value is almost absent;
- persistent information activation coincides with Candidate-F-scale sleep and
  inactivity.

Not established:

- any survival effect of correcting the asymmetry;
- any effect of ω, which Candidate-G never reads;
- any causal claim beyond these 36 lives. There are 12 blocks and two G0
  genomes, and they are engineering fixtures, not independent populations.

The owner's [first-contact decision note](../../STAGE1_FIRST_CONTACT_DECISION.md)
already identified the first-contact blocker on reference-preserving software
paths. This audit observes the same blocker in live development lives and adds
the imagined/perceived asymmetry.

## Expectations recorded before 58/59 is opened

Written at `main` `369012d` (#1165), when the 58/59 protocol was frozen and no
58/59 evidence existed. These are the author's predictions from this audit and
from #1162 to #1164. They are not rules, do not modify the 58/59 protocol, and
must be checked against its results as they stand.

- **First contact.** Without personal support, unified Candidate-H's final
  decision is a complete P1.3 `Mind.decide`, including the curiosity addend
  (#1164). Candidate-H should therefore find and try water far more often than
  Candidate-G, closer to P1.3.
- **Cost.** Once water is personally known, post-contact support is frequent,
  and each supported decision pays a probe plus a complete final decision.
  Candidate-H is expected to spend much more time in that regime than
  Candidate-G, which drank in only 2/12 lives. Its pooled cognitive energy and
  vigilance per lived step are therefore not expected to fall below
  Candidate-G's (rules H5 and H6). Unfunded probes may also rise in depleted
  bodies (rules H3 and H4).
- **Attribution.** If Candidate-H survives better than Candidate-G, the gain
  should be attributed first to P1.3 routes that keep the designer curiosity
  addend, not to stakes-based first contact.

## Handoff

No change follows for the 56/57 verdict, R1–R5, the Candidate-G live path
closure or the P1.3 reference.

**DRIFT DETECTED if any recurrence threshold, activation count, ω value, prior
scale, seed, horizon or ceiling is tuned on 56/57.**

Finding 3 is consistent with #1161, which diagnosed in software that personal
support was being treated as decision relevance. Candidate-H (#1162) now pays a
relevance probe and falls back to a complete paid P1.3 decision for imagined
first contact. Relevance gating removes the policy drift, not the cost: in
#1162 fallback states, combined work averages 503.36 simulated steps against
470.05 for the probe alone.

The asymmetry is addressed by a software-only falsifier draft under the same
relevance discipline, in which imagined and perceived first contact share one
inherited prior:
[STAGE1_SHARED_FIRST_CONTACT_PRIOR.md](../../STAGE1_SHARED_FIRST_CONTACT_PRIOR.md).
The exploration deficit of Finding 2 remains open.
