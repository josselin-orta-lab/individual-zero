# I3 G2d — Première porte sous sélection : résultat

**Décision préinscrite : `ADOPT_P1_3`.** Exécution unique par bras le 5 novembre 2026 ([protocole](../../G2D_SELECTION_GATE_PREREG.md), commit `628f203`, méthode [ADR-0015](../../../../../docs/decisions/ADR-0015-i3-portes-sous-selection.md)). Données : `P1_1.json`, `P1_2.json`, `P1_3.json`, `g2-*.json`, `reference.json`, [verdict.json](verdict.json).

## Critère principal : 5 génomes sélectionnés par bras, 100 mondes réservés neufs par famille

| Bras | Révision (R), sur 500 | Générale (dev), sur 500 | Total, sur 1 000 | Mondes meilleurs / pires que P1.1 | Test des signes |
| --- | --- | --- | --- | --- | --- |
| P1.1 (base) | 198 | 296 | 494 | — | — |
| P1.2 (croyances + exploration héritable) | 425 | 337 | 762 | 121 / 36 | p = 3 × 10⁻¹² |
| **P1.3 (croyances révisables seules)** | **434** | **346** | **780** | **122 / 15** | **p = 3 × 10⁻²²** |

Les deux candidats se qualifient : supériorité totale, aucune perte par famille (marge 15), planchers remplis (régression G2 passée avec des génomes de génération 0, rejeu exact, 0,82 et 0,83 ms par pas, mêmes mondes). La règle retient le meilleur total : P1.3, qui est aussi le plus simple (un gène de plus que P1.1 au lieu de deux).

## Descriptif

| | P1.1 | P1.2 | P1.3 | Chercheur de référence |
| --- | --- | --- | --- | --- |
| Génome aléatoire par monde : survivants R / dev (sur 100) | 33 / 59 | 64 / 58 | 71 / 60 | 93 / 70 |
| Candidats qui égalent la référence sur les mondes de sélection (49/60) | 0/40 | 2/40 | 4/40 | — |

Le dernier indicateur, prévu par l'ADR-0015 mais omis de l'outil figé, a été calculé **après l'exécution**, à titre descriptif ([descriptive_after.json](descriptive_after.json)).

## Lecture

La révision des croyances de lieu (un gène) explique l'essentiel du gain, et l'exploration en rayons n'ajoute rien une fois les génomes sélectionnés. Le gain apparaît aussi avec des génomes aléatoires en révision (71 contre 33 sur 100), ce qui confirme que la porte G2c avait jugé P1.2 sur sa moyenne et non sur ce que la sélection atteint. Les meilleurs génomes P1.3 approchent le chercheur systématique sans le dépasser : 87 % contre 93 % de survie en révision, 69 % contre 70 % en général.

Ce résultat porte sur des génomes de génération 0 sélectionnés parmi 40, dans deux familles de mondes générées par le laboratoire. Ce n'est ni une lignée, ni une preuve d'apprentissage au sens scientifique du projet.

## Conséquences

- La cognition de référence devient **P1.3** : génome `i3-genome-v3` (30 gènes), croyances de lieu révisées au rythme du gène `belief_rate`, exploration de P1.1.
- P1.2 reste dans la branche `i3/p1.2-variant`.
- Prochaine étape : P2 (familles de mondes pour l'évolution, porte G3 qui les gèle) puis le pilote de lignée P3.
