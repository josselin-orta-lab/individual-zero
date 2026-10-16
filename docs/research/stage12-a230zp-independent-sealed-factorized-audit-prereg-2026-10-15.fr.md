# A2.30-ZP · préenregistrement d'une contre-expertise indépendante des archives ZO scellées

**15 octobre 2026.** Audit **rétrospectif** : les résultats de ZO sont **déjà connus** et sa CI a réussi. Ce protocole est rédigé **après les résultats ZO mais AVANT toute ligne de code ZP**. Il ne peut être présenté comme une réplication physique ni comme une nouvelle cohorte prospective. Son rôle est de vérifier sans partage de logique de modélisation l'intégrité des données originales et les résultats annoncés.

**Source physique originale** : GitHub Actions [run #38792466785](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38792466785), commit `50185e2db1dc03188aca372fa0e3b854eaf85915`, deux artefacts `a230zo-py3.11` et `a230zo-py3.12`. Chaque artefact contient exactement les cinq fichiers JSON ci-dessous, dont le SHA-256 a été **relevé avant code ZP**. Ils sont identiques octet par octet entre les deux Pythons ; ceci n'en fait PAS deux échantillons indépendants.

| Fichier scellé original | SHA-256 |
|---|---|
| `a230zo-physical-training.json` | `4ad8489762b32ce21f17809121893a7afd7d96500464124ca28492d87a57d166` |
| `a230zo-frozen-partial-model.json` | `d649d5dd716972824f4190dee4ae3dc5818dc323bb757a1197adffa5232d2dee` |
| `a230zo-original-heldout-worlds.json` | `cc9bd690974c08b831e0ffc0d785040b3fba0a0875b8ce5fd99d8e33043607ef` |
| `a230zo-prospective-scores.json` | `0a8393c50d9200019435c1027f952ca5e1d9b99efb64d62ddad39184a2fe0354` |
| `a230zo-summary.json` | `d772ebe965238347396da77d40841c39e14573f964bfede50527714601fcd53c` |

## Critères de contre-expertise

1. **Indépendance du reviewer :** aucune importation du runner ZO, de `WorldBody`, `EquipmentCorpusRecorder`, `FrozenTableEquipment`, `SimulatorPlanner`, d'I0 ou de l'Oracle. Le code reconstruit la matrice, les deltas et les refus avec **son propre algorithme de lecture** depuis les états JSON first-person et les reçus externes. Seule l'utilitaire transversal de sérialisation déterministe SHA est permis.
2. Vérifier unicité, égalité byte-à-byte et SHA complet des **cinq** fichiers dans **les deux** artefacts d'origine, sans substitution de résultat généré. Vérifier 16 recettes TRAIN, 64 NOMINAL, 24 HIDDEN, 16 BOUNDARY et **120 identités physiques** uniques avec un acte chacune ; les fichiers doivent être relisibles et les SHA physiques de chaque exemple recalculés.
3. Vérifier intégralement les 16 transitions TRAIN et la séparation temporelle; reconstituer les six deltas par `MOVE_E` et `COLLECT_B` **uniquement depuis l'entrée observable et la sortie réellement enregistrée**, sans lire `physical_config_sha256`, effets B cachés ni autre label lab. Contrôler l'identité de ce modèle avec l'archive gelée et son SHA, et avec les 104 prévisions enregistrées.
4. Vérifier chacune des 104 racines HELDOUT : précondition sensorielle, corps loin ou proche des limites, comparaison du hash `SimulationState×PrimitiveCommand` aux 16 exemples sources, prédictions partielles reconstituées indépendamment, erreur numérique par dimension, cause physique externe terminale/blessure/échec. **Toute** sortie `safe`, `terminal=False`, `integrity=100` ou `next_adjacent` inventée doit faire échouer l'audit, même si la classe de monde est bénigne.
5. Démontrer l'indiscernabilité des **32 paires bénin/létal B** dans le nominal, et des **24 interventions cachées** par appariement exact de la première perception avec le nominal correspondant, sans injecter leur label dans la fonction de projection.
6. N'attendre **aucun** taux de sécurité. Les résultats connus à recompter (sans re-déclarer comme prospectifs) sont : exact full-state 0/104, delta partiel nominal 64/64 exact sur six dimensions, 16/16 `ABSTAIN_CLAMP`, 8/8 effets primitifs supprimés qui produisent une erreur de prévision, 8/8 blessures dont l'intégrité était justement **UNKNOWN**, 4/4 décès de mouvement pour lesquels la terminalité était justement **UNKNOWN**. Zéro ingestion, zéro vie autonome, zéro UC vécue.
7. Contrôles adversariaux contre le reviewer à produire dans des tests dédiés : faux hash d'archive, exemple de formation provenant d'HELDOUT, command target `manger(B)`, duplication de monde, action non candidate, premier état contenant `lethal_zone`, faux refus d'une borne, surestimation 64/64 avec score altéré, nouvelle observation postmortem, terminal `False` injecté dans la projection, compteur de mortalité modifié, origine Oracle fictive, modèle A prétendument installé sur un vrai individu. La résistance de l'auditeur à ces falsifications est un résultat technique distinct.
8. Bien distinguer **l'audit de cohérence des archives**, qui est indépendant du runner et peut être PASS, d'une reproduction du moteur physique, qui **ne l'est pas** ici : le fait que `WorldBody.apply` ait bien été exécuté est attesté par le script source et la CI ZO originale, pas par la lecture statique de fichiers ZP.

## Décision

**PASS technique ZP** seulement si la restitution est entièrement vérifiable sur les deux versions Python et si les contrôles négatifs échouent tous correctement. Un PASS ZP renforce la preuve étroite de **transfert empirique de six variations observables dans le sous-domaine nominal**, **pas** la sécurité du mouvement, l'acquisition vécue par I0, la prévision d'un vrai `SimulationState`, la planification de repas ou le jugement d'agence subjectif.

Aucun changement au MVP v1.3.1, aux modules `src/i0`, Stage9/DC-05, M11, Oracle, UC. PR #208 reste DRAFT. Le suivi GitHub #110 est administrativement clos à la date de vérification; aucune réouverture automatique ni certification cognitive. Déploiement : NO-GO.
