# A2.30-ZC : contre-expertise indépendante des résultats autonomes ZB

**Date : 15 octobre 2026.** Relecture indépendante des sorties des deux jobs de la CI ZB [#38767643472](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38767643472), commit `2a19742df22f27752635203304097134a3009c45`. Ce document est une **contre-expertise des agrégats CI et du protocole source**, non une nouvelle expérience et non un nouvel échantillon physique. Les deux versions Python réexécutent les mêmes 12 recettes déterministes.

## Résultats directement corroborés par les deux journaux CI

| Mesure | Python 3.11 | Python 3.12 |
|---|---:|---:|
| Tests unitaires | 12 PASS | 12 PASS |
| Naissances autonomes | 12 | 12 |
| Pas autonomes | 384 | 384 |
| Collectes B | 0 | 0 |
| Tentatives d'ingestion B | 0 | 0 |
| Ingestions B physiquement confirmées | 0 | 0 |
| Ingestions toutes espèces | 8 | 8 |
| Recherches Stage6 | 196 | 196 |
| Recherches sans premier pas prédictible | 174 | 174 |
| Recherches `plan_found` | 10 | 10 |
| Arêtes racine disponibles cumulées | 18 | 18 |
| Jugements dual-scope | 20 | 20 |
| Paires de variantes cachées | 6 | 6 |
| Paires avec parité motrice pré-exposition | 6 | 6 |
| Contrastes valides avec ingestion B | 0 | 0 |
| Décès | 0 | 0 |
| Arrêts par borne expérimentale | 12 | 12 |

Le script `run_stage12_issue110_b_a230zb_autonomous_food.py` crée les individus via `build_life` puis appelle `life.run_step()` sans commande de laboratoire injectée. Les layouts B et les effets cachés sont fixés au moment de la naissance. Le modèle exact prénatal ne reçoit aucune expérience B et rejette la prédiction de `manger(B)` à la racine. L'audit source contrôle la concordance WAL durable, journal canonique, clôtures P48, commandes vécues et journaux Stage6.

## Lecture scientifique

**ZB1, opportunité alimentaire autonome : non soutenue dans cette cohorte.** L'existence physique et perceptive de B n'a pas produit de collecte ni d'ingestion B en 32 pas par vie. Cela ne prouve ni impossibilité générale, ni absence de détection perceptive, ni défaut unique du Stage6. Les motifs des décisions, l'arbitrage, les UC et les limites de modèle restent des explications concurrentes à séparer.

**ZB2, modèle et planification : verrou observé.** 174/196 recherches n'ont aucun premier pas prévisible. Les 10 `plan_found` ne sont pas des plans alimentaires B physiquement accomplis. Il faut distinguer absence de prédiction de B, arbitrage des options et commandes réellement sélectionnées; les agrégats seuls n'identifient pas leur contribution causale respective.

**ZB3, effets cachés : impossibilité de mesurer un effet vécu de B.** Six paires ont la même capture initiale et la même séquence motrice pré-exposition; aucune n'a ingéré B. La toxicité B reste une intervention physique **non rencontrée** et n'explique pas les jugements subjectifs mesurés. Le dénominateur des comparaisons d'exposition est **zéro**, pas six.

**ZB4, garde-fous : contrôles positifs dans la CI**, mais validation opérateur toujours requise. Les 12 statuts `experiment_stopped` ne sont pas des morts; zéro décès ne signifie pas sécurité de B, puisque B n'a jamais été ingérée. La source a audité WAL, P48 et les bornes terminales, mais ce rapport n'est pas une expertise indépendante des 12 archives brutes octet par octet.

## Limites de l'identification

Les 12 identifiants de naissance sont distincts. Leur différence potentielle de graines/personnalité interdit de traiter la parité motrice comme une expérience contrefactuelle parfaite. La preuve Z physique et la preuve ZB cognitive ont des populations et interventions différentes : **168 mondes Z ≠ 12 vies I0 ZB**. Leurs effectifs ne doivent pas être additionnés comme s'ils étaient interchangeables.

Le protocole ZB a fixé `extrinsic_gain=1.6`, `progressive_planning=True` et une profondeur de 3; aucun test d'ablation des contraintes d'arbitrage, de la disponibilité de prédiction B ou du coût UC n'a été effectué dans cette cohorte. Ne pas attribuer les 0 collectes à une cause unique sans expérience discriminante.

## Décision et suite

**A2.30-ZB PARTIELLE, Stage12 PARTIAL, issue #110 OPEN, aucun déploiement.** Préenregistrer une expérience d'ablation **sans forcer les commandes** pour départager trois causes candidates : (i) B perceptible mais aucune proposition B, (ii) proposition B disponible mais perdante à l'arbitrage, (iii) commande B sélectionnée mais refusée par UC ou par le monde. L'ablation doit conserver un témoin non manipulé, une condition de connaissance B bornée et non toxique seulement si l'opérateur valide explicitement l'introduction de ce prior; elle ne doit pas prétendre que le monde dangereux est sûr. Aucun changement de code cognitif ni de spécification normative autorisé par le seul résultat ZB.
