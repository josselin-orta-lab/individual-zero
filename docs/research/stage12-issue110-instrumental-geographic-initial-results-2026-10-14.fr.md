# Stage 12 / issue #110 : résultats initiaux du contraste exploration instrumentale

Date : 14 octobre 2026. Préenregistrement avant code `29868373ebd1075b0cb18fb57f7743949279bf75`. Source de campagne `da9cbfbb99ec33d56ef5aa6b1386254c327baf6b`. [CI #38564583429](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38564583429) : **PASS Python 3.11 et 3.12** pour chacun des 16 scénarios (16 vies indépendantes, 42 transitions physiques chacune, **672 pas physiques uniques** ; les doubles exécutions sous deux versions de Python ne constituent pas 32 vies). Les audits de la campagne sur WAL, journal causal, action/objectif et A2 ne rapportent aucune erreur.

## Observation comportementale, version Python 3.11 (mêmes comptes sous 3.12)

| Profil | Contrôle libre / A2, engagements | Instrumental libre / A2, engagements | Attribution nouvelle dans instrumental | Couples nouveaux |
| --- | --- | --- | --- | ---: |
| restored | 3 / 3 | 3 / 3 | aucune : conserve 2 self + 1 unknown en libre, 1 self + 1 world + 1 unknown en A2 | 0 |
| sustained | 0 / 0 | **1 / 1** | libre : **1 self** ; A2 : **1 world** | **2** (1 success spatial libre, 1 failure spatial A2) |
| replenished | 0 / 0 | 0 / 0 | aucune | 0 |
| urgent | 0 / 0 | 0 / 0 | aucune | 0 |

Contrôle : **6** engagements, **3 self / 1 world / 2 unknown**, 3 couples effectivement consommés. Variante instrumentale : **8** engagements, **4 self / 2 world / 2 unknown**, 5 couples consommés. Les deux nouveaux couples sont dans des vies indépendantes sustained, et ne peuvent pas être combinés pour rendre le détecteur `attribution_bias` applicable. **0/16 vies évaluables** au seuil inchangé 2 succès + 2 échecs dans 12 observations.

## Limite scientifique impérative

Le module `stage12_goal_progress` évalue une **progression sur un pas**, pas l'achèvement du but absolu. Les deux nouveaux jugements `self` et `world` sont liés à la **progression spatiale vers une ressource perceptible** (`spatial_distance`). Une réussite de déplacement local ne signifie ni nourriture ingérée, ni satiété atteinte, ni responsabilité causale générale. Aucun gain de nourriture vécu propre à ces deux vies sustained n'est revendiqué. Le scénario A2 conserve sa réalité physique vérifiée séparée de la perception et du jugement. La comparaison fournit un premier signal de **motivation instrumentale avant action**, non une calibration scientifique générale de la causalité.

Les 16 vies atteignent exactement le total de pas physiques préenregistré et les comptes comportementaux sont identiques sous Python 3.11/3.12. **Cela ne démontre pas que les SHA JSONL sont identiques** : la divergence ULP du Stage8 précédemment documentée doit être vérifiée séparément.

## Décision de développement

**Effet logiciel et comportemental positif limité** : deux nouveaux préengagements authentiques (`active_goal`) dans le profil soutenu, avec deux jugements perceptifs différenciés selon l'intervention A2, alors que les deux témoins comparables n'en produisent aucun. Aucun effondrement manifeste de la locomotion dans les 16 vies : les comptes de commandes par condition sont identiques entre témoin et instrumental (dont 32 déplacements / 10 sommeils dans chaque sustained). Cette égalité n'est pas une preuve d'identité des trajectoires ni de maintien de la diversité de sites. Vérification du nombre de cellules réellement visitées encore nécessaire.

L'ajout est **opt-in OFF par défaut** via `instrumental_geographic_value=False` ; il utilise la frontière effectivement offerte par Exploration, le plan courant Stage6 et une valeur prospective positive Stage8. L'option intrinsèque demeure concurrente ; aucune commande ni aucun label post hoc n'est injecté. Le résultat doit être confirmé par des tests adversariaux de cohérence du **premier déplacement simulé**, de provenance du but et de non-double comptage P-48, ainsi que par un census indépendant des nouvelles visites et des événements de décision.

**Verdict : PARTIAL / bénéfice exploratoire soutenu, réception Stage12 impossible**. Ne pas changer MVP v1.3.1 sur cette seule cohorte, ne pas fusionner la PR #155, ne pas fermer l'issue #110, ne pas annoncer une calibration réussie.
