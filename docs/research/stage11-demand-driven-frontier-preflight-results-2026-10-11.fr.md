# Stage 11 : préfiltrage géographique à la demande, diagnostic UC v4

**Date :** 11 octobre 2026 (Europe/Paris). **Classification :** diagnostic logiciel sur mondes publics connus, non held-out. **Aucun verdict scientifique.**

## Traçabilité

- [Protocole déclaré avant toute modification de code et avant les observations](stage11-demand-driven-frontier-preflight-protocol.en.md).
- **Commit source effectivement testé :** `a585807da696e5f25a3fe0da2ec3914f52083371`.
- [GitHub Actions #38113317969](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38113317969) : **767 tests unitaires réussis en Python 3.12**, puis smoke vérifié. La matrice Python de référence et les longues suites Golden n'ont pas été exécutées par cette campagne.
- Commande de reproduction : `python -m lab.stage11_geographic_frontier_gate_probe`.
- Protocole du comparateur : `stage11-public-geographic-demand-preflight-dev-v1`. Les diagnostics existants de couverture et robustesse sont versionnés respectivement `stage11-public-frontier-coverage-dev-v3` et `stage11-public-frontier-layout-robustness-dev-v4`. Le diagnostic total-UC antérieur `stage11-public-geography-total-uc-ablation-dev-v1` **reste explicitement figé sur la configuration eager-v3** pour préserver son sens historique.

## Modification étroite

Quand le mode géographique est explicitement activé, Exploration relit les cellules adjacentes de **la capture Perception courante** et sa propre liste de sites physiquement visités. Si elle ne peut désigner **aucune case nouvelle et praticable**, `geographic_preflight_requires_frontier=True` évite la consultation préliminaire d'Action Control ainsi que sa charge de **1 UC Planning**. Aucun statut `sûr`, `interdit` ou `sous contrôle` n'est inféré de cette absence de nouveauté ; aucun cache intercycle n'est ajouté.

Dès qu'une seule cible potentiellement nouvelle existe, **l'intégralité du préfiltrage v3 demeure** : le service canonique de sécurité est consulté et facturé, seules les directions `inadmissible` sont supprimées avant le plafond de cibles, `indeterminate` reste éligible, et le veto final Action Control demeure inchangé. Une cible passable connue comme létale **reste un cas où la consultation est obligatoire même si aucun déplacement ne peut être effectué**.

Chaque cycle éligible où le v4 évite la préconsultation reçoit un événement technique `stage11_geographic_preflight_skipped` avec origine `perception_and_physical_visit_ledger`, `safety_decision=null`, `cached=false` et 1 UC évitée relativement à v3. Cet événement n'est ni une visite, ni une preuve causale, ni un signal de récompense.

## Consommation de calcul, trois configurations sur les mêmes six pas de monde

UC acceptées et effectivement consommées, tous modules confondus :

| Monde public | Sans préfiltrage | Préfiltrage systématique v3 | Nouveau v4 à la demande | UC économisées contre v3 |
| --- | ---: | ---: | ---: | ---: |
| Quatre cases adjacentes bloquées | 222 | 251 | **222** | **29** |
| Obstacle nord | 193 | 215 | **195** | **20** |
| Couloir vers l'est | 85 | 91 | **91** | 0 |
| Créature au nord | 99 | 107 | **102** | **5** |
| Zone létale connue au nord | 235 | 215 | **215** | 0 |
| Seule sortie nord connue comme létale | 280 | 251 | **251** | 0 |

Les variantes historiques (quatre premières cartes usuelles) et les deux nouvelles conditions extrêmes sont distinctes. La comparaison est une **ablation sur le code courant**, pas la reconstitution bit à bit d'un ancien commit.

### Contrôles de sécurité et de causalité

| Monde public | Préconsultations UC v3 → v4 | Cycles dont la préconsultation est évitée | Déplacements réellement appliqués, v3 = v4 | Sites réellement perçus, v3 = v4 |
| --- | ---: | ---: | ---: | ---: |
| Cases adjacentes bloquées | 29 → 0 | 29 | 0 | 1 |
| Obstacle nord | 22 → 2 | 20 | 2 | 3 |
| Couloir est | 6 → 6 | 0 | 6 | 6 |
| Créature nord | 8 → 3 | 5 | 3 | 5 |
| Létal connu nord | 22 → 22 | 0 | 2 | 3 |
| Sortie unique létale | 29 → 29 | 0 | 0 | 1 |

La voie sans préfiltrage présente **21** refus de Planning dans `known_lethal_north` et **29** dans `sole_north_known_lethal`. Les deux voies avec préfiltrage en présentent **zéro** sur ces scénarios. Aucun déplacement ne pénètre une zone létale connue ni une case occupée par une créature sur les trajectoires exécutées. Les six variantes n'ont subi **aucune demande de budget UC rejetée**.

Les résultats « sans préfiltrage » montrent également que le v4 n'est **pas** toujours la voie au coût total le plus faible : le v4 conserve +2 UC sur obstacle nord, +6 sur couloir est et +3 sur créature nord face à l'absence complète de préconsultation. Il conserve néanmoins l'économie de **20 UC** sur la zone létale connue et de **29 UC** sur la sortie uniquement létale, tout en évitant les refus de planification répétés.

## Empreintes SHA-256

| Monde public | SHA-256 des entrées | SHA-256 du résultat |
| --- | --- | --- |
| Cases bloquées | `3ef97b09e5219c159e210bf37ff0224623ae15f995a621c3e0193b2ec2e4c737` | `2ea187e883c3affe4908785bfa0e2f68badcb21c4fcf192e761b4e5e30b4a40a` |
| Obstacle nord | `5a8c773ea838f9635a5bc730754d603ab1a6aec47bc2655a8d3b25bab56742fe` | `d540d7c70057458cc6758e75e6e88ece7e09a38348250e35f8e19e681e5ad36f` |
| Couloir est | `70a2a94257944af0920c1d41ff7099e93c135ea7393092ea59c20002c2207087` | `1b886d82306ce25e6e63f00c0ca3793482328f60d02d24d461f7334003e45c8e` |
| Créature nord | `e6d112923a808ddf49bc5f54b3d78ff909dffc2279dfe049a368adad06e4b297` | `518b0e1a56dcfb5adf521f018411d14eabf15591457aedc49a752205a8b3d621` |
| Létal connu nord | `aecb0d365c6451f4e835bae02e3b0330f3dce23e69f92cba9ec9f12a5f242d8f` | `e5cd37e12abd7749362e64f7d84239f38ab1cf684fe94407cc8504ab0eabba9a` |
| Sortie unique létale | `8bf44fcb9fca097157e527fc226c1d49df1ec0ccaa059fc758c9981e57a428fd` | `0f487a9e5a743062282d920bb49e699086424e8e9a79a2a19b4606749d45ac3e` |

Les têtes des journaux pour les trois variantes sont enregistrées dans les lignes machines `stage11_public_demand_preflight` du job GitHub Actions. Le test vérifie `journal.verify()` sur chaque exécution et répète entièrement le cas sans frontière pour confirmer l'égalité exacte du résultat et des journaux à configuration identique.

## Limites et suites

Cette correction réduit du travail lorsqu'il n'existe **aucune frontière nouvelle accessible localement**, et non lorsqu'une frontière semble dangereuse, incertaine ou simplement peu prometteuse. Elle ne crée aucune cartographie globale, ne détecte pas les dangers invisibles, ne résout pas la navigation multi-étapes et ne démontre pas de sécurité à long terme. Le nombre de sites couverts ne prouve pas une généralisation cognitive.

Étapes restant à vérifier séparément : essai sous budget strict et mode dégradé, impasses après exploration de tous les voisins, dynamique des faits de sécurité avec restauration d'un snapshot, plans à plusieurs pas, mesures sur cartes publiques additionnelles préalablement déclarées, Python 3.11 de référence et Golden complets.

**Stage 11 : EN COURS. Stage 9 : SOFTWARE IMPLEMENTED / SCIENTIFIC VALIDATION PENDING / NO-GO. PR ouverte en brouillon, non fusionnée.**
