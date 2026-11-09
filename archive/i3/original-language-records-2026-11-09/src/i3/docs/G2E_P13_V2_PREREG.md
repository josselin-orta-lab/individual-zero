# I3 G2e — Préinscription : P1.3 contre P1.1 sur le substrat v2, sous sélection

**Déposé avant toute exécution.** Méthode : [ADR-0015](../../../docs/decisions/ADR-0015-i3-portes-sous-selection.md). Plan : [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md), point 1 (P1.3). Code figé : `src/i3/lab/selection_gate_v2.py`. Une seule exécution par bras.

## Question

Sur le **même** substrat physique v2 (cognition financée à l'avance, #1004) dans les deux bras, la révision des croyances de lieu (P1.3, un gène `belief_rate`) améliore-t-elle la survie des génomes sélectionnés, en particulier quand une source se tarit ?

## Bras

| Bras | Commit | Cognition |
| --- | --- | --- |
| Base (P1.1-v2) | commit de cette préinscription (cognition identique à `eb12a0f`, `main`) | Croyances de lieu cumulatives |
| P1.3-v2 | `474259d` (branche `i3/p1.3-v2`) | Croyances révisées au rythme du gène `belief_rate` (génome `i3-genome-v3`, 30 gènes) |

Les gènes communs ont la même valeur dans les deux bras (vérifié pour un génome témoin). Les résultats G2d (physique v1) restent archivés et ne servent à rien ici.

## Protocole

- **Candidats** : `generation_zero(6000)` à `(6039)` ; **sélection** des 5 meilleurs par persistance sur les mondes de développement `dev` 100–129 (horizon 300) et `R` 100–129 (horizon 400).
- **Évaluation** : graines réservées **neuves** 1 000 200 à 1 000 299 des familles `dev` (horizon 300) et `R` (horizon 400), jamais exécutées, sur aucun substrat. Graine de vie 80000 + k. Statistique : survivants parmi les 5 génomes sélectionnés, par monde.
- **Latence de révision** (famille R) : du pas où l'individu boit la dernière gorgée de la source proche (première preuve personnelle de son tarissement) à sa première gorgée à la source lointaine ; non révisée si cela n'arrive jamais.

## Règle de décision (code `decide`)

P1.3-v2 est adopté si :

1. son total sélectionné (sur 1 000) dépasse celui de la base, avec un test des signes exact unilatéral par monde p ≤ 0,05 ;
2. dans chaque famille, il ne perd pas plus de 15 survies sur 500 ;
3. planchers : dans chaque monde G2 (génomes de génération 0), au plus une vie qui boit de moins que la base ; rejeu exact du meilleur génome ; aucun pas en défaut de financement ; mêmes mondes (empreintes) ; temps moyen ≤ 2 ms par pas, garde-fou d'ingénierie sur cette machine (la v2 tourne vers 1 ms en développement).

Sinon : on garde la base. Un échec garde P1.1 sans interdire la construction du pilote de sélection (plan, point 1).

## Descriptif, sans critère

Survie d'un génome aléatoire par monde ; distribution des latences et part des révisions parmi les vies où la source proche a été vidée ; part de pas inactifs faute de financement ; classement des 40 candidats ; sondes de laboratoire (**ni validées ni appariées en coût**, P2) sur les mondes d'évaluation et de sélection.
