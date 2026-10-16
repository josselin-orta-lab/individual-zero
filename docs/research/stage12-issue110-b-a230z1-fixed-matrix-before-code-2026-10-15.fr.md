# A2.30-Z1 : plan de cellules et comptabilité gelés avant code et avant toute transition Z

**2026-10-15.** Complément prescriptif au préenregistrement initial `c046712b97b0e5887dece3b490957123013d7b5e`. Celui-ci demandait explicitement de fixer la matrice définitive **dans le code avant la première physique** ; pour renforcer la séparation, les quantités et séquences sont ici archivées **avant même le code**, donc vérifiables a posteriori. Aucun résultat Z n'a été observé.

## Mondes déterministes, sans import d'I0 vivant

**Deux valeurs initiales de nourriture :** {35,45}. **Deux positions :** {(5,5),(7,7)}. Physique de référence pure `physical_fixture_config` déjà utilisée pour W, adaptée comme W : nourriture décroissante de 0,5/pas, eau de 0,2/pas, coût énergie 0,75 pour collecter, 0,5 pour manger, 1 pour se déplacer, énergie initiale 50, intégrité initiale 100. Config de `berry_a` parmi cinq effets : bénin (+10,0), toxique léger (+10,-7), toxique modéré (+10,-30), létal (+10,-100), sans gain (0,0). Config de `berry_b` parmi trois effets **non dévoilés dans la perception** : alternative nourrissante (+12,0), toxique létale (+12,-100), sans gain (0,0). Les deux espèces et leurs effets restent des paramètres *du banc*. Aucun individu I0 vivant n'est instancié.

| Bras expérimental | Resource/layout | Variantes latentes | Mondes | Commandes physiques de laboratoire par monde | Total pas prévus |
|---|---|---|---:|---|---:|
| `a_only` | `berry_a` sur case initiale, aucune B | 5 effets cachés A | 20 | collecter A, manger A, précommandé par le banc **malgré abstention du shadow B** | 40 |
| `b_here` | A+B sur case initiale | 3 effets cachés B | 12 | collecter B, manger B | 24 |
| `b_blocked` | A au départ, B visible à l'est, obstacle est visible | 3 effets cachés B | 12 | essayer déplacement est (bloqué) **sans ingestion** | 12 |
| `b_east` | A au départ, B sur case est accessible | 3 effets cachés B | 12 | déplacement est, collecter B, manger B | 36 |
| `b_far` | A au départ, B à l'est à deux cases, initialement hors champ local | 3 effets cachés B | 12 | déplacement est **exploratoire imposé par le banc**, est à nouveau, collecter B, manger B | 48 |
| **Total** | | | **68 mondes indépendants** | | **160 transitions physiques prévues** |

Le bras `b_far` doit distinguer le **choix initial** (B non visible donc politique shadow s'abstient) de la **réévaluation après exploration exogène du banc** (B devient visible sur la case voisine). Le fait que le banc ait imposé le premier déplacement ne prouve pas qu'I0 l'aurait choisi. Le bras `b_blocked` doit vérifier un déplacement bloqué réel, sans prétendre que B est collectable depuis la case initiale.

Une **heuristique shadow d'accessibilité**, calculée strictement depuis un `SimulationState` first-person complet et le prédicat `SimulatorPlanner.candidate_commands`, renvoie :
- si B se trouve sur la case actuelle : `candidate_collect_b` ;
- sinon si B est sur la case est voisine et `east.passable` vrai : `candidate_move_east_to_b` ;
- sinon : `abstain_no_visible_accessible_b`.

Cette heuristique **ne prédit aucune sûreté**, ne lit ni effets cachés ni outcomes du banc, ne commande aucun monde. Le laboratoire applique toujours les commandes préengagées, **indépendamment** de l'heuristique. La seule validation prospective de sélection porte sur l'**accessibilité perceptive** et la correspondance des préconditions de mouvement/collecte, pas sur la capacité à éviter la toxicité.

Pour le **vrai algorithme `SimulatorPlanner.search` utilisé passivement**, faire une recherche alimentaire R=1, profondeur=3, setpoint nourriture=65 **après le tout premier pas physique** de chaque monde (soit 68 recherches). Chaque recherche utilise `FrozenTableEquipment` constitué **exclusivement des conséquences des actions précédemment vécues dans CE monde** (au moment de cette requête, une seule première transition), et un `Simulator` inchangé. Les commandes que le planificateur pourrait émettre restent seulement des propositions de *shadow* non exécutées. Le résultat `incomplete_model`, `partial_progress` ou `plan_found` sera enregistré fidèlement, sans forcer le statut attendu. **Les UC cognitives ne sont pas mesurées** : le coût de calcul du banc ou des appels shadow ne vaut pas reçus de UC vécues.

**Arrêt immédiat** après le premier événement terminal physique. Le dernier état d'un mort est une pièce du banc, non une perception future de l'individu. Aucun monde ne sera recyclé, rétabli ou poursuivi après sa mort.

## Critères et contrôles négatifs

Tester automatiquement la matrice (20/12/12/12/12), les 160 transitions attendues, le nombre de décès et les résultats alimentaires *sans définir un taux de succès comme objectif des tests*, l'identité des états perceptifs de départ des trois variantes B à bras/faim/position fixes, le contraste b_here/b_east/b_far avec b_blocked, les faux succès d'un proxy naïf `B visible donc sûr`, les refus d'un champ `latent_external_only` dans l'entrée, le retour à la case initiale ou obstacle obstruant une collecte impossible, l'intégrité des enregistrements et le gel à la mortalité.

Une incertitude sur la première arête de Stage6 devra être signalée, pas résolue artificiellement par des données d'entraînement venues d'autres mondes ou de l'Oracle. Publier les fichiers train/test physiques et hashes, les 68 réponses shadow Stage6, les dénominateurs non filtrés, ainsi que les coûts de déplacement et de collecte.

**Attention :** l'exécution de laboratoire d'une ingestion B physiquement sûre dans certains mondes ne vaut ni certificat `safe` ni connaissance vécue qu'une espèce B est sûre. Z ne peut ni clôturer l'issue #110 ni modifier le MVP v1.3.1. Les résultats physiques pourront ensuite être recalculés par un auditeur distinct après préenregistrement de celui-ci (Z2).
