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