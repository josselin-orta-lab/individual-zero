# Stage 11 : coût UC total du filtrage géographique, ablation publique

**Date :** 11 octobre 2026 (Europe/Paris). **Nature :** développement logiciel, scénarios publics connus. **Ce n'est ni une campagne held-out ni une preuve scientifique.**

## Méthode et provenance

- [Protocole expérimental logiciel déclaré avant modification et avant résultat](stage11-geographic-total-uc-ablation-protocol.en.md).
- **Commit de code testé :** `a3c1b23310b7dfbc801ed063a1e306ea95a49dbf`.
- [GitHub Actions #38112816144](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38112816144) : **761 tests unitaires réussis** sous Python 3.12 (67,070 s de temps de tests), plus contrôle smoke de trois cycles.
- Reproduction : `python -m lab.stage11_geographic_uc_probe`.
- Protocole versionné : `stage11-public-geography-total-uc-ablation-dev-v1`.
- Quatre dispositions publiques, **six pas de monde** chacune, même WorldPhysics, même Equipment figé, même position et état corporel initiaux, mêmes règles et faits de sécurité.
- Deux runtimes I0-vNext indépendants par disposition, avec un seul interrupteur différent : `geographic_preflight=False` contre `True`. Chaque configuration possède un identifiant de version distinct ; l'ancienne voie est reconstruite sur **le code actuel**, et non revendiquée byte-identique à un ancien commit Git.
- L'ancien comportement conserve le veto d'Action Control. La nouvelle voie retire avant Planning les seules directions jugées `inadmissible`. Un statut `indeterminate` reste éligible.

Les métriques de calcul proviennent **exclusivement des événements `compute_charge` journalisés**. Les UC acceptées sont effectivement consommées ; les UC demandées mais refusées sont recensées séparément, sans être additionnées à la consommation. Les UC ne sont jamais une récompense, une mesure CPU ou une valeur d'option.

## Résultat : consommation globale, tous modules confondus

| Monde public | Sans préfiltrage (UC) | Avec préfiltrage (UC) | Différence absolue | Variation relative |
| --- | ---: | ---: | ---: | ---: |
| Obstacle au nord | 193 | 215 | +22 | +11,4 % |
| Couloir vers l'est | 85 | 91 | +6 | +7,1 % |
| Créature visible au nord | 99 | 107 | +8 | +8,1 % |
| **Zone létale connue au nord** | **235** | **215** | **−20** | **−8,5 %** |

**Conclusion circonscrite :** l'optimisation économise réellement 20 UC au total lorsque l'interdiction connue provoquerait une replanification répétitive. Sur les trois cartes où aucun candidat n'est exclu, le préfiltrage est un pur surcoût dans ces petites trajectoires. Aucune promesse générale de performance n'est justifiée.

## Décomposition du scénario létal connu

| Mesure, six pas | Sans préfiltrage | Avec préfiltrage |
| --- | ---: | ---: |
| UC Planning totales acceptées | 52 | 32 |
| UC `planning_build` acceptées | 52 | 10 |
| UC `geographic_admissibility_preflight` acceptées | 0 | 22 |
| Rejets géographiques de Planning | 21 | 0 |
| Directions exclues par contrôle canonique | 0 | 4 |
| Cycles cognitifs | 23 | 23 |
| Déplacements géographiques appliqués | 2 | 2 |
| Positions distinctes physiquement perçues | 3 | 3 |
| Visites en zone létale connue | 0 | 0 |
| UC demandées mais rejetées | 0 | 0 |

Les autres modules consomment la **même** quantité d'UC dans les deux conditions de ce scénario. Le gain net de 20 UC est donc ici expliqué par `planning_build` (42 UC de moins) moins la préconsultation Action Control (22 UC supplémentaires). Les quatre directions interdites ont été filtrées lors de pas physiques distincts, et jamais promues en preuve causale.

Sur les trois autres dispositions, `planning_build`, les mouvements, les positions perçues et les cycles cognitifs sont identiques entre conditions ; seule la charge de préconsultation s'ajoute (+22, +6, +8 UC). Dans **aucune** des huit exécutions, une requête de budget n'a été rejetée.

## Empreintes de reproductibilité

| Monde | SHA-256 des entrées comparées | SHA-256 du résultat |
| --- | --- | --- |
| Obstacle nord | `2d5bbffd64d01045af06bfec558d641652627fd44ad74dc42b054b8d23b09b1a` | `506ff7dd84abdbbe56b9b3403605ae944d16db345f370a60d0b3d73d7632ce44` |
| Couloir est | `2ac1be7839ac525cbd859a6d48d5944f2020519ae72cd0575a992f81a214ad65` | `0b59cdc14b0a9716fa26b2c7398d1025f53deaea2217b09957ab5a7898438278` |
| Créature nord | `eb46ff488da3366e63664b460b268f744e3c271e8d9d26af3a5dd6124df78048` | `e6af6a8820294586a2face2bc61214bdb1739ad5a89f7c97b57385fe223de7f4` |
| Létal connu nord | `fb825847d97c29977e117c4c59c7ae08fef9792be875c6fb1842e5a65b6a12e4` | `d582a3c301bb999f591b71d979c5a63f63de27ebe669ae0402f7ca466e5ea6f0` |

Têtes des journaux en condition **sans / avec préfiltrage**, respectivement :

- Obstacle : `5cf90e53e2519e353136a194ce4a756a79bb531c1c6c9ddb4ce5146177740147` / `50ae57e8423d8dda4cd0f9c1b6db746f1b19f16bb445467854dcbec91bdc370f`.
- Couloir : `3c2ce7591df52432be32f95d3fe44467ed6c1036c2072cf7a7c42d07e877706e` / `abda9c3ded128211e5db1d60e9c56de0b8f3bdd903afa78cf1ef3c70cd8e09a5`.
- Créature : `50da26d404c51ab7492e089ed614e56a8907589939303d027579ed5ad35f239b` / `faa64338e8bd4bb54b6c8cdde31dd921074959dc904487991b5aa37b7e1ac112`.
- Létal : `6e41163e20f83a6eff6da552fb4b6484954767019a4e7a81c9cc6d65172782a1` / `a80bdfc9aca14c8516efc8ffee157b6efa94596df42e86da109cdd2854e866b2`.

Les tests contrôlent les journaux via `journal.verify()`, la cohérence entre ledger et captures Perception, l'égalité de deux réexécutions complètes du scénario létal et l'absence de visite en position occupée ou létale connue.

## Interprétation et prochaines étapes

Ce résultat établit uniquement que l'optimisation v3 réduit ici les UC lorsque des refus inutiles seraient répétés. Le coût systématique de la préconsultation mérite un incrément distinct, **préenregistré avant de modifier ses règles** : par exemple, éviter de contrôler des voisinages où Exploration ne dispose d'aucune nouvelle frontière perceptible, sans introduire de cache permanent, modifier la politique ou masquer des résultats incomplets par manque d'UC.

À traiter séparément : impasses après exploration de toutes les cases adjacentes, risque létal **inconnu** et restauration après rollback, mode dégradé sous budget strict, robustesse sur d'autres cartes publiques déclarées, matrice Python multi-versions, suites Golden complètes et acceptation indépendante.

**Stage 11 toujours EN COURS. Stage 9 toujours SOFTWARE IMPLEMENTED / SCIENTIFIC VALIDATION PENDING / NO-GO. Aucune fusion ni publication d'une conclusion scientifique autorisée par ces chiffres.**
