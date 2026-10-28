# #305 : exposition amont du classement Q dans une naissance dry-valley M11

## Question enregistrée avant la lecture de la nouvelle sortie

La PR #599 a observé un seul candidat pertinent à chaque cycle du pas 18 d'Oasis B. Le tri Q entre candidats ne pouvait donc pas modifier **ce** choix. Avant de modifier l'apprentissage ou de lancer une nouvelle naissance, vérifier si une autre fenêtre **déjà naturellement produite** expose plusieurs candidats à `_consider_uncertain_affordance`.

Reprendre le témoin déterministe `dry-valley`, physiologie v4, **12 pas**, de `tests/i1/test_i1_natural_stage8_read_contrast_438.py` (#592, intégré). Ce test exécute déjà deux vies M11 indépendamment persistées (Q Stage8 normal / lecture Stage8 masquée), à naissance et carte appariées; il ne faut créer **aucune naissance supplémentaire** pour cet audit. Leur intervention expérimentale porte sur l'évaluation Stage8 et **pas** sur le classement Q antérieur. Ne pas confondre ces bras avec un témoin de classement amont.

## Observation passive

Lire **après commit et audit M11** les événements personnels `i1_unknown_affordance_proposed` produits par la cognition, sans appel supplémentaire au propriétaire TD ni au moteur. Pour chaque événement : pas et cycle, `option_ref`, `goal_ref`, `candidate_count`, `candidate_primitives`, commande sélectionnée, état et valeur Q **du gagnant uniquement**, hachage de la perception visible.

Conserver séparément les deux bras et le premier changement moteur déjà identifié par le protocole #438. Contrôler le schéma des champs et le fait que la commande sélectionnée figure dans les primitives disponibles. Utiliser exclusivement les journaux dont le nombre de générations, le hash et l'état M11 correspondent au snapshot publié. Ne pas assimiler l'absence d'un événement à l'absence de toute action possible.

## Interprétation préenregistrée

- Aucun événement authentifié : `NOT_EXPOSED`.
- Toutes les propositions ont exactement un candidat : `UPSTREAM_RANK_NON_DISCRIMINATING_IN_THIS_WINDOW`.
- Au moins une proposition contient plusieurs candidats : `MULTI_CANDIDATE_EXPOSURE_OBSERVED`. **Cela n'établit toujours pas une influence causale de Q**, car le journal ne donne pas les Q des perdants ni un choix alternatif contrefactuel.
- Si les deux bras divergent après une ablation Stage8, l'effet appartient au chemin évalué dans #438, **pas** au classement amont Q.
- L'effet du crédit différé `collecter → manger`, l'amélioration adaptive, la robustesse, la survie et une seconde ingestion restent `NOT_ESTABLISHED` sauf preuve indépendante.

N'ajouter **aucun** candidat, aucune action imposée, aucune carte privilégiée, aucun débit UC fictif, aucun oracle, aucun propriétaire, ni modification de I1/I0/TD/Stage8/Competition/Action Control. Les étapes de la preuve ne doivent pas être promues à L3 au seul vu du nombre de candidats. La CI exacte Python 3.11/3.12 est une vérification technique, pas une réplication statistique indépendante.

Si la fenêtre contient effectivement deux candidats, la suite doit mesurer les lectures Q réellement effectuées sur chacun **sans seconde consultation gratuite** avant de concevoir une intervention sélective; sinon, préserver le résultat négatif et rechercher une autre exposition naturelle déjà enregistrée.

## Extension prospective, après le verdict dry-valley, avant lecture des nouvelles sorties

Le run #40737092827 (head `ad57fc8741e41e587d8df1a529ef37954592ac1d`, 4/4 CI verts) a donné `NOT_EXPOSED` : aucun événement `i1_unknown_affordance_proposed` dans les deux bras `dry-valley` des 12 pas. La recherche du premier classement alimentaire multi-candidat demeure ouverte.

**Nouvelle fenêtre, définie sans consulter ses nouveaux comptes** : reprendre les **18 pas entiers** des deux naissances M11 appariées `oasis/b` du test `tests/i1/test_i1_natural_selective_collect_q_305.py` (#598). Ce test exécute déjà ces deux vies pour le masquage aval Stage8 limité au pas 18 ; la présente extension lit exclusivement leurs événements cognitifs publiés et audités **après** l'exécution. Ne pas ajouter d'étape, d'individu, d'environnement ou d'appel Q. Les bras restent identiques en histoire motrice jusqu'au pas 17 ; au pas 18 leur sélection amont est hors portée de l'intervention aval.

Avant lecture des résultats, extraire pour chaque `i1_unknown_affordance_proposed` de chaque cycle : `step`, `cycle`, `option_ref`, `goal_ref`, `candidate_count`, `candidate_primitives`, `command`, `learned_value_status`, `learned_value` du **gagnant uniquement** et `visible_input_sha256`. Conserver tous les événements, pas seulement le dernier. Vérifier un nombre de candidats strictement positif et égal au nombre de primitives, la présence de la commande gagnante et son caractère perceptuellement disponible. Lire seulement le registre M11 déjà authentifié, sans postuler de candidat perdant ni reconstruire des évaluations Q inobservées.

**Décision préenregistrée, par bras** :
- `NOT_EXPOSED` : zéro événement;
- `UPSTREAM_RANK_NON_DISCRIMINATING_IN_THIS_WINDOW` : événements mais toujours un candidat;
- `MULTI_CANDIDATE_EXPOSURE_OBSERVED` : au moins un cycle comporte au moins deux candidats. Cette catégorie est une exposition à un tri, **pas** une preuve que Q diffère entre candidats ni qu'il modifie le choix;
- publier séparément les cycles multi-candidats avec gagnant `learned` vs `unlearned`. Une valeur Q apprise du gagnant ne renseigne pas les Q perdants.

Dans tous les cas `UPSTREAM_Q_CAUSAL_CHOICE_NOT_ESTABLISHED`, `INSTRUMENTAL_ADAPTIVE_BENEFIT_NOT_ESTABLISHED`, `LONG_TERM_SURVIVAL_NOT_ESTABLISHED` ; pas de GO, réglage moteur, règle alimentaire ou ablation amont. Les bornes et les deux versions Python sont des répétitions techniques d'un même scénario déterministe, non des cohortes indépendantes.
