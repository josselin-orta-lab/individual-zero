# A2.19 : révision épistémique non destructive après un déplacement passif perceptible

**Préenregistrement avant code A2.19**, 14 octobre 2026. Base `main 1c429382cecb83ac437c4afd104b55bc0206c712`, issue #110. A2.18 est intégrée ; MVP v1.3.1 inchangé. Stage12 PARTIAL.

## Hypothèse et restriction

Une observation ultérieure de déplacement corporel malgré une commande `attendre` est une preuve vécue que **la position peut varier sans commande de déplacement**. Cela justifie de réduire la certitude d'une attribution antérieure `self` à `unknown`, mais **ne prouve pas** que le déplacement initial était extérieur. Il ne faut jamais réécrire le reçu initial ni transmettre les étiquettes externes à la sonde. Une même révision peut toucher à tort une action initialement réussie. C'est précisément le coût à mesurer.

## Matrice prospective et interventions

**8 seeds physiques 101–108 × 2 causalités initiales × 2 suites = 32 mondes et 64 transitions `WorldBody.apply`** (une commande `se_deplacer east` puis une commande `attendre`). Première causalité : mouvement réellement exécuté ou échec forcé suivi d'une relocalisation extérieure confondue. Première attribution de `GoalAgencyService` : `self`, sous capture identique dans les deux mondes appariés. Deuxième expérience : `attendre` avec maintien de la position (témoin) ou relocalisation externe du corps **après** la transition d'attente, **avant** la capture t3.

La **sonde candidate hors-ligne** reçoit exclusivement : le premier jugement et son identifiant, les captures autorisées à t2 et t3, la commande réellement préengagée `attendre`, la référence de ce nouveau reçu perceptif. Elle ne reçoit ni `WorldBody.apply.effects`, ni action-failure schedule, ni étiquette causalité initiale, ni `set_position` ni vérité du banc. Règle prospective : sous `attendre`, déplacement visible t2→t3 conduit à un **événement append-only** `reconsider_to_unknown` qui cite le premier jugement mais ne l'écrase jamais. Sinon `no_revision`. Un tel événement est un **indice de non-exclusivité de cause**, pas une attribution `world` du passé et pas un jugement cognitif de production.

## Critères préfixés

- T1 : 32 mondes, 64 transitions physiques, 16 relocalisations externes au premier pas confondues et 16 déplacements passifs au second, toutes attestées par effets et captures.
- T2 : 16 premières paires normal/confondu indiscernables à t1/t2, mêmes premiers jugements `self`. La règle externe candidate ne lit aucune vérité physique.
- T3 : 16/16 déplacements passifs détectés → reconsidération `unknown`, 16/16 témoins immobiles inchangés. Dans les 16 révisions : 8 initialement fausses **et** 8 initialement correctes. La spécificité causale doit donc être rapportée, pas masquée par un taux de détection flatteur.
- T4 : reçu append-only lié à l'identifiant initial et à une référence perceptive ultérieure distincte ; refus explicite de première attribution autre que `self`, de doublon, de temps invalide, de commande autre que `attendre` et d'indice absent. Aucune mutation de `GoalAgencyService`.
- T5 : Python 3.11/3.12 et artefacts par monde ; 8 seeds et **0 vie autonome**. Aucun crédit GA-06, aucun changement de seuil 2+2/12 ou de politique.
- T6 : si les résultats divergent du protocole, déclarer l'échec ou le caractère inconclusif sans ajuster a posteriori les critères.

**Limite scientifique** : une révision prudente n'identifie pas le mécanisme historique. Les deux mondes restent indiscernables même après la nouvelle preuve. Les conclusions sur l'utilité en vies autonomes, le coût UC, la mémoire, l'atomicité WAL et la révision interne d'I0 restent **INCONCLUSIVE**. La séparation agency proximale / responsabilité distale reste une décision normative opérateur non prise. Issue #110 OPEN, Stage12 PARTIAL.
