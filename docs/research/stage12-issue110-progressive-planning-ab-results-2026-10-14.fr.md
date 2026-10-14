# Issue #110 : campagne A/B de planification progressive, résultats du 14 octobre 2026

**Préenregistrement avant code :** `95a735b`. **Code vérifié :** `fcf945d7a178c64406a535c239fe7dbb4e9b3a1c`. **CI :** [run #38551355467](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38551355467), **PASS Python 3.11 et 3.12** après correction d'un test initialement faux ; huit vies autonomes différentes × 36 pas, **288 transitions physiques uniques**. Même cohorte réexécutée sous l'autre Python, non comptée deux fois.

## Défauts éliminés avant le run positif

Le premier run `38549172088` a échoué avant de lancer des vies : son test confondait `incomplete_model` avec `not_found_within_horizon`. Le test a été corrigé en respectant explicitement l'indisponibilité de modèle, sans produire un progrès fictif (`02ef8ac`). Le producteur de progrès a été corrigé (`11625ae`) pour lier son indice à la **variable du but actif** (food/water/energy/integrity), sans compter des baies comme progrès dans une quête d'eau, et le nombre des vies prévues a été rectifié à huit (`fcf945d`). Le mécanisme reste opt-in, désactivé par défaut, et ne modifie pas les seuils UC/Stage12.

## Résultats réellement observés sur une cohorte, identiques en indicateurs sous les deux Python

| Branche | Monde | Engagements Stage12 | self | world | unknown | Couples appliqués | 2 success + 2 failure dans 12 observations |
|---|---|---:|---:|---:|---:|---:|---|
| baseline | restored libre | 3 | 2 | 0 | 1 | 1 | non |
| baseline | restored A2 | 3 | 1 | 1 | 1 | 2 | non |
| baseline | sustained libre | 0 | 0 | 0 | 0 | 0 | non |
| baseline | sustained A2 | 0 | 0 | 0 | 0 | 0 | non |
| progressive | restored libre | 3 | 2 | 0 | 1 | 1 | non |
| progressive | restored A2 | 3 | 1 | 1 | 1 | 2 | non |
| progressive | sustained libre | 0 | 0 | 0 | 0 | 0 | non |
| progressive | sustained A2 | 0 | 0 | 0 | 0 | 0 | non |

**Effet comportemental mesuré : zéro amélioration** des engagements d'objectifs ou de couples vérifiés par le nouveau mécanisme dans les deux mondes testés. `attribution_bias` reste **NON ÉVALUABLE**, 0/8 vies répondent au critère. Les huit journaux, WAL et audits indépendants ont abouti sans erreur, avec un `world` autonome A2 maintenu dans chacune des deux variantes.

Il n'est **pas démontré** que le plan progressif a été effectivement sélectionné : la présente campagne agrège les motifs et ne publie pas encore une vérification causale indépendante des `partial_progress` produits, des segments adoptés et des segments fermés. Ce manque de couverture du nouveau chemin est un verrou logiciel/scientifique à expliciter, même si les tests de contrat du planificateur passent.

## Reproductibilité

Les huit tuples de métriques cognitives sont égaux sous Python 3.11 et 3.12. Les journaux JSONL ne sont **pas** tous binaires-identiques : seuls `baseline_restored_free` et `progressive_restored_free` ont les mêmes empreintes entre versions. Les six autres divergent ; la dérive numérique de Stage8 observée précédemment reste ouverte. Ne pas la dissimuler.

## Verdict et décision

**PASS logiciel des contrats et du runner**, mais **FAIL de l'hypothèse scientifique « ce premier mécanisme suffit à restaurer les sous-objectifs alimentaires soutenus »**. Ce n'est pas une preuve qu'aucune planification progressive ne puisse fonctionner. La sélection d'un progrès fondée sur le premier pas d'un trajet simulé n'est utile que si le modèle Equipment connaît suffisamment de transitions successives vers un progrès ; l'absence d'une preuve de segment actif doit rester explicite.

Recommandation : garder `progressive_subgoals=False` par défaut et **ne pas modifier la spécification normative v1.3.1** sur la base de ce négatif. Prochaine étape : auditer séparément la couverture du modèle Equipment et les reçus de `partial_progress` avant de concevoir des sous-objectifs perceptibles robustes qui respectent le veto, le coût UC et la replanification. PR #155 draft sans fusion, issue #110 ouverte, Stage12 non reçu.
