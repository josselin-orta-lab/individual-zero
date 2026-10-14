# Issue #110 : première expérience de valeur prospective Stage6/8 (14 octobre 2026)

Préenregistrement antérieur au code : `97e776f`. Implémentation : `3cd36a0` (préfixe évalué), `bd22eb2` (clôture après une seule commande), `23aceed` (versionnement pré-naissance), runner `d9a5097`. Source initiale vérifiée `648f038b78717b2d0999ed2844a4215aac7617fe`. GitHub Actions [#38556953575](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38556953575) : PASS sous Python 3.11 et 3.12, huit vies uniques × 36 pas, 288 transitions physiques uniques. Audits propres à chaque vie PASS.

## Résultat préliminaire A/B

| Bras | Monde | Engagements Stage12 | Jugements self/world/unknown | Couples appliqués |
|---|---|---:|---|---:|
| Segment 1 commande | restored libre | 3 | 2/0/1 | 1 |
| Segment 1 commande | restored A2 | 3 | 1/1/1 | 2 |
| Segment 1 commande | sustained libre | 0 | 0/0/0 | 0 |
| Segment 1 commande | sustained A2 | 0 | 0/0/0 | 0 |
| Préfixe prospectif complet, exécution bornée à 1 commande | restored libre | 3 | 2/0/1 | 1 |
| Préfixe prospectif complet, exécution bornée à 1 commande | restored A2 | 3 | 1/1/1 | 2 |
| Préfixe prospectif complet, exécution bornée à 1 commande | sustained libre | 0 | 0/0/0 | 0 |
| Préfixe prospectif complet, exécution bornée à 1 commande | sustained A2 | 0 | 0/0/0 | 0 |

Le préfixe modifie **réellement l'évidence compétitive** : dans les deux mondes sustained, au pas 2, `competition_cycle.traces` pour l'option `...:sim:manger:progress:prefix` rapporte une evidence positive d'environ +0,210, un accumulateur > 0,5 au second cycle et `crossed=true`. Le bras témoin avait une evidence d'environ −0,070 et `crossed=false`. **Cependant aucun geste `active_goal` supplémentaire n'est observé.** La capacité de franchissement du seuil de Competition a augmenté, mais ni le résultat moteur ni l'agence vécue.

Il est donc prématuré d'expliquer l'absence d'action par Competition : la prochaine frontière est `crossed_ranked` → admissibilité Action Control → commande réellement appliquée, avec concurrence d'autres options. L'instrumentation `243da7e` relie les reçus `stage8_option_evaluation` et `command_admitted/command_vetoed` de l'option prospective, sans agir sur I0 ; [run #38557311371](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38557311371) était encore en cours au moment de la première rédaction.

**Aucune calibration de `attribution_bias`**, 0/8 vies atteignent deux résultats vérifiés de chaque classe dans une fenêtre de 12. Le nouvel algorithme est opt-in désactivé par défaut, n'introduit pas de bonus artificiel ni d'injection Oracle. La règle de valeur prospective continue d'être une hypothèse expérimentale, pas une réussite du Stage 12. Ne pas adopter la modification normative, ne pas fusionner PR #155 ni fermer issue #110 sur cette base.

## Réévaluation au run indépendant des admissions

L'instrumentation ajoutée en `243da7e` a été exécutée dans [GitHub Actions #38557311371](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38557311371). Pour `prefix_sustained_free` et `prefix_sustained_a2`, au pas 2, les reçus `stage8_option_evaluation` du segment `...:sim:manger:progress:prefix` donnent `simulated_value=+2.132` environ et `evidence=+0.210`; deux cycles Competition inscrivent `crossed=false` puis `crossed=true`. Les reçus d'admission/veto `command_admitted/command_vetoed` de **cette même référence d'option** sont absents au pas 2, dans les vies effectivement inspectées : le moteur n'a donc pas directement admis ou refusé le geste de cette option par Action Control au pas concerné.

**Interprétation limitée** : l'option a été évaluée et a franchi le seuil, sans être soumise à un contrôle d'admission tracé sous sa référence. Il reste à établir la concurrence exacte entre `crossed_ranked`, les autres options, le choix du premier candidat admissible et d'éventuels préemptions/fallbacks, grâce aux références des admissions d'autres options au même cycle. Ne pas identifier cela comme un veto de sécurité sans reçu explicite. L'absence d'engagement supplémentaire demeure un résultat négatif.


## Classement réellement franchi, investigué sans modifier la décision

Le commit `26a0665` fait reconstruire par le runner indépendant les marges de franchissement à partir de `competition_cycle.traces`, selon la règle existante `(accumulator_after - threshold)/threshold`, avec conservation du classement. [CI #38558243904](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38558243904), log Python 3.11 : au **pas 2, cycle 2**, dans `prefix_sustained_free` **et** `prefix_sustained_a2` :

| Candidat ayant franchi le seuil | Marge normalisée | Rang |
| --- | ---: | ---: |
| `option:geographic:frontier:3:1:from:2:1:t2` | **+1,1786033** | **1** |
| `option:goal:eat:food:1:2:sim:manger:progress:prefix` | **+0,0053882** | **2** |

Cela **explique directement** pourquoi franchir le seuil de compétition n'a pas suffi : l'option exploratoire possède une avance très importante, même si le segment de progression alimentaire a bien une evidence positive et franchit lui aussi le seuil. **Aucune modification du planificateur, des indices subjectifs, des seuils ou de Competition n'a été introduite par cet audit.**

Remarque : les anciens relevés d'admissions `admissions=[]` filtrés sur `cycle` ne prouvent pas l'absence d'admission d'une autre option, puisque les reçus `command_admitted` de Stage3 n'exposent pas nécessairement un cycle dans leur enveloppe. Les preuves les plus solides sont ici les rangs issus de Competition et les motifs de commande effectivement attestés par Stage12. Ne pas surinterpréter l'absence de reçus filtrés.

**Arbitrage architectural à étudier :** sans forcer le choix, différencier une exploration physique incidente qui conduit vers une ressource et une action réellement engagée en vue de satisfaire un besoin. Augmenter arbitrairement l'evidence ou rétro-étiqueter le déplacement `active_goal` détruirait la crédibilité scientifique. Tester séparément la concurrence des valeurs intrinsèques et la cohérence à horizon fini, puis la valeur d'engagement durable, en conservant les veto et les budgets UC.
