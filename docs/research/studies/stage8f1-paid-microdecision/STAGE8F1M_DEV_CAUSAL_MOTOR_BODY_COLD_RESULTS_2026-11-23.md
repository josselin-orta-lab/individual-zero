# Stage8-F1M · Bilan DEV_M de médiation causale, sans verdict scientifique

**23 novembre 2026. Résultat développement uniquement, vérifié à froid.** Nouveau pilote sur 8 origines DEV_M01..08 totalement distinctes des racines consommées F1L ; 2 contenus personnels T5 × 2 traitements des accumulateurs entre T5 et T6. Aucun F1M scientifique, aucune nouvelle racine L, aucun changement du moteur de référence, des résultats F1I/F1J/F1K/F1L ou de Stage2.

## Provenance / pièces vérifiables

- Workflow GitHub [#45187028118](https://github.com/josselin-orta-lab/individual-zero/actions/runs/45187028118) : **4/4 jobs success** (tests adversariaux, pilote 2 origines, audit indépendant Python 3.12 de ces 2, puis pilote 8 origines et audit indépendant complet). L'audit complet a indépendamment reconstruit **3 576 World.step natifs et 16 412 tours substantiels**, uniquement sur DEV_M, à partir des reçus originaux et sans importer le moteur.
- Original complet 8 origines : [artefact Actions #14824077631](https://github.com/josselin-orta-lab/individual-zero/actions/runs/45187028118/artifacts/14824077631), digest ZIP GitHub sha256:f5ef20cc188ecfef17f0824063b0bb2cf3b950abbed92ccaa16af9a3577b061e, GZIP interne sha256:b5166bf993e19eda72bed040fd2b7a9620dd661f5b6ebfe7b76562759b0970eb. **SHA256 du JSON canonique décompressé : 117c8b1126a2c62b03702fa6b4600ae962ae0b662607080953297b9a96f27ae7**, identique au rapport froid.
- Audit froid 8 origines : [artefact Actions #14823559471](https://github.com/josselin-orta-lab/individual-zero/actions/runs/45187028118/artifacts/14823559471), digest ZIP GitHub sha256:9b30c1021fff923c76aa017ca847190a562e36e63c629ed22380231f78c6a6df, SHA256 JSON 8f3108d2c1542a11a9bd45c27352c3b3e95c88506438ac65085854cfe240c22e.
- Artefacts temporaires Actions, prévus pour expiration le **23 décembre 2026**. Les numéros, SHA et résultats secondaires sont conservés dans cette note et l'issue #1516 ; les originaux volumineux DEV_M ne sont **pas** à eux seuls un séquestre permanent.

## Contrôles et dénominateurs

| Contrôle | Reconstruction froide |
| --- | ---: |
| Expériences personnelles réellement financées T1..T4 | 8/8 |
| Factures de décision T5 récentes vs anciennes identiques | 8/8 |
| Factures de décision T6 carry vs zero identiques | 16/16 |
| T5 full_sham et duplications résiduelles de continuation neutres | 8/8 |
| Options gagnantes différentes à T6 | 4/16 |
| Commandes motrices différentes à T6 | 2/16 |
| Réserves terminales différentes à T60 | 4/16 |
| Gains/pertes de ticks vécus | 0/16 |

Les 16 comparaisons ne sont **pas** 16 individus indépendants : elles représentent 2 contenus par chacune des 8 racines. En unités d'origine, un changement d'option T6 apparaît dans **2/8** racines (DEV_M01 et DEV_M02), un changement de moteur T6 dans **1/8** (DEV_M01), un changement corporel à T60 dans **2/8** (DEV_M01 et DEV_M03). Les cas positifs de mécanisme se concentrent dans le monde DEV_M_southwest_springs ; les quatre origines DEV_M05..08 de l'autre monde restent sans divergence corporelle.

## Trajectoires natives, sans réinterprétation

| Origine | Première différence de gagnant | Première commande différente | Premier écart des cinq réserves | Commandes divergentes T6..T60 | Interprétation |
| --- | --- | --- | --- | ---: | --- |
| DEV_M01 | T6 | T6 : se_deplacer S vs W | T7 | 47/55 | Effet moteur direct du résidu, puis compromis corporel |
| DEV_M02 | T6 | Aucune | Aucune | 0/55 | Effet sur l'option **bloqué** avant commande : même mouvement et même corps |
| DEV_M03 | T7 | T7 | T9 | 49/55 | Effet comportemental **différé**, aucun effet moteur à T6 |
| DEV_M04..DEV_M08 | Aucune | Aucune | Aucune | 0/55 | Aucun effet détecté dans ces contextes |

En DEV_M01, les deux branches choisissent à T6 un déplacement réel, mais **S contre W**, à coût cognitif identique et sans écart de réserve immédiatement après T6. L'écart corporel commence T7. À T60 (carry − zero, ordre énergie/nourriture/eau/intégrité/vigilance) : **[+2.2116, −0.66, −0.8, +0.2, −0.698]**, un compromis sans dominance ni vie supplémentaire.

En DEV_M03, la compétition et la commande **T6 sont identiques** entre carry et zero. Le premier gagnant/moteur divergent apparaît T7, le premier écart corporel T9, et les commandes diffèrent sur 49 des 55 ticks après fork. À T60 : **[−15.772, +0.55, +16.0, −1.0, −0.498]**. C'est un autre compromis réel sans gain de persistance.

DEV_M02 est un contrôle conceptuel essentiel : une **option gagnante différente** à T6 n'entraîne **aucune commande motrice différente** ni aucune conséquence corporelle détectée jusqu'à T60. L'admissibilité/action du Mind ne doit pas être omise des métriques.

## Mémoire personnelle et limites des résultats

Les deux moyennes personnelles T5 différentes (récente versus propre T1) sont attestées dans **8/8** origines du pilote. Néanmoins, chaque origine choisit la même commande et produit le même monde après T5 dans les deux contenus. Les résultats carry/zero observés sont identiques pour les deux contenus à chaque origine. **Ce développement ne démontre pas d'interaction bénéfique de la fraîcheur mémorielle avec la persistance des accumulateurs.** Il démontre localement la sensibilité du comportement à l'intervention carry/zero et, dans deux origines, des suites corporelles réelles sans amélioration nette de survie.

L'intervention est une manipulation de laboratoire de l'état Mind.acc juste avant T6, **non** une nouvelle faculté auto-initiée de l'individu et **non** un comportement imposé. Les actions et apprentissages post-fork sont librement calculés et véritablement facturés. Les constats ne valent pas preuve de généralisation écologique, hérédité, amélioration adaptative, ni promotion de Stage2.

## Décision

**DEV_M_VALIDATED_LOCAL_MECHANISM; SCIENCE_F1M_NOT_EXPOSED.** Conservons le pilote et l'audit comme preuves logicielles. Une campagne scientifique distincte nécessite huit écologies prospectives, nouvelles graines préenregistrées, contrôles coût/sham, verrou create-only, Releases immuables et autorisation du tir F1M. Les estimands et seuils d'avantage adaptatif doivent être gelés séparément avant exposition. Le statut F1L négatif reste inchangé.
