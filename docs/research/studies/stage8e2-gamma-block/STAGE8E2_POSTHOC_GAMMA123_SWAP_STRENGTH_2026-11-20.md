# Stage8-E2 · diagnostic post hoc de l'intensité de permutation gamma123

**Date : 20 novembre 2026. Statut : `READONLY_EXPLORATORY_NO_NEW_LIVES_NO_CONFIRMATORY_PROMOTION`.** Le verdict primaire [Stage8-E2 fermé](STAGE8E2_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-20.md) reste **`STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`**. Ce diagnostic n'est pas un second essai, une nouvelle hypothèse confirmatoire, une réinterprétation du seuil ni une allocation scientifique.

## Matériel et provenance

- [Unique science Stage8-E2, workflow #44637950471](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44637950471). Artefact métadonnées `stage8e2-science-native-metadata-44637950471`, ID GitHub `14601206944` : dans `METADATA.tar`, fichier `native-originals/SELECT_G2.json`. Empreinte SHA-256 du fichier **`b830e9e8500bdc32fa56d02bbbdac50fe1e475dad7c648ee532fb2ff57ffe3a7`**, liée à la sixième phase `SELECT_G2` du journal original.
- Artefact final `stage8e2-science-original-cold-audit-and-primary-44637950471`, ID `14601838862` : `SCIENCE_FINAL.json`, SHA-256 **`18ad42a1e68a0a7c1c2390bd397ee90e7872bdf398f0f5bac37d06bbfff8af45`**. Les 64 moyennes populationnelles y sont conservées et ont déjà été re-réduites par un job indépendant.
- **Aucun nouveau gzip ni World** : seules les **6 144 copies de génotypes G2 déjà archivées**, 1 536 paires S/M et les moyennes finales déjà publiées sont utilisées. Les trois racines Stage8-E2 restent consommées.

## Diagnostic génétique indépendant de l'assembleur

Pour chaque couple `(population p de 0 à 63, slot s de 0 à 23)`, contrôle des quatre génomes `S_sham / M_sham / S_swap / M_swap`, du triplet ordonné `gamma1,gamma2,gamma3` et des **28 autres coordonnées** :

- **6 144 / 6 144 génotypes G2** inspectés ; **1 536 / 1 536** couples ont des triplets gamma **distincts avant échange**. Il n'existe donc pas de couple « échange sans changement » sur cet échantillon.
- **1 518 / 1 536** couples ont des valeurs différentes sur **les trois** gènes ; les autres couples conservent au moins une coordonnée gamma commune.
- Pour les quatre versions, **tous les gènes hors gamma** sont strictement préservés entre `S_sham→S_swap` et `M_sham→M_swap`, tandis que les trois gamma du `S_swap` sont exactement ceux du `M_sham` et réciproquement.
- Distance `L1=|S.gamma1−M.gamma1|+|S.gamma2−M.gamma2|+|S.gamma3−M.gamma3|` : moyenne **0,13285871224**, médiane **0,1188475**, minimum **0,005518**, maximum **0,36747**.

| Coordonnée native | Différence absolue moyenne entre `S_sham` et `M_sham` | Plage observée sur les 3 072 sham |
| --- | ---: | --- |
| `gamma1` | **0,1002885423** | 0,600 à 0,900 |
| `gamma2` | **0,0265000410** | 0,900 à 0,980 |
| `gamma3` | **0,0060701289** | 0,980 à 0,998 |

La variance de `gamma3` était faible dans ces 3 072 génomes : écart-type **0,00542787**. Le traitement **changeait le triplet dans tous les couples**, mais la perturbation portée par gamma3 était relativement faible. **Cela ne mesure pas la sensibilité fonctionnelle de chaque gène** : des amplitudes dans les mêmes unités ne constituent pas des effets comparables sur le comportement.

## Éléments corporels descriptifs associés

Dans les 64 populations de la science, l'écart de persistance S−M était de **+7,274522569 pas** dans les sham et de **+7,365234375 pas** après l'échange. Leur différence préenregistrée est **−0,090711806 pas** avec IC bilatéral 97,5 % **[−4,589 ; +4,408]**, d'où le verdict primaire négatif inchangé.

À titre **purement exploratoire**, la corrélation de Pearson entre la distance gamma `L1` moyenne par population et son contraste primaire `T[p]` est **r=−0,09670** ; avec `|T[p]|` elle est **r=−0,10624**. Ces valeurs ne sont **ni un test de médiation, ni une analyse de puissance, ni une validation causale**. Ne pas chercher un seuil favorable, une sous-population gagnante ou une « correction » du résultat négatif sur ces données.

## Conséquences pour la recherche

Le résultat négatif ne découle **pas** d'un échange de gènes totalement inexistant : les blocs ont réellement été échangés et l'arrière-plan génétique préservé au sein de chaque paire. En revanche, l'expérience n'a **pas isolé gamma3**, dont la plage et la différence effective étaient petites. Elle n'identifie pas davantage de mécanisme comportemental reliant gamma1 au gain S−M.

**Prochaine question falsifiable possible, distincte de Stage8-E2 :** identifier un médiateur génétique/physiologique dont la manipulation produit une variation prédite des actions motrices et des coûts corporels, puis du gain de persistance, dans des **populations et WorldSpecs nouveaux**. Il faudrait préengager une direction d'effet, une taille minimale détectable, une intervention valide sous les contraintes `gamma1≤gamma2≤gamma3`, des contrôles sham et l'ajustement des comparaisons multiples avant toute nouvelle naissance. Les associations exploratoires Stage8-E1 ne peuvent servir de verdict causal ni de justification pour relancer Stage8-E2.

**Portée scientifique :** `F0_ONLY / INTERNAL_EVIDENCE / POSTHOC_DESCRIPTION / NO_NEW_LIVES`. I1 actif, i3 non enregistré ; Stage2 général `NOT_ISSUED/HOLD_NO_VERDICT`.
