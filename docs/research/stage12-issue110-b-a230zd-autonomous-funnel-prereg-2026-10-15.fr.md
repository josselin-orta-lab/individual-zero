# Individual Zero : A2.30-ZD, préenregistrement d'une contre-analyse des véritables vies ZB

**15 octobre 2026, avant tout code ZD et avant analyse ZD des événements détaillés.** Ce préenregistrement est **rétrospectif** : les résultats globaux ZB ont été lus et sont connus. Il n'autorise donc aucun qualificatif de campagne prospective nouvelle. La base est la [PR #197](https://github.com/josselin-orta-lab/individual-zero/pull/197), head `5df1be65f763d98a7657caade102123e51718fe4`. Les données **originales** proviennent exclusivement du run [#38767643472](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38767643472), code des naissances `2a19742df22f27752635203304097134a3009c45` ; artefacts `a230zb-py3.11` et `a230zb-py3.12`.

## Motivations et hypothèses bornées

Les nombres **déjà connus avant ZD** (ne constituent pas des prédictions falsifiables originales) : **12 vies**, **384 pas**, **0 collecte et 0 ingestion de berry_b**, **196 recherches Stage6** dont **174** sans transition prédictible à la racine, **10** recherches `plan_found`, **18** arêtes racine disponibles cumulées, **20** jugements de double portée, **8** ingestions d'autres espèces et **0 décès**. La mortalité `experiment_stopped` à 32 pas n'est pas un décès réel.

- **ZD1 : visibilité et éligibilité ne sont pas prédiction.** Pour chaque vie `B_LOCAL`, la capture `SimulationState` accessible initiale doit contenir `berry_b` sur la case et la fonction d'énumération pure `SimulatorPlanner.candidate_commands` doit inclure `collecter(berry_b)`; dans `B_EAST`, le voisin est doit signaler B et être passable, mais `collecter(B)` n'est pas encore légal à la racine. Le monde `B_NONE` ne doit annoncer B ni localement ni à l'est. La présence d'une commande candidate ne constitue jamais une option évaluée ou choisie.
- **ZD2 : attribution causale de l'absence d'action.** Reconstituer depuis les journaux canoniques des 384 étapes exécutées : commandes physiques, motifs B, objectifs attestés, résultats et diagnostics Stage6, enregistrements d'option, évaluation Stage8, traces de compétition et refus UC vécus. Classement **mutuellement exclusif, avec catégorie `insufficient_evidence` explicite**, sans inventer de proposition B non journalisée. Une proposition alimentaire générique ou un `plan_found` ne doit pas être recodé comme proposition B.
- **ZD3 : ne pas créditer la rareté de la concurrence au mauvais mécanisme.** Distinguer parmi les 196 recherches Stage6 : `plan_found`, `partial_progress`, `incomplete_model` et statut de racine. Vérifier que les 10 plans trouvés **ne sont pas présentés comme des plans B exécutés**. Quand l'option alimentaire n'existe pas, ne pas comptabiliser une perte contre l'exploration. Quand elle existe et est évaluée, documenter les seuils/compétitions de la vraie même étape, pas une comparaison entre étapes différentes.
- **ZD4 : frontières mémorielles et mortelles.** Relire les **12 WAL/journaux immuables** via `audit_export_bytes` et P48; recouper les sommes contre `a230zb-summary.json`, hash de journal, nombre d'événements, identité, évitement de `berry_b` et paire (bienveillant/mortel) avant exposition. Le banc **ne décide pas** des commandes, ne reçoit pas d'Oracle et ne fait naître aucune vie ZD.

## Données et méthode fixées

Télécharger les deux artefacts **originaux du même run**, comparer les fichiers `a230zb-summary.json` et les 12 `canonical.jsonl` **octet par octet** ou, si une divergence de sérialisation par Python est constatée, publier la nature de la divergence et bloquer toute inférence qui exige l'identité des trajectoires. Valider les hash SHA-256 stockés dans les résumés de vie, les têtes et nombres d'entrées du journal canonique, les 384 paires `command_experienced` / `world_transition_experienced`, les bornes et l'absence de morts restaurés.

Mesurer indépendamment au moins :
1. Nombre de mondes B absente/locale/à l'est par profil; vérification des capacités natives initiales sur la **même représentation accessible** avant le premier acte et sans lecture de l'effet `hidden_B_external_only`.
2. Par pas, existence d'un but alimentaire **attesté**, d'une recherche Stage6, d'une option de planification **effectivement enregistrée**, d'une option évaluée, franchissement du seuil de compétition et commande finalement vécue. Séparer option liée au but alimentaire de la preuve d'une cible **berry_b** dans un plan. Les événements journalisés ne contenant pas cette précision aboutissent à **inconnu**, jamais à oui.
3. Refus UC réels avec opération et étape, sommeil/capture réduite, motif d'action, propositions et exécutions des commandes B. Les obstacles physiques à B sont des témoins externes, pas des causes connues subjectivement par I0.
4. Regroupements par 12 vies et 6 contrastes cachés, sans jamais convertir une différence latente jamais vécue en preuve d'agence ou de détection de toxicité.

Le nombre de catégories n'est **pas** choisi d'après leurs résultats. Un champ source absent, les chemins journal non uniques ou une violation de préconditions impliquent un **FAIL** de provenance. Si le journal ne conserve pas une information requise pour distinguer deux causes, écrire `not_identifiable_from_receipts` et ne pas lancer de campagne additionnelle sur cette base sans protocole préalable.

**Falsifications obligatoires :** B inventée dans une capture initiale; option prétendue sélectionnée sans évaluation/compétition attestée; commande B recodée sans commande+transition; succès `plan_found` converti en ingestion; `compute_charge` refusé attribué à B sans lien d'étape/option; altération de hash WAL/journal; paire de variantes confondues avec la même identité; capture subjective après une issue terminale.

## Critères de conclusion

- PASS informatique uniquement si la relecture des deux archives et les contrôles négatifs passent sur Python 3.11 et 3.12 et si les totaux ZB restent inchangés.
- **Pas de validation de capacité alimentaire B** sans commande vécue; **pas d'identification du verrou unique** sans observations discriminantes de propositions, compétition et UC du même pas. Une commande candidate visible est nécessaire, mais pas suffisante, à l'action planifiée.
- Le verdict n'est pas une nouvelle preuve de réussite scientifique ni un test d'amélioration prospective. Une nouvelle cohorte future, si justifiée, devra être **préenregistrée** avant naissance, sans commandes imposées ni prior de sécurité de `berry_b` provenant du laboratoire.

**A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN; ZD purement archivistique; aucune modification de `src/i0`, de la spécification normative v1.3.1, de Stage9/DC-05, des UC ou du WAL. PR de recherche DRAFT, pas de fusion.**
