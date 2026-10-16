# A2.30-G : témoin indépendant de fermeture du graphe connu, résultats

**15 octobre 2026.** Protocole préenregistré dans le commit \`34bbfcba776092d790e86ec7047bfbc92649e3be\`, **avant** le témoin logiciel. Code testé au commit \`20936469efb6bf9f7340dd760fe019a99d73155a\`. [CI GitHub Actions #38717100599](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38717100599) **SUCCESS Python 3.11 et 3.12**, avec tests adversariaux sur l'erreur de pruning, l'arête inconnue, la fermeture des self-loops et le témoin censuré par succès. Les deux interpréteurs téléchargent **le même** artefact original \`a230e-py3.11\` de l'exécution #38715999434 ; ne pas compter ces répétitions comme des naissances.

## Provenance

L'auditeur télécharge et vérifie l'artefact scellé A2.30-E au SHA \`2be8008d51ad0d8a02d4795739a828acfba72aac\`, les huit identités originales de naissance, les empreintes SHA-256 des journaux, les têtes de chaîne et les comptes d'événements via \`audit_export_bytes\`. **Zéro naissance supplémentaire, zéro nouveau pas physique**. Il réanalyse les **192 pas existants** dans huit vies et les **141 recherches réelles**.

## Résultat discriminant

| Observation du graphe de recherche réellement consulté | Nombre |
|---|---:|
| Recherches Stage6 A2.30-E réanalysées | 141 |
| Recherches \`incomplete_model\` | **121** |
| Recherches \`incomplete_model\` sans **aucune** première arête connue depuis l'état perçu initial | **121 / 121** |
| Recherches \`incomplete_model\` avec au moins une première arête connue | **0 / 121** |
| Divergences du BFS indépendant avec les noeuds effectivement développés | **0** |
| Arêtes alimentaires inconnues à la racine, appels répétés | **10** |
| Arêtes de déplacement inconnues à la racine, appels répétés | **416** |
| Sous-graphes entièrement clos certifiés | **0** |
| États connus arrivant à une limite de profondeur dans l'ensemble des recherches | **12** |

Le témoin reconstruit pour chaque recherche épuisée l'ensemble accessible uniquement à partir des arêtes **connues** dans le modèle. Il exige qu'aucune commande candidate ait été omise et que tout noeud prédit atteignable dans l'horizon ait bien été développé. Le résultat **0 divergence** ne démontre pas la correction de tous les aspects de Stage6 ; notamment la projection corporelle et l'évaluation de la condition d'objectif ne sont pas testables depuis les seuls SHA des successeurs stockés en A2.30-E.

**Démonstration bornée :** dans ces **121 recherches**, aucun chemin non vide ne peut être prédit par ce modèle depuis leur état initial, quelle que soit la profondeur de recherche. Une augmentation purement numérique de \`max_depth\` ne suffirait donc pas à trouver une trajectoire sans élargissement justifié des arêtes prédictibles ou nouvelle capture pertinente. Cela concerne un modèle exact à un instant et des objectifs non déjà satisfaits, **pas** l'impossibilité physique dans le monde, ni l'absence générale de compétence alimentaire.

## Classement scientifique

- **H1 fortement soutenue, niveau racine :** l'Equipment ne connaît aucune transition exploitable de départ dans les 121 recherches incomplètes. Les 10 tentatives alimentaires inconnues ne prouvent pas que \`manger\` est absent en général ; il s'agit d'appels répétés depuis des états locaux précis.
- **H2 profondeur seule non soutenue pour ce sous-ensemble :** si la première arête est absente, agrandir l'horizon ne rend pas une arête connue. Les **12 états à profondeur maximale** peuvent concerner d'autres recherches, sans preuve d'un objectif réalisable au-delà.
- **H3 pruning BFS non observée sur le graphe effectivement disponible :** témoin de parcours conforme et zéro omission de commande. H3 projection des états, modélisation des préconditions ou but non exclue ; la vérité de la physique n'est pas accessible au présent auditeur.
- **Impossibilité structurelle : non démontrée.** Aucun sous-graphe fermé complet n'a été observé, et la frontière inconnue empêche ce verdict.

## Travail restant

Identifier pour ces racines si le blocage tient surtout (a) à une commande jamais entraînée, (b) au décalage exact d'un ou plusieurs champs du \`SimulationState\` pourtant entraîné pour cette commande, (c) à une observation locale erronée. Comparer les états *accessibles* de chaque racine aux exemples physiques pré-nataux, avec examen des variables corporelles mais sans inférence automatique de causalité à partir du plus proche exemple. Tester ensuite une intervention réellement prospective, préenregistrée, sans projection omnisciente.

**A2.30 PARTIELLE**, Stage12 PARTIAL, issue #110 OPEN, PR #187 DRAFT. Aucun changement de modèle, de critères subjectifs, d'UC, de Stage9/DC-05 ou de norme MVP v1.3.1. Aucune validation opérateur n'est revendiquée.
