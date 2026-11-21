# Stage8-F1E · effet du contenu numérique personnel à coût cognitif égal

**21 novembre 2026 · verdict primaire préenregistré NEGATIF : `NO_EQUAL_COST_CONTENT_EFFECT_ON_NEXT_MOTOR_COMMAND_IN_THIS_CASE`.** Contrairement à F1D, ce test contrôle rigoureusement, à partir de la même mémoire source F1C réellement apprise et facturée, le **volume de mémoire, le travail cognitif et les débits natifs des deux monnaies**. Il montre que la valeur des moyennes d'effets personnels intervient dans les calculs mais, dans **cette unique écologie synthétique**, ne fait pas basculer la commande physique suivante.

## Chaîne de preuve et délimitation

- [Plan préexposition F1E](STAGE8F1E_EXACT_CONTENT_READOUT_PREEXPOSURE_2026-11-21.md) fixé dans le commit `e2b8e8f80a68cc5b0ddeeb87fac4ac45cd1ac007` **avant l'exposition** ; base `main` `3dd12c94843ca2cadf1af5c885b9eb215db31553`. [PR logicielle #1489](https://github.com/josselin-orta-lab/individual-zero/pull/1489), version de preuve SHA `f27734320902b9bb88861a9cfd1896d10bf4524b`.
- Source physique/personnelle F1C d'origine téléchargée, non réinventée : [run #44837981694](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44837981694), artefact #14679910820, `F1C_PAID_NATIVE_ORIGINAL.json` **125 436 octets**, SHA256 `e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d`. Le vérificateur indépendant réexécute la re-réduction native de F1C avant tout accès aux résultats F1E.
- [GitHub Actions F1E #44891088978](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44891088978) **2/2 jobs PASS**, Python 3.11 pour le producteur natif, Python 3.12 pour le réducteur indépendant **stdlib only** sans importer `Mind`, `World` ou le producteur. **16/16 falsificateurs dédiés PASS**, notamment cinq altérations malveillantes/rescellées et la neutralité du sham. Deux processus producteurs ont généré des preuves **octet-identiques**.
- Artefact producteur #**14702585042** : `F1E_NATIVE_CONTENT_ORIGINAL.json` **332 967 octets**, SHA256 **`22cef70784ce7f7f1c3478ee12c269dfedfa8041930b9811b27fd18c4d6d3b6a`** ; `F1E_NATIVE_CONTENT_REPRODUCED.json` identique. L'artefact contient en outre l'original F1C source SHA-pinné.
- Artefact contre-audit #**14702240563** : `F1E_INDEPENDENT_COLD_AUDIT.json` **1 371 octets**, SHA256 **`c2d829537a4a2dd21ed4b62aac785f195da493434b4ecab1e6350e92cd9b1a63`**. Les empreintes ZIP des deux artefacts et l'archive portable sont consignées dans le [manifeste F1E](STAGE8F1E_EXACT_CONTENT_PROVENANCE_MANIFEST_2026-11-21.json).
- Toutes les preuves brutes sont aussi rassemblées dans l'archive portable `F1E_equal_cost_memory_content_evidence_20261121.tar.gz`, SHA256 **`36e58444d303b67e796e14a7fbc3b03c70cbea1cb477c25c37c85742192dd7b5`**, copie fournie dans la conversation. Le manifeste Git **ne remplace pas** la sauvegarde originale ; les artifacts GitHub Actions sont conservés **90 jours**.

## Intervention causale de laboratoire strictement appariée

Le même `Mind` a choisi le premier `World.step(dormir)` F1C, vécu et payé le résultat, puis payé `Mind.prepare_learning` / `World.pay_cognition` **0,1096 énergie et 0,174 vigilance** avant `Mind.learn_from_outcome`. La mise à jour est réellement retenue dans les effets, le buffer et les valeurs. L'expérience première contenait un **a priori personnel synthétique**, pas une mémoire historique G2.

Une seule reconstruction native est ensuite copiée dans **cinq instances détachées** sur le même corps `[2.9096, 74.63, 59.6, 90.2, 98.776]`, à même `World.capture`, mêmes valeurs TD, mêmes tampons, génotype, RNG et taille de `EffectsModel` (`n_eff` et `count` inchangés). Dans les bras masqués, **les seules moyennes d'effets numériques** `("dormir",)` et/ou `("*",)` sont temporairement remplacées, pour la durée de la décision, par les vraies moyennes personnelles archivées **avant** l'apprentissage F1C. Les véritables souvenirs restent stockés et sont restaurés après le readout. Le controle `sham` effectue l'intervention de copie mais expose les valeurs authentiques.

**C'est un masque causal de valeur de `EffectsModel`**, pas une intervention sur les variables TD ou le contenu du buffer, pas une mémoire générale effacée, et pas une nouvelle politique. `Mind.decide` décide naturellement, puis `World.step(action,param,work)` exécute ce qu'il a effectivement choisi, jamais une commande imposée.

## Résultats

| Valeur exposée à la décision | Score de l'option gagnante | Option / commande ultérieure | Cognition payée native |
|---|---:|---|---|
| `full` : valeur réellement apprise | −0,652133 | `explorer:1,0` ; `se_deplacer E` | 0,2306 E / 0,344 V |
| `sham` : valeur identique, test de neutralité | −0,652133 | `explorer:1,0` ; `se_deplacer E` | 0,2306 E / 0,344 V |
| `mask_both` : moyennes `dormir` et `*` antérieures | −0,648950 | `explorer:1,0` ; `se_deplacer E` | 0,2306 E / 0,344 V |
| `mask_sleep_only` : moyenne `dormir` antérieure | −0,646850 | `explorer:1,0` ; `se_deplacer E` | 0,2306 E / 0,344 V |
| `mask_global_only` : moyenne globale `*` antérieure | −0,652789 | `explorer:1,0` ; `se_deplacer E` | 0,2306 E / 0,344 V |

**Parité complète des unités de travail natif** : pour chacun des cinq bras, `CognitiveWork(cycles=4,simulated_steps=72,memory_items=33,replays=0)`, avec **0,2306 énergie / 0,344 vigilance** réellement débités par `World.step` (toutes deux sans impayé). Même corps avant le calcul, mêmes données visibles, même source, même `WorldSpec`, mêmes comptes de mémoire. Les cinq pas physiques après décision se terminent au même corps `[0.679, 74.43, 59.2, 90.2, 98.432]`. Le contrôle `sham` est exact, pré et post décision.

Les estimations du sommeil contiennent bien la nouvelle information : moyenne d'énergie après apprentissage F1C **+2,9288** contre moyenne d'avant **+3,0000**. Les **scores changent effectivement** avec le contenu exposé, notamment −0,652133 en `full` contre −0,648950 en `mask_both`. Toutefois la même option reste gagnante et la même commande est payée et exécutée.

Le **critère primaire** exigeait une commande `(action,param)` différente entre `full` et `mask_both` à factures identiques. **Ce critère échoue**. Ne pas promouvoir la différence de score ou d'urgence en influence motrice. La valeur de la mémoire intervient dans le calcul natif, pas dans le résultat moteur observé ici.

## Limites, statut scientifique et règle d'arrêt

Les cinq conditions sont **cinq masques appliqués au même épisode synthétique**, et **non cinq mondes écologiques indépendants** : cela ne mesure ni fréquence d'effets comportementaux dans une famille de mondes, ni amélioration de persistance. La parité est celle des unités `CognitiveWork` et factures corporelles **du modèle i3**, pas une preuve de temps CPU identique. Les compteurs `n_eff` / `count` sont tenus égaux : le test isole **les valeurs numériques des moyennes**, pas leur confiance, ni les valeurs TD ou le buffer. Le modèle d'apprentissage antérieur reste synthétique, pas les souvenirs réels des descendants G2, et aucun effet futur au-delà d'un unique nouveau tick n'est mesuré.

**Aucun `run_life`, aucune nouvelle naissance, aucune cohorte scientifique, aucun `evidence_head` de vie entière**, aucune modification du moteur i3 de référence. Aucune revendication d'utilité adaptative, causalité génétique ou survie. Stage8-F1D reste négatif selon son critère indépendant ; Stage8-E2 reste `STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`, i3 non promu, I1 toujours moteur actif.

Un prochain test, distinct et préenregistré, pourrait examiner une famille réelle de situations au niveau de leur décision motrice, **sans choisir les conditions après avoir vu ce résultat**. Ne jamais transformer les cinq contrôles d'une seule écologie en effet généralisé.
