# Stage 12 / issue #110, résultats A2.17a : contrastes physiques et jugement de première personne

**Date : 14 octobre 2026. Résultat scientifique global Stage12 : PARTIAL.** Protocole préenregistré avant code au commit `1cdd166ca6ddffce5afe75b0e1a6ea1a1fa5ef4a`, base `main e80ed9b2ccbaf0d3f04f05b3342b0be6a4b6e8c3`. Spécification normative v1.3.1 inchangée.

## Portée exacte de l'expérience

Cette première sous-campagne A2.17 ne constitue **pas** les vies autonomes multi-seeds de 600 pas annoncées comme cible du protocole. Elle réalise un **diagnostic physique contrôlé en laboratoire**, sans sélection autonome de commande ni une chaîne complète d'objectifs, mémoire, UC et détecteur métacognitif : 6 conditions ×8 graines spatiales reproductibles (71–78), soit **48 mondes externes indépendamment instanciés**, 48 véritables transitions `WorldBody.apply` et 48 évaluations via le véritable `GoalAgencyService` propriétaire Action Control. Les actions ont été prérédigées par le laboratoire dans chaque condition, pas choisies par I0. Les variations de position sont reproductibles ; elles ne constituent pas 48 vies indépendantes ni 48 preuves de calibrabilité `2+2/12`.

Le service de jugement reçoit seulement une perception locale `SymbolicPerception.capture` avant et après la commande, sa propre préinscription d'action et son `cue_ref`, jamais le résultat physique `WorldBody.apply.effects` ni la vérité des événements `set_obstacle` ou `set_action_failure_schedule`. Ces données restent à l'observateur externe. Une deuxième série de garde-fous vérifie directement **les effets réellement réalisés** avant d'accepter un jugement dans la métrique (inventaire, déplacement, nouvel obstacle, suppression physique de l'effet).

## Exécution et résultats

[GitHub Actions A2.17 #38632712756](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38632712756) : **PASS Python 3.11 + Python 3.12**, toutes les conditions avec résultats identiques (le dernier commit renforçant les assertions de physique est soumis à une nouvelle CI distincte). Les 48 jugements individuels et empreintes SHA des événements physiques restent dans les artefacts.

| Condition physique indépendante | Conséquence réellement observée | Jugement `self` | `world` | `unknown` |
| --- | --- | ---: | ---: | ---: |
| `collect_available` | Baie collectée, inventaire +1 | 0 | 0 | **8** |
| `collect_absent` | Collecte sans baie | 0 | 0 | **8** |
| `collect_forced_failure` | Baie physiquement disponible, effet de la commande inhibé par perturbation extérieure | 0 | 0 | **8** |
| `move_success` | Déplacement libre vers une eau réellement perçue | **8** | 0 | 0 |
| `move_external_obstacle` | Passage d'un voisin initialement libre à un obstacle extérieurement créé et perceptible | 0 | **8** | 0 |
| `move_forced_failure` | Déplacement inhibé par intervention extérieure **sans** nouvel obstacle perceptible | 0 | 0 | **8** |

Les variations de corps, position et environnement suivent une physique réelle contrôlée ; aucune commande `manger` n'est utilisée dans cet essai, qui n'établit donc aucune amélioration alimentaire.

## Analyse et limites

- **H1/H2 : PARTIAL, avec contre-exemple au seul succès physique.** Même une collecte réussie avec inventaire augmenté reste `unknown` : ce comportement est cohérent avec le contrat actuel, qui fixe `collecter` à mécanisme `unresolved`. Un résultat favorable et chronologiquement associé ne suffit pas à engager subjectivement la responsabilité causale. Le test ne démontre pas qu'un indice supplémentaire serait sûr, car une intervention extérieure indépendante pourrait augmenter l'inventaire de la même manière.
- **H_spatial : PASS borné** sur les 24 contrastes spatiaux : I0 distingue un déplacement réellement confirmé (`self`), un nouvel obstacle réellement perceptible (`world`) et un échec sans indice perceptif distinctif (`unknown`). Le banc connaît l'origine de la perturbation, I0 ne la déduit pas lorsqu'aucun obstacle n'est observé.
- **H_control : PASS borné** : les 48 transitions correspondent à une physique effectivement appliquée, aucun label issu des effets physiques n'est injecté dans le mécanisme de jugement.
- **Mortalité/WAL/mémoire/UC : NON ÉVALUÉS directement** : ces mondes externes ne passent pas par une vie d'I0. L'intégration générale #110 demeure une vérification séparée.
- **Horizon 600, Stage9 nocif/retardé, exploration, P-48, calibrabilité 2+2/12 : INCONCLUSIVE** pour ce sous-lot. Le résultat ne doit pas être présenté comme réception scientifique.

## Décision

La politique `GoalAgencyService` de production et la spécification normative v1.3.1 restent **INCHANGÉES**. Ne pas convertir `collect_available` en `self` sur le seul incrément d'inventaire, ni `collect_forced_failure` en `world` sur la seule absence de progression. Un protocole additionnel A2.17b doit établir si une variation d'inventaire causée par une intervention externe indépendante est perceptivement distinguable d'une vraie collecte volontaire, puis comparer la sécurité d'une politique ON/OFF **sans transférer les causes cachées**. Les comparaisons long horizon, multi-seeds, nourriture nocive et attribution subjective calibrable resteront ensuite indispensables.

**Verdict global Stage12 : PARTIAL ; issue #110 OPEN ; aucune réception opérateur.**
