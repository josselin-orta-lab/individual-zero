# I2 : plan de validation, deux niveaux distincts

**G2 : les tests logiciels synthétiques sont exécutés en CI ciblée.** Le workflow `.github/workflows/i2-proposal-safety.yml` vérifie les suites `tests/i2/test_*.py` sous Python 3.11/3.12, la compilation et le blocage de toute activation I2. Ils ne créent aucune vie et ne représentent pas une preuve scientifique.

## Completed, closed one-shot G1-LAB factorial (2026-11-01)

The owner separately authorized **one** non-living v1-r1 parameter-locked
need/nutrition/aversion study (exact protocol Git blob
`a279067fbfd21f02ee4aa7854509c19f12cfbb62`), not a living G1 or G3
gate. Merged PR #814 contains the opt-in policy and the bounded
`tests/i2/test_g1_lab_need_aversion_v1r1.py` verification; PR #815 records
[all 16 arms and 128 modeled captures](../../../docs/research/studies/i2-g1lab-need-aversion-protocol-2026-11-01/execution-report.md), including null contrasts,
fixed-prior successes, varied synthetic UC and high-energy aversive
abstention. The output comes from researcher-specified deterministic
valuation, **not established natural learning**.

Historical software verification on the exact PR #814 head
`5a8080fc1fe146ff67e391b6d48655689691f46f`: Python 3.11 and
3.12 PASS (the same single protocol, not independent scientific
replications). No new cohort or tuned rerun is permitted under that
authorization. If an unrelated future code change affects this feature,
the narrow regression command is
`python -m unittest discover -s tests/i2 -p 'test_g1_lab_need_aversion_v1r1.py' -v`;
such a software retest does **not** count as a fresh experimental run.
ADR-0008 retires the mandatory external G1 reviewer requirement (#662).
The I2 engine remains unregistered and currently unexecutable; implement
an isolated research-only integrated prototype under #664 without claiming
authenticated M11, scientific GO or automatic activation.

## Invariants logiciels G2 à conserver

1. I2 reste absent du registre actif, sans point d'entrée de naissance.
2. Les observations sont déclarées first-person, chronologiques, sans oracle caché admis.
3. Toute évaluation cognitive doit être facturée en UC **synthétiques**, avec refus du lot impayé.
4. Les intentions persistent dans l'état du banc sans stocker un gagnant moteur.
5. Veto, fraîcheur et scellage terminal synthétiques sont vérifiés en replay.
6. Le journal SQLite v5 demeure **l'unique transaction cognitive** ; anciennes tables et propriétaires concurrents interdits.
7. H2 conserve les tests défavorables, neutres, de rejouage et de non-causalité.
8. Les sources de tests `tests/i2` ne doivent pas contenir de liens symboliques ni importer directement ou dynamiquement un ancien moteur (I0/I1) ou une autre génération. Contrôle AST statique uniquement : les dépendances transitives et chargeurs personnalisés exigent toujours une revue séparée.

Commande locale : `python -m unittest discover -s tests/i2 -p 'test_*.py' -v`.

## Programme scientifique encore NON EXÉCUTÉ

Authentification M11 indépendante, débit du Scheduler vivant, action et conséquence WorldBody réellement appliquées, mortalité irréversible, protections anti-rollback, continuité H2 atomique, études confirmatoires préenregistrées avec contrôles et comparaison sans réutiliser les résultats d'I1. Ces étapes nécessitent une revue G1/G3 distincte. **Aucune naissance, cohorte ni GO scientifique I2 n'est établie.**

## Science-first offline vertical slice (not a born life)

`tests/i2/test_science_first_behavioral_slice.py` couples an experimenter-controlled miniature world to **existing** H2 contrast, paid Competition and the v5 single cognitive SQLite owner. Three hidden consequence regimes (positive, neutral, negative), both training orders, a no-H2 ablation, synthetic UC, veto and omitted-outcome negative checks must be reported. A proposed decision is evaluated only by a research-controller shadow function: **I2 never actuates WorldBody**, cannot see hidden outcomes before learning, and the synthetic evidence port is not M11. Success means a coherent G2 vertical diagnostic, **not** a scientifically valid comparison of autonomous individuals or proof of real causal learning. See [ADR-0002](../../../docs/decisions/ADR-0002-scientific-prototype-first.md).

## Sequential offline shadow, delayed H2 feedback (G2 only)

`tests/i2/test_science_first_sequential_shadow.py` is a fixed four-capture trajectory in the **existing** v5 cognitive SQLite fixture. It compares stable +8 outcomes against a +8 to -8 reversal, each with an equal-UC no-H2 ablation. A research controller supplies the historical and later matched episodes **after each prospective issuance**; feedback committed in cycle t only affects paid Competition advice in cycle t+1, and a cold replay precedes the next capture. Missing observed outcomes must refuse the update.

The separate test-world shadow computes consequences of **proposed advice** without allowing the I2 fixture to actuate anything. Report reversal losses and the adaptation delay, not only eventual correction. The source and issuer are synthetic; this is **not** actual self-directed experience, a living WorldBody, causal identification, authenticated first-person observation, M11 or G3. See [ADR-0002](../../../docs/decisions/ADR-0002-scientific-prototype-first.md). The next science decision is whether this delay and dependence on experimenter-provided matched episodes justify a narrower learning hypothesis, not whether another guard can be added.

## Chosen-only feedback-gap falsification (offline G2, NOT autonomous learning)

`tests/i2/test_science_first_chosen_only_feedback_gap.py` follows only the current v5 advice in **separate research-controller worlds**, then records the outcome of that chosen arm. The baseline follows its own advice under the same regime. No missing counterfactual B episode may be fabricated. Test both stable and abruptly reversed regimes over four cycles with identical synthetic UC accounting, cold SQLite audits and exact evidence recording. Compare to the previous `run_sequence` reference where the experimenter explicitly supplies both heldout matched episodes.

**Predeclared expected limitation:** chosen-only observations cannot form a complete matched pair, so the current H2 `feedback_version` stays zero and advice does not adapt after reversal. The shadow reference with experimenter-provided pairs *can* update, but cannot demonstrate autonomous learning from I2's own chosen consequences. Record reversal losses even when the earlier paired-protocol simulation passes. This is an H2 feasibility/identifiability diagnostic, not evidence for G3 or a reason to pretend that rejected evidence can be learned.

**Next decision under ADR-0002:** review whether to specify a narrowly bounded observational, chosen-outcome learning path with explicit exploration and falsification controls, or revise the H2 question. No new running motor owner, live WorldBody or M11 is authorized by this negative result.

## Chosen-outcome observational adaptation (G2 diagnostic, not G3)

`src/i2/modules/chosen_outcome_study.py` is a **pure, non-persistent** G2 readout from previously recorded, single chosen-arm results. It supplies the already-paid v5 Competition through `ChosenOutcomeValuationStudy` without fabricating an unchosen counterfactual. Its score is deliberately simple and fixed: **last observed net consequence +5**, otherwise explicit prior scores A=3/B=2/C=0. No hidden regime or next consequence enters the current capture. This is NOT the accepted H2 owner, an independently verified subjective record, or a motor policy.

`tests/i2/test_science_first_chosen_outcome_adaptation.py` reports six captures under stable (+8), reversal (+8 then -8), adverse (-8) and recovery (+8/-8/+8) regimes. It compares zero intervention with exactly one research-controller exploration (cycle index 3); the controller follows suggestions otherwise, but I2 never actuates the world. Each arm spends 5 synthetic UC per capture, performs cold SQLite audit and preserves all losses. The intended falsifier is that chosen-only consequences may cause a recommendation change, but a greedy recency readout may fail to rediscover a previously abandoned option, even when the world recovers. A six-cycle test is **not** a preregistered confirmatory science trial or reliable evidence of natural learning. This is an explicit ADR-0002 probe of whether the chosen-only H2 blockage can be escaped with the smallest observational rule; subsequent work should be selected from its failures rather than adding guard layers.

## Experience-only stale-option revisit, no forced exploration (G2 diagnostic)

`tests/i2/test_science_first_chosen_outcome_adaptation.py` now also tests a
**study-only** bounded reconsideration of a *previously sampled* action, without
the research controller forcing an exploratory choice. The existing
`ChosenOutcomeValuationStudy` optionally adds a fixed +9 score if at least
two **other already-observed chosen results** followed its last observation.
The scores still enter the same paid v5 Competition. Untried options get no
imagined outcome or free novelty bonus. This heuristic is authored by the
experimenter; it is not a learned intrinsic exploration drive.

The controller follows the nonmotor preparatory advice in all six captures,
and **then scripts a second action B=eat** before recording its two-step outcome.
This is NOT a freely completed action sequence. Compare to the no-revisit
ablation with identical synthetic UC (5 per capture), stable/reversal/adverse/
recovery regimes and cold reopens. Corrected expected two-step net outcome
totals for revisit versus no-revisit: stable **24/24**, reversal **-32/-24**,
adverse **-40/-32**, recovery **-8/-24**. These include worse outcomes in
two regimes. Invalid/future/replayed chosen evidence is rejected.

This is a developmental G2 test of an *advice-to-consequence-to-later-advice*
chain, NOT motor autonomy: physical interventions remain research-controller
calls, subjective sources are test doubles, the revisit bonus is a fixed
prior assumption, H2 has no living memory, and there is no birth or M11.
No G1/G3/G4-G6 permission or scientific claim follows. Per
[ADR-0003](../../../docs/decisions/ADR-0003-integrated-living-i2-milestone.md),
the next substantive gate is independent G1 review for a minimal living loop,
not continued accumulation of synthetic protection layers.

## Scientific correction: food-action semantics, 1 November 2026

**DRIFT DETECTED: experimental construct validity, not a runtime bug.**
The previous versions of the four `test_science_first_*.py` studies used the
synthetic `C=drink:water` action as the berry-consuming completion and kept
`B=eat:berry_a` as a -2 no-op. This invalidated any interpretation of
those passes as an actual `collect -> eat` causal mechanism. Preserve the
historical PR #777-#782 records, but **do not count their food-learning
conclusions as established**. They were not living or confirmatory science
even before this correction.

The shared `TinyControlledWorld` now uses **A=collect berry** (inventory+1,
step net -2), **B=eat berry** (consume exactly one carried berry; step
net `completion_delta - 2`, or -2 on empty inventory), and **C=drink
water** (step net -2, never consumes a berry or produces nutritional value).
For paired H2 studies, C is the no-preparation control and B is the same
experimenter-commanded completion in both arms. All H2 forecasts and paired
controls use `(preparation=A, alternative=C, completion=B)`; that
triple is distinct, temporally ordered and physically consistent.

The researcher still **forces the later B eating action** in all existing
matched-pair and chosen-outcome two-step trials. The prep-choice is made
via paid Competition and may be followed without intervention, but **the
individual does not independently decide to eat**. In the six-step study
`controller_forced_eating_after_advice=true` exposes this directly.
The simple chosen-only readout offset is reparameterized from +4 to **+5**
**after inspection of the first failing CI** so that the no-preparation
control's observed -4 result remains positive (+1), allowing Competition
to recommend it rather than correctly withholding all nonpositive advice.
This adjustment was made **after seeing test failures**. Thus the fixed
six-capture contrasts are exploratory regression diagnostics and must NOT
be called preregistered or confirmatory. The experimenter-supplied score
and forced eating remain important confounders. No conclusion about general
learning performance or intrinsic valuation is licensed.

Corrected G2 reports are software evidence about *advice for preparations
when eating is scripted*, not proof of autonomous delayed credit,
first-person WorldBody consequences, G3, H2 natural learning or H3
integration. The next real scientific milestone remains an unforced
sequence in an independently reviewed living loop after G1/G3. Avoid
another optimization of fixed bonuses before that review.

## One-action-per-capture unforced G2 falsifier (2026-11-01)

`tests/i2/test_science_first_unforced_action_chain.py` is the shortest
existing-component check of the missing self-completion link exposed by PR #784.
The synthetic cognitive fixture proposes *one* action on each capture, and
the **separate research controller follows exactly that advice** in the
already-existing `TinyControlledWorld`. It never scripts a second `eat`
action, substitutes a recommendation or supplies the unchosen outcome.
A minimal test-world affordance filter exposes `eat` only when an earlier
`collect` has left a berry in inventory. Cognition receives the current
**offered action names only**, not inventory counts, hidden regime, future
consumption result or the research controller's instrumentation.

An outcome affects the observational readout only **after** its action
has been applied and at a *later* capture. The one cognitive SQLite v5 owner
spends synthetic intake, Competition and Action Control UC on every capture.
Compare independently initialized, equally funded **60-UC** research arms:
fixed prior values (no-learning ablation), chosen-only recency valuation,
and optional stale-action revisit. The starting budgets are equal; **actual
UC spending can differ** when advice changes inventory, available candidates
or a tie withholds review. Record actual UC rather than claiming that costs
were identical. Eight deterministic captures, stable, adverse, reversal,
recovery and neutral regimes. The priors A=3 (collect), B=4 (eat),
C=1 (drink), fixed recency offset +5 and stale bonus +9 are
**researcher-authored**; previous +5 scoring was adjusted after seeing
CI failures in PR #784. This is an *exploratory regression probe*, not
a preregistered confirmatory efficacy test.

Expected action traces (A=collect, B=eat, _=no advice), total outcome and
charged synthetic UC (all values remain to be verified by exact-SHA CI):

| Regime | Fixed | Chosen-observational | Stale revisit |
| --- | --- | --- | --- |
| Stable | ABABABAB / +16 / 36 | ABABABAB / +16 / 36 | ABABABAB / +16 / 36 |
| Adverse | ABABABAB / -48 / 36 | ABAAAAAA / -24 / 38 | ABAABAAB / -40 / 38 |
| Reversal | ABABABAB / -32 / 36 | ABABAAAA / -16 / 37 | ABABAABA / -24 / 37 |
| Recovery | ABABABAB / -16 / 36 | ABAAAAAA / -24 / 38 | ABAABBAB / 0 / 37 |
| Neutral | ABABABAB / -16 / 36 | ABA_____ / -6 / 33 | ABA_____ / -6 / 33 |

**Interpretation:** the stable action sequence also occurs in the fixed-prior
ablation, so its apparent success is NOT evidence of learning. Chosen-only
past consequences can suppress a newly harmful eat option, but in a later
recovery can fail to try it again. A fixed revisit heuristic can rediscover
it in recovery but pays extra adverse losses. The neutral condition can
produce ambiguous paid advice and leave berries unconsumed. A withheld
adverse eating outcome causes an extra harmful eating decision: the
consequence existed in the test world but is intentionally absent from
the synthetic evidentiary readout. These are behavioral G2 limitations,
not an individually learned physiological need or a demonstration of H2
delayed credit. The action offer itself includes the experimenter's
rule `eat iff inventory>0`.

**No G3 claim:** the test-world controller actually invokes `intervene`;
the cognitive fixture still has `motor_authority=NONE` and no real
Scheduler, body owner, M11 identity/attestation, birth, mortality or
autonomous multi-goal learning. No real individual acts. A green CI
only says the exploratory test produced the expected software behavior.
The next project action after this bounded falsification is **independent
G1 review** of #662 and #664, then a living G3 implementation when
authorized. Do not respond to this study by inventing another G2 owner
or tuning the post-hoc score to optimize its five regimes.
