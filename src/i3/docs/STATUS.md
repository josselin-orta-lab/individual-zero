# I3 — Statut d'ingénierie

**PROPOSITION. NON ENREGISTRÉ. AUCUN POINT D'ENTRÉE. AUCUN GO SCIENTIFIQUE.** I1 reste le seul moteur actif.

Décision : [ADR-0014](../../../docs/decisions/ADR-0014-i3-lignee-enjeu-de-soi.md) (accepté le 5 novembre 2026). Spécification : [SPECIFICATION.md](SPECIFICATION.md).

| Phase | État |
| --- | --- |
| P0 Décision | Fait : ADR-0014 accepté, invariant de naissance reformulé |
| P1 Noyau | Implémenté : monde séparé, corps à cinq canaux, monnaie vitale, capacités vulnérables, génome, cognition, rejeu exact |
| G2 Porte | **Franchie** le 5 novembre 2026 : 30/30 vies ont bu, rejeu exact, 0,40 ms par pas ([résultat](studies/g2-first-falsifier/RESULTS.md)). Deux défauts relevés pour P1.1 |
| P1.1 | Adopté (porte G2b, [résultat](studies/g2b-p11-heldout/RESULTS.md)) : non inférieur à P1, sans gain mesurable |
| P1.2 | **Rejeté** par la porte G2c ([résultat](studies/g2c-p12-heldout/RESULTS.md)) : révision bien meilleure (69 contre 46, p = 0,0007) mais non-infériorité générale manquée d'une vie. Variante conservée dans la branche `i3/p1.2-variant` |
| Méthode | [ADR-0015](../../../docs/decisions/ADR-0015-i3-portes-sous-selection.md) : les portes jugent une architecture sur ses meilleurs génomes sélectionnés |
| P1.3 | **Adopté** par la porte G2d sous sélection ([résultat](studies/g2d-selection/RESULTS.md)) : 780 survies sur 1 000 contre 494 pour P1.1 (p = 3 × 10⁻²²). Cognition de référence : croyances de lieu révisables, génome `i3-genome-v3` |
| P2 Mondes | Commencé : générateur de familles (`dev`, `R`, `E` à définir), oracle de vivabilité, chercheur de référence |
| P3 Lignée | Non commencé |
| P4 Étude | Non commencé |

Tests : `python -m unittest discover -s tests/i3 -p 'test_*.py' -v`. Une suite verte valide le logiciel au SHA exact, pas un comportement adaptatif.
