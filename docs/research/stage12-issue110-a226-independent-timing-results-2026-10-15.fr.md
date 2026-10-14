# A2.26 : réplication des frontières temporelles de résultat vécu

**15 octobre 2026.** Préenregistrement `a40ba3d3` avant le code. Réplication confirmatoire informée par A2.25, non découverte aveugle. La matrice a été exécutée sur le commit `46c2bfcbc9fbdaca93b9e8a5eda8ce2b99ebd902` ; [CI #38653873760](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38653873760) **SUCCESS Python 3.11 et 3.12**, mêmes 24 vies rejouées et valeurs agrégées identiques.

## Résultats de la cohorte indépendante

**24 naissances Stage12 autonomes et mortelles, 24 × 32 = 768 véritables pas physiques fermés**, trois profils `restored/sustained/episodic`, obstacles OFF/ON, impulsion extérieure OFF ou `set_body(food=75)` préengagée avant le pas 4, 6 ou 8. **18/18 injections reçues/appliquées** par le scénario extérieur avec journaux vérifiés. Les commandes sont exclusivement choisies par I0.

Les chiffres **des 21 vies entièrement auditables** sont **16 progrès d'objectifs vérifiés, 18 non-progrès vérifiés, 10 jugements `unknown`, 17 paires GA-06 réellement appliquées**, **0 vie dont le détecteur devient évaluable** par le critère intravie `2 succès + 2 échecs / 12 diagnostics`. Les 24 vies ont produit **10 ingestions effectives** dans l'observation physique ; elles ne sont pas toutes des succès de but subjectivement imputés. Ces agrégats n'autorisent pas une fenêtre GA-06 artificiellement concaténée.

**3 suivis de progrès sont refusés par l'audit original `audit_stage12_goal_progress`** avec la divergence exacte entre `body_after` de l'action précédente et observation corporelle du pas suivant. Les trois vies sont `fail_closed_exogenous_confounded`. Le code reconnaît la fenêtre d'intervention, mais **n'accepte ni leurs progrès ni leurs jugements ni leurs paires dans les agrégats vérifiés**. La réussite de la CI signifie que le dispositif expérimental traite ces refus en échec fermé ; **T3 de vérification intégrale d'A2.25 n'est toujours pas rétabli** et le contrat d'une attribution causale sûre n'est pas démontré.

## Sommeil et fenêtre de preuve

L'instrumentation initiale A2.26 attendait à tort un reçu `perceptual_capture` à chaque injection. Les premiers tests ont échoué sur quatre cas d'intervention en sommeil où le système produit `stage10_reduced_capture`. Une deuxième vérification a identifié deux fenêtres lors desquelles **la capture réduite précède un réveil puis une perception complète dans le même pas**. Le code de banc a été corrigé pour accepter ces deux chemins réellement autorisés **à condition** de préserver l'ordre `external_input_applied` avant le premier reçu sensoriel et de valider `stage10_sleep_woke` lorsqu'il y a les deux captures. Cela n'ajoute aucune preuve de jugement d'agence pendant le sommeil.

Résultats finaux : **4 interventions vues uniquement en perception réduite de sommeil**, **2 suivies du réveil et de la perception éveillée au même pas**. Ces épisodes restent distincts des résultats autonomes d'action et de la vérification rétrospective d'un objectif.

## Verdict et bornes

T1/T2/T4/T5/T6/T7 : **PASS technique borné** au laboratoire ; trois divergences de suivi sont confirmées et explicitement non vérifiables. Les CI rouges intermédiaires restent consultables et documentent les corrections de l'instrumentation : domaine du sommeil puis réveil mixte. Aucune modification du runtime I0, de WorldBody, de Perception, de M11, du WAL, des UC, de l'Oracle, de Stage9/DC-05, des seuils `2+2/12`, ni du MVP v1.3.1.

**Conclusion :** la modification exogène du corps entre commande et suivi peut produire un `success` subjectivement compatible mais non validable par une transition causale unique. Le sommeil ajoute une deuxième frontière d'observabilité. L'inférence d'une **responsabilité du résultat distal** est toujours injustifiée à partir d'un reçu d'action proximale seul. Une décision normative opérateur reste nécessaire pour distinguer résultat observé et responsabilité causale, avant toute extension de la politique cognitive.

**Stage12 PARTIAL, issue #110 OPEN, aucune réception opérateur.** La CI de l'ajout documentaire final doit être vérifiée indépendamment du run expérimental cité.
