# A2.30-ZT : contre-audit indépendant des prédictions scellées AVANT l'action

**15 octobre 2026. Verdict technique : PASS, limité à l'intégrité et au recalcul des archives originales.**
CI auditeur : [run #38802690308](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38802690308), **26 tests adversariaux PASS Python 3.11 et 3.12**. Code audité à la tête b77266cf7ecb8c263e3691a4d7ca09c23f6a6999. La source physique originale exclusive est le run [ZS #38801013480](https://github.com/josselin-orta-lab/individual-zero/actions/runs/38801013480), commit 0af1868efe158347992e531c48b182cb5ca91644.

## Chronologie préengagée et méthode

ZS a déposé son protocole e642e7f240909c906cc2bb9d045623f4c4afbf35 **avant** la création de son modèle et de ses mondes. Il a réellement appliqué 120 commandes dans 120 mondes détachés : 16 exemples TRAIN puis 104 mondes HELDOUT (64 nominaux, 24 avec intervention cachée, 16 témoins aux limites corporelles).

**ZT est un audit rétrospectif et non une nouvelle expérience.** Son préenregistrement e3ee40e9d79cfd3bcc09598556a941c09a571427 a été commis après connaissance des résultats de ZS, mais **avant le code ZT**. Les sept SHA-256 ont été archivés dans ce préenregistrement après récupération des deux ZIP originaux. ZT ne crée ni nouveau corps, ni monde, ni action, ni UC.

L'auditeur scripts/audit_stage12_issue110_b_a230zt_independent_preaction.py est **strictement bibliothèque standard Python** : aucun import du runner ZS/ZO, des bibliothèques lab ou i0, de WorldBody, SimulatorPlanner ou Oracle. Il réimplémente indépendamment la sérialisation causale NFC, IEEE-754 hex ($f64) et JSON UTF-8 canonique, les recettes factorielles exactes, le modèle de deltas et le score physique. Les 26 contrôles adversariaux sont dans tests/test_stage12_a230zt_independent_preaction.py.

Les originaux Python 3.11 et 3.12 ont **sept fichiers strictement identiques octet pour octet**, sans que cela représente deux cohortes scientifiques.

## Provenance des sept fichiers originaux

| Original récupéré du run 38801013480 | SHA-256 intégral |
|---|---|
| a230zs-physical-training.json | 818fbb1679603323ea8641aa6dfc1684c12757877bd9d570a53aa332d0bd551a |
| a230zs-frozen-training-model.json | ef52706bf956af484e9c8f6f61d02fab39b35c7db876aa6aa5b9c48d3908f788 |
| a230zs-preaction-forecast-chain.jsonl | 3294a763fe6a0091770ed95aaa672978f9ca7f186b4ad02ee1b1ce86d5f73fc4 |
| a230zs-heldout-worlds.json | b44e987ca36e792ac1772eb38d8cf0b0d4c97151874d802d761f485c10339cc3 |
| a230zs-postaction-scoring.json | 0a8393c50d9200019435c1027f952ca5e1d9b99efb64d62ddad39184a2fe0354 |
| a230zs-summary.json | c3f8d36f4653a353332685c8f982d6bcdcdc369207e8ff3ae9996d83c8201a74 |
| a230zs.log | 5385244c6d4616542926fc237471550eb46039afa08d1c8d857dc4f855b863b4 |

Une source manquante, dupliquée, modifiée ou issue d'un autre run est rejetée sans recours à une copie « équivalente ».

## Reconstitution à partir des seules perceptions et actions observées

**Modèle source.** ZT vérifie physiquement par archives les seize événements de formation (8 déplacements est, 8 collectes B), avec états et empreintes de chaque exemple. Seules six dimensions accessibles sont apprises : x, y, énergie, nourriture, eau, inventaire B. L'empreinte reconstruite du modèle est exactement d837d17d285c20ac53a55f3f78818d4f2abfa7cd387b6232e3c105bd9ac25171, déjà verrouillée par ZO/ZS.

Les dimensions **intégrité, terminalité, voisinage futur et sécurité** restent NULL dans le modèle et dans les 104 prévisions. Aucune conséquence d'ingestion de B n'a été utilisée. Aucune des 104 clés complètes des tests n'est présente parmi les 16 exemples TRAIN.

**Ordre causal scellé.** Les 208 enveloppes originales forment 104 paires strictement alternées « prediction_committed » et « outcome_sealed ». ZT recalcule tous les SHA, préfixes, numéros, empreintes de perception, actions éligibles et liens vers les enveloppes précédentes. Il recalcule également **les 104 prévisions indépendamment de la fonction du runner**. Une chaîne intégralement rehashée après falsification d'un chiffre échoue tout de même à la comparaison avec le modèle source.

**Conséquences physiques recomptées, non déduites des compteurs du runner :**

| Cohorte | Mondes originaux | Résultats |
|---|---:|---|
| NOMINAL | 64 | **64/64** prévisions numériques à six composantes exactes, aucun décès |
| HIDDEN | 24 | **4 morts** motrices, **8 blessures**, **8 échecs forcés** d'action ; 8 erreurs numériques |
| BOUNDARY | 16 | **16 abstentions** liées aux contraintes visibles du corps, sans certitude de sécurité |
| TOTAL HELDOUT | 104 | **88 prévisions**, **16 abstentions**, aucun résultat de sécurité alimentaire B |

Les **32 paires** de variantes B bénignes/létales nominales produisent des entrées, prévisions et effets non ingestifs identiques. Les interventions cachées ne figurent pas dans la perception préaction. Certaines issues mortelles coexistent avec des prévisions x/y/énergie/nourriture/eau/inventaire exactes : **bonne prédiction numérique ne veut pas dire sécurité motrice**.

## Tests adversariaux et limites

**26/26 tests PASS** sous chaque version Python : modification des SHA des fichiers et doublon d'archive, inversion ou retrait de reçus, falsification numérique même après re-signature intégrale de la chaîne, fuite d'un champ caché, faux « safe=True » ou « terminal=False », insertion d'un HELDOUT dans TRAIN, modèle corrompu, ingestion B inventée, reçu subjectif post-mortem, fausse UC, événement mortel retiré, mauvaise provenance de commande, scores falsifiés et mensonge sur le nombre de clés complètes connues.

**Frontière méthodologique :** les seules archives ne prouvent pas à elles seules l'ordre temporel face à un opérateur capable de reconstruire tout un jeu de fichiers. Le code source du runner ZS démontre une séquence interne fsync de la prévision, **avant** WorldBody.apply, puis fsync de la conséquence. Les sept SHA source et l'historique GitHub Actions d'origine en bornent les falsifications ultérieures ; ce n'est **pas une signature temporelle indépendante par un tiers**. Le prolongement distinct [#214](https://github.com/josselin-orta-lab/individual-zero/pull/214) teste des jobs séparés et ne doit pas être mélangé aux 120 mondes ZS de cette revue.

**Verdict final : PASS pour l'intégrité, les 208 reçus, la reconstruction des 104 prévisions et le scorage des risques cachés.** ZT n'a pas réexécuté WorldBody, Stage6 ou I0. Aucune naissance, aucun coût UC, aucun jugement subjectif, aucune amélioration de sécurité ni modification normative. **Stage12 PARTIAL, A2.30 PARTIELLE, issue #110 administrativement CLOSED ; déploiement cognitif NO-GO. PR #215 DRAFT, sans fusion.**
