# Issue #110, Option A : progression du registre canonique et de l'audit spatial

**14 octobre 2026. Statut : implémentation partielle, non validée scientifiquement et non fusionnée.** PR #155, branche `feature/stage12-issue110-spatial-agency-option-a-20261014`, basée sur #153 et non sur la branche `main`.

## 1. Logiciel effectivement développé dans cette passe

- `Stage12GoalProgressLedger` conserve son **unique propriétaire** métacognitif et ajoute une intention immuable `LivedSpatialGoalIntent` versionnée `stage12-lived-goal-spatial-progress-v1`, sans créer de nouveau registre.
- Le sous-critère est local à un mouvement dirigé vers une cellule adjacente, avec cible, nature de ressource, direction, position initiale, `life_id`, `goal_ref`, `option_ref`, hash commande et échéance `t+1`. Valeur initiale Manhattan = 1, réussite stricte = 0 et échec local = distance non réduite, **pas échec du but global**.
- La réponse inconnue reste obligatoire si l'observation est absente, tardive ou refusée pour UC. Les entrées malformées sont refusées avant modification du propriétaire.
- L'état causal courant contient le sous-type spatial et accepte sa restauration **uniquement sur un registre vierge** pour la génération courante. La restauration historique d'un propriétaire ayant déjà travaillé reste interdite. Aucun test M-11 complet `os._exit` sur le nouveau chemin n'a encore été exécuté.
- `audit_stage12_goal_progress` reconnaît les deux contrats historiques et spatiaux. Le critère spatial exige le motif `active_goal`, une cible réellement perçue avant la commande, un déplacement effectif `se_deplacer` dans la direction préenregistrée, un hash de commande cohérent, un seul pas de capture ultérieur, une position de capture concordant avec `world_transition_experienced.position_after` et une valeur finale recomputée indépendamment. La chaîne de hash n'est **pas** une vérité physique externe.
- Des tests purement logiciels vérifient la restauration, les échéances, l'abstention, l'unicité, la validité de la cible et la séparation d'attribution ; des tests à commandes de fixture effectuent de vraies transitions WorldBody libres et bloquées puis comparent séparément le jugement perceptif et le critère de distance.
- Les anciens audits et tests de gains corporels continuent à s'exécuter, sans convertir P-47 en `success` ni `failure`.

**Validation ciblée :** [GitHub Actions #38485879401](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38485879401), SHA `752b482158fe0d30f4d424815b8a4686cb2e0f73`, PASS Python 3.11 et 3.12. Un run précédent #38485763068 était rouge uniquement à cause d'un fichier `test_stage12_goal_progress_audit.py` inexistant, retiré du workflow. Cela reste un défaut CI réel conservé dans l'historique et ne démontre pas une défaillance du calcul spatial.

## 2. Frontière non franchie

**La chaîne expérimentale spatiale n'est pas intégrée** : `Stage12Runtime._dispatch_decision` préenregistre encore exclusivement la mesure corporelle du but et ne crée pas de `LivedSpatialGoalIntent` à partir de choix moteurs autonomes. `GoalAgencyService` ne produit encore aucun jugement spatial original ; la politique pure `evaluate_spatial_goal_cue` est une candidate isolée et les tests de fixture ne comptent donc **jamais** comme `world` vécu. La jointure P43, le coût UC supplémentaire de classification spatiale, l'audit indépendant du jugement, la restauration M-11 globale et les scénarios de décision spontanée restent à implémenter et valider.

Ne pas envoyer un résultat `failure` local à la politique de jugement : elle doit uniquement recevoir copie efférente, cible et passabilité directement perçues et capture ultérieure. Ne jamais inventer un `world` si Action Control ne sélectionne pas spontanément de commande admissible envers l'obstacle.

## 3. État scientifique et critères de poursuite

La dernière campagne autonome de faisabilité publiée reste celle du [run #38484769557](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38484769557), 4 vies × 50 pas, **zéro plan d'objectif, zéro jugement spatial et zéro paire**. La présente passe logicielle ne transforme pas rétrospectivement ce résultat négatif en réussite. L'issue #110 reste ouverte et Stage 12 non réceptionné.

La suite nécessaire est l'opt-in versionné au runtime avec débit UC déterministe, la politique de jugement détenue par Action Control, l'audit des paires spatiales depuis les événements canoniques, tests de reprise à froid/crash/mort, puis nouvelles vies préenregistrées avec traces effectivement auditables, sans choix imposé. Stage 9 reste scientifique NO-GO.
