# Individual Zero / Stage12 / Issue #110 : A2.29, arbitrage des options sous besoin persistant

**15 octobre 2026, préenregistrement AVANT toute instrumentation A2.29.** Base fixe : PR #185, `649a03fa559c2a47dcf9d9666bf31c1314a77ab5`, elle-même empilée sur l'option B en PR #184. A2.28 a déjà trouvé 12 jugements B dans 512 pas, mais zéro dans certaines vies avec une faim persistante et du sommeil/exploration. Ce constat connu inspire cette expérience ; A2.29 **n'est pas aveugle**.

## Hypothèses concurrentes, falsifiables

- **H0, manque d'objectif** : l'objectif corporel n'existe pas à l'instant de la décision.
- **H1, recherche** : malgré un objectif visible dans les reçus, `stage6_planning_result` ne propose rien (`incomplete_model`, `not_found_within_horizon`, erreur de modèle, absence de financement). Le diagnostic de recherche n'est pas une vérité physique du monde.
- **H2, compétition** : une option liée à l'objectif est publiée, enregistrée et évaluée, mais une option d'exploration/sommeil ou `attendre` dépasse son accumulateur/seuil. Il faut prouver la présence des options dans le **même pas** et si possible le **même cycle**; sans paire d'options observée, refuser une conclusion de « compétition perdue ».
- **H3, admission** : l'option d'objectif franchit effectivement le seuil et est classée, mais échoue à l'admission d'Action Control, y compris garde de sécurité. Un simple `option_registration=False` n'est pas automatiquement un échec d'admission.
- **H4, post-admission** : commande motivée par `active_goal` réellement exécutée mais sans préengagement / jugement B ; comparer le `goal_ref`, la mesure, les captures, les UC et les décisions, sans fabriquer de jugement.
- **H5, sommeil** : une commande `dormir` issue d'une capture réduite n'a légitimement pas de preuve de motivation éveillée. Le réveil à perception complète doit rester distinct et ne peut pas être imputé à un jugement durant le sommeil.

## Matrice avant code

**Huit nouvelles naissances B réellement autonomes et mortelles**, avec identifiants distincts de A2.28. Facteurs préexistants : quatre profils corporels `restored`, `sustained`, `episodic`, `marginal`, croisés avec obstacle `free` ou `A2` appliqué après admission au pas 2 et retiré avant pas 4. Le même scénario `near_food_free`, eau initiale 70, plan `horizon_three`, planification progressive et révalidation active, `extrinsic_gain_override=1.6`, `attribution_join=False`, `subjective_goal_agency=True`, `dual_scope_agency=True` et `dual_scope_cost_uc=1` sont fixés avant la naissance. Aucun `set_body` extérieur. **48 pas physiques au maximum par vie**, soit cible de 384, et deux CI Python 3.11/3.12 reproduisant les mêmes huit configurations déterministes, pas seize vies indépendantes. Pas de commande choisie par le banc.

## Audit extérieur strictement en lecture seule

L'observateur relit le WAL durable et journal canonique, puis exige les audits `audit_export_bytes`, `audit_stage12_first_person_agency`, `audit_stage12_dual_scope`, `audit_stage12_goal_progress` originaux. Par pas et tentative : relier `active_goal_changed`, `stage6_planning_result` (avec `progressive_search_diagnostic`), `option_registration`, `stage11_geographic_option_proposed/registration`, `stage10_sleep_option_registered`, `stage8_option_evaluation`, `competition_cycle` (accumulateur/seuil), `stage12_action_motive_attested`, `command_experienced`, `stage10_reduced_capture`, `stage12_goal_agency_precommitted`, `stage12_outcome_responsibility_precommitted/judgement` et `compute_charge`.

La classification par pas adopte ces catégories **disjointes et ordonnées** : `reduced_sleep`, `no_attested_active_goal`, `no_planner_proposal`, `goal_proposed_not_registered`, `registered_but_not_evaluated`, `evaluated_but_not_crossed`, `crossed_not_selected` (ne signifie pas rejet de sécurité sans refus de contrôle), `goal_selected_no_B`, `goal_selected_B`, `evidence_insufficient`. La catégorie `evidence_insufficient` interdit de présenter une simple absence d'événement comme un mécanisme confirmé lorsque des cycles sont dégradés. L'analyse comptabilise en plus, sur les seuls pas avec objectif actif attesté, combien disposent d'une option d'objectif et d'une option géographique/sommeil concurrentes dans le même cycle, puis combien de fois chaque option franchit réellement son seuil. Les `status` de recherche, statut d'évaluation et coûts UC acceptés/refusés sont rapportés sans effet contrefactuel inventé.

## Critères préfixés

- T1 : au plus 384 véritables pas, une commande/transition/`step_closed` par pas, huit vies examinées y compris zéro jugement ou mortalité précoce. Si arrêt prématuré, archive + échec déclaré sans fabriquer des pas.
- T2 : conservation du journal et du WAL et correspondance des audits originaux ; aucune promotion des effets physiques du laboratoire comme vérité subjective.
- T3 : catégories d'entonnoir par pas exhaustives et mutuellement exclusives, reliées à des reçus; au moins les cas `reduced_sleep`, `no_planner_proposal` et `goal_selected_B` sont vérifiés via contrôles négatifs hors cohorte sans affecter I0.
- T4 : ne pas déclarer qu'une option perd en compétition si elle n'a pas été **simultanément présente et évaluée** avec l'autre. Un `stage6_planning_result.proposal_ref=None` est une absence de proposition, pas une défaite de compétition. Un statut `partial_progress` indique une trajectoire bornée et ne prouve pas un gain physique.
- T5 : décrire les raisons de refus UC, inadmissibilité, cycle dégradé et sommeil sans baisse des seuils GA-06 (`2+2/12`) ni déclenchement forcé d'un `manger`.
- T6 : logs JSONL et agrégats par vie reproduits sous les deux Python. Toute divergence doit apparaître et non être effacée.
- T7 : zéro modification du runtime cognitif / physique, des UC, M11, mortalité, Oracle, Bench, Stage9/DC-05 et de la spécification normative MVP v1.3.1. Les PR #184/#185 demeurent techniquement indépendantes, et #110 reste OPEN / Stage12 PARTIAL.

Le **résultat possible « aucune option d'objectif proposée »** est tout aussi utile que le résultat inverse, mais il exige de vérifier que l'appel à la planification était effectivement admissible, pas juste absent. L'audit est une décomposition descriptive de l'action réellement vécue, pas une preuve que l'exploration était irrationnelle. Tout ajustement futur d'une politique de compétition nécessite une expérience contrefactuelle préenregistrée distincte et un arbitrage opérateur.
