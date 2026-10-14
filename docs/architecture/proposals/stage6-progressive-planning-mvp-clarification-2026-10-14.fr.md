# MVP : décision architecturale proposée pour la planification progressive (Stage 6)

Date 2026-10-14. **Statut : proposition additive, non normative tant que l'expérience A/B et la réception opérateur n'ont pas abouti.** Source conservée : `docs/architecture/reference/en/mvp-specification-v1.3.1.md` (hérite des exigences v1.2.1 §§8.11 et 12.4).

## Constats préalables

- Le Stage 6 est borné par `max_depth <= H_max`, non par une constante normative `3`.
- Une recherche sans solution totale à profondeur finie ne démontre pas l'impossibilité d'un but. Un but peut persister et être poursuivi par des actions dont les effets n'atteignent pas immédiatement le seuil.
- Le contrôle Action Control reste seul habilité à appliquer une commande, avec le même veto de sécurité et les mêmes captures perceptives.
- Un segment intermédiaire **n'est pas** une réussite du but. Son résultat moteur `step_completed` et sa provenance sont distincts du critère `food_at_setpoint` du but.

## Clarification normative candidate

> Planning PEUT, lorsqu'aucun plan final satisfaisant l'objectif n'est trouvé dans son horizon complet, proposer un segment de progression borné, sur la seule base d'états accessibles à I0 et de transitions complètes de son Equipment. Cette proposition conserve la référence du but actif, exprime explicitement que son succès concerne **uniquement le segment**, et n'autorise aucune attribution causale du résultat final. Aucun segment ne peut être proposé sans effet intermédiaire prédit positif et observable. Après une commande réellement exécutée, la poursuite exige une nouvelle observation, une nouvelle évaluation payée et une admissibilité contrôlée. Ni la simulation partielle, ni l'échec de recherche finie, ni l'absence de modèle ne démontrent une impossibilité ontologique ou une cause extérieure. Les budgets de simulation et les invariants de conservation du journal, de mortalité et d'interdiction d'accès Oracle restent inchangés.

Cette clarification suffit probablement en tant qu'interprétation des principes existants. **Ne pas modifier rétroactivement la référence v1.3.1**. Une nouvelle version mineure devra être proposée à l'opérateur seulement si la nouvelle valeur `partial_progress` et l'identité des segments deviennent un contrat durable inter-modules.

## Implémentation expérimentale associée

- `Stage6PlanningConfig.progressive_subgoals=False` par défaut, activation opt-in par configuration de vie, versionnée.
- Recherche exhaustive dans le **même horizon** ; priorité toujours à un plan satisfaisant le but.
- Si aucun plan complet, choix d'un progrès simulé corporel positif ou de baies supplémentaires en inventaire. Aucun nouvel edge simulé par un second pass.
- Segment borné à une commande, `success_condition=step_completed`, `goal_ref` conservé, option normale admissible et concurrente.
- Clôture d'une option progressive après un geste appliqué, puis nouvelle décision sur les captures du cycle suivant. Ni le but ni son résultat scientifique ne sont automatiquement promus.
- Audit et campagne A/B préenregistrés : `docs/research/stage12-issue110-progressive-planning-prereg-2026-10-14.fr.md`.

## Réserves à investiguer

Le gain de stock dans le simulateur peut être un simple proxy de capacité et ne garantit pas une consommation utile ; aucune appréciation subjective de causalité ne doit être formée sur ce seul proxy. Les profils très pauvres peuvent encore ne disposer d'aucune transition connue offrant un progrès dans l'horizon ; dans ce cas l'option est absente, sans étiquette d'impossibilité. La suppression d'options expirées, les interruptions M11, le sommeil et la compatibilité de la signature d'apprentissage du segment doivent être revérifiés par CI et expériences avant recommandation d'intégration.

**Décision courante :** proposition normative seulement, Stage12 non reçu, PR #155 sans fusion, issue #110 ouverte.
