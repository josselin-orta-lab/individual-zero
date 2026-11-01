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
