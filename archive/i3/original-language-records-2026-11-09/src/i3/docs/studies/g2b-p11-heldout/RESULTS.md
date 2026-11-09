# I3 G2b — P1.1 contre P1 sur mondes réservés : résultat

**Décision préinscrite : `ADOPT_P1_1`.** Exécution unique le 5 novembre 2026 ([protocole](../../G2B_P11_HELDOUT_PREREG.md), commit `d88fc3d`). Données : [p1.json](p1.json), [p11.json](p11.json), [g2-regression-p11.json](g2-regression-p11.json), [verdict.json](verdict.json).

## Critères

| Monde (30 génomes, 400 pas) | Ont bu P1 / P1.1 | Survivants P1 / P1.1 | Morts de soif après avoir bu P1 / P1.1 | Source lointaine utilisée P1 / P1.1 |
| --- | --- | --- | --- | --- |
| H1 source cachée (eau à 4 cases, hors de vue) | 9 / 9 | 1 / 0 | 0 / 0 | — |
| H2 aller-retour (eau au départ, nourriture à 10 cases) | 30 / 29 | 29 / 28 | 1 / 0 | — |
| H3 source tarie (A finie, B à 14 cases) | 30 / 30 | 3 / 2 | 15 / 16 | 3 / 1 |

Non-infériorité (marge 3) remplie dans les trois mondes ; défaut ciblé en H2 non aggravé (1 → 0) ; régression G2 passée (10/10 boivent dans chaque monde ; survivants *foraging* 7/10 contre 9/10 avec P1) ; rejeux identiques ; 0,56 ms par pas.

## Ce que cela veut dire

**P1.1 ne change rien de mesurable.** Les écarts entre versions sont de une à deux vies sur trente, dans les deux sens. La correction est adoptée parce qu'elle est juste sur le principe et non inférieure, pas parce qu'elle améliore la survie.

**Le défaut dominant est la découverte de ce qui est hors de vue.** Avec l'eau à 4 cases dans H1, seuls 9 individus sur 30 la trouvent, et 29 à 30 meurent avant 400 pas (médiane 113). Dans H3, presque tous boivent à la source voisine, mais quand elle se tarit, 1 à 3 seulement trouvent la seconde : la **révision de stratégie**, défi central de l'ADR-0013, échoue. Le retour vers une source connue (H2), lui, fonctionne : 28 à 29 survivants sur 30.

## Conséquence pour la suite

Aucune lignée ne doit être lancée tant que la recherche dans l'inconnu reste à ce niveau : la sélection ne trierait que la chance. Prochaine étape **P1.2**, sur mondes de développement uniquement :

1. Mesurer le plafond atteignable avec cette perception et cette économie d'énergie, grâce à un chercheur de référence de laboratoire (balayage systématique, sans oracle), pour distinguer un défaut de stratégie d'un monde infaisable.
2. Concevoir une exploration qui couvre l'espace, et rendre ses réglages génériques (persistance de cap, rayon de recherche autour de l'origine) héritables, pour que la lignée puisse les sélectionner.
3. Vérifier sur de **nouveaux** mondes réservés ; H1 à H3 ne servent plus au réglage.
