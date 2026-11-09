# I3 G2c — P1.2 contre P1.1 sur mondes réservés : résultat

**Décision préinscrite : `REJECT_P1_2_KEEP_P1_1`.** Le critère B (non-infériorité sur les mondes généraux) échoue d'une vie. Exécution unique le 5 novembre 2026 ([protocole](../../G2C_P12_HELDOUT_PREREG.md), commit `d45809d`). Données : [p11.json](p11.json), [p12.json](p12.json), [g2-regression-p12.json](g2-regression-p12.json), [verdict.json](verdict.json).

## Critères

| Critère | Résultat | Requis | Rempli |
| --- | --- | --- | --- |
| A. Révision de stratégie (famille R, 100 mondes) | 69 survivants P1.2 contre 46 P1.1 ; paires discordantes 36 contre 13 ; p = 0,0007 | P1.2 > P1.1 et p ≤ 0,05 | oui |
| B. Mondes généraux (famille dev, 100 mondes) | 58 contre 64 | ≥ 59 | **non** |
| C. Régression G2 | 8/10, 10/10, 10/10 boivent | ≥ 8/10 chacun | oui |
| D. Technique | rejeux identiques ; 0,85 ms par pas | ≤ 1 ms | oui |

## Descriptif

| | Famille R (révision) | Famille dev (générale) |
| --- | --- | --- |
| Chercheur systématique de référence | 90/100 | 70/100 |
| Source lointaine utilisée, P1.1 / P1.2 | 45 / 70 | — |
| Meilleur génome sélectionné sur les mondes de développement, P1.1 / P1.2 | — | 66 / 73 |

## Lecture

P1.2 améliore fortement la révision de stratégie et, sous sélection, sa meilleure version dépasse P1.1 et le chercheur de référence. Mais avec des génomes de génération 0 tirés au hasard, elle est un peu moins bonne en général (6 vies sur 100, différence non significative dans un sens comme dans l'autre). Les deux changements (croyances révisables, exploration en rayons) ont été testés ensemble : ce protocole ne permet pas de savoir lequel coûte en général.

## Conséquences

- La cognition de référence reste **P1.1**. Le code P1.2 est conservé dans la branche `i3/p1.2-variant`.
- Les outils de laboratoire (générateur de familles, sondes, exécuteur G2c) sont conservés.
- Hypothèses nouvelles, issues de ce résultat et à tester **prospectivement** sur des graines réservées neuves (≥ 1 000 100), jamais en rattrapage de G2c : (1) les croyances révisables seules améliorent la révision sans coût général ; (2) une architecture se juge sous sélection, ce qu'il faut préinscrire comme tel au lieu d'utiliser des génomes aléatoires.
