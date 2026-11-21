# Stage8-F1H · valeur corporelle prospective du contraste mémoriel F1F à T12

**21 novembre 2026 · résultat primaire scientifique : `NO_SURVIVAL_ADVANTAGE_OF_THE_MEMORY_INFLUENCED_DECISION_AT_T12` ; résultat corporel secondaire : `MIXED_BODILY_TRADEOFF`.** Les trajectoires F1H ont été obtenues **après** le [préenregistrement T12](STAGE8F1H_PROSPECTIVE_BODY_VALUE_PREEXPOSURE_2026-11-21.md) figé au commit `5c2abb2fc755bf0a580e2880bedf507b59a2baec`, référence `main` `3ad4cb687b403214c9b9f6055b46a489dca44af4`. Ni le code ni le verdict de F1D, F1E, F1F, F1G ou Stage8-E2 n'ont été modifiés.

## Question et lecture correcte du contraste

Dans F1F, le contenu personnellement appris, réellement débité du corps et conservé avait **causé une différence de commande motrice dans 1/8 écologies déterministes** : au monde `mixed_here_water_east_food`, lire les moyennes apprises conduisait à `se_deplacer E`, lire les anciennes moyennes avant apprentissage conduisait à `se_deplacer N`, et le témoin `sham` choisissait Est, tous à **coût cognitif strictement identique**. La présente expérience demande **prospectivement** si cette différence a des conséquences corporelles avantageuses jusqu'au tick **T12 fixé à l'avance**, sans lui imposer aucune direction, et **en laissant l'individu payer et apprendre** à chaque pas.

Cette expérience est conditionnelle au contexte mixte **connu comme divergent AVANT la préexposition F1H**. Les 7 autres mondes F1F sont conservés sans sélection, mais il ne s'agit pas d'une validation indépendante du contraste moteur connu. Un résultat corporel ici est l'**effet total de l'accès aux moyennes** avec tous ses médiateurs ultérieurs (commande, position, processus compétitif et apprentissage), et **non** une comparaison expérimentale forcée « action Est vs action Nord » à état interne égal.

## Chaîne native originale conservée

