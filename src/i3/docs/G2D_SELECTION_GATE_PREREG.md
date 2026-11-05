# I3 G2d — Préinscription : première porte sous sélection (P1.1, P1.2, P1.3)

**Déposé le 5 novembre 2026, avant toute exécution.** Méthode : [ADR-0015](../../../docs/decisions/ADR-0015-i3-portes-sous-selection.md). Code figé : `src/i3/lab/selection_gate.py` (sélection, évaluation, comparaison, règle de décision). Une seule exécution par bras.

## Bras

| Bras | Commit | Ce qui change par rapport à P1.1 | Gènes |
| --- | --- | --- | --- |
| P1.1 (base) | `49f8747` (cognition identique à `2657f3b`) | — | 29 |
| P1.2 | `24a7ed9` (branche `i3/p1.2-variant`) | Croyances de lieu révisables + exploration héritable (rayons à cap) | 31 |
| P1.3 | `9e160e6` (branche `i3/p1.3-variant`) | Croyances de lieu révisables seulement | 30 |

P1.2 a été rejeté par G2c sur génomes aléatoires ; il est retesté ici **prospectivement**, sur des graines neuves, comme l'autorise l'ADR-0015. Le verdict G2c n'est pas révisé.

## Protocole

- **Candidats** : `generation_zero(6000)` à `(6039)` (K = 40). Les gènes communs ont la même valeur dans les trois bras (vérifié).
- **Sélection** : mondes de développement `dev` 100–129 (horizon 300) et `R` 100–129 (horizon 400) ; les 5 meilleurs par persistance. Les mondes `dev` 100–129 ont déjà servi aux mesures de capacité ; les mondes `R` 100–129 n'ont jamais été exécutés.
- **Évaluation** : graines réservées neuves 1 000 100 à 1 000 199 des familles `dev` (horizon 300) et `R` (horizon 400), jamais exécutées. Pour chaque monde : nombre de génomes sélectionnés qui survivent (0 à 5). Graine de vie 80000 + k.
- **Descriptif** : un génome aléatoire par monde (`generation_zero(70000 + k)`), chercheur systématique de référence, classement complet des 40 candidats.

## Règle de décision (code `decide`)

Un bras candidat **se qualifie** face à P1.1 si :

1. le total sélectionné, toutes familles confondues (sur 1 000), est supérieur à celui de P1.1, avec un test des signes exact unilatéral sur les mondes p ≤ 0,05 ;
2. dans chaque famille, il ne perd pas plus de 15 survies sur 500 ;
3. il passe les planchers : régression G2 avec génomes de génération 0, rejeu exact du meilleur génome sur tous les mondes d'évaluation, ≤ 1 ms par pas, mêmes mondes que la base (empreintes).

Aucun bras qualifié : on garde P1.1. Un seul : il est adopté. Deux : le meilleur total, sauf si l'écart est d'au plus 10 survies, auquel cas on prend celui qui a le moins de gènes (P1.3).
