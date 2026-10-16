# A2.30 : complétude du modèle alimentaire, protocole prospectif

**15 octobre 2026. Préenregistrement avant toute modification de code A2.30.** Base PR #186 au commit `9addd42967f4063a054032602c3d877d683323cd`. PR #184–#186 restent en brouillon. Stage12 PARTIAL, issue #110 OPEN.

## Observation déjà connue, non comptée comme résultat prospectif

A2.29 a produit 247 pas classés `no_planner_proposal` sur 384, avec diagnostic `incomplete_model`, contre seulement deux cas où l'option alimentaire franchit le seuil et perd la sélection. L'implémentation Stage6 emploie `incomplete_model` lorsque sa recherche a rencontré au moins une transition indisponible ; ce statut ne prouve pas à lui seul que le modèle alimentaire entier est absent.

## Hypothèses concurrentes

H1 : le modèle manque d'une transition indispensable `collecter` ou `manger`. H2 : les transitions sont disponibles mais leur précondition (inventaire, lieu, ressources, percepts) n'est pas satisfaite. H3 : les transitions sont accessibles, mais l'horizon de recherche et les restrictions d'UC empêchent la chaîne complète. H4 : l'option alimentaire existe et est évaluée, mais l'arbitrage favorise une option concurrente. H5 : la recherche est réinitialisée par une capture ou une révision d'objectif, avant d'aboutir. Ces hypothèses ne sont pas interchangeables.

## Étape A, audit de preuve, sans modification de runtime

Relire les journaux canoniques A2.29 avec leur tête de hash et leur WAL, et relier, au même pas et à la même tentative, `stage6_planning_result`, `progressive_search_diagnostic`, coûts UC de recherche, préconditions et observations disponibles, options proposées, compétition, action effectivement vécue et suivi d'objectif. Distinguer explicitement `transition_unavailable`, `precondition_unsatisfied`, `budget_exhausted`, `horizon_exhausted` et `evidence_insufficient` seulement si les reçus existants le permettent ; sinon conserver `unresolved`. Aucun événement ni jugement subjectif synthétique.

## Étape B, intervention contrefactuelle seulement après audit A

Si un défaut précis est démontré, comparer des cohortes B nouvellement nées avec modèle témoin et modèle candidat, mêmes facteurs alimentaires/obstacles, seeds et horizons fixés avant naissance. Aucun `set_body`, aucune commande forcée, aucun oracle transmis à I0. Mesurer les propositions, actions autonomes, conséquences alimentaires réellement vécues, décès, coûts UC, sommeil, préengagements et jugements proximaux/distaux. Comparer également les régressions en exploration, sécurité et intégrité WAL. Une hausse de jugements B seule ne constitue **pas** une amélioration causale.

## Critères de décision

Aucun changement normatif MVP v1.3.1, seuil GA-06 `2+2/12`, attribution distale `self`, mortalité, Stage9/DC-05, Oracle ou M11. Toute proposition de correction de modèle doit préciser le mécanisme causal, sa surface logicielle et ses tests de non-régression. Si le journal existant ne permet pas d'identifier la cause, publier cette limite et préenregistrer une instrumentation strictement non intrusive avant de l'utiliser. Une CI verte ne suffit pas à déclarer Stage12 terminé : validation opérateur distincte, issue #110 ouverte.
