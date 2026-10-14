# Individual Zero #110 : A2.14, apprentissage relationnel borné et abstention sur contradictions physiques

**14 octobre 2026. Verdict global Stage12 : PARTIAL.** Préenregistrement **AVANT** la première implémentation `bf7ef295db5c9504acee1ac8cbf78a32bf9650b0`. Base : `main cac44c54c551f6d874bc889deee705cfa51790d6`. Expérience hors-ligne uniquement ; aucun modèle cognitif ou contrat normatif MVP v1.3.1 changé.

## Protocole et provenance

[CI expérimentale #38622988897](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38622988897) : **PASS Python 3.11 et Python 3.12**, 80 paires entraînement/test, seeds **61..68**, 10 familles. [CI de provenance physique #38623196741](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38623196741) : **PASS Python 3.11 et 3.12**, enregistrement de **272 transitions réellement appliquées via `WorldBody.apply`**, 0 transition sans rôle de monde, au sein de **176 mondes physiques externes distincts** (160 mondes d'entraînement source/test + 16 mondes supplémentaires de contradictions observées avant le test). Les fichiers JSON par famille et seed conservent les empreintes SHA-256 de la transition, la commande, le pas physique, le rôle du monde, les clés et les résultats. Ces 176 mondes **ne sont pas des vies autonomes d'I0**, et 272 transitions externes **ne sont pas** un horizon autonome de 600 pas.

L'Equipment historique ne reconnaît aucune des 80 entrées `heldout` à coordonnées absolues translatées, car elles n'ont pas de hash complet identique aux exemples sources. Le candidat naïf laboratoire calcule la clé depuis la perception autorisée, en conservant tous les champs corporels, inventaire, voisinage cardinal, `current_resources`, `is_night` et commande, et en remplaçant les coordonnées absolues des voisins par leurs déplacements relatifs. Pour contrôler la traduction des prédictions, les résultats physiques sont comparés sous forme relative : déplacement, corps, inventaire, localité suivante, fin de vie et effets de commande.

Une variante **abstention sur conflits** n'émet une empreinte de conséquence observée que s'il existe exactement **une conséquence distincte** dans les exemples prénataux correspondant à cette clé relative. Zéro ou au moins deux conséquences incompatibles → **pas de prédiction**. Cette règle n'infère aucune cause physique cachée et ne connaît aucune étiquette Oracle. La seconde expérience contradictoire est recueillie sur **un monde d'entraînement supplémentaire indépendant**, jamais sur le monde `heldout`.

## Observations physiques et métriques, prédéfinies

| Famille / groupe | N tests physiques `heldout` | Table exacte : couvert | Lookup relatif naïf : correct | Lookup naïf : erreur | Lookup prudent : prédictions | Lookup prudent : erreur |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Translation mouvement libre | 8 | 0 | **8** | 0 | 8 | 0 |
| Translation mouvement bloqué | 8 | 0 | **8** | 0 | 8 | 0 |
| Translation collecte | 8 | 0 | **8** | 0 | 8 | 0 |
| Translation ingestion | 8 | 0 | **8** | 0 | 8 | 0 |
| Toxicité cachée | 8 | 0 | 0 | **8** | **0 (abstient)** | 0 |
| Danger extérieur caché | 8 | 0 | 0 | **8** | **0 (abstient)** | 0 |
| Obstacle perceptible différent | 8 | 0 | aucune prédiction | 0 | **0 (abstient)** | 0 |
| Saturation corporelle différente | 8 | 0 | aucune prédiction | 0 | **0 (abstient)** | 0 |
| Inventaire différent | 8 | 0 | aucune prédiction | 0 | **0 (abstient)** | 0 |
| Jour/nuit et créature | 8 | 0 | aucune prédiction | 0 | **0 (abstient)** | 0 |
| **Total** | **80** | **0** | **32** | **16** | **32** | **0 erreurs émises** |

Tous les 32 transferts relatifs compatibles sont reproduits par les deux Python, sans erreur observée **dans cette matrice**. Les 32 contextes à **différence accessible** produisent une clé différente et le lookup refuse d'inférer leur effet. Dans les 16 contextes à **cause cachée**, un unique exemple sain conduit le lookup naïf à une fausse prédiction (même état relatif accessible, vraie blessure), y compris pour une baie bénigne associée à un danger ambiant non perceptible. Après exposition de la table de laboratoire à **un second résultat physique prénatal contradictoire**, le lookup prudent s'abstient 16/16.

**Point scientifique critique :** le fait qu'aucune erreur n'ait été *émise* par le modèle prudent ne constitue **pas** une capacité à prédire un danger nouveau. Dans les mondes nocifs jamais observés, **avant** l'exemple contradictoire, le même lookup prudent aurait émis la prédiction bénigne (comme le modèle naïf). L'expérience démontre la valeur de l'abstention **sur ambiguïté déjà observée**, pas une innocuité ni un seuil fiable de risque pour les événements rares et retardés. Les exemples contradictoires dérivent de véritables transitions `WorldBody.apply` avec effets corporels, mais I0 ne reçoit pas leur étiologie cachée, leurs vérités Oracle, ni les résultats des mondes test.

## Hypothèses et décisions

- **H_trans : PASS borné** : translation de coordonnées absolues utile quand l'état local, la commande, le corps, l'inventaire et l'issue sont physiquement comparables, sur 32 contrastes prédéfinis. Pas de garantie près des frontières, hazards inconnus ou états imparfaitement observés.
- **H_single : FAIL sécurité du naïf** : 16/16 prédictions incompatibles avec de vrais résultats nocifs, malgré la même entrée accessible.
- **H_conflict : PASS borné hors ligne** : 16/16 abstentions après preuve contradictoire déjà rencontrée ; sans expérience contradictoire, aucun garde-fou démontré.
- **H_retention : PASS dans les 32 contre-contextes ciblés** : différence perceptible ou corporelle conservée, aucune prédiction produite. Pas de validation universelle.
- **Déploiement : NO-GO** pour I0 à ce stade. Aucun `FrozenTableEquipment` général ni `Simulator` modifié. Une transition prédite compatible n'établit ni responsabilité causale subjective ni étiologie de danger.

## Critères du Stage12

| Critère | Verdict A2.14 |
| --- | --- |
| C1 Attribution subjective | INCONCLUSIVE (aucune vie cognitive dans l'expérience) |
| C2 Distinction causale | PARTIAL : confondeurs externes identifiés, aucune attribution I0 mesurée |
| C3 Diversité | INCONCLUSIVE (aucune action autonome) |
| C4 Alimentation réellement vécue par I0 | INCONCLUSIVE (ingestions physiques programmées externes uniquement) |
| C5 Discrimination P-48 | INCONCLUSIVE |
| C6 Robustesse long horizon | INCONCLUSIVE |
| C7 Reproductibilité | PASS borné (deux Python, huit seeds physiques, fichiers de provenance) |
| C8 Conformité à la séparation épistémique | PASS borné (laboratoire externe et défaut de modèle I0 inchangé) |

**Verdict global Stage12 : PARTIAL.** L'issue #110 reste OPEN et le Stage12 n'est pas réceptionné par l'opérateur.

## Points à traiter après intégration

1. Créer un témoin adversarial à **effet retardé réellement intervenu après ingestion**, sans imputer le danger extérieur à la baie ni modifier silencieusement la définition DC-05 de v1.3.1.
2. Tester davantage de translations près des bords, ressources et obstacles évolutifs, et collisions entre différentes géométries ; conserver l'abstention pour tout cas insuffisamment étayé.
3. Avant une expérience cognitive ON/OFF du modèle relationnel, définir les sources autorisées d'apprentissage, la propriété du stockage, les coûts UC, un niveau explicite d'incertitude et l'intégration avec les corrections Stage9. Le coût de refus sous données rares doit être mesuré en même temps que le coût de faux optimisme.
4. Conserver l'échec transversale préexistant de `tests/test_stage12_a26_long_horizon.py::test_actual_mortal_life_with_small_external_cap`, qui suppose parfois un reçu `stage10_reduced_capture` inexistant après la première paire causale ; ne pas masquer ce problème avec un résultat d'Equipment favorable. La suite focused Stage12 continue d'être vérifiée séparément.

**Aucune adoption de la proposition normative MVP v1.3.2/DC-05** par cette campagne.
