# Stage8-E3C · après le premier échec énergétique, aucune reprise motrice observée

**Résultat descriptif clos, 20 novembre 2026 :** `READONLY_ALL_36864_ORIGINAL_G2_FIRST_ENERGY_GATE_TIME_COURSE_COMPLETE`. L'examen des **36 864 vies G2 originales** montre que **17 560** ont rencontré au moins une fois `NO_PROCESSING_BUDGET`, et **aucune de ces vies n'a ensuite exécuté une nouvelle action motrice financée** jusqu'à sa mort ou à la censure. Les 19 304 vies sans premier échec *observé* ne sont pas des preuves de résistance éternelle : leur temps d'observation était fini.

**Qualification obligatoire :** diagnostic **post hoc**, observationnel, non test de significativité, non médiation génétique et **zéro nouvelle naissance**. Le résultat causal historiquement préengagé de Stage8-E2 reste `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`, avec T primaire moyen `−0,090712` pas, inchangé.

## 1. Provenance et intégrité indépendante

- [Science native Stage8-E2, run #44637950471](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44637950471) : source moteur `03faff4b9c194a5288b92e394f6a75cbe62cd095`, fichiers source SHA-256 `e816ff5f5ee679253fc57f6e9ee79d21dff73dd72d6adf3c7f55ba7aa0f3e7f6`, matrice G2 de **64 populations × 4 bras × 144 vies** et 384 WorldSpecs d'origine. G2 archive originale artifact **14601222013**, métadonnées natives artifact **14601206944**, manifeste `61eb74a1f429c2f9189ee13da5c52593776d2b6f9d2b2d8ac41bfdea31a6ba00`. Science close SHA `18ad42a1e68a0a7c1c2390bd397ee90e7872bdf398f0f5bac37d06bbfff8af45`.
- Audits précédents historiquement fixés : [E3A #44706318958](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44706318958), rapport `16e69fdcb664f73b7d67fa6e620017dc30e78bec834ddb148a2c58c6b0939d8b` ; [E3B #44715847132](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44715847132), rapport `c0709ad5ff8491538eab5fcb4f93bd854502d3aec9714878550426a88a179720`. Leurs secondes réductions sont vérifiées elles aussi.
- [Workflow first-only E3C #44737606261](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44737606261), source HEAD fusionné `93775dba3979911468aecaa1898c9328a0d604b5`, **run_attempt=1, 3/3 jobs PASS**. Préflight avec tests synthétiques, puis **36 864 gzip compressés ET JSON décompressés réhachés** et chaînes natives corporelles et cognitives payées reconstituées par original. **9 211 248 pas historiques**, 14 337 866 000 octets JSON décompressés, **aucun individu recréé**.
- Artifact E3C des **256 cellules population×bras et quatre fenêtres** : **14629459511**, fichier `STAGE8E3C_FULL.json` SHA-256 **`c99011ff4dc2bc7d57eb4edea5e68fa3a273777d984ddae8073777c38e5e4e23`**. Artifact de réduction indépendante **14629908704**, fichier `STAGE8E3C_SECOND.json` SHA-256 **`b3ed0a35f4b51d9b77e8d34edb7f48b7d5858de05036018868da237ecffd2fd0`**.
- **Troisième vérification arithmétique extérieure à la CI** : lecture des deux fichiers JSON originaux téléchargés et comparaison des 256 cellules, 33 types de contrastes descriptifs, dénominateurs et comptes agrégés par bras. **Concordance intégrale**. Ce contrôle tiers n'a **pas retéléchargé les 1,49 Go d'originaux** ; l'audit des octets des 36 864 gzip est celui du job CI source-figé.

Le [protocole E3C](STAGE8E3C_ORIGINAL_TEMPORAL_METHOD_2026-11-20.md) a préfixé ses quatre fenêtres avant de prendre connaissance des résultats. Le résultat est conservé même s'il est défavorable à l'hypothèse de protection génétique.

## 2. Première impossibilité de financer la décision, par bras

| Mesure | S_sham | S_swap | M_sham | M_swap |
|---|---:|---:|---:|---:|
| Vies originales | 9 216 | 9 216 | 9 216 | 9 216 |
| Au moins un `NO_PROCESSING_BUDGET` | **4 028** | **4 293** | **4 647** | **4 592** |
| Pourcentage de vies atteintes | **43,71 %** | **46,58 %** | **50,42 %** | **49,83 %** |
| Premier échec, pas moyen *conditionnel à l'échec observé* | 128,80 | 126,08 | 119,52 | 119,66 |
| Énergie immédiatement avant premier échec | 0,05293 | 0,05348 | 0,05194 | 0,05142 |
| Vigilance immédiatement avant premier échec | 94,03 | 94,05 | 93,91 | 94,08 |
| Retour ultérieur à ≥ 1 action financée | **0** | **0** | **0** | **0** |
| Décès après le premier échec | 3 472 | 3 737 | 4 094 | 4 018 |
| Censures à l'horizon après le premier échec | 556 | 556 | 553 | 574 |

**Total : 17 560 / 36 864 vies (47,635 %) rencontrent ce premier échec, aucune reprise motrice financée, 15 321 décès et 2 239 censures ensuite.** Les censures ne sont pas comptées comme des décès. Parmi les **19 304** vies sans échec observé, certaines se sont terminées par décès ou horizon avant la possibilité d'en voir un : la variable est censurée à droite.

Le contraste descriptif sur les 64 fractions d'incidence par population est `(S_sham−M_sham)−(S_swap−M_swap) = −0,0347222`, soit **−3,4722 points de pourcentage**. Répartition : **23 populations positives, 37 négatives, 4 exactement nulles**. **Pas de p-value ni d'argument de significativité**, pas de changement du T de survie Stage8-E2.

## 3. Quand survient le premier échec ?

Les quatre fenêtres natives avaient été fixées **avant** le téléchargement des trajectoires E3C :

| Fenêtre de temps natif | Premiers échecs observés, tous bras | Définition |
|---|---:|---|
| t = 1–20 | **0** | Les 36 864 vies financent intégralement leurs 20 premiers pas |
| t = 21–100 | **10 098** | 57,5 % des 17 560 échecs observés |
| t = 101–200 | **3 555** | 20,2 % |
| t = 201–400 | **3 907** | 22,2 % |

Chaque vie n'entre **qu'une fois** dans le compteur de premier échec, même si elle reste inactive pendant cent autres pas. Les dénominateurs « à risque au début » et « pas réellement observés » sont conservés par fenêtre et par cellule. Comparer les fenêtres tardives naïvement exposerait un biais de survie : leurs populations présentes ont déjà vécu plus longtemps.

## 4. Que faisait l'individu juste avant la première panne ?

Les **10 pas effectivement observés précédant le premier échec** sont disponibles sans imputation pour **toutes** les vies touchées. L'agrégation est ici *conditionnelle* à la survenue de l'échec, et **ne constitue pas** un groupe contrôle non défaillant à âge identique.

| Descripteur avant le premier échec, par pas antérieur | S_sham | S_swap | M_sham | M_swap |
|---|---:|---:|---:|---:|
| Déplacement physique | 54,73 % | 54,81 % | 55,05 % | 54,47 % |
| Sommeil actif | 24,91 % | 24,98 % | 25,07 % | 25,90 % |
| Énergie de prédécision moyenne des 10 pas | 5,202 | 5,179 | 5,090 | 4,951 |
| Énergie cognitive effectivement payée par pas | 0,542 | 0,540 | 0,534 | 0,538 |

Dans cette fenêtre précédant la première panne, on observe **environ 55 % de déplacements, 25 % de sommeil** et une dépense cognitive déjà financée d'**environ 0,54 unité d'énergie par pas**. À l'instant du refus, l'énergie est proche de **0,052**, la vigilance proche de **94**. Les dix valeurs ne prouvent pas que le déplacement ou la cognition *cause* la panne : ces individus ont été sélectionnés rétrospectivement parce qu'ils ont justement connu cette panne.

Le moteur natif demande initialement au moins **0,06 énergie + 0,0002 × mémoire mobilisée**, et **0,15 vigilance** pour les premiers blocs de traitement. L'énergie observée au refus est insuffisante, alors que la vigilance est largement suffisante. Après un refus, le moteur exécute `None`, qui ne produit ni sommeil ni restauration d'énergie ; il ne crédite pas une nouvelle décision financée. **L'absence de reprise motrice est une observation exhaustive de cette cohorte**, et non une preuve que tous les mondes possibles produiraient éternellement ce blocage.

## 5. Interprétation scientifique, limites et suite falsifiable

**Mécanisme désormais observable :** dans les vies G2 F0 historiques, un niveau d'énergie très bas bloque l'amorçage du traitement, puis l'absence de décision empêche l'accès aux actions énergétiquement réparatrices. L'épisode devient **persistant jusqu'à mort ou censure dans 17 560/17 560 cas observés**.

**Ce que cela ne démontre pas :** l'échange gamma123 comme **cause** de l'épuisement, une médiation génétique par l'énergie ou par `gamma3`, la supériorité évolutive du phénotype, une politique alternative correcte, ou une généralisation à d'autres environnements. Les graines des vies physiques ne sont pas un contrefactuel individuel couplé entre bras. Les comparaisons à n=64 restent descriptives multiples post hoc et le résultat Stage8-E2 causal demeure négatif et clos.

**Question suivante sans nouvelle naissance :** décomposer la **baisse d'énergie réellement observée dans les dix pas précédant le premier refus** en (i) paiement de décision et apprentissage, (ii) coût des actions motrices, (iii) regain réellement constaté lors des sommeils, et (iv) changements d'état restants. Comparer ensuite, dans des fenêtres de temps *prédéfinies* et en préservant les risques de décès/censure, les individus proches du seuil à ceux du même bras, de la même population et du même temps qui ne l'ont pas encore franchi. De telles comparaisons restent **observationnelles** ; elles ne démontrent pas une médiation. La garde de tous les originaux au-delà des 90 jours GitHub Actions est suivie en [#1463](https://github.com/josselin-orta-lab/individual-zero/issues/1463).

**États inchangés :** moteur I1 actif, i3 non promu, Stage2.1 `NOT_ISSUED/HOLD_NO_VERDICT`, étude Stage8-E2 `CLOSED_NO_RETRY`.
