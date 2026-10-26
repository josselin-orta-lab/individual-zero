# Questions d'enquête scientifique (non normatives)

**Source :** [revue externe du 26 octobre 2026](COGNITIVE_ARCHITECTURES.md#6-hypotheses-de-recherche-et-criteres-de-validation). Ces hypothèses n'attestent ni succès de I1 ni statut de développement actuel. Vérifier les PR et `main` avant de commencer.

| ID | Priorité indicative | Question de recherche | I1 : mécanisme / issue |
| --- | --- | --- | --- |
| H01 | P0 | Le signal de valeur pénalise-t-il certaines améliorations corporelles ? | ValueAndNeeds, [#306](https://github.com/josselin-orta-lab/individual-zero/issues/306) |
| H02 | P0 | Le crédit différé bénéficie-t-il réellement aux actions préparatoires ? | TD/Q, [#305](https://github.com/josselin-orta-lab/individual-zero/issues/305) |
| H03 | P0 | Une forme consolidée persiste-t-elle et change-t-elle les décisions après récupération froide ? | Stage10 / owners, [#293](https://github.com/josselin-orta-lab/individual-zero/issues/293) |
| H04 | P1 | Un épisode ancien est-il accessible via un rappel sélectif et payé en UC ? | Memory, [#535](https://github.com/josselin-orta-lab/individual-zero/issues/535), [#538](https://github.com/josselin-orta-lab/individual-zero/issues/538) |
| H05 | P1 | Les effets d'action sont-ils prédits hors échantillon à partir d'expériences vécues ? | CausalModel / lived_prediction, [#526](https://github.com/josselin-orta-lab/individual-zero/issues/526) |
| H06 | P1 | Un souvenir influence-t-il la sélection indépendamment des autres prédicteurs ? | Stage8 / Competition, [#512](https://github.com/josselin-orta-lab/individual-zero/issues/512) |
| H07 | P1 | Le sommeil et l'attente produisent-ils des connaissances contextuelles de leurs effets différés ? | Memory / Stage10, [#467](https://github.com/josselin-orta-lab/individual-zero/issues/467), [#541](https://github.com/josselin-orta-lab/individual-zero/issues/541), [#543](https://github.com/josselin-orta-lab/individual-zero/issues/543) |
| H08 | P1 | Une segmentation par surprise observée préserve-t-elle les épisodes rares ? | Memory / Perception |
| H09 | P2 | Une procédure dérivée des expériences répétées diminue-t-elle le coût UC sans rigidité ? | Consolidation / Competition, [#326](https://github.com/josselin-orta-lab/individual-zero/issues/326) |
| H10 | P2 | Urgence prédite et intensité de besoin sont-elles deux signaux utiles distincts ? | ValueAndNeeds / GoalManager, [#307](https://github.com/josselin-orta-lab/individual-zero/issues/307) |
| H11 | P2 | La confiance reflète-t-elle les contradictions, l'incertitude et le changement de contexte ? | CausalModel / Metacognition |
| H12 | P3 | Des projections internes courtes aident-elles davantage qu'elles ne coûtent ? | Planning / CausalModel |

## Grille de validation
- **A : logiciel** : sources de première personne, indices authentifiés, UC comptés, cas invalides, M11, mort irréversible, aucun oracle.
- **B : capacité active** : observation sur une naissance naturelle, preuve du propriétaire consulté ; aucun helper dormant assimilé à une capacité.
- **C : effet causal** : ablation ciblée, contrôle Q/Stage6/P40, graines et mondes appariés, différence dans l'action réellement exécutée.
- **D : généralisation** : contradictions, situations nouvelles, réplications indépendantes, durabilité, coût des calculs et résultats négatifs.

Les détails des 12 hypothèses, leurs témoins et critères de validation sont archivés dans [le dossier](COGNITIVE_ARCHITECTURES.md#6-hypotheses-de-recherche-et-criteres-de-validation). La revue est un **registre d'idées vérifiables**, pas une autorisation d'ouvrir 12 PR ni de forcer I1 à se comporter d'une manière donnée.

**Doublons à éviter :** travaux déjà ouverts autour du rappel long terme et des fragments d'action, [#535](https://github.com/josselin-orta-lab/individual-zero/issues/535), [#538](https://github.com/josselin-orta-lab/individual-zero/issues/538), [#541](https://github.com/josselin-orta-lab/individual-zero/issues/541), [#543](https://github.com/josselin-orta-lab/individual-zero/issues/543). Les issues ne prouvent pas que leurs PR sont intégrées.
