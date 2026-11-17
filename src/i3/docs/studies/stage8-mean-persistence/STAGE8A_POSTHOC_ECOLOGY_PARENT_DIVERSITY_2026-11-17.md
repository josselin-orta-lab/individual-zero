# i3 · Stage8-A : interactions écologiques et concentration des parents (analyse post hoc du 17 novembre 2026)

**Statut : `EXPLORATORY_DESCRIPTIVE_READ_ONLY` ; aucune naissance, nouveau World ou mutation.** Ce rapport est produit **après** la clôture du protocole Stage8-A. Ses statistiques secondaires ne deviennent jamais des tests confirmatoires, ne modifient pas les règles du protocole et n'autorisent aucune répétition sélective.

## 1. Bases archivistiques, identité et limites

| Source | Preuve |
| --- | --- |
| Étude prospective (source originale) | [Actions #43950098410](https://github.com/josselin-orta-lab/individual-zero/actions/runs/43950098410), SHA Git `ac353a9c4206ee3ecfd90bb101e26d092103958b`, `run_attempt=1` |
| Plan scientifique **antérieur à la première naissance** | Artifact `14278546177`; SHA-256 du ZIP `3a3eb789cb3a726e019238c72fa3b7a66ef45781d2fdf7b6be45bbb3a3ed61c2`; SHA d'allocation `dcd93550453541273c940f78fc459dd3f4deaa807911cb89992c4d1eb7d3b660` |
| Résultat scientifique | Artifact `14289613177` ; SHA-256 du ZIP `5c5bced3b05c0331230811e79bb6ac6155b2ff3f04fc99ad1bcee8c21d017e90` ; `SCIENCE_RESULT.json` et `originals/SCIENCE_FINAL.json` |
| Originaux scientifiques complets | Artifact `14289668087`, SHA-256 ZIP `d4abb68e809940ef1eab82049e0e1b86c2a62e8c10622740eea45678109503ea` |
| Réduction indépendante, déjà exécutée | [Actions #44042075429](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44042075429), artifact `14309617788`, ZIP `5ff6a686f259f50433785cd8e13bf58d825915b12c0df165fc396ac15a0afc7a` ; `READ_ONLY_REPRODUCTION_OK`, 23 040 vies originales rehashées, zéro vie créée |
| Suivi public scientifique | [Issue #1427](https://github.com/josselin-orta-lab/individual-zero/issues/1427#issuecomment-6943652965) ; [rapport prospectif](STAGE8A_PROSPECTIVE_SCIENTIFIC_RESULT_2026-11-17.md) et [audit indépendant](STAGE8A_INDEPENDENT_READONLY_AUDIT_RESULT_2026-11-17.md) |

Le fichier `SCIENCE_RESULT.json` contient les **32 enregistrements `all_population_statistics`** utilisés ici. Les empreintes des trois ZIP de plan, de résultats et d'audit ont été vérifiées localement ; le SHA-256 du fichier `originals/SCIENCE_FINAL.json` présent dans le ZIP résultat correspond au `science_original_sha256` publié : `f755c7e6000fafd3be9409e4ae1aa5d8d4aa097e9159338ccd68e7204ffee6ad`. Les 32 contrastes G2 correspondent, valeur par valeur, à la sortie de l'audit indépendant. Il s'agit d'une **nouvelle réduction descriptive des sorties archivées**, non d'un deuxième replay du moteur ni d'une nouvelle relecture individuelle des 23 040 gzip.

**Résultat prospectif à ne pas réécrire :** `STAGE8A_MEAN_PERSISTENCE_ADVANTAGE_F0`, différence moyenne sélectionné–témoin en G2 `+14,4874131944` pas ; borne inférieure unilatérale de Student 97,5 % `+7,9933122338` pas ; **23 populations favorables, 9 défavorables, aucune nulle**. L'unité statistique est la population (n=32), pas le nombre d'individus.

## 2. Décomposition par écologie F0

Chacun des 24 génomes G2 de chaque bras possède **deux vies par famille** (`stable`, `depletion`, `pulse`), soit **48 vies par bras, population et famille**. La différence `D[p,f]` est la durée moyenne dans la famille pour les sélectionnés, moins la durée moyenne chez le témoin `random_parent`, tous sur les opportunités écologiques appariées de cette génération. Les trois familles ont le même poids dans le critère global :

```text
D[p,G2] = (D[p,stable] + D[p,depletion] + D[p,pulse]) / 3
mean_p D[p,G2] = +14,4874131944 pas
```

| Famille F0 | Différence G2 moyenne (pas) | Populations +/−/0 | Survivants censurés à 400 : selected | random_parent |
| --- | ---: | ---: | ---: | ---: |
| `stable` | **+12,861979** | 21 / 11 / 0 | 35,55 % | 29,43 % |
| `depletion` | **+14,549479** | 23 / 9 / 0 | 51,69 % | 44,14 % |
| `pulse` | **+16,050781** | 24 / 8 / 0 | 23,70 % | 19,14 % |
| **Moyenne des trois familles** | **+14,487413** | *Ne pas additionner les signes* | | |

Les trois moyennes sont positives, **mais il n'y a pas de démonstration d'une différence d'effet entre les familles**. Exemple exploratoire utilisant les **32 contrastes intra-population**, sans multiplier artificiellement par les 48 vies : `stable−pulse=-3,188802` pas, intervalle t *bilatéral* descriptif à 95 % **[−15,025 ; +8,648]**. Pour `stable−depletion` : −1,688 [−10,159 ; +6,784] ; `depletion−pulse` : −1,501 [−9,649 ; +6,647]. **Tous comprennent zéro**. Ces intervalles n'ont pas été préenregistrés comme critères confirmatoires, ne sont pas ajustés pour comparaisons multiples, et leur couverture suppose des populations suffisamment indépendantes.

Les familles `stable`, `depletion` et `pulse` sont trois modalités **F0** fixes. L'effet positif moyen dans chaque modalité ne suffit ni à prouver une interaction spécifique sélection×écologie ni à généraliser à d'autres mondes.

## 3. Les neuf populations défavorables : diagnostic sans élimination

Les identifiants ci-dessous désignent **les nouvelles populations de Stage8-A**, non celles de Stage7 ; leurs chiffres et mécanismes ne doivent pas être amalgamés.

| Population | D G2 global (pas) | `stable` | `depletion` | `pulse` | Parents distincts G2 selected/random |
| --- | ---: | ---: | ---: | ---: | ---: |
| P00 | −4,889 | −25,625 | −2,167 | +13,125 | 15 / 17 |
| P01 | −7,722 | +1,083 | +12,021 | −36,271 | 16 / 15 |
| P02 | −7,507 | −17,583 | −3,000 | −1,938 | 15 / 15 |
| P04 | −1,486 | −10,750 | −2,125 | +8,417 | 14 / 15 |
| P07 | **−18,875** | −8,812 | −17,292 | −30,521 | 14 / 17 |
| P15 | −5,333 | +18,125 | −23,646 | −10,479 | 17 / 16 |
| P23 | −2,965 | −17,125 | −14,771 | +23,000 | 16 / 15 |
| P29 | −10,854 | +6,271 | −15,000 | −23,833 | 15 / 16 |
| P31 | −0,667 | −5,729 | +12,938 | −9,208 | 16 / 16 |

**P02 et P07 sont les seules de ces neuf à perdre dans chacune des trois écologies.** Les sept autres changent de signe selon le monde ; P01 bénéficie de deux familles et perd fortement dans `pulse`. P07 est le désavantage global le plus important parmi les neuf. **Huit sur neuf avaient un avantage G1 positif**, mais une inversion apparente G1→G2 n'est **pas une démonstration causale** : les mondes et les génomes changent entre générations.

Les panneaux indépendants de graines au sein de cette même allocation scientifique sont hétérogènes : P00–P15, **10+ / 6−**, moyenne +9,5751 pas ; P16–P31, **13+ / 3−**, moyenne +19,3997 pas. Ce sont deux blocs du même test n=32, **pas deux répétitions scientifiques indépendantes**.

## 4. Concentration parentale : grandeur observée et résultat d'un mécanisme déjà prévu

`G2_parent_diversity_selected/random` mesure ici **le nombre de slots parentaux distincts parmi 24 tirages d'ascendance G2**, PAS la diversité génétique réelle des 24 génomes, leur hétérozygotie, leur diversité fonctionnelle ni leur avantage de survie intrinsèque.

| Mesure sur 32 populations | Valeur |
| --- | ---: |
| Parents distincts, bras selected (moyenne) | **14,00 / 24** |
| Parents distincts, contrôle uniform parent (moyenne) | **15,25 / 24** |
| Différence moyenne selected−random | **−1,25 parent** |
| Populations où selected a moins / autant / davantage de parents distincts | **20 / 5 / 7** |
| Parmi les neuf populations globalement défavorables : moins / autant / davantage | **4 / 2 / 3** |

Le nombre de parents distincts plus faible du bras sélectionné **ne constitue pas, à lui seul, un goulet génétique nuisible**. Avec 24 enfants échantillonnés *avec remise* parmi 24 parents, l'espérance de parents uniques est :

```text
Tirage uniforme : 24 × (1−(23/24)^24) ≈ 15,358
Poids de rang 24,23,...,1 : Σ(r=1..24)[1−(1−r/300)^24] ≈ 13,919
Différence mécanique de référence ≈ −1,439 parent
```

La différence observée **−1,25** est cohérente avec cette concentration de tirage prévue par construction. Ce calcul n'est pas un test de causalité génétique.

L'association exploratoire entre la différence de nombre de parents distincts et le gain G2 par population est quasi nulle : **Pearson r≈−0,0115 ; Spearman ρ≈+0,0280 (n=32)**. Les populations défavorables ont une différence de parents distincts moyenne de **−0,444**, tandis que les favorables sont à **−1,565**. La concentration des parents ne suit donc **pas simplement** la persistance défavorable. Cela n'exclut pas des mécanismes impliquant l'identité des parents, des mutations, la coadaptation ou la diversité des variantes génomiques ; ces propriétés ne sont pas mesurées par cet indicateur.

## 5. Règles d'interprétation et prochaines expériences, distinctes de Stage8-A

1. **Acquis Stage8-A :** avantage **moyen** F0 de G2 selon le critère prospectif ; archives et réduction indépendante conformes. `STAGE8A_MEAN_PERSISTENCE_ADVANTAGE_F0 / CLOSED_NO_RETRY` reste inchangé. Stage7 reste négatif à son propre critère 13/16, également `CLOSED_NO_RETRY`.
2. **Non démontré :** rôle causal d'une famille F0 spécifique, mécanisme génétique transmissible identifié, nocivité causale du nombre réduit de parents distincts, supériorité d'i3 hors F0, effet G0→G2 causal, indépendance écologique et statistique prouvée.
3. **Stage8-B candidat (pas de nouvelles vies lancées) :** préenregistrer la question *interaction sélection×famille écologique*, les mondes réservés hors des conditions actuelles, les contrastes au niveau **population**, la correction de multiplicité entre familles et le critère d'arrêt avant naissance. Ne pas élever `pulse` au rang d'hypothèse confirmée à partir de la seule moyenne +16,05.
4. **Stage8-C candidat (pas de nouvelles vies lancées) :** distinguer l'effet de la sélection, la distribution de rang et la concentration des parents par un contrôle **à diversité parentale appariée**, plus un témoin uniforme, en tenant fixes le moteur P1.3 et les frais cognitifs. Mesurer diversité des génomes *et* nombre de parents distincts, avec allocation prospective factorielle ; ne pas attribuer le désavantage de P07 à un gène sans intervention ou réplication mécanistique.

**Origines, limites et décisions :** `INTERNAL_PROSPECTIVE_NOT_EXTERNALLY_ATTESTED`. L'audit indépendant atteste la réduction des 23 040 enregistrements internes, **pas** la physique par replay, la validité externe, l'indépendance statistique ni un horodatage hors GitHub. I1 runtime actif ; I3 référence de développement non enregistrée ; Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT`. Aucun tirage de parent, World, mutation, réexécution ou archive historique n'a été modifié ou créé pendant cette analyse.

Les ZIP complets Stage8-A actuellement hébergés par GitHub ont une expiration annoncée au **14 février 2027** : les conserver avec empreintes et métadonnées avant échéance, sans supprimer les résultats négatifs.
