# A2.30-ZS : preuve temporelle scellée avant 104 actions physiques tenues à l'écart

**15 octobre 2026.** Protocole de ce bras prospectivement déposé **avant code et monde ZS** au commit `8ae4f26650bdb5f47f474051763bd8c91aba7afd`, PR [#214](https://github.com/josselin-orta-lab/individual-zero/pull/214). Expérience originale **figée** : [GitHub Actions #38801117723](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38801117723), commit `804e2ebb653278f18bd85aa364015acffd3bdb0e`. CI source : **quatre jobs PASS**, `seal-before-physics` et `realize-after-seal` pour chacun des Python 3.11 et 3.12 ; **20 tests adversariaux PASS par version**. Cette expérience respecte la séparation de processus établie par les deux jobs du workflow, avec `needs: [seal-before-physics]` comme condition obligatoire de la phase physique.

## Problème corrigé

ZO (#208), même si son modèle était réellement figé avant les mondes tenus à l'écart, enregistrait la prédiction par monde seulement *après* l'ensemble des observations physiques. ZP (#210) avait constaté l'absence de preuves **par prédiction enregistrée avant l'acte**. La première expérience ZS du bras #213, menée en parallèle, a scellé chaque prévision dans un **même processus** immédiatement avant son acte. Le présent bras **distinct** #214, malgré le même préfixe d'étude ZS adopté simultanément, renforce spécifiquement cette séparation : **toutes les 104 prévisions sont émises, synchronisées et exportées dans un premier job avant la moindre action physique heldout dans le second job**. Les sources sont distinguées par leurs SHA et runs, jamais confondues statistiquement.

**Cette procédure ne fait pas d'un modèle partiel un modèle complet et ne prouve aucune sécurité.**

## Chronologie vérifiable depuis la source CI

1. Dans le **premier job**, 16 mondes sources extérieurs sont réellement exécutés (16 actions `WorldBody.apply`). Le modèle empirique est appris sur exactement 8 observations de `MOVE_E` et 8 de `COLLECT_B`. Son empreinte canonique `d837d17d285c20ac53a55f3f78818d4f2abfa7cd387b6232e3c105bd9ac25171` est identique au modèle ZO/ZP précédent.
2. Le premier job construit les 104 autres mondes en état **non agi**, capture les seules perceptions accessibles, produit les 104 prévisions des six variables corporelles/spatiales autorisées, sans `integrity`, terminalité, sûreté ou prochaine adjacency. Les trois fichiers (entraînement, modèle, prévisions) sont écrits **une fois**, avec `flush + fsync`, puis le manifeste `a230zs-source-seal.json` est scellé avec une empreinte SHA-256 **`c5157c83a78ad0a3ce2a071e14d05cd6365aff2e1d74caeefdbf3686363241c5`**. Le compteur physique heldout est **0** à ce moment.
3. Le premier job **termine avec succès** et publie son artefact. Le second job ne peut démarrer qu'ensuite, charge les octets originaux et vérifie intégralement **les 104 entrées perceptives, commandes, prévisions, hashes, modèle et manifeste avant la première action heldout**. Les prévisions d'origine ne sont jamais remplacées par des sorties calculées après les actes. Le second job construit puis exécute physiquement les 104 mondes, produit les reçus externes et compare leurs conséquences aux seules prévisions préexistantes.
4. Une relecture du SHA après les actes confirme l'identité des fichiers de la première phase. Les octets des sept fichiers de résultats (quatre source, trois outcome) sont **strictement identiques** entre les deux jobs Python 3.11 et 3.12. **Deux Pythons ne représentent pas deux échantillons scientifiques indépendants.**

SHA-256 des fichiers d'origine : le [préenregistrement ZT associé](https://github.com/josselin-orta-lab/individual-zero/blob/science/stage12-b-a230zs-preaction-forecast-commit-20261015/docs/research/stage12-issue110-b-a230zt-independent-split-job-seal-prereg-2026-10-15.fr.md) conserve les **sept empreintes intégrales fixées avant le développement de ZT**, sans réécriture.

## Résultats physiques et limites quantitatives

| Condition physique | Mondes/actions | Prévisions scellées et scores externes |
|---|---:|---|
| Entraînement physique source | **16** | 16 observations avant tout test ; aucune fuite heldout |
| Test nominal | **64** | **64/64** prédictions partielles exactes sur six composantes numériques ; 32 paires de toxicité B cachée avec mêmes observations et prévisions |
| Test avec effet caché | **24** | **4** décès moteurs cachés, **8** blessures d'intégrité non annoncées, **8** échecs physiques de commande donnant une discordance numérique |
| Test de clamp des variables corporelles | **16** | **16/16** abstentions `abstain_clamp`, sans prédiction des six conséquences |
| **Total** | **120 mondes, 120 actions** | **104 prévisions pré-action** : 88 prédictions partielles et 16 abstentions |

Tous les **104** états tenus à l'écart ont une clé exacte `SimulationState×PrimitiveCommand` **inconnue** du modèle tabulaire à 16 exemples. L'amélioration est donc une projection empirique factorisée sur six deltas **visibles**, sans généraliser automatiquement l'état complet. Les effets cachés ne deviennent ni certitudes ni entrées cognitives. Aucun `manger(B)` n'a été entraîné ou exécuté; collecte physique B de laboratoire ne garantit pas un aliment sûr.

**Critère temporel ZS1 : PASS sur cette nouvelle réplication** par la preuve conjointe du protocole GitHub à deux jobs, du scellement fsync et SHA, de la vérification initiale de toutes les prévisions dans le second processus et des 104 jointures intactes. **Critère numérique ZS2 : PASS borné** aux six composantes et à cette grille déterministe. **Frontière épistémique ZS3 : conservée**, aucune prédiction de `safe`, `terminal`, `integrity`, `next_adjacency`. Ces observations ne constituent pas une estimation probabiliste de sécurité ni une preuve de compétence vécue chez I0.

**Aucun nouvel I0 né, aucune UC I0, aucun jugement subjectif, aucun changement de `src/i0`, de Stage9/DC-05, M11 ou du MVP v1.3.1.** A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 CLOSED **administrativement**, prédicteur expérimental externe, **déploiement NO-GO**.
