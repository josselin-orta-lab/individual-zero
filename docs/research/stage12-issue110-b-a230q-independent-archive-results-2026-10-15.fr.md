# A2.30-Q : relecture indépendante des trajectoires et terminalités archivées

**15 octobre 2026.** L'analyse Q a été **préenregistrée après connaissance des résultats P mais avant le code d'audit**, au commit `0cb14c1bd4668b8ca8482451c98c6c7a5a3056da`. Le témoin `audit_stage12_issue110_b_a230q_independent_archives.py` reconstitue le modèle empirique depuis les fichiers P, sans importer le modèle P, le runner physique P, WorldBody, Oracle ou Bench. [GitHub Actions Q #38731532528](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38731532528) **PASS Python 3.11 et 3.12**, sur le code de référence `8407e5ac61d829addc75b7e9639cebbe25f9a377`. Recontrôles ultérieurs également verts dans les commits de la branche.

## Sources figées et falsifiables

Deux artefacts `a230p-py3.11` et `a230p-py3.12` du run physique P #38730415503, SHA code P `3ab03a90b38d6c968cddcd9ed699c3f089d0544c`. Les trois fichiers sont **strictement identiques octet pour octet** sous les deux versions Python et SHA-256 vérifiés intégralement :

| Fichier | SHA-256 |
|---|---|
| `a230p-training-manifest.json` | `f706cd25a31b8f716c4bb0a5a7e617bed87c0b8b47577d8b9dd31221cf23839e` |
| `a230p-heldout-physical-results.json` | `570713d9a44c55a13482dba3d5e9b2f8095df8ba8f487f22d5aa917db8bc3514` |
| `a230p-summary.json` | `45167e3bd7be3827f2839208aa8bfe2e316e6b4f110106b94d68bf32a3fea0e0` |

Pour chacun des **128 mondes physiques originaux**, le vérificateur recalcule les empreintes des exemples et leurs états accessibles avant/après, vérifie l'enchaînement `after_i == before_(i+1)`, les 11 deltas corporels/spatiaux/d'inventaire, les pas de terminaison et l'absence de reprise après mortalité. Il reforme les **trois contextes accessibles**, les **quatre branches conjointes** de chacun depuis les 48 mondes d'entraînement seulement, et réévalue les 80 cas tenus à l'écart.

## Compteurs indépendamment retrouvés

| Mesure | Résultat |
|---|---:|
| Mondes archivés contrôlés | **128** |
| Transitions des originaux vérifiées dans les fichiers | **352** |
| Tests hors entraînement indépendamment recalculés | **80** |
| Traces ordinaires reconnues par les branches entraînées | **48/48** |
| Trajectoires latentes inédites pour un groupe connu | **24/24** |
| Abstentions pour commandes/contexte non entraînés | **8/8** |
| Décès différés ordinaires non révélés par les seuls exemples au premier pas | **8** |
| Décès à un pas absent des branches enregistrées, mondes OOD | **8** |
| Certificats de sûreté publiés par P | **0** |

Les contrôles adversariaux du reviewer rejettent : faux SHA d'observation physique, fausse terminalité, suite ajoutée après mort, prétendue branche connue sans exemple, `certifies_safe=true`, branche ajoutée artificiellement à un groupe connu, identité train/test réutilisée et modification de statistiques. **0 omission détectée**.

## Ce que Q ne démontre PAS

Une reconstruction d'archives immuables ne peut pas démontrer, à elle seule, que le moteur physique a réellement appliqué toutes les commandes. Elle prouve **la cohérence des traces, du protocole et de l'évaluation de P relativement aux octets du run original**, pas l'indépendance ontologique de la réalité physique. Une relecture technique exécutant de nouveaux mondes depuis le protocole préenregistré, distincte du runner P, est réalisée en A2.30-R. Les archives ne sont pas de nouvelles données et les deux Pythons ne sont pas des répétitions statistiques indépendantes.

**Résultat : PASS d'intégrité des archives et recalcul des résultats, A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 OPEN, PR #189 DRAFT.** Ni preuve d'exhaustivité des risques cachés ni validation d'un prédicteur utilisable par Stage6.
