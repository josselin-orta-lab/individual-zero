# I2 : plan de validation, deux niveaux distincts

**G2 : les tests logiciels synthétiques sont exécutés en CI ciblée.** Le workflow `.github/workflows/i2-proposal-safety.yml` vérifie les suites `tests/i2/test_*.py` sous Python 3.11/3.12, la compilation et le blocage de toute activation I2. Ils ne créent aucune vie et ne représentent pas une preuve scientifique.

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

`src/i2/modules/chosen_outcome_study.py` is a **pure, non-persistent** G2 readout from previously recorded, single chosen-arm results. It supplies the already-paid v5 Competition through `ChosenOutcomeValuationStudy` without fabricating an unchosen counterfactual. Its score is deliberately simple and fixed: **last observed net consequence +4**, otherwise explicit prior scores A=3/B=2/C=0. No hidden regime or next consequence enters the current capture. This is NOT the accepted H2 owner, an independently verified subjective record, or a motor policy.

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

The controller follows the nonmotor advice in all six captures, then returns
only the outcome of that action for the next capture. Compare to the no-revisit
ablation with identical synthetic UC (5 per capture), stable/reversal/adverse/
recovery regimes and cold reopens. Expected net outcome totals for revisit
versus no-revisit, respectively: stable **36/36**, reversal **-20/-12**,
adverse **-28/-20**, recovery **4/-12**. These include worse outcomes in
two regimes. Invalid/future/replayed chosen evidence is rejected.

This is a developmental G2 test of an *advice-to-consequence-to-later-advice*
chain, NOT motor autonomy: physical interventions remain research-controller
calls, subjective sources are test doubles, the revisit bonus is a fixed
prior assumption, H2 has no living memory, and there is no birth or M11.
No G1/G3/G4-G6 permission or scientific claim follows. Per
[ADR-0003](../../../docs/decisions/ADR-0003-integrated-living-i2-milestone.md),
the next substantive gate is independent G1 review for a minimal living loop,
not continued accumulation of synthetic protection layers.
