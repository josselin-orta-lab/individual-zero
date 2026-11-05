# I3 — Statut d'ingénierie

**PROPOSITION. NON ENREGISTRÉ. AUCUN POINT D'ENTRÉE. AUCUN GO SCIENTIFIQUE.** I1 reste le seul moteur actif.

Décision : [ADR-0014](../../../docs/decisions/ADR-0014-i3-lignee-enjeu-de-soi.md) (accepté le 5 novembre 2026). Spécification : [SPECIFICATION.md](SPECIFICATION.md).

| Phase | État |
| --- | --- |
| P0 Décision | Fait : ADR-0014 accepté, invariant de naissance reformulé |
| P1 Noyau | Implémenté : monde séparé, corps à cinq canaux, monnaie vitale, capacités vulnérables, génome, cognition, rejeu exact |
| G2 Porte | **Franchie** le 5 novembre 2026 : 30/30 vies ont bu, rejeu exact, 0,40 ms par pas ([résultat](studies/g2-first-falsifier/RESULTS.md)). Deux défauts relevés pour P1.1 |
| P1.1 | Prochaine étape : projection de l'énergie vers sa restauration, exploration qui couvre l'espace |
| P2 Mondes | Non commencé |
| P3 Lignée | Non commencé |
| P4 Étude | Non commencé |

Tests : `python -m unittest discover -s tests/i3 -p 'test_*.py' -v`. Une suite verte valide le logiciel au SHA exact, pas un comportement adaptatif.
