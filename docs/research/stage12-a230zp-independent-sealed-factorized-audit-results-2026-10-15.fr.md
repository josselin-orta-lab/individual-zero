# A2.30-ZP : contre-expertise indépendante de ZO, périmètre de généralisation et écart au protocole temporel

**15 octobre 2026.** La campagne ZP est une **réanalyse a posteriori**, préenregistrée après connaissance des résultats ZO mais **avant** son propre auditeur et ses tests dans `docs/research/stage12-a230zp-independent-sealed-factorized-audit-prereg-2026-10-15.fr.md` sur la branche parente [PR #208](https://github.com/josselin-orta-lab/individual-zero/pull/208). Elle n'est ni un nouvel échantillon physique ni une expérience autonome I0.

**Provenance originale fixée :** [ZO GitHub Actions #38792466785](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38792466785), source scientifique `50185e2db1dc03188aca372fa0e3b854eaf85915`. Les cinq fichiers JSON d'origine sont identiques octet pour octet sous Python 3.11/3.12, **et chacun est contrôlé par SHA-256 complet avant analyse**. Les SHA-256 ne sont pas re-déterminés après correction, le script ZP rejette toute substitution ou duplication de fichier.

| Fichier source ZO scellé | SHA-256 |
|---|---|
| `a230zo-physical-training.json` | `4ad8489762b32ce21f17809121893a7afd7d96500464124ca28492d87a57d166` |
| `a230zo-frozen-partial-model.json` | `d649d5dd716972824f4190dee4ae3dc5818dc323bb757a1197adffa5232d2dee` |
| `a230zo-original-heldout-worlds.json` | `cc9bd690974c08b831e0ffc0d785040b3fba0a0875b8ce5fd99d8e33043607ef` |
| `a230zo-prospective-scores.json` | `0a8393c50d9200019435c1027f952ca5e1d9b99efb64d62ddad39184a2fe0354` |
| `a230zo-summary.json` | `d772ebe965238347396da77d40841c39e14573f964bfede50527714601fcd53c` |

## Reproduction indépendante sur les véritables archives

[CI ZP #38796472497](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38796472497) : les deux jobs Python **3.11 et 3.12 PASS**, **26 tests de falsification** réussis dans chaque job. Le code ZP est autonome, en bibliothèque standard uniquement. Il **n'importe pas** le runner ZO, `WorldBody`, `EquipmentCorpusRecorder`, `FrozenTableEquipment`, `SimulatorPlanner`, I0 ni l'Oracle. La sérialisation causale UTF-8/SHA-256 est réimplémentée et les 120 exemples physiques sont relus sans reprendre les fonctions d'entraînement/scorage d'origine.

### Résultats indépendamment retrouvés

| Dimension contrôlée | Résultat ZP |
|---|---:|
| Mondes ZO d'entraînement scellés | 16 |
| Mondes ZO de test hors entraînement | 104 |
| Reçus d'actions physiques recomptés et rehashés | 120 |
| Mondes nominaux inédits, six composantes exactes | **64/64** |
| Entrées de test connues du modèle exact complet | **0/104** |
| Corps proches de la limite avec abstention numérique | **16/16** |
| Contrastes d'effets cachés B avec même perception et même conséquence non ingestive | **32 paires** |
| Interventions cachées sans signal préaction différent du nominal | **24/24** |
| Décès par déplacement invisible | **4** |
| Dommages d'intégrité cachés | **8** |
| Échecs imposés de l'effet primitif | **8** |
| Prévisions partielles émettant une certitude de sécurité, d'intégrité, de terminalité ou d'adjacence complète | **0/104** |
| Nouvelles vies, nouveaux pas d'I0, nouvelles dépenses UC vécues | **0, 0, non mesurées** |

L'auditeur reproduit exactement le modèle mathématique entraîné **seulement** depuis les 16 états/perceptions et 16 conséquences physiques TRAIN, puis reconstruit chacun des 104 jugements numériques. Il contrôle les deux commandes éligibles (`se_deplacer(east)`, `collecter(berry_b)`), les corps initiaux, les horloges, les 32 paires bénin/létal, les hash de chaque couple `SimulationState × PrimitiveCommand`, l'absence de B ingérée et les reçus terminaux externes. Les nombres 3.11/3.12 ne représentent **pas 240 mondes indépendants**.

**Résistance à 26 falsifications :** archives altérées ou dupliquées, exemples HELDOUT injectés dans TRAIN, Oracle/zone cachée dans `SimulationState`, voisin enrichi illégitimement, faux résultat `manger(B)`, corps non physique, fin terminale travestie en survie, observation vécue après décès, `safe=True` ou `terminal=False` inventés, `next_adjacency` prétendue connue, faux scores 64/64, refus de borne modifié, UC vécues fabriquées et statut nominal modifié. Le code contrôle aussi la séquence physique/score du runner ZO **par analyse statique de l'AST source, sans l'importer**.

## Écart méthodologique vérifié : la prévision n'est pas scellée avant l'action

Le préenregistrement ZO prescrit : **(1)** état perceptible reçu, **(2)** prédiction figée et hachée, **(3)** application physique de la commande, **(4)** scoring externe. Les sources CI originales révèlent un autre ordre d'implémentation dans `experiment()` :

`training_pairs = [apply_one(...)] → model = fit_partial_empirical(training) → heldout = [apply_one(...) ...] → scores = [compare_forecast(...) ...]`.

Le modèle de six deltas est donc **réellement figé avant la construction des mondes HELDOUT**, et les prédictions sont une fonction réexécutable de ce modèle et des observations initiales. **Cependant le calcul et l'enregistrement des prédictions de chaque monde se produisent après l'exécution physique des 104 interventions**. Le run ZO ne fournit donc pas la preuve pré-engagée, individuelle et séquentielle `prévision_sha_avant → commande_physique → résultat`.

**Verdict séparé et non maquillé :**
- **ZP cohérence indépendante des archives : PASS** : intégrité, recomptage et résistance aux falsifications sous les deux Pythons.
- **ZO généralisation empirique partielle sur données de test séparées : soutenue dans les 64 cas nominaux** (six composantes seulement, aucun statut de risque).
- **ZO conformité prospective stricte de la chronologie de chaque prévision : NON ÉTABLIE / non conforme à l'ordre préenregistré**. Il faut refaire un banc qui **scelle chaque prédiction avant chaque `WorldBody.apply`** pour lever ce point. Cela ne modifie ni le résultat physique enregistré, ni les dénominateurs, ni les risques cachés.
- **Sécurité des mouvements, ingestion B, autonomie I0, mémoire vécue, attribution subjective : NON DÉMONTRÉES**. Le résultat 64/64 n'autorise pas une prédiction complète de `SimulationState`, un contrat `EquipmentModel.predict` ou une commande autonome.

### Frontière d'indépendance

Un auditeur d'archives ne démontre pas indépendamment que `WorldBody.apply` a été physiquement appelé : la CI ZO et son code source apportent ce témoin. ZP **n'exécute aucune nouvelle physique** et ne transforme pas une lecture de fichiers en deuxième cohorte. Les étiquettes `hidden_lethal_east`, `hidden_danger_here` et `toxic_lethal` servent exclusivement au **scorage externe** et aux témoins appariés ; le modèle n'a jamais accès à ces variables.

**Décision : A2.30 PARTIELLE, Stage12 PARTIAL, issue #110 administrativement CLOSED. PR scientifique ZP DRAFT, aucun merge, aucune évolution de `src/i0`, du MVP v1.3.1, de Stage9/DC-05, des UC, de M11 ni des frontières Oracle. Déploiement cognitif : NO-GO.**
