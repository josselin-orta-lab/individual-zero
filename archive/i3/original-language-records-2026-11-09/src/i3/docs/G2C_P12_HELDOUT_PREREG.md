# I3 G2c — Préinscription : P1.2 contre P1.1 sur mondes générés réservés

**Déposé le 5 novembre 2026, avant toute exécution des graines réservées.** Protocole `i3-g2c-p12-heldout-v1`, code `src/i3/lab/heldout_p12.py` (exécuteur et verdict). Une seule exécution par version.

## Ce que P1.2 change

1. **Croyances de lieu révisées au rythme d'un gène** (`belief_rate`) : moyenne mobile des observations au lieu d'un cumul ; une source tarie cesse d'être crue.
2. **Exploration héritable** (`reach`) : portée 0 = frontière la plus proche (P1.1) ; portée ≥ 1 = rayons qui s'enfoncent dans l'inconnu, valant le nombre de cases qu'ils révéleraient, avec une identité de cap stable qui donne de la persistance.

Génome `i3-genome-v2` : les deux gènes sont tirés en dernier, donc les génomes v1 et v2 de même graine partagent tous les gènes de v1 (comparaison appariée).

## Développement déclaré (mondes de développement uniquement)

| Mesure | P1.1 | P1.2 |
| --- | --- | --- |
| Famille générée `dev` (graines 0–99), génomes aléatoires | 59/100 | 59/100 |
| Capacité : meilleur de 40 génomes sur 30 mondes `dev` (100–129) | 23/30 | 25/30 |
| Chercheur systématique de référence, mêmes 30 mondes | 22/30 | — |
| `dev-failing-well` : survivants / source lointaine utilisée | 6 / 5 sur 30 | 20 / 18 sur 30 |
| `dev-wide-field` : survivants | 0/30 | 9/30 |
| `dev-far-home` : survivants | 26/30 | 15/30 |

La perte dans `dev-far-home` (couloir) vient des rayons, qui voient de l'inconnu au-delà des bords jamais touchés ; c'est pourquoi l'exploration est rendue héritable plutôt que tranchée.

## Conditions

- **Versions** : P1.1 = commit `2657f3b` ; P1.2 = commit de cette préinscription. Même générateur pour les deux (empreinte vérifiée).
- **Mondes réservés** : graines 1 000 000 à 1 000 099 de la famille `R` (révision de stratégie : source proche finie, source lointaine hors de vue, horizon 400) et de la famille `dev` (horizon 300). La famille `R` a été écrite après l'arrêt du développement ; seul son constructeur a été vérifié sur une graine de développement, sans aucune vie.
- **Génomes** : pour le monde k, `generation_zero(70000 + k)`, graine de vie 80000 + k.

## Critères (tous requis pour adopter P1.2)

- **A. Révision (supériorité)** : dans `R`, plus de survivants avec P1.2 qu'avec P1.1, et test des signes exact unilatéral sur les paires discordantes p ≤ 0,05.
- **B. Généralité (non-infériorité)** : dans `dev`, survivants P1.2 ≥ survivants P1.1 − 5.
- **C. Régression G2** : au moins 8/10 vies qui boivent dans chacun des trois mondes G2.
- **D. Technique** : rejeux identiques ; ≤ 1 ms par pas en moyenne.

Décision : `ADOPT_P1_2` ou `REJECT_P1_2_KEEP_P1_1`.

**Descriptif, sans critère** : survie du chercheur de référence ; survie du meilleur génome de chaque version sélectionné sur les mondes `dev` 100–129 (P1.1 : 6003 ; P1.2 : 6002), évalué sur les mondes réservés.
