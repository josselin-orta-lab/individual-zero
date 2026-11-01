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
