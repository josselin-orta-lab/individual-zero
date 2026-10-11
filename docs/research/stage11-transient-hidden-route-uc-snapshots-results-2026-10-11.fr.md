# Stage 11 : danger caché transitoire, retour observé, UC strictes et snapshots

**11 octobre 2026. Diagnostic de développement public : NON HELD-OUT, NON GOLDEN, NON SCIENTIFIQUE.** Source normative inchangée : `docs/architecture/reference/en/mvp-specification-v1.2.1.md`. **Stage 11 EN COURS ; Stage 9 NO-GO scientifique ; PR #25 Draft et non fusionnée.**

## Antériorité, code, exécution

- Protocole [stage11-transient-hidden-route-uc-snapshots-protocol.en.md](stage11-transient-hidden-route-uc-snapshots-protocol.en.md) enregistré **avant** le code et les tests, commit `5ba46e53a4679aa43b56ad0235d67d0651a08fd5`.
- Sonde versionnée `src/lab/stage11_transient_hidden_route_probe.py` au commit `aa918bda6dbc1afcec00e0e1763190382b1ce5a2` ; deux tests additionnels dans `tests/test_stage11_transient_hidden_route_uc_snapshots.py`, SHA de code et test **`00619fecae037269b60b47cff0141a4e7019adc1`**.
- [GitHub Actions #38134913304](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38134913304) **SUCCESS**, Python **3.12.15**, **891/891 tests PASS** (`Ran 891 tests in 129.235s`), bootstrap réussi. Le job `ci-full` a été intentionnellement ignoré. À cet instant, **pas de nouvelle validation Python 3.11 ni de campagne Golden scientifique** sur le SHA de ce diagnostic.
- La sonde a imprimé **8 lignes** `stage11_public_transient_hidden_route=` dans les logs. Chaque condition est réexécutée dans un autre runtime de naissance avec **le même calendrier de snapshots aux pas 4 et 5**, puis deux restaurations **après** les dix transitions physiques ; les objets de preuve, octets canoniques du journal et hash final sont exactement égaux entre ces exécutions indépendantes. Ce contrôle n'essaie pas de rejouer les pas physiques 5–10 dans la même branche après une restauration.

## Matrice publique : dix pas physiques par condition

Les deux variantes reçoivent les deux mêmes opérations externes `set_danger_zone` aux pas **3** puis **5**, journalisées avant application. Le témoin impose `active=False` aux deux dates ; le monde exposé impose `True` au pas 3 puis `False` au pas 5. Le danger est sur (3,2), **caché** du Perception et des facts de sécurité initiaux. Les budgets sont (Planning UC, Exploration UC), dans les enveloppes déjà versionnées du dépôt.

| Budget | Variante | Positions Perception distinctes | Transits routés appliqués | UC Planning route-search acceptées | Dommages physiques | Intégrité finale |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 0 / 0 | Témoin | 1 | 0 | 0 | 0 | 100 |
| 0 / 0 | Danger transitoire | 1 | 0 | 0 | 0 | 100 |
| 3 / 4 | Témoin | 3 | 0 | 40 | 0 | 100 |
| 3 / 4 | Danger transitoire | 3 | 0 | 40 | 0 | 100 |
| 4 / 4 | Témoin | **5** | **2** | 25 | 0 | 100 |
| 4 / 4 | Danger transitoire | **3** | **2** | 5 | **10** | **90** |
| 4 / 0 | Témoin | 1 | 0 | 0 | 0 | 100 |
| 4 / 0 | Danger transitoire | 1 | 0 | 0 | 0 | 100 |

À 0/0 et 4/0, l'individu reste sur (2,2) pendant dix captures ; aucune exposition à la zone (3,2), aucun transit routé. À 3/4, les deux variantes atteignent (4,2) puis stagnent, sans transit. Les **40 UC de recherche acceptées** ne démontrent pas qu'un plan de transit de 2 UC a pu être construit, ni que des demandes refusées ont été consommées.

**Divergence négative sous 4/4 :**
- **Témoin** : positions (2,2), (3,2), (4,2), (3,2), (2,2), (2,3), (2,4), puis (2,4) jusqu'au pas 10. Au pas 5, commande `se_deplacer` au sud, objectif adjacent nouvellement observé.
- **Exposé** : positions (2,2), (3,2), (4,2), (3,2), (2,2), puis (2,2) jusqu'au pas 10. Les mêmes deux transits de retour ont été appliqués aux pas 3 et 4, mais **au pas 5 `attendre` a été exécuté via l'option permanente** et aucun déplacement vers (2,3) n'a suivi pendant les dix pas. Le dommage physique total = **10** ; l'intégrité corporelle finale = **90**.
- Les captures et les actions des **deux premiers pas** sont identiques entre exposé/témoin, ainsi que la capture locale initiale et l'empreinte des deux premières Perception. Aucune fuite démontrée du danger futur dans la première décision.
- La sécurité canonique du site dangereux reste **`unknown`** initialement, après le pas 4 et après le pas 5 dans les huit conditions. Ni l'activation ni le retrait physique du danger ne deviennent automatiquement une certitude de l'individu. Le changement de décision au pas 5 est **observé, non expliqué** ici ; il ne peut être automatiquement attribué à un apprentissage de danger, un succès de Gatekeeper ou une modulation de récupération sans un diagnostic causal supplémentaire.
- Les **UC** sont les opérations effectivement acceptées dans les événements `compute_charge`. Le rythme différent (25 vs 5 UC de recherche route sous 4/4) ne prouve pas à lui seul la cause du choix `attendre`.

## États physiques, scénarios et snapshots

Pour chaque condition, les deux inputs sont reçus puis appliqués aux pas 3 et 5, avec ordre et séquences exacts. Dans les quatre variantes exposées, le checkpoint pris **après le pas 4** contient la zone active ; le checkpoint pris **après le pas 5** ne contient aucune zone active. Dans les témoins, la zone est absente aux deux points. La propriété `scenario.next_index` vaut **1 puis 2** dans les snapshots correspondants.

Les deux snapshots sont périodiques, pris uniquement après clôture de pas, sur **tous les propriétaires causaux**. Ils sont vérifiés puis restaurés après les dix pas ; les états propriétaires complets, les ressources physiques, les snapshots et les hashes concordent avec les valeurs gelées à la capture. Deux `snapshot_restored` techniques sont ajoutés : le journal **reste append-only** et le hash *après* restauration diffère légitimement du hash *avant* restauration. Les exécutions indépendantes ont le même ordre de captures et de restaurations ; on ne compare jamais des calendriers différents.

## Empreintes du code testé

SHA-256 d'input et du journal **après dix pas et deux prises de snapshots, avant les deux restaurations** ; dernier digest = sortie `evidence_sha256` de la sonde, qui inclut les digests post-restauration.

| Budget | Variante | Entrée SHA-256 | Journal SHA-256 pré-restauration | Sortie evidence SHA-256 |
| --- | --- | --- | --- | --- |
| 0/0 | Témoin | `eb21bff9643249c5f7f822fe42de7b4f816a941af0bf6e45985871188635f549` | `96066c0af3a32370d7fa56fe83881d831022c77d32ed2584eb19002c6b5a0ef4` | `b80a06de7eadb06c2488722ec78ed40ac0c5578c1b84e0f4fd42914abbe447b5` |
| 0/0 | Danger | `0cd4724d7aa11170a81b25beef84b148899a87e8201050057147c870f506735b` | `95f1dc18d1bce33f128d959e3a0dad441d4bc9fc3bd5af0fc043bed4e4923595` | `63de90ca5b56c857d436da4b88e1f69fea851b8c624833c42356b35ff415a7d1` |
| 3/4 | Témoin | `c7590fb2322723ccc3b01264dabfe2c3f4e5e851b8f9795a10e309229b50a411` | `f6a3ae8e63ae919f97f40db4fc7a3e27ad6f354400e86f2eec9a21eccf1f90ee` | `72ffad0e9135cc3bf4f10c4441b224ec4fd571fe571eaf1be068c3be5df8a970` |
| 3/4 | Danger | `05a1c6ed1898c559a2dc355f2ad3e7c654236c20cace40cacca9a7bb6fcc3ae3` | `e3d974a7203e60b98e892f4a1afc2937b6f1da98200574df3c2912c2047f8b42` | `5edd552788cabfefca7d345cb528dc5110e86a9c5feabb9e342113a68b83bd6c` |
| 4/4 | Témoin | `93d4174155c3d1c5c0fe5443928a1df1bf14f078ef80c58f88458af43a1e9f8d` | `97ce45cb83a16329442d4da94bdde4ecc8d7346c2bebb0ae5dca04a9d234ad41` | `c731fa06117a8f857fd3f9796314ffa7fe410df1ee53ad25d295011faa2d2223` |
| 4/4 | Danger | `9c864d9f4577f33946685c199d63fa9f00eb6d1e814282fbe7688c251af595d7` | `a93ef4d2326eea618be7a47a4db8ab7957c2678cd88fa07040fff15ff413fd6e` | `b25c265c67e645c8a655eca83b0681c599fb7fd691982cc3b66b723563726be0` |
| 4/0 | Témoin | `d8bc180707943cd679e727057c54848ba3b4c81d2ed70b35e33308c31ed401` | `aed5c8ba302f35f4e6337b2ddfd6c0da0edbdaba3286f49813d2043fe2a0c49d` | `f41691eca631b628341dfe2ba7051413e4d43593f7a98b460bad5e6d887c2a91` |
| 4/0 | Danger | `644e0f28bc55b541c890566248d77d709ba3783bece2f5657c752c9d75cac6dd` | `427f8060c632b0505353b5ffa0986b4dbb70a80d07e91763c3c9d2524d520bed` | `a014172ea0f47c4ebf32ea0476677c413a516f0791f12f13a834c812e8af64c4` |

## Reproduction et limites

Sur le checkout exact du SHA source/test ci-dessus, avec le projet installé et Python 3.12 :

```sh
python -m unittest discover -s tests -p 'test_stage11_transient_hidden_route_uc_snapshots.py' -v
python -m lab.stage11_transient_hidden_route_probe
```

La commande de sonde émet exactement huit lignes JSON `stage11_public_transient_hidden_route=`. Ces lignes sont des **diagnostics de développement ouverts**, non des mesures held-out ou preuves d'acceptation scientifique. Aucun paramètre de Planning, Exploration, Action Control, modulation, seuil de compétition, physique du monde ou algorithme de routage n'a été retouché pour obtenir les trajectoires constatées.

La découverte de branche sud sous budget 4/4 **témoin** constitue une observation sur ce couloir connu uniquement. La **non-découverte** sous budget 4/4 exposé reste une limitation explicite ; elle ne démontre pas une stratégie de sécurité, une préemption de menace ou un apprentissage. Des tests et une instrumentation séparés sont requis pour localiser la première différence d'arbitrage au pas 5. Les tests historiques Stage 9 demeurent scientifiquement NO-GO.

**Stage 11 EN COURS ; Stage 9 scientifique NO-GO ; PR #25 Draft, non fusionnée.**