- **F1C** : réel premier `PaidMicrodecisionMind.decide` suivi `World.step(dormir)`, apprentissage personnel conservé et payé au vrai prix `0,1096 énergie / 0,174 vigilance`, [source d'origine #44837981694](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44837981694), artifact #14679910820, SHA256 JSON `e46ad5f54af49796da65f48d603595544116aa6e73632546b0935d2178c5e91d` ;
- **F1F** : huit mondes écologiques figés, 24 décisions suivantes, première divergence motrice `1/8`, artifact original #14702338615, SHA256 `f620d1b46ddf269dc368dcd90ba6c93f44f0b6442f8d9e6322440de32e3fbab5`, audit à froid #14702267579, SHA256 `8013f2add1f3eb0190127bb77eac588c95f153f32ba21113302bafa0292e2ac2` ;
- **F1G** : deux contrôles distincts déjà négatifs, `0/8` valeurs TD et `0/8` tampon d'épisodes, source SHA256 `a7f0782886b3d2b97cd91ea11803934f31736b91e6d659c700a3d1dd886a8376`, contre-audit SHA256 `ec3b1c953c69d87dc042ab81da55809984e7b78c175a2697a6b3d0a24fa21310` : résultats **non réinterprétés**.

Le logiciel F1H reconstruit la première expérience native F1C à coût payé, puis **compare bit à bit l'intégralité de chacun des 24 reçus originaux F1F au tick 2**, avant de poursuivre. Les seuls masques de moyenne sont ceux du tick 2 ; les vraies moyennes F1C sont restaurées avant physique, comme dans F1F. À partir du tick 3, les trois bras `full`, `sham` et `mask_both` agissent sous le **même** moteur natif sans intervention supplémentaire, en regardant `World.capture`, puis `Mind.decide`, `World.step`, `Mind.observe_outcome` et `Mind.prepare_learning`. Chaque apprentissage est **autorisé** par `CognitiveBudget`, réellement payé dans `World.pay_cognition` **avant** `Mind.learn_from_outcome`. Les débits peuvent désormais différer naturellement selon les trajectoires ; **aucun cycle de cognition n'a été artificiellement ajouté pour les égaliser**.

**Huit écologies × trois bras × onze pas natifs (ticks 2 à 12) : 264 `World.step`**, plus huit premières expériences sources F1C. **264 paiements postaction** ont été constatés et indépendamment recalculés. Les 24 bras survivent jusqu'à T12, et les huit bras `sham` sont **rigoureusement identiques à `full` tout le long de la trajectoire**, de leurs actions à leurs états privés et factures. Aucun tick après mort, aucune naissance, aucun `run_life`.

## Résultat corporel primaire : survie égale à T12

| Critère préenregistré | Moyennes authentiques `full` | Anciennes moyennes exposées au tick 2 `mask_both` |
|---|---:|---:|
| Ticks exécutés après F1C | 11 | 11 |
| Vivant à T12 | Oui | Oui |
| Énergie terminale après tous paiements | **13,4260** | 8,8682 |
| Nourriture terminale | 71,2200 | **71,3900** |
| Eau terminale | 80,2000 | 80,2000 |
| Intégrité terminale | **91,8000** | 91,6000 |
| Vigilance terminale | 99,3640 | 99,3640 |
| Position finale | (1,1) | (1,2) |
| Déplacements totaux | 2 | 3 |
| Boissons / aliments collectés | 1 / 0 | 1 / 0 |

Le critère **principal de survie** ne trouve **aucun avantage** : les deux branches sont vivantes au tick 12. La branche qui a effectivement lu ses moyennes personnelles apprises gagne **+4,5578 énergie** et **+0,2 intégrité**, mais perd **0,17 nourriture** au terminal. À cause de ce coût alimentaire, il n'existe **aucune dominance Pareto des cinq réserves** : `MIXED_BODILY_TRADEOFF`. Il serait faux de présenter le seul gain d'énergie comme une amélioration adaptative générale.

Les **intégrales non pondérées** sur les onze corps postaction permettent de documenter le chemin : énergie `full=57,2280` contre `mask=48,2912` (**+8,9368**), nourriture `full=802,0200` contre `mask=802,3600` (**−0,3400**), eau `829,2` identique, intégrité `full=999,8` contre `mask=999,4` (**+0,4**), vigilance `full=1091,9700` contre `mask=1091,4920` (**+0,478**). Le minimum vital observé vaut **58,4** dans les deux bras. **Ce sont cinq mesures descriptives**, pas les composantes d'un score composite ou un critère de survie remplacé après exposition.

**Coût cognitif réellement prélevé au fil des trajectoires**, intégré aux valeurs corporelles finales :

| Cumul coût natif jusqu'à T12 | `full` | `mask_both` | Différence `full-mask` |
|---|---:|---:|---:|
| Décisions, énergie | 2,6716 | 2,6364 | +0,0352 |
| Apprentissage, énergie | 2,9620 | 2,5550 | +0,4070 |
| Décisions, vigilance | 3,8220 | 3,8180 | +0,0040 |
| Apprentissage, vigilance | 3,8880 | 3,4260 | +0,4620 |
| **Total énergie** | **5,6336** | **5,1914** | **+0,4422** |
| **Total vigilance** | **7,7100** | **7,2440** | **+0,4660** |

La branche `full` termine ainsi avec **plus d'énergie corporelle malgré un calcul total plus coûteux**, sans que cela prouve un bénéfice de survie. Le contenu du seul token alimentaire F1F est volontairement resté **sans `token_effects`** conformément à son `WorldSpec` initial ; aucune récompense alimentaire, bénéfice physique caché ou comportement favorable n'a été inventé après F1F. Aucun aliment n'est collecté par l'un des deux individus dans le cas mixte.

## Mécanisme de trajectoire observé

Dans le monde mixte `mixed_here_water_east_food`, les commandes successives des deux premières divergences sont :

- `full` : tick 2 **Est**, tick 3 sommeil, tick 4 **Ouest**, tick 5 **boire** ici. Au tick 11 : sommeil.
- `mask_both` : tick 2 **Nord**, tick 3 sommeil, tick 4 **Sud**, tick 5 **boire** ici. Au tick 11 : **Sud** (déplacement supplémentaire).

Ce sont de **véritables actions choisies** par chaque `Mind.decide` avec factures corporelles, et non un itinéraire imposé. L'écart terminal d'énergie est compatible avec le troisième déplacement du contrôle et avec des séquences différentes de cognition et de sommeil ; l'étude ne démontre pas que l'information acquise a anticipé un trajet « optimal ». La **position finale** n'a aucune valeur de récompense propre dans le protocole. Les **sept autres écologies** ont des états corporels terminaux identiques entre `full` et `mask_both` et **aucun avantage de survie**, sans les soustraire de l'analyse.

## Contrôle indépendant et conservation

[CI F1H #44896342369](https://github.com/josselin-orta-lab/individual-zero/actions/runs/44896342369), **2/2 jobs PASS** : 17 tests dédiés, dont des témoins rescellés de fausse survie, cognition gratuite, factures après action modifiées et prolongation au tick 13. Deux producteurs Python 3.11 ont généré des **preuves octet-identiques**. Auditeur froid Python 3.12 **stdlib-only sans import du producteur, de `Mind`, de `World` ou `BodyLaws`** : **264 `World.step`** post F1C recalculés, **264 factures d'apprentissage** contrôlées, ressources/positions/lois figées et **24/24 reçus tick 2 identiques à F1F original**. L'auditeur réexamine les empreintes des états mentaux complets et la continuité de l'apprentissage ; **il ne prétend pas recalculer indépendamment tout l'algorithme TD**.

Artefact source #**14704126450**, `F1H_PROSPECTIVE_ORIGINAL.json` **21 334 939 octets**, SHA256 **`f6b9129c56fcb7a9eaa7f574561fd511fa0b730600553ade1b132ae700c6566b`** ; reproduction de taille et octets identiques. ZIP source SHA256 `204b8e0e71561651bd0e0219c34cb3d552ba75486822ace77392d2671af43cd2`. Artefact froid #**14704226017**, `F1H_INDEPENDENT_COLD_BODY_AUDIT.json` **7 555 octets**, SHA256 **`79ed96a2a09a66e4dfe0173d2e138c3c37d03378157f916d71193d2642cf5606`**, ZIP SHA `cb3364e76d54cd7a0fc7006120ba9e10f88b797e7b8d2daaf029f19453f734f3`.

Archive portable source-verrouillée incluant F1C, F1F, F1G, F1H (original et reproduction) et audits : `F1H_T12_native_prospective_adaptive_value_evidence_20261121.tar.gz`, **3 165 349 octets**, SHA256 **`c212f5127cc44becc6066e96d68e10f93d5dac95a702e6f452f33553a694888d`**. Manifeste d'originaux [JSON](STAGE8F1H_PROSPECTIVE_BODY_VALUE_PROVENANCE_MANIFEST_2026-11-21.json). Les originaux portables sont fournis dans la conversation, distincts du délai GitHub Actions de 90 jours. Les empreintes de toutes les étapes sont conservées ; l'archive Git ne contient pas les 21 Mo de reçus.

## Conclusion scientifique et limite

**F1H montre des conséquences corporelles mesurables, mais aucun bénéfice de survie à T12 et aucune dominance corporelle générale.** C'est un résultat **négatif sur le critère adaptatif strict**, sans effacer le résultat F1F déjà démontré : **lire les moyennes acquises peut faire basculer une décision motrice** (dans une écologie synthétique préenregistrée), mais cette modification n'implique pas automatiquement une amélioration de viabilité.

Un nouvel horizon, un monde réellement nutritif ou une cohorte supplémentaire nécessiterait un **nouveau protocole figé avant collecte**, et ne pourrait pas reclassifier F1H a posteriori. Les huit mondes ne sont pas des vies indépendantes ; le prior F1C est synthétique et n'équivalait pas aux souvenirs privés archivés des descendants historiques G2. `CognitiveWork` et ses débits physiques sont audités, mais **l'égalité du temps CPU** n'est pas démontrée. Aucun `run_life`, naissance/cohorte scientifique ou promotion du moteur de référence. Stage8-E2 reste **`STAGE8E2_CAUSAL_GAMMA_BLOCK_NOT_DEMONSTRATED_F0 / CLOSED_NO_RETRY`**.
