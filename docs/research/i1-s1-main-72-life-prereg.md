# Individual Zero, S1 cohort principale prospective (2026-10-18)

**Préenregistrement avant exécution** : sujet I1 immuable `11fa9104e7e9d2c7ad70e837c80463fc4cbe4777`, qui intègre les corrections #283/#287 et les capteurs passifs validés par #290. Aucune comparaison avec les anciennes expériences cassées. Le pilote précédent sur `f90e7bc3` reste descriptif et EXCLU de cette cohorte.

## Plan d'échantillonnage
Six mondes enregistrés : oasis, foraging, dry-valley, empty-land, hazard-edge, blocked-route. Pour chaque monde : **12 vies neuves, quatre lots de trois naissances**, graines de lot 246, 247, 248, 249. Chaque vie avance jusqu'à **300 pas observés au plus**, sauf décès irréversible. Ainsi 72 vies et un maximum théorique de 21 600 pas. Carte fixe pour chaque monde, naissance et tempérament selon le moteur. Les lots sont les unités de randomisation pertinentes ; les pas d'une même vie ne sont pas des réplications indépendantes.

Aucun apprentissage ou état n'est transmis entre vies, aucun monde ne révèle son état caché à I1, pas d'actions forcées, pas de rollback ni résurrection. Chaque sous-job a son propre répertoire et des identifiants scellés. Un échec technique ne compte pas comme mort ni réussite. Tous les artefacts sont conservés, y compris les échecs.

## Mesures et hypothèses
(A1) actions physiques appliquées/pas clos : moyenne pondérée et moyennes individuelles.
(A2) fréquence par 100 pas et fraction de l'ensemble des actions, pour chaque primitive réellement vue.
(A3) évolution par fenêtres d'âge préenregistrées : 1-30, 31-60, 61-120, 121-180, 181-240, 241-300 ; effectifs et mortalité/censure à chaque fenêtre.
(C1) événements Stage10 par vie : sommeil, lot, ajournement, activation, commit.
(C2) empreintes avant/après des propriétaires et versions `SlowHistory`, ainsi que référence du commit observé ; les changements hors commit sont séparés.
(L1) comportements avant/après publications : analyses purement exploratoires tant qu'aucune chaîne causale propriétaire->décision->résultat physique n'est démontrée.
(B1) données physiologiques et inventaire par pas, séparées par monde et tempérament si authentifiées.

Indicateur de consolidation cognitive non vide : NOT_ESTABLISHED sur le seul hash. Les empreintes peuvent indiquer un changement technique mais pas sa cause, son contenu, ni sa qualité. Apprentissage causal : NOT_ESTABLISHED sans étude adaptée. Les comparaisons entre mondes (ressources, réserves, environnement) sont descriptives, pas des expériences contrôlées sur un seul facteur. Survie des mondes dangereux : suivre décès et censure et éviter le biais de survivants.

**Conditions de clôture** : 72 vies authentifiées ou échec explicite documenté, pas de mélange de SHA, rapport d'activité/physiologie/survie/consolidation, revue des preuves d'apprentissage et des limites, décision GO/NO-GO par question, puis clôture administrative de S1 avec statut scientifique indépendant des souhaits de l'expérimentateur.
