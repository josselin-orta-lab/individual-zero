# F1M-PH1 · Seuils de compétition : audit archivistique exploratoire

**Date : 24 novembre 2026 · Statut : `POSTHOC_ARCHIVE_ONLY_COMPLETE`, aucune nouvelle vie.** Ce texte et l'analyse qui l'accompagne viennent **après** le verdict scientifique F1M. Ils ne constituent ni un préenregistrement, ni un résultat confirmatoire, ni une nouvelle intervention sur l'individu. L'unité indépendante reste **32 origines** ; les 64 comparaisons carry/zero sont corrélées par origine.

## Sources immuables et reproductibilité

- Exécution scientifique originale, jamais rejouée : [Actions #45500772324](https://github.com/josselin-orta-lab/individual-zero/actions/runs/45500772324), source `a0d063402cad87d6dd255e2f842586b8f8f95267`, ref consommée `f6e213ca197c432b03907c3d8999ddf10bcac809`.
- [RAW Release](https://github.com/josselin-orta-lab/individual-zero/releases/tag/i3-stage8f1m-t60-raw-heldout-once), `immutable=true`. Archive `F1M_ORIGINALS_384_GZIP.tar.gz` SHA-256 `4e4888d00d5494f071d84d469e26f62d497dba8ce390bbe01101607a018992bc`; manifeste `F1M_CUSTODY_MANIFEST.json` SHA-256 `47ad255aaac32756a1777cbecfe4d3356b58beee4b7e4b1aaf403612a961a4af`. L'artefact Actions ZIP natif a le SHA-256 `5421f48132ea2839114baa97199acdaa3cfe2f581610e733000308f99d5e6324`.
- [COLD Release](https://github.com/josselin-orta-lab/individual-zero/releases/tag/i3-stage8f1m-t60-cold-heldout-once), `immutable=true`. Rapport `F1M_INDEPENDENT_COLD_T60.json`, SHA-256 `85cc44b84075321f96114b14e8d1c6b52b592e0c44e8cb40180b568e9c1c8791`.
- Script reproductible : `tools/stage8f1m_ph1_archival_thresholds.py`, Python 3.12 stdlib, **sans aucun import du moteur**. Il vérifie le SHA du tar, du manifeste, des 384 gzip, des 128 charges JSON consultées, des 32 checkpoints, du rapport COLD et des **7 040 décisions natives de continuation**. Chaque instant T6..T60 est lu depuis les reçus, sans `World.step` ; les cinq tours F1J de chaque décision sont vérifiés algébriquement contre leurs témoins.
- Résultat per-paire (`64` contrastes) : `docs/research/studies/stage8f1-paid-microdecision/data/STAGE8F1M_PH1_THRESHOLD_ARCHIVE_ANALYSIS_2026-11-24.json`, SHA-256 **`ed4adcbef9b93527c74f87de67de412e1e377bae2933ad910f03148bd455ff23`**, calculé sur les octets du fichier terminé par LF.

## Contrôle de compréhension du moteur, sans le réexécuter

Le F1J gelé depuis le préenregistrement autorise un nombre **fixe de tours substantiels** et applique, à chaque tour payé, la transition suivante à chaque option réellement scorée :

`activation_suivante = max(0, 0.8 × activation_précédente + évidence_normalisée)`

Après le **dernier tour payé seulement**, les options ayant franchi leur seuil sont comparées par surplus relatif `(activation − seuil)/seuil`, le maximum donne le candidat gagnant. Si aucun seuil n'est franchi, un autre mécanisme de sélection native est utilisé. Les accumulateurs du perdant sont ensuite multipliés par 0,5 et celui du gagnant remis à zéro. Les seuils (éventuellement modifiés par l'intention) et les évidences sont **relus du témoin natif**, pas recalculés en inventant des scores. Les « gagnants transitoires » des tours précédant le dernier sont des **candidats algébriques exploratoires**, jamais des actions réellement choisies.

## Observations PH1a : franchissement des seuils

| Variable observée dans les 64 paires | Valeur |
|---|---:|
| Résidu T5 réel non nul et neutralisé dans `zero` | **40/64** |
| Au moins un ensemble d'options franchissant le seuil différent pendant les tours T6 | **21/64** |
| Premier franchissement de seuil (toutes options) à un tour différent | **16/64** |
| Premier franchissement du **gagnant final** à un tour différent | **14/64** |
| Ensemble de candidats provisoires différent avant la fin de T6 | **10/64** |
| Ensemble des candidats au **tour final** différent | **0/64** |
| Ensemble des options ayant franchi le seuil au tour final différent | **0/64** |
| Gagnant **effectivement sélectionné** différent à T6 | **0/64** |

Dans les **40 paires R actives**, le gagnant final franchit son seuil au **tour 1 dans 14 cas carry**, contre **zéro dans la condition zero** ; les autres interviennent au **tour 2** dans les deux conditions. Les **10 écarts de candidat provisoire** concernent tous des paires à résidu actif et totalisent **14 tours intermédiaires**. Le F1J ne s'arrête pas à ces franchissements précoces : les décisions n'interviennent qu'à la fin des cinq tours payés. Les candidates finales sont les mêmes dans **64/64** contrastes.

Sur les 40 paires actives, le surplus normalisé du gagnant après le dernier tour (ratio `(A−seuil)/seuil`) a une médiane descriptive de **1,2041** en carry contre **1,0978** en zero. La médiane de sa marge relative au deuxième meilleur surplus est **0,4347** contre **0,2004**. Ces nombres décrivent des états internes, **pas un gain d'adaptation ni un test d'effet statistique**.

**Résultat PH1a :** les traces prouvent une **modification transitoire du franchissement de seuil**, compatible avec une sélection finale inchangée parce que la compétition F1J est à durée fixe. Il serait incorrect de prétendre que les gagnants provisoires auraient été exécutés ou auraient payé une facture corporelle différente.

## Observations PH1b : quelles options portent le résidu ?

Les **40/40** résidus actifs ont au moins une clé encore scorée à T6. Dans **27/40** cas, une option portant le résidu est aussi le gagnant final ; dans les **13/40** autres, seules des options perdantes portent ce résidu. Parmi les 40 paires actives, la meilleure position de leur option porteuse dans le classement d'évidence normalisée à T6 est : **rang 1 dans 27 cas**, **rang 2 dans 10 cas**, **rang 3 dans 3 cas**. Le classement et l'évidence normalisée restent strictement identiques entre les deux branches.

La répartition descriptive des contrastes R non nuls dépend des mondes déjà préenregistrés : **8/32 comparaisons** dans les quatre écologies à eau adjacente (4/16 racines) et **32/32 comparaisons** dans les quatre écologies à eau diagonale (16/16 racines). Ceci n'est **pas** un nouveau sous-groupe confirmatoire, ni une preuve que la distance à l'eau cause le mécanisme.

## Observations PH1c : disparition des écarts internes, moteurs identiques

Dans les **40 comparaisons avec R actif**, l'écart dans les accumulateurs *au début de la compétition* apparaît à T6 dans les 40 cas. Sa **dernière** apparition dans ces témoins est T6 pour **30 paires**, T7 pour **4**, T8 pour **6**. Dans les accumulateurs relevés *après application du résiduel de compétition*, **30/40** paires ne portent déjà plus aucune différence au terme de T6, **4/40** en portent jusqu'à T6, **6/40** jusqu'à T7 ; aucune différence après le résiduel n'est visible après T7. Cette mesure ne prétend pas établir l'identité de tous les états internes non enregistrés : elle porte exclusivement sur les dictionnaires d'accumulation observés.

**64/64** paires conservent le même gagnant de compétition et les mêmes **55 commandes motrices T6..T60** ; l'audit froid officiel confirme que les cinq réserves corporelles terminales et les durées de vie sont identiques. Les coûts payés et l'autonomie motrice restent ceux des individus originaux.

## Limites, règle d'arrêt et suite

**F1M était déjà conclusif et négatif** : `NO_REPRODUCIBLE_LOCAL_T6_RESIDUAL_MOTOR_EFFECT`, `NO_REPRODUCIBLE_LOCAL_T60_SURVIVAL_ADVANTAGE`, `NO_REPRODUCIBLE_LOCAL_BODY_PARETO_SUPPORT`. Ce diagnostic post-hoc n'altère **aucun** des trois verdicts ni ceux de F1L, et ne promeut pas Stage2 (`NOT_ISSUED/HOLD_NO_VERDICT`).

Les données identifient un mécanisme local descriptif : **résidu effectivement injecté → franchissements et marges internes parfois modifiés → cinq tours F1J achevés → même choix final → mêmes commandes et mêmes conséquences corporelles**. Elles ne démontrent ni qu'un arrêt anticipé aurait été bénéfique, ni qu'une politique différente serait plus adaptative. Aucun moteur n'a été lancé dans PH1, aucune nouvelle exposition n'est autorisée.

La prochaine étape admissible est **PH1 de vérification croisée** : faire rejouer le calcul de seuils par le script stdlib depuis les Releases RAW/COLD immuables, sous CI lecture seule et en comparant le SHA-256 du rapport reproduit. Une étude prospective ultérieure devrait faire l'objet d'un **autre** préenregistrement avec de nouvelles origines, avant toute naissance.
