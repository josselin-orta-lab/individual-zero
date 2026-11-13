# RP-A2 / S2-C07 — Concordance avec le cahier des charges initial de l'étape 2

**Date :** 13 novembre 2026. **Nature :** annexe de traçabilité documentaire **postérieure** à la décision [ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md), et non nouvel ADR, nouveau protocole, autorisation de source/indice, validation indépendante ou verdict scientifique. **État scientifique canonique :** `NOT_ISSUED`. **Disposition interne :** `HOLD_NO_VERDICT`, **suspension** de la question générale, jamais clôture de l'étape 2. **Exécution pour cette annexe :** 0 World, 0 vie, 0 nouvelle preuve expérimentale.

## 1. Hiérarchie des sources et question d'origine

1. **Cahier des charges initial, non modifié :** [DEVELOPMENT_PLAN.md, étape 2](DEVELOPMENT_PLAN.md), [STAGE2_LAUNCH.md](STAGE2_LAUNCH.md), [issue #1062](https://github.com/josselin-orta-lab/individual-zero/issues/1062). La question est : **l'individu choisit-il si un calcul supplémentaire vaut son gain de viabilité attendu, calculé dans sa propre détresse prédite D, une fois son coût énergétique et de vigilance réellement payé ?** L'évaluation elle-même est payée ; aucun oracle, moteur imposé ni calcul récursif gratuit.
2. **Contrats et preuves :** [STAGE2_REPLAY_GATE.md](STAGE2_REPLAY_GATE.md), [audit C01 du 12 novembre](STAGE2_C01_INTERNAL_FUTILITY_REVIEW_2026-11-12.md), [disposition C01 du 13 novembre](STAGE2_C01_INTERNAL_DISPOSITION_2026-11-13.md), [chemin critique du 12 novembre, C07 et §G](STAGE2_AUDIT_DELTA_AND_CRITICAL_PATH_2026-11-12.md). Le dernier conserve quatre rubriques de décision **T/E/S/Tr**, distinctes, et interdit une clôture scientifique par absence de preuve.
3. **Feuille de route de travail, non normative :** [PR #1359, section RP-A2 et DÉC-2](https://github.com/josselin-orta-lab/individual-zero/pull/1359) ; cette PR demeure une **proposition**. Son tableau 2.1 indexe les faits mais ne remplace ni la source originelle ni une autorisation du propriétaire.
4. **Décision applicable :** [ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md), adoptée pour la **gouvernance documentaire** par [PR #1362](https://github.com/josselin-orta-lab/individual-zero/pull/1362). Le relecteur externe obligatoire a été supprimé pour RP-A1 ; cela n'attribue ni attestation indépendante, ni clôture générale, ni nouveau World.

**Règle de confrontation :** les chiffres, sources, contrastes et périmètres sont ceux de leurs résultats originaux ; les indices des explorations corrélées ne sont pas de nouvelles unités indépendantes. Tout énoncé non relié à ces pièces reste **NON DÉMONTRÉ**, plutôt que converti rétrospectivement en conclusion.

## 2. Matrice RP-A2 / S2-C07 : exigence initiale → pièce → disposition constatée

| Exigence RP-A2 | Pièce vérifiable | Concordance et limite |
| --- | --- | --- |
| **Question falsifiable :** consigner l'étape 2 sans redéfinir sa question | [Lancement](STAGE2_LAUNCH.md), [plan](DEVELOPMENT_PLAN.md) §« Stage 2 », [C01](STAGE2_C01_INTERNAL_DISPOSITION_2026-11-13.md) | **Conforme** : D, coût réellement financé, décision native et portée restent séparés. Aucun succès ou échec général ajouté. |
| **Intention :** conserver les erreurs et les résultats nuls/défavorables | [Revue C01](STAGE2_C01_INTERNAL_FUTILITY_REVIEW_2026-11-12.md) §2–4, [ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md) §Decision 2–3 | **Conforme** : P1.3 funded-v2 maintenu, sans retouche des originaux ni effacement des négatifs E1/E3. |
| **Falsificateur :** chaque affirmation reliée au tableau des preuves et règle d'arrêt | [Audit du 12 novembre](STAGE2_AUDIT_DELTA_AND_CRITICAL_PATH_2026-11-12.md) §C/G, [C01](STAGE2_C01_INTERNAL_DISPOSITION_2026-11-13.md) | **Conforme sous périmètre** : l'absence d'estimand, d'unité indépendante, de puissance ou d'acte réel interdit une conclusion générale. Pas de révision sans fait substantiellement nouveau. |
| **Contrôle :** « quatre verdicts » séparés | [Audit du 12 novembre](STAGE2_AUDIT_DELTA_AND_CRITICAL_PATH_2026-11-12.md) §G ; [présente annexe §3](#3-les-quatre-dimensions-de-verdict-t--e--s--tr) | **Clarifié** : T, E, S, Tr sont **quatre dimensions**, **pas quatre issues concurrentes de RP-A1**. `HOLD_NO_VERDICT` = état de suspension S/Tr, avec `NOT_ISSUED` en S. |
| **Observable :** ADR-0021, référence P1.3, génome `n_base`/`h_max`, négatifs, DÉC-2 et réouverture | [ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md), [sections 3 à 6 ci-dessous](#3-les-quatre-dimensions-de-verdict-t--e--s--tr) | **Complété ici** pour budgets, liste des négatifs et statut **non adopté** de DÉC-2 ; aucun nouvel ADR. |
| **Plus petit test :** brouillon d'ADR relu contre sources, 0 vie | [ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md), [PR #1362](https://github.com/josselin-orta-lab/individual-zero/pull/1362) | **Réalisé documentairement** ; l'annexe est une vérification d'alignement, pas une nouvelle mesure ni une revue externe. |
| **Dépendances :** RP-A1 / DÉC-1 / DÉC-2 | [C01 du 13 novembre](STAGE2_C01_INTERNAL_DISPOSITION_2026-11-13.md), [ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md), [PR #1359](https://github.com/josselin-orta-lab/individual-zero/pull/1359) | **RP-A1 / DÉC-1 documentaire traités** sans relecteur ; **DÉC-2 au sens d'ouverture inter-étapes reste proposé, non autorisé** (voir §5). |
| **Coût et permissions :** 0 World, 0 vie, acceptation propriétaire | [ADR-0020](../../../docs/decisions/ADR-0020-i3-owner-selected-development-reference.md), [ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md), [manifeste I3](../ACTIVE_SURFACE.json) | **Décision interne acceptée** ; l'autorité déléguée est documentaire/ingénierie. Les nouveaux indices scientifiques restent interdits. Aucun nouveau GO impliqué. |
| **Risque :** faire d'une absence de preuve une clôture | [C01](STAGE2_C01_INTERNAL_DISPOSITION_2026-11-13.md), [ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md) | **Contrôle explicite** : `HOLD_NO_VERDICT` n'est pas `CLOSE_BOUNDED` global, ni une promotion de 2.2/2.3 ou des étapes 3–6. |
| **Sortie T/E/S/Tr et issue** | §3 ci-dessous, [issue #1062](https://github.com/josselin-orta-lab/individual-zero/issues/1062) | **T/E inchangés ; S `NOT_ISSUED` ; Tr = ADR interne versionné.** L'issue #1062 reste **ouverte** car la question scientifique demeure non résolue. |

## 3. Les quatre dimensions de verdict T / E / S / Tr

| Dimension | Ce qui est appuyé par les pièces | Ce qui n'est PAS décidé |
| --- | --- | --- |
| **T, technique** | Porte logicielle de rejeu 2.1 : `REPLAY_GATE_CAPACITY_SHOWN` sur R0–R4 ; R3 est non discriminant sur S1. Les contrôles de source/autorité peuvent progresser séparément. | Ni sélection personnelle générale du nombre de calculs, ni succès des mécanismes 2.2/2.3, ni M11 indépendant, ni moteur I3 activé. |
| **E, expérimental** | Résultats de DEVELOPMENT et écrans E1/E3 conservés, avec leurs coûts et leurs limites. `VISIBLE`/`PAID_DISCARD` E3 est une comparaison logicielle de cas synthétiques, pas un deuxième moteur effectivement vécu. | Pas de chaîne prospective personnelle payée → choix natif → action World → état corporel, pas de confirmation indépendante. |
| **S, scientifique** | **`NOT_ISSUED`**, diagnostic C01 **`HOLD_NO_VERDICT_FOR_GENERAL_STAGE2`**. E1/E3 sont négatifs uniquement sur leur candidat figé. | Ni réussite de la valeur adaptative du calcul, ni réfutation générale, ni non-infériorité de survie établie. |
| **Tr, transition** | [ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md) versionne la **suspension**. Ingénierie I3 R1/R2 autorisée dans son périmètre délégué ; I3 reste référence architecturale, I1 moteur actif. | Pas de clôture scientifique de l'étape 2, pas de promotion automatique d'étapes ni d'admission d'un nouveau World. |

**Trois issues de RP-A1, à ne pas confondre avec ces quatre dimensions :** `CLOSE_BOUNDED` (seulement les écrans figés E1/E3), `DISTINCT_SOURCE_REQUIRED` (condition éventuelle pour une **nouvelle** question sourcée), `HOLD_NO_VERDICT` (issue **retenue** pour la question générale). `NOT_ISSUED` est **le statut scientifique canonique**, pas une quatrième issue concurrente.

## 4. Paramètres hérités et inventaire des négatifs / résultats non concluants

- [Génome v4](../modules/genome.py) : `n_base` (bornes génétiques `2..8`) et `h_max` (`4..24`) sont lus par [Mind](../modules/mind.py) à la naissance. Les [capacités corporelles](../modules/body.py) abaissent le nombre de cycles avec une énergie faible et l'horizon avec une vigilance faible. **Ces valeurs héritées ne sont pas modifiées par RP-A2.** L'objectif de l'étape 2 de les utiliser comme **plafonds** et de décider si la prochaine pensée est utile **n'est pas déjà démontré** dans la référence complète P1.3 : ne pas transformer un plafond génétique/body-dépendant en preuve d'une décision métacognitive sur D.
- **2.1 logiciel** : R0–R4 passent ; R3 plat/non discriminant. C'est une capacité logicielle, pas une confirmation de bénéfice.
- **DEVELOPMENT 80/81** : GATE `3/12` survivants vs FIXED `4/12`, direction défavorable ; résultats de coûts descriptifs, pas inférence de population.
- **B1 / 96** : GATE `38/96` vs FIXED `30/96` ; vigilance `+4.01314` par vie assignée. Différence favorable **exploratoire** en survie, mais dette de vigilance et indépendance/marge non établies ; pas succès.
- **Trois bras / 64** : GATE `27/64` et RANDOM-count payé `27/64`. Comparaison particulière, ni égalité générale ni preuve de bénéfice.
- **Contenu / 48** : TD-priority `17/48` vs random-content `23/48`, signal défavorable au candidat de sélection de contenu.
- **E1** : `0` changement de moteur admis sur `12` contextes synthétiques, malgré certains scores modifiés ; clôture **bornée** de cet écran de profondeur.
- **E3** : `0/2` changements de moteur natif, `1/2` changement de score, `CLOSED_NEGATIVE` du seul écran payé d'information de branche.
- **Coût d'aval** : les cycles de Competition peuvent différer après une information visible même si le premier moteur est identique ; ne pas supposer que mêmes opérateurs exogènes = mêmes charges corporelles totales ([disposition C01](STAGE2_C01_INTERNAL_DISPOSITION_2026-11-13.md)).

Ces contrastes portent sur des interventions et unités différentes : aucun cumul en « méta-analyse indépendante » et aucune correction rétrospective des taux, marges ou originaux.

## 5. DÉC-2 : proposition de feuille de route versus décision applicable

La [feuille de route RP-A2 / DÉC-2, PR #1359](https://github.com/josselin-orta-lab/individual-zero/pull/1359) proposait **A** (avancer étape 0, lignée et portes 3–5 sous budget hérité fixe), **B** (étape 0 et lignée seulement), ou **C** (attendre entièrement le verdict de l'étape 2). **A était recommandée dans la proposition ; aucune de ces options n'a été adoptée comme autorisation générale par l'ADR-0021.**

**Décision effectivement en vigueur :** seule la **transition documentaire vers un `HOLD`** et la poursuite **autonome de l'ingénierie indépendamment admissible** (R1/R2/M11, etc., sous ADR-0020) sont actées. Ne pas assimiler le `HOLD` à une levée des portes de l'étape 0, des lignées expérimentales ou des étapes 3–6. Un futur amendement de ces dépendances/étapes exigerait une décision **distincte et explicite**, avec ses propres sources, portes de preuve et autorisations d'indices. L'absence de relecteur C01 obligatoire n'est pas un vote pour DÉC-2 option A.

## 6. Conditions exactes de réouverture, sans permission implicite

Reprise de [C01 revue interne, §4.5–4.6](STAGE2_C01_INTERNAL_FUTILITY_REVIEW_2026-11-12.md), compatible avec [ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md) :

1. **Avant toute exposition** : définir une information personnelle **réellement distincte** de la source E3, son origine première personne et son mécanisme causal, le prédicteur et sa dérivation, ainsi que ce qui n'était pas déjà testé.
2. **Geler** le traitement, les cas neufs, le coût d'acquisition/lecture/stockage, les dépenses réellement finançables dans les deux monnaies corporelles, la règle d'arrêt et l'absence d'oracle/contrôle moteur.
3. **Discriminateur sans World** à travail exogène payé identique `VISIBLE` vs `PAID_DISCARD`, avec non-exposition, décès et faible énergie/vigilance ; observer un **moteur natif admissible différent**, non un simple score. Enregistrer les cycles de Competition comme coût endogène, pas les neutraliser artificiellement. Si le test échoue, **STOP local négatif**, sans grille de sauvetage post-hoc.
4. Seulement après une porte logicielle discriminante, **préannoncer** un estimand causal sur l'expérience vécue et le corps après paiement, les unités indépendantes et familles d'écologies, la puissance/marge justifiée, les coûts d'opportunité, les comparateurs et les limites. Un budget irréaliste => maintenir `HOLD`.
5. Exiger un transport/scellement exact-source G/R et une **nouvelle permission propriétaire spécifique** des sources, Worlds et plages d'indices avant toute vie scientifique ; séparer DEVELOPMENT, SELECTION, VALIDATION et RÉSERVE. Ne pas rouvrir les cohortes consommées ni modifier leurs originaux.
6. Ne réévaluer le verdict général qu'après un **fait nouveau réellement pertinent** ; jamais en réécrivant la même preuve. La documentation technique R2/M11 ne vaut pas résultat de métaraisonnement.

## 7. Contrôle de sortie RP-A2 / S2-C07

**Décision :** l'[ADR-0021](../../../docs/decisions/ADR-0021-i3-stage2-internal-hold-no-verdict.md) reste **l'unique ADR applicable** pour cette suspension. Cette concordance **n'émet pas une nouvelle version scientifique** de RP-A2. T/E : inchangés ; S : `NOT_ISSUED` ; Tr : `HOLD_NO_VERDICT` versionné et **non-clôturant**. [Issue #1062](https://github.com/josselin-orta-lab/individual-zero/issues/1062) maintenue ouverte pour la question scientifique. La présente annexe consigne les correspondances et limites sans créer de World, de vie, de test expérimental ou de permission nouvelle.
